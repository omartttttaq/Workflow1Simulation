import random

mots=["python", "ordinateur", "programmation", "pendu", "algorithme", "intelligence", "crocodile", "catana", "international", "adam", "nabil", "azerty", "zèbre", "nébuleuse"]
mot_secret = random.choice(mots).upper()
lettres_trouvées = set()
lettres_fausses = set()
essais_restants = 8

print("Bienvenue au jeu du pendu !")

while essais_restants > 0:
    # Affichage du mot avec_pour les lettres non trouvées
    affichage = [lettre if lettre in lettres_trouvées else "_" for lettre in mot_secret]
    print("\nMot:", "".join(affichage))
    print(f"Lettres fausses : {', '.join(sorted(lettres_fausses))}")
    print(f"Essais restants : {essais_restants}")

# Vérification si gagné
    if "_" not in affichage:   
        print("Bravo, tu as trouvé le mot :", mot_secret)
        break

# Demande une lettre
    lettre = input("Propose une lettre : ").upper()
    
    if len(lettre) != 1 or not lettre.isalpha():
        print("ENTRE UNE SEULE LETTRE VALIDE !!!")
        continue

    if lettre in lettres_trouvées or lettre in lettres_fausses:
        print("Tu as déjà proposé cette lettre !")
        continue

    if lettre in mot_secret:
        print("Bien vu !!!!!")
        lettres_trouvées.add(lettre)
    else:
        print("Mauvais choix.")
        lettres_fausses.add(lettre)
        essais_restants -= 1

print("\n Partie terminée ! Le mot était :", mot_secret)