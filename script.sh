xterm -e 'python3 serveur.py' &
sleep 0.5s
xterm -e 'python3 affichage.py' &
sleep 0.5s
xterm -e 'python3 client_joueur.py --equipe joueur1'&
xterm -e 'python3 client_joueur.py --equipe joueur2'&
