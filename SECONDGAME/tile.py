import pygame
from settings import *

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, groups, sprite_type='wall'):
        super().__init__(groups)
        self.sprite_type = sprite_type
        
        # Taille pour correspondre à Link (16x16 pixels d'origine agrandis 4 fois)
        self.pixel_size = 4 
        self.image = pygame.Surface((16 * self.pixel_size, 16 * self.pixel_size), pygame.SRCALPHA)
        
        self.rect = self.image.get_rect(topleft=pos)
        
        # Gestion des collisions : les murs bloquent, le reste non
        if self.sprite_type == 'wall':
            self.hitbox = self.rect.copy()
        else:
            # Hitbox minuscule au centre pour les objets non-solides (herbe, récompense, escalier)
            self.hitbox = self.rect.inflate(-self.rect.width, -self.rect.height)
            
        self.draw_tile()

    def draw_tile(self):
        """Dessine la tuile pixel par pixel selon son type."""
        self.image.fill((0, 0, 0, 0))
        
        # Initialisation pour éviter les erreurs si sprite_type n'est pas reconnu
        colors = {}
        tile_map = []

        # --- DESIGN DU MUR (Briques de Donjon NES) ---
        if self.sprite_type == 'wall':
            colors = {
                'D': '#404040', # Gris très foncé (Ombre)
                'L': '#A0A0A0', # Gris clair (Lumière)
                'M': '#808080'  # Gris moyen
            }
            tile_map = [
                "LLLLLLLLLLLLLLLL",
                "LMMMMMMMMMMMMMMD",
                "LMMMMMMMMMMMMMMD",
                "LMMMMMMMMMMMMMMD",
                "LDDDDDDDDDDDDDDD",
                "LMMMMMDLMMMMMMMD",
                "LMMMMMDLMMMMMMMD",
                "LMMMMMDLMMMMMMMD",
                "LDDDDDDLDDDDDDDD",
                "LLLLLLLLLLLLLLLL",
                "LMMMMMMMMMMMMMMD",
                "LMMMMMMMMMMMMMMD",
                "LMMMMMMMMMMMMMMD",
                "LDDDDDDDDDDDDDDD",
                "LLLLLLLLLLLLLLLL",
                "DDDDDDDDDDDDDDDD"
            ]

        # --- DESIGN DE L'HERBE (Zelda 1 NES) ---
        elif self.sprite_type == 'grass':
            colors = {
                'G': '#1E7610', # Vert base
                'L': '#ACDF87', # Vert clair (Brin d'herbe)
                'D': '#114408'  # Vert sombre (Ombre)
            }
            tile_map = [
                "GGGGGGGGGGGGGGGG",
                "GGGGGGGGGGGGGGGG",
                "GGGLGGGGGGGLGGGG",
                "GGLLDGGGGGLLDGGG",
                "GGLDDGGGGGLDDGGG",
                "GGGGGGGGGGGGGGGG",
                "GGGGGGGGGGGGGGGG",
                "GGGGGGGGGGGGGGGG",
                "GLGGGGGGGLGGGGGG",
                "LLDGGGGGLLDGGGGG",
                "LDDGGGGGLDDGGGGG",
                "GGGGGGGGGGGGGGGG",
                "GGGGGGGGGGGGGGGG",
                "GGGGGGGGGGGGGGGG",
                "GGGGGGGGGGGGGGGG",
                "GGGGGGGGGGGGGGGG"
            ]

        # --- DESIGN DE L'ESCALIER (Effet de trou/profondeur) ---
        elif self.sprite_type == 'exit':
            colors = {
                '1': '#555555', # Bordure
                '2': '#333333', # Marche 1
                '3': '#111111', # Marche 2
                '0': '#000000'  # Fond du trou
            }
            tile_map = [
                "1111111111111111",
                "1222222222222221",
                "1233333333333221",
                "1230000000003221",
                "1230000000003221",
                "1230000000003221",
                "1230000000003221",
                "1230000000003221",
                "1230000000003221",
                "1230000000003221",
                "1230000000003221",
                "1230000000003221",
                "1230000000003221",
                "1233333333333221",
                "1222222222222221",
                "1111111111111111"
            ]

        # --- DESIGN DE LA RÉCOMPENSE (Cœur de Donjon) ---
        elif self.sprite_type == 'reward':
            colors = {
                'R': '#F83800', # Rouge vif (NES)
                'W': '#FFFFFF', # Blanc (Reflet)
                'B': '#000000'  # Contour noir
            }
            tile_map = [
                "      BBBBBB    ",
                "    BBWWWWWWBB  ",
                "  BBWWWWWWWWWWBB",
                "BBWWWWWWWWWWWWBB",
                "BBRRRRRRRRRRRRBB",
                "BBRRRRRRRRRRRRBB",
                "BBRRRRRRRRRRRRBB",
                "  BBRRRRRRRRBB  ",
                "  BBRRRRRRRRBB  ",
                "    BBRRRRBB    ",
                "    BBRRRRBB    ",
                "      BBBB      ",
                "      BBBB      ",
                "        BB      ",
                "                ",
                "                "
            ]

        # Application de la grille de couleurs sur la surface
        if tile_map:
            for row_index, row in enumerate(tile_map):
                for col_index, char in enumerate(row):
                    if char in colors:
                        pygame.draw.rect(
                            self.image, 
                            colors[char], 
                            (col_index * self.pixel_size, row_index * self.pixel_size, self.pixel_size, self.pixel_size)
                        )
        else:
            # Fallback si rien n'est défini
            self.image.fill('purple')

    def destroy(self):
        """Supprime la tuile du jeu (utilisé pour l'herbe)"""
        self.kill()