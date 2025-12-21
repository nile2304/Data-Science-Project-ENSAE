import pandas as pd

def check_missing_values(data,col):
    """
    Checks and prints the number and percentage of missing values in the specified column of the DataFrame,
    along with the range of years and number of unique countries represented in the data.
    Parameters
    ----------
    data : pandas.DataFrame
        The DataFrame containing the data.
    col : str
    The name of the column to check for missing values.
    Returns
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
        
    print(f"Il y a {missing_vals_number} valeurs manquantes sur un total de {total_values} dans la base de données. Soit un ratio de {(missing_vals_number/total_values)*100:.2f}% de valeurs manquantes dans la base de données.")


def impute_missing_values(data,col,method="mean"):
    """
    Imputes missing values in the specified column of the DataFrame using the specified method.

    Parameters
    ----------
    data : pandas.DataFrame
        The DataFrame containing the data.
    col : str
        The name of the column in which to impute missing values.
    method : str, optional
        The method to use for imputation. Default is "mean". Other options could be "median", "ffill", "bfill".

    Returns
    -------
    pandas.DataFrame
        The DataFrame with missing values imputed.
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