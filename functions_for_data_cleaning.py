
""" 
Functions for data cleaning 
Document python contenant les fonctions nécessaires pour le nettoyage des données du dataframe. Elles seront ensuite importées dans le notebook final. Il y a quatre parties (correspondant aux 4 parties du nettoyage): 
- get_loyer : pour récupérer le loyer des résidences;
- get_surface : idem pour les surfaces;
- get_localisation : permet de récupérer les coordonnées de la résidence sous la forme adéquate pour un GéoDataFrame;
- get_nb_student :permet de récupérer le nombre d'étudiants des écoles aux alentour de x km des résidences. 

"""  


import pandas as pd
import nltk
nltk.download('punkt')
import numpy as np
import geopandas as gpd
from shapely import wkt 


"""
Part I. Get_Loyer 
"""

"""
I.A. String_checking
String_checking est une fonction qui prend un mot en argument et un élément et retourne 0 si l'élément n'est 
pas inclus dans le mot et 1 inversement. 
"""


def string_checking(string, check):
    result = 0 
    if string.find(check) == -1:
        result = 0
    else: 
        result = 1
    return result


"""
I.B. word_ban
Cette fonction prend en argument un mot à tester et une liste. Elle va utiliser la fonction précédente pour
vérifier qu'il n'y a aucun élèment de la liste dans notre mot. De même elle retourne 0 ou 1 en fonction de
s'il y a un élément ou non. 
"""


def word_ban(string, liste):
    result = 0 
    for check in liste:
        if string_checking(string, check) == 1:
            result = result + 1  
    return result 

"""
I.C. rent
On va créer une fonction pour trouver le loyer à partir de la fonction précédente. La fonction prend pour argument un texte (ici df['infos'][j] qui correspond au texte informatif d'une résidence où se trouve le loyer. La fonction va nettoyer le texte d'une manière très précise : 

1 - On va enlever tous les espaces du texte de façon à n'avoir qu'un block uniforme de texte. 
2 - on va enlever les parenthèses.  
3 - On va enlever les petits 2 des mètres carrés qui posent souvent problème dans la suite du code. 
4 - On va remplacer les à en € de façon à avoir les loyers qui sont inscrits de la manière suivante : 200 à 350€ (notre recherche se fonde grâce au €). 
5 - On va remplacer les 'euros' en €
6 - on va remplacer les €€ en € car il peut y avoir des '200€à350€' qui deviennent '200€€350€'et nous on veut '200€350€'. 
7 - On va rajouter un espace après chaque '€'. 
8 - On normalise les , en . pour avoir les mêmes typologies
9 - on va enlever les ":" . 

On va ensuite tokeniser notre block de texte grâce à la fonction word_tokenize du package nltk. On va ainsi passer de blocks de caractères séparés par un espace à une liste de mots. 

Exemple (df["infos"][0]): 

On passe de :

"Logements HLM

70 T1 : 325 euros
14 T1bis de 30m² : 373,50 euros
13 T2 de 37m² : 404 euros

   
   
   
 Photos de la résidence"
   
à : 

"['LogementsHLM', '70T1', '325€', '14T1bisde30m373.50€', '13T2de37m404€', 'Photosdelarésidence', 'https//www.flickr.com/photos/crousaixmarseilleavignon/albums/72157679829208245']"

L'idée va ensuite de trouver le loyer grâce à cette liste de mots. On va ainsi appliquer la fonction rent. cette fonction prend en argument cette liste de mots. Pour chaque éléments de notre liste on va d'abord chercher l'index de € (s'il existe et s'il n'appartient pas à la liste des mots interdits - on ne veut pas les montants des cautions par exemple). On va ensuite regarder si le caractère à la gauche du € est un chiffre ou non. Si c'est un chiffre on va réitérer cela pour le caractère à gauche de ce dernier. Ainsi de suite jusqu'à trouver un élèment qui n'est pas un chiffre. Dans ce cas là on va s'arrêter et prendre le nombre entre les deux indices. Le problème est celui des virgule : on rajoute une condition qui dit que si on trouve une virgule on regarde à gauche si c'est un chiffre. On obtient ainsi une liste des loyers avec quelques valeurs abberrantes que l'on gérera après. 

"""
            
def rent(word, List_banned_word):
    Loyer = [] #On crée une liste qui stockera le loyer
    for i in range(0,len(word)): #on regarde dans chaque block de caractère 
        index = word[i].find("€") #on cherche l'index de l'euros normalement pour tout les loyers il y est 
        search = 0 #il nous servira à arrêter la boucle while 
        if word_ban(word[i],List_banned_word) == 0 and word[i].find("€") != -1: #On regarde si dans le block de mot il n'y a pas un mot banni comme APL pour éviter d'avoir le montant de ceux-ci, ce qui fausserait nos résultats. Et qu'il y a le signe euro dans le texte. 
            while search == 0: #Tant que notre variable de contrôle est égale à 0, on va chercher le loyer (ie : tant que ce sont des chiffres, on va chercher la nature (chiffre ou non) de ce qui se situe à gauche.
                search_index = word[i][index - 1] #On cherche l'index de ce qui se trouve à gauche de l'euros
                if search_index.isdigit() == True: #si le caractère est un chiffre. 
                    index = index - 1 #on remonte de 1 l'index pour voir si ce qui se trouve à gauche de notre chiffre est également un chiffre.
                elif  search_index == "." and word[i][index - 2].isdigit() == True and word[i][index - 3].isdigit() == True and word[i][index - 4].isdigit() == True : 
                    #Si c'est un . et si à gauche de celui-ci les trois caractères sont également des chiffres (exemple : "2.").
                    #on remonte de 3 et on arrête la boucle while (pour avoir le chiffre en entier et éviter d'avoir un nouveau point dans le cas de 1.305.30)
                    index = index - 4
                    search = 1
                else : 
                    search = 1 #quand ce n'est pas un chiffre, on arrête la boucle while. 
                    if index == -1: #Dans le cas où il n'y a rien devant le loyer (ex: le token ressemble à '200€')
                        index = index + 1
        if word[i][index : word[i].find("€")]!= '': #on regarde le fait que le token ne soit pas juste un '€'
            Loyer.append(float(word[i][index : word[i].find("€")])) #On ajoute au loyer le loyer trouvé
    return Loyer


"""
I.C.bis rent_find
voir au-dessus 
"""

def rent_find(residence, List_banned_word): 
    residence = residence.replace(' ', '')
    residence = residence.replace('²', '')
    residence = residence.replace('mà', '')
    residence = residence.replace('à', '€')
    residence = residence.replace('euros', '€')
    residence = residence.replace('€€', '€')
    residence = residence.replace('€', '€ ')
    residence = residence.replace(',', '.')
    word =  nltk.word_tokenize(residence, language='french') #on transforme notre scripts en block de mots. ceux qui nous intéressent ont un euros à la fin (mais il y en a qui ont un euros à la fin et qui ne nous intéresse pas
    return rent(word, List_banned_word)


"""
I.D remove
fonction servant à ne garder que les loyers et enlever les quelques erreurs du style 5.99 qui serait l'abonnement au wifi
"""
    
def remove(residence, a, b):
    L = []
    for i in residence:
        if i >= a and i < b:
            L.append(i)                        
    return L


"""
I.E get_loyer
Fonction qui prend le dataframe en argument et qui retourne le dataframe avec 4 nouvelles colonnes contenant les loyers (liste), le loyer maximum, minimum et moyen. 
On applique les fonctions rent_find et remove. 
"""


def get_loyer(df): 
    List_banned_word = ['APL', 'Apl', 'Caution', 'caution', 'apl', 'CAUTION', "Charge", "charge", "Charges", "charge", "Dépôtdegarantie","wifi", "wifirst","abonnement", "Logementssoumis", "machineàlaver"]
    df['Loyer'] = df["infos"].apply(lambda x: rent_find(x, List_banned_word) if str(x) != "nan" else None) #si la colonne infos est remplie alors on cherche les loyers. 
    df["Loyer"] =  df["Loyer"].apply(lambda x: remove(x, 100, 1000) if x != None else None) #s'il y a des loyers, on applique la fonction remove pour n'avoir que les loyers et pas les surfaces ou autres erreures. 
    df["Max Loyer"] = df["Loyer"].apply(lambda x : max(x) if x != None and x !=[]  else None) #on prend le maximum. 
    df['Min Loyer'] = df["Loyer"].apply(lambda x : min(x) if x != None and x !=[]  else None)
    df['Mean Loyer'] = df["Loyer"].apply(lambda x : np.mean(x) if x != None and x !=[]  else None)
    return df


"""
Part II : Get_surface
"""

"""
II.A. Surface 
Même idée que la fonction rent mais avec les surfaces 
"""
def surface(word):
    Surface = [] #On crée une liste qui stockera la surface
    #try:
    for i in range(0,len(word)): #on regarde dans chaque block de caractère 
        index = word[i].find("m²") #on cherche l'index du m² normalement pour toutes les surfaces il y est 
        search = 0 #il nous servira à arrêter la boucle while 
        if word[i].find("m²") != -1: 
            while search == 0: #Tant que notre variable de contrôle est égale à 0, on va chercher la surface (ie : tant que ce sont des chiffres, on va chercher la nature (chffre ou non) de ce qui se situe à gauche.
                search_index = word[i][index - 1] #On cherche l'index de ce qui se trouve à gauche du m²
                if search_index.isdigit() == True: #si le caractère est un chiffre. 
                    index = index - 1 #on remonte de 1 l'index pour voir si ce qui se trouve à gauche de notre chiffre est également un chiffre.
                elif search_index == "." and word[i][index - 2].isdigit() == True : #Si c'est un . et si à gauche de celui-ci c'est également un chiffre (exemple : "2.").
                    index = index - 1 #on remonte de 1
                else : 
                    search = 1 #quand ce n'est pas un chiffre, on arrête la boucle while. 
                    if index == -1: #Dans le cas où il n'y a rien devant le loyer (ex: le token ressemble à '27m^2')
                        index = index + 1
            if word[i][index : word[i].find("m²")]!= '' and word[i][index : word[i].find("m²")]!= '.': #on regarde le fait que le token ne soit pas juste un '€'
                Surface.append(float(word[i][index : word[i].find("m²")])) #On ajoute à la surface la surface trouvée
    return Surface

def surface_find(residence): 
    residence = residence.replace(' ', '')
    residence = residence = residence.replace('à', 'm²')
    residence = residence.replace('m²à', 'm² ')
    residence = residence.replace('m²', 'm² ')
    residence = residence.replace('m2', 'm²') #unificier les notations de m2
    residence = residence.replace('€€', '€')
    residence = residence.replace(',', '.')
    residence = residence.replace(':', '')
    word =  nltk.word_tokenize(residence, language='french') #on transforme notre scripts en block de mots. ceux qui nous intéressent ont un euros à la fin (mais il y en a qui ont un euros à la fin et qui ne nous intéresse pas
    return surface(word)

"""
II.B get_surface
"""


def get_surface(df): 
        df['Surface'] = df["infos"].apply(lambda x: surface_find(x) if str(x) != "nan" else None) #si la colonne infos est remplie alors on cherche les loyers. 
        df["Surface"] =  df["Surface"].apply(lambda x: remove(x, 7, 100) if x != None else None) #s'il y a des loyers, on applique la fonction remove pour n'avoir que les loyers et pas les surfaces ou autres erreures. 
        df["Max Surface"] = df["Surface"].apply(lambda x : max(x) if x != None and x !=[]  else None) #on prend le maximum. 
        df['Min Surface'] = df["Surface"].apply(lambda x : min(x) if x != None and x !=[]  else None)
        df['Mean Surface'] = df["Surface"].apply(lambda x : np.mean(x) if x != None and x !=[]  else None)
        return df


"""
Part III : get_localisation  
"""

def get_localisation(df): 
    Longitude = []
    Latitude = []
    for j in range(0,df.shape[0]):
        geocalisation = df["geocalisation"][j]
        geocalisation = geocalisation.replace(',', ' ')
        word =  nltk.word_tokenize(geocalisation, language='french')
        Latitude.append(float(word[0]))
        Longitude.append(float(word[1]))
    df['Longitude'] = Longitude
    df['Latitude'] = Latitude
    df = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude))
    return df

"""
Part IV : Get_nb_students
"""

"""
IV.A. Within_fun
Fonction qui a pour but de rajouter le nombre d'élèves de l'école si celle-ci est dans le rayon de x km autour de la résidence. 

Arguments:
Elle prend pour argument ecole_bool (bool pour booléen) qui  est soit égale à true si l'école est dans le rayon et false sinon. S est une liste stockant les noms des écoles qui sont dans ce rayon pour la résidence. idem pour N mais pour le nombre d'élèves. 
index = l'index de ecole_bool.
var_1 = va correspondre à la colonne des noms des établissements.
var_2 = va correspondre à la colonne au nombre des élèves.

Retour: 
Elle retourne S le nom de l'école, N le nombre d'élèves et l'index augmenté de 1 pour après pouvoir réappliquer cette fonction à la prochaine école après. 
"""

def within_fun(ecole_bool,S,N, index, var_1, var_2):
    if ecole_bool == True: 
                S.append(var_1[index]) #on ajoute le nom de l'école de l'index 
                N.append(var_2[index]) #idem pour le nombre d'étudiants
    return S, N

"""
IV.B. Get_student
Fonction qui a pour but d'obtenir le nombre d'étudiants et les écoles dans un rayon de x km pour une résidence.
Elle prend en arguments la residence et le dataframe des écoles.

Elle applique la fonction précèdente pour toutes les écoles. On stocke les noms des écoles et le nombre d'élèves dans S et N que l'on retourne par la suite. 
"""

def get_student(residence, df_schools) : 
    S = [] #stocke les écoles pour la résidence
    N = [] #idem pour le nb d'étudiants 
    index = 0 #index 
    Bool = df_schools.within(residence) #On utilise gpd.within qui regarde pour chaque élèment si sa coordonnée est dans le polygone résidence (retourne un dataframe avec True si l'école est dans le rayon, false sinon). 
    for ecole_bool in Bool: #pour chaque école 
        within_fun(ecole_bool,S,N,index, df_schools['etablissement_lib'], df_schools['effectif_sans_cpge'])
        index = index + 1 #on augmente l'index de 1 pour appliquer la fonction à la prochaine école
    return S, N


"""
IV.C. Get_nb_student
Retourne le dataframe avec deux nouvelles colonnes avec le nom des écoles et le nombre des élèves dans un rayon de nb_km kilomètres. 

Arguments: 
df : le dataframe sur lequel appliquer la fonction.
df_schools : le dataframe des écoles 
nb_km : le rayon en km autour duquel on veut avoir les informations. 
"""

def get_nb_student(df, df_schools, nb_km):
    df1 = df
    df1 = df1.to_crs(epsg = 3395) #On prend une projection en mètres
    df1['geometry'] = df1['geometry'].buffer(nb_km*1000) #On prend un rayon de x km 
    df1 = df1.to_crs(4326) #on repasse dans la projection uselle 
    Schools = [] #on crée une liste pour stocker la liste des écoles 
    Nbstudents = [] #on crée une liste pour stocker la liste du nombre d'étudiants
    for residence in df1["geometry"]: #on prend pour chaque résidence le cercle de x km autour de cette résidence
        Schools.append(get_student(residence, df_schools)[0]) #on récupère pour cette résidence, les noms des écoles. 
        Nbstudents.append(get_student(residence, df_schools)[1]) #on récupère pour cette résidence, le nombre d'élèves.  
    df['Schools'] = Schools
    df['Nbstudents'] = Nbstudents
    df['Nbstudents'] = df['Nbstudents'].apply(lambda x : sum(x)) #on additionne le nombre d'élèves. 
    return df
