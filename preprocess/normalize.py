import pandas as pd

def normalize_rating(df):
    min_rating = df["Star Rating"].min()
    max_rating = df["Star Rating"].max()

    if max_rating == min_rating:
        df["rating_norm"] = 1.0
    else:
        df["rating_norm"] = (
            (df["Star Rating"] - min_rating) /
            (max_rating - min_rating)
        )

    return df

def compute_recency(df):
    today = pd.Timestamp.today().normalize()

    df["days_since_read"] = (
        today - df["Last Date Read"]
    ).dt.days

    min_days = df["days_since_read"].min()
    max_days = df["days_since_read"].max()

    if max_days == min_days:
        df["recency_norm"] = 1.0
    else:
        df["recency_norm"] = 1 - (
            (df["days_since_read"] - min_days) /
            (max_days - min_days)
        )

    return df

def compute_score(df, rating_weight=0.7, recency_weight=0.3):
    df["score"] = (
        rating_weight * df["rating_norm"] +
        recency_weight * df["recency_norm"]
    )

    return df