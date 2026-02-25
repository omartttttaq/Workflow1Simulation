import tkinter as tk
import random

fenetre = tk.Tk()
fenetre.title("🎯 Juste Prix")
fenetre.geometry("300x200")

couleurs_fond = ["lightblue", "lightgreen", "lightyellow", "lightpink", "lavender", "mistyrose"]
index_couleur = 0

nombre_secret = random.randint(1, 10)
essais = 0

def verifier():
    global essais
    try:
        choix = int(entree.get())
        essais += 1
        if choix < nombre_secret:
            resultat.config(text="🔼 C'est plus grand !")
        elif choix > nombre_secret:
            resultat.config(text="🔽 C'est plus petit !")
        else:
            resultat.config(text=f"🎉 Bravo ! Trouvé en {essais} essais.")
            bouton.config(state="disabled")
    except ValueError:
        resultat.config(text="⛔ Entrez un nombre valide.")

def rejouer():
    global nombre_secret, essais
    nombre_secret = random.randint(1, 10)
    essais = 0
    resultat.config(text="")
    entree.delete(0, tk.END)
    bouton.config(state="normal")

def changer_fond():
    global index_couleur
    index_couleur = (index_couleur + 1) % len(couleurs_fond)
    fenetre.config(bg=couleurs_fond[index_couleur])
    for widget in [label, entree, bouton, resultat, bouton_rejouer, bouton_fond]:
        widget.config(bg=couleurs_fond[index_couleur])

label = tk.Label(fenetre, text="Devine un nombre entre 1 et 10")
label.pack(pady=10)

entree = tk.Entry(fenetre)
entree.pack()

bouton = tk.Button(fenetre, text="Valider", command=verifier)
bouton.pack(pady=5)

resultat = tk.Label(fenetre, text="")
resultat.pack(pady=10)

bouton_rejouer = tk.Button(fenetre, text="Rejouer", command=rejouer)
bouton_rejouer.pack(pady=5)

bouton_fond = tk.Button(fenetre, text="🎨 Changer le fond", command=changer_fond)
bouton_fond.pack(pady=5)

fenetre.mainloop()