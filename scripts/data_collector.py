import requests
import bs4
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

class WorldBankData:
    """
    Classe pour récupérer et visualiser des indicateurs World Bank pour un ou plusieurs pays.
    
    Cette classe permet de :
    - Récupérer des données économiques depuis l'API World Bank
    - Gérer les données manquantes avec des fichiers de secours locaux
    - Visualiser les indicateurs avec des graphiques personnalisés
    
    Indicateurs disponibles :
    - PIB : Produit Intérieur Brut
    - Chômage : Taux de chômage
    - Exportations : Exportations de biens et services
    - Importations : Importations de biens et services
    """

    INDICATEURS = {
        "PIB": "NY.GDP.MKTP.KD",
        "Chomage": "SL.UEM.TOTL.ZS",
        "Exportations": "NE.EXP.GNFS.ZS",
        "Importations": "NE.IMP.GNFS.ZS"
    }

    BACKUP_PATHS = {
        "PIB": "data/PIB_data.csv",
        "Importations": "data/Importations_data.csv",
        "Exportations": "data/Exportations_data.csv",
        "Chomage": "data/Chomage_data.csv"
    }

    def __init__(self):
        self.data = {}  # stocke les DataFrames par indicateur

    def get_indicator(self, indicator_name, countries, start=2000, end=2024):
        """
        Récupère un indicateur pour plusieurs pays.
        """
        if indicator_name not in self.INDICATEURS:
            raise ValueError(f"Indicateur inconnu. Choisir parmi : {list(self.INDICATEURS.keys())}")

        code = self.INDICATEURS[indicator_name]
        countries_str = ";".join([c.upper() for c in countries])
        url = f"https://api.worldbank.org/v2/country/{countries_str}/indicator/{code}?date={start}:{end}&format=json&per_page=20000"
        try:
            response = requests.get(url)
            if response.status_code != 200:
                raise ConnectionError(f"Erreur API : {response.status_code}")

            data_json = response.json()[1]

            df = pd.DataFrame(data_json)[["country", "date", "value"]]
            df["country"] = df["country"].apply(lambda x: x["value"])
            df["date"] = df["date"].astype(int)
            
            df.rename(columns={"value":indicator_name},inplace=True)
            
            self.data[indicator_name] = df
            
            return df
        
        except Exception as e:
            print(f"Erreur lors de la récupération des données : {e}")

            # Path to backup
            backup_path = self.BACKUP_PATHS.get(indicator_name)

            if not backup_path:
                raise FileNotFoundError(f"Impossible de charger les données locales pour {indicator_name}.")

            # Load backup CSV
            df = pd.read_csv(backup_path)
            self.data[indicator_name] = df
            df.drop(columns=['Unnamed: 0'], inplace=True)
            print(f" Données locales chargées depuis {backup_path}")

            return df
    sns.set_style("whitegrid")
    def plot(self, indicator_name, title=None, figsize=(10,6), colors=None):
        """
        Trace un indicateur pour tous les pays chargés.
        """
        
        if indicator_name not in self.data:
            raise ValueError(f"Aucune donnée pour {indicator_name}. Utilisez get_indicator() d'abord.")

        df = self.data[indicator_name]

        plt.figure(figsize=figsize)

        # Couleurs personnalisées
        if colors:
            for i, country in enumerate(df.columns):
                plt.plot(df.index, np.log(df[country]), marker='x', label=country, color=colors[i])
        else:
            for country in df.columns:
                plt.plot(df.index, np.log(df[country]), marker='x', label=country)

        plt.title(title if title else indicator_name, fontsize=16)
        plt.xlabel("Année", fontsize=12)
        plt.ylabel(indicator_name, fontsize=12)
        plt.xticks(df.index, rotation=45)
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.tight_layout()
        plt.show()

def get_rawlandlockedCountries(url):
    """
    Récupère un tableau Wikipedia contenant les pays et la longueur de leurs côtes.

    Paramètres
    ----------
    url : str
        L'URL de la page Wikipedia contenant le tableau des pays et la longueur de leurs côtes.

    Retours
    -------
    list
        Une liste d'éléments BeautifulSoup 'tr' représentant les lignes du tableau HTML.
    """
    
    requests_text = requests.get(
        url,
        headers={"User-Agent": "Python for data science tutorial"}
        ).content
    
    # Récupération des données du tableau depuis la page Wikipédia
    page = bs4.BeautifulSoup(requests_text,"lxml")
    countries_table = page.find("table") 
    table_body = countries_table.find('tbody')
    rows = table_body.find_all('tr')
    
    return rows

def get_ISOcodes(url):
    """
    Récupère un tableau Wikipedia contenant les pays et leurs codes ISO.

    Paramètres
    ----------
    url : str
        L'URL de la page Wikipedia contenant le tableau des pays et leurs codes ISO.

    Retours
    -------
    list
        Une liste d'éléments BeautifulSoup 'tr' représentant les lignes du tableau HTML.
    """

    requests_text = requests.get(
    url,
    headers={"User-Agent": "Python for data science tutorial"}
    ).content

    page = bs4.BeautifulSoup(requests_text, "lxml")
    iso_table= page.find('table')
    table_body = iso_table.find('tbody')
    rows = table_body.find_all('tr')
    
    return rows
