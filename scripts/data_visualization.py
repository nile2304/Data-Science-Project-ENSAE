import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.cluster import KMeans


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
    
def visualize_economicPower_clusters(weightCountry_data):

    # KMeans clustering
    kmeans = KMeans(n_clusters=4, random_state=42)
    weightCountry_data["Power"] = kmeans.fit_predict(weightCountry_data[["avgWeightCountry"]])

    # Sort clusters by weight (so 3 = very high, 2 = high, 1= low, 0 = very low)
    cluster_order = weightCountry_data.groupby("Power")["avgWeightCountry"].mean().sort_values().index
    mapping = {cluster_order[0]: 0, cluster_order[1]: 1, cluster_order[2]: 2, cluster_order[3]: 3}
    weightCountry_data["Power"] = weightCountry_data["Power"].map(mapping)

    fig = px.choropleth(
        weightCountry_data,
        locations="country",
        locationmode="ISO-3",
        color="Power",
        color_continuous_scale=["red", "orange", "blue", "green"],
        title="World Classification Map by Economic Power"
    )
    fig.show()