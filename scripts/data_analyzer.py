import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from . import data_collector as dc
from . import data_cleaner as dcl

codesISO_url = "https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes"
codesISO_data = dc.get_ISOcodes(codesISO_url)
codesISO_data = dcl.clean_ISOData(codesISO_data)
liste_pays = codesISO_data["ISO-2"].tolist()

#print(liste_pays[:10])


wb = dc.WorldBankData()

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


imports__data = wb.get_indicator("Importations", liste_pays, start=2015, end=2024)
exports_data = wb.get_indicator("Exportations", liste_pays, start=2015, end=2024)


