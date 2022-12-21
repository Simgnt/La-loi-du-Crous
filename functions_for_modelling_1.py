
"""
functions for modelling
"""

import pandas as pd

import numpy as np


import statsmodels.api as sm
import matplotlib.pyplot as plt

from sklearn.linear_model import LinearRegression
import math
from sklearn.model_selection import train_test_split


"""
Part IV : Régressions  
"""

""" La fonction get_OLS_reg permet de construire une régression simple ou multipe, elle prend en argument la ou les variables explicatives (Xcolumn) et la variable expliquée (Ycolumn). Pour construire la régression on utilise les fonctions du module Statsmodels."""

def get_OLS_reg(Xcolumn,Ycolumn): 
    Xcolumn= sm.add_constant(Xcolumn) #on ajoute une constante au vecteur de variables explicatives. 
    return(print(sm.OLS(Ycolumn, Xcolumn).fit().summary())) #on définit le modèle de régression linéaire par la commande sm.OLS(Y,X).fit() et la fonction summary permet d'afficher le tableau récapitulatif


"""La fonction get_bp_test permet d'effectuer un test de Breusch-Pagan. Ce test permet de tester l'hypothèse HO "les résidus sont homoscedastiques". La fonction prend en argument la ou les variables explicatives (Xcolumn) et la variable expliquée (Ycolumn). """

def get_bp_test_OLS(Xcolumn,Ycolumn):
    Xcolumn= sm.add_constant(Xcolumn)
    model = sm.OLS(Ycolumn, Xcolumn).fit()
    res = model.resid
    bp_test=sm.stats.diagnostic.het_breuschpagan(res,Xcolumn)
    labels = ['LM Statistic', 'LM-Test p-value', 'F-Statistic', 'F-Test p-value']
    return('breusch_pagan_results=',dict(zip(labels, bp_test)))


"""La fonction get_RLM permet de construire une régression linéaire robuste prenant en compte une possible hétéroscedasticité des données. On utilise la commande RLM (Robust Linear Model) de Statsmodels. La fonction prend en argument la ou les variables explicatives (Xcolumn) et la variable expliquée (Ycolumn) de la régression."""

def get_RLM(Xcolumn, Ycolumn):
    Xcolumn = sm.add_constant(Xcolumn) #on ajoute l'intercept à la variable explicative.
    return(print(sm.RLM(Ycolumn, Xcolumn).fit().summary())) #on définit cette fois le modèle de régression linéaire robust par la commande sm.RLM(Y,X).fit() et la fonction summary permet d'afficher le tableau récapitulatif

