def check_missing_values(data,col):
    
    missing_vals_number = data.isna().sum()[col]

    num_countries = data["country"].nunique()
    total_values = len(data)

    debut = data["date"].min() 
    fin = data["date"].max()
    
    print(f"Le dataframe contient des données temporelles relatives à {num_countries} pays de {debut} à {fin}.")
    print(f"Il y a {missing_vals_number} valeurs manquantes sur un total de {total_values} dans la base de données. Soit un ratio de {(missing_vals_number/total_values)*100:.2f}%.")

    
    