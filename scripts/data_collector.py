import requests
import bs4
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np



url = "https://api.worldbank.org/v2/country?format=json&per_page=500"
response = requests.get(url)
data = response.json()[1]  # [1] contient la liste des pays

# Transformer en DataFrame
countries_df = pd.DataFrame(data)

# Sélection des codes ISO2
iso2_codes = countries_df["iso2Code"].tolist()

# Afficher les 10 premiers codes
#print("the 10 first codes are : ", iso2_codes[:10])

class WorldBankData:
    """
    Classe pour récupérer et visualiser des indicateurs World Bank pour un ou plusieurs pays.
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
    

class TradeDataAnalyzer:
    """
    Analyse des importations, exportations et balance commerciale.
    Fournit nettoyage, calcul de la balance, ratio et classification binaire.
    """

    def __init__(self, imports_df, exports_df):
        """
        imports_df, exports_df : DataFrames pivotés (index = années, colonnes = pays)
        """
        self.imports = imports_df.copy()
        self.exports = exports_df.copy()
        self._clean_data()
        self._compute_balance_ratio()
        self._concat_by_country()

    def _clean_data(self):
        """Remplacer les NaN par 0 et aligner tous les pays dans les deux DataFrames."""
        self.imports = self.imports.fillna(0)
        self.exports = self.exports.fillna(0)

        all_countries = set(self.imports.columns).union(set(self.exports.columns))
        for country in all_countries:
            if country not in self.imports.columns:
                self.imports[country] = 0
            if country not in self.exports.columns:
                self.exports[country] = 0

        # Réordonner les colonnes
        self.imports = self.imports[sorted(all_countries)]
        self.exports = self.exports[sorted(all_countries)]
        self.all_countries = sorted(all_countries)

    def _compute_balance_ratio(self):
        """Calculer la balance commerciale et le ratio export/import."""
        self.balance = self.exports - self.imports
        # Ratio export/import
        self.ratio = self.exports / self.imports.replace(0, 1) # empêcher la division par zéro

    def _concat_by_country(self):
        """Concaténer les colonnes par pays : import, export, balance, ratio."""
        df_list = []
        for country in self.all_countries:
            temp = pd.concat([
                self.imports[[country]].rename(columns={country: f"{country}_import"}),
                self.exports[[country]].rename(columns={country: f"{country}_export"}),
                self.balance[[country]].rename(columns={country: f"{country}_balance"}),
                self.ratio[[country]].rename(columns={country: f"{country}_ratio"})
            ], axis=1)
            df_list.append(temp)
        self.df_combined = pd.concat(df_list, axis=1)
        self.df_combined.index.name = "Year"

    def get_combined_df(self):
        """Retourne le DataFrame complet avec colonnes groupées par pays."""
        return self.df_combined

    def get_balance(self):
        """Retourne le DataFrame de la balance commerciale uniquement."""
        return self.balance

    def get_ratio(self):
        """Retourne le DataFrame des ratios export/import."""
        return self.ratio

    def classify_countries(self, threshold=0):
        """
        Classifie les pays selon leur balance moyenne.
        Exportateur net = 1 si balance moyenne > threshold, sinon 0.
        """
        balance_mean = self.balance.mean()
        classification = (balance_mean > threshold).astype(int)
        classification_df = pd.DataFrame({
            "Country": balance_mean.index,
            "Balance_mean": balance_mean.values,
            "Exportateur_net": classification.values
        })
        return classification_df
  

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
PIB_df = wb.get_indicator("PIB", ["FR","DE","US"], start=2000, end=2024)

print("Données récupérées avec succès.")