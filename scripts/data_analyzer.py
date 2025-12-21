import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import data_collector as dc
import data_cleaner as dcl



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

