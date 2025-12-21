import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt

def clean_landlockedData(rawData):
    """
        Cleans raw HTML table data of countries and their coastline lengths,
        returning a structured DataFrame with country names and coastline lengths in kilometers.

        Parameters
        ----------
        rawData : list
            A list of BeautifulSoup 'tr' elements representing rows of the HTML table.

        Returns
        -------
        pandas.DataFrame
        A cleaned DataFrame with two columns:
        - 'Pays': the name of each country (string)
        - 'Coastline(km)': the length of its coastline in kilometers (numeric)
    """

    # Regroupement des données dans un dictionnaire 
    dico_countries = dict()
    for row in rawData:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        if len(cols) > 0 : 
            dico_countries[cols[0]] = cols[:3] # Je ne sélectionne que les collones relatives aux frontières maritimes

    # Structuration dans un dataframe en suite
    data_countries = pd.DataFrame.from_dict(dico_countries,orient='index')
    data_countries = data_countries.reset_index()
    columns_to_drop = data_countries.columns[[0,2]] # J'enlève les données de la CIA. Pas très pertinentes 
    data_countries = data_countries.drop(columns=columns_to_drop,axis=1)
    data_countries = data_countries.rename(columns={0: "country", 2: "Coastline"})
    
    data_countries.drop(0,inplace=True) # Enlever la ligne contenant l'information sur tout le MONDE

    # Convertir la colonne des frontières en valeurs numériques
    data_countries["Coastline"] = data_countries["Coastline"].apply(lambda x: x.replace(',',''))
    data_countries["Coastline"] = pd.to_numeric(data_countries["Coastline"])
    
    return data_countries


def clean_ISOData(rawData):
    """
    Cleans raw HTML table data of countries and their ISO codes,
    returning a structured DataFrame with each country's name and its corresponding ISO codes.

    Parameters
    ----------
    rawData : list
        A list of BeautifulSoup 'tr' elements representing rows of the HTML table.

    Returns
    -------
    pandas.DataFrame
    A cleaned DataFrame with the following columns:
    - 'Pays': the name of each country
    - 'ISO-2': the two-letter ISO country code
    - 'ISO-3': the three-letter ISO country code
    """

    # Regroupement des données dans un dictionnaire 
    dico_ISO = dict()
    for row in rawData:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        if len(cols) > 0 : 
            dico_ISO[cols[0]] = cols[:5] # Je ne sélectionne que les colonnes qui contiennent les codes ISO

   
    # Structuration dans un dataframe ensuite
    data_ISO = pd.DataFrame.from_dict(dico_ISO,orient='index')
    data_ISO.reset_index(drop=True,inplace=True)

    columns_to_drop = data_ISO.columns[[1]] # J'enlève les colonnes inutiles 
    data_ISO.drop(columns=columns_to_drop,axis=1,inplace=True)
    data_ISO.rename(columns={0: "Pays", 3: "ISO-2", 4: "ISO-3"},inplace=True)

    # Certaines lignes inutiles à enlever (lignes vides qui renvoient vers d'autres dénominations du pays en question)
    # Ou même des régions qui sont sous la souveraineté d'un pays. On les enlève.

    data_ISO.dropna() # Enlever les lignes vides
    data_ISO = data_ISO[data_ISO[2] == 'UN member'] # Ne garder que les pays membres de l'ONU
    data_ISO.drop(columns=[2],axis=1,inplace=True)
    
    return data_ISO.reset_index(drop=True)
