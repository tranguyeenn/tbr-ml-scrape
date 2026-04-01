import pandas as pd

from book_data import load_data, save_data


def mark_finished(title):

    df = load_data()

    df.loc[df["Title"] == title, "Read Status"] = "read"
    df.loc[df["Title"] == title, "Last Date Read"] = (
        pd.Timestamp.today().normalize()
    )

    save_data(df)
    print(f"{title} marked as finished.")


def mark_dnf(title):

    df = load_data()

    df.loc[df["Title"] == title, "Read Status"] = "dnf"

    save_data(df)
    print(f"{title} marked as DNF.")


def add_to_tbr():

    df = load_data()

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

    save_data(df)

    print(f"{new_title} added to TBR.")
