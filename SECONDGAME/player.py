import pygame
import math
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, obstacle_sprites, create_attack, destroy_attack, create_magic, save_data, weapon_type='sword'):
        super().__init__(groups)

        # 1. Configuration de base de l'image (Transparence)
        self.image = pygame.Surface((48, 48), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(-6, -26)

        # 2. STATS (Chargées depuis la sauvegarde)
        self.stats = save_data['stats']
        self.health = self.stats['health']
        self.energy = self.stats['magic']
        self.exp = save_data['exp']
        self.speed = self.stats['speed']
        self.rubies = save_data['rubies']
        self.sword_level = save_data['sword_level']

        # 3. ÉTAT ET MOUVEMENT 
        self.status = 'down'
        self.direction = pygame.math.Vector2()
        self.attacking = False
        self.attack_cooldown = 400
        self.attack_time = None
        self.obstacle_sprites = obstacle_sprites
        
        # --- LOGIQUE BONUS 3 COEURS ---
        self.life_hearts = save_data.get('life_hearts', 0)
        self.vulnerable = True
        self.hurt_time = None
        self.invincibility_duration = 500

        # 4. DESSIN INITIAL
        self.draw_player_shape()

        # 5. MÉTHODES ET MAGIE
        self.create_attack = create_attack
        self.destroy_attack = destroy_attack
        self.create_magic = create_magic
        self.weapon_type = weapon_type if weapon_type else 'sword'

        # Système de magie simplifié (une seule magie : boule de feu)
        self.can_cast = True
        self.magic_time = None
        self.magic_cooldown = 800  # Plus long pour éviter le spam

        # Invisibilité
        self.invisible = False

    def get_direction_vector(self):
        """Retourne un vecteur basé sur le statut actuel (Corrige l'AttributeError)"""
        direction = self.status.split('_')[0]
        if direction == 'right': return pygame.math.Vector2(1,0)
        if direction == 'left':  return pygame.math.Vector2(-1,0)
        if direction == 'up':    return pygame.math.Vector2(0,-1)
        return pygame.math.Vector2(0,1) # down

    def draw_player_shape(self, weapon_type=None):
        """Dessine un personnage RPG détaillé avec style Zelda-like."""
        if weapon_type:
            self.weapon_type = weapon_type
        self.image.fill((0, 0, 0, 0))

        # Couleurs améliorées
        CLOTHES = '#4169E1'  # Royal Blue
        SKIN = '#F5DEB3'    # Wheat (warm skin tone)
        HAIR = '#8B4513'    # Saddle Brown
        SHIRT = '#228B22'   # Forest Green
        BELT = '#8B4513'    # Saddle Brown
        BOOTS = '#654321'   # Dark Brown
        HIGHLIGHT = '#FFFFFF'  # White for highlights

        # Effet visuel du bonus (clignotement doré)
        if self.life_hearts >= 3:
            if math.sin(pygame.time.get_ticks() / 50) >= 0:
                CLOTHES = '#FFD700'  # Gold
                HIGHLIGHT = '#FFFF00'  # Yellow highlight

        # Position des yeux selon la direction
        eye_y = 11
        if 'down' in self.status:
            left_eye_x, right_eye_x = 20, 28
        elif 'up' in self.status:
            left_eye_x, right_eye_x = 20, 28  # Même position pour up
        elif 'left' in self.status:
            left_eye_x, right_eye_x = 18, 26
        elif 'right' in self.status:
            left_eye_x, right_eye_x = 22, 30

        # 1. Bottes (base du personnage)
        pygame.draw.rect(self.image, BOOTS, (16, 38, 8, 6))  # Botte gauche
        pygame.draw.rect(self.image, BOOTS, (24, 38, 8, 6))  # Botte droite

        # 2. Jambes (pantalon)
        pygame.draw.rect(self.image, CLOTHES, (18, 28, 6, 12))  # Jambe gauche
        pygame.draw.rect(self.image, CLOTHES, (24, 28, 6, 12))  # Jambe droite

        # 3. Ceinture
        pygame.draw.rect(self.image, BELT, (14, 26, 20, 4))

        # 4. Corps (Tunique)
        pygame.draw.rect(self.image, SHIRT, (16, 18, 16, 10), border_radius=2)
        # Col de la tunique
        pygame.draw.rect(self.image, SHIRT, (18, 16, 12, 4), border_radius=1)

        # 5. Bras
        pygame.draw.rect(self.image, SKIN, (12, 20, 4, 10))  # Bras gauche
        pygame.draw.rect(self.image, SKIN, (32, 20, 4, 10))  # Bras droit

        # 5.5 Arme dans les bras (selon l'arme sélectionnée)
        self.draw_weapon_in_hands()

        # 6. Tête (forme plus détaillée)
        pygame.draw.ellipse(self.image, SKIN, (16, 6, 16, 14))  # Tête ovale

        # 7. Cheveux (style Zelda-like avec mèche)
        pygame.draw.ellipse(self.image, HAIR, (14, 2, 20, 12))  # Chevelure principale
        pygame.draw.ellipse(self.image, HAIR, (18, 0, 12, 8))   # Mèche frontale

        # 8. Yeux (plus détaillés)
        # Pupilles
        pygame.draw.circle(self.image, 'black', (left_eye_x, eye_y), 1)
        pygame.draw.circle(self.image, 'black', (right_eye_x, eye_y), 1)
        # Reflets blancs
        pygame.draw.circle(self.image, 'white', (left_eye_x-1, eye_y-1), 1)
        pygame.draw.circle(self.image, 'white', (right_eye_x-1, eye_y-1), 1)


        # 11. Détails de la tunique (coutures)
        pygame.draw.line(self.image, BELT, (20, 18), (20, 26), 1)  # Couture centrale
        pygame.draw.line(self.image, BELT, (16, 22), (30, 22), 1)  # Ceinture horizontale

        # 12. Highlights sur les bottes
        pygame.draw.line(self.image, HIGHLIGHT, (18, 40), (22, 40), 1)
        pygame.draw.line(self.image, HIGHLIGHT, (26, 40), (30, 40), 1)

    def draw_weapon_in_hands(self):
        """Dessine l'arme sélectionnée dans les mains du joueur"""
        weapon = self.weapon_type if hasattr(self, 'weapon_type') else 'sword'
        if weapon == 'sword':
            # Épée dans la main droite (position verticale)
            pygame.draw.rect(self.image, '#C0C0C0', (34, 18, 2, 12))  # Lame
            pygame.draw.rect(self.image, '#8B4513', (33, 28, 4, 3))   # Garde
            pygame.draw.circle(self.image, '#FFD700', (35, 16), 2)    # Pompeau

        elif weapon == 'boomerang':
            # Boomerang dans la main droite
            pygame.draw.polygon(self.image, '#8B4513', [(34, 18), (38, 22), (34, 26), (30, 22)])  # Forme de boomerang
            pygame.draw.circle(self.image, '#FFD700', (32, 22), 1)  # Détail doré

        elif weapon == 'bomb':
            # Bombe dans la main gauche
            pygame.draw.circle(self.image, '#000000', (10, 22), 3)  # Corps de la bombe
            pygame.draw.circle(self.image, '#8B0000', (10, 22), 2)  # Liquide rouge
            pygame.draw.line(self.image, '#FFFFFF', (10, 20), (10, 19), 1)  # Mèche

        elif weapon == 'bow':
            # Arc dans les deux mains
            pygame.draw.arc(self.image, '#8B4513', (8, 15, 24, 16), 0.3, 2.8, 2)  # Arc courbé
            pygame.draw.line(self.image, '#FFFFFF', (20, 17), (20, 27), 1)  # Corde

        elif weapon == 'shotgun':
            # Fusil à pompe dans les deux mains
            pygame.draw.rect(self.image, '#654321', (8, 20, 8, 3))   # Corps du fusil
            pygame.draw.rect(self.image, '#2F4F4F', (16, 19, 6, 5))  # Canon
            pygame.draw.circle(self.image, '#FFD700', (8, 22), 1)    # Détail métallique

    def input(self):
        if not self.attacking:
            keys = pygame.key.get_pressed()

            # Déplacement
            if keys[pygame.K_UP]:
                self.direction.y = -1
                self.status = 'up'
            elif keys[pygame.K_DOWN]:
                self.direction.y = 1
                self.status = 'down'
            else:
                self.direction.y = 0

            if keys[pygame.K_RIGHT]:
                self.direction.x = 1
                self.status = 'right'
            elif keys[pygame.K_LEFT]:
                self.direction.x = -1
                self.status = 'left'
            else:
                self.direction.x = 0

            # Attaque Épée
            if keys[pygame.K_SPACE]:
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()
                self.create_attack()

            # Attaque Magique - simple boule de feu
            if keys[pygame.K_LCTRL] and self.can_cast:
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()
                self.create_magic('fireball', 15, 20)  # force/cout de base

    def get_damage(self, amount, attack_type=None):

        """Version ultra-sécurisée contre les inversions d'arguments"""

        # 2. Correction dynamique de l'erreur TypeError
        # Si 'amount' est l'objet Player et 'attack_type' est un nombre
        if not isinstance(amount, (int, float)) and isinstance(attack_type, (int, float)):
            actual_damage = attack_type
        # Si 'amount' est un nombre (cas normal)
        elif isinstance(amount, (int, float)):
            actual_damage = amount
        # Si aucun n'est un nombre (sécurité finale)
        else:
            actual_damage = 10 

        # 3. Application des dégâts
        if self.vulnerable:
            self.health -= actual_damage
            self.vulnerable = False
            self.hurt_time = pygame.time.get_ticks()
            
            # Reset Bonus 3 Coeurs
            if self.life_hearts >= 3:
                self.life_hearts = 0
                self.sword_level = 1

    def move(self, speed):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        self.hitbox.x += self.direction.x * speed
        self.collision('horizontal')
        self.hitbox.y += self.direction.y * speed
        self.collision('vertical')
        self.rect.center = self.hitbox.center

    def collision(self, direction):
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0: self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0: self.hitbox.left = sprite.hitbox.right

        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0: self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0: self.hitbox.top = sprite.hitbox.bottom

    def cooldowns(self):
        current_time = pygame.time.get_ticks()
        if self.attacking:
            if current_time - self.attack_time >= self.attack_cooldown:
                self.attacking = False
                self.destroy_attack()
        
        if not self.vulnerable:
            if current_time - self.hurt_time >= self.invincibility_duration:
                self.vulnerable = True

    def energy_recovery(self):
        if self.energy < self.stats['magic']:
            self.energy += 0.2  # Régénération plus rapide (0.2 au lieu de 0.05)
        else:
            self.energy = self.stats['magic']

    def update(self):
        self.input()
        self.cooldowns()
        self.energy_recovery()
        
        # Gestion de l'invisibilité (Alpha)
        if self.invisible:
            self.image.set_alpha(100)
        else:
            self.image.set_alpha(255)
            
        # Redessiner pour mettre à jour le regard et l'effet de clignotement
        self.draw_player_shape()
        self.move(self.speed)