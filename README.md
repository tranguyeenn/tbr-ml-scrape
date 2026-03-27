# LibroRank

LibroRank is a modular book ranking system with a flexible CSV pipeline.  
It supports user-uploaded CSV files with arbitrary schemas, maps them into canonical internal fields, runs preprocessing and scoring, and returns ranked reading recommendations.

## Highlights

- Flexible CSV ingestion with user-defined column mappings
- Validation gate with clear `accept`, `accept_with_warnings`, or `reject` outcomes
- Canonical feature pipeline: `book_id`, `title`, `author`, `genre`, `read_status`, `rating`, `last_date_read`
- Feature-aware preprocessing and normalization (works when some columns are missing)
- Modular ranking for read and to-read lists
- FastAPI backend plus a minimal Next.js frontend
- Unit tests for flexible pipeline behavior

## Project Structure

```txt
libroRank/
├── api.py
├── ingest/
│   ├── load_csv.py
│   ├── pipeline.py
│   └── mapping.example.json
├── preprocess/
│   ├── clean_books.py
│   └── normalize.py
├── ranking/
│   └── score.py
├── cli/
│   └── manage_books.py
├── test/
│   └── test_flexible_pipeline.py
├── frontend/
│   ├── app/
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── package.json
│   └── ...
└── data/
    ├── raw/
    └── processed/
```

## Flexible Pipeline Flow

1. Load raw CSV
2. Apply user mapping config (`column_mappings`)
3. Validate required canonical fields
4. Clean and coerce types
5. Normalize available features
6. Score and rank books

## Mapping Configuration

Use `ingest/mapping.example.json` as the base template.

Example:

```json
{
  "column_mappings": {
    "Book Name": "title",
    "Writer": "author",
    "Status": "read_status",
    "My Rating": "rating",
    "Finished On": "last_date_read"
  }
}
```

## Backend Setup (Python)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Run API:

```bash
uvicorn api:app --reload
```

## Frontend Setup (Next.js + TypeScript)

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

## Run the Flexible Pipeline in Code

```python
from ingest.pipeline import run_flexible_pipeline

result = run_flexible_pipeline(
    "path/to/upload.csv",
    mapping_config={
        "column_mappings": {
            "Book Name": "title",
            "Writer": "author",
            "Status": "read_status",
            "My Rating": "rating",
            "Finished On": "last_date_read"
        }
    }
)
```

## Tests

Run unit tests:

```bash
python3 -m unittest discover -s test -v
```

## License

MIT
