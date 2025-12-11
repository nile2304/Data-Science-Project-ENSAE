import requests
import pandas as pd
import json
import os
from datetime import datetime

# --- Configuration ---
INDICATEURS = {
    "PIB_reel": "NY.GDP.MKTP.KD",
    "PIB_nominal": "NY.GDP.MKTP.CD",
    "PIB_par_habitant": "NY.GDP.PCAP.KD",
    "Chomage": "SL.UEM.TOTL.ZS",
    "Exportations": "NE.EXP.GNFS.ZS",
    "Importations": "NE.IMP.GNFS.ZS"
}

START_YEAR = 2000
END_YEAR = 2024
PER_PAGE = 20000
BACKUP_FOLDER = "worldbank_backup"

# --- Création du dossier backup ---
os.makedirs(BACKUP_FOLDER, exist_ok=True)

# --- Récupération de la liste complète des pays ---
url_countries = f"https://api.worldbank.org/v2/country?format=json&per_page=500"
response = requests.get(url_countries)
if response.status_code != 200:
    raise ConnectionError(f"Erreur API : {response.status_code}")
countries_data = response.json()[1]
country_codes = [c["id"] for c in countries_data]  # ISO3 codes

# --- Fonction pour récupérer un indicateur complet ---
def get_indicator_full(indicator_code, countries, start=START_YEAR, end=END_YEAR, batch_size=50):
    """
    Récupère toutes les séries temporelles pour tous les pays listés pour un indicateur donné,
    en découpant par batch pour éviter les erreurs 400.
    """
    all_dfs = []
    for i in range(0, len(countries), batch_size):
        batch = countries[i:i+batch_size]
        countries_str = ";".join(batch)
        url = f"https://api.worldbank.org/v2/country/{countries_str}/indicator/{indicator_code}?date={start}:{end}&format=json&per_page={PER_PAGE}"
        
        response = requests.get(url)
        if response.status_code != 200:
            print(f"⚠️ Erreur API pour le batch {batch}: {response.status_code}")
            continue  # passe au batch suivant
        
        data_json = response.json()[1]
        df = pd.DataFrame(data_json)[["country","date","value"]]
        df["country"] = df["country"].apply(lambda x: x["value"])
        df["date"] = df["date"].astype(int)
        df_pivot = df.pivot(index="date", columns="country", values="value").sort_index()
        all_dfs.append(df_pivot)
    
    # Concaténer tous les batchs
    if all_dfs:
        df_full = pd.concat(all_dfs, axis=1)
        df_full = df_full.loc[:,~df_full.columns.duplicated()]  # enlever doublons si nécessaire
        return df_full
    else:
        return pd.DataFrame()


# --- Récupération et sauvegarde de tous les indicateurs ---
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

for name, code in INDICATEURS.items():
    print(f"Récupération de l'indicateur : {name}")
    df_indicator = get_indicator_full(code, country_codes)
    
    # Sauvegarde CSV
    csv_path = os.path.join(BACKUP_FOLDER, f"{name}_{timestamp}.csv")
    df_indicator.to_csv(csv_path, index=True)
    
    # Sauvegarde JSON
    json_path = os.path.join(BACKUP_FOLDER, f"{name}_{timestamp}.json")
    df_indicator.to_json(json_path, orient="split")
    
    print(f"-> Sauvegardé : {csv_path} et {json_path}")

print("Backup complet terminé !")
