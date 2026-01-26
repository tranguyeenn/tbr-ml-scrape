from utils.text import normalize_text


def score_book(book: dict, user_profile: dict) -> float:
    score = 0.0

    # --- USER SIGNALS ---
    user_titles = user_profile["titles"]
    user_authors = user_profile["authors"]

    # --- BOOK FIELDS ---
    title = normalize_text(book.get("title", ""))
    author = normalize_text(book.get("author", ""))
    description = normalize_text(book.get("description", ""))

    genres = book.get("genres") or []
    genres = [normalize_text(g) for g in genres]

    if "children" in genres:
        score -= 2.0

    for g in genres:
        if g in {"philosophical", "psychological", "literary"}:
            score += 2.0

    # --- GENRE MATCH (PRIMARY) ---
    for g in genres:
        for ut in user_titles:
            if g and g in ut:
                score += 3.0

    # --- DESCRIPTION KEYWORD MATCH ---
    for ut in user_titles:
        for word in ut.split():
            if len(word) > 4 and word in description:
                score += 1.0

    # --- AUTHOR AFFINITY (WEAK) ---
    for ua in user_authors:
        if ua and ua in author:
            score += 0.5

    return score


def rank_books(
    books: list[dict],
    user_profile: dict,
    exclude_titles: set[str],
    top_k: int = 10,
):
    scored = []

    for book in books:
        title = book.get("title", "")
        if not title:
            continue

        if title.lower() in exclude_titles:
            continue

        s = score_book(book, user_profile)
        if s > 0:
            scored.append((s, book))

    # Sort by score
    scored.sort(key=lambda x: x[0], reverse=True)

    if scored:
        return [b for _, b in scored[:top_k]]

    # --- FALLBACK: POPULAR CLASSICS ---
    fallback = [
        b for b in books
        if b.get("title", "").lower() not in exclude_titles
    ]

    fallback.sort(
        key=lambda b: b.get("edition_count") or 0,
        reverse=True
    )

    return fallback[:top_k]