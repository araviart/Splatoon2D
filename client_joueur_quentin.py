# coding: utf-8
import argparse
import random
import client
import const
import plateau
import case
import joueur

from math import *

def mon_IA(ma_couleur,carac_jeu, plan, les_joueurs):
    """ Cette fonction permet de calculer les deux actions du joueur de couleur ma_couleur
        en fonction de l'état du jeu décrit par les paramètres. 
        Le premier caractère est parmi XSNOE X indique pas de peinture et les autres
        caractères indique la direction où peindre (Nord, Sud, Est ou Ouest)
        Le deuxième caractère est parmi SNOE indiquant la direction où se déplacer.

    Args:
        ma_couleur (str): un caractère en majuscule indiquant la couleur du jeur
        carac_jeu (str): une chaine de caractères contenant les caractéristiques
                                   de la partie séparées par des ;
             duree_act;duree_tot;reserve_init;duree_obj;penalite;bonus_touche;bonus_rechar;bonus_objet           
        plan (str): le plan du plateau comme comme indiqué dans le sujet
        les_joueurs (str): le liste des joueurs avec leur caractéristique (1 joueur par ligne)
        couleur;reserve;nb_cases_peintes;objet;duree_objet;ligne;colonne;nom_complet
    
    Returns:
        str: une chaine de deux caractères en majuscules indiquant la direction de peinture
            et la direction de déplacement
    """
    # réglage
    distance_max = 5
    attaque_seuil = 20 # reserve minimum pour attaquer
    stack = 10 # récupere de la peinture si la reserve est en dessous

    etat_id = {
        "stack": 0,
        "objet": 1,
        "attaque": 2,
        "bidon": 3,
        "pistolet": 4,
        "bombe": 5,
        "start": 6
    }
    etat = 0 # par default

    plateau_jeux = plateau.Plateau(plan)
    pos = position(les_joueurs, ma_couleur)

    direction_possible = "N" # par default pour eviter les crash si le joueur est bloqué
    for i in plateau.directions_possibles(plateau_jeux, pos):
        direction_possible = i

    # objet possèdé par le joueur
    objet_j = objet_joueur(les_joueurs, ma_couleur)
    objet_d = objet_duree(les_joueurs, ma_couleur)

    reserve = reserve_joueur(les_joueurs, ma_couleur)

    # objet disponible sur le plateau
    objet_pl = objet(plateau_jeux, pos)

    # premier et deuxième tour 
    if int(carac_jeu.split(";")[0]) == 0 or int(carac_jeu.split(";")[0]) == 1:
        etat = etat_id["start"]

    # plus aucune case et plus de peinture
    elif reserve < 0 and plateau.surfaces_peintes(plateau_jeux, len(les_joueurs.split(";")))[ma_couleur] <= 1:
        # recherche un bidon
        etat = etat_id["bidon"]

    elif reserve < 0:
        etat = etat_id["stack"]

    elif reserve < stack:
        # case la plus proche pour récupérer de la peinture 
        cplus_proche = case_plus_proche(plateau_jeux, pos, ma_couleur)
        if cplus_proche is not None:

            # récupère le cout du trajet pour rejoindre la peinture du joueur la plus proche
            cout = cout_chemin(plateau_jeux, pos, (cplus_proche[0], cplus_proche[1]), ma_couleur)
            if cout < reserve:
                etat = etat_id["stack"]

        # pose de la peinture pour pouvoir en gagner
            else:
                etat = etat_id["attaque"]
        else:
            etat = etat_id["attaque"]

    #si un objet est présent et qu'il est avantageux
    elif objet_pl is not None and recup_objet(objet_pl[2], objet_j, reserve):

        # récupère l'objet seulement si il est le plus pret
        cplus_proche = plus_proche(plateau_jeux, les_joueurs, (objet_pl[0], objet_pl[1]))
        if cplus_proche == ma_couleur:
            cout = cout_chemin(plateau_jeux, pos, (objet_pl[0], objet_pl[1]), ma_couleur)
            if cout < reserve:
                etat = etat_id["objet"]

    elif objet_j == const.PISTOLET:
        etat = etat_id["pistolet"]

    elif objet_j == const.BOMBE:
        etat = etat_id["bombe"]

    elif reserve >= attaque_seuil:
        etat = etat_id["attaque"]

    # action en fonction de l'etat
    
    if etat == etat_id["attaque"]:

        # récupère la position de la case qui n'a pas la meme couleur 
        pos2 = attaque(plateau_jeux, pos, ma_couleur)
        if pos2 is not None:
            if pos == pos2:
                #peint la case
                return direction_possible+direction_possible
            
            # transforme la position en direction 
            direction = direction_chemin(plateau_jeux, pos, pos2)
            if direction is not None:
                # se dirige vers la case
                return direction+direction

    if etat == etat_id["pistolet"]:
        # position ou aller pour avoir un nombre de mur peint le plus rentable
        pos_pistolet = pistolet(plateau_jeux, pos, distance_max, objet_d)
        if pos_pistolet is not None:
            # a atteint la position idéale pour tiré
            if pos == (pos_pistolet[0], pos_pistolet[1]):
                return pos_pistolet[2]+direction_possible

            # transforme la position en direction
            direction = direction_chemin(plateau_jeux, pos, (pos_pistolet[0], pos_pistolet[1]))
            if direction is not None:
                # se dirige vers la position idéale
                return "X"+direction

    elif etat == etat_id["bombe"]:
        # position ou aller pour avoir un nombre de case peinte le plus rentable
        pos_bombe = bombe(plateau_jeux, pos, distance_max, objet_d)
        if pos_bombe is not None:
            # a atteint la position idéale pour tiré
            if pos == (pos_bombe[0], pos_bombe[1]):
                return pos_bombe[2]+direction_possible

            # transforme la position en direction
            direction = direction_chemin(plateau_jeux, pos, (pos_bombe[0], pos_bombe[1]))
            if direction is not None:
                # se dirige vers la position idéale
                return "X"+direction

    elif etat == etat_id["objet"]:
        # transforme la position de l'objet en direction
        direction = direction_chemin(plateau_jeux, pos, (objet_pl[0], objet_pl[1]))
        if direction is not None:
            if reserve >= attaque_seuil:
                d = meilleur_tir(plateau_jeux, pos, ma_couleur, distance_max)
                if d is not None:
                    return d+direction

            return "X"+direction

    elif etat == etat_id["stack"]:

        # récupère la position la plus proche qui permet de récupéré de la peinture 
        # en alternant de position entre deux cases 
        pos2 = cumul_peinture(plateau_jeux, pos, ma_couleur)
        if pos2 is not None:

            #transforme la position en direction
            direction = direction_chemin(plateau_jeux, pos, pos2)
            if direction is not None:
                return "X"+direction

    # récupère les bidons peut importe la distance
    # utile si le joueur n'a plus de case et de reserve
    elif etat == etat_id["bidon"]:
        for l in range(plateau.get_nb_lignes(plateau_jeux)):
            for c in range(plateau.get_nb_colonnes(plateau_jeux)):
                casepl = plateau.get_case(plateau_jeux, (l, c))
                if case.get_objet(casepl) == const.BIDON:

                    # direction a prendre pour aller a la position
                    direction = direction_chemin(plateau_jeux, pos, (l, c))
                    if direction is not None:
                        return "X"+direction

    # permet de poser directement de peinture pour commencer
    # a en gagner d'avantage
    elif etat == etat_id["start"]:
        return direction_possible+direction_possible

    #tir et se déplace dans une direction possible
    return direction_possible+direction_possible

def meilleur_tir(plateau_jeux, pos, couleur, distance_max):
    """retourne la meilleur direction pour tirer

    Args:
        plateau_jeux (dict): plateau du jeu
        pos (tuple): position du joueur
        couleur (str): couleur du joueur
        distance_max (int): distance max 

    Returns:
        str: direction
    """    
    direction = None
    nb_max = 0
    for d, pos2 in plateau.INC_DIRECTION.items():
        pos3 = pos
        mur = False
        nb = 0
        for i in range(distance_max):
            pos3 = (pos3[0] + pos2[0], pos3[1] + pos2[1])
            if pos3[0] >= 0 and pos3[0] < plateau.get_nb_lignes(plateau_jeux) and pos3[1] >= 0 and pos3[1] < plateau.get_nb_colonnes(plateau_jeux):
                casepl = plateau.get_case(plateau_jeux, pos3)
                if case.est_mur(casepl):
                    mur = True
                if mur is False and case.get_couleur(casepl) != couleur:
                    nb += 1
        if direction is None or nb > nb_max:
            direction = d
            nb_max = nb
    return direction

def attaque(plateau_jeux, pos, couleur):
    """retourne la case la plus proche pouvant etre peinte

    Args:
        plateau_jeux (dict): plateau du jeu
        pos (tuple): position du joueur (ligne, colonne)
        couleur (str): couleur du joueur

    Returns:
        tuple|None: tuple (ligne, colonne) de la position de la case la plus proche, None si aucune
    """    
    c = calque(plateau_jeux, pos)
    for coordonne, valeur in c.items():
        if coordonne != pos: #ne va pas sur la case ou il se trouve
            casepl = plateau.get_case(plateau_jeux, coordonne)
            if case.get_couleur(casepl) != couleur and case.est_mur(casepl) is False:
                return coordonne
    return None

def case_plus_proche(plateau_jeux, pos, couleur):
    """retourne la position de la case la plus proche d'une certaine couleur

    Args:
        plateau_jeux (dict): plateau du jeu
        pos (tuple): position du joueur (ligne, colonne)
        couleur (str): couleur du joueur

    Returns:
        tuple|None: tuple (ligne, colonne) de la position de la case la plus proche, None si aucune
    """    
    c = calque(plateau_jeux, pos)
    for coordonne, valeur in c.items():
        if coordonne != pos: #ne va pas sur la case ou il se trouve
            casepl = plateau.get_case(plateau_jeux, coordonne)
            if case.get_couleur(casepl) == couleur and case.est_mur(casepl) is False:
                return coordonne
    return None

def cumul_peinture(plateau_jeux, pos, couleur):
    """determine l'emplacement ou aller afin de récupéré de la peinture

    Args:
        plateau_jeux (dict): plateau du jeu
        pos (tuple): position du joueur (ligne, colonne)
        couleur (str): couleur du joueur

    Returns:
        tuple|None: tuple (ligne, colonne) de la position de la case la plus proche, None si aucune
    """    
    c = calque(plateau_jeux, pos)
    for coordonne, valeur in c.items():
        if coordonne != pos:
            casepl = plateau.get_case(plateau_jeux, coordonne)
            if case.get_couleur(casepl) == couleur and case.est_mur(casepl) is False:

                # recherche si une autre case est présente a coter afin d'alterner
                for d in plateau.INC_DIRECTION.values():
                    new_pos = (coordonne[0] + d[0], coordonne[1] + d[1])
                    # la position est sur le plateau
                    if new_pos[0] >= 0 and new_pos[0] < plateau.get_nb_lignes(plateau_jeux) and new_pos[1] >= 0 and new_pos[1] < plateau.get_nb_colonnes(plateau_jeux):
                        new_casepl = plateau.get_case(plateau_jeux, new_pos)
                        if case.get_couleur(new_casepl) == couleur or case.get_couleur(new_casepl) == " " and case.est_mur(new_casepl):
                            return coordonne
    return None # aucun emplacement

def position(les_joueurs, couleur):
    """retourne la position d'un joueur en particulier

    Args:
        les_joueurs (str): le liste des joueurs avec leur caractéristique (1 joueur par ligne)
        couleur;reserve;nb_cases_peintes;objet;duree_objet;ligne;colonne;nom_complet

        couleur (str): couleur du joueur

    Returns:
        tuple: (ligne, colonne)
    """    
    for joueur in les_joueurs.split("\n"):
        info = joueur.split(";")
        if info[0] == couleur:
            return (int(info[5]), int(info[6]))
    return (0, 0) #normalement se produit jamais

def objet_duree(les_joueurs, couleur):
    """retourne la durée de l'objet d'un joueur en particulier

    Args:
        les_joueurs (str): le liste des joueurs avec leur caractéristique (1 joueur par ligne)
        couleur;reserve;nb_cases_peintes;objet;duree_objet;ligne;colonne;nom_complet

        couleur (str): couleur du joueur

    Returns:
        int: tour restant avant la disparition
    """   
    for joueur in les_joueurs.split("\n"):
        info = joueur.split(";")
        if info[0] == couleur:
            return int(info[4])
    return 0 #normalement se produit jamais

def objet_joueur(les_joueurs, couleur):
    """retourne l'objet d'un joueur en particulier

    Args:
        les_joueurs (str): le liste des joueurs avec leur caractéristique (1 joueur par ligne)
        couleur;reserve;nb_cases_peintes;objet;duree_objet;ligne;colonne;nom_complet

        couleur (str): couleur du joueur

    Returns:
        int: id de l'objet du joueur
    """   
    for joueur in les_joueurs.split("\n"):
        info = joueur.split(";")
        if info[0] == couleur:
            return int(info[3])
    return const.AUCUN

def reserve_joueur(les_joueurs, couleur):
    """retourne la reserve d'un joueur en particulier

    Args:
        les_joueurs (str): le liste des joueurs avec leur caractéristique (1 joueur par ligne)
        couleur;reserve;nb_cases_peintes;objet;duree_objet;ligne;colonne;nom_complet

        couleur (str): couleur du joueur

    Returns:
        int: reserve de peinture
    """   
    for joueur in les_joueurs.split("\n"):
        info = joueur.split(";")
        if info[0] == couleur:
            return int(info[1])
    return 0

def objet(plateau_jeux, pos_joueur):
    """retourne l'objet qui est le plus proche

    Args:
        plateau_jeux (dict): plateau
        pos_joueur (tuple): position du joueur sur le plateau (ligne, colonne)

    Returns:
        None|tuple: tuple (ligne, colonne, objet) ou None si aucun 
    """
    o = None
    dist = 0
    for l in range(plateau.get_nb_lignes(plateau_jeux)):
        for c in range(plateau.get_nb_colonnes(plateau_jeux)):
            casepl = plateau.get_case(plateau_jeux, (l, c))
            if case.get_objet(casepl) != const.AUCUN:
                direction = direction_chemin(plateau_jeux, pos_joueur, (l, c))
                if direction is not None:
                    dist2 = distance(plateau_jeux, pos_joueur, (l, c))
                    if dist2 is not None:
                        if o is None or dist2 < dist:
                            o = (l, c, case.get_objet(casepl))
                            dist = dist2
    return o

def plus_proche(plateau_jeux, les_joueurs, pos):
    """retourne le joueur le plus proche d'une certaine position

    Args:
        plateau_jeux (dict): plateau du jeu
        les_joueurs (str): le liste des joueurs avec leur caractéristique (1 joueur par ligne)
        couleur;reserve;nb_cases_peintes;objet;duree_objet;ligne;colonne;nom_complet        
        pos (tuple): position (ligne, colonne)

    Returns:
        str: joueur le plus proche de la position
    """
    joueur = None
    dist = 0
    for j in les_joueurs.split("\n"):
        info = j.split(";")
        p = (int(info[5]), int(info[6]))
        dist2 = distance(plateau_jeux, p, pos)
        if joueur is None or dist2 < dist:
            joueur = info[0]
            dist = dist2
    return joueur

def recup_objet(objet, objet_joueur, reserve):
    """indique si récupérer l'objet est plus avantageux

    Args:
        objet (int): objet qui peut etre récupéré
        objet_joueur (_type_): objet du joueur

    Returns:
        _type_: _description_
    """
    if objet_joueur == const.AUCUN and objet == const.BIDON and reserve > 0:
        return False

    if objet_joueur == const.AUCUN:
        return True

    if objet == const.BIDON and reserve < 0:
        return True
    elif objet == const.BIDON and reserve > 0:
        return False
        
    # classement pour avoir un ordre de priorité
    classement = {
        const.BIDON: 4,
        const.BOMBE: 1, 
        const.BOUCLIER: 3,
        const.PISTOLET: 2,
    }
    if classement[objet] < classement[objet_joueur]:
        return True
    return False

def pistolet(plateau_jeux, pos, distance_max, deplacement_max):
    """indique la meilleur position pour utiliser le pistolet

    Args:
        plateau_jeux (dict): plateau du jeu
        pos (tuple): position (ligne, colonne)
        direction (str): direction 
        distance_max (int): distance maximum

    Returns:
       tuple: position du meilleur emplacement pour utiliser le pistolet
    """   
    liste = dict()
    positions = []
    positions.append(pos)
    liste[pos] = 0

    # récupère les positions possibles dans un certain rayon (deplacement_max)
    while len(positions) > 0:
        for pos in positions.copy():
            for direction in plateau.directions_possibles(plateau_jeux, pos):
                d = plateau.INC_DIRECTION[direction]
                new_pos = (pos[0] + d[0], pos[1] + d[1])
                if new_pos not in liste.keys() and liste[pos]+1 < deplacement_max:
                    liste[new_pos] = liste[pos] +1
                    positions.append(new_pos)

            positions.remove(pos)

    max_nb = 0
    position = None
    for pos in liste:
        casepl = plateau.get_case(plateau_jeux, pos)
        objet_pos = case.get_objet(casepl)
        if objet_pos == const.AUCUN or objet_pos == const.PISTOLET:
            for d, pos2 in plateau.INC_DIRECTION.items():
                mur = nb_mur(plateau_jeux, pos, d, distance_max)
                if position is None or mur > max_nb:
                    max_nb = mur
                    position = (pos[0], pos[1], d)
    return position

def bombe(plateau_jeux, pos, distance_max, deplacement_max):
    """indique la meilleur position pour utiliser la bombe

    Args:
        plateau_jeux (dict): plateau du jeu
        pos (tuple): position (ligne, colonne)
        direction (str): direction 
        distance_max (int): distance maximum

    Returns:
       tuple: position du meilleur emplacement pour utiliser la bombe
    """    
    liste_pos = dict() 
    positions = [] 
    positions.append(pos)
    liste_pos[pos] = 0

    # récupère les positions possibles dans un certain rayon (deplacement_max)
    while len(positions) > 0:
        for pos in positions.copy():
            for direction in plateau.directions_possibles(plateau_jeux, pos): 
                d = plateau.INC_DIRECTION[direction]
                new_pos = (pos[0] + d[0], pos[1] + d[1])
                if new_pos not in liste_pos.keys() and liste_pos[pos]+1 < deplacement_max: # si le déplacement n'a pas était mit à liste
                    liste_pos[new_pos] = liste_pos[pos] +1
                    positions.append(new_pos)
            positions.remove(pos)

    position = None
    max_nb = 0
    for pos in liste_pos:
        nb = 0
        for direction, pos2 in plateau.INC_DIRECTION.items():
            mur = False
            for i in range(distance_max):
                if pos[0] >= 0 and pos[0] < plateau.get_nb_lignes(plateau_jeux) and pos[1] >= 0 and pos[1] < plateau.get_nb_colonnes(plateau_jeux):
                    case_pl = plateau.get_case(plateau_jeux, pos)
                    if case.est_mur(case_pl):
                        mur = True

                    if mur is False:
                        nb += 1
                pos = (pos[0]+pos2[0], pos[1]+pos2[1])

        if position is None or nb > max_nb:
            max_nb = nb
            position = (pos[0], pos[1], direction)
    return position

def nb_mur(plateau_jeux, pos, direction, distance_max):
    """retourne le nombre de mur dans une direction a une certaine position

    Args:
        plateau_jeux (dict): plateau du jeu
        pos (tuple): position (ligne, colonne)
        direction (str): direction 
        distance_max (int): distance maximum

    Returns:
        int: nombre de mur 
    """    
    direction = plateau.INC_DIRECTION[direction]
    nb = 0
    for i in range(distance_max):
        #si la position est sur le plateau
        if pos[0] >= 0 and pos[0] < plateau.get_nb_lignes(plateau_jeux) and pos[1] >= 0 and pos[1] < plateau.get_nb_colonnes(plateau_jeux):
            case_pl = plateau.get_case(plateau_jeux, pos)
            if case.est_mur(case_pl) and case.get_couleur(case_pl) == " ":
                nb += 1
        pos = (pos[0]+direction[0], pos[1]+direction[1])
    return nb


def calque(plateau_jeux, pos1):
    """retourne un calque du plateau indiquant la distance de chaque case par rapport à la position

    Args:
        plateau_jeux (dict): plateau du jeu
        pos1 (tuple): position (ligne, colonne)

    Returns:
        dict: positions avec leur distance de la premier position comme valeur
    """    
    liste = dict()
    positions = []
    positions.append(pos1)
    liste[pos1] = 0
    while len(positions) > 0:
        for pos in positions.copy():
            for direction in plateau.directions_possibles(plateau_jeux, pos):
                d = plateau.INC_DIRECTION[direction]
                new_pos = (pos[0] + d[0], pos[1] + d[1])
                if new_pos not in liste.keys():
                    liste[new_pos] = liste[pos] +1
                    positions.append(new_pos)

            positions.remove(pos)
    return liste

def direction_chemin(plateau_jeux, pos1, pos2):
    """donne la direction a prendre afin d'aller a la deuxieme position

    Args:
        plateau_jeux (dict): plateau du jeu
        pos1 (tuple): position (ligne, colonne)
        pos2 (tuple): position (ligne, colonne)

    Returns:
        str|None: direction ou None si pas accessible
    """    
    calque_plateau = calque(plateau_jeux, pos2)
    while pos1 in calque_plateau.keys() and calque_plateau[pos1] != 0:
        for d, p in plateau.INC_DIRECTION.items():
            new_pos = (pos1[0] + p[0], pos1[1] + p[1])
            if new_pos in calque_plateau.keys():
                if calque_plateau[new_pos] + 1 == calque_plateau[pos1]:
                    pos1 = new_pos
                    return d
    # zone pas accessible
    return None

def distance(plateau_jeux, pos1, pos2):
    """retourne la distance entre deux positions

    Args:
        plateau_jeux (dict): plateau du jeu
        pos1 (tuple): position (ligne, colonne)
        pos2 (tuple): position (ligne, colonne)

    Returns:
        int: distance entre deux positions
    """    
    liste = []
    liste.append(pos1)
    calque_plateau = calque(plateau_jeux, pos2)
    while pos1 in calque_plateau.keys() and calque_plateau[pos1] != 0:
        for d, p in plateau.INC_DIRECTION.items():
            new_pos = (pos1[0] + p[0], pos1[1] + p[1])
            if new_pos in calque_plateau.keys():
                if calque_plateau[new_pos] + 1 == calque_plateau[pos1]:
                    pos1 = new_pos
                    liste.append(new_pos)
    return len(liste)

def cout_chemin(plateau_jeux, pos1, pos2, couleur):
    """indique le cout en peindure d'un chemin entre deux positions

    Args:
        plateau_jeux (dict): plateau du jeu
        pos1 (tuple): position (ligne, colonne)
        pos2 (tuple): position (ligne, colonne)
        couleur (str): couleur du joueur

    Returns:
        int: cout du chemin
    """    
    liste = []
    liste.append(pos1)
    calque_plateau = calque(plateau_jeux, pos2)
    while pos1 in calque_plateau.keys() and calque_plateau[pos1] != 0:
        for d, p in plateau.INC_DIRECTION.items():
            new_pos = (pos1[0] + p[0], pos1[1] + p[1])
            if new_pos in calque_plateau.keys():
                if calque_plateau[new_pos] + 1 == calque_plateau[pos1]:
                    pos1 = new_pos
                    liste.append(new_pos)
    liste.remove(pos1)
    cout = 0
    for position in liste:
        casepl = plateau.get_case(plateau_jeux, position)
        if case.get_couleur(casepl) == couleur:
            cout -= 1
        elif case.get_couleur(casepl) == " ":
            cout += 1
        elif case.get_couleur(casepl) != couleur:
            cout += 2
    return cout

if __name__=="__main__":
    parser = argparse.ArgumentParser()  
    parser.add_argument("--equipe", dest="nom_equipe", help="nom de l'équipe", type=str, default='Non fournie')
    parser.add_argument("--serveur", dest="serveur", help="serveur de jeu", type=str, default='localhost')
    parser.add_argument("--port", dest="port", help="port de connexion", type=int, default=1111)
        
    args = parser.parse_args()
    le_client=client.ClientCyber()
    le_client.creer_socket(args.serveur,args.port)
    le_client.enregistrement(args.nom_equipe,"joueur")
    ok=True
    while ok:
        ok,id_joueur,le_jeu=le_client.prochaine_commande()
        if ok:
            carac_jeu,le_plateau,les_joueurs=le_jeu.split("--------------------\n")
            actions_joueur=mon_IA(id_joueur,carac_jeu,le_plateau,les_joueurs[:-1])
            le_client.envoyer_commande_client(actions_joueur)
            # le_client.afficher_msg("sa reponse  envoyée "+str(id_joueur)+args.nom_equipe)
    le_client.afficher_msg("terminé")
