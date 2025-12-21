import statsmodels.api as sm
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.preprocessing import StandardScaler



def perform_regression(data, x_cols, y_col, method='HC3',plotnum=3):
    """
    Performs a multiple linear regression of y_col on x_cols.

    Parameters:
    - data (DataFrame): Input data
    - x_cols (list[str]): Independent variables
    - y_col (str): Dependent variable
    - method (str): Covariance estimator (default HC3)

    Returns:
    None
    """
    cols = x_cols + [y_col]
    data = data[cols].dropna()

    X = sm.add_constant(data[x_cols])
    y = data[y_col]

    model = sm.OLS(y, X).fit(cov_type=method)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5), gridspec_kw={'width_ratios': [6, 5]})
    ax1.text(0, 0.5, model.summary().as_text(),va='center', ha='left', fontsize=9, family='monospace')
    ax1.axis('off')
    sns.scatterplot(x=data[x_cols[plotnum]],y=y,ax=ax2,color='skyblue')
    sns.regplot(x=data[x_cols[plotnum]],y=y,scatter=False,ax=ax2,color='sandybrown')
    ax2.set_title(f'{y_col} vs {x_cols[plotnum]}')
    plt.tight_layout()
    plt.show()