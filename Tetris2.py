import fltk
import random
import json
import time
# Constantes
LARGEUR_GRILLE = 10
HAUTEUR_GRILLE = 20
TAILLE_CASE = 20
GRAVITE = 0.15
LONGUEUR_INFO = 5
HAUTEUR_INFO = 10
LARGEUR_ZONE = (LARGEUR_GRILLE * TAILLE_CASE) + (LONGUEUR_INFO * TAILLE_CASE)  # Fenêtre plus large pour l'info
HAUTEUR_ZONE = HAUTEUR_GRILLE * TAILLE_CASE  # Hauteur reste la même pour la grille

# Formes et couleurs
FORMES = [
    [[1, 1, 1, 1]],  # Ligne (I)
    [[1, 1], [1, 1]],  # Carré (O)
    [[0, 1, 0], [1, 1, 1]],  # T
    [[1, 1, 0], [0, 1, 1]],  # Z
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]],  # J
]
COULEURS = ["red", "blue", "yellow","cyan","green","orange"]

# Variables globales
forme_actuelle = None
grille = [[0 for _ in range(LARGEUR_GRILLE)] for _ in range(HAUTEUR_GRILLE)]
score = 0
niveau = 1
vitesse = GRAVITE
forme_suiv = None
pause = False
tps_pourr = 0
dernier_temps_pourri = time.time()  # Initialisation du chrono avant la boucle
scoreParniv = False
game_over = False


def menu():
    """Affiche le menu principal permettant de démarrer une nouvelle partie ou de charger une partie sauvegardée."""
    choix = 0
    options = ["Nouveau Jeu", "Charger Partie","Pourrissement","Points Différent par niveau"]
    while True:
        fltk.efface_tout()
        fltk.rectangle(0, 0, (LARGEUR_GRILLE + LONGUEUR_INFO) * TAILLE_CASE, HAUTEUR_GRILLE * TAILLE_CASE, remplissage="black")
        fltk.texte(
            (LARGEUR_GRILLE + LONGUEUR_INFO) * TAILLE_CASE // 2,
            TAILLE_CASE * 3,
            "Tetris",
            couleur="white",
            taille=24,
            ancrage="center"
        )

        # Afficher les options
        for i, option in enumerate(options):
            couleur = "yellow" if i == choix else "white"
            fltk.texte(
                (LARGEUR_GRILLE + LONGUEUR_INFO) * TAILLE_CASE // 2,
                TAILLE_CASE * (5 + i * 2),
                option,
                couleur=couleur,
                taille=18,
                ancrage="center"
            )

        fltk.mise_a_jour()

        ev = fltk.donne_ev()
        if ev and fltk.type_ev(ev) == "Touche":
            touche = fltk.touche(ev)
            if touche == "Down":
                choix = (choix + 1) % len(options)
            elif touche == "Up":
                choix = (choix - 1) % len(options)
            elif touche == "Return":
                return choix  

def sauvegarde(nom_fichier="sauvegarde.json"):
    global grille, score, niveau, vitesse, forme_actuelle, forme_suiv,tps_pourr, dernier_temps_pourri
    etat_jeu = {
        "grille": grille,
        "score": score,
        "niveau": niveau,
        "vitesse": vitesse,
        "forme_actuelle": forme_actuelle,
        "forme_suiv": forme_suiv,
        "tps_pourr": tps_pourr,
        "dernier_temps_pourri": dernier_temps_pourri
    }

    with open(nom_fichier, "w") as fichier:
        json.dump(etat_jeu, fichier, indent=4)
    print(f"Partie sauvegardée dans {nom_fichier}")

def charger_sauv(nom_fichier="sauvegarde.json"):
    """Charge un état de jeu depuis un fichier JSON."""
    global grille, score, niveau, vitesse, forme_actuelle, forme_suiv,tps_pourr,dernier_temps_pourri

    try:
        with open(nom_fichier, "r") as fichier:
            etat_jeu = json.load(fichier)

        grille = etat_jeu["grille"]
        score = etat_jeu["score"]
        niveau = etat_jeu["niveau"]
        vitesse = etat_jeu["vitesse"]
        forme_actuelle = etat_jeu["forme_actuelle"]
        forme_suiv = etat_jeu["forme_suiv"]
        tps_pourr = etat_jeu["tps_pourr"]
        dernier_temps_pourri = etat_jeu["dernier_temps_pourri"]

        print(f"Partie chargée depuis {nom_fichier}") 
    except FileNotFoundError: #Au cas où le fichier est introuvable
        print(f"Fichier {nom_fichier} introuvable.")
    except json.JSONDecodeError: #Au cas où on arrive pas à lire le fichier de sauvegarde
        print(f"Erreur de lecture du fichier {nom_fichier}.")

def nouvelle_forme():
    """Crée une nouvelle forme avec une position initiale."""
    forme = random.choice(FORMES)
    couleur = random.choice(COULEURS)
    position = (0, LARGEUR_GRILLE // 2 - len(forme[0]) // 2)  # Position initiale au sommet
    return {"forme": forme, "couleur": couleur, "position": position}

def prochain_forme():
    global forme_suiv
    if forme_suiv is None:
        return  # Sort si `forme_suiv` n'est pas initialisée correctement

    offset_x = (LONGUEUR_INFO - len(forme_suiv["forme"][0])) * TAILLE_CASE // 2
    offset_y = (6 - len(forme_suiv["forme"])) * TAILLE_CASE // 2

    for i, ligne in enumerate(forme_suiv["forme"]):
        for j, case in enumerate(ligne):
            if case:
                fltk.rectangle(offset_x + j * TAILLE_CASE, 
                               HAUTEUR_GRILLE * TAILLE_CASE - 6 * TAILLE_CASE + offset_y + i * TAILLE_CASE,
                               offset_x + (j + 1) * TAILLE_CASE, 
                               HAUTEUR_GRILLE * TAILLE_CASE - 6 * TAILLE_CASE + offset_y + (i + 1) * TAILLE_CASE,
                               remplissage=forme_suiv["couleur"])

                
def dessiner_forme(forme, couleur, position):
    """Dessine une forme à l'écran."""
    ligne, colonne = position
    for i, ligne_forme in enumerate(forme):
        for j, case in enumerate(ligne_forme):
            if case == 1:  # Case remplie
                x1 = (colonne + j) * TAILLE_CASE + LONGUEUR_INFO * TAILLE_CASE  # Décalage à droite pour la grille
                y1 = (ligne + i) * TAILLE_CASE
                x2 = x1 + TAILLE_CASE
                y2 = y1 + TAILLE_CASE
                fltk.rectangle(x1, y1, x2, y2, remplissage=couleur)

def gerer_clavier():
    """Gère les actions du clavier pour déplacer la forme."""
    global forme_actuelle
    ev = fltk.donne_ev()
    if ev and fltk.type_ev(ev) == "Touche":
        touche = fltk.touche(ev)
        ligne, colonne = forme_actuelle["position"]

        if touche == "Left":
            nouvelle_position = (ligne, colonne - 1)
            if not collisions(forme_actuelle["forme"], nouvelle_position):
                forme_actuelle["position"] = nouvelle_position
        elif touche == "Right":
            nouvelle_position = (ligne, colonne + 1)
            if not collisions(forme_actuelle["forme"], nouvelle_position):
                forme_actuelle["position"] = nouvelle_position
        elif touche == "Down":
            nouvelle_position = (ligne + 1, colonne)
            if not collisions(forme_actuelle["forme"], nouvelle_position):
                forme_actuelle["position"] = nouvelle_position
        elif touche == "Up":
            nouvelle_forme = rotation_horaire(forme_actuelle["forme"])
            if not collisions(nouvelle_forme, (ligne, colonne)):
                forme_actuelle["forme"] = nouvelle_forme
        elif touche == "q":
            return False
        elif touche == "Escape":
            pause_menu()
    return True


def rotation_horaire(forme):
    """Fait tourner une forme de 45° dans le sens horaire."""
    hauteur = len(forme)      
    largeur = len(forme[0])    

    nouvelle_forme = [[0] * hauteur for _ in range(largeur)]

    for j in range(largeur):  
        for i in range(hauteur):
            nouvelle_forme[j][i] = forme[hauteur - 1 - i][j]

    return nouvelle_forme


def collisions(forme, position):
    """Vérifie si une collision se produit pour une forme à une position donnée."""
    ligne, colonne = position
    for i, ligne_forme in enumerate(forme):
        for j, case in enumerate(ligne_forme):
            if case == 1:
                if ligne + i >= HAUTEUR_GRILLE:
                    return True
                if colonne + j < 0 or colonne + j >= LARGEUR_GRILLE:
                    return True
                if grille[ligne + i][colonne + j] == 1:
                    return True
    return False


def ligne_complete():
    global score, niveau, vitesse, grille, scoreParniv
    nouvelle_grille = []
    for ligne in grille:
        if any(carre is None for carre in ligne):
            nouvelle_grille.append(ligne)

    ligne_efface= HAUTEUR_GRILLE - len(nouvelle_grille)
    for _ in range(ligne_efface):
        nouvelle_grille.insert(0, [None]* LARGEUR_GRILLE)
    grille[:]= nouvelle_grille
    
    if not scoreParniv:
        if ligne_efface == 1:
            score += 100
        elif ligne_efface == 2:
            score += 250
        elif ligne_efface == 3:
            score += 400
        elif ligne_efface == 4:
            score += 500
        niveau = 1 + score // 500

    if scoreParniv:
        if ligne_efface == 1:
            score += 25 *1* niveau
        elif ligne_efface == 2:
            score += 50* 1 * niveau
        elif ligne_efface == 3:
            score += 75 * 1 * niveau
        elif ligne_efface == 4:
            score += 100 * 1 * niveau
        niveau = 1 + score // (500 * 1 * niveau)

    vitesse= GRAVITE * (0.9 ** (niveau - 1))

    

def afficher_info():
    """Affiche les informations à gauche de l'écran."""
    fltk.rectangle(0, 0, LONGUEUR_INFO * TAILLE_CASE, HAUTEUR_ZONE, remplissage="black")
    fltk.texte(LONGUEUR_INFO * TAILLE_CASE // 2, 10, f"Score : {score}", couleur="white", taille=14, ancrage="center")
    fltk.texte(LONGUEUR_INFO * TAILLE_CASE // 2, 30, f"Niveau : {niveau}", couleur="white", taille=14, ancrage="center")
    fltk.ligne(LONGUEUR_INFO * TAILLE_CASE, 0, LONGUEUR_INFO * TAILLE_CASE, HAUTEUR_ZONE, couleur="white", epaisseur=4)

def pause_menu():
    """Affiche le menu de pause avec les options de sauvegarde et de quitter."""
    global pause
    pause = True
    while pause:
        fltk.rectangle(0, 0, LARGEUR_ZONE, HAUTEUR_ZONE, remplissage="black")

        fltk.texte(LARGEUR_ZONE // 2, HAUTEUR_ZONE // 3, "Pause", couleur="white", taille=16, ancrage="center")
        fltk.texte(LARGEUR_ZONE // 2, HAUTEUR_ZONE // 2.5, "Appuyez sur Échap pour continuer", couleur="white", taille=12, ancrage="center")
        fltk.texte(LARGEUR_ZONE // 2, HAUTEUR_ZONE // 2, "Appuyez sur S pour sauvegarder", couleur="white", taille=12, ancrage="center")
        fltk.texte(LARGEUR_ZONE // 2, HAUTEUR_ZONE // 1.8, "Appuyez sur L pour charger", couleur="white", taille=12, ancrage="center")
        fltk.texte(LARGEUR_ZONE // 2, HAUTEUR_ZONE // 1.6, "Appuyez sur Q pour quitter", couleur="white", taille=12, ancrage="center")

        fltk.mise_a_jour()

        ev = fltk.donne_ev()
        if ev and fltk.type_ev(ev) == "Touche":
            touche = fltk.touche(ev)
            if touche == "Escape":
                pause = False
            elif touche == "q":
                fltk.ferme_fenetre()
            elif touche == "s":
                sauvegarde()
            elif touche == "l":
                charger_sauv()


                
def mettre_a_jour_forme():
    """Fait descendre la forme actuelle automatiquement."""
    global forme_actuelle, grille, forme_suiv, game_over

    if forme_actuelle is not None:
        ligne, colonne = forme_actuelle["position"]
        nouvelle_position = (ligne + 1, colonne)

        if collisions(forme_actuelle["forme"], nouvelle_position):
            for i, ligne_forme in enumerate(forme_actuelle["forme"]):
                for j, case in enumerate(ligne_forme):
                    if case == 1:
                        if ligne + i < HAUTEUR_GRILLE:
                            grille[ligne + i][colonne + j] = 1

            if ligne == 0:
                game_over = True
                return

            forme_actuelle = forme_suiv
            forme_suiv = nouvelle_forme()
        else:
            # Sinon, descendre la forme
            forme_actuelle["position"] = nouvelle_position

    ligne_complete()  


def perdu():
    global game_over
    if game_over:
        fltk.rectangle(0, 0, LARGEUR_ZONE, HAUTEUR_ZONE, remplissage="black")
        fltk.texte(LARGEUR_ZONE // 2, HAUTEUR_ZONE // 3, "Game Over", couleur="red", taille=16, ancrage="center")
        fltk.attente(1)
        fltk.ferme_fenetre

def verifie_fin_de_jeu():
    """
    Vérifie si le jeu est terminé en tentant de placer une nouvelle forme.
    Retourne True si une collision est détectée au sommet de la grille.
    """
    global forme_actuelle
    ligne, colonne = forme_actuelle["position"]
    for i, ligne_forme in enumerate(forme_actuelle["forme"]):
        for j, case in enumerate(ligne_forme):
            if case == 1 and grille[ligne + i][colonne + j] == 1:
                return True
    return False


def boucle_principale():
    """Boucle principale du jeu."""
    global forme_actuelle, forme_suiv, tps_pourr,dernier_temps_pourri, grille, game_over
    forme_suiv = nouvelle_forme()  
    

    while True:
        fltk.efface_tout()

        fltk.rectangle(0, 0, LARGEUR_ZONE, HAUTEUR_ZONE, remplissage="black")

        if not gerer_clavier():
            break

        if forme_actuelle is None:
            forme_actuelle = forme_suiv
            forme_suiv = nouvelle_forme()
        if forme_suiv is None:
            forme_suiv = nouvelle_forme()
        if forme_actuelle is not None:
            dessiner_forme(
                forme_actuelle["forme"],
                forme_actuelle["couleur"],
                forme_actuelle["position"],
            )

        mettre_a_jour_forme()

        if verifie_fin_de_jeu():
            game_over = True
            perdu()
            break  # Sortir de la boucle principale



        if tps_pourr > 0 and time.time() - dernier_temps_pourri >= tps_pourr:
            positions_occupees = [
                (i, j) for i in range(HAUTEUR_GRILLE) for j in range(LARGEUR_GRILLE) if grille[i][j] == 1
            ]
            if positions_occupees:
                ligne, colonne = random.choice(positions_occupees)
                grille[ligne][colonne] = 0
            dernier_temps_pourri = time.time()  # Réinitialisation du chrono après l'action

        for i in range(HAUTEUR_GRILLE):
            for j in range(LARGEUR_GRILLE):
                if grille[i][j] == 1:
                    x1 = j * TAILLE_CASE + LONGUEUR_INFO * TAILLE_CASE  
                    y1 = i * TAILLE_CASE
                    x2 = x1 + TAILLE_CASE
                    y2 = y1 + TAILLE_CASE
                    fltk.rectangle(x1, y1, x2, y2, remplissage="gray")

        for i in range(HAUTEUR_GRILLE + 1):  
            fltk.ligne(LONGUEUR_INFO * TAILLE_CASE, i * TAILLE_CASE,
                       LARGEUR_GRILLE * TAILLE_CASE + LONGUEUR_INFO * TAILLE_CASE, i * TAILLE_CASE, couleur="white")
        for j in range(LARGEUR_GRILLE + 1):  
            fltk.ligne(j * TAILLE_CASE + LONGUEUR_INFO * TAILLE_CASE, 0,
                       j * TAILLE_CASE + LONGUEUR_INFO * TAILLE_CASE, HAUTEUR_GRILLE * TAILLE_CASE, couleur="white")

        afficher_info()
        prochain_forme()

        # Rafraîchir l'affichage
        fltk.mise_a_jour()
        fltk.attente(vitesse)  # Pause entre chaque descente


if __name__ == "__main__":
    fltk.cree_fenetre(LARGEUR_ZONE, HAUTEUR_ZONE)
    choix = menu()
    if choix == 0:  
        print("Démarrage d'une nouvelle partie.")
    elif choix == 1:  
        print("Chargement d'une partie existante.")
        charger_sauv()
    elif choix == 2:
        print ('Mode pourrisement activé\n')
        tps_pourr = int(input('Choisissez le temps de pourrissement entre chaque bloc:  '))
        print(f'Temps entre chaque effacement {tps_pourr}')
    elif choix == 3:
        print ('Mode Score par niveau activé\n')
        scoreParniv = True
        

    boucle_principale()
    fltk.ferme_fenetre()
