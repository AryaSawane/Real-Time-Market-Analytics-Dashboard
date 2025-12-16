def resample_ticks(df, rule):
    """
    rule examples:
    '1S' = 1 second
    '1T' = 1 minute
    '5T' = 5 minutes
    """
    if df.empty:
        return df

    resampled = df.resample(rule).agg({
        "price": "last",
        "qty": "sum"
    })

    return resampled.dropna()
