# trade_clustering.py

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
countries = liste_pays  # exemple, à remplacer par liste complète si besoin

imports_df = wb.get_indicator("Importations", countries=countries, start=2000, end=2024)
exports_df = wb.get_indicator("Exportations", countries=countries, start=2000, end=2024)
PIB_df     = wb.get_indicator("PIB_reel", countries=countries, start=2000, end=2024)

trade_preparer = TradeDataPreparer(imports_df, exports_df, PIB_df)
analyzer = TradeDataAnalyzer(trade_preparer)

df_agg = analyzer.aggregate_by_country()
print("Données agrégées par pays :")
print(df_agg.head())

# -----------------------------------------------------------------
# Étape 2 : Standardisation
# -----------------------------------------------------------------
features = ["Balance_mean", "Ratio_mean", "Openness_mean"]
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df_agg[features])

# -----------------------------------------------------------------
# Étape 3 : Choix automatique du k optimal (silhouette)
# -----------------------------------------------------------------
k_values = range(2, 10)
silhouette_scores = {}

for k in k_values:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init="auto")
    labels = kmeans.fit_predict(X_scaled)
    score = silhouette_score(X_scaled, labels)
    silhouette_scores[k] = score

# Détermination du meilleur k
k_final = max(silhouette_scores, key=silhouette_scores.get)
print("\nScores silhouette :", silhouette_scores)
print(f"k optimal sélectionné automatiquement : {k_final}")

# -----------------------------------------------------------------
# Étape 4 : Application finale du K-Means
# -----------------------------------------------------------------
kmeans = KMeans(n_clusters=k_final, random_state=42, n_init="auto")
df_agg["Cluster"] = kmeans.fit_predict(X_scaled)

score_final = silhouette_score(X_scaled, df_agg["Cluster"])
print(f"Silhouette score final pour k={k_final} : {score_final:.3f}")

# -----------------------------------------------------------------
# Étape 5 : Visualisations
# -----------------------------------------------------------------

# 1. Méthode du coude (optionnelle mais conservée)
inertia = []
for k in k_values:
    km = KMeans(n_clusters=k, random_state=42, n_init="auto")
    km.fit(X_scaled)
    inertia.append(km.inertia_)

plt.figure(figsize=(8,5))
plt.plot(k_values, inertia, marker='o')
plt.xlabel("Nombre de clusters k")
plt.ylabel("Inertia (somme des distances intra-clusters)")
plt.title("Méthode du coude (pour comparaison)")
plt.show()

# 2. Scatter plot Balance vs Ratio
plt.figure(figsize=(8,6))
sns.scatterplot(
    data=df_agg,
    x="Balance_mean",
    y="Ratio_mean",
    hue="Cluster",
    palette="Set2",
    s=100
)
plt.title("Clusters des pays : Balance vs Ratio")
plt.show()

# 3. Scatter plot Balance vs Openness
plt.figure(figsize=(8,6))
sns.scatterplot(
    data=df_agg,
    x="Balance_mean",
    y="Openness_mean",
    hue="Cluster",
    palette="Set2",
    s=100
)
plt.title("Clusters des pays : Balance vs Ouverture commerciale")
plt.show()

# 4. Heatmap des indicateurs par cluster
df_clustered = df_agg.sort_values("Cluster")
plt.figure(figsize=(10,6))
sns.heatmap(
    df_clustered[features + ["Cluster"]],
    annot=True,
    fmt=".2f",
    cmap="coolwarm"
)
plt.title("Indicateurs commerciaux par pays et cluster")
plt.show()

# -----------------------------------------------------------------
# Étape 6 : Résumé des pays par cluster
# -----------------------------------------------------------------
for i in range(k_final):
    print(f"\nPays du cluster {i}:")
    print(df_agg[df_agg["Cluster"] == i].index.tolist())
