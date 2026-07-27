# CDP Lite

A minimal Customer Data Platform (CDP) API built with Python. Its purpose is to centralize customer profiles, record the events they generate, and create simple segments for audience queries.

The project is designed as an educational, locally runnable MVP: it requires no external services and uses SQLite as its initial storage layer.

## MVP Scope

The first version will include:

- Customer profiles with basic data and unique identifiers.
- Events associated with each profile, such as `page_view`, `signup`, or `purchase`.
- Simple segments based on profile attributes.
- A self-documented HTTP API.
- Automated tests for the primary flows.

Authentication, real-time processing, advanced deduplication, and marketing-tool integrations are outside this MVP's scope. Those capabilities can be added once the foundation is stable.

## Proposed Architecture

```text
HTTP client
    |
    v
FastAPI (routing and validation)
    |
    v
SQLAlchemy (models and queries)
    |
    v
SQLite (cdp_lite.db)
```

The application will be organized as follows:

```text
app/
  main.py          # FastAPI application entry point
  db.py            # SQLite configuration and database sessions
  models.py        # persistence models
  schemas.py       # API request and response contracts
  routers/         # endpoints grouped by domain
tests/             # automated tests
requirements.txt   # pinned dependencies
```

## Prerequisites

- Python 3.11 or later.
- Git (optional, for version control).

Check Python with:

```powershell
py --version
```

If the command is unavailable, install Python from [python.org](https://www.python.org/downloads/) and enable the option to add Python to `PATH` during installation.

## Installation

From the repository root, create a virtual environment and install the dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

> If PowerShell prevents script activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` for the current session only, then activate the environment again.

## Running the API

Start the development server with:

```powershell
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`. Interactive documentation is available at `http://127.0.0.1:8000/docs`.

## Testing and Quality

```powershell
pytest
ruff check .
```

Tests validate the MVP use cases. Ruff keeps the code style consistent and identifies common errors before changes are pushed to the repository.

## Dependencies

Dependency versions are pinned in `requirements.txt` so every contributor installs the same library set:

- **FastAPI**: API framework.
- **Uvicorn**: ASGI server for FastAPI.
- **SQLAlchemy**: data-access layer.
- **Pydantic**: data validation and serialization.
- **Pytest + HTTPX**: endpoint testing.
- **Ruff**: static analysis and code style.

## Next Steps

1. Configure SQLite and create the customer profile model.
2. Implement profiles, events, and segments with their tests.
