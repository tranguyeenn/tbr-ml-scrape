import json
from pathlib import Path

from ingest.loader import load_user_books
from recommend.profile import select_recent_books, build_user_profile
from recommend.rank import rank_books


DATA_DIR = Path("data")
PROCESSED_BOOKS = DATA_DIR / "processed" / "books.json"


def load_corpus():
    if not PROCESSED_BOOKS.exists():
        raise FileNotFoundError(
            f"Processed books not found at {PROCESSED_BOOKS}"
        )

    with open(PROCESSED_BOOKS, encoding="utf-8") as f:
        return json.load(f)


def main():
    print("📚 TBR Recommender")
    print("-" * 40)

    path = input("Path to Goodreads CSV: ").strip()
    if not path:
        print("No file provided. Exiting.")
        return

    # 1. Load user books
    user_books = load_user_books(path)
    if not user_books:
        print("No usable books found in file.")
        return

    # 2. Select recent reads
    recent = select_recent_books(user_books)

    print("\nRecent reads detected:")
    for b in recent:
        print(f"• {b.title} ({b.status})")

    # 3. Build user profile
    user_profile = build_user_profile(recent)

    # Titles to exclude from recommendations
    exclude_titles = {b.title.lower() for b in recent if b.title}

    # 4. Load Open Library corpus
    corpus = load_corpus()

    # 5. Rank books
    recommendations = rank_books(
        books=corpus,
        user_profile=user_profile,
        exclude_titles=exclude_titles,
        top_k=10
    )

    # 6. Output
    print("\nRecommended reads:")
    print("-" * 40)

    if not recommendations:
        print("No recommendations found. (Yes, that’s information.)")
        return

    for i, book in enumerate(recommendations, 1):
        print(f"{i}. {book.get('title')}")
        author = book.get("author")
        if author:
            print(f"   Author: {author}")
        print()


if __name__ == "__main__":
    main()
