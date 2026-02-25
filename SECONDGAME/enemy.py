import pygame
import random
import math
from settings import *
from drop import Drop

class Enemy(pygame.sprite.Sprite):
    def __init__(self, monster_name, pos, groups, obstacle_sprites, damage_player, trigger_death_particles, create_magic=None, trigger_shake=None):
        super().__init__(groups)
        self.sprite_type = 'enemy'
        self.monster_name = monster_name
        self.create_magic = create_magic
        self.trigger_shake = trigger_shake
        self.groups_list = groups  # Sauvegarder les groupes pour créer les drops
        self.attack_cooldown = 1000

        # --- STATS ET CONFIGURATION ---
        if monster_name == 'squid':
            self.health = 40 
            self.speed = 3
            self.attack_damage = 10
            self.image_size = (64, 64)
        elif monster_name == 'raccoon':
            self.health = 60 
            self.speed = 2.5
            self.attack_damage = 15
            self.image_size = (64, 64)
        elif monster_name == 'demon':
            self.health = 80 
            self.speed = 3.5
            self.attack_damage = 20
            self.image_size = (64, 64)
        elif monster_name == 'boss':
            self.health = 200
            self.speed = 2
            self.attack_damage = 40
            self.image_size = (96, 96)
            # Logique Boss
            self.enraged = False
            self.current_pattern = 'follow'
            self.last_pattern_change = pygame.time.get_ticks()
            self.pattern_duration = 3000
            self.attack_cooldown = 1500

        elif monster_name == 'elite_enemy':
            self.health = 150
            self.speed = 4.5  # Très rapide
            self.attack_damage = 25
            self.image_size = (64, 64)
            self.exp = 300  # Plus d'EXP 

        # --- VISUEL ET PHYSIQUE ---
        self.image = pygame.Surface(self.image_size, pygame.SRCALPHA)
        self.draw_monster_shape()
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(-10, -10)
        self.obstacle_sprites = obstacle_sprites
        
        self.direction = pygame.math.Vector2()
        self.knockback_vector = pygame.math.Vector2()
        self.exp = 2000 if monster_name == 'boss' else 100
        
        # --- TIMERS ET ÉTATS ---
        self.damage_player = damage_player
        self.trigger_death_particles = trigger_death_particles
        self.can_attack = True
        self.attack_time = None
        self.vulnerable = True
        self.hit_time = None
        self.invincibility_duration = 400 

    def draw_monster_shape(self):
        self.image.fill((0, 0, 0, 0)) 
        
        if self.monster_name == 'squid':
            pygame.draw.ellipse(self.image, '#FF4444', (12, 10, 40, 45))
            pygame.draw.circle(self.image, 'white', (24, 25), 6)
            pygame.draw.circle(self.image, 'white', (40, 25), 6)
            pygame.draw.circle(self.image, 'black', (24, 25), 2)
            pygame.draw.circle(self.image, 'black', (40, 25), 2)
            for i in range(4):
                pygame.draw.rect(self.image, '#CC0000', (16 + (i*8), 48, 6, 12), border_radius=2)
                
        elif self.monster_name in ['raccoon', 'demon']:
            color = '#885522' if self.monster_name == 'raccoon' else '#333333'
            pygame.draw.circle(self.image, color, (32, 35), 25)
            pygame.draw.rect(self.image, '#222222', (15, 28, 34, 12), border_radius=5)
            eye_color = 'yellow' if self.monster_name == 'raccoon' else 'red'
            pygame.draw.circle(self.image, eye_color, (24, 34), 3)
            pygame.draw.circle(self.image, eye_color, (40, 34), 3)
            
        elif self.monster_name == 'boss':
            body_color = '#4B0082' if not getattr(self, 'enraged', False) else '#AA0000'
            aura_color = 'purple' 
            if hasattr(self, 'current_pattern'):
                if self.current_pattern == 'circle': aura_color = 'red'
                if self.current_pattern == 'burst': aura_color = 'orange'
                if self.current_pattern == 'berserk': aura_color = 'white'

            pygame.draw.rect(self.image, body_color, (10, 20, 76, 66), border_radius=15)
            pygame.draw.polygon(self.image, 'gold', [(20, 20), (35, 0), (48, 20), (61, 0), (76, 20)])
            pygame.draw.circle(self.image, 'white', (48, 50), 18)
            pygame.draw.circle(self.image, 'red', (48, 50), 10)
            pygame.draw.circle(self.image, 'black', (48, 50), 5)
            pygame.draw.rect(self.image, aura_color, (10, 20, 76, 66), 6, border_radius=15)

        elif self.monster_name == 'elite_enemy':
            # Ennemi d'élite avec un design spécial (rouge et noir)
            body_color = '#8B0000'  # Rouge foncé
            highlight_color = '#FF0000'  # Rouge clair

            # Corps principal
            pygame.draw.ellipse(self.image, body_color, (10, 15, 44, 34))

            # Marques spéciales (comme des scarifications ou armure)
            pygame.draw.line(self.image, '#000000', (20, 20), (44, 20), 3)
            pygame.draw.line(self.image, '#000000', (20, 25), (44, 25), 3)
            pygame.draw.line(self.image, '#000000', (20, 30), (44, 30), 3)

            # Yeux rougeoyants
            pygame.draw.circle(self.image, highlight_color, (24, 22), 4)
            pygame.draw.circle(self.image, highlight_color, (40, 22), 4)
            pygame.draw.circle(self.image, '#FFFFFF', (24, 22), 2)
            pygame.draw.circle(self.image, '#FFFFFF', (40, 22), 2)

            # Aura rouge
            pygame.draw.ellipse(self.image, '#FF4444', (10, 15, 44, 34), 2)

    def get_player_distance_direction(self, player):
        enemy_vec = pygame.math.Vector2(self.rect.center)
        player_vec = pygame.math.Vector2(player.rect.center)
        distance = (player_vec - enemy_vec).magnitude()
        direction = (player_vec - enemy_vec).normalize() if distance > 0 else pygame.math.Vector2()
        return (distance, direction)

    def boss_logic(self, player):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_pattern_change >= self.pattern_duration:
            patterns = ['follow', 'circle', 'burst']
            if getattr(self, 'enraged', False): patterns.append('berserk')
            self.current_pattern = random.choice(patterns)
            self.last_pattern_change = current_time
            self.draw_monster_shape()

        dist, dir = self.get_player_distance_direction(player)
        
        if self.current_pattern == 'follow':
            self.direction = dir
        elif self.current_pattern == 'circle':
            self.direction = pygame.math.Vector2(0,0)
            if self.can_attack:
                self.shoot_circle()
                self.can_attack = False
                self.attack_time = current_time
        elif self.current_pattern == 'burst':
            self.direction = dir * 0.5
            if self.can_attack:
                self.create_magic('fireball', 20, 0, self.rect.center, dir)
                self.can_attack = False
                self.attack_time = current_time
        elif self.current_pattern == 'berserk':
            self.direction = dir
            self.move_berserk(dir)

    def move_berserk(self, dir):
        speed_boost = 6 if self.enraged else 4
        self.hitbox.x += dir.x * speed_boost
        self.collision('horizontal')
        self.hitbox.y += dir.y * speed_boost
        self.collision('vertical')

    def shoot_circle(self):
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            direction = pygame.math.Vector2(math.cos(rad), math.sin(rad))
            self.create_magic('fireball', 20, 0, self.rect.center, direction)

    def actions(self, player):
        if self.monster_name == 'boss':
            self.boss_logic(player)
        else:
            dist, dir = self.get_player_distance_direction(player)
            if dist <= 50 and self.can_attack:
                self.attack_time = pygame.time.get_ticks()
                self.damage_player(self.attack_damage, 'physical')
                self.can_attack = False
            elif dist <= 400: self.direction = dir
            else: self.direction = pygame.math.Vector2()

    def move(self, speed):
        if not self.vulnerable:
            # --- RECUL SÉCURISÉ (Empêche de traverser les murs) ---
            self.hitbox.x += self.knockback_vector.x
            self.collision('horizontal')
            self.hitbox.y += self.knockback_vector.y
            self.collision('vertical')
            # Friction : s'arrête plus vite (0.7 au lieu de 0.9)
            self.knockback_vector *= 0.7
        else:
            # --- MOUVEMENT NORMAL ---
            self.hitbox.x += self.direction.x * speed
            self.collision('horizontal')
            self.hitbox.y += self.direction.y * speed
            self.collision('vertical')

        self.rect.center = self.hitbox.center

    def enemy_collision(self, direction):
        """Gestion des collisions entre ennemis pour éviter l'entassement"""
        # Obtenir tous les autres ennemis
        enemy_sprites = [sprite for sprite in self.groups()[0] if hasattr(sprite, 'sprite_type') and sprite.sprite_type == 'enemy' and sprite != self]

        for enemy in enemy_sprites:
            if enemy.hitbox.colliderect(self.hitbox):
                if direction == 'horizontal':
                    if self.direction.x > 0:
                        self.hitbox.right = enemy.hitbox.left
                    if self.direction.x < 0:
                        self.hitbox.left = enemy.hitbox.right
                if direction == 'vertical':
                    if self.direction.y > 0:
                        self.hitbox.bottom = enemy.hitbox.top
                    if self.direction.y < 0:
                        self.hitbox.top = enemy.hitbox.bottom

    def collision(self, direction):
        # Collisions avec les murs
        for sprite in self.obstacle_sprites:
            if sprite.hitbox.colliderect(self.hitbox):
                if direction == 'horizontal':
                    # Détection selon la direction du mouvement OU du knockback
                    if self.direction.x > 0 or self.knockback_vector.x > 0: self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0 or self.knockback_vector.x < 0: self.hitbox.left = sprite.hitbox.right
                if direction == 'vertical':
                    if self.direction.y > 0 or self.knockback_vector.y > 0: self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0 or self.knockback_vector.y < 0: self.hitbox.top = sprite.hitbox.bottom

        # Collisions avec les autres ennemis
        self.enemy_collision(direction)

    def get_damage(self, player, attack_type):
        if self.vulnerable:
            # Calcul dégâts
            damage = player.stats['attack'] * (1 + (player.sword_level * 0.5)) if attack_type == 'weapon' else 30
            self.health -= damage
            
            # Déclenchement Phase 2 Boss
            if self.monster_name == 'boss' and not self.enraged and self.health <= 100:
                self.enraged = True
                self.speed *= 1.5
                self.attack_cooldown /= 2
                self.pattern_duration = 1500
                if self.trigger_shake: self.trigger_shake(15, 40)
                self.draw_monster_shape()

            if self.health > 0:
                player_pos = pygame.math.Vector2(player.rect.center)
                enemy_pos = pygame.math.Vector2(self.rect.center)
                
                # Appliquer Knockback (Sauf pour le Boss pour éviter qu'il sorte de la petite map)
                if (enemy_pos - player_pos).magnitude() != 0:
                    # Force réduite pour éviter l'effet de "téléportation" lors des collisions
                    force = 0 if self.monster_name == 'boss' else 3
                    self.knockback_vector = (enemy_pos - player_pos).normalize() * force
                
                self.vulnerable = False
                self.hit_time = pygame.time.get_ticks()
                self.image.fill((255, 0, 0, 150), special_flags=pygame.BLEND_RGBA_MULT)

            if self.health <= 0:
                was_boss = self.monster_name == 'boss'

                # Chance de drop (15% pour les ennemis normaux, 100% pour le boss)
                drop_chance = 100 if was_boss else 15
                if random.randint(1, 100) <= drop_chance:
                    # Créer un drop
                    drop_type = 'money_bag' if random.randint(1, 2) == 1 else 'health_potion'
                    Drop(self.rect.center, drop_type, self.groups_list)

                self.kill()
                return (self.exp, was_boss)
        return 0

    def cooldowns(self):
        current_time = pygame.time.get_ticks()
        if not self.can_attack:
            if current_time - self.attack_time >= self.attack_cooldown:
                self.can_attack = True
        if not self.vulnerable:
            if current_time - self.hit_time >= self.invincibility_duration:
                self.vulnerable = True
                self.draw_monster_shape()

    def update(self):
        self.move(self.speed)
        self.cooldowns()

    def enemy_update(self, player):
        self.actions(player)