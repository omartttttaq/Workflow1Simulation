import pygame
import math
from settings import *

class UI:
    def __init__(self):
        # Informations générales
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)

        # Configuration des barres
        self.health_bar_rect = pygame.Rect(10, 10, HEALTH_BAR_WIDTH, BAR_HEIGHT)
        self.energy_bar_rect = pygame.Rect(10, 34, ENERGY_BAR_WIDTH, BAR_HEIGHT)

    def show_bar(self, current, max_amount, bg_rect, color):
        # Dessiner le fond
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)

        # Convertir les stats en pixels
        ratio = current / max_amount
        current_width = bg_rect.width * ratio
        current_rect = bg_rect.copy()
        current_rect.width = current_width

        # Dessiner la barre
        pygame.draw.rect(self.display_surface, color, current_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)

    def show_enemy_count(self, count):
        """Affiche le nombre d'ennemis restants en haut à droite"""
        text_surf = self.font.render(f'Ennemis: {count}', True, TEXT_COLOR)
        if count == 0:
            text_surf = self.font.render('Sortie déverrouillée !', True, 'Gold')
        
        text_rect = text_surf.get_rect(topright = (WIDTH - 20, 20))
        
        # Fond du texte
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, text_rect.inflate(20, 20))
        self.display_surface.blit(text_surf, text_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, text_rect.inflate(20, 20), 3)

    def show_special_hearts(self, count):
        """Affiche les cœurs de donjons récoltés"""
        for i in range(count):
            x = 10 + (i * 30)
            y = 60
            # Dessine un petit cœur doré ou rouge
            pygame.draw.circle(self.display_surface, 'Gold', (x + 15, y + 15), 10)
            if count >= 3: # Indicateur épée laser
                pygame.draw.circle(self.display_surface, 'White', (x + 15, y + 15), 4)

    def display_help(self):
        """Affiche le guide des touches (H)"""
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(150)
        overlay.fill('black')
        self.display_surface.blit(overlay, (0,0))

        help_text = [
            "=== GUIDE DE SURVIE ===",
            "Z,Q,S,D : Se déplacer",
            "ESPACE : Attaquer à l'épée",
            "CTRL : Lancer la boule de feu",
            "L_SHIFT : Dash / Esquive",
            "T : Menu des Talents (500 XP requis)",
            "H : Fermer ce guide",
            "",
            "OBJECTIF : Tuez tous les ennemis pour",
            "faire apparaître l'escalier de sortie."
        ]

        for i, line in enumerate(help_text):
            surf = self.font.render(line, True, 'White')
            rect = surf.get_rect(center = (WIDTH//2, 150 + i * 40))
            self.display_surface.blit(surf, rect)

    def display_talent_menu(self, player):
        """Interface des talents stylisée avec compteurs et cadres"""
        # 1. Overlay de fond (Sombre et élégant)
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill('#050505')
        self.display_surface.blit(overlay, (0,0))

        # 2. Calcul des points
        talent_pts = player.exp // 500
        next_point_xp = 500 - (player.exp % 500)

        # 3. Titre Principal
        title_surf = self.font.render("MENU DES AMÉLIORATIONS", True, 'Gold')
        title_rect = title_surf.get_rect(center=(WIDTH // 2, 80))
        self.display_surface.blit(title_surf, title_rect)
        pygame.draw.line(self.display_surface, 'Gold', (WIDTH//2 - 150, 105), (WIDTH//2 + 150, 105), 3)

        # 4. Affichage des Stats Globales (XP et Points)
        # Cadre pour les points
        info_rect = pygame.Rect(WIDTH//2 - 200, 130, 400, 80)
        pygame.draw.rect(self.display_surface, '#222222', info_rect, 0, 10) # Fond arrondi
        pygame.draw.rect(self.display_surface, 'Gold', info_rect, 2, 10) # Bordure

        pts_surf = self.font.render(f"POINTS DE TALENT : {talent_pts}", True, '#00FF00')
        self.display_surface.blit(pts_surf, (info_rect.x + 20, info_rect.y + 15))

        xp_surf = self.font.render(f"XP TOTAL : {int(player.exp)}", True, 'White')
        self.display_surface.blit(xp_surf, (info_rect.x + 20, info_rect.y + 45))

        next_surf = self.font.render(f"Prochain point dans : {int(next_point_xp)} XP", True, '#AAAAAA')
        self.display_surface.blit(next_surf, (info_rect.x + 180, info_rect.y + 45))

        # 5. Options d'amélioration
        options = [
            {"key": "1", "name": "Vigueur", "desc": "+20 Vie Maximum", "val": f"{int(player.health)}/{int(player.stats['health'])}"},
            {"key": "2", "name": "Force", "desc": "+5 Dégâts d'Attaque", "val": f"{player.stats['attack']}"},
            {"key": "3", "name": "Agilité", "desc": "+Vitesse de mouvement", "val": f"{round(player.speed, 1)}"}
        ]

        for i, opt in enumerate(options):
            y_pos = 250 + (i * 100)
            item_rect = pygame.Rect(WIDTH//2 - 250, y_pos, 500, 80)

            # Couleur selon disponibilité
            color_border = 'Gold' if talent_pts > 0 else '#444444'
            color_text = 'White' if talent_pts > 0 else 'Gray'

            # Dessin du slot
            pygame.draw.rect(self.display_surface, '#1A1A1A', item_rect, 0, 5)
            pygame.draw.rect(self.display_surface, color_border, item_rect, 2, 5)

            # Texte de l'option
            key_surf = self.font.render(f"[{opt['key']}]", True, color_border)
            self.display_surface.blit(key_surf, (item_rect.x + 15, item_rect.y + 25))

            name_surf = self.font.render(opt['name'], True, color_text)
            self.display_surface.blit(name_surf, (item_rect.x + 70, item_rect.y + 15))

            desc_surf = self.font.render(opt['desc'], True, '#888888')
            self.display_surface.blit(desc_surf, (item_rect.x + 70, item_rect.y + 45))

            val_surf = self.font.render(opt['val'], True, color_border)
            self.display_surface.blit(val_surf, (item_rect.right - 100, item_rect.y + 25))

        # 6. Footer
        exit_surf = self.font.render("Appuyez sur [T] pour fermer", True, '#666666')
        self.display_surface.blit(exit_surf, (WIDTH//2 - 100, HEIGHT - 50))

    def display_weapon_menu(self, player, save_data):
        """Menu des armes désactivé (une seule arme : épée)."""
        pass

    def display_magic_menu(self, player, save_data, cursor_index=0):
        """Menu de magie désactivé (une seule magie : boule de feu)."""
        pass
    def display(self, player, save_data=None):
        # Barres de vie et énergie
        self.show_bar(player.health, player.stats['health'], self.health_bar_rect, HEALTH_COLOR)
        self.show_bar(player.energy, player.stats['energy'], self.energy_bar_rect, ENERGY_COLOR)
        
        # Affichage XP et Rubis
        exp_surf = self.font.render(f'XP: {int(player.exp)}', True, TEXT_COLOR)
        ruby_surf = self.font.render(f'Rubis: {player.rubies}', True, '#FFD700')
        self.display_surface.blit(exp_surf, (10, HEIGHT - 60))
        self.display_surface.blit(ruby_surf, (10, HEIGHT - 30))

        # Affichage simple des contrôles combat
        controls_surf = self.font.render("Épée: ESPACE  |  Feu: CTRL", True, '#FFD700')
        self.display_surface.blit(controls_surf, (WIDTH - 320, HEIGHT - 40))

    def display_mission(self, mission):
        """Affiche la mission active"""
        if mission:
            # Fond de la mission
            mission_rect = pygame.Rect(WIDTH//2 - 200, 10, 400, 60)
            pygame.draw.rect(self.display_surface, '#222222', mission_rect, 0, 10)
            pygame.draw.rect(self.display_surface, '#FFD700', mission_rect, 2, 10)

            # Description
            desc_surf = self.font.render(mission.description, True, 'White')
            self.display_surface.blit(desc_surf, (mission_rect.x + 10, mission_rect.y + 10))

            # Timer ou progression
            if mission.type == 'speed_kill':
                time_left = mission.get_time_left() // 1000
                progress_surf = self.font.render(f"Temps: {time_left}s | Tués: {mission.enemies_killed}/{mission.target_kills}", True, '#FFD700')
            else:  # elite_hunt
                progress_surf = self.font.render("Trouvez et tuez l'ennemi d'élite !", True, '#FFD700')

            self.display_surface.blit(progress_surf, (mission_rect.x + 10, mission_rect.y + 35))