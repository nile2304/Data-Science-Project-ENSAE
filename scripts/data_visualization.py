import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.cluster import KMeans
import plotly.graph_objects as go


def plot_missing_values_per_year(data,col,text="PIB Reel"):
    """
    Plots the number of missing values per year for a specified column in a dataset.

    This function groups the dataset by the 'date' column, counts the number of
    missing values for the specified column in each year, and visualizes the result
    as a bar chart. Each bar is annotated with the exact number of missing values.

    Parameters
    ----------
    data : pandas.DataFrame
        The input DataFrame containing a 'date' column and the column to analyze.
    col : str
        The name of the column for which missing values should be counted per year.

    Returns
    -------
    None
        The function displays a matplotlib bar plot but does not return any object.
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
    Identifies and visualizes countries with an abnormal number of missing values for a given column.

    This function groups the dataset by country, counts missing values for the specified
    column, and determines which countries exceed a missing-value threshold expressed as
    a proportion of the total number of observations per country. It plots these countries
    on a bar chart with annotated values and returns their names.

    Parameters
    ----------
    data : pandas.DataFrame
        The input DataFrame containing a 'country' column and the column to analyze.
    col : str
        The name of the column for which missing values are evaluated.
    treshold : float
        A value between 0 and 1 representing the proportion of missing values above which
        a country is flagged as aberrant (e.g., 0.2 for 20%).

    Returns
    -------
    pandas.Index
        An index containing the names of all countries whose missing-value counts exceed
        the specified threshold.
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
    Plots the total world GDP over time using the provided GDP data.

    This function aggregates the GDP data by year, sums the GDP values for all countries,
    and visualizes the total world GDP as a line plot.

    Parameters
    ----------
    PIB_data : pandas.DataFrame
        A DataFrame containing 'date' and 'PIB' columns, where 'date' represents years
        and 'PIB' represents the GDP values for various countries.

    Returns
    -------
    None
        The function displays a matplotlib line plot but does not return any object.
    """

    world_PIB = PIB_data.groupby("date")["PIB"].sum()

    plt.figure(figsize=(10,6))
    plt.plot(world_PIB.index, world_PIB.values)
    plt.title("Évolution du PIB mondial (1990-2024 USD)")
    plt.xlabel("Année")
    plt.ylabel("PIB Mondial")
    plt.show()

def plot_PIB_quantile(PIB_data):

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

def plot_PIB_top_quantile_countries(PIB_data,chosen_quantile=19):

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

    print(f'Countries in the {chosen_quantile+1}th-decile: {data[data['quantiles'] == chosen_quantile]['country'].unique()}')
    
def visualize_economicPower_clusters(weightCountry_data, width=900, height=500):

    data = weightCountry_data.copy()

    kmeans = KMeans(n_clusters=4, random_state=42)
    data["Power"] = kmeans.fit_predict(data[["avgWeightCountry"]])

    cluster_order = data.groupby("Power")["avgWeightCountry"].mean().sort_values().index
    mapping = {cluster_order[0]: 0, cluster_order[1]: 1, cluster_order[2]: 2, cluster_order[3]: 3}
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

    return data

def visualize_trade_clusters(netExportators_data, width=900, height=500):

    fig = px.choropleth(
        netExportators_data,
        locations=netExportators_data["country"],
        locationmode="ISO-3",
        color="netExportateur",
        color_continuous_scale=["red", "green"],
        title="World Classification Map by Exportators Countries"
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

def visualize_landlocked_countries(landlocked_data, width=900, height=500):

    fig = px.choropleth(
        landlocked_data,
        locations=landlocked_data["country"],
        locationmode="ISO-3",
        color="isLandlocked",
        color_continuous_scale=["green", "red"],
        title="World Classification Map by Landlocked Countries"
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

def visualize_HDI_clusters(HDI_data, width=900, height=500):

    data = HDI_data.copy()

    kmeans = KMeans(n_clusters=3, random_state=42)
    data["HDI_mean"] = kmeans.fit_predict(data[["HDI_mean"]])

    cluster_order = data.groupby("HDI_mean")["HDI_mean"].mean().sort_values(ascending=False).index
    mapping = {cluster_order[0]: 0, cluster_order[1]: 1, cluster_order[2]: 2}
    data["HDI_cluster"] = data["HDI_mean"].map(mapping)

    fig = px.choropleth(
        data,
        locations="country",
        locationmode="ISO-3",
        color="HDI_cluster",
        color_continuous_scale=["red", "orange", "green"],
        title="World Classification Map by Human Development Index (HDI)"
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


def animated_economicPower_map(weightCountry_data, width=900, height=500):
    """
    Creates an animated world map showing clusters of countries based on economic power over time.

    Parameters:
    - weightCountry_data (DataFrame): The input dataframe containing 'country', 'year' and 'avgWeightCountry'.
    - width (int): Width of the map figure.
    - height (int): Height of the map figure.

    Notes:
    - Uses KMeans clustering to classify countries into 4 economic power clusters per year.
    - Displays an animated choropleth map using Plotly.
    """
    data = weightCountry_data.copy()
    
    # Calculer les clusters par année
    clustered_data = []
    for date, group in data.groupby("date"):
        kmeans = KMeans(n_clusters=4, random_state=42)
        group = group.copy()
        group["Power"] = kmeans.fit_predict(group[["weightCountry"]])
        
        # Réordonner les clusters de manière croissante
        cluster_order = group.groupby("Power")["weightCountry"].mean().sort_values().index
        mapping = {cluster_order[i]: i for i in range(4)}
        group["Power"] = group["Power"].map(mapping)
        
        clustered_data.append(group)
    
    data_clustered = pd.concat(clustered_data)
    
    # Carte animée
    fig = px.choropleth(
        data_clustered,
        locations="country",
        locationmode="ISO-3",
        color="Power",
        animation_frame="date",
        color_continuous_scale=["red", "orange", "blue", "green"],
        title="World Classification Map by Economic Power over Time",
        range_color=(0, 3)
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
    

def plot_world_map(dataframe, y_col, data_name, width=900, height=500):
    """
    Creates an animated world map showing the distribution of a specific data column across countries and years.
    Parameters:
    - dataframe (DataFrame): The input dataframe containing country-level data.
    - y_col (str): The column to be visualized on the map (e.g., 'HDI')
    - data_name (str): A label for the data being visualized (e.g., 'IDH' )
    - width (int): The width of the map figure.
    - height (int): The height of the map figure.
    Notes:
    - Assumes the dataframe has columns 'country_code', 'year', and the specified y_col.
    """
    min_value = dataframe[y_col].min()
    max_value = dataframe[y_col].max()
    # Création d'une carte du monde avec Plotly
    fig = px.choropleth(dataframe, 
                        locations='country_code',
                        color=y_col,
                        hover_name='country_code',
                        color_continuous_scale="turbo",
                        projection='natural earth',
                        animation_frame='year',
                        range_color=(min_value, max_value))
    fig.update_coloraxes(colorbar_title_text='')
    # Mise en page des sous-plots pour les barres d'histogramme
    fig.update_layout(
        xaxis2=dict(domain=[0, 0.45], anchor='y2'),
        xaxis3=dict(domain=[0.55, 1], anchor='y3'),
        yaxis2=dict(domain=[0, 1], anchor='x2'),
        yaxis3=dict(domain=[0, 1], anchor='x3'),
        title_text= f'{data_name} par pays, 1990-2021',
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
                {"args": [[f"{year}"], {"frame": {"duration": 500, "redraw": True}, "mode": "immediate", "transition": {"duration": 500}}], "label": f"{year}", "method": "animate"} 
                for year in sorted(dataframe['year'].unique())
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

