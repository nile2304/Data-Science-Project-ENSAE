import requests
import bs4
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import json
from datetime import datetime
import time 


url = "https://api.worldbank.org/v2/country?format=json&per_page=500"
response = requests.get(url)
print("Status code:", response.status_code)
data = response.json()[1]
#[1] contient la liste des pays

<<<<<<< HEAD
=======
# Transformer en DataFrame
countries_df = pd.DataFrame(data)

# Sélection des codes ISO2
iso2_codes = countries_df["iso2Code"].tolist()
# Afficher les 10 premiers codes
#print("the 10 first codes are : ", iso2_codes[:10])

>>>>>>> 8c435ea8fc992d2b676e63264af91f6c1af2cb87
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
        self.data = {}
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "python-requests/2.31.0",
            "Accept": "application/json"
        })
    
    def get_indicator(self, indicator_name, countries, start=2000, end=2024, batch_size=10):
        if indicator_name not in self.INDICATEURS:
            raise ValueError(f"Indicateur inconnu. Choisir parmi : {list(self.INDICATEURS.keys())}")
        
        code = self.INDICATEURS[indicator_name]
        all_df = []

        for i in range(0, len(countries), batch_size):
            batch = countries[i:i+batch_size]
            countries_str = ";".join([c.upper() for c in batch])
            url = f"https://api.worldbank.org/v2/country/{countries_str}/indicator/{code}?date={start}:{end}&format=json&per_page=20000"
            
            for attempt in range(3):  # retry si erreur 403
                response = self.session.get(url)
                if response.status_code == 200:
                    break
                else:
                    print(f"Erreur {response.status_code} pour batch {batch}, retry {attempt+1}/3...")
                    time.sleep(2)
            else:
                print(f"Impossible de récupérer le batch {batch}, saut...")
                continue

            data_json = response.json()[1]
            df = pd.DataFrame(data_json)[["country", "date", "value"]]
            df["country"] = df["country"].apply(lambda x: x["value"])
            df["date"] = df["date"].astype(int)
            df_pivot = df.pivot(index="date", columns="country", values="value").sort_index()
            all_df.append(df_pivot)

        result = pd.concat(all_df, axis=1)
        self.data[indicator_name] = result
        return result
    def backup_data(self, folder="backup"):
        """
        Sauvegarde toutes les données récupérées dans des fichiers JSON.
        Chaque indicateur est sauvegardé dans un fichier séparé avec timestamp.
        """
        if not self.data:
            print("Aucune donnée à sauvegarder.")
            return

        # Crée le dossier backup s'il n'existe pas
        os.makedirs(folder, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        for indicator, df in self.data.items():
            file_path = os.path.join(folder, f"{indicator}_{timestamp}.json")
            # Conversion du DataFrame en dictionnaire
            data_dict = df.to_dict(orient="index")
            # Sauvegarde en JSON
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data_dict, f, ensure_ascii=False, indent=4)
            print(f"Backup de '{indicator}' sauvegardé dans : {file_path}")

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

wb = WorldBankData()
liste_pays = iso2_codes  # Utilisation des codes ISO2 récupérés précédemment

# Récupération des données
imports_df = wb.get_indicator("Importations", ["FR","DE","US"], start=2000, end=2024)
exports_df = wb.get_indicator("Exportations", ["FR","DE","US"], start=2000, end=2024)
PIB_df = wb.get_indicator("PIB_reel", ["FR","DE","US"], start=2000, end=2024)

print("Données récupérées avec succès.")

# Récupération d’un indicateur pour tester
#wb.get_indicator("PIB_nominal", countries=["FR","DE","US"], start=2000, end=2024)

# Sauvegarde de toutes les données déjà récupérées
#wb.backup_data(folder="worldbank_backup")