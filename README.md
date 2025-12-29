# Data-Science-Project-ENSAE

Par Saad ABDELLAOUI ANDALOUSSI MAANE & Patrick Junior HOUNKPE, 2025.

## Table des matières

- Définitions
- Objectifs
- Sources des données
- Présentation du dépôt

---

## 1. Définitions

**PIB réel :**  
Le produit intérieur brut (PIB) réel correspond à la valeur totale des biens et services produits par un pays, ajustée de l'inflation. Il reflète la croissance économique réelle d'un pays sur une période donnée.  
(Source : [Banque mondiale](https://data.worldbank.org/indicator/NY.GDP.MKTP.KD))

**Pays enclavé :**  
Un pays qui ne possède pas d’accès direct à la mer, ce qui peut limiter ses échanges commerciaux et affecter sa capacité à réagir rapidement aux chocs économiques.

**Indice de Développement Humain :**
Indice agrégé, moyenne géométrique de trois sous-indices relatifs respectivement à la santé, l'éducation et le revenu de la population. Compris entre 0 (exécrable) et 1 (excellent), les valeurs actuelles vont, en 2021, de 0,95+ (Europe du Nord) à 0,4- (certains pays d'Afrique), avec une médiane autour de 0,7.

---

## 2. Objectifs

L'objectif de ce projet est d’étudier la **vitesse de réponse aux crises financières** en fonction de certains paramètres structurels des pays, tels que :  

- La taille de l’économie dans le contexte mondial (poids économique)  
- L’état enclavé ou non du pays   
- Les échanges commerciaux (importations/exportations)  

Nous cherchons à comprendre comment ces facteurs influencent la résilience économique et la capacité d’adaptation des États face aux crises financières.

---

## 3. Sources des données

Nous nous sommes reposés de façon essentielle sur les sources suivantes :  

- Wikipédia (pour les codes ISO des pays et les pays enclavés que nous avons récupéré par scraping)
    [Codes ISO](https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes)
    [Pays enclavés](https://en.wikipedia.org/wiki/List_of_countries_by_length_of_coastline)
- API de la Banque mondiale (pour le PIB réel, les importations, les exportations)
    [Banque mondiale](https://data.worldbank.org/indicator/NY.GDP.MKTP.KD)
- United Nations Development Programme (pour l’IDH)
    [UNDP](https://hdr.undp.org/data-center/human-development-index#/indicies/HDI)

Les données sont récupérées autant que possible via les API publiques de ces sources. Et si ce n'est pas possible on stocke le dataset dans notre projet.

---

## 4. Présentation du dépôt

Notre production est essentiellement localisée dans le fichier `main.ipynb` qui a été préalablement exécutée pour présenter les résultats.

Le dossier `data/` contient une copie locale d’une partie des données pour pallier les indisponibilités d’API.  
Le dossier `scripts/` contient des fonctions utilitaires pour rendre le code plus lisible et maintenable.  
Le fichier `requirements.txt` permet l’installation des packages nécessaires via pip.  
Le dossier `ne_110m_admin_0_countries` contient des fichiers nécessaires pour l'affichage de cartes avec geopandas.

## 5. Notes sur l'utilisation

Par souci avec l'API de la WorldBank qui aléatoirement n'envoie pas des données relatives à certains pays, nous avons vu notre analyse de corrélation se rendre non reproductible. Pour la reproductibilité nous avons donc utilisé nos données backup. Toutes les analyses du document sont donc faites avec ces données backups. Pour assurer des résultats reproductibles il faut donc exécuter le notebook **HORS CONNEXION** sans quoi, les résultats varieront dû au défaut de l'API. Si l'exécution est réalisée en ligne il ne faudrait donc pas s'étonner de remarquer sur les graphiques des chiffres différents de ceux avec lesquels nous avons fait les analyses.