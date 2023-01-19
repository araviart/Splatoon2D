# coding: utf-8
import argparse
import random
import client
import const
import plateau
import case
import joueur

from math import *

ETAT = 0

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
    plateau_jeux = plateau.Plateau(plan)
    pos = position(les_joueurs, ma_couleur)
    objet_j = objet_joueur(les_joueurs, ma_couleur)
    reserve = reserve_joueur(les_joueurs, ma_couleur)
    d = plateau.directions_possibles(plateau_jeux, pos)
    direction = "N"
    for a in d:
        direction = a

    if reserve < 0 and plateau.surfaces_peintes(plateau_jeux, 1)[ma_couleur] > 5:
        c = case_plus_proche(plateau_jeux, pos, ma_couleur)
        if c is not None:
            direction = direction_chemin(plateau_jeux, pos, c)
            if direction is not None:
                print("a")
                return "X"+direction

    if objet_j == const.PISTOLET and reserve > 0:
        positionn = pistolet(plateau_jeux, pos, 5, objet_duree(les_joueurs, ma_couleur))
        if pos == (positionn[0], positionn[1]):
            return positionn[2]+random.choice("NSEO")

        if positionn is not None:
            direction = direction_chemin(plateau_jeux, pos, (positionn[0], positionn[1]))
            return random.choice("XNSEO")+direction

    objet_pl = objet(plateau_jeux, pos)
    if objet_pl is not None:
        if recup_objet(objet_pl[2], objet_j, reserve):
            direction = direction_chemin(plateau_jeux, pos, (objet_pl[0], objet_pl[1]))
            if direction is not None:
                if reserve > 0:
                    peindre = direction
                else:
                    peindre = "X"
                return peindre+direction

    return random.choice("XNSEO")+random.choice("NSEO")

def case_plus_proche(plateau_jeux, pos, couleur):
    c = calque(plateau_jeux, pos)
    for coordonne, valeur in c.items():
        if coordonne != pos:
            casepl = plateau.get_case(plateau_jeux, coordonne)
            if case.get_couleur(casepl) == couleur:
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
    if objet_joueur == const.AUCUN:
        return True
    
    if objet == const.BIDON and reserve < -20:
        return True
    elif objet == const.BIDON and reserve >= 0:
        return False
        
    classement = {
        const.BIDON: 4,
        const.BOMBE: 2, 
        const.BOUCLIER: 3,
        const.PISTOLET: 1,
    }
    if classement[objet] < classement[objet_joueur]:
        return True
    return False

def bombe(plateau_jeux, pos, deplacement_max):
    pass

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
