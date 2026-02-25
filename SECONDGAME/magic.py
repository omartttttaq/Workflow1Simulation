import pygame
from settings import *
from random import randint

class MagicPlayer:
    def __init__(self, animation_player):
        self.animation_player = animation_player

    def fireball(self, player, cost, groups, obstacle_sprites, attackable_sprites, boss_victory_callback=None):
        """Magie unique : boule de feu de base."""
        if player.energy >= cost:
            player.energy -= cost

            # Déterminer la direction du projectile selon le regard du joueur
            direction = pygame.math.Vector2(0,0)
            if 'right' in player.status: direction = pygame.math.Vector2(1,0)
            elif 'left' in player.status: direction = pygame.math.Vector2(-1,0)
            elif 'up' in player.status: direction = pygame.math.Vector2(0,-1)
            else: direction = pygame.math.Vector2(0,1)

            # Créer le projectile
            Projectile('fireball', player.rect.center, direction, groups, obstacle_sprites, attackable_sprites, player, boss_victory_callback)

    def cast_ice_spell(self, player, level, spell_data, attackable_sprites):
        print(f"Lancement glace niveau {level}")  # Debug
        if level == 1:
            # Gel - ralentit avec effet visuel
            affected_count = 0
            for sprite in attackable_sprites:
                dist = (pygame.math.Vector2(sprite.rect.center) - pygame.math.Vector2(player.rect.center)).magnitude()
                if dist < 150 and hasattr(sprite, 'speed'):
                    sprite.speed *= 0.3  # Ralentissement à 30%
                    sprite.frozen_timer = pygame.time.get_ticks() + 3000  # 3 secondes
                    affected_count += 1

            # Effet visuel : cercle de gel
            if affected_count > 0:
                freeze_effect = IceFreezeEffect(player.rect.center, 150)
                # On ne peut pas ajouter directement aux groupes ici, mais l'effet sera visible temporairement
        elif level == 6:
            print("Explosion glacée niveau 6")  # Debug
            # Explosion glacée
            IceExplosion(player.rect.center, attackable_sprites, spell_data['damage'])
        elif level == 10:
            print("Gel instantané niveau 10")  # Debug
            # Gel instantané
            killed_count = 0
            for sprite in attackable_sprites:
                dist = (pygame.math.Vector2(sprite.rect.center) - pygame.math.Vector2(player.rect.center)).magnitude()
                if dist < 100 and hasattr(sprite, 'health'):
                    sprite.health = 0  # Mort instantanée
                    killed_count += 1
            print(f"Gel instantané: {killed_count} ennemis tués")  # Debug

    def cast_water_spell(self, player, level, spell_data, groups, attackable_sprites, player_ref):
        direction = pygame.math.Vector2(0, 0)
        if 'right' in player.status: direction = pygame.math.Vector2(1, 0)
        elif 'left' in player.status: direction = pygame.math.Vector2(-1, 0)
        elif 'up' in player.status: direction = pygame.math.Vector2(0, -1)
        else: direction = pygame.math.Vector2(0, 1)

        if level == 1:
            print("Jet d'eau niveau 1: repousse les ennemis")  # Debug
            # Jet d'eau - repousse avec effet visuel
            WaterJetProjectile(player_ref.rect.center, direction, groups, attackable_sprites, spell_data['damage'])
            # Effet visuel autour du joueur
            push_effect = WaterPushEffect(player_ref.rect.center, 100)
            groups[0].add(push_effect)
        elif level == 6:
            print("Prison d'eau niveau 6")  # Debug
            # Prison d'eau
            WaterPrisonProjectile(player_ref.rect.center, direction, groups, attackable_sprites, spell_data['damage'])
        elif level == 10:
            print("Eau vitalisante niveau 10")  # Debug
            # Eau vitalisante
            HealingWaterProjectile(player_ref.rect.center, direction, groups, attackable_sprites, player_ref, spell_data['damage'])

    def cast_wind_spell(self, player, level, spell_data, groups, attackable_sprites, player_ref):
        print(f"Lancement vent niveau {level}")  # Debug
        if level == 1:
            print("Dash de vent niveau 1")  # Debug
            # Dash avec effet visuel
            WindDash(player_ref)
            # Effet visuel temporaire autour du joueur
            dash_effect = WindDashEffect(player_ref)
            groups[0].add(dash_effect)  # Ajouter au groupe visible
        elif level == 6:
            print("Tourbillon de vent niveau 6")  # Debug
            # Tourbillon
            WindVortex(player_ref.rect.center, groups, attackable_sprites, spell_data['damage'])
        elif level == 10:
            print("Lames d'air niveau 10")  # Debug
            # Lames d'air
            WindBlades(player_ref.rect.center, groups, attackable_sprites, spell_data['damage'])

    # Les autres magies (glace, eau, vent, invisibilité, etc.) ont été supprimées

class Projectile(pygame.sprite.Sprite):
    def __init__(self, type, pos, direction, groups, obstacle_sprites, attackable_sprites, player, boss_victory_callback=None):
        super().__init__(groups)
        self.player = player # On garde une référence au joueur
        self.boss_victory_callback = boss_victory_callback
        self.sprite_type = 'projectile'
        self.image = pygame.Surface((32, 32))
        if type == 'fireball':
            self.image.fill('orange')
        elif type == 'sword_beam':
            self.image.fill('red')
        else:
            self.image.fill('blue')
        self.rect = self.image.get_rect(center = pos)

        self.direction = direction
        self.speed = 10
        self.obstacle_sprites = obstacle_sprites
        self.attackable_sprites = attackable_sprites

        self.spawn_time = pygame.time.get_ticks()
        self.duration = 1500
        self.pierces_walls = (type == 'sword_beam')  # Sword beams pierce walls 

    def update(self):
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed

        # Collision murs (sauf si perce les murs)
        if not self.pierces_walls:
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.rect):
                    self.kill()
                    break

        # Collision Ennemis avec récompenses
        attackable_sprites_copy = self.attackable_sprites.sprites().copy()
        for sprite in attackable_sprites_copy:
            # Vérifier que le sprite existe encore
            if sprite not in self.attackable_sprites or not hasattr(sprite, 'hitbox'):
                continue

            if sprite.hitbox.colliderect(self.rect):
                if hasattr(sprite, 'get_damage'):
                    # On passe self.player au lieu de None pour l'EXP
                    damage_result = sprite.get_damage(self.player, 'fireball')
                    if isinstance(damage_result, tuple):
                        exp_gagne, was_boss_killed = damage_result
                        if exp_gagne and exp_gagne > 0:
                            self.player.exp += exp_gagne
                            self.player.rubies += randint(5, 15)
                            if was_boss_killed and self.boss_victory_callback:
                                self.boss_victory_callback()
                    else:
                        exp_gagne = damage_result
                        if exp_gagne and exp_gagne > 0:
                            self.player.exp += exp_gagne
                            self.player.rubies += randint(5, 15)
                self.kill()
                break  # Sortir de la boucle après avoir touché un ennemi

        if pygame.time.get_ticks() - self.spawn_time >= self.duration:
            self.kill()

    # Les classes avancées de projectiles/effets (explosions, glace, eau, vent...)
    # ont été supprimées pour simplifier le système de magie.