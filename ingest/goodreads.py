import csv
from datetime import datetime
from .schema import UserBook

DATE_FMT = "%Y/%m/%d"

def parse_goodreads(path: str) -> list[UserBook]:
    books = []

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            shelf = row.get("Exclusive Shelf", "").lower()
            if shelf not in {"read", "currently-reading"}:
                continue

            title = row.get("Title", "").strip()
            author = row.get("Author", "").strip() or None

            date_str = row.get("Date Read", "") or row.get("Date Added", "")
            date = None
            if date_str:
                try:
                    date = datetime.strptime(date_str, DATE_FMT)
                except ValueError:
                    pass

            books.append(
                UserBook(
                    title=title,
                    author=author,
                    status="currently_reading" if shelf == "currently-reading" else "read",
                    dates=date
                )
            )

    return books