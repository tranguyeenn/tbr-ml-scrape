from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np

from book_data import load_data, save_data
from preprocess.normalize import normalize_rating, compute_recency
from ranking.score import score_tbr_books, recommend_one


app = FastAPI(title="LibroRank API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def clean_for_json(df):
    return df.replace({np.nan: None})


def parse_date_or_today(date_str):
    try:
        return pd.to_datetime(date_str) if date_str else pd.Timestamp.today().normalize()
    except Exception:
        return pd.Timestamp.today().normalize()


class AddBook(BaseModel):
    title: str
    author: str
    total_pages: int | None = None


class UpdateProgress(BaseModel):
    title: str
    pages_read: int
    total_pages: int | None = None


class FinishBook(BaseModel):
    title: str
    rating: float
    date: str | None = None


class DNFBook(BaseModel):
    title: str
    date: str | None = None


class PatchBook(BaseModel):
    """Update fields and/or move between shelves. `title` identifies the row."""

    title: str
    new_title: str | None = None
    author: str | None = None
    total_pages: int | None = None
    pages_read: int | None = None
    move_to: str | None = None  # want | reading | read | dnf
    rating: float | None = None
    date_read: str | None = None


class ImportRow(BaseModel):
    title: str
    author: str | None = None
    total_pages: int | None = None


class ImportBooks(BaseModel):
    books: list[ImportRow]


class RemoveBook(BaseModel):
    title: str


def _delete_book_by_title(title: str) -> dict:
    df = load_data()
    if title not in df["Title"].values:
        raise HTTPException(status_code=404, detail="Book not found")
    df = df[df["Title"] != title].copy()
    save_data(df)
    return {"message": "Book deleted"}


@app.get("/books")
def get_books():
    df = load_data()
    df = clean_for_json(df)
    return df.to_dict(orient="records")


@app.post("/books")
def add_book(book: AddBook):
    df = load_data()

    new_row = {
        "Title": book.title,
        "Authors": book.author,
        "ISBN/UID": str(pd.Timestamp.now().timestamp()),
        "Read Status": "to-read",
        "Star Rating": np.nan,
        "Last Date Read": None,
        "Progress (%)": 0,
        "Pages Read": 0,
        "Total Pages": book.total_pages
    }

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    save_data(df)

    return {"message": "Book added"}


@app.delete("/books")
def delete_book(title: str = Query(..., min_length=1)):
    return _delete_book_by_title(title)


@app.post("/books/remove")
def remove_book(body: RemoveBook):
    """Same as DELETE /books — POST avoids 405 from proxies that block DELETE."""
    t = body.title.strip()
    if not t:
        raise HTTPException(status_code=400, detail="title is required")
    return _delete_book_by_title(t)


@app.patch("/books")
def patch_book(p: PatchBook):
    df = load_data()

    if p.title not in df["Title"].values:
        raise HTTPException(status_code=404, detail="Book not found")

    if p.new_title is not None and p.new_title != p.title:
        if p.new_title in df["Title"].values:
            raise HTTPException(status_code=400, detail="A book with that title already exists")
        df.loc[df["Title"] == p.title, "Title"] = p.new_title

    key = p.new_title if p.new_title else p.title
    row = df["Title"] == key

    if p.author is not None:
        df.loc[row, "Authors"] = p.author
    if p.total_pages is not None:
        df.loc[row, "Total Pages"] = p.total_pages

    if p.move_to is not None:
        m = p.move_to.strip().lower()
        if m == "want":
            df.loc[row, "Read Status"] = "to-read"
            df.loc[row, "Progress (%)"] = 0
            df.loc[row, "Pages Read"] = 0
        elif m == "reading":
            tp = df.loc[row, "Total Pages"].values[0]
            if pd.isna(tp) or not tp or float(tp) <= 0:
                raise HTTPException(status_code=400, detail="Set total pages before moving to currently reading")
            tp = int(float(tp))
            pr = p.pages_read if p.pages_read is not None else 1
            pr = max(1, min(int(pr), tp))
            df.loc[row, "Read Status"] = "to-read"
            df.loc[row, "Pages Read"] = pr
            df.loc[row, "Progress (%)"] = round((pr / tp) * 100, 2)
        elif m == "read":
            rating = p.rating
            if rating is None:
                existing = df.loc[row, "Star Rating"].values[0]
                rating = float(existing) if pd.notna(existing) else None
            if rating is None or not (1 <= rating <= 5):
                raise HTTPException(status_code=400, detail="Rating 1–5 required when marking as read")
            df.loc[row, "Read Status"] = "read"
            df.loc[row, "Star Rating"] = rating
            df.loc[row, "Progress (%)"] = 100
            tp = df.loc[row, "Total Pages"].values[0]
            if pd.notna(tp) and float(tp) > 0:
                df.loc[row, "Pages Read"] = int(float(tp))
            df.loc[row, "Last Date Read"] = parse_date_or_today(p.date_read)
        elif m == "dnf":
            df.loc[row, "Read Status"] = "dnf"
            df.loc[row, "Star Rating"] = 1
            df.loc[row, "Progress (%)"] = 0
            df.loc[row, "Pages Read"] = 0
            df.loc[row, "Last Date Read"] = parse_date_or_today(p.date_read)
        else:
            raise HTTPException(status_code=400, detail="move_to must be want, reading, read, or dnf")
    elif p.pages_read is not None:
        tp = df.loc[row, "Total Pages"].values[0]
        if pd.isna(tp) or not tp or float(tp) <= 0:
            raise HTTPException(status_code=400, detail="Total pages not set")
        tp = int(float(tp))
        pr = min(int(p.pages_read), tp)
        df.loc[row, "Pages Read"] = pr
        df.loc[row, "Progress (%)"] = round((pr / tp) * 100, 2)
        df.loc[row, "Read Status"] = "to-read"
    elif p.rating is not None:
        rs = str(df.loc[row, "Read Status"].iloc[0]).lower()
        if rs != "read":
            raise HTTPException(status_code=400, detail="Rating can only be updated on finished books")
        if not (1 <= p.rating <= 5):
            raise HTTPException(status_code=400, detail="Rating must be 1–5")
        df.loc[row, "Star Rating"] = p.rating

    save_data(df)
    return {"message": "Book updated"}


@app.post("/books/import")
def import_books(data: ImportBooks):
    df = load_data()
    imported = 0
    skipped = 0
    for book in data.books:
        if not book.title or not book.title.strip():
            skipped += 1
            continue
        t = book.title.strip()
        if t in df["Title"].values:
            skipped += 1
            continue
        new_row = {
            "Title": t,
            "Authors": (book.author or "").strip() or "Unknown",
            "ISBN/UID": str(pd.Timestamp.now().timestamp()) + f"_{imported}",
            "Read Status": "to-read",
            "Star Rating": np.nan,
            "Last Date Read": None,
            "Progress (%)": 0,
            "Pages Read": 0,
            "Total Pages": book.total_pages,
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        imported += 1
    save_data(df)
    return {"imported": imported, "skipped": skipped}


@app.patch("/books/progress")
def update_progress(update: UpdateProgress):
    df = load_data()

    if update.title not in df["Title"].values:
        raise HTTPException(status_code=404, detail="Book not found")

    if update.total_pages:
        df.loc[df["Title"] == update.title, "Total Pages"] = update.total_pages

    total_pages = df.loc[df["Title"] == update.title, "Total Pages"].values[0]

    if not total_pages:
        raise HTTPException(status_code=400, detail="Total pages not set")

    pages_read = min(update.pages_read, total_pages)
    progress = round((pages_read / total_pages) * 100, 2)

    df.loc[df["Title"] == update.title, "Pages Read"] = pages_read
    df.loc[df["Title"] == update.title, "Progress (%)"] = progress

    save_data(df)

    return {"progress": progress}


@app.patch("/books/finish")
def finish_book(data: FinishBook):
    df = load_data()

    if data.title not in df["Title"].values:
        raise HTTPException(status_code=404, detail="Book not found")

    if not (1 <= data.rating <= 5):
        raise HTTPException(status_code=400, detail="Rating must be 1-5")

    date = parse_date_or_today(data.date)

    df.loc[df["Title"] == data.title, "Read Status"] = "read"
    df.loc[df["Title"] == data.title, "Star Rating"] = data.rating
    df.loc[df["Title"] == data.title, "Progress (%)"] = 100
    df.loc[df["Title"] == data.title, "Last Date Read"] = date

    save_data(df)

    return {"message": "Book marked as finished"}


@app.patch("/books/dnf")
def dnf_book(data: DNFBook):
    df = load_data()

    if data.title not in df["Title"].values:
        raise HTTPException(status_code=404, detail="Book not found")

    date = parse_date_or_today(data.date)

    df.loc[df["Title"] == data.title, "Read Status"] = "dnf"
    df.loc[df["Title"] == data.title, "Star Rating"] = 1
    df.loc[df["Title"] == data.title, "Progress (%)"] = 0
    df.loc[df["Title"] == data.title, "Last Date Read"] = date

    save_data(df)

    return {"message": "Book marked as DNF"}


@app.get("/recommend")
def recommend():
    df = load_data()

    df = normalize_rating(df)
    df = compute_recency(df)

    tbr_ranked = score_tbr_books(df)
    recommendation = recommend_one(tbr_ranked)

    if recommendation is None or len(recommendation) == 0:
        return []

    recommendation = clean_for_json(recommendation)

    return recommendation.to_dict(orient="records")