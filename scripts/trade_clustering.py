import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

# Importer vos classes depuis vos fichiers
from data_cleaner import TradeDataPreparer
from data_analyzer import TradeDataAnalyzer
import data_collector as dc
import data_cleaner as dcl

codesISO_url = "https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes"
codesISO_data = dc.get_ISOcodes(codesISO_url)
codesISO_data = dcl.clean_ISOData(codesISO_data)
liste_pays = codesISO_data["ISO-2"].tolist()
print("Liste des pays récupérée.")

# --- Étape 1 : Récupérer les données et préparer les indicateurs ---
wb = dc.WorldBankData()
countries = liste_pays  # exemple, à remplacer par la liste complète
imports_df = wb.get_indicator("Importations", countries=countries, start=2000, end=2024)
exports_df = wb.get_indicator("Exportations", countries=countries, start=2000, end=2024)
PIB_df = wb.get_indicator("PIB_reel", countries=countries, start=2000, end=2024)

# Préparer les données
trade_preparer = TradeDataPreparer(imports_df, exports_df, PIB_df)
analyzer = TradeDataAnalyzer(trade_preparer)

# Agréger par pays : ouverture commerciale moyenne
df_agg = analyzer.aggregate_by_country()
df_agg = df_agg[["Openness_mean"]]  # on ne garde que l'ouverture commerciale

print("Ouverture commerciale moyenne par pays :")
print(df_agg.head())

# --- Étape 2 : Standardisation ---
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df_agg)

# --- Étape 3 : Choix automatique du nombre de clusters ---
sil_scores = []
k_values = range(2, min(10, len(df_agg)))  # au moins 2 clusters, max 10 ou nombre de pays
for k in k_values:
    kmeans = KMeans(n_clusters=k, random_state=42)
    labels = kmeans.fit_predict(X_scaled)
    score = silhouette_score(X_scaled, labels)
    sil_scores.append(score)

# k optimal = celui avec le meilleur score silhouette
k_final = k_values[np.argmax(sil_scores)]
print(f"Nombre optimal de clusters selon silhouette score : {k_final}")

# --- Étape 4 : Application de K-Means ---
kmeans = KMeans(n_clusters=k_final, random_state=42)
df_agg["Cluster"] = kmeans.fit_predict(X_scaled)

# --- Étape 5 : Visualisations ---
# 1. Bar plot des pays par cluster
df_sorted = df_agg.sort_values("Cluster")
plt.figure(figsize=(12,6))
sns.barplot(x=df_sorted.index, y="Openness_mean", hue="Cluster", data=df_sorted, dodge=False, palette="Set2")
plt.xticks(rotation=90)
plt.ylabel("Ouverture commerciale moyenne")
plt.title("Clustering des pays selon leur ouverture commerciale")
plt.legend(title="Cluster")
plt.show()

# 2. Heatmap
plt.figure(figsize=(10,6))
sns.heatmap(df_sorted[["Openness_mean","Cluster"]], annot=True, fmt=".2f", cmap="coolwarm")
plt.title("Openness par pays et cluster")
plt.show()

# --- Étape 6 : Résumé des pays par cluster ---
for i in range(k_final):
    print(f"\nPays du cluster {i}:")
    print(df_agg[df_agg["Cluster"] == i].index.tolist())
