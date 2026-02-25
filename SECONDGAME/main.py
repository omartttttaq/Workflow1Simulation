import pygame, sys
from settings import *
from level import Level
from save_manager import SaveManager
import os

class Game:
    def __init__(self):
        # Configuration initiale de Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Zelda RPG - New Game+ Edition')
        self.clock = pygame.time.Clock()

        # 1. Gestionnaire de sauvegarde
        self.save_manager = SaveManager()
        self.data = self.save_manager.load()
# SUPPRIMEZ OU COMMENTEZ CETTE LIGNE :
        # self.generate_world_maps() 

        # Initialisation des données de sauvegarde
        # Dans main.py, à l'intérieur de class Game, méthode __init__
        self.data = {
            'current_level': 1,
            'health': 200,
            'exp': 0,
            'rubies': 0,
            'life_hearts': 0 ,
            'sword_level': 1,
    # AJOUTEZ CE BLOC 'stats' ICI :
            'stats': {
                'health': 100, 
                'energy': 60, 
                'attack': 10, 
                'magic': 4, 
                'speed': 5
            }
        }
        # Lancer le premier niveau
        self.level = Level(self.data, self.update_save_data)

        # 3. États du jeu
        self.game_state = 'MENU'
        self.level = None
        self.last_escape_time = 0 # Pour le double Échap
        self.font = pygame.font.Font(UI_FONT, 50)


    def start_game(self, is_new=True):
        if is_new:
            self.data = self.save_manager.default_data
        else:
            self.data = self.save_manager.load()
        
        self.level = Level(self.data, self.update_save_data)
        self.game_state = 'PLAYING'

    def update_save_data(self, new_data):
        """Callback utilisé par Level pour sauvegarder la progression."""
        self.data = new_data
        self.save_manager.save(self.data)
        # On recharge le niveau avec les nouvelles données (ex: passage au niveau suivant)
        self.level = Level(self.data, self.update_save_data)

    def draw_menu(self):
        # 1. Arrière-plan stylisé (Dégradé ou Couleur sombre profonde)
        self.screen.fill('#0a0a0c')
        
        # Petit effet de "vignettage" (bordures sombres)
        for i in range(10):
            alpha = 150 - (i * 15)
            s = pygame.Surface((WIDTH, HEIGHT))
            s.set_alpha(alpha)
            s.fill('#000000')
            pygame.draw.rect(s, (0,0,0,0), (i*20, i*20, WIDTH-(i*40), HEIGHT-(i*40)))
            self.screen.blit(s, (0,0))

        # 2. Titre avec Ombre portée
        title_text = "ZELDA ADVENTURE"
        # Ombre
        shadow_surf = self.font.render(title_text, True, '#3d2b00')
        shadow_rect = shadow_surf.get_rect(center=(WIDTH//2 + 4, 154))
        self.screen.blit(shadow_surf, shadow_rect)
        # Texte principal
        title_surf = self.font.render(title_text, True, 'gold')
        title_rect = title_surf.get_rect(center=(WIDTH//2, 150))
        self.screen.blit(title_surf, title_rect)

        # 3. Gestion des boutons et des interactions
        mouse_pos = pygame.mouse.get_pos()
        btn_new = pygame.Rect(WIDTH//2 - 150, 300, 300, 60)
        btn_cont = pygame.Rect(WIDTH//2 - 150, 400, 300, 60)

        for btn, text in [(btn_new, "NOUVEAU JEU"), (btn_cont, "CONTINUER")]:
            # Effet Hover (si la souris est sur le bouton)
            is_hovered = btn.collidepoint(mouse_pos)
            bg_color = '#444444' if is_hovered else '#222222'
            border_color = 'gold' if is_hovered else '#666666'
            text_color = 'white' if not is_hovered else 'gold'
            
            # Dessin du bouton (Fond + Bordure)
            pygame.draw.rect(self.screen, bg_color, btn, border_radius=12)
            pygame.draw.rect(self.screen, border_color, btn, 3, border_radius=12)

            # Texte du bouton centré
            text_surf = self.font.render(text, True, text_color)
            text_rect = text_surf.get_rect(center=btn.center)
            self.screen.blit(text_surf, text_rect)

        return btn_new, btn_cont

    def draw_game_over(self):
        self.screen.fill('black')
        go_surf = self.font.render("GAME OVER", True, 'red')
        self.screen.blit(go_surf, (WIDTH//2 - 120, HEIGHT//2 - 50))
        retry_surf = pygame.font.Font(None, 30).render("Appuyez sur R pour le Menu", True, 'white')
        self.screen.blit(retry_surf, (WIDTH//2 - 110, HEIGHT//2 + 50))

    def run(self):
        while True:
            # --- GESTION DES ÉVÉNEMENTS ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if self.level: self.update_save_data(self.level.save_data)
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    # Double Échap pour quitter
                    if event.key == pygame.K_ESCAPE:
                        current_time = pygame.time.get_ticks()
                        if current_time - self.last_escape_time < 500:
                            if self.level: self.update_save_data(self.level.save_data)
                            pygame.quit()
                            sys.exit()
                        self.last_escape_time = current_time

                    # Touche T pour le Menu des Talents
                    if self.game_state == 'PLAYING' and event.key == pygame.K_t:
                        self.level.show_talents = not self.level.show_talents

                    # Menus d'armes et de magie supprimés : M et K ne font plus rien
                    
                    # Touche R pour recommencer après Game Over
                    if self.game_state == 'GAMEOVER' and event.key == pygame.K_r:
                        self.game_state = 'MENU'

                if self.game_state == 'MENU' and event.type == pygame.MOUSEBUTTONDOWN:
                    btn_new, btn_cont = self.draw_menu()
                    if btn_new.collidepoint(event.pos):
                        self.start_game(is_new=True)
                    elif btn_cont.collidepoint(event.pos):
                        self.start_game(is_new=False)

            # --- MISE À JOUR ET DESSIN ---
            if self.game_state == 'MENU':
                self.draw_menu()
            
            elif self.game_state == 'PLAYING':
                self.screen.fill('black')
                self.level.run()
                
                # Vérification de la mort du joueur
                if self.level.player.health <= 0:
                    self.game_state = 'GAMEOVER'
            
            elif self.game_state == 'GAMEOVER':
                self.draw_game_over()

            pygame.display.update()
            self.clock.tick(FPS)

if __name__ == '__main__':
    game = Game()
    game.run()