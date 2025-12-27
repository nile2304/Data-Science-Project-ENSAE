import pandas as pd

def clean_landlockedData(rawData):
    """
    Nettoie les données brutes du tableau HTML des pays et leurs longueurs de côtes,
    en retournant un DataFrame structuré avec les noms des pays et les longueurs de côtes en kilomètres.

    Paramètres
    ----------
    rawData : list
        Une liste d'éléments BeautifulSoup 'tr' représentant les lignes du tableau HTML.

    Retours
    -------
    pandas.DataFrame
    Un DataFrame nettoyé avec deux colonnes :
    - 'Pays': le nom de chaque pays (chaîne de caractères)
    - 'Coastline(km)': la longueur de sa côte en kilomètres (numérique)
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
    
    return data_countries.dropna().reset_index(drop=True)


def clean_ISOData(rawData):
    """
    Nettoie les données brutes du tableau HTML des pays et leurs codes ISO,
    en retournant un DataFrame structuré avec les noms des pays et leurs codes ISO correspondants.

    Paramètres
    ----------
    rawData : list
        Une liste d'éléments BeautifulSoup 'tr' représentant les lignes du tableau HTML.

    Retours
    -------
    pandas.DataFrame
    Un DataFrame nettoyé avec les colonnes suivantes :
    - 'Pays': le nom de chaque pays
    - 'ISO-2': le code ISO à deux lettres du pays
    - 'ISO-3': le code ISO à trois lettres du pays
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
