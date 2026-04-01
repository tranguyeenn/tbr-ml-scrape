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
- Frontend API proxy routes for stable backend connectivity
- Unit tests for flexible pipeline and API endpoints

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
│   ├── test_api.py
│   └── test_flexible_pipeline.py
├── frontend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── books/route.ts
│   │   │   └── recommend/route.ts
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── package.json
│   └── ...
└── data/
    ├── raw/          # optional: place your own CSV exports here (gitignored)
    └── processed/    # books.csv is gitignored; created empty on first API/CLI use
```

The API does not ship with a sample library. On first run it creates `data/processed/books.csv` with the correct headers and no rows. Use the ingest pipeline or the app to add books.

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

Next.js proxy routes (`/api/books`, `/api/recommend`) call the backend URL from `frontend/lib/backendUrl.ts`. **Local development defaults to `http://127.0.0.1:8000`** so you use your own `data/processed/books.csv` (empty until you add books). Run `uvicorn` in another terminal.

Only create `frontend/.env.local` when you need to override that, for example:

```bash
# Point the UI at a deployed API (you will see that server’s library, not your local file)
API_BASE_URL=https://your-api.example.com
```

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

## Frontend Features

- Shelves (Want to read, Currently reading, Read, DNF) from `GET /books`
- Add book (`POST /books`), edit / move shelves (`PATCH /books`), remove (`DELETE /books?title=…`)
- CSV import tab (`POST /books/import`) — maps Title / Authors / Total pages columns
- Next-read suggestion (`GET /recommend` via proxy)

Batch CSV ingestion for the canonical pipeline is also available in Python (`ingest/`).

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
./venv/bin/python -m unittest discover -s test -v
```

## License

MIT
