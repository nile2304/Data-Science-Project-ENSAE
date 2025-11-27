import matplotlib.pyplot as plt

def plot_missing_values_per_year(data,col):
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
    ax1.set_title('Missing Values per Year for PIB Reel')
    ax1.set_xticks(missing_values.index)
    ax1.set_xticklabels(missing_values.index, rotation=90)
    plt.show()
    
    
def plot_missing_values_per_country(data,col,treshold):
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
    ax1.set_title('Missing Values per Country for PIB Reel')
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