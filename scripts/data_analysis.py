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
    
    return data
    