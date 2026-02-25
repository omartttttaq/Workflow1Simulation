import pygame
import math
import random
from settings import *

class SwordTrail(pygame.sprite.Sprite):
    """Classe pour créer les éclats de traînée derrière la lame"""
    def __init__(self, groups, pos, image, angle):
        super().__init__(groups)
        self.sprite_type = 'effect'
        # On crée une copie de l'image tournée pour la traînée
        self.image = image.copy()
        # On rend l'image toute blanche pour l'effet de traînée
        self.image.fill((255, 255, 255, 180), special_flags=pygame.BLEND_RGBA_MULT)
        self.rect = self.image.get_rect(center=pos)
        self.alpha = 150
        self.fade_speed = 25 # Vitesse de disparition

    def update(self):
        # L'effet s'estompe et disparaît
        self.alpha -= self.fade_speed
        self.image.set_alpha(self.alpha)
        if self.alpha <= 0:
            self.kill()

class WeaponProjectile(pygame.sprite.Sprite):
    """Classe de base pour les projectiles d'armes spéciales"""
    def __init__(self, weapon_type, pos, direction, groups, obstacle_sprites, attackable_sprites, player):
        super().__init__(groups)
        self.sprite_type = 'weapon_projectile'
        self.weapon_type = weapon_type
        self.player = player
        self.direction = direction
        self.obstacle_sprites = obstacle_sprites
        self.attackable_sprites = attackable_sprites

        # Configuration selon le type d'arme
        self.setup_weapon()

        self.rect = self.image.get_rect(center=pos)
        self.hitbox = self.rect.copy()
        self.spawn_time = pygame.time.get_ticks()

    def setup_weapon(self):
        if self.weapon_type == 'boomerang':
            self.image = pygame.Surface((16, 16), pygame.SRCALPHA)
            pygame.draw.polygon(self.image, '#8B4513', [(8, 2), (14, 8), (8, 14), (2, 8)])
            pygame.draw.circle(self.image, '#FFD700', (8, 8), 6, 2)
            self.speed = 8
            self.damage = 25
            self.lifetime = 2000
            self.returning = False
            self.return_distance = 0

        elif self.weapon_type == 'bomb':
            self.image = pygame.Surface((12, 12), pygame.SRCALPHA)
            pygame.draw.circle(self.image, '#000000', (6, 6), 6)
            pygame.draw.circle(self.image, '#8B0000', (6, 6), 4)
            self.speed = 6
            self.damage = 50
            self.lifetime = 1500
            self.explosion_timer = None
            self.explosion_radius = 60

        elif self.weapon_type == 'arrow':
            self.image = pygame.Surface((20, 4), pygame.SRCALPHA)
            pygame.draw.rect(self.image, '#8B4513', (0, 1, 16, 2))
            pygame.draw.polygon(self.image, '#C0C0C0', [(16, 0), (20, 2), (16, 4)])
            self.speed = 12
            self.damage = 30
            self.lifetime = 3000

        elif self.weapon_type == 'shotgun':
            # Le shotgun tire 5 projectiles
            self.speed = 10
            self.damage = 20
            self.lifetime = 1000

    def update(self):
        current_time = pygame.time.get_ticks()

        if self.weapon_type == 'boomerang':
            self.update_boomerang(current_time)
        elif self.weapon_type == 'bomb':
            self.update_bomb(current_time)
        elif self.weapon_type == 'arrow':
            self.update_arrow(current_time)
        elif self.weapon_type == 'shotgun':
            self.update_shotgun(current_time)

        # Collision avec les murs
        for sprite in self.obstacle_sprites:
            if sprite.hitbox.colliderect(self.hitbox):
                if self.weapon_type == 'bomb':
                    self.explode()
                else:
                    self.kill()
                return

        # Collision avec les ennemis
        for sprite in self.attackable_sprites:
            if sprite.hitbox.colliderect(self.hitbox) and hasattr(sprite, 'get_damage'):
                damage_result = sprite.get_damage(self.player, 'weapon')
                if self.weapon_type == 'bomb':
                    self.explode()
                elif self.weapon_type != 'boomerang':  # Le boomerang traverse les ennemis
                    self.kill()
                break

        # Durée de vie écoulée
        if current_time - self.spawn_time >= self.lifetime:
            if self.weapon_type == 'bomb':
                self.explode()
            else:
                self.kill()

    def update_boomerang(self, current_time):
        if not self.returning:
            # Aller vers l'avant
            self.hitbox.x += self.direction.x * self.speed
            self.hitbox.y += self.direction.y * self.speed
            self.return_distance += self.speed

            # Commencer à revenir après une certaine distance
            if self.return_distance >= 150:
                self.returning = True
        else:
            # Revenir vers le joueur
            player_vec = pygame.math.Vector2(self.player.rect.center)
            projectile_vec = pygame.math.Vector2(self.hitbox.center)
            return_direction = (player_vec - projectile_vec).normalize()
            self.hitbox.x += return_direction.x * self.speed
            self.hitbox.y += return_direction.y * self.speed

            # Ramasser si proche du joueur
            if projectile_vec.distance_to(player_vec) < 20:
                self.kill()

        self.rect.center = self.hitbox.center

    def update_bomb(self, current_time):
        self.hitbox.x += self.direction.x * self.speed
        self.hitbox.y += self.direction.y * self.speed
        self.rect.center = self.hitbox.center

        # Faire tourner la bombe pour l'effet visuel
        angle = (current_time // 50) % 360
        self.image = pygame.transform.rotate(pygame.Surface((12, 12), pygame.SRCALPHA), angle)
        pygame.draw.circle(self.image, '#000000', (6, 6), 6)
        pygame.draw.circle(self.image, '#8B0000', (6, 6), 4)

    def update_arrow(self, current_time):
        self.hitbox.x += self.direction.x * self.speed
        self.hitbox.y += self.direction.y * self.speed
        self.rect.center = self.hitbox.center

    def update_shotgun(self, current_time):
        self.hitbox.x += self.direction.x * self.speed
        self.hitbox.y += self.direction.y * self.speed
        self.rect.center = self.hitbox.center

    def explode(self):
        """Explosion de la bombe"""
        # Créer un effet d'explosion
        explosion = ExplosionEffect(self.hitbox.center, self.explosion_radius, self.groups())
        explosion.damage_enemies(self.attackable_sprites, self.player, self.damage)
        self.kill()

class ExplosionEffect(pygame.sprite.Sprite):
    """Effet visuel d'explosion"""
    def __init__(self, pos, radius, groups):
        super().__init__(groups)
        self.sprite_type = 'effect'
        self.pos = pos
        self.radius = radius
        self.max_radius = radius
        self.current_radius = 5
        self.expand_speed = 10
        self.alpha = 200

    def damage_enemies(self, attackable_sprites, player, damage):
        """Inflige des dégâts à tous les ennemis dans le rayon"""
        for sprite in attackable_sprites:
            if hasattr(sprite, 'hitbox') and hasattr(sprite, 'get_damage'):
                distance = pygame.math.Vector2(self.pos).distance_to(sprite.hitbox.center)
                if distance <= self.radius:
                    sprite.get_damage(player, 'weapon')

    def update(self):
        self.current_radius += self.expand_speed
        if self.current_radius >= self.max_radius:
            self.kill()
            return

        # Créer l'effet visuel
        self.image = pygame.Surface((self.current_radius * 2, self.current_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 100, 0, self.alpha), (self.current_radius, self.current_radius), self.current_radius)
        pygame.draw.circle(self.image, (255, 200, 0, self.alpha//2), (self.current_radius, self.current_radius), self.current_radius * 0.7)
        self.rect = self.image.get_rect(center=self.pos)
        self.alpha -= 10

class Weapon(pygame.sprite.Sprite):
    def __init__(self, player, groups, weapon_type='sword'):
        super().__init__(groups)
        self.sprite_type = 'weapon'
        self.player = player
        self.weapon_type = 'sword'
        self.groups_list = groups # On garde les groupes pour créer la traînée

        self.setup_sword()

    def setup_sword(self):
        # Paramètres de l'animation
        self.distance = 50
        self.angle_range = 140
        self.animation_speed = 15   # Plus rapide pour l'effet de traînée
        self.current_angle_step = 0

        # Déterminer l'angle de départ
        direction = self.player.status.split('_')[0]
        base_angles = {'up': 90, 'down': 270, 'left': 180, 'right': 0}
        self.start_angle = base_angles.get(direction, 0) - (self.angle_range // 2)

        # Création du visuel de l'épée
        self.original_image = pygame.Surface((54, 16), pygame.SRCALPHA)
        self.draw_master_sword()

        self.image = self.original_image
        self.rect = self.image.get_rect()

    def draw_master_sword(self):
        # Lame
        pygame.draw.rect(self.original_image, '#ACDDF1', (15, 4, 35, 8), border_radius=2)
        # Garde
        pygame.draw.rect(self.original_image, '#0000AA', (10, 0, 6, 16), border_radius=2)
        # Poignée
        pygame.draw.rect(self.original_image, '#8B4513', (0, 5, 10, 6))

    def update(self):
        self.update_sword()

    def update_sword(self):
        # 1. Calcul de l'angle
        self.current_angle_step += self.animation_speed
        angle_rad = math.radians(self.start_angle + self.current_angle_step)

        # 2. Positionnement
        self.rect.centerx = self.player.rect.centerx + math.cos(angle_rad) * self.distance
        self.rect.centery = self.player.rect.centery - math.sin(angle_rad) * self.distance

        # 3. Rotation
        rotation_angle = self.start_angle + self.current_angle_step
        self.image = pygame.transform.rotate(self.original_image, rotation_angle)
        self.rect = self.image.get_rect(center=self.rect.center)

        # 4. CRÉATION DE LA TRAÎNÉE
        # On crée un effet visuel à la position actuelle avant que l'épée ne bouge plus
        SwordTrail(self.groups_list, self.rect.center, self.image, rotation_angle)

        # 5. Fin de l'attaque
        if self.current_angle_step >= self.angle_range:
            self.kill()

class NewWeapon(pygame.sprite.Sprite):
    def __init__(self, player, groups, weapon_type='sword', obstacle_sprites=None, attackable_sprites=None):
        super().__init__(groups)
        self.sprite_type = 'weapon'
        self.player = player
        self.weapon_type = 'sword'
        self.groups_list = groups
        self.obstacle_sprites = obstacle_sprites
        self.attackable_sprites = attackable_sprites

        self.setup_sword()

    def setup_sword(self):
        # Paramètres de l'animation
        self.distance = 50
        self.angle_range = 140
        self.animation_speed = 15   # Plus rapide pour l'effet de traînée
        self.current_angle_step = 0

        # Déterminer l'angle de départ
        direction = self.player.status.split('_')[0]
        base_angles = {'up': 90, 'down': 270, 'left': 180, 'right': 0}
        self.start_angle = base_angles.get(direction, 0) - (self.angle_range // 2)

        # Création du visuel de l'épée
        self.original_image = pygame.Surface((54, 16), pygame.SRCALPHA)
        self.draw_master_sword()

        self.image = self.original_image
        self.rect = self.image.get_rect()

    def draw_master_sword(self):
        # Lame
        pygame.draw.rect(self.original_image, '#ACDDF1', (15, 4, 35, 8), border_radius=2)
        # Garde
        pygame.draw.rect(self.original_image, '#0000AA', (10, 0, 6, 16), border_radius=2)
        # Poignée
        pygame.draw.rect(self.original_image, '#8B4513', (0, 5, 10, 6))

    def update(self):
        self.update_sword()

    def update_sword(self):
        # 1. Calcul de l'angle
        self.current_angle_step += self.animation_speed
        angle_rad = math.radians(self.start_angle + self.current_angle_step)

        # 2. Positionnement
        self.rect.centerx = self.player.rect.centerx + math.cos(angle_rad) * self.distance
        self.rect.centery = self.player.rect.centery - math.sin(angle_rad) * self.distance

        # 3. Rotation
        rotation_angle = self.start_angle + self.current_angle_step
        self.image = pygame.transform.rotate(self.original_image, rotation_angle)
        self.rect = self.image.get_rect(center=self.rect.center)

        # 4. CRÉATION DE LA TRAÎNÉE
        SwordTrail(self.groups_list, self.rect.center, self.image, rotation_angle)

        # 5. Fin de l'attaque
        if self.current_angle_step >= self.angle_range:
            self.kill()