import json
import os

class SaveManager:
    def __init__(self):
        self.save_filename = "save_data.json"
        # Statistiques de base par défaut pour une nouvelle partie
        self.default_data = {
            "player_name": "Link",
            "current_level": 1,
            "rubies": 0,
            "exp": 0,
            "talent_points": 0,
            "sword_level": 1,
            "stats": {
                "health": 100,
                "energy": 60,
                "attack": 10,
                "speed": 5,
                "magic": 50
            },
            "unlocked_spells": ["fireball"]
        }

    def save(self, data):
        """Sauvegarde les données au format JSON."""
        try:
            with open(self.save_filename, 'w') as f:
                json.dump(data, f, indent=4)
            print("Partie sauvegardée automatiquement.")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde : {e}")

    def load(self):
        """Charge les données. Si le fichier n'existe pas, retourne les données par défaut."""
        if not os.path.exists(self.save_filename):
            print("Aucune sauvegarde trouvée. Chargement des données par défaut.")
            return self.default_data
        
        try:
            with open(self.save_filename, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erreur lors du chargement : {e}")
            return self.default_data

    def delete_save(self):
        """Supprime la sauvegarde pour recommencer à zéro."""
        if os.path.exists(self.save_filename):
            os.remove(self.save_filename)