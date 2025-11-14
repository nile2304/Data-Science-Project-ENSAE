import requests
import bs4
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

class WorldBankData:
    """
    Classe pour récupérer et visualiser des indicateurs World Bank pour un ou plusieurs pays.
    """

    INDICATEURS = {
        "PIB_reel": "NY.GDP.MKTP.KD",
        "PIB_nominal": "NY.GDP.MKTP.CD",
        "PIB_par_habitant": "NY.GDP.PCAP.KD",
        "Chomage": "SL.UEM.TOTL.ZS",
        "Exportations": "NE.EXP.GNFS.ZS",
        "Importations": "NE.IMP.GNFS.ZS"
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

        response = requests.get(url)
        if response.status_code != 200:
            raise ConnectionError(f"Erreur API : {response.status_code}")

        data_json = response.json()[1]

        df = pd.DataFrame(data_json)[["country", "date", "value"]]
        df["country"] = df["country"].apply(lambda x: x["value"])
        df["date"] = df["date"].astype(int)

        df_pivot = df.pivot(index="date", columns="country", values="value").sort_index()
        self.data[indicator_name] = df_pivot
        return df_pivot

    sns.set_theme(style="whitegrid")  # style de base pour les graphiques

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
    Scrapes a Wikipedia table containing countries and their coastline lengths.

    Parameters
    ----------
    url : str
        The URL of the Wikipedia page containing the table of countries and their coastline lengths.

    Returns
    -------
    list
    A list of BeautifulSoup 'tr' elements representing rows of the HTML table.
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
    Scrapes a Wikipedia table containing countries and their ISO codes.

    Parameters
    ----------
    url : str
        The URL of the Wikipedia page containing the table of countries and their ISO codes.

    Returns
    -------
    list:
        A list of BeautifulSoup 'tr' elements representing rows of the HTML table.
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