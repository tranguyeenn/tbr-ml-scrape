from pathlib import Path
import pandas as pd

from ingest.load_csv import load_csv
from preprocess.clean_books import clean_books
from preprocess.normalize import normalize_rating, compute_recency
from ranking.score import score_read_books, score_tbr_books, recommend_one


RAW_PATH = Path("data/raw/storyGraph_export.csv")
PROCESSED_PATH = Path("data/processed/books.csv")

if PROCESSED_PATH.exists():
    df = pd.read_csv(PROCESSED_PATH)
    df["Last Date Read"] = pd.to_datetime(df["Last Date Read"], errors="coerce")
else:
    df = load_csv(RAW_PATH)
    df = clean_books(df)
    df.to_csv(PROCESSED_PATH, index=False)

print("\nWhat would you like to do?")
print("1 - Smart recommendation")
print("2 - Mark book as finished")
print("3 - Mark book as DNF")
print("4 - Add book to TBR")
print("5 - Exit")

choice = input("Enter choice: ")

if choice == "1":

    df = normalize_rating(df)
    df = compute_recency(df)

    read_ranked = score_read_books(df)
    tbr_ranked = score_tbr_books(df)

    print("\nTop Read Books:")
    print(read_ranked[["Title", "score"]].head(5))

    print("\nRecommended From TBR:")
    print(tbr_ranked[["Title", "Authors", "score"]].head(5))

    recommendation = recommend_one(tbr_ranked)

    print("\nTonight You Read:")
    print(recommendation[["Title", "Authors", "score"]])

elif choice == "2":

    title = input("Enter exact book title: ")

    today = pd.Timestamp.today().normalize()

    df.loc[df["Title"] == title, "Read Status"] = "read"
    df.loc[df["Title"] == title, "Last Date Read"] = today

    print(f"{title} marked as finished on {today.date()}.")

    df.to_csv(PROCESSED_PATH, index=False)

elif choice == "3":

    title = input("Enter exact book title: ")

    today = pd.Timestamp.today().normalize()

    df.loc[df["Title"] == title, "Read Status"] = "dnf"
    df.loc[df["Title"] == title, "Last Date Read"] = today

    print(f"{title} marked as DNF on {today.date()}.")

    df.to_csv(PROCESSED_PATH, index=False)

elif choice == "4":

    new_title = input("Enter book title: ")
    new_author = input("Enter author: ")

    new_row = {
        "Title": new_title,
        "Authors": new_author,
        "ISBN/UID": str(pd.Timestamp.now().timestamp()),
        "Read Status": "to-read",
        "Star Rating": None,
        "Last Date Read": None
    }

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    df.to_csv(PROCESSED_PATH, index=False)

    print(f"{new_title} added to TBR.")


else:
    print("Goodbye.")
