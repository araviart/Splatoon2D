import pygame
import argparse
import os
import sys
import threading
import jeu
import client
import const

class JeuGraphique(object):
    """Classe simple d'affichage et d'interaction pour le labyrinthe."""

    def __init__(self, lecteur_jeu, nom_partie, titre="Splat'IUT'O", size=(3000, 1600),
                 couleur=(209, 238, 238),
                 prefixe_image="./images"):
        """Method docstring."""
        self.lecteur_jeu=lecteur_jeu
        self.jeu = lecteur_jeu.get_jeu()
        self.nom_partie = nom_partie
        self.sauve = False
        self.message_info = None
        self.img_info = []
        self.fini = False
        self.couleur_texte = couleur
        self.plateau=self.jeu.plateau
        self.nb_colonnes = self.plateau.meth2()
        self.nb_lignes = self.plateau.meth1()
        self.phase = 1
        self.titre = titre
        self.images_cartes = {}
        self.images_pions = {}
        self.images_objets = {}
        self.images_murs={}
        self.icone = None
        self.hauteur = 0
        self.largeur = 0
        self.deltah = 0
        self.deltal = 0
        self.finh = 0
        self.finl = 0
        self.taille_font = 0
        self.get_images(prefixe_image)
        pygame.init()
        pygame.display.set_icon(self.icone)
        pygame.display.set_mode(size, pygame.RESIZABLE | pygame.DOUBLEBUF)
        pygame.display.set_caption(titre)
        self.surface = pygame.display.get_surface()
        self.maj_parametres()
        self.affiche_jeu()

    def get_images(self, prefixe_image="./images"):
        codage="_abcdefghijklmnopqrstuvwxyz"
        for i in range(7):
            if os.path.isfile(os.path.join(prefixe_image, 'mur' + codage[i] + '.jpeg')):
                s = pygame.image.load(os.path.join(prefixe_image, 'mur' + codage[i] + '.jpeg'))
            else:
                s = None
            self.images_murs[codage[i]]=s
            if os.path.isfile(os.path.join(prefixe_image, 'peinture' + codage[i] + '.jpg')):
                s = pygame.image.load(os.path.join(prefixe_image, 'peinture' + codage[i] + '.jpg'))
            else:
                s = None
            self.images_cartes[codage[i]]=s
            if i>0:
                s = pygame.image.load(os.path.join(prefixe_image, 'pion'+codage[i]+'.png'))
            self.images_pions[codage[i]] = s
        # lecture des différents objets dans les fichiers de la forme objetxxx.png où xxx va de 0 à 3
        i = 1
        while os.path.isfile(os.path.join(prefixe_image, 'objet' + str(i) + '.png')):
            s = pygame.image.load(os.path.join(prefixe_image, 'objet' + str(i) + '.png'))
            self.images_objets[i] = s
            i += 1

        # lecture du logo de l'IUT'O
        icone_img = pygame.image.load(os.path.join(prefixe_image, 'logo.jpeg'))
        self.icone = pygame.transform.smoothscale(icone_img, (50, 50))

    def maj_parametres(self):
        """
        permet de mettre à jour les paramètre d'affichage en cas de redimensionnement de la fenêtre
        """
        self.surface = pygame.display.get_surface()
        self.hauteur = round(self.surface.get_height() * .9)
        self.largeur = self.hauteur
        self.deltah = self.hauteur // (self.nb_lignes + 2)
        self.deltal = self.largeur // (self.nb_colonnes + 2)
        self.finh = self.deltah * (self.nb_lignes + 2)
        self.finl = self.deltal * (self.nb_colonnes + 2)
        self.taille_font = min(self.deltah, self.deltal) * 1 // 2

    def surface_carte(self, carte):
        """
        transforme une carte en une surface (image 2D) avec les pions et trésor associés
        """
        couleur = carte.meth2().lower()
        if couleur==" ":
            couleur='_'
        if carte.meth1():
            surf_carte=pygame.transform.smoothscale(self.images_murs[couleur], (self.deltal, self.deltah))
            return surf_carte
        objet = carte.meth3()
        pions = carte.meth4()
        img = self.images_cartes[couleur]
        if img is None:
            return None

        surf_carte = pygame.transform.smoothscale(img, (self.deltal, self.deltah))
        dist = 5
        coord = [(dist, dist), (dist, self.deltah - (self.deltah // 2 +dist)),
                 (self.deltal - (self.deltal // 2 +dist), self.deltah - (self.deltah // 2 +dist)),
                 (self.deltal - (self.deltal // 2 +dist), dist), (self.deltal//4+dist,dist),
                 (self.deltal//4+dist,self.deltah - (self.deltah // 2 +dist))]
        for pion in pions:
            surf_pion = pygame.transform.smoothscale(
                self.surface_pion(pion, True),
                (self.deltal // 2, self.deltah // 2))
            surf_carte.blit(surf_pion, coord.pop(0))
        if objet != const.AUCUN:
            surf_objet = pygame.transform.smoothscale(self.images_objets[objet],
                                                      (self.deltal // 4, self.deltah // 4))
            surf_carte.blit(surf_objet, (self.deltah // 4 + dist, self.deltah // 4 + dist))
        return surf_carte

    
    def surface_pion(self, couleur, affiche_objet=False):
        """
        transforme un numéro de pion en son image
        """
        res = pygame.Surface((self.deltal, self.deltah), pygame.SRCALPHA)
        objet=self.jeu.les_joueurs[couleur].meth5()
        surf_pion = pygame.transform.smoothscale(self.images_pions[couleur.lower()], (self.deltal // 2, self.deltah // 2))
        res.blit(surf_pion, (self.deltal // 2, self.deltah // 2))
        if affiche_objet and objet != 0:
            surf_objet = pygame.transform.smoothscale(self.images_objets[objet],
                                                      (self.deltal // 4, self.deltah // 4))
            res.blit(surf_objet, (self.deltal // 4, self.deltah // 4))
        return res

    def surface_objet(self, objet):
        """
        produit l'image de l'objet dont le numéro est passé en paramètre
        """
        res = pygame.Surface((self.deltal, self.deltah))
        surf_objet = pygame.transform.smoothscale(self.images_objets[objet], (self.deltal // 2, self.deltah // 2))
        res.blit(surf_objet, (self.deltal // 4, self.deltah // 4))
        return res

    def affiche_message(self, ligne, texte, images=[], couleur=None):
        """
        affiche un message en mode graphique à l'écran
        """
        font = pygame.font.Font(None, self.taille_font)
        if couleur is None:
            couleur = self.couleur_texte
        posy = self.finh//2 # + self.taille_font * (ligne - 1)
        posx = self.finl + self.deltal 
        liste_textes = texte.split('@img@')
        for msg in liste_textes:
            if msg != '':
                texte = font.render(msg, True, couleur)
                textpos = texte.get_rect()
                textpos.y = posy
                textpos.x = posx
                self.surface.blit(texte, textpos)
                posx += textpos.width
            if images != []:
                surface = pygame.transform.smoothscale(images.pop(0),
                                                       (round(self.taille_font * 1.5), round(self.taille_font * 1.5)))
                debuty = posy - (self.taille_font // 2)
                self.surface.blit(surface, (posx, debuty))
                posx += surface.get_width()

    def affiche_joueurs(self, couleur=None):
        font = pygame.font.Font(None, self.taille_font)
        if couleur is None:
            couleur = self.couleur_texte
        posx = self.finl + self.deltal // 3
        posy = self.deltah
        classement = self.jeu.classement()
        for joueur in classement:
            nom = joueur.meth2()
            surface = joueur.meth4()
            points = joueur.meth3()
            contenu = "{} s({}) r({})"
            surfp = self.surface_pion(joueur.meth1())
            objet = joueur.meth5()
            if objet != 0:
                surfo = self.surface_objet(objet)
            else:
                surfo = pygame.Surface((self.deltal // 4, self.deltal // 4))
            self.surface.blit(surfp, (posx, posy - self.deltah // 3))
            texte = font.render(
                contenu.format(nom[:24].ljust(30), surface, points), True,
                couleur)
            textpos = texte.get_rect()
            textpos.y = posy
            textpos.x = posx + surfp.get_width()
            self.surface.blit(texte, textpos)
            textpos.x += texte.get_width()
            textpos.y = posy - self.deltah // 3
            self.surface.blit(surfo, textpos)
            posy += texte.get_height() * 2

    def affiche_message_info(self, num_ligne=4):
        """
        affiche un message d'information aux joueurs
        """
        if self.message_info is not None:
            self.affiche_message(num_ligne, self.message_info, self.img_info)
        self.img_info = []
        pygame.display.flip()

    def affiche_grille(self):
        """
        affiche le labyrinthe
        """
        self.surface.fill((0, 0, 0))
        font = pygame.font.Font(None, self.taille_font)
        for i in range(self.nb_lignes):
            for j in range(self.nb_colonnes):
                try:
                    carte = self.jeu.plateau.meth3((i, j))
                    s = self.surface_carte(carte)
                    if s is None:
                        self.surface.fill((0, 0, 0),
                                          ((j + 1) * self.deltal, (i + 1) * self.deltah, self.deltal, self.deltah))
                    else:
                        self.surface.blit(s, ((j + 1) * self.deltal, (i + 1) * self.deltah))
                except Exception as ex:
                    print(ex, i, j)
                    pass

    def affiche_jeu(self):
        """
        affiche l'ensemble du jeu du labyrinthe
        """
        self.affiche_grille()
        if self.jeu.est_fini():
            self.affiche_message(1, "La partie est terminée")
        nb_tours = self.jeu.get_duree_restante()
        pluriel = "s"
        if nb_tours <= 1:
            pluriel = ""
        self.affiche_message(2, "il reste " + str(nb_tours) + " tour" + pluriel + " de jeu", [])
        self.affiche_joueurs()
        self.affiche_message_info()
        pygame.display.flip()

    def demarrer(self):
        """
        démarre l'environnement graphique et la boucle d'écoute des événements
        """
        pygame.time.set_timer(pygame.USEREVENT + 1, 100)
        en_cours = False
        sauver = False
        clock = pygame.time.Clock()
        while (True):
            ev = pygame.event.wait()
            if ev.type == pygame.QUIT:
                break
            # if ev.type == pygame.KEYDOWN:
            #     en_cours = True
            # if not en_cours:
            #     continue
            if ev.type == pygame.USEREVENT + 1:
                le_jeu=self.lecteur_jeu.get_jeu()
                if le_jeu is not None:
                    self.jeu=le_jeu
                
                self.affiche_jeu()
            if ev.type == pygame.VIDEORESIZE:
                fenetre = pygame.display.set_mode(ev.size, pygame.RESIZABLE | pygame.DOUBLEBUF)
                self.maj_parametres()
                self.affiche_jeu()
                self.affiche_jeu()
        pygame.quit()


class LecteurThread(threading.Thread):
    def __init__(self,serveur="",port=1111):
        super().__init__()
        self.client=client.ClientCyber()
        self.client.creer_socket(serveur,port)
        self.client.enregistrement("affichage principal","afficheur")
        self.ok=True
        self.verrou=threading.Lock()
        ok,_,le_jeu=self.client.prochaine_commande()
        if not ok:
            sys.exit(0)
        self.le_jeu=jeu.Jeu()
        self.le_jeu.jeu_from_str(le_jeu)
        self.change=True

    def get_jeu(self):
        self.verrou.acquire()
        res=None
        if self.change:
            res=self.le_jeu
            self.change=False
        self.verrou.release()
        return res

    def lire_jeu(self):
        ok,_,le_jeu=self.client.prochaine_commande()
        if not ok:
            self.ok=ok
            return
        self.verrou.acquire()    
        self.le_jeu==jeu.Jeu()
        self.le_jeu.jeu_from_str(le_jeu)
        self.change=True
        self.verrou.release()
    
    def arreter(self):
        self.ok=False

    def run(self):
        while self.ok:
            self.lire_jeu()



if __name__ == '__main__':
    parser = argparse.ArgumentParser()  
    parser.add_argument("--nom_partie", dest="nom_partie", help="nom de la partie", type=str, default='Non fournie')
    parser.add_argument("--serveur", dest="serveur", help="serveur de jeu", type=str, default='localhost')
    parser.add_argument("--port", dest="port", help="port de connexion", type=int, default=1111)
    args = parser.parse_args()
    print("Bienvenue dans le jeu du Splat'IUT'O")
    id_joueur=1
    lecteur=LecteurThread(args.serveur,args.port)
    lecteur.start()
    jg=JeuGraphique(lecteur,[],args.nom_partie)
    jg.demarrer()
    lecteur.arreter()
 



