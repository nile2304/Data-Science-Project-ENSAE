import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.cluster import KMeans
import plotly.graph_objects as go

def plot_missing_values_per_year(data,col,text="PIB Reel"):
    """
    Trace le nombre de valeurs manquantes par année pour une colonne spécifiée dans un ensemble de données.

    Cette fonction groupe l'ensemble de données par la colonne 'date', compte le nombre de
    valeurs manquantes pour la colonne spécifiée chaque année, et visualise le résultat
    sous forme de graphique en barres. Chaque barre est annotée avec le nombre exact de valeurs manquantes.

    Paramètres
    ----------
    data : pandas.DataFrame
        Le DataFrame d'entrée contenant une colonne 'date' et la colonne à analyser.
    col : str
        Le nom de la colonne pour laquelle les valeurs manquantes doivent être comptées par année.

    Retours
    -------
    None
        La fonction affiche un graphique en barres matplotlib mais ne retourne aucun objet.
    """
    
    missing_values = data.groupby(["date"])[col].apply(lambda x: x.isna().sum())

    fig, ax1 = plt.subplots(figsize=(12, 6))
    bars = ax1.bar(missing_values.index, missing_values.values, label='Yearly Missing Values')
    for bar in bars:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2, yval, int(yval), va='bottom', ha='center')
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Number of Missing Values per Year')
    ax1.set_title(f'Missing Values per Year for {text}')
    ax1.set_xticks(missing_values.index)
    ax1.set_xticklabels(missing_values.index, rotation=90)
    plt.show()
    
    
def plot_missing_values_per_country(data,col,treshold,text="PIB Reel"):
    """
    Identifie et visualise les pays ayant un nombre anormal de valeurs manquantes pour une colonne donnée.

    Cette fonction groupe l'ensemble de données par pays, compte les valeurs manquantes pour la colonne
    spécifiée, et détermine quels pays dépassent un seuil de valeurs manquantes exprimé comme
    une proportion du nombre total d'observations par pays. Elle trace ces pays sur un graphique
    en barres avec des valeurs annotées et retourne leurs noms.

    Paramètres
    ----------
    data : pandas.DataFrame
        Le DataFrame d'entrée contenant une colonne 'country' et la colonne à analyser.
    col : str
        Le nom de la colonne pour laquelle les valeurs manquantes sont évaluées.
    treshold : float
        Une valeur entre 0 et 1 représentant la proportion de valeurs manquantes au-delà de laquelle
        un pays est signalé comme aberrant (par exemple, 0.2 pour 20%).

    Retours
    -------
    pandas.Index
        Un index contenant les noms de tous les pays dont le nombre de valeurs manquantes dépasse
        le seuil spécifié.
    """

    subset_data = data.groupby(["country"])[col]
    missing_values = subset_data.apply(lambda x: x.isna().sum())
    total_values_per_country = subset_data.apply(lambda x: len(x)).iloc[0]
    relevant_missing_values = missing_values.loc[missing_values > int(treshold*total_values_per_country)]

    fig, ax1 = plt.subplots(figsize=(12, 6))
    bars = ax1.bar(relevant_missing_values.index, relevant_missing_values.values, label='Aberrant Country Missing Values')
    for bar in bars:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2, yval, int(yval), va='bottom', ha='center')
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Number of Missing Values per Country')
    ax1.set_title(f'Missing Values per Country for {text}')
    ax1.set_xticks(relevant_missing_values.index)
    ax1.set_xticklabels(relevant_missing_values.index, rotation=90)
    plt.show()
    
    return relevant_missing_values.index

def plot_world_PIB(PIB_data):
    """
    Trace le PIB total mondial au fil du temps en utilisant les données de PIB fournies.

    Cette fonction agrège les données de PIB par année, additionne les valeurs de PIB pour tous les pays,
    et visualise le PIB mondial total sous forme de graphique linéaire.

    Paramètres
    ----------
    PIB_data : pandas.DataFrame
        Un DataFrame contenant les colonnes 'date' et 'PIB', où 'date' représente les années
        et 'PIB' représente les valeurs de PIB pour différents pays.

    Retours
    -------
    None
        La fonction affiche un graphique linéaire matplotlib mais ne retourne aucun objet.
    """

    world_PIB = PIB_data.groupby("date")["PIB"].sum()

    plt.figure(figsize=(10,6))
    plt.plot(world_PIB.index, world_PIB.values)
    plt.title("Évolution du PIB mondial (1990-2024 USD)")
    plt.xlabel("Année")
    plt.ylabel("PIB Mondial")
    plt.show()

def plot_PIB_quantile(PIB_data):
    """
    Trace le PIB moyen par quantiles au fil du temps.
    Cette fonction divise les données de PIB en 20 quantiles et visualise comment le PIB moyen
    dans chaque quantile évolue au fil du temps. Elle affiche également le PIB moyen global
    comme ligne de référence.

    :param PIB_data: pandas.DataFrame
        DataFrame contenant les données de PIB avec les colonnes:
        - 'PIB': Valeurs de PIB à quantifier
        - 'date': Années ou périodes de temps pour l'axe des x
        
    :return: None
        Affiche une figure matplotlib avec plusieurs lignes de quantiles et une ligne de moyenne globale.
        Chaque quantile est étiqueté sur le côté droit du graphique avec sa couleur de ligne correspondante.
    """

    quantiles = pd.qcut(PIB_data['PIB'], q=20, labels=False)

    data = pd.DataFrame({
        'year': PIB_data['date'],
        'quantiles': quantiles,
        'PIB': PIB_data['PIB']
    })

    grouped_data = data.groupby(['year', 'quantiles'])['PIB'].mean().unstack()
    overall_mean = data.groupby('year')['PIB'].mean()

    plt.figure(figsize=(11, 6))
    for decile in range(20):
        plt.plot(grouped_data.index, grouped_data[decile], label=f'Quantiles {decile + 1}')
        plt.text(grouped_data.index[-1] + 2, grouped_data[decile].iloc[-1],
                f'Quantiles {decile + 1}',
                va='center', ha='left', color=plt.gca().get_lines()[-1].get_color())
    plt.plot(overall_mean.index, overall_mean, label='Overall Mean', linestyle='--', color='black')
    plt.text(overall_mean.index[-1] + 2, overall_mean.iloc[-1] + 13,
         'Mean',
         va='center', ha='left', color='black')
    plt.xlabel('Year')
    plt.ylabel('Average GDP')
    plt.title('Average GDP by Quantiles Over Time')
    plt.show()

def plot_PIB_top_quantile_countries(PIB_data, chosen_quantile=19):
    """
    Trace l'évolution temporelle du PIB des pays appartenant à un quantile supérieur donné.

    - Découpe la distribution du PIB en 20 quantiles.
    - Filtre les pays du quantile `chosen_quantile`.
    - Trace la trajectoire PIB(date) pour chaque pays.
    - Affiche la liste des pays sélectionnés.

    Paramètres
    ----------
    PIB_data : DataFrame
        Doit contenir : `country`, `date`, `PIB`.
    chosen_quantile : int, défaut=19
        Quantile ciblé (0 = plus bas, 19 = 20ᵉ quantile).

    Retour
    ------
    None
    """
    quantiles = pd.qcut(PIB_data['PIB'], q=20, labels=False)

    data = pd.DataFrame({
        'country': PIB_data['country'],
        'year': PIB_data['date'],
        'quantiles': quantiles,
        'CG_debt': PIB_data['PIB']
    })

    top_decile_data = data[data['quantiles'] == chosen_quantile]
    plt.figure(figsize=(12, 6))
    for country in top_decile_data['country'].unique():
        country_data = top_decile_data[top_decile_data['country'] == country]
        plt.plot(country_data['year'], country_data['CG_debt'], label=country)

    plt.xlabel('Year')
    plt.ylabel('PIB')
    plt.title(f'Evolution of PIB for Countries in the {chosen_quantile+1}th Decile')
    plt.show()

    print(f'Countries in the {chosen_quantile+1}th-decile: {data[data["quantiles"] == chosen_quantile]["country"].unique()}')


def visualize_economicPower_clusters(weightCountry_data, width=900, height=500):
    """
    Classe les pays en 4 clusters de puissance économique et affiche une carte choroplèthe.

    - Applique K-Means sur `avgWeightCountry`.
    - Réordonne les clusters par puissance croissante.
    - Génère une carte mondiale interactive.

    Paramètres
    ----------
    weightCountry_data : DataFrame
        Doit contenir : `country`, `avgWeightCountry`.
    width : int, défaut=900
        Largeur de la carte.
    height : int, défaut=500
        Hauteur de la carte.

    Retour
    ------
    DataFrame
        Données avec labels de clusters (`Power`).
    """
    data = weightCountry_data.copy()

    kmeans = KMeans(n_clusters=4, random_state=42)
    data["Power"] = kmeans.fit_predict(data[["avgWeightCountry"]])

    cluster_order = data.groupby("Power")["avgWeightCountry"].mean().sort_values().index
    mapping = {cluster_order[i]: i for i in range(4)}
    data["Power"] = data["Power"].map(mapping)

    fig = px.choropleth(
        data,
        locations="country",
        locationmode="ISO-3",
        color="Power",
        color_continuous_scale=["red", "orange", "blue", "green"],
        title="World Classification Map by Economic Power"
    )

    fig.update_layout(
        geo=dict(showcoastlines=True, coastlinecolor="Black", showland=True, landcolor="white"),
        width=width,
        height=height
    )

    fig.show()
    return data


def visualize_trade_clusters(netExportators_data, width=900, height=500):
    """
    Affiche une carte mondiale de classification binaire des pays exportateurs nets.

    Paramètres
    ----------
    netExportators_data : DataFrame
        Doit contenir : `country`, `netExportateur` (valeur continue ou binaire).
    width : int, défaut=900
        Largeur de la carte.
    height : int, défaut=500
        Hauteur de la carte.

    Retour
    ------
    None
    """
    fig = px.choropleth(
        netExportators_data,
        locations=netExportators_data["country"],
        locationmode="ISO-3",
        color="netExportateur",
        color_continuous_scale=["red", "green"],
        title="World Classification Map by Exportators Countries"
    )

    fig.update_layout(
        geo=dict(showcoastlines=True, coastlinecolor="Black", showland=True, landcolor="white"),
        width=width,
        height=height
    )

    fig.show()


def visualize_landlocked_countries(landlocked_data, width=900, height=500):
    """
    Génère une carte mondiale indiquant si un pays est enclavé ou non.

    Paramètres
    ----------
    landlocked_data : DataFrame
        Doit contenir : `country`, `isLandlocked` (0/1 ou False/True).
    width : int, défaut=900
        Largeur de la carte.
    height : int, défaut=500
        Hauteur de la carte.

    Retour
    ------
    None
    """
    fig = px.choropleth(
        landlocked_data,
        locations=landlocked_data["country"],
        locationmode="ISO-3",
        color="isLandlocked",
        color_continuous_scale=["green", "red"],
        title="World Classification Map by Landlocked Countries"
    )

    fig.update_layout(
        geo=dict(showcoastlines=True, coastlinecolor="Black", showland=True, landcolor="white"),
        width=width,
        height=height
    )

    fig.show()


def visualize_HDI_clusters(HDI_data, width=900, height=500):
    """
    Segmente les pays en 3 clusters selon leur IDH et affiche une carte choroplèthe.

    - Applique K-Means sur la valeur IDH.
    - Réordonne les clusters du plus élevé au plus faible.
    - Affiche la carte interactive.

    Paramètres
    ----------
    HDI_data : DataFrame
        Doit contenir : `country`, `HDI_mean`.
    width : int, défaut=900
        Largeur de la carte.
    height : int, défaut=500
        Hauteur de la carte.

    Retour
    ------
    None
    """
    data = HDI_data.copy()

    kmeans = KMeans(n_clusters=3, random_state=42)
    data["cluster"] = kmeans.fit_predict(data[["HDI_mean"]])

    cluster_order = data.groupby("cluster")["HDI_mean"].mean().sort_values(ascending=False).index
    mapping = {cluster_order[i]: i for i in range(3)}
    data["HDI_cluster"] = data["cluster"].map(mapping)

    fig = px.choropleth(
        data,
        locations="country",
        locationmode="ISO-3",
        color="HDI_cluster",
        color_continuous_scale=["red", "orange", "green"],
        title="World Classification Map by Human Development Index (HDI)"
    )

    fig.update_layout(
        geo=dict(showcoastlines=True, coastlinecolor="Black", showland=True, landcolor="white"),
        width=width,
        height=height
    )

    fig.show()


def animated_economicPower_map(weightCountry_data, width=900, height=500):
    """
    Produit une carte mondiale animée montrant l'évolution des clusters de puissance économique.

    - Applique K-Means (k=4) séparément par année sur `weightCountry`.
    - Réordonne les clusters par puissance croissante.
    - Concatène les données et génère la carte animée.

    Paramètres
    ----------
    weightCountry_data : DataFrame
        Doit contenir : `country`, `date`, `weightCountry`.
    width : int, défaut=900
        Largeur de la carte.
    height : int, défaut=500
        Hauteur de la carte.

    Retour
    ------
    None
    """
    data = weightCountry_data.copy()
    clustered = []

    for year, group in data.groupby("date"):
        kmeans = KMeans(n_clusters=4, random_state=42)
        g = group.copy()
        g["Power"] = kmeans.fit_predict(g[["weightCountry"]])

        order = g.groupby("Power")["weightCountry"].mean().sort_values().index
        mapping = {order[i]: i for i in range(4)}
        g["Power"] = g["Power"].map(mapping)

        clustered.append(g)

    df_clustered = pd.concat(clustered)

    fig = px.choropleth(
        df_clustered,
        locations="country",
        locationmode="ISO-3",
        color="Power",
        color_continuous_scale=["red", "orange", "blue", "green"],
        animation_frame="date",
        title="Economic Power (clusters) over Time",
        range_color=(0, 3)
    )

    fig.update_layout(
        geo=dict(showcoastlines=True, coastlinecolor="Black", showland=True, landcolor="white"),
        width=width,
        height=height
    )

    fig.show()


def animated_HDI_map(HDI_data, width=900, height=500):
    """
    Génère une carte mondiale animée montrant l'évolution des clusters IDH dans le temps.

    Paramètres
    ----------
    HDI_data : DataFrame
        Doit contenir : `country`, `date`, `HDI`.
    width : int, défaut=900
        Largeur de la carte.
    height : int, défaut=500
        Hauteur de la carte.

    Retour
    ------
    None
    """
    clustered = []

    for year, group in HDI_data.groupby("date"):
        kmeans = KMeans(n_clusters=3, random_state=42)
        g = group.copy()
        g["Scale"] = kmeans.fit_predict(g[["HDI"]])

        order = g.groupby("Scale")["HDI"].mean().sort_values().index
        mapping = {order[i]: i for i in range(3)}
        g["Scale"] = g["Scale"].map(mapping)

        clustered.append(g)

    df_clustered = pd.concat(clustered)

    fig = px.choropleth(
        df_clustered,
        locations="country",
        locationmode="ISO-3",
        color="Scale",
        animation_frame="date",
        title="HDI (clusters) over Time",
        range_color=(0, 2)
    )

    fig.update_layout(
        geo=dict(showcoastlines=True, coastlinecolor="Black", showland=True, landcolor="white"),
        width=width,
        height=height
    )

    fig.show()

    

def plot_world_map(dataframe, y_col, data_name, width=900, height=500):
    """
    Crée une carte mondiale animée montrant la distribution d'une colonne de données spécifique
    à travers les pays et les années.
    
    Paramètres:
    - dataframe (DataFrame): Le dataframe d'entrée contenant les données au niveau des pays.
    - y_col (str): La colonne à visualiser sur la carte (par exemple, 'HDI')
    - data_name (str): Une étiquette pour les données visualisées (par exemple, 'IDH')
    
    Remarques:
    - Suppose que le dataframe contient les colonnes 'country_code', 'year' et la colonne y_col spécifiée.
    """
    min_value = dataframe[y_col].min()
    max_value = dataframe[y_col].max()
    # Création d'une carte du monde avec Plotly
    fig = px.choropleth(dataframe, 
                        locations='country',
                        color=y_col,
                        hover_name='country',
                        color_continuous_scale=["red", "orange","green"],
                        projection='natural earth',
                        animation_frame='date',
                        range_color=(min_value, max_value))
    fig.update_coloraxes(colorbar_title_text='')
    # Mise en page des sous-plots pour les barres d'histogramme
    fig.update_layout(
        xaxis2=dict(domain=[0, 0.45], anchor='y2'),
        xaxis3=dict(domain=[0.55, 1], anchor='y3'),
        yaxis2=dict(domain=[0, 1], anchor='x2'),
        yaxis3=dict(domain=[0, 1], anchor='x3'),
        title_text= f'{data_name} par pays, 1990-2023',
    )
    # Ajout d'un slider pour choisir l'année
    slider = go.layout.Slider(
        currentvalue=dict(prefix="Année: "),
        font=dict(size=16),
        len=0.9,
        pad=dict(t=50, b=10),
        steps=[
            {"args": [f"slider{i}.value", {"duration": 400, "frame": {"duration": 400, "redraw": True}, "mode": "immediate"}],
             "label": str(i),
             "method": "animate",
            } for i in range(1990, 2022)
        ],
    )
    fig.update_layout(
    sliders=[
        {
            "steps": [
                {"args": [[f"{date}"], {"frame": {"duration": 500, "redraw": True}, "mode": "immediate", "transition": {"duration": 500}}], "label": f"{date}", "method": "animate"} 
                for date in sorted(dataframe['date'].unique())
            ],
            "active": 0,
            "yanchor": "top",
            "xanchor": "left",
            "transition": {"duration": 300, "easing": "cubic-in-out"},
        }
    ],
    updatemenus=[{"type": "buttons", "showactive": False, "buttons": [{"label": "Play", "method": "animate", "args": [None, {"frame": {"duration": 500, "redraw": True}, "fromcurrent": True, "transition": {"duration": 300, "easing": "quadratic-in-out"}}]}]},
                 {"type": "buttons", "showactive": False, "buttons": [{"label": "Quick", "method": "animate", "args": [None, {"frame": {"duration": 0, "redraw": True}, "transition": {"duration": 0}}]}]}]
)
    fig.update_layout(
        geo=dict(
            showcoastlines=True,
            coastlinecolor="Black",
            showland=True,
            landcolor="white",
    ),
    width=width,
    height=height
)
    fig.show()

