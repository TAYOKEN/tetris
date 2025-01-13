import fltk
import random
import json
import time
import os
# Constantes
LARGEUR_GRILLE = 10
HAUTEUR_GRILLE = 20
TAILLE_CASE = 28
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

# Variables Jeu de base
forme_actuelle = None
grille = [[None for _ in range(LARGEUR_GRILLE)] for _ in range(HAUTEUR_GRILLE)]
score = 0
niveau = 1
vitesse = GRAVITE
forme_suiv = None
pause = False
game_over = False
jeu_en_cours = True

#Variables Variantes/Bonus
tps_pourr = 0
dernier_temps_pourri = time.time()  # Initialisation du chrono avant la boucle
scoreParniv = False
bloc_bonus_activ = False
info_bloc_gris = {
    "position": None,
    "couleur_originale": None,
    "temps_devenu_gris": None
}
bonus_active = False
POLYOMINOS_PERSONNALISES = []
elim_couleurs_adjacentes = False

# Variables globales pour le joueur 2
j2_forme_actuelle = None
j2_grille = [[None for _ in range(LARGEUR_GRILLE)] for _ in range(HAUTEUR_GRILLE)]
j2_score = 0
j2_niveau = 1
j2_vitesse = GRAVITE
j2_forme_suiv = None
j2_pause = False
j2_game_over = False


def menu():
    """Affiche le menu principal avec des décorations et animations."""
    choix = 0
    options = ["Nouveau Jeu", "Charger Partie", "Variantes", "Bonus", "Mode 2 Joueurs", "Quitter"]
    bordure_couleur = "white"
    animation_timer = 0
    
    while True:
        fltk.efface_tout()
        
        # Décoration : Fond animé
        for i in range(HAUTEUR_GRILLE):
            couleur_ligne = f"#{(10 * i) % 255:02x}{(5 * i) % 255:02x}33"  # Gradation de couleur
            fltk.rectangle(0, i * TAILLE_CASE, LARGEUR_ZONE, (i + 1) * TAILLE_CASE, remplissage=couleur_ligne)
        
        # Décoration : Bordures dynamiques
        if animation_timer % 20 < 10:
            bordure_couleur = "yellow"
        else:
            bordure_couleur = "orange"
        
        fltk.rectangle(
            0, 0, (LARGEUR_GRILLE + LONGUEUR_INFO) * TAILLE_CASE, HAUTEUR_GRILLE * TAILLE_CASE,
            remplissage="", couleur=bordure_couleur, epaisseur=6
        )
        
        # Titre animé
        taille_titre = 24 + (animation_timer % 20) // 5  # Variation de la taille du texte
        couleur_titre = "cyan" if animation_timer % 40 < 20 else "magenta"
        
        fltk.texte(
            (LARGEUR_GRILLE + LONGUEUR_INFO) * TAILLE_CASE // 2,
            TAILLE_CASE * 3,
            "TETRIS",
            couleur=couleur_titre,
            taille=taille_titre,
            ancrage="center"
        )

        # Afficher les options
        for i, option in enumerate(options):
            couleur_option = "yellow" if i == choix else couleur_titre
            fltk.texte(
                (LARGEUR_GRILLE + LONGUEUR_INFO) * TAILLE_CASE // 2,
                TAILLE_CASE * (5 + i * 2),
                option,
                couleur=couleur_option,
                taille=18,
                ancrage="center"
            )

        fltk.mise_a_jour()

        # Gestion des événements
        ev = fltk.donne_ev()
        if ev and fltk.type_ev(ev) == "Touche":
            touche = fltk.touche(ev)
            if touche == "Down":
                choix = (choix + 1) % len(options)
            elif touche == "Up":
                choix = (choix - 1) % len(options)
            elif touche == "Return":
                return choix

        animation_timer += 1
        fltk.attente(0.05) 

            
def menu_variantes():
    """Affiche le menu principal permettant de démarrer une nouvelle partie ou de charger une partie sauvegardée."""
    choix = 0
    options = ["Pourrissement", "Points par Niveau", "Charger Polyominos", "Retour"]
    bordure_couleur = "white"
    animation_timer = 0
    
    while True:
        fltk.efface_tout()
        
        # Décoration : Fond animé
        for i in range(HAUTEUR_GRILLE):
            couleur_ligne = f"#{(10 * i) % 255:02x}{(5 * i) % 255:02x}33"  # Gradation de couleur
            fltk.rectangle(0, i * TAILLE_CASE, LARGEUR_ZONE, (i + 1) * TAILLE_CASE, remplissage=couleur_ligne)
        
        # Décoration : Bordures dynamiques
        if animation_timer % 20 < 10:
            bordure_couleur = "yellow"
        else:
            bordure_couleur = "orange"
        
        fltk.rectangle(
            0, 0, (LARGEUR_GRILLE + LONGUEUR_INFO) * TAILLE_CASE, HAUTEUR_GRILLE * TAILLE_CASE,
            remplissage="", couleur=bordure_couleur, epaisseur=6
        )
        
        # Titre animé
        taille_titre = 24 + (animation_timer % 20) // 5  # Variation de la taille du texte
        couleur_titre = "cyan" if animation_timer % 40 < 20 else "magenta"
        
        fltk.texte(
            (LARGEUR_GRILLE + LONGUEUR_INFO) * TAILLE_CASE // 2,
            TAILLE_CASE * 3,
            "TETRIS",
            couleur=couleur_titre,
            taille=taille_titre,
            ancrage="center"
        )

        for i, option in enumerate(options):
            couleur_option = "yellow" if i == choix else couleur_titre
            fltk.texte(
                (LARGEUR_GRILLE + LONGUEUR_INFO) * TAILLE_CASE // 2,
                TAILLE_CASE * (5 + i * 2),
                option,
                couleur=couleur_option,
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

        animation_timer += 1
        fltk.attente(0.1) 

def menu_bonus():
    """Affiche le menu principal permettant de démarrer une nouvelle partie ou de charger une partie sauvegardée."""
    choix = 0
    options = ["Sauvegarde des paramètres", "Charger des paramètres", "Bloc Bonus", "Couleur Adjacentes", "Retour"]
    bordure_couleur = "white"
    animation_timer = 0
    
    while True:
        fltk.efface_tout()
        
        for i in range(HAUTEUR_GRILLE):
            couleur_ligne = f"#{(10 * i) % 255:02x}{(5 * i) % 255:02x}33"  # Gradation de couleur
            fltk.rectangle(0, i * TAILLE_CASE, LARGEUR_ZONE, (i + 1) * TAILLE_CASE, remplissage=couleur_ligne)
        
        if animation_timer % 20 < 10:
            bordure_couleur = "yellow"
        else:
            bordure_couleur = "orange"
        
        fltk.rectangle(
            0, 0, (LARGEUR_GRILLE + LONGUEUR_INFO) * TAILLE_CASE, HAUTEUR_GRILLE * TAILLE_CASE,
            remplissage="", couleur=bordure_couleur, epaisseur=6
        )
        
        # Titre animé
        taille_titre = 24 + (animation_timer % 20) // 5  # Variation de la taille du texte
        couleur_titre = "cyan" if animation_timer % 40 < 20 else "magenta"
        
        fltk.texte(
            (LARGEUR_GRILLE + LONGUEUR_INFO) * TAILLE_CASE // 2,
            TAILLE_CASE * 3,
            "TETRIS",
            couleur=couleur_titre,
            taille=taille_titre,
            ancrage="center"
        )

        for i, option in enumerate(options):
            couleur_option = "yellow" if i == choix else couleur_titre
            fltk.texte(
                (LARGEUR_GRILLE + LONGUEUR_INFO) * TAILLE_CASE // 2,
                TAILLE_CASE * (5 + i * 2),
                option,
                couleur=couleur_option,
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

        animation_timer += 1
        fltk.attente(0.1) 

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
        json.dump(etat_jeu, fichier)
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

def config(nom_fichier="config.json"):
    global LARGEUR_GRILLE, HAUTEUR_GRILLE,TAILLE_CASE,GRAVITE,LONGUEUR_INFO,FORMES,COULEURS

    config_jeu = {
        "longeur de la grille": LARGEUR_GRILLE,
        "Hauteur de la fenetre et de la grille": HAUTEUR_GRILLE,
        "Taille de la fenetre": TAILLE_CASE,
        "vitesse de base": GRAVITE,
        "longueur de la zone info": LONGUEUR_INFO,
        "couleurs": COULEURS,
    }

    with open(nom_fichier, "w") as fichier:
        json.dump(config_jeu, fichier, indent= 4)
    print(f"Configuration sauvegardée dans {nom_fichier}")

def charger_config(nom_fichier="config.json"):
    """Charge un état de configuration depuis un fichier JSON et met à jour la fenêtre."""
    global LARGEUR_GRILLE, HAUTEUR_GRILLE, TAILLE_CASE, GRAVITE, LONGUEUR_INFO, COULEURS
    global LARGEUR_ZONE, HAUTEUR_ZONE  # Recalculer les dimensions

    try:
        with open(nom_fichier, "r") as fichier:
            config_jeu = json.load(fichier)

        LARGEUR_GRILLE = config_jeu["longeur de la grille"]
        HAUTEUR_GRILLE = config_jeu["Hauteur de la fenetre et de la grille"]
        TAILLE_CASE = config_jeu["Taille de la fenetre"]
        GRAVITE = config_jeu["vitesse de base"]
        LONGUEUR_INFO = config_jeu["longueur de la zone info"]
        COULEURS = config_jeu["couleurs"]

        LARGEUR_ZONE = (LARGEUR_GRILLE * TAILLE_CASE) + (LONGUEUR_INFO * TAILLE_CASE)
        HAUTEUR_ZONE = HAUTEUR_GRILLE * TAILLE_CASE

        print(f"Configuration chargée depuis {nom_fichier}")
        print("Redémarrage de la fenêtre pour appliquer les changements...")

        fltk.ferme_fenetre()
        fltk.cree_fenetre(LARGEUR_ZONE, HAUTEUR_ZONE)

    except FileNotFoundError:
        print(f"Fichier {nom_fichier} introuvable.")
    except json.JSONDecodeError:
        print(f"Erreur de lecture du fichier {nom_fichier}.")


def nouvelle_forme():
    """Crée une nouvelle forme aléatoire avec une position initiale"""
    global POLYOMINOS_PERSONNALISES
    if POLYOMINOS_PERSONNALISES:
        forme = random.choice(POLYOMINOS_PERSONNALISES)
    else:
        forme = random.choice(FORMES)
    couleur = random.choice(COULEURS)
    position = (0, LARGEUR_GRILLE // 2 - len(forme[0]) // 2)
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
    """Dessine une forme à l'écran à sa position donnée."""
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
    global forme_actuelle, jeu_en_cours
    ev = fltk.donne_ev()
    if ev and fltk.type_ev(ev) == "Touche":
        touche = fltk.touche(ev)
        ligne, colonne = forme_actuelle["position"]

        if touche == "Left":
            nouvelle_position = (ligne, colonne - 1)
            if not collisions(forme_actuelle["forme"], nouvelle_position,grille):
                forme_actuelle["position"] = nouvelle_position
        elif touche == "Right":
            nouvelle_position = (ligne, colonne + 1)
            if not collisions(forme_actuelle["forme"], nouvelle_position,grille):
                forme_actuelle["position"] = nouvelle_position
        elif touche == "Down":
            nouvelle_position = (ligne + 1, colonne)
            if not collisions(forme_actuelle["forme"], nouvelle_position,grille):
                forme_actuelle["position"] = nouvelle_position
        elif touche == "Up":
            nouvelle_forme = rotation_horaire(forme_actuelle["forme"])
            if not collisions(nouvelle_forme, (ligne, colonne),grille):
                forme_actuelle["forme"] = nouvelle_forme
        elif touche == "q":
            jeu_en_cours = False 
        elif touche == "Escape":
            pause_menu()
    return True


def rotation_horaire(forme):
    """Fait tourner une forme de 90° dans le sens horaire."""
    if not forme or not all(isinstance(ligne, list) and len(ligne) == len(forme[0]) for ligne in forme):
        print("Erreur : Forme invalide pour la rotation (lignes de longueurs différentes ou forme vide).")
        return forme  
    hauteur = len(forme)
    largeur = len(forme[0])
    nouvelle_forme = [[0] * hauteur for _ in range(largeur)]  
    for i in range(hauteur):
        for j in range(largeur):
            nouvelle_forme[j][hauteur - 1 - i] = forme[i][j]  
    return nouvelle_forme

def collisions(forme, position, grille):
    """Vérifie si une collision se produit pour une forme à une position donnée."""
    ligne, colonne = position
    for i, ligne_forme in enumerate(forme):
        for j, case in enumerate(ligne_forme):
            if case == 1:
                if ligne + i >= HAUTEUR_GRILLE or colonne + j < 0 or colonne + j >= LARGEUR_GRILLE:
                    return True
                if grille[ligne + i][colonne + j] is not None:
                    return True
    return False



def ligne_complete():
    global score, niveau, vitesse, grille, scoreParniv
    nouvelle_grille = []
    lignes_effacees = 0
    gris_efface = False

    for ligne in grille:
        if all(carre is not None for carre in ligne):  
            lignes_effacees += 1
            if 'gray' in ligne:  
                gris_efface = True
        else:
            nouvelle_grille.append(ligne)

    for _ in range(lignes_effacees):
        nouvelle_grille.insert(0, [None] * LARGEUR_GRILLE)

    grille = nouvelle_grille

    if lignes_effacees > 0:
        points_par_lignes = [0, 100, 250, 400, 500][min(lignes_effacees, 4)]
        score += points_par_lignes * niveau if not scoreParniv else points_par_lignes

    if gris_efface:
        bonus_effet()

    return lignes_effacees > 0


    

def afficher_info():
    """Affiche les informations à gauche de l'écran."""
    global tps_pourr
    fltk.rectangle(0, 0, LONGUEUR_INFO * TAILLE_CASE, HAUTEUR_ZONE, remplissage="black")
    fltk.texte(LONGUEUR_INFO * TAILLE_CASE // 2, 10, f"Score : {score}", couleur="white", taille=14, ancrage="center")
    fltk.texte(LONGUEUR_INFO * TAILLE_CASE // 2, 30, f"Niveau : {niveau}", couleur="white", taille=14, ancrage="center")        
    fltk.texte(LONGUEUR_INFO * TAILLE_CASE // 2, 50, f"Pourrisement : {tps_pourr}", couleur="white", taille=14, ancrage="center")
    fltk.ligne(LONGUEUR_INFO * TAILLE_CASE, 0, LONGUEUR_INFO * TAILLE_CASE, HAUTEUR_ZONE, couleur="white", epaisseur=4)

def pause_menu():
    """Affiche le menu de pause avec les options de sauvegarde et de quitter."""
    global pause, jeu_en_cours
    pause = True
    while pause:
        fltk.rectangle(0, 0, LARGEUR_ZONE, HAUTEUR_ZONE, remplissage="black")
        fltk.texte(LARGEUR_ZONE // 2, HAUTEUR_ZONE // 3, "Pause", couleur="white", taille=16, ancrage="center")
        fltk.texte(LARGEUR_ZONE // 2, HAUTEUR_ZONE // 2.5, "Appuyez sur Échap pour continuer", couleur="white", taille=12, ancrage="center")
        fltk.texte(LARGEUR_ZONE // 2, HAUTEUR_ZONE // 2, "Appuyez sur S pour sauvegarder", couleur="white", taille=12, ancrage="center")
        fltk.texte(LARGEUR_ZONE // 2, HAUTEUR_ZONE // 1.6, "Appuyez sur Q pour quitter", couleur="white", taille=12, ancrage="center")

        fltk.mise_a_jour()

        ev = fltk.donne_ev()
        if ev and fltk.type_ev(ev) == "Touche":
            touche = fltk.touche(ev)
            if touche == "Escape":
                pause = False
            elif touche == "q":
                jeu_en_cours = False
                pause = False
            elif touche == "s":
                sauvegarde()


                
def mettre_a_jour_forme():
    """Fait descendre la forme actuelle automatiquement pour le joueur 1."""
    global forme_actuelle, grille, forme_suiv, game_over

    if forme_actuelle is not None:
        ligne, colonne = forme_actuelle["position"]
        nouvelle_position = (ligne + 1, colonne)

        if collisions(forme_actuelle["forme"], nouvelle_position, grille):  
            for i, ligne_forme in enumerate(forme_actuelle["forme"]):
                for j, case in enumerate(ligne_forme):
                    if case == 1 and ligne + i < HAUTEUR_GRILLE:
                        grille[ligne + i][colonne + j] = forme_actuelle["couleur"]  
            if ligne == 0:
                game_over = True
                return

            forme_actuelle = forme_suiv
            forme_suiv = nouvelle_forme()
        else:
            forme_actuelle["position"] = nouvelle_position

    ligne_complete()

    ligne_complete() 

def pourrissement(): 
    positions_occupees = [
                (i, j) for i in range(HAUTEUR_GRILLE) for j in range(LARGEUR_GRILLE) if grille[i][j] != None
            ]
    if positions_occupees:
        ligne, colonne = random.choice(positions_occupees)
        grille[ligne][colonne] = None
        return grille

def bloc_bonus(): 
    global info_bloc_gris

    if info_bloc_gris["position"] is not None:
        temps_ecoule = time.time() - info_bloc_gris["temps_devenu_gris"]
        if temps_ecoule >= 30:
            ligne, colonne = info_bloc_gris["position"]
            grille[ligne][colonne] = info_bloc_gris["couleur_originale"]
            info_bloc_gris = {
                "position": None,
                "couleur_originale": None,
                "temps_devenu_gris": None
            }
        else:
            return grille

    positions_occupees = [
        (i, j) for i in range(HAUTEUR_GRILLE) for j in range(LARGEUR_GRILLE) if grille[i][j] is not None
    ]
    if positions_occupees:
        ligne, colonne = random.choice(positions_occupees)
        info_bloc_gris = {
            "position": (ligne, colonne),
            "couleur_originale": grille[ligne][colonne],
            "temps_devenu_gris": time.time()
        }
        grille[ligne][colonne] = 'gray'
    
    return grille

def bonus_effet():
    """Applique un effet aléatoire si un bloc gris est supprimé."""
    global grille, score, niveau, vitesse, game_over
    effet = random.randint(1, 3) 

    if effet == 1: 
        print("Multiplicateur de points activé !")

    elif effet == 2:  # Effacement du plateau
        print("Effacement du plateau activé !")
        grille = [[None for _ in range(LARGEUR_GRILLE)] for _ in range(HAUTEUR_GRILLE)]

    elif effet == 3: 
        print("Gravité réelle activée !")
        appliquer_gravite()

    fltk.mise_a_jour()


    fltk.mise_a_jour()

def appliquer_gravite():
    """Applique la gravité réelle aux blocs de la grille."""
    global grille, game_over

    for colonne in range(LARGEUR_GRILLE):
        pile = [grille[ligne][colonne] for ligne in range(HAUTEUR_GRILLE) if grille[ligne][colonne] is not None]
        
        for ligne in range(HAUTEUR_GRILLE):
            grille[ligne][colonne] = None
        
        for ligne in range(HAUTEUR_GRILLE - len(pile), HAUTEUR_GRILLE):
            grille[ligne][colonne] = pile.pop(0)

    for colonne in range(LARGEUR_GRILLE):
        if grille[0][colonne] is not None:
            print("Game over détecté après gravité.")
            game_over = True
            break
        
def perdu():
    global game_over,grille,niveau,vitesse,score
    if game_over:
        fltk.rectangle(0, 0, LARGEUR_ZONE, HAUTEUR_ZONE, remplissage="black")
        fltk.texte(LARGEUR_ZONE // 2, HAUTEUR_ZONE // 3, "Game Over", couleur="red", taille=16, ancrage="center")
        grille = [[None for _ in range(LARGEUR_GRILLE)] for _ in range(HAUTEUR_GRILLE)]

        fltk.attente(1)
        fltk.ferme_fenetre
        game_over = False
        niveau = 1
        vitesse = GRAVITE
        score = 0

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
    global forme_actuelle, forme_suiv, game_over,dernier_temps_pourri, jeu_en_cours

    forme_suiv = nouvelle_forme()

    while jeu_en_cours:
        fltk.efface_tout()
        
        if bloc_bonus_activ == True:
            bloc_bonus()
        
        if tps_pourr > 0 and time.time() - dernier_temps_pourri >= tps_pourr:
            pourrissement()
            dernier_temps_pourri = time.time()  # Réinitialisation du chrono après l'action
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

        for i in range(HAUTEUR_GRILLE):
            for j in range(LARGEUR_GRILLE):
                if grille[i][j] is not None:  # Si la cellule contient une couleur
                    x1 = j * TAILLE_CASE + LONGUEUR_INFO * TAILLE_CASE
                    y1 = i * TAILLE_CASE
                    x2 = x1 + TAILLE_CASE
                    y2 = y1 + TAILLE_CASE
                    fltk.rectangle(x1, y1, x2, y2, remplissage=grille[i][j])

        for i in range(HAUTEUR_GRILLE + 1):
            fltk.ligne(LONGUEUR_INFO * TAILLE_CASE, i * TAILLE_CASE,
                       LARGEUR_GRILLE * TAILLE_CASE + LONGUEUR_INFO * TAILLE_CASE, i * TAILLE_CASE, couleur="white")
        for j in range(LARGEUR_GRILLE + 1):
            fltk.ligne(j * TAILLE_CASE + LONGUEUR_INFO * TAILLE_CASE, 0,
                       j * TAILLE_CASE + LONGUEUR_INFO * TAILLE_CASE, HAUTEUR_GRILLE * TAILLE_CASE, couleur="white")

        afficher_info()

        prochain_forme()

        fltk.mise_a_jour()
        fltk.attente(vitesse)

        if game_over:
            perdu()
            break


def charger_polyominos(nom_fichier):
    """
    Charge les polyominos depuis un fichier texte.
    Chaque polyomino est séparé par une ou plusieurs lignes vides.
    """
    if not os.path.isfile(nom_fichier):
        print(f"Erreur : Le fichier {nom_fichier} n'existe pas.")
        return []

    with open(nom_fichier, "r") as fichier:
        contenu = fichier.read().strip()

    if not contenu:
        print("Erreur : Le fichier est vide ou mal formaté.")
        return []

    polyominos = []
    blocs = contenu.split("\n\n")  
    for bloc in blocs:
        try:
            forme = [[1 if char == "+" else 0 for char in ligne] for ligne in bloc.split("\n")]
            polyominos.append(forme)
        except IndexError:
            print(f"Erreur : Format incorrect dans le bloc suivant :\n{bloc}")
            continue


    if not polyominos:
        print("Erreur : Aucun polyomino valide n'a été trouvé.")
    return polyominos


def gerer_clavier_j2():
    """Gère les actions du clavier pour le joueur 2."""
    global j2_forme_actuelle, j2_game_over
    ev = fltk.donne_ev()
    if ev and fltk.type_ev(ev) == "Touche":
        touche = fltk.touche(ev)
        ligne, colonne = j2_forme_actuelle["position"]

        if touche == "q":  
            nouvelle_position = (ligne, colonne - 1)
            if not collisions(j2_forme_actuelle["forme"], nouvelle_position, j2_grille):
                j2_forme_actuelle["position"] = nouvelle_position
        elif touche == "d":  
            nouvelle_position = (ligne, colonne + 1)
            if not collisions(j2_forme_actuelle["forme"], nouvelle_position, j2_grille):
                j2_forme_actuelle["position"] = nouvelle_position
        elif touche == "s":  
            nouvelle_position = (ligne + 1, colonne)
            if not collisions(j2_forme_actuelle["forme"], nouvelle_position, j2_grille):
                j2_forme_actuelle["position"] = nouvelle_position
        elif touche == "z":  
            nouvelle_forme = rotation_horaire(j2_forme_actuelle["forme"])
            if not collisions(nouvelle_forme, (ligne, colonne), j2_grille):
                j2_forme_actuelle["forme"] = nouvelle_forme
        elif touche == "Escape":
            j2_pause = True
    return True

def mettre_a_jour_forme_j2():
    """Fait descendre la forme actuelle automatiquement pour le joueur 2."""
    global j2_forme_actuelle, j2_grille, j2_forme_suiv, j2_game_over

    if j2_forme_actuelle is not None:
        ligne, colonne = j2_forme_actuelle["position"]
        nouvelle_position = (ligne + 1, colonne)

        if collisions(j2_forme_actuelle["forme"], nouvelle_position, j2_grille):  
            for i, ligne_forme in enumerate(j2_forme_actuelle["forme"]):
                for j, case in enumerate(ligne_forme):
                    if case == 1 and ligne + i < HAUTEUR_GRILLE:
                        j2_grille[ligne + i][colonne + j] = j2_forme_actuelle["couleur"]  

            if ligne == 0:
                j2_game_over = True
                return

            j2_forme_actuelle = j2_forme_suiv
            j2_forme_suiv = nouvelle_forme()
        else:
            j2_forme_actuelle["position"] = nouvelle_position

    ligne_complete_j2()


def ligne_complete_j2():
    global j2_score, j2_niveau, j2_vitesse, j2_grille
    nouvelle_grille = []
    lignes_effacees = 0

    for ligne in j2_grille:
        if all(carre is not None for carre in ligne):  
            lignes_effacees += 1
        else:
            nouvelle_grille.append(ligne)

    for _ in range(lignes_effacees):
        nouvelle_grille.insert(0, [None] * LARGEUR_GRILLE)

    j2_grille = nouvelle_grille

    if lignes_effacees > 0:
        points_par_lignes = [0, 100, 250, 400, 500][min(lignes_effacees, 4)]
        j2_score += points_par_lignes * j2_niveau

def dessiner_forme_j2(forme, couleur, position):
    """Dessine une forme pour le joueur 2 à l'écran à sa position donnée."""
    ligne, colonne = position
    for i, ligne_forme in enumerate(forme):
        for j, case in enumerate(ligne_forme):
            if case == 1:  # Case remplie
                x1 = (colonne + j) * TAILLE_CASE + LARGEUR_GRILLE * TAILLE_CASE + LONGUEUR_INFO * TAILLE_CASE
                y1 = (ligne + i) * TAILLE_CASE
                x2 = x1 + TAILLE_CASE
                y2 = y1 + TAILLE_CASE
                fltk.rectangle(x1, y1, x2, y2, remplissage=couleur)

def dessiner_separation():
    """Dessine une séparation entre les grilles des deux joueurs."""
    fltk.ligne(
        LARGEUR_GRILLE * TAILLE_CASE + LONGUEUR_INFO * TAILLE_CASE, 0,
        LARGEUR_GRILLE * TAILLE_CASE + LONGUEUR_INFO * TAILLE_CASE, HAUTEUR_ZONE,
        couleur="white", epaisseur=4
    )

def boucle_principale_2_joueurs():
    """Boucle principale pour le mode 2 joueurs."""
    global forme_actuelle, forme_suiv, game_over, j2_forme_actuelle, j2_forme_suiv, j2_game_over
    global jeu_en_cours, dernier_temps_pourri, tps_pourr

    configurer_fenetre_2_joueurs()
    forme_suiv = nouvelle_forme()
    j2_forme_suiv = nouvelle_forme()

    while jeu_en_cours:
        fltk.efface_tout()

        if forme_actuelle is None:
            forme_actuelle = forme_suiv
            forme_suiv = nouvelle_forme()

        if j2_forme_actuelle is None:
            j2_forme_actuelle = j2_forme_suiv
            j2_forme_suiv = nouvelle_forme()

        gerer_clavier()  
        gerer_clavier_j2() 

        for i in range(HAUTEUR_GRILLE):
            for j in range(LARGEUR_GRILLE):
                if grille[i][j] is not None:
                    x1 = j * TAILLE_CASE + LONGUEUR_INFO * TAILLE_CASE
                    y1 = i * TAILLE_CASE
                    x2 = x1 + TAILLE_CASE
                    y2 = y1 + TAILLE_CASE
                    fltk.rectangle(x1, y1, x2, y2, remplissage=grille[i][j])

                if j2_grille[i][j] is not None:
                    x1 = j * TAILLE_CASE + LARGEUR_GRILLE * TAILLE_CASE + LONGUEUR_INFO * TAILLE_CASE
                    y1 = i * TAILLE_CASE
                    x2 = x1 + TAILLE_CASE
                    y2 = y1 + TAILLE_CASE
                    fltk.rectangle(x1, y1, x2, y2, remplissage=j2_grille[i][j])

        for i in range(HAUTEUR_GRILLE + 1):
            fltk.ligne(
                LONGUEUR_INFO * TAILLE_CASE, i * TAILLE_CASE,
                LARGEUR_GRILLE * TAILLE_CASE + LONGUEUR_INFO * TAILLE_CASE, i * TAILLE_CASE,
                couleur="white"
            )
        for j in range(LARGEUR_GRILLE + 1):
            fltk.ligne(
                j * TAILLE_CASE + LONGUEUR_INFO * TAILLE_CASE, 0,
                j * TAILLE_CASE + LONGUEUR_INFO * TAILLE_CASE, HAUTEUR_GRILLE * TAILLE_CASE,
                couleur="white"
            )

        for i in range(HAUTEUR_GRILLE + 1):
            fltk.ligne(
                LARGEUR_GRILLE * TAILLE_CASE + LONGUEUR_INFO * TAILLE_CASE, i * TAILLE_CASE,
                2 * LARGEUR_GRILLE * TAILLE_CASE + LONGUEUR_INFO * TAILLE_CASE, i * TAILLE_CASE,
                couleur="white"
            )
        for j in range(LARGEUR_GRILLE + 1):
            fltk.ligne(
                j * TAILLE_CASE + LARGEUR_GRILLE * TAILLE_CASE + LONGUEUR_INFO * TAILLE_CASE, 0,
                j * TAILLE_CASE + LARGEUR_GRILLE * TAILLE_CASE + LONGUEUR_INFO * TAILLE_CASE, HAUTEUR_GRILLE * TAILLE_CASE,
                couleur="white"
            )

        dessiner_separation()

        dessiner_forme(forme_actuelle["forme"], forme_actuelle["couleur"], forme_actuelle["position"])
        dessiner_forme_j2(j2_forme_actuelle["forme"], j2_forme_actuelle["couleur"], j2_forme_actuelle["position"])

        afficher_info()
        afficher_info_j2()

        mettre_a_jour_forme()
        mettre_a_jour_forme_j2()
        prochain_forme()
        dessiner_forme_j2(j2_forme_suiv["forme"], j2_forme_suiv["couleur"], (0, LARGEUR_GRILLE + 2))

        fltk.mise_a_jour()
        fltk.attente(vitesse)

        # Vérification des états de fin de jeu
        if game_over or j2_game_over:
            perdu()
            break

def detecter_connexions_adjacentes():
    """
    Détecte et supprime les pièces adjacentes ayant la même couleur,
    avec au moins deux côtés connectés, mais en excluant les blocs
    appartenant à une seule et même forme.
    """
    global grille, score, elim_couleurs_adjacentes, forme_actuelle

    # Si le bonus n'est pas activé, sortir immédiatement
    if not elim_couleurs_adjacentes:
        return

    hauteur = len(grille)
    largeur = len(grille[0])
    blocs_a_supprimer = set()

    # Identifier les blocs de la forme actuelle
    blocs_forme_actuelle = set()
    if forme_actuelle is not None:
        ligne_debut, colonne_debut = forme_actuelle["position"]
        for i, ligne in enumerate(forme_actuelle["forme"]):
            for j, case in enumerate(ligne):
                if case == 1:
                    blocs_forme_actuelle.add((ligne_debut + i, colonne_debut + j))

    # Parcourir chaque bloc de la grille
    for i in range(hauteur):
        for j in range(largeur):
            if grille[i][j] is not None:
                couleur = grille[i][j]
                voisins_identiques = []

                # Vérifier les voisins adjacents
                for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # Haut, Bas, Gauche, Droite
                    ni, nj = i + di, j + dj
                    if (
                        0 <= ni < hauteur and 0 <= nj < largeur and
                        grille[ni][nj] == couleur and
                        (ni, nj) not in blocs_forme_actuelle  # Exclure la même forme
                    ):
                        voisins_identiques.append((ni, nj))

                # Ajouter les blocs si au moins deux voisins identiques sont trouvés
                if len(voisins_identiques) >= 2:
                    blocs_a_supprimer.add((i, j))
                    blocs_a_supprimer.update(voisins_identiques)

    # Supprimer les blocs détectés
    for i, j in blocs_a_supprimer:
        grille[i][j] = None

    # Calcul des points
    points_supprimes = len(blocs_a_supprimer)
    if points_supprimes > 0:
        score += points_supprimes * 50  # Exemple : 50 points par bloc supprimé


 #def mettre_a_jour_forme():
     #global forme_actuelle, grille, forme_suiv, game_over

   #  if forme_actuelle is not None:
        # ligne, colonne = forme_actuelle["position"]
        # nouvelle_position = (ligne + 1, colonne)

         #if collisions(forme_actuelle["forme"], nouvelle_position):
            # Fixer les blocs de la pièce actuelle dans la grille
            # for i, ligne_forme in enumerate(forme_actuelle["forme"]):
              #   for j, case in enumerate(ligne_forme):
                    # if case == 1 and ligne + i < HAUTEUR_GRILLE:
                    #     grille[ligne + i][colonne + j] = forme_actuelle["couleur"]

           #  if ligne == 0:
            #     game_over = True
            #     return

         #    forme_actuelle = forme_suiv
         #    forme_suiv = nouvelle_forme()

            # Appeler la détection des couleurs adjacentes si le bonus est actif
        #     detecter_connexions_adjacentes()
  #       else:
    #         forme_actuelle["position"] = nouvelle_position

    #ligne_complete()




def afficher_info_j2():
    """Affiche les informations du joueur 2 dans une zone distincte à droite de l'écran."""
    global j2_score, j2_niveau, tps_pourr

    # Dessiner le fond noir pour la zone d'information du joueur 2
    fltk.rectangle(
        LARGEUR_GRILLE * TAILLE_CASE + LONGUEUR_INFO * TAILLE_CASE, 0,
        (LARGEUR_GRILLE * 2 + LONGUEUR_INFO) * TAILLE_CASE, HAUTEUR_ZONE,
        remplissage="black"
    )

    # Afficher les informations principales
    fltk.texte(
        (LARGEUR_GRILLE * 2 + LONGUEUR_INFO // 2) * TAILLE_CASE, 10,
        f"Score J2: {j2_score}",
        couleur="white", taille=14, ancrage="center"
    )
    fltk.texte(
        (LARGEUR_GRILLE * 2 + LONGUEUR_INFO // 2) * TAILLE_CASE, 30,
        f"Niveau J2: {j2_niveau}",
        couleur="white", taille=14, ancrage="center"
    )

    # Afficher les autres informations si nécessaire (par ex. pourrissement)
    if tps_pourr > 0:
        fltk.texte(
            (LARGEUR_GRILLE * 2 + LONGUEUR_INFO // 2) * TAILLE_CASE, 50,
            f"Pourrissement: {tps_pourr}",
            couleur="white", taille=14, ancrage="center"
        )

    # Ligne de séparation visuelle entre la zone d'information et la grille
    fltk.ligne(
        LARGEUR_GRILLE * TAILLE_CASE + LONGUEUR_INFO * TAILLE_CASE, 0,
        LARGEUR_GRILLE * TAILLE_CASE + LONGUEUR_INFO * TAILLE_CASE, HAUTEUR_ZONE,
        couleur="white", epaisseur=4
    )

def configurer_fenetre_2_joueurs():
    """Configure les dimensions de la fenêtre pour le mode 2 joueurs."""
    global LARGEUR_ZONE, HAUTEUR_ZONE

    # Doubler la largeur pour inclure les deux grilles
    LARGEUR_ZONE = 3 * (LARGEUR_GRILLE * TAILLE_CASE + LONGUEUR_INFO * TAILLE_CASE)
    HAUTEUR_ZONE = HAUTEUR_GRILLE * TAILLE_CASE

    fltk.ferme_fenetre()
    fltk.cree_fenetre(LARGEUR_ZONE, HAUTEUR_ZONE)



if __name__ == "__main__":
    fltk.cree_fenetre(LARGEUR_ZONE, HAUTEUR_ZONE)
    
    while True: 
        choix = menu()
        
        if choix == 0:  
            print("Démarrage d'une nouvelle partie.")
            boucle_principale()

        elif choix == 1:  
            print("Chargement d'une partie existante.")
            charger_sauv()
            boucle_principale()

        elif choix == 2:  
            while True: 
                choix_var = menu_variantes()
                
                if choix_var == 0:
                    print("Mode Pourrissement Activé")
                    try:
                        tps_pourr = int(input("Temps de pourrissement en secondes ? (entrez un nombre entier) : "))
                    except ValueError:
                        print("Entrée invalide, le pourrissement n'a pas été activé.")
                        tps_pourr = 0
                
                elif choix_var == 1:
                    print("Score par niveau activé")
                    scoreParniv = True
                
                elif choix_var == 2:
                    fichier = input("Entrez le nom du fichier contenant les polyominos : ")
                    POLYOMINOS_PERSONNALISES = charger_polyominos(fichier)
                    if POLYOMINOS_PERSONNALISES:
                        print(f"{len(POLYOMINOS_PERSONNALISES)} polyominos personnalisés chargés.")
                    else:
                        print("Aucun polyomino personnalisé chargé. Utilisation des formes par défaut.")
                
                
                elif choix_var == 3:
                    print("Retour au menu principal.")
                    break
                
                else:
                    print("Option invalide, veuillez réessayer.")

        elif choix == 3:  
            while True: 
                choix_bon = menu_bonus()
                
                if choix_bon == 0:
                    config()
                    print("Configuration Sauvegardée")

                
                elif choix_bon == 1:
                    charger_config()
                    print("Configuration Chargée")

                
                elif choix_bon == 2:
                    bloc_bonus_activ = True
                    print(f'Bloc Bonus Activé')
                
                elif choix_bon == 3:
                    print("Couleurs Adjacentes Activé")
                    elim_couleurs_adjacentes = True
                
                elif choix_bon == 4:
                    print("Retour au menu principal.")
                    break
                
                else:
                    print("Option invalide, veuillez réessayer.")

        elif choix == 4:  
            print("Démarrage du mode 2 joueurs.")
            boucle_principale_2_joueurs()

        elif choix == 5:  
            jeu_en_cours = False
        else:
            print("Option invalide, veuillez redémarrer le programme.")
            break

        if not jeu_en_cours:  
            break

    fltk.ferme_fenetre()
