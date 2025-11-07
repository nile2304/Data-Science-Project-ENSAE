import requests
import bs4
import pandas as pd

def get_landlockedCountries(url):
    """
    Scrapes a Wikipedia table of countries and their coastline lengths
    and returns a DataFrame containing only relevant columns. 
    The resulting DataFrame includes country names and their coastline lengths (in kilometers).

    *** Parameters

    url : str
    The URL of the Wikipedia page containing the table of countries and their coastlines.

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
    

# url_Landlocked = "https://en.wikipedia.org/wiki/List_of_countries_by_length_of_coastline"
# data = get_landlockedCountries(url_Landlocked)
# print(data.head(10))
