import pandas as pd

def check_missing_values(data,col):
    """
    Vérifie et affiche le nombre et le pourcentage de valeurs manquantes dans la colonne spécifiée du DataFrame,
    ainsi que la plage de dates et le nombre de pays uniques représentés dans les données.
    
    Paramètres
    ----------
    data : pandas.DataFrame
        Le DataFrame contenant les données.
    col : str
        Le nom de la colonne à vérifier pour les valeurs manquantes.
    
    Retours
    -------
    None
    """
    
    missing_vals_number = data.isna().sum()[col]

    num_countries = data["country"].nunique()
    total_values = len(data)

    if "date" in data.columns:
        debut = data["date"].min() 
        fin = data["date"].max()
        
        print(f"Le dataframe contient des données temporelles relatives à {num_countries} pays de {debut} à {fin}.")
        
    print(f"Il y a {missing_vals_number} valeurs manquantes sur un total de {total_values} dans la base de données.\nSoit un ratio de {(missing_vals_number/total_values)*100:.2f}% de valeurs manquantes dans la base de données.\n")


def impute_missing_values(data,col,method="mean"):
    """
    Impute les valeurs manquantes dans la colonne spécifiée du DataFrame en utilisant la méthode spécifiée.

    Paramètres
    ----------
    data : pandas.DataFrame
        Le DataFrame contenant les données.
    col : str
        Le nom de la colonne dans laquelle imputer les valeurs manquantes.
    method : str, optional
        La méthode à utiliser pour l'imputation. Par défaut "mean". Autres options possibles : "median", "ffill", "bfill".

    Retours
    -------
    pandas.DataFrame
        Le DataFrame avec les valeurs manquantes imputées.
    """
    
    if method == "mean":
        data[col] = data.groupby("country")[col].transform(lambda x: x.fillna(x.mean()))
    elif method == "backward_fill":
        data[col] = data.groupby("country")[col].transform(lambda x: x.bfill())
    elif method == "forward_fill":
        data[col] = data.groupby("country")[col].transform(lambda x: x.ffill())

    return data
    

class TradeDataAnalyzer:

    def __init__(self, trade_data):
        self.trade_data = trade_data
        
    def get_balance(self) -> pd.DataFrame:
        self.commercialBalance = self.trade_data['Exportations'] - self.trade_data['Importations']
        self.trade_data['commBalance'] = self.commercialBalance
    
    def aggregate_commercialBalance(self) -> pd.DataFrame:
        aggregated_data = self.trade_data.groupby('country')['commBalance'].mean().reset_index()
        return aggregated_data

    def classify_exporters(self, threshold=0) -> pd.DataFrame:

        aggregated_data = self.aggregate_commercialBalance()
        aggregated_data['netExportateur'] = (aggregated_data['commBalance'] > threshold).astype(int)
        return aggregated_data.drop(columns=['commBalance'])


class HDIDataAnalyzer:
    """
    Classe pour collecter, nettoyer et analyser les données HDI.
    On conserve les colonnes : countryIsoCode (ISO-3), country, indexCode, year, value.
    Analyse des valeurs manquantes, suppression des pays incomplets et imputation.
    """

    def __init__(self, HDI_data):
        self.rawData = HDI_data

    def clean_data(self):
        """
        Nettoyage des données :
        - Suppression des données inutiles
        """

        self.cleaned_data = self.rawData.rename(columns={'year':'date','value':'HDI','countryIsoCode':'country',"country":"pays"})
        self.cleaned_data = self.cleaned_data[['country','date', 'HDI']]
        
        # Enlever les lignes ne contenant pas des informations relatives au pays
        indexes = self.cleaned_data[self.cleaned_data["country"].str.startswith("ZZ")].index
        self.cleaned_data.drop(indexes,inplace=True)
        return self.cleaned_data

    def aggregated_HDI(self):
        """
        Agrégation par pays ISO-3 :
        - HDI moyen
        """
        agg_df = self.cleaned_data.groupby('country')['HDI'].agg(['mean']).reset_index()
        agg_df.rename(columns={'mean':'HDI_mean'}, inplace=True)

        return agg_df