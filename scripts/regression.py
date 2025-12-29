import statsmodels.api as sm
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd


def perform_regression(data, x_cols, y_col, method='HC3', plotnum=0):
    """
    Effectue une régression linéaire multiple et fournit un résumé complet
    avec visualisation d'une variable explicative.

    Paramètres
    ----------
    data : pd.DataFrame
        Dataset contenant les variables explicatives et la variable expliquée.
    x_cols : list[str]
        Colonnes explicatives.
    y_col : str
        Colonne expliquée.
    method : str
        Type de covariance pour erreurs robustes ('HC3' par défaut).
    plotnum : int
        Index de la variable explicative à visualiser dans le scatter plot.

    Returns
    -------
    model : RegressionResults
        L'objet modèle ajusté de statsmodels pour analyses ultérieures.
    """

    # Préparer les données
    cols = x_cols + [y_col]
    df = data[cols].dropna().copy()

    # Matrices X et y
    X = sm.add_constant(df[x_cols])
    y = df[y_col]

    # Ajustement du modèle
    model = sm.OLS(y, X).fit(method='qr',cov_type=method)

    # Affichage des résultats
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.text(0, 0.5, model.summary().as_text(), va='top', ha='center', fontsize=10, family='monospace')
    ax.axis('off')
    plt.tight_layout()
    plt.show()



    # Calcul des coefficients standardisés pour interprétation relative
    df_std = df.copy()
    for col in x_cols:
        df_std[col] = (df_std[col] - df_std[col].mean()) / df_std[col].std()
    X_std = sm.add_constant(df_std[x_cols])
    y_std = df_std[y_col]
    model_std = sm.OLS(y_std, X_std).fit(method='qr',cov_type=method)

    print("\nCoefficients standardisés :")
    print(pd.DataFrame({'Variable': ['const'] + x_cols,
                        'Coeff_std': model_std.params.values}))

    return