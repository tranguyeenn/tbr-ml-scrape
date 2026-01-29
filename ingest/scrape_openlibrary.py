import requests
import json
import re
from pathlib import Path
from time import sleep
from uuid import uuid4

URL = "https://openlibrary.org/search.json" 
BASE_URL = Path("data/raw/books")
BASE_URL.mkdir(parents=True, exist_ok=True)

def fetch(query: str, limit: int=25) -> list[dict]:
    params = {
        "q": query,
        "limit": limit
    }

    r = requests.get(URL, params=params, timeout=50)
    r.raise_for_status()
    return r.json().get("docs", [])

def normalize(raw: dict) -> dict:
    return {
        "book-id": str(uuid4()), 
        "title": raw.get("title"),
        "author": raw.get("author_name", []),
        "author-key": raw.get("author_key", []),
        "work-key": raw.get("key"),
        "publish-year": raw.get("first_publish_year"),
        "edition count": raw.get("edition_count"),
        "isbn": raw.get("isbn", []),
        "source": "openlibrary_search"
    }

def safe_filename(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\-]+", "_", text)
    return text[:80]

def save(book: dict) -> None:
    filename = safe_filename(f"{book['title']}_{book.get('publish-year', 'unknown')}")
    path = BASE_URL / f"{filename}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(book, f, indent=2, ensure_ascii=False)

def run(query: str, limit: int=25) -> None:
    print(f"Open Library Search: {query}")
    result = fetch(query, limit)
    print(f"Fetching {len(result)} {query} results")

    for i, raw in enumerate(result):
        books = normalize(raw)
        save(books)

        print(f"         [{i+1}/{len(result)}]: {books['title']}")
        sleep(0.15)

if __name__ == "__main__":
    query = input("Enter a genre: ")
    run(query=query, limit=25)