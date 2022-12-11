"""
function for data cleaning 
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
String_checking est une fonction qui prend un mot en argument et un élèment et retourne 0 si l'élèmenet n'est 
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
Cette fonction prend en argument un mot à tester et une liste. Elle va utiliser la fonction précédente pour
vérifier qu'il n'y a aucun élèment de la liste dans notre mot. De même elle retourne 0 ou 1 en fonction de
s'il y a un élèment ou non. 
"""


def word_ban(string, liste):
    result = 0 
    for check in liste: 
        if string_checking(string, check) == 1: 
            result = 1 
        else: 
            result = 0
    return result 
            
    
    
def rent(word, List_banned_word):
    Loyer = [] #On crée une liste qui stockera le loyer
    #try:
    for i in range(0,len(word)): #on regarde dans chaque block de caractère 
        index = word[i].find("€") #on cherche l'index de l'euros normalement pour tout les loyers il y est 
        search = 0 #il nous servira à arrêter la boucle while 
        if word_ban(word[i],List_banned_word) == 0 and word[i].find("€") != -1: 
        #On regarde si dans le block de mot il n'y a pas un mot banni comme APL pour éviter d'avoir le montant    de ceux-ci, ce qui fausserait nos résultats.
            while search == 0: #Tant que notre variable de contrôle est égale à 0, on va chercher le loyer (ie : tant que ce sont des chiffres, on va chercher la nature (chffre ou non) de ce qui se situe à gauche.
                search_index = word[i][index - 1] #On cherche l'index de ce qui se trouve à gauche de l'euros
                try: #Try permet de tester si c'est un chiffre tout en ne bloquant pas les opérations avec une erreur. 
                    search_index = int(search_index) #On regare si à gauche de l'ancien index c'est un entier ou non (Dans le cas contraire on sera dans except).
                    index = index - 1 #on remonte de 1 l'index pour voir si ce qui se trouve à gauche de notre chiffre est également un chiffre.
                except: #si ce n'est pas un entier à gauche de l'euros ou du dernier chiffre identifié. 
                    if word[i][index - 1] == ".": #on regarde si ce n'est pas un point comme dans 350.85 euros. Si on ne met pas cette ligne on aurait seulement 85 et non 350.85. 
                        index = index - 2 #On va regarde ce qui est avant le point pour trouver le reste du montant
                        search_index = word[i][index - 1] #Sysiphe remonte sa pierre et recommence le même processus qu'avant
                        try: #on regarde de nouveau si à gauche du point c'est un entier
                            search_index = int(search_index) 
                            index = index - 1 
                        except:
                            search = 1 #si ce n'est pas un chiffre ie une lettre on arrête
                            index = -1 #permet de ne pas avoir des erreurs du style .50
    
                    else: #si ce n'est pas un point on arrête le compte. 
                        search = 1
                #print(word[i][index : word[i].find("euros")])

            if word[i][index : word[i].find("€")]!= '': #on regarde le fait que le token ne soit pas juste un '€'
                Loyer.append(float(word[i][index : word[i].find("€")])) #On ajoute au loyer le loyer trouvé
    #except:
        #if word[i] != "€" :
            #List_banned_word.append(word[i])
            #print(List_banned_word)
            #rent(word)
    return Loyer

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
fonction servant à ne garder que les loyers et enlever les quelques erreures du style 5.99 qui serait l'abonnement au wifi
"""
    
def remove(residence, a, b):
    L = []
    for i in residence:
        if i >= a and i < b:
            L.append(i)                        
    return L   


def get_max_mean_min(var):
    Max = []
    Min = []
    Mean =[]
    for ele in var:
        if ele != None and ele != []:
            Max.append(max(ele))
            Min.append(min(ele))
            Mean.append(np.mean(ele))
        else: 
             Max.append(np.NaN)
             Min.append(np.NaN)
             Mean.append(np.NaN)
    return Max, Min, Mean


"""
On crée trois colonnes stockant le loyer maximum, le loyer minimum et la moyenne des loyers. 
"""


def get_loyer(df): 
    List_banned_word = ['APL', 'Apl', 'Caution', 'caution', 'apl', 'CAUTION', "Charge", "de", "charge", "Charges", "charge", "Dépôtdegarantie","wifi", "wifirst","abonnement", "Logementssoumis", "machineàlaver"]
    Loyer = []
    for j in range(0,df.shape[0]):
        try:
            Loyer.append(rent_find(df["infos"][j], List_banned_word))
        except: 
            Loyer.append(None)
    df['Loyer'] = Loyer
    
    for j in range(0,df.shape[0]):
        if df["Loyer"][j] != None : #s'il y a un Loyer
            df["Loyer"][j] = remove(df["Loyer"][j], 100, 1000)
    
    df['Max Loyer'] = get_max_mean_min(df["Loyer"])[0]
    df['Min Loyer'] = get_max_mean_min(df["Loyer"]) [1]
    df['Mean Loyer'] =  get_max_mean_min(df["Loyer"]) [2]
    return df 


"""
Part II : Get_loyer
"""


def surface (word):
    Surface = [] #On crée une liste qui stockera la surface
    #try:
    for i in range(0,len(word)): #on regarde dans chaque block de caractère 
        index = word[i].find("m²") #on cherche l'index du m² normalement pour toutes les surfaces il y est 
        search = 0 #il nous servira à arrêter la boucle while 
        if word[i].find("m²") != -1: 
            while search == 0: #Tant que notre variable de contrôle est égale à 0, on va chercher la surface (ie : tant que ce sont des chiffres, on va chercher la nature (chffre ou non) de ce qui se situe à gauche.
                search_index = word[i][index - 1] #On cherche l'index de ce qui se trouve à gauche du m²
                try: #Try permet de tester si c'est un chiffre tout en ne bloquant pas les opérations avec une erreur
                    search_index = int(search_index) #On regarde si à gauche de l'ancien index c'est un entier ou non (Dans le cas contraire on sera dans except).
                    index = index - 1 #on remonte de 1 l'index pour voir si ce qui se trouve à gauche de notre chiffre est également un chiffre.
                except: #si ce n'est pas un entier à gauche de l'euros ou du dernier chiffre identifié. 
                    if word[i][index - 1] == "." :
                        index = index - 2 #On va regarde ce qui est avant le point pour trouver le reste du montant
                        search_index = word[i][index - 1] #Sysiphe remonte sa pierre et recommence le même processus qu'avant
                        try: #on regarde de nouveau si à gauche du point c'est un entier
                            search_index = int(search_index) 
                            index = index - 1 
                        except:
                            search = 1 #si ce n'est pas un chiffre ie une lettre on arrête
                            index = -1 
    
                    else: #si ce n'est pas un point on arrête le compte. 
                        search = 1
                #print(word[i][index : word[i].find("euros")])

            if word[i][index : word[i].find("m²")]!= '': #on regarde le fait que le token ne soit pas juste un '€'
                Surface.append(float(word[i][index : word[i].find("m²")])) #On ajoute à la surface la surface trouvée
    #except:
        #if word[i] != "€" :
            #List_banned_word.append(word[i])
            #print(List_banned_word)
            #rent(word)
    return Surface


def surface_find(residence): 
    residence = residence.replace(' ', '')
    residence = residence.replace('m²à', 'm² ')
    residence = residence.replace('m²', 'm² ')
    residence = residence.replace('m2', 'm²') #unificier les notations de m2
    residence = residence.replace('€€', '€')
    residence = residence.replace('€', '€ ')
    residence = residence.replace(',', '.')
    residence = residence.replace(':', '')
    word =  nltk.word_tokenize(residence, language='french') #on transforme notre scripts en block de mots. ceux qui nous intéressent ont un euros à la fin (mais il y en a qui ont un euros à la fin et qui ne nous intéresse pas
    return surface(word)

def get_surface(df): 
    Surface = []
    for j in range(0,df.shape[0]):
        try:
            Surface.append(surface_find(df["infos"][j]))
        except: 
            Surface.append(None)
    df['Surface'] = Surface
    
    for j in range(0,df.shape[0]):
        if df['Surface'][j] != None : #s'il y a un Loyer
            df['Surface'][j] = remove(df['Surface'][j], 7, 100)
    
    df['Max Surface'] = get_max_mean_min(df['Surface'])[0]
    df['Min Surface'] = get_max_mean_min(df['Surface']) [1]
    df['Mean Surface'] =  get_max_mean_min(df['Surface']) [2]
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

def get_OLS_reg(Xcolumn,Ycolumn):
    Xcolumn= sm.add_constant(Xcolumn)
    model = sm.OLS(Ycolumn, Xcolumn).fit()
    res = model.resid
    fig = sm.qqplot(res, fit=True, line="45") 
    return(model.summary(), plt.show())

def get_sklearn_regression(Xcolumn,Yvolumn,nomX,nomY):
    X=np.array(X).reshape(-1,1) ##on transforme Y et X en matrices colonnes
    Y = np.array(Y).reshape(-1,1)
    X_train, X_test, Y_train, Y_test = train_test_split(X,Y,test_size=0.3,train_size=0.7)
    lin= LinearRegression()
    reg = lin.fit(X_train,Y_train)
    pred_train = lin.predict(X_train)
    pred_test = lin.predict(X_test)
    coefficients_sans_cst= reg.coef_
    r_2 = reg.score(X_train,Y_train)
    
    plt.scatter(X_train, Y_train, color='red') # plotting the observation line
    plt.plot(X_train, lin.predict(X_train), color='blue') # plotting the regression line
    plt.title("nomY vs nomX (Training set)") # stating the title of the graph
    plt.xlabel("nomX") # adding the name of x-axis
    plt.ylabel("nomY") # adding the name of y-axis
    plt.show() # specifies end of graph
    
    return (r_2, coefficients_sans_cst)