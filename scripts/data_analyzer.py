import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import data_collector as dc
import data_cleaner as dcl
from data_collector import WorldBankData
from data_cleaner import TradeDataPreparer
from data_analysis import check_missing_values, impute_missing_values
from data_visualization import plot_missing_values_per_country
import plotly.express as px



# --- Préparer la liste des pays ---
codesISO_url = "https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes"
codesISO_data = dc.get_ISOcodes(codesISO_url)
codesISO_data = dcl.clean_ISOData(codesISO_data)
liste_pays = codesISO_data["ISO-2"].tolist()
#print(liste_pays)

wb = WorldBankData()

# Exemple : on récupère pour 3 pays pour le test
country_list = ['AF', 'AL', 'DZ']

imports_df = wb.get_indicator("Importations", countries=country_list, start=2000, end=2024)
exports_df = wb.get_indicator("Exportations", countries=country_list, start=2000, end=2024)
PIB_df = wb.get_indicator("PIB", countries=country_list, start=2000, end=2024)

print("Données Import/Export récupérées.")

# --- Assurer que les colonnes de données sont numériques ---
for df, val_col in zip([imports_df, exports_df, PIB_df],
                       ['Importations', 'Exportations', 'PIB']):
    df[val_col] = pd.to_numeric(df[val_col], errors='coerce')

# --- Pivot pour avoir les pays en colonnes (format attendu par TradeDataAnalyzer) ---
imports_df = imports_df.pivot(index='date', columns='country', values='Importations')
exports_df = exports_df.pivot(index='date', columns='country', values='Exportations')
PIB_df = PIB_df.pivot(index='date', columns='country', values='PIB')

# --- Interpolation pour combler les éventuelles valeurs manquantes ---
imports_df = imports_df.interpolate(method='linear', axis=0)
exports_df = exports_df.interpolate(method='linear', axis=0)
PIB_df = PIB_df.interpolate(method='linear', axis=0)

print("Données Import/Export nettoyées et interpolées.")

# --- Préparer l'objet TradeDataPreparer ---
trade_preparer = TradeDataPreparer(imports_df, exports_df, PIB_df)

# --- Analyse et calcul des indicateurs commerciaux ---
class TradeDataAnalyzer:
    """Classe pour analyse des données commerciales."""
    def __init__(self, trade_preparer: TradeDataPreparer, min_years=10):
        self.imports = trade_preparer.imports.copy()
        self.exports = trade_preparer.exports.copy()
        self.PIB = trade_preparer.PIB.copy()
        self.countries = list(self.imports.columns)

        self._filter_countries(min_years)
        self._compute_trade_indicators()

    def _filter_countries(self, min_years=10):
        initial_countries = list(self.imports.columns)
        valid_countries = []
        for country in initial_countries:
            n_valid = sum(
                self.imports[country].notna() &
                self.exports[country].notna() &
                self.PIB[country].notna()
            )
            if n_valid >= min_years:
                valid_countries.append(country)

        self.imports = self.imports[valid_countries]
        self.exports = self.exports[valid_countries]
        self.PIB = self.PIB[valid_countries]
        self.countries = valid_countries

        print(f"{len(valid_countries)} pays conservés après filtrage (≥{min_years} années).")
        print("Pays conservés :", self.countries)
        print("Pays supprimés :", set(initial_countries) - set(self.countries))

    def _compute_trade_indicators(self):
        """Balance, ratio export/import, ouverture commerciale"""
        self.balance = self.exports - self.imports
        self.ratio = self.exports.divide(self.imports)
        self.ratio[self.imports == 0] = np.nan
        self.openness = (self.exports + self.imports)
        self.openness[self.PIB.isna()] = np.nan

    def get_balance(self) -> pd.DataFrame:
        return self.balance

    def get_ratio(self) -> pd.DataFrame:
        return self.ratio

    def get_openness(self) -> pd.DataFrame:
        return self.openness

    def aggregate_by_country(self) -> pd.DataFrame:
        df_agg = pd.DataFrame({
            "Balance_mean": self.balance.mean(),
            "Ratio_mean": self.ratio.mean(),
            "Openness_mean": self.openness.mean()
        })
        return df_agg
    
analyzer = TradeDataAnalyzer(trade_preparer)

balance = analyzer.get_balance()
ratio = analyzer.get_ratio()
openness = analyzer.get_openness()

print("Indicateurs commerciaux calculés.")
print(balance.head())
print(ratio.head())
print(openness.head())

# --- Agrégats ---
df_summary = analyzer.aggregate_by_country()
print("Résumé par pays :")
print(df_summary)

# --- Accès à un pays spécifique ---
albania_imports = imports_df['Albania'].head(10)
albania_exports = exports_df['Albania'].head(10)
albania_PIB = PIB_df['Albania'].head(10)
openness_albania = (albania_imports + albania_exports)

print("Albania - Ouverture commerciale :")
print(openness_albania)

class HDIDataAnalyzer:
    """
    Classe pour collecter, nettoyer et analyser les données HDI.
    On conserve les colonnes : countryIsoCode (ISO-3), country, indexCode, year, value.
    Analyse des valeurs manquantes, suppression des pays incomplets et imputation.
    """

    def __init__(self, file_path, missing_threshold=0.3):
        """
        Parameters
        ----------
        file_path : str
            Chemin vers le fichier hdi-data.xlsx
        missing_threshold : float
            Seuil de proportion de valeurs manquantes par pays pour exclusion (0-1)
        """
        self.file_path = file_path
        self.missing_threshold = missing_threshold
        self.raw_data = None
        self.df_clean = None
        self.df_aggregated = None
        self.excluded_countries = []

        self.read_data()


    def read_data(self):
        """Lecture et filtrage des données HDI depuis le fichier Excel."""
        df = pd.read_excel(self.file_path)
        if 'indexCode' in df.columns:
            df = df[df['indexCode'] == 'HDI']
        self.raw_data = df[['countryIsoCode', 'country', 'indexCode', 'year', 'value']].copy()
        print(f"Données lues : {self.raw_data.shape[0]} lignes.")

    def descriptive_stats(self):
        """Statistiques descriptives globales et par pays."""
        df = self.raw_data.copy()
        print("Statistiques globales HDI :")
        print(df['value'].describe())
        print("\nNombre de pays :", df['countryIsoCode'].nunique())
        print("Années couvertes : de", df['year'].min(), "à", df['year'].max())

    def analyze_missing(self):
        """
        Analyse des valeurs manquantes :
        - Par pays : compte et ratio
        - Visualisation des pays au-dessus du seuil
        - Exclusion des pays incomplets
        """
        df = self.raw_data.copy()
        missing_counts = df.groupby('countryIsoCode')['value'].apply(lambda x: x.isna().sum())
        total_years = df['year'].nunique()
        missing_ratio = missing_counts / total_years

        self.excluded_countries = missing_ratio[missing_ratio > self.missing_threshold].index.tolist()
        print(f"Pays exclus (>{self.missing_threshold*100:.0f}% valeurs manquantes) : {self.excluded_countries}")

        # Visualisation des pays avec trop de valeurs manquantes
        if len(self.excluded_countries) > 0:
            plot_missing_values_per_country(df.rename(columns={'year':'date','value':'HDI'}),
                                            'HDI',
                                            treshold=self.missing_threshold)
            
    def clean_data(self):
        """
        Nettoyage des données :
        - Suppression des pays incomplets
        - Imputation des valeurs manquantes par pays (moyenne)
        """
        df = self.raw_data[~self.raw_data['countryIsoCode'].isin(self.excluded_countries)].copy()
        df = df.rename(columns={'year':'date','value':'HDI'})
        df = impute_missing_values(df, 'HDI', method="mean")
        self.df_clean = df
        print(f"Données nettoyées : {self.df_clean.shape[0]} lignes conservées.")

    def aggregate_by_country(self):
        """
        Agrégation par pays ISO-3 :
        - HDI moyen
        - HDI minimum
        """
        if self.df_clean is None:
            raise ValueError("Les données doivent être nettoyées avec clean_data() avant l'agrégation.")
        agg_df = self.df_clean.groupby('countryIsoCode')['HDI'].agg(['mean', 'min']).reset_index()
        agg_df.rename(columns={'mean':'HDI_mean','min':'HDI_min'}, inplace=True)
        self.df_aggregated = agg_df
        print("Agrégation par pays terminée.")

    def get_clean_df(self):
        """Retourne le DataFrame nettoyé et harmonisé."""
        if self.df_clean is None:
            raise ValueError("Données non nettoyées. Exécuter clean_data() d'abord.")
        return self.df_clean.copy()

    def get_aggregated_df(self):
        """Retourne le DataFrame agrégé par pays (HDI_mean, HDI_min)."""
        if self.df_aggregated is None:
            raise ValueError("Données non agrégées. Exécuter aggregate_by_country() d'abord.")
        return self.df_aggregated.copy()


hdi_file_path = "data\\hdi-data.xlsx"
hdi_analyzer = HDIDataAnalyzer(hdi_file_path, missing_threshold=0.3)
hdi_analyzer.descriptive_stats()
hdi_analyzer.analyze_missing()
hdi_analyzer.clean_data()
hdi_analyzer.aggregate_by_country()
df_clean = hdi_analyzer.get_clean_df()
df_agg = hdi_analyzer.get_aggregated_df()
print("Données HDI nettoyées :")
print(df_clean.head())
print("\nDonnées HDI agrégées :")
print(df_agg.head())


plt.hist(df_agg['HDI_mean'], bins=20, color='skyblue', edgecolor='black')
plt.title("Distribution de l'IDH moyen par pays")
plt.xlabel("HDI moyen")
plt.ylabel("Nombre de pays")
plt.show()



#Heatmap mondiale de l'IDH moyen par pays
fig = px.choropleth(
    df_agg,
    locations="countryIsoCode",  # colonnes ISO-3
    color="HDI_mean",            # valeur à afficher
    hover_name="countryIsoCode", # nom affiché au survol
    color_continuous_scale=px.colors.sequential.YlGnBu,
    title="Heatmap mondiale de l'IDH moyen par pays"
)

fig.show()

df_hdi_time = hdi_analyzer.get_clean_df().groupby('date')['HDI'].mean().reset_index()
plt.figure(figsize=(10,6))
sns.lineplot(data=df_hdi_time, x='date', y='HDI')
plt.title("Évolution de l'IDH moyen mondial")
plt.xlabel("Année")
plt.ylabel("HDI")
plt.tight_layout()  # pour que tout rentre bien
plt.show() 

