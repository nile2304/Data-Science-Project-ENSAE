import matplotlib.pyplot as plt

def plot_missing_values_per_year(data,col):
    
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