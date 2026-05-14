# DEVELOPMENT PLAN: DEM 4 — URL Shortener Microservice

## 1. ARCHITECTURE OVERVIEW
- **Stack**: Python 3.11, FastAPI, Google Cloud Firestore (firebase-admin), Docker, Google Cloud Run, GitHub Actions.
- **Service**: Single backend service (`backend/`) running on port 8001.
- **Database**: Firestore in spark tier, collection `urls`, document ID = `short_code`.
- **Components**:
  - `config.py` – environment validation (pydantic.BaseSettings).
  - `models.py` – Pydantic request/response models (ShortenRequest, ShortenResponse, StatsResponse, DeleteResponse, ErrorResponse).
  - `database/` – Firestore client singleton and CRUD operations (`client.py`, `urls.py`).
  - `services/` – Short code generator (`encoding.py`) and click increment logic (`tracking.py`).
  - `routes/` – Four APIRouter modules: `shorten.py`, `redirect.py`, `stats.py`, `delete.py`.
  - `main.py` – FastAPI instance, registers routers, health endpoint, startup event.
- **Data Contracts** (strictly per SPEC.md):
  - `ShortenRequest { long_url: HttpUrl, api_key: str }`
  - `ShortenResponse { short_code, short_url, long_url, created_at }`
  - `StatsResponse { short_code, long_url, created_at, clicks, api_key_owner, is_owner }`
  - `DeleteResponse { short_code, message }`
  - `ErrorResponse { detail, code }`
- **Endpoints** (all as defined in SPEC.md §3):
  - `POST /shorten` – creates short URL (collision‑resistant, stores in Firestore).
  - `GET /{short_code}` – 302 redirect, increments click count.
  - `GET /stats/{short_code}?api_key=...` – returns stats if api_key matches.
  - `DELETE /{short_code}?api_key=...` – deletes entry if api_key matches.
  - `GET /health` – returns `{ "status": "healthy" }`.

## 2. ACCEPTANCE CRITERIA
1. POST /shorten with a valid URL and api_key returns 201 with a short_code, short_url, and created_at timestamp.
2. GET /{short_code} redirects to the original URL with 302 and increments click count in Firestore; unknown codes return 404.
3. GET /stats/{short_code}?api_key=correct returns 200 with correct click count and is_owner=true; missing/wrong api_key returns 401/403.
4. DELETE /{short_code}?api_key=correct returns 200 and removes the document; wrong api_key returns 403.
5. The entire system runs locally via `./run.sh` (Docker Compose), all endpoints respond correctly, and `GET /health` returns healthy status.

## TEAM SCOPE
- `role-tl` (technical_lead) – defines shared contracts, config, and database layer.
- `role-be` (backend_developer) – implements business logic (routes, services).
- `role-devops` (devops_support) – containerisation, CI/CD scaffolding, local orchestration.

## 3. EXECUTABLE ITEMS

### ITEM 1: Foundation — shared types, configuration, database, and utility modules
**Goal:** Create all modules that other items will import: config, Pydantic models, Firestore client, CRUD operations, short‑code generator, click recording. These are the building blocks for the API endpoints.
**Files to create:**
- `backend/app/__init__.py` (create) – empty.
- `backend/app/config.py` (create) – `pydantic.BaseSettings` instance `settings` validating all environment variables.
- `backend/app/models.py` (create) – all Pydantic models: `ShortenRequest`, `ShortenResponse`, `StatsResponse`, `DeleteResponse`, `ErrorResponse`.
- `backend/app/services/__init__.py` (create) – empty.
- `backend/app/services/encoding.py` (create) – `generate_short_code(length: int = 8) -> str` (collision‑resistant).
- `backend/app/services/tracking.py` (create) – `record_click(short_code: str) -> None`.
- `backend/app/database/__init__.py` (create) – empty.
- `backend/app/database/client.py` (create) – `get_firestore_client() -> google.cloud.firestore.Client` singleton.
- `backend/app/database/urls.py` (create) – CRUD functions: `create_url_entry`, `get_url_entry`, `increment_clicks`, `delete_url_entry`.
**Tests required:** (none – SPEC.md §4 does not permit test files; validation via curl in deployment)
**Dependencies:** None
**Validation:** From `backend/`, run `python -c "from app.config import settings; print(settings.BASE_URL)"` – must print the configured BASE_URL.
**Role:** role-tl (technical_lead)

### ITEM 2: Shorten endpoint — POST /shorten
**Goal:** Implement the route that generates and stores a new short URL. Accepts `ShortenRequest` JSON, generates a unique `short_code` via `generate_short_code`, stores document in Firestore, and returns `ShortenResponse`.
**Files to create:**
- `backend/app/routes/__init__.py` (create) – empty.
- `backend/app/routes/shorten.py` (create) – exports `router as shorten_router` with `POST /shorten`.
**Dependencies:** Item 1 (Foundation)
**Validation:** `curl -X POST http://localhost:8001/shorten -H "Content-Type: application/json" -d '{"long_url":"https://example.com/very-long-path","api_key":"aGVsbG8td29ybGQteC1zZWNyZXQtMTIzNA"}'` → 201 with `short_code`, `short_url`.
**Role:** role-be (backend_developer)

### ITEM 3: Redirect endpoint — GET /{short_code}
**Goal:** Implement the public redirect route. Looks up the short code in Firestore, increments the click counter using `record_click`, and returns a 302 redirect to the stored `long_url`. Handles 404 for unknown codes.
**Files to create:**
- `backend/app/routes/redirect.py` (create) – exports `router as redirect_router` with `GET /{short_code}`.
**Dependencies:** Item 1 (Foundation)
**Validation:** After creating a short code with Item 2, `curl -i http://localhost:8001/<short_code>` → 302 with `Location` header set to original URL; second request increments clicks (visible via stats later).
**Role:** role-be (backend_developer)

### ITEM 4: Stats endpoint — GET /stats/{short_code}
**Goal:** Implement metadata & statistics retrieval. Requires `api_key` query parameter; if missing → 401, if incorrect → 403. On success returns `StatsResponse` with click count, creation date, masked owner key, and `is_owner` always `true`.
**Files to create:**
- `backend/app/routes/stats.py` (create) – exports `router as stats_router` with `GET /stats/{short_code}`.
**Dependencies:** Item 1 (Foundation)
**Validation:** `curl "http://localhost:8001/stats/<short_code>?api_key=correct_key"` → 200 with `clicks`, `api_key_owner` (masked), `is_owner: true`. Omitting `api_key` → 401; wrong key → 403.
**Role:** role-be (backend_developer)

### ITEM 5: Delete endpoint — DELETE /{short_code}
**Goal:** Implement deletion of a shortened URL. Requires `api_key` query parameter, verifies ownership (matching stored key), and removes document from Firestore. Returns `DeleteResponse`.
**Files to create:**
- `backend/app/routes/delete.py` (create) – exports `router as delete_router` with `DELETE /{short_code}`.
**Dependencies:** Item 1 (Foundation)
**Validation:** `curl -X DELETE "http://localhost:8001/<short_code>?api_key=correct_key"` → 200 `{"short_code":"...","message":"Short URL deleted successfully"}`. Wrong key → 403. Missing key → 401.
**Role:** role-be (backend_developer)

### ITEM 6: Infrastructure & Deployment
**Goal:** Provide a fully integrated, locally runnable environment with zero manual steps. Includes FastAPI app entry point (`main.py`), Dockerfile, Docker Compose, and all supporting files. The app starts with all four API endpoints and a health check.
**Files to create:**
- `backend/app/main.py` (create) – FastAPI instance, includes all routers (`shorten_router`, `redirect_router`, `stats_router`, `delete_router`), `GET /health`, startup event.
- `backend/Dockerfile` (create) – Python 3.11-slim, multi-stage, non‑root, exposes 8001, CMD `uvicorn src.main:app --host 0.0.0.0 --port 8001` (build context `./backend`).
- `docker-compose.yml` (create) – single service `url-shortener`, port mapping `8001:8001`, healthcheck, environment file.
- `.env.example` (create) – template with all required variables and descriptions.
- `.gitignore` (create) – excludes Python artifacts, `.env`, credentials.
- `run.sh` (create) – validates Docker, loads `.env`, runs `docker-compose up --build`, waits for health, prints access URL.
- `README.md` (create) – project description, setup instructions, curl examples for all endpoints.
**Dependencies:** Items 1–5 (all business logic)
**Validation:** `chmod +x run.sh && ./run.sh` → after build, `curl http://localhost:8001/health` returns `{"status":"healthy"}`; all API endpoints respond correctly per manual smoke tests.
**Role:** role-devops (devops_support)
**CRITICAL:** Clone repository → `./run.sh` → fully working app at `http://localhost:8001`.