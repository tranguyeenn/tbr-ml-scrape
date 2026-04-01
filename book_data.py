"""Shared CSV persistence for the API and CLI. No bundled library data — file is created empty on first use."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
PROCESSED_PATH = BASE_DIR / "data" / "processed" / "books.csv"

BOOKS_COLUMNS = [
    "Title",
    "Authors",
    "ISBN/UID",
    "Read Status",
    "Star Rating",
    "Last Date Read",
    "Progress (%)",
    "Pages Read",
    "Total Pages",
]


def ensure_books_file() -> None:
    if PROCESSED_PATH.exists():
        return
    PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(columns=BOOKS_COLUMNS).to_csv(PROCESSED_PATH, index=False)


def load_data() -> pd.DataFrame:
    ensure_books_file()
    df = pd.read_csv(PROCESSED_PATH)
    for col in BOOKS_COLUMNS:
        if col not in df.columns:
            df[col] = np.nan
    df = df[BOOKS_COLUMNS]
    df["Read Status"] = df["Read Status"].astype(str).str.strip().str.lower()
    df["Last Date Read"] = pd.to_datetime(df["Last Date Read"], errors="coerce")
    return df


def save_data(df: pd.DataFrame) -> None:
    ensure_books_file()
    df.to_csv(PROCESSED_PATH, index=False)
