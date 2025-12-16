import statsmodels.api as sm
import pandas as pd

def hedge_ratio(y, x):
    """
    y, x: pandas Series (aligned)
    returns hedge ratio (beta)
    """
    # Ensure we have at least 2 points to compute regression
    if len(y) < 2 or len(x) < 2:
        return 0  # Not enough data yet

    x_const = sm.add_constant(x)
    model = sm.OLS(y, x_const).fit()

    # Sometimes OLS fails or returns only constant
    if len(model.params) < 2:
        return 0  # Default hedge ratio
    return model.params[1]

def spread(y, x, beta):
    return y - beta * x

def zscore(series, window=30):
    mean = series.rolling(window).mean()
    std = series.rolling(window).std()
    return (series - mean) / std
