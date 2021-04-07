import math, time, bisect
from tkinter import Tk, Canvas

# TRAITEMENT DU FICHIER NOEUDS.CSV
fichier_noeuds = 'Noeuds.csv'

# PRAMETRES DEPENDANT DU FICHIER EN ENTREE

LesNoeuds = open(fichier_noeuds, "r")
# format du fichier : numero du noeud \t longitude \t latitude \n
tousLesNoeuds = LesNoeuds.readlines()
LesNoeuds.close()

# On initialise les listes a vide
Longitude = []
Latitude = []

minLong = 1
maxLong = 0
minLat = 1
maxLat = 0

for un_noeud in tousLesNoeuds:
    un_noeud.strip("\n")
    ce_noeud = un_noeud.split('\t')

    # On converti ces valeurs en float
    long = float(ce_noeud[1]) * (math.pi / 180)
    lat = float(ce_noeud[2]) * (math.pi / 180)

    Longitude.append(long)
    Latitude.append(lat)

    if (minLat > lat): minLat = lat
    if (maxLat < lat): maxLat = lat
    if (minLong > long): minLong = long
    if (maxLong < long): maxLong = long

# TRAITEMENT DU FICHIER ARC.CSV
fichier_arc = 'Arcs.csv'

# PRAMETRES DEPENDANT DU FICHIER EN ENTREE

LesArcs = open(fichier_arc, "r")
# format du fichier : origine \t destination \t longueur \t dangerosite \n
tousLesArcs = LesArcs.readlines()
LesArcs.close()

Origine = []
Destination = []
Longueur = []
Dangerosite = []

for un_arc in tousLesArcs:
    un_arc.strip('\n')
    cet_arc = un_arc.split("\t")

    Orig = int(cet_arc[0])
    Origine.append(Orig)

    Dest = int(cet_arc[1])
    Destination.append(Dest)

    Long = int(cet_arc[2])
    Longueur.append(Long)

    Dang = int(cet_arc[3].strip('\n'))
    Dangerosite.append(Dang)

# NbSommets = max(max(Origine), max(Destination)) + 1
NbSommets = len(tousLesNoeuds)
Succ = [[] for j in range(NbSommets)]

for u in range(0, len(Origine)):
    orig = Origine[u]
    dest = Destination[u]
    Succ[orig].append(dest)

# ########################################################
# Dessin du graphe
# ########################################################

print('*****************************************')
print('* Dessin du graphe                      *')
print('*****************************************')


def cercle(x, y, r, couleur):
    can.create_oval(x - r, y - r, x + r, y + r, outline=couleur, fill=couleur)


def TraceCercle(j, couleur, rayon):
    x = (Longitude[j] - minLong) * ratioWidth + border
    y = ((Latitude[j] - minLat) * ratioHeight) + border
    y = winHeight - y
    cercle(x, y, rayon, couleur)


def TraceSegment(i, j, color):
    # Coordonnees de i
    x1 = (Longitude[i] - minLong) * ratioWidth + border
    y1 = ((Latitude[i] - minLat) * ratioHeight) + border
    y1 = winHeight - y1

    # Coordonnees de j
    x2 = (Longitude[j] - minLong) * ratioWidth + border
    y2 = ((Latitude[j] - minLat) * ratioHeight) + border
    y2 = winHeight - y2

    can.create_line(x1, y1, x2, y2, fill=color)


fen = Tk()
fen.title('Graphe')
coul = "dark green"  # ['purple','cyan','maroon','green','red','blue','orange','yellow']

Delta_Long = maxLong - minLong
Delta_Lat = maxLat - minLat
border = 20  # taille en px des bords
winWidth_int = 800
winWidth = winWidth_int + 2 * border  # largeur de la fenetre
winHeight_int = 800
winHeight = winHeight_int + 2 * border  # hauteur de la fenetre : recalculee en fonction de la taille du graphe
# ratio= 1.0          # rapport taille graphe / taille fenetre
ratioWidth = winWidth_int / (maxLong - minLong)  # rapport largeur graphe/ largeur de la fenetre
ratioHeight = winHeight_int / (maxLat - minLat)  # rapport hauteur du graphe hauteur de la fenetre

can = Canvas(fen, width=winWidth, height=winHeight, bg='dark grey')
can.pack(padx=5, pady=5)

#  cercles
rayon = 1  # rayon pour dessin des sommets
rayon_od = 5  # rayon pour sommet origine et destination
# Affichage de tous les sommets
for i in range(0, NbSommets):
    TraceCercle(i, 'black', rayon)

# On trace tous les arcs de la ville en noir
for i in range(NbSommets):
    for succ in Succ[i]:
        TraceSegment(i, succ, "black")


def Distance_vol_oiseau(villeA):
    # Calcule la distance de la ville A a la destination
    xA = Longitude[villeA]
    xB = Longitude[sommet_destination]
    yA = Latitude[villeA]
    yB = Latitude[sommet_destination]
    R = 6372795.477598

    AB = R * math.acos(math.sin(yA) * math.sin(yB) + math.cos(yA) * math.cos(yB) * math.cos(xA - xB))
    return (AB)


Long_Arc_Succ = [[] for sommet in range(NbSommets)]
for so in range(len(Origine)):
    Long_Arc_Succ[Origine[so]].append(Longueur[so])

INFINITY = 999999


def a_star(epsilon, N):
    Pi = [INFINITY for j in range(NbSommets)]
    LePrec = [-1 for j in range(NbSommets)]
    Marque = [-1 for j in range(NbSommets)]
    Candidats = []
    PiLB_Trie = []
    Pi[sommet_depart] = 0
    Marque[sommet_depart] = 1
    nb_sommets_explores = 0
    # Weighted-A*
    # w sert a ponderer la distance a vol d'oiseau
    # On aura mtn pour chaque sommet candidat une distance au sommet_dest qui
    # peut etre 'mal estimee'
    # f(j) = g(j) + w * h(j)
    w = (1 + epsilon * (1 - (nb_sommets_explores) / N))

    for k in Succ[sommet_depart]:
        ind_k = Succ[sommet_depart].index(k)
        Pi[k] = Long_Arc_Succ[sommet_depart][ind_k]
        LePrec[k] = sommet_depart
        # On calcul le potentiel de k + Distance_vol_oiseau entre k et sommet_destination
        w = (1 + epsilon * (1 - (nb_sommets_explores) / N))
        PiLB = Pi[k] + w * Distance_vol_oiseau(k)
        # point_d_insertion = bisect.bisect_left(PiLB_Trie, PiLB)
        # Pi.insert(point_d_insertion,PiLB)
        # print(PiLB, point_d_insertion)
        bisect.insort_left(PiLB_Trie, PiLB)
        Candidats.insert(PiLB_Trie.index(PiLB), k)

    fini = False

    while not fini:
        # On prend le 1e candidat
        # print("Candidats : ", Candidats)
        j = Candidats.pop(0)
        # On le marque, le trace en jaune, le retire des candidats
        Marque[j] = 1
        TraceCercle(j, 'yellow', 1)
        # et retire son potentie de la liste PiLB_Trie
        nb_sommets_explores += 1
        # print(nb_sommets_explores, j)
        PiLB_Trie.pop(0)
        # Si j == sommet_dest alors c'est fini
        if j == sommet_destination:
            fini = True
        else:
            # print('j = ', j , Succ[j])
            # Pour chaque k parmis les successeurs de j
            for k in Succ[j]:
                # S'il n'est pas marque
                if Marque[k] == -1:
                    # On calcul son nouveau potentiel
                    Pi_k = Pi[j] + Long_Arc_Succ[j][Succ[j].index(k)]
                    # Si ce potentiel est inferieur a l'ancien
                    if Pi_k < Pi[k]:
                        # On cherche k dans Candidats, on le retire lui et son potentiel dans PiLB_Trie
                        if k in Candidats:
                            ind_k = Candidats.index(k)
                            Candidats.remove(k)
                            PiLB_Trie.pop(ind_k)
                        # On met a jour son potentiel et son pere
                        Pi[k] = Pi_k
                        LePrec[k] = j
                        # On calcule la borne inf PiLB du sommet k
                        w = (1 + epsilon * (1 - (nb_sommets_explores) / N))
                        PiLB = Pi[k] + w * Distance_vol_oiseau(k)
                        # On l'insert a sa place dans PiLB_Trie
                        bisect.insort_left(PiLB_Trie, PiLB)
                        # Et on insert k dans Candidats a la meme place
                        Candidats.insert(PiLB_Trie.index(PiLB), k)
                        # print("Candidats, PiLB_Trie.index(PiLB)")

    s = sommet_destination
    # On part du sommet_destination
    while LePrec[s] != -1:
        # On trace un segment entre le sommet et son pere
        # le sommet devient son pere et on repete cette operation tant que le sommet a un pere
        TraceSegment(s, LePrec[s], 'red')
        s = LePrec[s]
    # On retourne la longueur du chemin
    return Pi[sommet_destination], nb_sommets_explores


sommet_depart = 10436

# sommet_destination = 11342
# Environs 8s pour la V1 et 0.8s pour la v2

# sommet_destination = 22279
# Environs 65s pour la v2
# Environs 1.6s pour la V2

# Weighted-A*
sommet_destination = 22336
epsilon = 0.5
n = 10000

time_start = time.process_time()
TraceCercle(sommet_depart, 'green', rayon_od)

TraceCercle(sommet_destination, 'red', rayon_od)

longueur, nb_sommets_explores = a_star(epsilon, n)
time_end = time.process_time()
print('La duree du processus est de : ', time_end - time_start)
print('La longueur du chemin parcouru est de : ', longueur)
print('Le nombre de sommets explorés : ', nb_sommets_explores)
print('weighted-A* avec w : ', 1 + epsilon)
fen.mainloop()
