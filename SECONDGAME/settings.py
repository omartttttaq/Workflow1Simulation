import pygame

# --- CONFIGURATION GÉNÉRALE ---
WIDTH = 1280
HEIGHT = 720
FPS = 60
TILESIZE = 64

# --- INTERFACE UTILISATEUR (UI) ---
BAR_HEIGHT = 20
HEALTH_BAR_WIDTH = 200
ENERGY_BAR_WIDTH = 140
UI_FONT = None
UI_FONT_SIZE = 18

# Couleurs
UI_BG_COLOR = '#222222'
UI_BORDER_COLOR = '#111111'
TEXT_COLOR = '#EEEEEE'
HEALTH_COLOR = '#ed3b3b'
ENERGY_COLOR = '#2662e2'
UI_BORDER_COLOR_ACTIVE = 'gold'

# --- ÉQUILIBRAGE DU JEU ---
# Prix de la boutique
SHOP_PRICES = {
    'health_upgrade': 100,
    'strength_upgrade': 150,
    'speed_upgrade': 200,
    'magic_potion': 50
}

# Statistiques de la magie : on ne garde que la boule de feu de base
MAGIC_DATA = {
    'fireball': {'strength': 15, 'cost': 20},
}

# Données des armes : uniquement l'épée
WEAPON_DATA = {
    'sword': {'price': 0, 'damage': 25, 'unlocked': True},  # Gratuit et disponible dès le début
}

# --- SYSTÈME DE NIVEAUX ---
# Liste des fichiers de cartes pour chaque niveau
LEVEL_MAPS = {
    1: 'map/level1.txt',
    2: 'map/level2.txt',
    3: 'map/level3.txt',
    4: 'map/level4.txt',
    5: 'map/boss_level.txt',
    6: 'map/level6.txt'
}

# --- DONNÉES MONSTRES ---
MONSTER_DATA = {
    'squid': {'health': 100, 'exp': 100, 'damage': 10, 'speed': 3, 'resistance': 3, 'notice_radius': 400},
    'raccoon': {'health': 250, 'exp': 250, 'damage': 30, 'speed': 4, 'resistance': 5, 'notice_radius': 500},
    'boss': {'health': 2000, 'exp': 5000, 'damage': 50, 'speed': 2, 'resistance': 20, 'notice_radius': 1000}
}