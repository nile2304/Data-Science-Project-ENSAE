import statsmodels.api as sm
import seaborn as sns
import matplotlib.pyplot as plt


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
    model = sm.OLS(y, X).fit(cov_type=method)

    # Affichage du résumé dans un subplot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6), gridspec_kw={'width_ratios': [7, 5]})
    ax1.text(0, 0.5, model.summary().as_text(), va='center', ha='left', fontsize=9, family='monospace')
    ax1.axis('off')

    # Scatter plot + régression pour une variable explicative choisie
    sns.scatterplot(x=df[x_cols[plotnum]], y=y, ax=ax2, color='skyblue', s=50)
    sns.regplot(x=df[x_cols[plotnum]], y=y, scatter=False, ax=ax2, color='sandybrown', line_kws={'lw':2})
    ax2.set_title(f'{y_col} vs {x_cols[plotnum]}')
    ax2.set_xlabel(x_cols[plotnum])
    ax2.set_ylabel(y_col)

    plt.tight_layout()
    plt.show()

    # Calcul des coefficients standardisés pour interprétation relative
    df_std = df.copy()
    for col in x_cols + [y_col]:
        df_std[col] = (df_std[col] - df_std[col].mean()) / df_std[col].std()
    X_std = sm.add_constant(df_std[x_cols])
    y_std = df_std[y_col]
    model_std = sm.OLS(y_std, X_std).fit(cov_type=method)

    print("\nCoefficients standardisés :")
    print(pd.DataFrame({'Variable': ['const'] + x_cols,
                        'Coeff_std': model_std.params.values}))

    return model