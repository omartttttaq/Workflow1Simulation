import pygame
from os import walk

def import_csv_layout(path):
    """
    Lit un fichier texte (.txt ou .csv) représentant la carte
    et le transforme en une liste utilisable.
    """
    terrain_map = []
    try:
        with open(path) as level_map:
            for row in level_map:
                # On nettoie la ligne et on sépare par virgule ou caractère
                # Si vous utilisez des espaces, remplacez ',' par None
                layout = list(row.strip().replace(',', ''))
                terrain_map.append(layout)
        return terrain_map
    except FileNotFoundError:
        print(f"Erreur : Le fichier {path} est introuvable.")
        return []

def import_folder(path):
    """
    Parcourt un dossier et charge toutes les images qu'il contient.
    Utile pour les animations du joueur et des ennemis.
    """
    surface_list = []
    for _, __, img_files in walk(path):
        for image in sorted(img_files):
            full_path = path + '/' + image
            image_surf = pygame.image.load(full_path).convert_alpha()
            surface_list.append(image_surf)
    return surface_list

def import_folder_dict(path):
    """
    Charge les images d'un dossier sous forme de dictionnaire.
    Clé = nom du fichier sans extension.
    """
    surface_dict = {}
    for _, __, img_files in walk(path):
        for image in img_files:
            full_path = path + '/' + image
            image_surf = pygame.image.load(full_path).convert_alpha()
            surface_dict[image.split('.')[0]] = image_surf
    return surface_dict