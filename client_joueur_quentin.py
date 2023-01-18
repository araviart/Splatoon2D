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
    pos = None
    joueurs = les_joueurs.split("\n")
    for joueur in joueurs:
        info = joueur.split(";")
        if info[0] == ma_couleur:
            pos = (int(info[5]), int(info[6]))

    plateau_jeux = plateau.Plateau(plan)

    objets = []
    for l in range(plateau.get_nb_lignes(plateau_jeux)):
        for c in range(plateau.get_nb_colonnes(plateau_jeux)):
            casepl = plateau.get_case(plateau_jeux, (l, c))
            if case.get_objet(casepl) != const.AUCUN:
                a = direction_chemin(plateau_jeux, pos, (l, c))
                if a is not None:
                    objets.append((l, c, a))

    def critere(tuple):
        return tuple[2]

    if len(objets) > 0:
        objet = sorted(objets, key=critere, reverse=True)[0]
        print(objet[2], pos, (objet[0], objet[1]))
        return random.choice("NSOE")+objet[2]

    return random.choice("NSOE")+random.choice("NSEO")

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

    print(liste)
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
            if case.est_mur(case_pl):
                nb += 1
        pos = (pos[0]+direction[0], pos[1]+direction[1])
    return nb


def recup_objet(plateau_jeux, joueurs, objet1, objet2):
    distance_joueur = dict()
    for joueur, info in joueurs.items():
        #distance_joueur[joueur] = distance(plateau_jeux, (objet))
        pass

def joueurs_info(les_joueurs):
    positions = dict()
    for joueur in les_joueurs.split("\n"):
        j = joueur.split(";")
        positions[j[0]] = (int(j[1]), int(j[2]), int(j[3]), int(j[4]), int(j[5]), int(j[6]))
    return positions

def objets(plateau_jeux):
    objets_pl = []
    for l in range(plateau.get_nb_lignes(plateau_jeux)):
        for c in range(plateau.get_nb_colonnes(plateau_jeux)):
            casepl = plateau.get_case(plateau_jeux, (l, c))
            objet = case.get_objet(casepl)
            if objet != const.AUCUN:
                objets_pl.append((l, c, objet))
    return objets_pl

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

with open("cartes/test.txt") as fic:
    plan=fic.read()

p = plateau.Plateau(plan)
print(pistolet(p, (3, 7), 5, 5))

def danger(plateau_jeux, pos, distance_max=5):
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


# if __name__=="__main__":
#     parser = argparse.ArgumentParser()  
#     parser.add_argument("--equipe", dest="nom_equipe", help="nom de l'équipe", type=str, default='Non fournie')
#     parser.add_argument("--serveur", dest="serveur", help="serveur de jeu", type=str, default='localhost')
#     parser.add_argument("--port", dest="port", help="port de connexion", type=int, default=1111)
        
#     args = parser.parse_args()
#     le_client=client.ClientCyber()
#     le_client.creer_socket(args.serveur,args.port)
#     le_client.enregistrement(args.nom_equipe,"joueur")
#     ok=True
#     while ok:
#         ok,id_joueur,le_jeu=le_client.prochaine_commande()
#         if ok:
#             carac_jeu,le_plateau,les_joueurs=le_jeu.split("--------------------\n")
#             actions_joueur=mon_IA(id_joueur,carac_jeu,le_plateau,les_joueurs[:-1])
#             le_client.envoyer_commande_client(actions_joueur)
#             # le_client.afficher_msg("sa reponse  envoyée "+str(id_joueur)+args.nom_equipe)
#     le_client.afficher_msg("terminé")
