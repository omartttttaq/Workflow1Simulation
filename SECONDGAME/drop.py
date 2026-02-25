import pygame
import random
import math
from settings import *

class Drop(pygame.sprite.Sprite):
    def __init__(self, pos, drop_type, groups):
        super().__init__(groups)
        self.sprite_type = 'drop'
        self.drop_type = drop_type

        # Créer l'image selon le type (taille un peu plus grande pour plus de lisibilité)
        self.image = pygame.Surface((24, 24), pygame.SRCALPHA)
        self.draw_drop()
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = self.rect.inflate(-4, -4)

        # Animation de flottement
        self.float_offset = 0
        self.float_speed = 2
        self.float_amplitude = 3

    def draw_drop(self):
        self.image.fill((0, 0, 0, 0))  # Transparent

        if self.drop_type == 'health_potion':
            # Potion rouge de soin
            pygame.draw.rect(self.image, '#8B0000', (6, 10, 12, 10), border_radius=3)  # Corps
            pygame.draw.rect(self.image, '#FF0000', (8, 8, 8, 8))  # Liquide
            pygame.draw.circle(self.image, '#FFFFFF', (12, 6), 3)  # Bulle

        elif self.drop_type == 'money_bag':
            # Sac d'argent doré
            pygame.draw.ellipse(self.image, '#FFD700', (4, 8, 16, 10))  # Sac
            pygame.draw.line(self.image, '#000000', (12, 8), (12, 3), 2)  # Corde
            pygame.draw.circle(self.image, '#FFFF00', (10, 12), 2)  # Pièce
            pygame.draw.circle(self.image, '#FFFF00', (14, 12), 2)  # Pièce

    def update(self):
        # Animation de flottement
        self.float_offset += self.float_speed
        self.rect.y += self.float_amplitude * math.sin(self.float_offset * 0.1) * 0.1

    def collect(self, player):
        """Méthode appelée quand le joueur ramasse le drop"""
        if self.drop_type == 'health_potion':
            heal_amount = min(50, player.stats['health'] - player.health)  # Soigne jusqu'à 50 HP
            player.health += heal_amount
            if player.health > player.stats['health']:
                player.health = player.stats['health']
        elif self.drop_type == 'money_bag':
            money_amount = random.randint(50, 150)
            player.rubies += money_amount

        self.kill()  # Supprimer le drop après collecte