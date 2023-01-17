"""module de gestion du plateau de jeu
"""
import const
import case


# dictionnaire permettant d'associer une direction et la position relative
# de la case qui se trouve dans cette direction
INC_DIRECTION = {'N': (-1, 0), 'E': (0, 1), 'S': (1, 0),
                 'O': (0, -1), 'X': (0, 0)}

# plateau = { (0, 0) : ' ', (0,1) : ' ', (0, 2) : ' '}

def get_nb_lignes(plateau):
    """retourne le nombre de lignes du plateau

    Args:
        plateau (dict): le plateau considéré

    Returns:
        int: le nombre de lignes du plateau
    """
    def ligne(tuple):
        return tuple[0]
    return max(plateau, key=ligne)[0]+1

def get_nb_colonnes(plateau):
    """retourne le nombre de colonnes du plateau

    Args:
        plateau (dict): le plateau considéré

    Returns:
        int: le nombre de colonnes du plateau
    """
    def colonne(tuple):
        return tuple[1]
    return max(plateau, key=colonne)[1]+1


def get_case(plateau, pos):
    """retourne la case qui se trouve à la position pos du plateau

    Args:
        plateau (dict): le plateau considéré
        pos (tuple): une paire (lig,col) de deux int

    Returns:
        dict: La case qui se situe à la position pos du plateau
    """
    return plateau[pos]

def poser_joueur(plateau, joueur, pos):
    """pose un joueur en position pos sur le plateau

    Args:
        plateau (dict): le plateau considéré
        joueur (str): la lettre représentant le joueur
        pos (tuple): une paire (lig,col) de deux int
    """
    plateau[pos] = case.Case(joueurs_presents=joueur)

def poser_objet(plateau, objet, pos):
    """Pose un objet en position pos sur le plateau. Si cette case contenait déjà
        un objet ce dernier disparait

    Args:
        plateau (dict): le plateau considéré
        objet (int): un entier représentant l'objet. const.AUCUN indique aucun objet
        pos (tuple): une paire (lig,col) de deux int
    """
    plateau[pos] = objet

def plateau_from_str(la_chaine):
    """Construit un plateau à partir d'une chaine de caractère contenant les informations
        sur le contenu du plateau (voir sujet)

    Args:
        la_chaine (str): la chaine de caractères décrivant le plateau

    Returns:
        dict: le plateau correspondant à la chaine. None si l'opération a échoué
    """
    plateau = dict()
    la_chaine = la_chaine.split("\n")
    x = -1
    y = -1
    la_chaine = la_chaine[1::] # on omet la première ligne qui n'est pas matrice
    for ligne in la_chaine:
        y += 1
        x = 0
        for terme in ligne:
            if terme == " ":
                plateau[x, y] = case.Case()
            else: 
                plateau[x, y] = case.Case(True)
            x += 1
    return plateau


#le nombre de ligne est ici = y, et colonne = x 
def Plateau(plan):
    """Créer un plateau en respectant le plan donné en paramètre.
        Le plan est une chaine de caractères contenant
            '#' (mur)
            ' ' (couloir non peint)
            une lettre majuscule (un couloir peint par le joueur représenté par la lettre)

    Args:
        plan (str): le plan sous la forme d'une chaine de caractères

    Returns:
        dict: Le plateau correspondant au plan
    """
    les_lignes=plan.split("\n")
    [nb_lignes,nb_colonnes]=les_lignes[0].split(";")

    plateau = dict()
    lignes = plan.split("\n")
    lignes.pop(0)
    l, c = 0, 0
    for ligne in lignes:
        if l < int(nb_lignes):
            for lettre in ligne:
                if lettre == "#":
                    plateau[(l, c)] = case.Case(True)
                elif lettre == " ":
                    plateau[(l, c)] = case.Case(False, " ", joueurs_presents=set())
                elif lettre in "abcdefg":
                    plateau[(l, c)] = case.Case(True, lettre)
                elif lettre in "ABCDEFG":
                    plateau[(l, c)] = case.Case(False, lettre, joueurs_presents=set())
                c += 1
            l += 1
            c = 0
    joueurs = lignes[l:]
    for elem in joueurs:
        if len(elem) > 2:
            p = elem.split(";")
            l = int(p[1])
            c = int(p[2])
            case_pl = get_case(plateau, (l, c))
            if p[0].isalpha():
                case.poser_joueur(case_pl, p[0])
            else:
                case.poser_objet(case_pl, int(p[0]))

    return plateau

#print(Plateau(open("plans/plan1.txt").read()))
    


def set_case(plateau, pos, une_case):
    """remplace la case qui se trouve en position pos du plateau par une_case

    Args:
        plateau (dict): le plateau considéré
        pos (tuple): une paire (lig,col) de deux int
        une_case (dict): la nouvelle case
    """
    plateau[pos] = une_case

def enlever_joueur(plateau, joueur, pos):
    """enlève un joueur qui se trouve en position pos sur le plateau

    Args:
        plateau (dict): le plateau considéré
        joueur (str): la lettre représentant le joueur
        pos (tuple): une paire (lig,col) de deux int

    Returns:
        bool: True si l'opération s'est bien déroulée, False sinon
    """
    #return plateau[pos]["joueurs_presents"].remove(pos)
    if joueur in case.get_joueurs(plateau[pos]):
        case.get_joueurs(plateau[pos]).remove(joueur)
        return True
    else:
        return False

def prendre_objet(plateau, pos):
    """Prend l'objet qui se trouve en position pos du plateau et retourne l'entier
        représentant cet objet. const.AUCUN indique qu'aucun objet se trouve sur case

    Args:
        plateau (dict): Le plateau considéré
        pos (tuple): une paire (lig,col) de deux int

    Returns:
        int: l'entier représentant l'objet qui se trouvait sur la case.
        const.AUCUN indique aucun objet
    """
    res = case.get_objet(plateau[pos])
    if case.get_objet(plateau[pos]) != const.AUCUN:
        plateau[pos]["objet"] = 0
    return res

def deplacer_joueur(plateau, joueur, pos, direction):
    """Déplace dans la direction indiquée un joueur se trouvant en position pos
        sur le plateau

    Args:
        plateau (dict): Le plateau considéré
        joueur (str): La lettre identifiant le joueur à déplacer
        pos (tuple): une paire (lig,col) d'int
        direction (str): une lettre parmie NSEO indiquant la direction du déplacement

    Returns:
        tuple: un tuple contenant 4 informations
            - un bool indiquant si le déplacement a pu se faire ou non
            - un int valeur une des 3 valeurs suivantes:
                *  1 la case d'arrivée est de la couleur du joueur
                *  0 la case d'arrivée n'est pas peinte
                * -1 la case d'arrivée est d'une couleur autre que celle du joueur
            - un int indiquant si un objet se trouvait sur la case d'arrivée (dans ce
                cas l'objet est pris de la case d'arrivée)
            - une paire (lig,col) indiquant la position d'arrivée du joueur (None si
                le joueur n'a pas pu se déplacer)
    """
    # déplacement 
    new_direc = None
    if direction == "N":
        new_direc = pos[0]+INC_DIRECTION['N'][0], pos[1]+INC_DIRECTION['N'][0]
    elif direction == 'E':
        if direction == "N":
        new_direc = pos[0]+INC_DIRECTION['E'][0], pos[1]+INC_DIRECTION['E'][0]

    


#-----------------------------
# fonctions d'observation du plateau
#-----------------------------

def surfaces_peintes(plateau, nb_joueurs):
    """retourne un dictionnaire indiquant le nombre de cases peintes pour chaque joueur.

    Args:
        plateau (dict): le plateau considéré
        nb_joueurs (int): le nombre de joueurs total participant à la partie

    Returns:
        dict: un dictionnaire dont les clées sont les identifiants joueurs et les
            valeurs le nombre de cases peintes par le joueur
    """
    joueurs = dict()

    for pos, valeur in plateau.items():
        couleur = case.get_couleur(valeur)
        if couleur in joueurs.keys():
            joueurs[couleur] +=1
        else:
            joueurs[couleur] = 1

    return joueurs

    
def directions_possibles(plateau,pos):
    """ retourne les directions vers où il est possible de se déplacer à partir
        de la position pos

    Args:
        plateau (dict): le plateau considéré
        pos (tuple): un couple d'entiers (ligne,colonne) indiquant la position de départ
    
    Returns:
        dict: un dictionnaire dont les clés sont les directions possibles et les valeurs la couleur
              de la case d'arrivée si on prend cette direction
              à partir de pos
    """
    liste = dict()
    for direction, pos2 in INC_DIRECTION.items():
        new_pos = (pos2[0] + pos[0], pos2[1] + pos[1])
        new_case = get_case(plateau, new_pos)
        if case.est_mur(new_case) is False:
            liste[direction] = case.get_couleur(new_case)
    return liste

    
def nb_joueurs_direction(plateau, pos, direction, distance_max):
    """indique combien de joueurs se trouve à portée sans protection de mur.
        Attention! il faut compter les joueurs qui sont sur la case pos

    Args:
        plateau (dict): le plateau considéré
        pos (_type_): la position à partir de laquelle on fait le recherche
        direction (str): un caractère 'N','O','S','E' indiquant dans quelle direction on regarde
    Returns:
        int: le nombre de joueurs à portée de peinture (ou qui risque de nous peindre)
    """
    nb = 0
    for direction, pos2 in INC_DIRECTION.items():
        new_pos = (pos2[0] + pos[0], pos2[1] + pos[1])
        new_case = get_case(plateau, new_pos)
        if case.est_mur(new_case) is False:
            for joueur in case.get_joueurs(new_case):
                nb +=1
    return nb

    
def peindre(plateau, pos, direction, couleur, reserve, distance_max, peindre_murs=False):
    """ Peint avec la couleur les cases du plateau à partir de la position pos dans
        la direction indiquée en s'arrêtant au premier mur ou au bord du plateau ou
        lorsque que la distance maximum a été atteinte.

    Args:
        plateau (dict): le plateau considéré
        pos (tuple): une paire (lig,col) de int
        direction (str): un des caractères 'N','S','E','O' indiquant la direction de peinture
        couleur (str): une lettre indiquant l'idenfiant du joueur qui peint (couleur de la peinture)
        reserve (int): un entier indiquant la taille de la reserve de peinture du joueur
        distance_max (int): un entier indiquant la portée maximale du pistolet à peinture
        peindre_mur (bool): un booléen indiquant si on peint aussi les murs ou non

    Returns:
        dict: un dictionnaire avec 4 clés
                "cout": un entier indiquant le cout en unités de peinture de l'action
                "nb_repeintes": un entier indiquant le nombre de cases qui ont changé de couleur
                "nb_murs_repeints": un entier indiquant le nombre de murs qui ont changé de couleur
                "joueurs_touches": un ensemble (set) indiquant les joueurs touchés lors de l'action
    """
    cout = 0
    nb_repeintes = 0
    nb_murs_repeints = 0
    joueurs_touches = set
        
    positions = [pos]
    d = INC_DIRECTION[direction]
    for i in range(distance_max):
        p = positions[-1]
        new_pos = (p[0] + d[0], p[1] + d[1])
        positions.append(new_pos)
    
    for pos in positions:
        case_pl = get_case(plateau, pos)

        stop = True
        if 0 <= case_pl[0] < get_nb_lignes(plateau):
            if 0 <= case_pl[1] < get_nb_colonnes(plateau):
                if case.est_mur(case_pl) is False:

                    stop = False

                    if couleur == case.get_couleur(case_pl):
                        cout +=1 
                    else:
                        cout += 2

                    nb_repeintes += 1

                    for joueur in case.get_joueurs(case_pl):
                        joueurs_touches.add(joueur)

                else:
                    stop = True
                    nb_murs_repeints += 1
        if stop:
            return {
                "cout": cout,
                "nb_repeintes": nb_repeintes, 
                "nb_murs_repeints": nb_murs_repeints,
                "joueurs_touches": joueurs_touches
            }
    return {
        "cout": cout,
        "nb_repeintes": nb_repeintes, 
        "nb_murs_repeints": nb_murs_repeints,
        "joueurs_touches": joueurs_touches
    }

