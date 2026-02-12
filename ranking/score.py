import numpy as np

def score_read_books(df, rating_weight=0.7, recency_weight=0.3):

    read_df = df[df["Read Status"] == "read"].copy()

    read_df["score"] = (
        rating_weight * read_df["rating_norm"] +
        recency_weight * read_df["recency_norm"]
    )

    read_df["score"] = read_df["score"].clip(0, 1)

    read_df = read_df.sort_values(
        by="score",
        ascending=False
    )

    return read_df

def score_tbr_books(df, randomness_strength=0.05, diverse_authors=True):

    read_df = df[df["Read Status"] == "read"].copy()
    tbr_df = df[df["Read Status"] == "to-read"].copy()

    # Remove duplicate books
    tbr_df = tbr_df.drop_duplicates(
        subset=["Title", "Authors"]
    )

    author_pref = (
        read_df
        .groupby("Authors")["rating_norm"]
        .mean()
        .reset_index()
    )

    author_pref.rename(
        columns={"rating_norm": "author_score"},
        inplace=True
    )

    tbr_df = tbr_df.merge(
        author_pref,
        on="Authors",
        how="left"
    )

    global_avg = read_df["rating_norm"].mean()

    tbr_df["author_score"] = (
        tbr_df["author_score"]
        .fillna(global_avg)
    )

    noise = np.random.uniform(
        -randomness_strength,
        randomness_strength,
        len(tbr_df)
    )

    tbr_df["score"] = tbr_df["author_score"] + noise

    # Keep score in clean range
    tbr_df["score"] = tbr_df["score"].clip(0, 1)

    tbr_df = tbr_df.sort_values(
        by="score",
        ascending=False
    )

    # Optional diversity: only 1 book per author
    if diverse_authors:
        tbr_df = tbr_df.drop_duplicates(
            subset=["Authors"]
        )

    return tbr_df

def recommend_one(tbr_ranked):

    if len(tbr_ranked) == 0:
        return None

    # Pick randomly from top 5
    top_slice = tbr_ranked.head(5)
    recommendation = top_slice.sample(1)

    return recommendation