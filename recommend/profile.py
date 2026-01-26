from collections import Counter
from ingest.schema import UserBook


def select_recent_books(
    books: list[UserBook],
    max_books: int = 8,
    max_current: int = 3,
):
    """
    Select books that best represent current user taste.
    Priority:
    1. currently reading
    2. most recent reads
    """

    currently_reading = [
        b for b in books if b.status == "currently_reading"
    ]

    read_books = [
        b for b in books if b.status == "read"
    ]

    read_books = sorted(
        read_books,
        key=lambda b: b.dates or 0,
        reverse=True
    )

    selected = (
        currently_reading[:max_current]
        + read_books[: max_books - len(currently_reading)]
    )

    return selected


def build_user_profile(recent_books: list[UserBook]) -> dict:
    """
    Build a lightweight user profile from recent books.
    Output is intentionally simple.
    """

    titles = []
    authors = []

    for b in recent_books:
        titles.append(b.title.lower())
        if b.author:
            authors.append(b.author.lower())

    return {
        "titles": titles,
        "authors": authors,
    }
