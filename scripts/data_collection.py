import requests
import bs4
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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
                plt.plot(df.index, df[country], marker='o', label=country, color=colors[i % len(colors)])
        else:
            for country in df.columns:
                plt.plot(df.index, df[country], marker='o', label=country)

        plt.title(title if title else indicator_name, fontsize=16)
        plt.xlabel("Année", fontsize=12)
        plt.ylabel(indicator_name, fontsize=12)
        plt.xticks(df.index, rotation=45)
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.legend(title="Pays")
        plt.tight_layout()
        plt.show()

def get_landlockedCountries(url):

    """
    Scrapes a Wikipedia table of countries and their coastline lengths
    and returns a DataFrame containing only relevant columns. 
    The resulting DataFrame includes country names and their coastline lengths (in kilometers).

    *** Parameters

    url : str (The URL of the Wikipedia page containing the table of countries and their coastlines.)

    *** Returns

    pandas.DataFrame
    A cleaned DataFrame with two columns:
    - 'Pays': the name of each country (string)
    - 'Coastline(km)': the length of its coastline in kilometers (numeric)
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
    
    # Regroupement des données dans un dictionnaire 
    dico_countries = dict()
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        if len(cols) > 0 : 
            dico_countries[cols[0]] = cols[:3] # Je ne sélectionne que les collones relatives aux frontières maritimes

    # Structuration dans un dataframe en suite
    data_countries = pd.DataFrame.from_dict(dico_countries,orient='index')
    data_countries = data_countries.reset_index()
    columns_to_drop = data_countries.columns[[0,2]] # J'enlève les données de la CIA. Pas très pertinentes 
    data_countries = data_countries.drop(columns=columns_to_drop,axis=1)
    data_countries = data_countries.rename(columns={0: "Pays", 2: "Coastline(km)"})
    
    data_countries.drop(0,inplace=True) # Enlever la ligne contenant l'information sur tout le MONDE

    # Convertir la colonne des frontières en valeurs numériques
    data_countries["Coastline(km)"] = data_countries["Coastline(km)"].apply(lambda x: x.replace(',',''))
    data_countries["Coastline(km)"] = pd.to_numeric(data_countries["Coastline(km)"])
    
    return data_countries



def get_ISOcodes(url):

    """
    Scrapes a Wikipedia table containing ISO country codes, cleans the data, 
    and returns a structured DataFrame with each country's name and its corresponding ISO codes.

    Parameters
    ----------
    url : str
        The URL of the Wikipedia page containing the table of countries and their ISO codes.

    Returns
    -------
    pandas.DataFrame
        A cleaned DataFrame with the following columns:
        - 'Pays': the name of each country
        - 'ISO-2': the two-letter ISO country code
        - 'ISO-3': the three-letter ISO country code
    """

    requests_text = requests.get(
    url,
    headers={"User-Agent": "Python for data science tutorial"}
    ).content

    page = bs4.BeautifulSoup(requests_text, "lxml")
    iso_table= page.find('table')
    table_body = iso_table.find('tbody')
    rows = table_body.find_all('tr')

    # Regroupement des données dans un dictionnaire 
    dico_ISO = dict()
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        if len(cols) > 0 : 
            dico_ISO[cols[0]] = cols[:5] # Je ne sélectionne que les colonnes qui contiennent les codes ISO

   
    # Structuration dans un dataframe ensuite
    data_ISO = pd.DataFrame.from_dict(dico_ISO,orient='index')
    data_ISO = data_ISO.reset_index()

    columns_to_drop = data_ISO.columns[[0,2,3]] # J'enlève les colonnes inutiles 
    data_ISO = data_ISO.drop(columns=columns_to_drop,axis=1)
    data_ISO = data_ISO.rename(columns={0: "Pays", 3: "ISO-2", 4: "ISO-3"})
    
    return data_ISO
    
# iso_url = "https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes"
# data = get_ISOcodes(iso_url)
# print(data.head())

# url_Landlocked = "https://en.wikipedia.org/wiki/List_of_countries_by_length_of_coastline"
# data = get_landlockedCountries(url_Landlocked)
# print(data.head(10))

