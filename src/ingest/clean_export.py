import pandas as pd
from pathlib import Path

PATH = Path("data/raw/sample_export.csv")

def clean_export(path):
    df = pd.read_csv(path)

    #normalize blank and turn it into NA
    df = df.replace(r"^\s*$", pd.NA, regex=True)

    #clean columns
    df.columns = (df.columns.str.strip().str.lower().str.replace(" ", "_"))

    #clean author
    df["author"] = (df["author"].str.strip().str.title())

    #clean my_rating
    df["my_rating"] = pd.to_numeric(df["my_rating"], errors="coerce")

    #clean avg_rating
    df["average_rating"] = pd.to_numeric(df["average_rating"], errors="coerce")

    #clean publisher
    df["publisher"] = (df["publisher"].str.strip().str.title())

    #clean binding
    df["binding"] = (df["binding"].str.strip().str.title())

    #clean year_published
    df["year_published"] = (pd.to_numeric(df["year_published"], errors="coerce").astype("Int64"))

    #clean original_pub_yr
    df["original_publication_year"] = (pd.to_numeric(df["original_publication_year"], errors="coerce").astype("Int64"))

    #clean date_read
    df["date_read"] = pd.to_datetime(df["date_read"], errors="coerce")

    #clean date_added
    df["date_added"] = pd.to_datetime(df["date_added"], errors="coerce")
    
    #clean shelves
    df["shelves"] = (df["shelves"].str.strip().str.title())

    #clean bookshelves
    df["bookshelves"] = (df["bookshelves"].str.strip().str.title())

    #clean review
    df = df.drop(columns=["my_review"], errors="ignore")
    
    return df

clean_export(PATH)