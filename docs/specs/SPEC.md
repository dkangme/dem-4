# SPEC.md

## 1. TECHNOLOGY STACK
- **Python**: 3.11
- **Web framework**: FastAPI 0.104.1
- **Database**: Google Cloud Firestore (firebase-admin 6.2.0)
- **Container runtime**: Docker 24.0
- **Cloud deployment**: Google Cloud Run (fully managed)
- **CI/CD**: GitHub Actions
- **Testing**: pytest 7.4.3, httpx 0.25.0
- **Environment management**: python-dotenv 1.0.0
- **Production HTTP server**: uvicorn[standard] 0.24.0

## 2. DATA CONTRACTS

### Pydantic Models

```python
from datetime import datetime
from pydantic import BaseModel, HttpUrl, Field

class ShortenRequest(BaseModel):
    """Payload to create a shortened URL."""
    long_url: HttpUrl
    api_key: str = Field(min_length=32, max_length=64)

class ShortenResponse(BaseModel):
    """Successful creation response."""
    short_code: str
    short_url: str
    long_url: HttpUrl
    created_at: datetime

class StatsResponse(BaseModel):
    """Statistics for a short URL."""
    short_code: str
    long_url: HttpUrl
    created_at: datetime
    clicks: int
    api_key_owner: str          # masked: only first 8 chars shown
    is_owner: bool              # whether the requester owns this URL

class DeleteResponse(BaseModel):
    """Result of a successful deletion."""
    short_code: str
    message: str

class ErrorResponse(BaseModel):
    """Standard error envelope."""
    detail: str
    code: int                   # HTTP status code
```

### Firestore Document Schema (`urls` collection)
Document id = `short_code` (8‑char alphanumeric). Fields:
- `long_url`: string
- `api_key`: string
- `created_at`: timestamp (firestore.SERVER_TIMESTAMP)
- `clicks`: integer (default 0)

## 3. API ENDPOINTS

All endpoints relative to base URL (e.g., `https://short.example.com`).  
Header `Content-Type: application/json` required for POST/PUT requests.

### POST /shorten
- **Description**: Create a new short URL
- **Request body** (JSON): `ShortenRequest`
    ```json
    { "long_url": "https://example.com/very-long-url", "api_key": "aGVsbG8td29ybGQteC1zZWNyZXQtMTIzNA" }
    ```
- **Response 201**: `ShortenResponse`
    ```json
    {
        "short_code": "aB3dEf9X",
        "short_url": "https://short.example.com/aB3dEf9X",
        "long_url": "https://example.com/very-long-url",
        "created_at": "2025-03-22T10:00:00Z"
    }
    ```
- **Responses error**:
    - `422`: Validation error (invalid URL, missing fields)
    - `409`: `{ "detail": "Collision: short_code already exists (retry)", "code": 409 }`

### GET /{short_code}
- **Description**: Redirect to original URL (public, no authentication)
- **Path parameter**: `short_code` – 8 characters
- **Response 302**: Redirect to `long_url`
    - Tracking: increments click count in Firestore before redirecting.
- **Response 404**: `{ "detail": "Short URL not found", "code": 404 }`
- **Response 400**: `{ "detail": "Invalid short_code format", "code": 400 }`

### GET /stats/{short_code}
- **Description**: Retrieve click statistics and metadata. Requires ownership verification.
- **Path parameter**: `short_code`
- **Query parameter**: `api_key` (string) – the API key used during creation
- **Response 200**: `StatsResponse`
    ```json
    {
        "short_code": "aB3dEf9X",
        "long_url": "https://example.com/very-long-url",
        "created_at": "2025-03-22T10:00:00Z",
        "clicks": 42,
        "api_key_owner": "aGVsbG8t...",
        "is_owner": true
    }
    ```
- **Response 404**: Not found
- **Response 403**: `{ "detail": "Forbidden: incorrect api_key", "code": 403 }`
- **Response 401**: `{ "detail": "Missing api_key query parameter", "code": 401 }`

### DELETE /{short_code}
- **Description**: Delete a shortened URL. Requires ownership verification.
- **Path parameter**: `short_code`
- **Query parameter**: `api_key` (string)
- **Response 200**: `DeleteResponse`
    ```json
    { "short_code": "aB3dEf9X", "message": "Short URL deleted successfully" }
    ```
- **Response 404**: Not found
- **Response 403**: `{ "detail": "Forbidden: incorrect api_key", "code": 403 }`
- **Response 401**: Missing api_key

### GET /health
- **Description**: Health check (used by Cloud Run)
- **Response 200**: `{ "status": "healthy" }`

## 4. FILE STRUCTURE
```
├── backend/
│   ├── app/
│   │   ├── __init__.py               # empty
│   │   ├── main.py                   # FastAPI application instance, route inclusion, startup event
│   │   ├── models.py                 # All Pydantic request/response models
│   │   ├── routes/
│   │   │   ├── __init__.py           # empty
│   │   │   ├── shorten.py            # POST /shorten
│   │   │   ├── redirect.py           # GET /{short_code}
│   │   │   ├── stats.py              # GET /stats/{short_code}
│   │   │   └── delete.py             # DELETE /{short_code}
│   │   ├── services/
│   │   │   ├── __init__.py           # empty
│   │   │   ├── encoding.py           # short_code generator (collision‑resistant)
│   │   │   └── tracking.py           # click increment logic
│   │   ├── database/
│   │   │   ├── __init__.py           # empty
│   │   │   ├── client.py             # Firestore client singleton from environment
│   │   │   └── urls.py               # CRUD operations for urls collection
│   │   └── config.py                 # Application settings (via pydantic.BaseSettings)
│   ├── Dockerfile                    # Backend Docker image
│   └── requirements.txt              # Python dependencies
├── .env.example                      # Template for environment variables
├── .gitignore                        # Standard Python/Docker ignore rules
├── docker-compose.yml                # Local development setup (optional)
├── run.sh                            # Script to build & run containers locally
└── README.md                         # Project documentation
```

### PORT TABLE
| Service       | Listening Port | Path      |
|---------------|----------------|-----------|
| url-shortener | 8001           | backend/  |

### SHARED MODULES
No cross‑service shared modules – single service architecture.

### Deployment Files Details

- **backend/Dockerfile**:
  - `FROM python:3.11-slim`
  - `WORKDIR /app`
  - `COPY requirements.txt .`
  - `RUN pip install --no-cache-dir -r requirements.txt`
  - `COPY app/ ./app/`
  - `EXPOSE 8001`
  - `CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]`

- **docker-compose.yml**:
  Single service definition with environment file, port mapping `8001:8001`, volume mount for local development.

- **run.sh**:
  ```bash
  #!/bin/bash
  if [ -f .env ]; then
    export $(cat .env | xargs)
  fi
  docker-compose up --build
  ```

- **.env.example**:
  Contains all non‑secret environment variable names with placeholder values.

- **.gitignore**:
  Excludes `__pycache__/`, `*.pyc`, `.env`, `credentials.json`, etc.

- **README.md**:
  Project description, setup instructions, API usage examples.

## 5. ENVIRONMENT VARIABLES

| Variable                  | Type   | Description                                     | Example                          |
|---------------------------|--------|-------------------------------------------------|----------------------------------|
| `FIRESTORE_PROJECT_ID`    | string | GCP project ID for Firestore                    | `my-project-id`                  |
| `GOOGLE_APPLICATION_CREDENTIALS` | string | Path to Firestore service account JSON key | `/secrets/firestore-key.json`    |
| `BASE_URL`                | string | Public base URL of the shortener (used to build short_url) | `https://short.example.com`      |
| `SHORT_CODE_LENGTH`       | int    | Length of generated short code                  | `8`                              |
| `ENVIRONMENT`             | string | `development`, `staging`, or `production`       | `production`                     |
| `LOG_LEVEL`               | string | Logging level                                   | `info`                           |

## 6. IMPORT CONTRACTS

Each foundation file exports the following symbols:

- **`app/config.py`**
  - `from app.config import settings` → `settings` is a `pydantic.BaseSettings` instance containing all env vars.

- **`app/database/client.py`**
  - `from app.database.client import get_firestore_client` → `get_firestore_client()` returns a `google.cloud.firestore.Client` singleton.

- **`app/database/urls.py`**
  - `from app.database.urls import create_url_entry, get_url_entry, increment_clicks, delete_url_entry`
    - `create_url_entry(short_code: str, long_url: str, api_key: str) -> dict`
    - `get_url_entry(short_code: str) -> dict | None`
    - `increment_clicks(short_code: str) -> None`
    - `delete_url_entry(short_code: str) -> None`

- **`app/models.py`**
  - `from app.models import ShortenRequest, ShortenResponse, StatsResponse, DeleteResponse, ErrorResponse` (all Pydantic classes)

- **`app/services/encoding.py`**
  - `from app.services.encoding import generate_short_code` → `generate_short_code(length: int = 8) -> str` (collision‑resistant)

- **`app/services/tracking.py`**
  - `from app.services.tracking import record_click` → `record_click(short_code: str) -> None`

- **Route modules** each export their APIRouter:
  - `from app.routes.shorten import router as shorten_router`
  - `from app.routes.redirect import router as redirect_router`
  - `from app.routes.stats import router as stats_router`
  - `from app.routes.delete import router as delete_router`
  These are included in `app/main.py` via:
  ```python
  from app.routes.shorten import router as shorten_router
  app.include_router(shorten_router)
  ...
  ```

## 7. FRONTEND STATE & COMPONENT CONTRACTS
No frontend exists in this project. All interactions are via HTTP API.

## 8. FILE EXTENSION CONVENTION
- All source code files use `.py` (Python 3.11).
- Configuration files: `.env`, `Dockerfile` (no extension), `docker-compose.yml`, `run.sh`.
- Entry point: `backend/app/main.py` → FastAPI application object `app` is instantiated there and served by uvicorn.
- The Docker container starts with `uvicorn app.main:app ...`.