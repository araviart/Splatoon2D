# coding: utf-8
import argparse
import random
import client
import const
import plateau
import case
import joueur

from math import *

#autre item que le pistolet sur la case ou le pistolet doit etre utilisé

def mon_IA(ma_couleur,carac_jeu, plan, les_joueurs):
    global ETAT
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
    etat_id = {
        "stack": 0,
        "objet": 1,
        "attaque": 2,
        "bidon": 3,
        "pistolet": 4,
        "bombe": 5,
        "start": 6
    }
    etat = 0

    plateau_jeux = plateau.Plateau(plan)
    pos = position(les_joueurs, ma_couleur)

    objet_j = objet_joueur(les_joueurs, ma_couleur)
    objet_d = objet_duree(les_joueurs, ma_couleur)

    reserve = reserve_joueur(les_joueurs, ma_couleur)

    objet_pl = objet(plateau_jeux, pos)

    # premier et deuxième tour 
    if int(carac_jeu.split(";")[0]) == 0 or int(carac_jeu.split(";")[0]) == 1:
        etat = etat_id["start"]

    elif objet_pl is not None and recup_objet(objet_pl[2], objet_j, reserve): # mettre le cout et si on est le plus pret 
        etat = etat_id["objet"]

    elif reserve >= 30 and etat != etat_id["objet"]:
        etat = etat_id["attaque"]

    elif objet_pl is None and reserve >= 20:
        etat = etat_id["attaque"]

    elif objet_pl is None and reserve <= 5:
        plus_proche = case_plus_proche(plateau_jeux, pos, ma_couleur)
        if plus_proche is not None:
            dist = distance(plateau_jeux, pos, plus_proche)
            if dist < reserve:
                etat = etat_id["stack"]
            else:
                etat = etat_id["attaque"]
        else:
            etat = etat_id["attaque"]

    elif objet_j == const.PISTOLET:
        etat = etat_id["pistolet"]

    elif objet_j == const.BOMBE:
        etat = etat_id["bombe"]

    print(etat)
    #############################
    
    if etat == etat_id["attaque"] and reserve > 30:
        t = tir(plateau_jeux, pos, 5, ma_couleur)
        return t+t

    if etat == etat_id["pistolet"] and objet_j == const.PISTOLET:
        distance_max = 5
        if reserve >= distance_max:
            distance_max = reserve

        # position ou aller pour avoir un nombre de mur peint au maximal a l'utilisation du pistolet
        positionn = pistolet(plateau_jeux, pos, distance_max, objet_duree(les_joueurs, ma_couleur))

        # a atteint la position idéale pour tiré
        if pos == (positionn[0], positionn[1]):
            return positionn[2]+random.choice("NSEO")

        if positionn is not None:
            # transforme la position en direction
            direction = direction_chemin(plateau_jeux, pos, (positionn[0], positionn[1]))
            return tir(plateau_jeux, pos, 5, ma_couleur)+direction

    elif etat == etat_id["objet"] and recup_objet(objet_pl[2], objet_j, reserve):
        # transforme la position de l'objet en direction
        direction = direction_chemin(plateau_jeux, pos, (objet_pl[0], objet_pl[1]))
        if direction is not None:            
            return "X"+direction
        else:
            objet_pl = objet(plateau_jeux, pos)
            direction = direction_chemin(plateau_jeux, pos, (objet_pl[0], objet_pl[1]))
            if direction is not None:
                return "X"+direction

    elif etat == etat_id["bombe"] and objet_j == const.BOMBE:
        distance_max = 5
        if reserve >= distance_max:
            distance_max = reserve

        # position ou aller pour avoir un nombre de mur peint au maximal a l'utilisation du pistolet
        positionn = bombe(plateau_jeux, pos, distance_max, objet_duree(les_joueurs, ma_couleur))

        # a atteint la position idéale pour tiré
        if pos == (positionn[0], positionn[1]):
            return positionn[2]+random.choice("NSEO")

        if positionn is not None:
            # transforme la position en direction
            direction = direction_chemin(plateau_jeux, pos, (positionn[0], positionn[1]))
            return tir(plateau_jeux, pos, 5, ma_couleur)+direction

    elif etat == etat_id["stack"]:
        pos2 = case_plus_proche(plateau_jeux, pos, ma_couleur)
        if pos2 is not None:
            direction = direction_chemin(plateau_jeux, pos, pos2)
            if direction is not None:
                return "X"+direction

    elif etat == etat_id["bidon"]:
        for l in range(plateau.get_nb_lignes(plateau_jeux)):
            for c in range(plateau.get_nb_colonnes(plateau_jeux)):
                casepl = plateau.get_case(plateau_jeux, (l, c))
                if case.get_objet(casepl) == const.BIDON:
                    direction = direction_chemin(plateau_jeux, pos, (l, c))
                    if direction is not None:
                        return "X"+direction

    direction = "N"
    for d in plateau.directions_possibles(plateau_jeux, pos):
        direction = d

    if etat == etat_id["start"]:
        return direction+direction


    return "X"+direction


def tir(plateau_jeux, pos, distance_max, couleur):
    direction = "X"
    nb_direction = 0
    for d, pos2 in plateau.INC_DIRECTION.items():
        nb = 0
        for i in range(distance_max):
            if pos[0] >= 0 and pos[0] < plateau.get_nb_lignes(plateau_jeux) and pos[1] >= 0 and pos[1] < plateau.get_nb_colonnes(plateau_jeux):
                case_pl = plateau.get_case(plateau_jeux, pos)
                if case.est_mur(case_pl) and case.get_couleur(case_pl) != couleur:
                    nb += 1
            pos = (pos[0]+pos2[0], pos[1]+pos2[1])
        if direction == "X" or nb > nb_direction:
            nb_direction = nb
            direction = d

    # si il y a aucune case a peindre on le peint pas
    if nb_direction == 0:
        return "X"

    return direction

def bombe(plateau_jeux, pos, distance_max, deplacement_max): # deplacement max avant que l'item disparaisse
    liste_pos = dict() # liste des positions
    positions = [] #stocke position
    positions.append(pos) # stocke premiere position
    liste_pos[pos] = 0
    while len(positions) > 0: # tant qu'il y'a toujours une position
        for pos in positions.copy(): # parcours pos
            for direction in plateau.directions_possibles(plateau_jeux, pos): 
                d = plateau.INC_DIRECTION[direction]
                new_pos = (pos[0] + d[0], pos[1] + d[1])
                if new_pos not in liste_pos.keys() and liste_pos[pos]+1 < deplacement_max: # si le déplacement n'a pas était mit à liste
                    liste_pos[new_pos] = liste_pos[pos] +1 # ajout de la nouvelle position
                    positions.append(new_pos) # plus de position
            positions.remove(pos)
    position = None
    max_nb = 0
    for pos in liste_pos:
        for d, pos2 in plateau.INC_DIRECTION.items():
            if d != "X":
                nbcase = nb_case(plateau_jeux, pos, d, distance_max)
                if position is None or nbcase > max_nb:
                    max_nb = nbcase
                    position = (pos[0], pos[1], d)
    return position


def nb_case(plateau_jeux, pos, direction, distance_max):
    direction = plateau.INC_DIRECTION[direction]
    nb = 0
    for i in range(distance_max):
        if pos[0] >= 0 and pos[0] < plateau.get_nb_lignes(plateau_jeux) and pos[1] >= 0 and pos[1] < plateau.get_nb_colonnes(plateau_jeux):
            case_pl = plateau.get_case(plateau_jeux, pos)
            if not case.est_mur(case_pl):
                nb += 1
        pos = (pos[0]+direction[0], pos[1]+direction[1])
    return nb

def case_plus_proche(plateau_jeux, pos, couleur):
    c = calque(plateau_jeux, pos)
    for coordonne, valeur in c.items():
        if coordonne != pos:
            casepl = plateau.get_case(plateau_jeux, coordonne)
            if case.get_couleur(casepl) == couleur and case.est_mur(casepl) is False:
                return coordonne
    return None

def position(les_joueurs, couleur):
    for joueur in les_joueurs.split("\n"):
        info = joueur.split(";")
        if info[0] == couleur:
            return (int(info[5]), int(info[6]))
    return (0, 0)

def objet_duree(les_joueurs, couleur):
    for joueur in les_joueurs.split("\n"):
        info = joueur.split(";")
        if info[0] == couleur:
            return int(info[4])
    return 0

def objet_joueur(les_joueurs, couleur):
    for joueur in les_joueurs.split("\n"):
        info = joueur.split(";")
        if info[0] == couleur:
            return int(info[3])
    return const.AUCUN

def reserve_joueur(les_joueurs, couleur):
    for joueur in les_joueurs.split("\n"):
        info = joueur.split(";")
        if info[0] == couleur:
            return int(info[1])
    return 0

def objet(plateau_jeux, pos_joueur):
    """retourne l'objet le plus proche

    Args:
        plateau_jeux (_type_): _description_
        pos_joueur (_type_): _description_

    Returns:
        None|tuple: _description_
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
        plateau_jeux (_type_): _description_
        les_joueurs (_type_): _description_
        pos (_type_): _description_

    Returns:
        _type_: _description_
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
    """indique si récupérer un objet est plus avantageux

    Args:
        objet (_type_): _description_
        objet_joueur (_type_): _description_

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
    liste = dict()
    positions = []
    positions.append(pos)
    liste[pos] = 0
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
        for d, pos2 in plateau.INC_DIRECTION.items():
            mur = nb_mur(plateau_jeux, pos, d, distance_max)
            if position is None or mur > max_nb:
                max_nb = mur
                position = (pos[0], pos[1], d)

    return position

def nb_mur(plateau_jeux, pos, direction, distance_max):
    direction = plateau.INC_DIRECTION[direction]
    nb = 0
    for i in range(distance_max):
        if pos[0] >= 0 and pos[0] < plateau.get_nb_lignes(plateau_jeux) and pos[1] >= 0 and pos[1] < plateau.get_nb_colonnes(plateau_jeux):
            case_pl = plateau.get_case(plateau_jeux, pos)
            if case.est_mur(case_pl) and case.get_couleur(case_pl) == " ":
                nb += 1
        pos = (pos[0]+direction[0], pos[1]+direction[1])
    return nb


def calque(plateau_jeux, pos1):
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


def danger(plateau_jeux, pos, distance_max=5):
    """indique si on peut etre touché par un autre joueur

    Args:
        plateau_jeux (_type_): _description_
        pos (_type_): _description_
        distance_max (int, optional): _description_. Defaults to 5.

    Returns:
        _type_: _description_
    """    
    nb = 0
    for direction in plateau.INC_DIRECTION:
        nb += plateau.nb_joueurs_direction(plateau_jeux, pos, direction, distance_max)
    if nb > 0:
        return True
    return False

def deplace_danger(plateau_jeux, pos, distance_max=5):
    directions = plateau.directions_possibles(plateau_jeux, pos)
    nb_min = 0
    direction = None
    for d in directions.keys():
        nb = plateau.nb_joueurs_direction(plateau_jeux, pos, d, distance_max)
        if direction is None or nb_min < nb:
            direction = d
            nb_min = nb
    return direction


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
