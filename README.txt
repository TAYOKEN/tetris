README.txt
Yanis BOUKAYOUH et Wali Wassagoua
Bonus Implémenté

    Sauvegarde des données : Le programme permet de sauvegarder la progression du joueur. Cette fonctionnalité enregistre les informations essentielles pour que le joueur puisse reprendre là où il s'est arrêté, même après avoir quitté le jeu.

Organisation du Programme

    Main : Point d'entrée du programme, qui initialise le jeu et gère la boucle principale.
    Modules : Le programme est divisé en plusieurs modules pour gérer les différentes parties du jeu (par exemple, les ennemis, le joueur, et la gestion de la sauvegarde).
    Fichiers de Sauvegarde : Un fichier de sauvegarde est créé ou mis à jour chaque fois que le joueur décide de sauvegarder sa progression.

Choix Techniques

    Format de Sauvegarde : Nous avons opté pour un format texte simple (par exemple, JSON ou texte brut) pour stocker les données de sauvegarde. Ce format est lisible, ce qui facilite le débogage et la modification manuelle en cas de besoin.
    Gestion de la Sauvegarde : La sauvegarde est déclenchée manuellement par le joueur. Cela donne plus de contrôle au joueur sur le moment où il souhaite sauvegarder sa progression.

Problèmes Rencontrés

    Complexité de la Sauvegarde : La sauvegarde des données de jeu n'est pas toujours simple, car il faut enregistrer de nombreuses informations pour assurer une reprise fidèle de la partie. De plus, il faut gérer les erreurs qui peuvent survenir lors de l'écriture du fichier, pour éviter la perte de progression en cas de problème.