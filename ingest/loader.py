from .goodreads import parse_goodreads

def load_user_books(path: str):
    if path.endswith(".csv"):
        return parse_goodreads(path)

    raise ValueError("Unsupported file format")
