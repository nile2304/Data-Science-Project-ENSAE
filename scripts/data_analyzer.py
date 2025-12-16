import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import data_collector as dc
import data_cleaner as dcl
from data_collector import WorldBankData
from data_cleaner import TradeDataPreparer

# --- Préparer la liste des pays ---
codesISO_url = "https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes"
codesISO_data = dc.get_ISOcodes(codesISO_url)
codesISO_data = dcl.clean_ISOData(codesISO_data)
liste_pays = codesISO_data["ISO-2"].tolist()
#print(liste_pays)

# --- Classe pour analyser les données commerciales ---
class TradeDataAnalyzer:
    """
    Analyse des importations, exportations et balance commerciale.
    Fournit calcul de la balance, ratio export/import et ouverture commerciale,
    ainsi qu'une classification binaire simple des pays exportateurs nets.
    """

    def __init__(self, trade_preparer: TradeDataPreparer, min_years=10):
        """
        trade_preparer : instance de TradeDataPreparer déjà exécutée
        min_years : nombre minimal d'années de données valides pour conserver un pays
        """
        self.imports = trade_preparer.imports.copy()
        self.exports = trade_preparer.exports.copy()
        self.PIB = trade_preparer.PIB.copy()
        self.countries = list(self.imports.columns)

        # Filtrer les pays avec trop peu de données
        self._filter_countries(min_years)

        # Calcul des indicateurs
        self._compute_trade_indicators()
<<<<<<< HEAD

=======
#Filter on
>>>>>>> 8c435ea8fc992d2b676e63264af91f6c1af2cb87
    def _filter_countries(self, min_years=10):
        """Ne conserve que les pays avec au moins min_years années de données valides"""
        initial_countries = list(self.imports.columns)  # <-- sauvegarder avant filtrage
        valid_countries = []
        for country in initial_countries:
            n_valid = sum(
                self.imports[country].notna() & 
                self.exports[country].notna() & 
                self.PIB[country].notna()
            )
            if n_valid >= min_years:
                valid_countries.append(country)

        # Ne conserver que les pays valides
        self.imports = self.imports[valid_countries]
        self.exports = self.exports[valid_countries]
        self.PIB = self.PIB[valid_countries]
        self.countries = valid_countries

        print(f"{len(valid_countries)} pays conservés après filtrage sur au moins {min_years} années de données valides contre {len(initial_countries)} initialement.")
        print("Pays conservés :", self.countries)
        print("Pays supprimés :", set(initial_countries) - set(self.countries))  # <-- maintenant correct

    def _compute_trade_indicators(self):
        """Calcule balance, ratio export/import et ouverture commerciale"""
        # Balance commerciale
        self.balance = self.exports - self.imports

        # Ratio export/import (NaN si imports = 0 ou NaN)
        self.ratio = self.exports.divide(self.imports)
        self.ratio[self.imports == 0] = np.nan

        # Ouverture commerciale = (exports + imports) / PIB
        self.openness = (self.exports + self.imports)
        self.openness[self.PIB.isna()] = np.nan

    def get_balance(self) -> pd.DataFrame:
        return self.balance

    def get_ratio(self) -> pd.DataFrame:
        return self.ratio

    def get_openness(self) -> pd.DataFrame:
        return self.openness

    def aggregate_by_country(self) -> pd.DataFrame:
        """Retourne un résumé par pays : moyenne des trois indicateurs"""
        df_agg = pd.DataFrame({
            "Balance_mean": self.balance.mean(),
            "Ratio_mean": self.ratio.mean(),
            "Openness_mean": self.openness.mean()
        })
        return df_agg

    def classify_exporters(self, threshold=0) -> pd.DataFrame:
        """Classe les pays en exportateurs nets ou non"""
        balance_mean = self.balance.mean()
        classification = (balance_mean > threshold).astype(int)
        return pd.DataFrame({
            "Country": balance_mean.index,
            "Balance_mean": balance_mean.values,
            "Exportateur_net": classification.values
        })

# --- Collecte des données via WorldBankData ---
wb = WorldBankData()
imports_df = wb.get_indicator("Importations", countries=['AF', 'AL', 'DZ'], start=2000, end=2024)
exports_df = wb.get_indicator("Exportations", countries=['AF', 'AL', 'DZ'], start=2000, end=2024)
PIB_df = wb.get_indicator("PIB_reel", countries=['AF', 'AL', 'DZ'], start=2000, end=2024)
print("Données Import/Export récupérées.")

# --- Préparer les données pour analyse ---
trade_preparer = TradeDataPreparer(imports_df, exports_df, PIB_df)
analyzer = TradeDataAnalyzer(trade_preparer)

print("Données prêtes pour analyse.")

# --- Calcul des indicateurs ---
balance = analyzer.get_balance()
ratio = analyzer.get_ratio()
openness = analyzer.get_openness()

print("Indicateurs commerciaux calculés.")
print( "la balance commerciale est", "\n", balance)
print("le ratio export/import est", "\n", ratio)
print("l'ouverture commerciale est", "\n", openness)


# --- Agrégats et classification ---
df_summary = analyzer.aggregate_by_country()
df_class = analyzer.classify_exporters(threshold=0)

print("Résumé par pays :")
print(df_summary)
print("Classification des pays en exportateurs nets :")
print(df_class)

# --- Vérification pour un pays spécifique ---
imports_clean, exports_clean, PIB_clean = trade_preparer.get_clean_data()
albania_imports = imports_clean['Albania'].head(10)
albania_exports = exports_clean['Albania'].head(10)
albania_PIB = PIB_clean['Albania'].head(10)

print("Albania - Imports:", albania_imports)
print("Albania - Exports:", albania_exports)
print("Albania - PIB:", albania_PIB)
# --- Ouverture commerciale Albania ---
openness_albania = (albania_imports + albania_exports)
print("Albania - Ouverture commerciale :")
print(openness_albania)