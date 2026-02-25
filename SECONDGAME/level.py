import pygame 
from settings import *
from tile import Tile
from player import Player
from support import *
from weapon import Weapon, NewWeapon
from enemy import Enemy
from ui import UI
from magic import MagicPlayer, Projectile
from drop import Drop
import random
import math

class Mission:
    def __init__(self, mission_type, pos=None):
        self.type = mission_type
        self.active = True
        self.start_time = pygame.time.get_ticks()
        self.duration = 30000  # 30 secondes pour la mission de vitesse
        self.enemies_killed = 0
        self.target_kills = 10
        self.reward_money = random.randint(200, 400)
        self.reward_heart = random.choice([True, False])

        if mission_type == 'elite_hunt':
            self.description = "Tuez l'ennemi d'élite rapide !"
            self.enemy_pos = pos
        elif mission_type == 'speed_kill':
            self.description = "Tuez 10 ennemis en 30 secondes !"

    def update(self, enemies_killed, current_time):
        if self.type == 'speed_kill':
            self.enemies_killed = enemies_killed
            if current_time - self.start_time >= self.duration:
                self.active = False
                return False  # Mission échouée
            elif self.enemies_killed >= self.target_kills:
                self.active = False
                return True  # Mission réussie
        return None  # Mission en cours

    def get_time_left(self):
        return max(0, self.duration - (pygame.time.get_ticks() - self.start_time))

class Level:
    def __init__(self, save_data, change_level):
        # Configuration initiale
        self.display_surface = pygame.display.get_surface()
        
        # Variables d'état
        self.show_talents = False
        self.show_help = False
        self.flash_alpha = 0
        self.current_attack = None

        # Groupes de sprites
        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()
        self.attack_sprites = pygame.sprite.Group()
        self.attackable_sprites = pygame.sprite.Group()
        self.drop_sprites = pygame.sprite.Group()

        # Données de progression
        self.save_data = save_data
        if 'life_hearts' not in self.save_data: self.save_data['life_hearts'] = 0
        # Système simplifié : une seule arme (épée) et une seule magie (boule de feu)
        self.level_number = save_data['current_level']
        self.change_level = change_level

        # Système de missions
        self.active_mission = None
        self.mission_timer = 0
        self.mission_start_time = 0
        self.enemies_killed_in_mission = 0
        self.mission_enemy = None  # Pour l'ennemi d'élite de mission
        
        # Effets visuels
        self.flash_surface = pygame.Surface((WIDTH, HEIGHT))
        self.flash_surface.fill((255, 255, 255))

        # Systèmes de jeu
        self.ui = UI()
        self.magic_player = MagicPlayer(None)
        
        # Création du niveau
        self.create_map()
        # --- LOGIQUE DE PROBABILITÉ UNIQUE ---
    # On décide au début du niveau s'il y a une mission
        is_boss_level = self.level_number % 5 == 0 # On évite les missions aux boss
    
        if not is_boss_level:
            if random.randint(1, 12) == 1:
                self.try_spawn_mission()

    def create_map(self):
        self.layout = import_csv_layout(LEVEL_MAPS[self.level_number])
        layout = self.layout

        for row_index, row in enumerate(layout):
            for col_index, col in enumerate(row):
                x = col_index * TILESIZE
                y = row_index * TILESIZE
                
                if col == 'x':
                    Tile((x,y), [self.visible_sprites, self.obstacle_sprites], 'wall')
                elif col == 's': 
                    self.exit_sprite = Tile((x,y), [self.visible_sprites], 'exit')
                    self.exit_sprite.image.set_alpha(0) 
                elif col == 'r': 
                    self.secret_reward = Tile((x,y), [self.visible_sprites], 'reward')
                elif col == 'p':
                    # Toujours l'épée comme arme unique
                    self.player = Player(
                        (x,y), [self.visible_sprites],
                        self.obstacle_sprites,
                        self.create_attack,
                        self.destroy_attack,
                        self.create_magic,
                        self.save_data,
                        'sword')
                elif col in ['e','d']:
                    monster = 'demon' if col == 'd' else ('raccoon' if self.level_number > 2 else 'squid')
                    Enemy(monster, (x,y), [self.visible_sprites, self.attackable_sprites, self.drop_sprites],
                          self.obstacle_sprites, self.damage_player, self.trigger_death_particles)
                elif col == 'B':
                    Enemy('boss', (x,y), [self.visible_sprites, self.attackable_sprites, self.drop_sprites],
                          self.obstacle_sprites, self.damage_player, self.trigger_death_particles,
                          self.spawn_boss_projectile, self.trigger_boss_effects)

        # Sécurité : si aucune case 'p' n'est trouvée dans la carte, créer un joueur par défaut
        if not hasattr(self, 'player'):
            # Position par défaut : centre de l'écran
            default_x = WIDTH // 2
            default_y = HEIGHT // 2

            self.player = Player(
                (default_x, default_y), [self.visible_sprites],
                self.obstacle_sprites,
                self.create_attack,
                self.destroy_attack,
                self.create_magic,
                self.save_data,
                'sword')

    # --- EFFETS ET COMBAT ---
    def trigger_boss_effects(self, amount, duration):
        self.visible_sprites.shake(amount, duration)
        self.flash_alpha = 255 

    def spawn_boss_projectile(self, style, strength, cost, pos, direction):
        Projectile(style, pos, direction, [self.visible_sprites, self.attack_sprites],
                   self.obstacle_sprites, [self.player], self.player)

    def trigger_dungeon_reward(self):
        self.save_data['life_hearts'] += 1
        self.player.life_hearts = self.save_data['life_hearts'] # Sync avec le player
        self.player.exp += 500
        self.flash_alpha = 150 

    def sync_player_to_save(self):
        """Synchronise les valeurs persistantes du joueur avec la sauvegarde."""
        if hasattr(self, 'player'):
            self.save_data['exp'] = self.player.exp
            self.save_data['rubies'] = self.player.rubies
            self.save_data['life_hearts'] = self.player.life_hearts
            self.save_data['stats'] = self.player.stats
            self.save_data['sword_level'] = self.player.sword_level

    def create_attack(self):
        # Système simplifié : toujours l'épée
        self.current_attack = NewWeapon(self.player, [self.visible_sprites, self.attack_sprites],
                                        'sword', self.obstacle_sprites, self.attackable_sprites)

        # Logique Épée Laser (si 3 cœurs ou plus) conservée
        if self.player.life_hearts >= 3:
            dir_vec = self.player.get_direction_vector()
            Projectile('sword_beam', self.player.rect.center, dir_vec,
                       [self.visible_sprites, self.attack_sprites],
                       self.obstacle_sprites, self.attackable_sprites, self.player, self.victory)

    def create_magic(self, style, strength, cost, element=None, level=None):
        """Système simplifié : seule la boule de feu de base est disponible."""
        if style == 'fireball':
            self.magic_player.fireball(self.player, cost, [self.visible_sprites, self.attack_sprites],
                                       self.obstacle_sprites, self.attackable_sprites, self.victory)

    def destroy_attack(self):
        if self.current_attack: self.current_attack.kill()
        self.current_attack = None

    def player_attack_logic(self):
        if self.attack_sprites:
            # Créer une copie de la liste pour éviter les modifications pendant l'itération
            attack_sprites_copy = self.attack_sprites.sprites().copy()
            for attack_sprite in attack_sprites_copy:
                # Vérifier que le sprite existe encore
                if attack_sprite not in self.attack_sprites:
                    continue

                collision_sprites = pygame.sprite.spritecollide(attack_sprite, self.attackable_sprites, False)
                if collision_sprites:
                    for target_sprite in collision_sprites:
                        if target_sprite.sprite_type == 'enemy':
                            # --- RESET TIMER TÉLÉPORTATION ---
                            target_sprite.last_hit_time = pygame.time.get_ticks()

                            damage_result = target_sprite.get_damage(self.player, 'weapon')
                            if isinstance(damage_result, tuple):
                                exp_gagne, was_boss_killed = damage_result
                                if exp_gagne > 0:
                                    self.player.exp += exp_gagne
                                    # Compter pour les missions (sauf boss et ennemis d'élite)
                                    if not was_boss_killed and target_sprite.monster_name != 'elite_enemy':
                                        self.on_enemy_killed_for_mission()
                                    if was_boss_killed:
                                        self.victory()
                            else:
                                exp_gagne = damage_result
                                if exp_gagne > 0:
                                    self.player.exp += exp_gagne
                                    # Compter pour les missions
                                    if target_sprite.monster_name not in ['boss', 'elite_enemy']:
                                        self.on_enemy_killed_for_mission()
                                    if target_sprite.monster_name == 'boss' and not target_sprite.alive():
                                        self.victory()

    def damage_player(self, amount, attack_type):
        if not self.player.invisible:
            self.player.get_damage(amount)
            # Annuler l'effet des 3 cœurs si le joueur se fait toucher
            if self.player.life_hearts >= 3:
                self.player.life_hearts = 0
                self.save_data['life_hearts'] = 0
            # Mise à jour de la save_data pour l'UI après perte du bonus
            self.save_data['life_hearts'] = self.player.life_hearts
            if self.player.health <= 0: self.player.kill()

    def enemy_teleportation_logic(self):
        """Téléporte les ennemis s'ils n'ont pas été touchés depuis 90 secondes"""
        current_time = pygame.time.get_ticks()
        for enemy in self.attackable_sprites:
            if enemy.sprite_type == 'enemy':
                # Initialisation du timer si inexistant
                if not hasattr(enemy, 'last_hit_time'):
                    enemy.last_hit_time = current_time

                # Si 90 secondes sans dégâts
                if current_time - enemy.last_hit_time >= 90000:
                    angle = random.uniform(0, 2 * math.pi)
                    dist = random.randint(150, 250)
                    new_x = self.player.rect.centerx + math.cos(angle) * dist
                    new_y = self.player.rect.centery + math.sin(angle) * dist
                    
                    # Vérification collision murs
                    temp_rect = enemy.hitbox.copy()
                    temp_rect.center = (new_x, new_y)
                    can_teleport = True
                    for wall in self.obstacle_sprites:
                        if wall.hitbox.colliderect(temp_rect):
                            can_teleport = False
                            break
                    
                    if can_teleport:
                        enemy.hitbox.center = (new_x, new_y)
                        enemy.rect.center = enemy.hitbox.center
                        enemy.last_hit_time = current_time # Reset timer après TP

    def trigger_death_particles(self, pos, particle_type):
        pass

    # --- GESTION DE LA SORTIE ---
    def check_exit_collision(self):
        if hasattr(self, 'exit_sprite'):
            if self.exit_sprite.image.get_alpha() > 0:
                detection_zone = self.exit_sprite.rect.inflate(30, 30)
                if self.player.hitbox.colliderect(detection_zone):
                    self.next_level()

    def check_drop_collection(self):
        """Vérifie si le joueur ramasse des drops"""
        for drop in self.drop_sprites:
            # Vérifier que c'est bien un objet Drop (pas un Enemy)
            if hasattr(drop, 'collect') and drop.hitbox.colliderect(self.player.hitbox):
                drop.collect(self.player)

    def try_spawn_mission(self):
        """Tente de faire apparaître une mission (chance rare)"""
        if self.active_mission is None and random.randint(1, 100) <= 20:  # 20% de chance
            mission_type = random.choice(['elite_hunt', 'speed_kill'])
            self.active_mission = Mission(mission_type)

            if mission_type == 'elite_hunt':
                # Faire apparaître l'ennemi d'élite près du joueur
                max_attempts = 20  # Éviter une boucle infinie
                valid_position = None

                for _ in range(max_attempts):
                    angle = random.uniform(0, 2 * math.pi)
                    dist = random.randint(200, 300)
                    x = self.player.rect.centerx + math.cos(angle) * dist
                    y = self.player.rect.centery + math.sin(angle) * dist

                    # Vérifier que la position est dans les limites de la map
                    map_width = len(self.layout[0]) * TILESIZE if self.layout else WIDTH
                    map_height = len(self.layout) * TILESIZE if self.layout else HEIGHT

                    if 0 <= x < map_width and 0 <= y < map_height:
                        # Vérifier qu'il n'y a pas d'obstacle à cette position
                        temp_rect = pygame.Rect(x - 16, y - 16, 32, 32)  # Taille approximative d'un ennemi
                        collision = False
                        for obstacle in self.obstacle_sprites:
                            if obstacle.hitbox.colliderect(temp_rect):
                                collision = True
                                break

                        if not collision:
                            valid_position = (x, y)
                            break

                # Créer l'ennemi d'élite seulement si on a trouvé une position valide
                if valid_position:
                    self.mission_enemy = Enemy('elite_enemy', valid_position, [self.visible_sprites, self.attackable_sprites, self.drop_sprites],
                                             self.obstacle_sprites, self.damage_player, self.trigger_death_particles)

            elif mission_type == 'speed_kill':
                # Pour la mission speed_kill, faire apparaître quelques ennemis supplémentaires
                self.spawn_mission_enemies(3)  # Faire apparaître 3 ennemis supplémentaires

    def spawn_mission_enemies(self, count):
        """Fait apparaître des ennemis supplémentaires pour les missions"""
        map_width = len(self.layout[0]) * TILESIZE if self.layout else WIDTH
        map_height = len(self.layout) * TILESIZE if self.layout else HEIGHT

        spawned = 0
        max_attempts = 50  # Éviter une boucle infinie

        for _ in range(max_attempts):
            if spawned >= count:
                break

            # Choisir une position aléatoire dans la map (éviter les bords)
            margin = 100
            x = random.randint(margin, map_width - margin)
            y = random.randint(margin, map_height - margin)

            # Vérifier que la position n'est pas sur un obstacle
            temp_rect = pygame.Rect(x - 16, y - 16, 32, 32)
            collision = False
            for obstacle in self.obstacle_sprites:
                if obstacle.hitbox.colliderect(temp_rect):
                    collision = True
                    break

            # Vérifier qu'il n'y a pas d'ennemi déjà présent
            for enemy in self.attackable_sprites:
                if enemy.hitbox.colliderect(temp_rect):
                    collision = True
                    break

            # Vérifier la distance avec le joueur (pas trop près)
            player_dist = pygame.math.Vector2(x, y).distance_to(self.player.rect.center)
            if player_dist < 150:
                collision = True

            if not collision:
                # Créer un ennemi (type aléatoire selon le niveau)
                monster = 'demon' if self.level_number > 2 else 'squid'
                Enemy(monster, (x, y), [self.visible_sprites, self.attackable_sprites],
                      self.obstacle_sprites, self.damage_player, self.trigger_death_particles)
                spawned += 1

    def update_missions(self):
        """Met à jour les missions actives"""
        # Chance de déclencher une mission
        # Mettre à jour la mission active
        if self.active_mission:
            current_time = pygame.time.get_ticks()
            result = self.active_mission.update(self.enemies_killed_in_mission, current_time)

            if result is True:  # Mission réussie
                self.complete_mission()
            elif result is False:  # Mission échouée
                self.fail_mission()

    def complete_mission(self):
        """Termine une mission avec succès"""
        if self.active_mission:
            # Récompenses
            self.player.rubies += self.active_mission.reward_money
            if self.active_mission.reward_heart:
                if self.save_data['life_hearts'] < 3:
                    self.save_data['life_hearts'] += 1
                    self.player.life_hearts = self.save_data['life_hearts']

            # Supprimer l'ennemi de mission s'il existe
            if self.mission_enemy and self.mission_enemy.alive():
                self.mission_enemy.kill()

            self.active_mission = None
            self.mission_enemy = None
            self.enemies_killed_in_mission = 0

    def fail_mission(self):
        """Échoue une mission"""
        if self.active_mission:
            # Supprimer l'ennemi de mission s'il existe
            if self.mission_enemy and self.mission_enemy.alive():
                self.mission_enemy.kill()

            self.active_mission = None
            self.mission_enemy = None
            self.enemies_killed_in_mission = 0

    def on_enemy_killed_for_mission(self):
        """Incrémenter le compteur d'ennemis tués pour la mission de vitesse"""
        if self.active_mission and self.active_mission.type == 'speed_kill':
            self.enemies_killed_in_mission += 1

    def next_level(self):
        self.save_data['current_level'] += 1
        # Si on vient de finir le boss level (niveau 5), passer au niveau 6 (salle vide)
        # mais seulement après avoir collecté la récompense du boss
        if self.level_number == 5:  # Boss level
            # Ajouter une récompense spéciale pour le boss
            self.player.rubies += 700  # Beaucoup d'argent du boss
            self.player.exp += 1000  # EXP bonus
        self.change_level(self.save_data)

    def victory(self):
        # Après avoir tué le boss, faire apparaître l'escalier de sortie au lieu de retourner au niveau 1
        if hasattr(self, 'exit_sprite'):
            self.exit_sprite.image.set_alpha(255)  # Faire apparaître l'escalier
            # Ne pas changer de niveau immédiatement - le joueur doit marcher vers l'escalier

    def input_talents(self):
        keys = pygame.key.get_pressed()
        if self.player.exp >= 500:
            if keys[pygame.K_1]:
                self.player.stats['health'] += 20
                self.player.exp -= 500
            elif keys[pygame.K_2]:
                self.player.stats['attack'] += 5
                self.player.exp -= 500
            elif keys[pygame.K_3]:
                self.player.speed += 0.5
                self.player.exp -= 500

    # Menus d'armes et de magie supprimés : les méthodes associées sont désormais vides
    def input_weapon_menu(self):
        pass

    def input_magic_menu(self):
        pass

    def update_selected_magic(self):
        pass

    def run(self):
        # 1. Rendu et UI
        self.visible_sprites.custom_draw(self.player)
        self.ui.display(self.player, self.save_data)
        
        # 2. Décompte des ennemis (excluant les ennemis de mission)
        enemies = [s for s in self.attackable_sprites if s.sprite_type == 'enemy' and s.monster_name != 'elite_enemy']
        enemy_count = len(enemies)
        self.ui.show_enemy_count(enemy_count)
        
        # Synchronisation du HUD avec les coeurs du joueur
        self.save_data['life_hearts'] = self.player.life_hearts
        if self.save_data['life_hearts'] > 0:
            self.ui.show_special_hearts(self.save_data['life_hearts'])

        # Affichage de la mission active
        if self.active_mission:
            self.ui.display_mission(self.active_mission)

        # 3. Flash blanc
        if self.flash_alpha > 0:
            self.flash_alpha -= 4
            self.flash_surface.set_alpha(self.flash_alpha)
            self.display_surface.blit(self.flash_surface, (0,0))

        # 4. Menus et Logique
        if self.show_help:
            self.ui.display_help()
        elif self.show_talents:
            self.ui.display_talent_menu(self.player)
            self.input_talents()
        else:
            self.visible_sprites.update()
            self.visible_sprites.enemy_update(self.player)
            self.player_attack_logic()
            self.enemy_teleportation_logic()

            # Récompense donjon
            if hasattr(self, 'secret_reward') and self.secret_reward.alive():
                if self.player.hitbox.colliderect(self.secret_reward.rect):
                    self.trigger_dungeon_reward()
                    self.secret_reward.kill()

            # L'escalier devient visible si enemy_count == 0
            if hasattr(self, 'exit_sprite'):
                if enemy_count == 0:
                    self.exit_sprite.image.set_alpha(255)
                    self.check_exit_collision()
                else:
                    self.exit_sprite.image.set_alpha(0)

            # Vérifier la collecte des drops
            self.check_drop_collection()

            # Système de missions
            self.update_missions()

        # Gestion des menus

        if self.show_talents:
            self.ui.display_talent_menu(self.player)
            self.input_talents()

        # Synchroniser chaque frame les données persistantes (XP, rubis, upgrades, etc.)
        self.sync_player_to_save()

# --- GROUPE CAMERA ---
class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()
        self.shake_amount = 0
        self.shake_duration = 0

    def shake(self, amount, duration):
        self.shake_amount = amount
        self.shake_duration = duration

    def custom_draw(self, player):
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height

        if self.shake_duration > 0:
            self.offset.x += random.randint(-self.shake_amount, self.shake_amount)
            self.offset.y += random.randint(-self.shake_amount, self.shake_amount)
            self.shake_duration -= 1

        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)

    def enemy_update(self, player):
        enemy_sprites = [s for s in self.sprites() if hasattr(s, 'sprite_type') and s.sprite_type == 'enemy']
        for enemy in enemy_sprites:
            enemy.enemy_update(player)