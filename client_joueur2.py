# coding: utf-8
import argparse
import random
import client
import const
import plateau
import case
import joueur

def est_safe (calque_plan, dico_joueur):
    """Cette fonction indique si il n'y a pas de joueur dans un rayon de déplacement de 6 ou -

    Args:
        calque_plan (dict): le calque du plan de jeux
        dico_joueur (dict): le dictionnaire contenant les infos de chaque joueurs

    Returns:
        bool : True si il n'y a pas de joueur dans un rayon de 6 et false sinon 
    """    
    for info_joueur in dico_joueur.values():
        if calque_plan[info_joueur["position"]] <= 6 :
            return False
    return True

def info_objet(plan):
    """Cette fonction renvoie la liste des objets présent sur le plan ainsi que leurs position

    Args:
        plan (str): le plan du plateau comme comme indiqué dans le sujet

    Returns:
        dic: Un dictionnaire ayant pour clé l'identifiant des objets et pour valeurs leurs position
    """    
    liste_ligne = plan.split("\n")
    dico_objet = {}
    for i in range(1, len(liste_ligne)):
        try :
            pos_objet = liste_ligne[-i].split(";")
            if int(pos_objet[0]) not in dico_objet.keys():
                dico_objet[int(pos_objet[0])]= {(int(pos_objet[1]), int(pos_objet[2]))}
            else :
                dico_objet[int(pos_objet[0])].add((int(pos_objet[1]), int(pos_objet[2])))
        except :
            if pos_objet != [''] :
                dico_objet["nb_objet"] = int(liste_ligne[-i])
                break
    return dico_objet

def case_appartient(plateau, ma_couleur):
    """Cette fonction permet de connaitre les cases qui sont de la meme couleur que celle passer en paramètre

    Args:
        plateau (dict): le plateau de jeux
        ma_couleur (str): la couleur voulu

    Returns:
        list: La liste des cases appartenant a la couleur passer en paramètre
    """    
    liste_case = []
    for coord, case in plateau.items():
        if isinstance(coord, tuple):
            if case["couleur"] == ma_couleur and case["mur"] == False:
                liste_case.append(coord)
    return liste_case

def calque(plateaux, pos):
    """Crée le calque du plateaux passer en paramètre

    Args:
        plateaux (dict): le plateau du plan de jeux
        pos (tuple): la position de notre joueur

    Returns:
        dict : Le calque correspondant au plan
    """
    calque = {pos:0}
    direction = plateau.directions_possibles(plateaux, pos)
    changement = True
    cpt = 0
    pos_origine = pos
    pos_possible = set()
    for dir in direction :
        pos_possible.add((pos[0] + plateau.INC_DIRECTION[dir][0], pos[1] + plateau.INC_DIRECTION[dir][1]))
    while changement :
        cpt += 1
        for pos in pos_possible :
                calque[pos] = cpt
        position_changer = pos_possible
        pos_possible = set()
        for position in position_changer:
            x = plateau.directions_possibles(plateaux, position)
            for y in x :
                if (position[0] + plateau.INC_DIRECTION[y][0], position[1] + plateau.INC_DIRECTION[y][1]) not in calque.keys() and (position[0] + plateau.INC_DIRECTION[y][0], position[1] + plateau.INC_DIRECTION[y][1]) != pos_origine:
                    pos_possible.add((position[0] + plateau.INC_DIRECTION[y][0], position[1] + plateau.INC_DIRECTION[y][1]))
        if position_changer == pos_possible :
            changement = False
    return calque

def objet_x_le_plus_proche(calque_plan, dico_objet, objet):
    """Cette fonction permet de savoir ou se situe l'objet de tel identifiant le plus proche

    Args:
        calque_plan (dict): le calque du plan de jeux
        dico_objet (dict): le dictionnaire de tous les objets avec leurs positions
        objet (int): le code de l'objet

    Returns:
        tuple : la position de l'objet (ligne, colonne)
    """    
    le_plus_proche = None
    for pos_objet in dico_objet[objet] :
        if le_plus_proche == None :
            le_plus_proche = pos_objet
        elif calque_plan[pos_objet] < calque_plan[le_plus_proche] :
            le_plus_proche = pos_objet
    return le_plus_proche

def objet_le_plus_proche(calque_plan, dico_objet):
    """Cette fonction permet de retourner l'objet le plus proche du joueur

    Args:
        calque_plan (dict): Le calque du plan de jeux
        dico_objet (dict): Le dictionnaire des objets présents sur le plan

    Returns:
        tuple: la position de l'objet le plus proche (ligne, colonne)
    """    
    dico_objet_plus_proche = {}
    le_plus_proche = None
    for objet in dico_objet.keys():
        if isinstance(objet, int):
            dico_objet_plus_proche[objet] = objet_x_le_plus_proche(calque_plan, dico_objet, objet)
    for pos_objet in dico_objet_plus_proche.values() :
        if le_plus_proche == None :
            le_plus_proche = pos_objet
        elif calque_plan[pos_objet] < calque_plan[le_plus_proche] :
            le_plus_proche = pos_objet
    return le_plus_proche

def y_aller_plus_court (plateaux, pos_arriver, pos):
    """Cette fonction permet de connaitre le chemin le plus court vers une position x

    Args:
        plateaux (dict): le plateau de jeux
        pos_arriver (tuple): la position (ligne, colonne)
        pos (tuple): la position (ligne, colonne)

    Returns:
        list : La liste des directions a effectuer
    """    
    calque_plan = calque(plateaux, pos)
    liste_position = [pos_arriver]
    liste_direction = []
    changement = True
    num_pos = calque_plan[pos_arriver]-1
    pos_actuel = pos_arriver
    pos_possible = set()
    while changement:
        for pos_voisin in plateau.directions_possibles(plateaux, pos_actuel):
            pos_possible.add((pos_actuel[0] + plateau.INC_DIRECTION[pos_voisin][0], pos_actuel[1] + plateau.INC_DIRECTION[pos_voisin][1]))
        for direction in pos_possible :
            if calque_plan[direction] == num_pos:
                if (pos_actuel[0] - direction[0], pos_actuel[1] - direction[1]) == plateau.INC_DIRECTION["N"]:
                    liste_direction.append('N')
                elif (pos_actuel[0] - direction[0], pos_actuel[1] - direction[1]) == plateau.INC_DIRECTION["S"]:
                    liste_direction.append('S')
                elif (pos_actuel[0] - direction[0], pos_actuel[1] - direction[1]) == plateau.INC_DIRECTION["E"]:
                    liste_direction.append('E')
                elif (pos_actuel[0] - direction[0], pos_actuel[1] - direction[1]) == plateau.INC_DIRECTION["O"]:
                    liste_direction.append('O')
                pos_actuel = direction
                pos_possible = set()
                num_pos -= 1
        if pos_actuel != pos :
            liste_position.append(pos_actuel)
        else :
            changement = False
    return liste_direction

def meilleur_pos_a_peindre (plateaux, pos, dic_direction, couleur, reserve, peindre_murs = False, distance_max = const.DIST_MAX) :
    """Cette fonction permet de connaitre la direction ou peindre la plus rentable

    Args:
        plateaux (dict): le plateaux de jeux
        pos (tuple): la position du joueur (ligne, colonne)
        dic_direction (dict): le dictionnaire des directions N S O E
        couleur (str): la couleur du joueur
        reserve (int): la reserve du joueur
        peindre_murs (bool, optional): _description_. Defaults to False.
        distance_max (_type_, optional): _description_. Defaults to const.DIST_MAX.

    Returns:
        str : la direction on il faut peindre
    """    
    dico_stat_peindre = {}
    direction_optit = None
    cout_min = None
    nb_repeints_max = None
    for direction in dic_direction.keys() :
        dico_stat_peindre[direction] = plateau.peindre(plateaux, pos, direction, couleur, reserve, distance_max, peindre_murs)
    for direction in dico_stat_peindre.keys() :
        if nb_repeints_max == None :
            nb_repeints_max = dico_stat_peindre[direction]["nb_repeintes"]
            cout_min = dico_stat_peindre[direction]["cout"]
            direction_optit = direction
        elif nb_repeints_max < dico_stat_peindre[direction]["nb_repeintes"] :
            dico_stat_peindre[direction]["nb_repeintes"]
            cout_min = dico_stat_peindre[direction]["cout"]
            direction_optit = direction
        elif nb_repeints_max == dico_stat_peindre[direction]["nb_repeintes"] :
            if reserve > 50 or cout_min > dico_stat_peindre[direction]["cout"] :
                dico_stat_peindre[direction]["nb_repeintes"]
                cout_min = dico_stat_peindre[direction]["cout"]
                direction_optit = direction
    return direction_optit

p2= "4;6\n#  b# \n  A## \n##A   \n  Aa##\n2\nA;0;1\nB;3;0\n1\n4;0;2"

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
    # IA complètement aléatoire
    # ici il faudra décoder le plan, les joueur et les caractéristiques du jeu
    directions = plateau.INC_DIRECTION
    le_plateau = plateau.Plateau(plan)
    liste_case = case_appartient(le_plateau, ma_couleur)
    les_objets = info_objet(plan)
    dico_joueurs = dict()
    mouvement_imp = dict()
    tire = 'X'
    for le_joueur in les_joueurs.split("\n"): 
        dico_joueurs[le_joueur[0]] = joueur.joueur_from_str(le_joueur)
    reserve = dico_joueurs[ma_couleur]["reserve"]
    pos_mon_joueur = dico_joueurs[ma_couleur]["position"]
    objet_joueur = dico_joueurs[ma_couleur]["objet"]
    le_calque = calque(le_plateau, pos_mon_joueur)
    mouvement_possible = plateau.directions_possibles(le_plateau, pos_mon_joueur)
    mouv = ""
    duree_act = int(carac_jeu.split(";")[0])
    if objet_joueur == const.PISTOLET and reserve > 0:
        for all_dir in directions.keys():
            if all_dir not in mouvement_possible.keys():
                mouvement_imp[all_dir] = ' '
        tire = meilleur_pos_a_peindre(le_plateau, pos_mon_joueur, mouvement_imp, ma_couleur, reserve, True)
    for direct in mouvement_possible.keys():
        mouv += direct    
    for direction, couleur in mouvement_possible.items():
        if (duree_act > 5 and duree_act < 30) or (reserve < 20 and reserve > 0) and dico_joueurs[ma_couleur]['surface'] > 1 and est_safe(le_calque, dico_joueurs):
            if couleur == ma_couleur:
                print("le joueur "+ ma_couleur + " recharge et est safe")
                return tire + direction
        else:        
            if reserve > 0:
                if couleur != ma_couleur:
                    if tire == 'X':
                        tire = meilleur_pos_a_peindre(le_plateau, pos_mon_joueur, mouvement_possible, ma_couleur, reserve)
                    return tire + direction
                else:
                    pos_objet = objet_le_plus_proche(le_calque, les_objets)
                    if pos_objet != None:
                        chemin = y_aller_plus_court(le_plateau, pos_objet, pos_mon_joueur)
                        if tire == 'X':
                            tire = meilleur_pos_a_peindre(le_plateau, pos_mon_joueur, mouvement_possible, ma_couleur, reserve)
                        print("le joueur " + ma_couleur + " direction "+ str(pos_objet))
                        return tire + chemin[-1]
                    else:
                        distance = 0
                        for joueur_adv in dico_joueurs.values():
                            maxi = 0
                            if joueur_adv['surface'] > maxi and joueur_adv["couleur"] != ma_couleur :
                                maxi = joueur_adv['surface']
                                pos_adverse = (joueur_adv['position'])
                                chemin = y_aller_plus_court(le_plateau, pos_adverse, pos_mon_joueur)
                                if (distance == 0 or len(chemin) < distance) and chemin != [] :
                                    distance = len(chemin)
                                    print("le chemin de "+ ma_couleur + " vers " + joueur_adv["couleur"] + " est " + str(chemin))
                                    print("le joueur " + ma_couleur + " est en chasse de "+ joueur_adv["couleur"])
                                    mouv = chemin[-1]
                                    if tire == 'X':
                                        tire = meilleur_pos_a_peindre(le_plateau, pos_mon_joueur, mouvement_possible, ma_couleur, reserve)
                                    return tire + mouv
            else:
                tire = 'X'
                if const.BIDON in les_objets.keys():
                    distance = 0
                    for coord in les_objets[const.BIDON]:
                        chemin = y_aller_plus_court(le_plateau, coord, pos_mon_joueur)
                        if distance == 0 or len(chemin) < distance :
                            distance = len(chemin)
                            mouv = chemin[-1]
                            tire = meilleur_pos_a_peindre(le_plateau, pos_mon_joueur, mouvement_possible, ma_couleur, reserve)
                            print("le joueur"+ ma_couleur + " va à bidon ")

                elif const.BOMBE in les_objets.keys():
                    distance = 0
                    for coord in les_objets[const.BOMBE]:
                        chemin = y_aller_plus_court(le_plateau, coord, pos_mon_joueur)
                        if distance == 0 or len(chemin) < distance :
                            distance = len(chemin)
                            mouv = chemin[-1]
                            tire = meilleur_pos_a_peindre(le_plateau, pos_mon_joueur, mouvement_possible, ma_couleur, reserve)
                            print("le joueur"+ ma_couleur + " va à bombe ")
                else:
                    tire = 'X'
                    distance = 0
                    if len(liste_case) >= 1:
                        for coord in liste_case:
                            if coord != pos_mon_joueur:
                                chemin = y_aller_plus_court(le_plateau, coord, pos_mon_joueur)
                                if distance == 0 or len(chemin) < distance :
                                    distance = len(chemin)
                                    mouv = chemin[-1]        
    return tire + random.choice(mouv)

    

p2= "4;6\n#  b# \n  A## \n##A   \n  Aa##\n2\nA;0;1\nB;3;0\n1\n4;2;0"
p1 = "12;12\n##A #  ##BB#\n #A  #   B# \n #A ##  ####\n #A         \n #A  #  # C#\n##A#DDDD##C \n# A# #    C#\n##A    ###CC\n##   #  #CCC\n# #   #  ##C\n #   # #   C\n ###     ###\n4\nB;0;9\nA;2;2\nD;5;5\nC;7;10\n1\n4;6;10"
#print(info_objet(p1))
#print(calque(plateau.Plateau(p1),(3,2)))
#mon_IA('A', "duree_act;duree_tot;reserve_init;duree_obj;penalite;bonus_touche;bonus_rechar;bonus_objet", p2, "A;10;0;0;0;0;1;bidul\nB;10;1;0;0;1;1;truc")

#chercher_objet_plus_proche(p1, (3, 2))

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
            le_client.afficher_msg("sa reponse  envoyée "+str(id_joueur)+args.nom_equipe)
    le_client.afficher_msg("terminé")