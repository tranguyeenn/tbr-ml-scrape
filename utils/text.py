import re


def normalize_text(text: str) -> str:
    """
    Lowercase, strip punctuation, normalize whitespace.
    Used for rough text matching.
    """
    if not text:
        return ""

    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()
