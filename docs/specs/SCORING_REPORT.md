# SCORING REPORT

## 1. RESULTADO GLOBAL

**Weighted Total Score: 28 / 100**

| Item | Description | Declared Files | Present | Missing | Critical Bugs | Score |
|------|-------------|---------------|---------|---------|---------------|-------|
| 1 | Foundation — config, models, DB, services | 9 | 6 | 3 (`__init__.py` ×3) | 0 | 70 |
| 2 | Shorten endpoint — POST /shorten | 2 | 1 | 1 (`routes/__init__.py`) | 3 | 40 |
| 3 | Redirect endpoint — GET /{short_code} | 1 | 0 | 1 (`redirect.py`) | — | 10 |
| 4 | Stats endpoint — GET /stats/{short_code} | 1 | 0 | 1 (`stats.py`) | — | 10 |
| 5 | Delete endpoint — DELETE /{short_code} | 1 | 0 | 1 (`delete.py`) | — | 10 |
| 6 | Infrastructure & Deployment | 7 | 0 | 7 | — | 0 |

> **Note:** Items 3–5 are partially implemented inside `shorten.py` (wrong file, wrong router names, wrong module structure), but the declared separate files do not exist. Item 6 is entirely absent. The app cannot start at all (`main.py` is missing).

---

## 2. SCORING POR ITEM

---

### ITEM 1 — Foundation (score: 70/100)

| File | Status | Notes |
|------|--------|-------|
| `backend/app/__init__.py` | ❌ Missing | Not in FILE TREE; Python package marker absent |
| `backend/app/config.py` | ✅ Exists | Correct `BaseSettings` usage, all env vars present |
| `backend/app/models.py` | ✅ Exists | All five models present, field names match SPEC |
| `backend/app/services/__init__.py` | ❌ Missing | Not in FILE TREE |
| `backend/app/services/encoding.py` | ✅ Exists | `generate_short_code` correct |
| `backend/app/services/tracking.py` | ✅ Exists | `record_click` delegates to `increment_clicks` correctly |
| `backend/app/database/__init__.py` | ❌ Missing | Not in FILE TREE |
| `backend/app/database/client.py` | ✅ Exists | Singleton pattern correct |
| `backend/app/database/urls.py` | ✅ Exists | All four CRUD functions present |

**Bugs found:**

- `backend/app/database/urls.py` line 3: `from google.cloud.firestore import Increment` — `Increment` is not a top-level export of `google.cloud.firestore`; the correct import is `from google.cloud.firestore import firestore` and then `firestore.Increment`, or `from google.cloud.firestore_v1 import Increment`. This will raise `ImportError` at startup. **−15 pts**
- Three `__init__.py` files missing (non-critical in Python 3 namespace packages but required by plan). **−5 pts each × 3 = −15 pts** (capped at −10 for non-critical)

**Penalty: −25 pts → Score: 70/100**

---

### ITEM 2 — Shorten endpoint (score: 40/100)

| File | Status | Notes |
|------|--------|-------|
| `backend/app/routes/__init__.py` | ❌ Missing | Not in FILE TREE |
| `backend/app/routes/shorten.py` | ⚠️ Exists with problems | See bugs below |

**Bugs found:**

1. **Wrong router variable name** (`shorten.py` line 10): The plan and SPEC require the router to be exported as `shorten_router` (for import in `main.py`). The file exports `router`, not `shorten_router`. Any `main.py` that follows the plan will fail to import `shorten_router`. **−10 pts**

2. **All four endpoints crammed into one file** (`shorten.py` lines 10–120): The redirect, stats, and delete routes are all defined inside `shorten.py` instead of their own dedicated files (`redirect.py`, `stats.py`, `delete.py`). This violates the architecture and means Items 3–5 declared files are absent.

3. **Stats endpoint returns 400 instead of 401 for missing api_key** (`shorten.py` line 77): `return JSONResponse(status_code=400, ...)` — SPEC §3 and API_CONTRACT require HTTP 401 when `api_key` is absent. **−10 pts**

4. **Delete endpoint returns 400 instead of 401 for missing api_key** (`shorten.py` line 103): Same issue as above. **−10 pts**

5. **`api_key_owner` is not masked** (`shorten.py` line 88): The full `api_key` is returned in `api_key_owner`. SPEC §2 states "masked: only first 8 chars shown" and API_CONTRACT shows `"aGVsbG8t..."`. **−5 pts**

6. **Health endpoint returns `{"status": "ok"}` not `{"status": "healthy"}`** (`shorten.py` line 120): SPEC §3 and API_CONTRACT require `"healthy"`. **−5 pts**

7. **`created_at` conversion uses non-existent method** (`shorten.py` line 36): `entry['created_at'].to_datetime()` — Firestore `DatetimeWithNanoseconds` does not have a `.to_datetime()` method; the object itself is already a `datetime`. This will raise `AttributeError` at runtime when `hasattr` returns `True` (it won't, so the fallback is used — but the logic is fragile and wrong). Minor risk but still a bug.

**Penalty: −60 pts → Score: 40/100**

---

### ITEM 3 — Redirect endpoint (score: 10/100)

| File | Status | Notes |
|------|--------|-------|
| `backend/app/routes/redirect.py` | ❌ Missing | Not in FILE TREE |

The redirect logic exists inside `shorten.py` but the declared file `redirect.py` with `redirect_router` does not exist. `main.py` (also missing) cannot import `redirect_router` from the correct module.

**Penalty: −90 pts → Score: 10/100**

---

### ITEM 4 — Stats endpoint (score: 10/100)

| File | Status | Notes |
|------|--------|-------|
| `backend/app/routes/stats.py` | ❌ Missing | Not in FILE TREE |

Stats logic exists inside `shorten.py` but with bugs (wrong 400 vs 401, unmasked `api_key_owner`). The declared file `stats.py` with `stats_router` does not exist.

**Penalty: −90 pts → Score: 10/100**

---

### ITEM 5 — Delete endpoint (score: 10/100)

| File | Status | Notes |
|------|--------|-------|
| `backend/app/routes/delete.py` | ❌ Missing | Not in FILE TREE |

Delete logic exists inside `shorten.py` but with bugs (wrong 400 vs 401). The declared file `delete.py` with `delete_router` does not exist.

**Penalty: −90 pts → Score: 10/100**

---

### ITEM 6 — Infrastructure & Deployment (score: 0/100)

| File | Status | Notes |
|------|--------|-------|
| `backend/app/main.py` | ❌ Missing | Not in FILE TREE — app cannot start |
| `backend/Dockerfile` | ❌ Missing | Not in FILE TREE — cannot containerise |
| `docker-compose.yml` | ❌ Missing | Not in FILE TREE — `./run.sh` cannot work |
| `.env.example` | ❌ Missing | Not in FILE TREE |
| `.gitignore` | ❌ Missing | Not in FILE TREE |
| `run.sh` | ❌ Missing | Not in FILE TREE |
| `README.md` | ❌ Missing | Not in FILE TREE |

All seven files for Item 6 are absent. The application cannot be started in any form.

**Penalty: −100 pts → Score: 0/100**

---

## 3. PROBLEMAS CRÍTICOS BLOQUEANTES

| # | Problem | File:Line | Impact | Item |
|---|---------|-----------|--------|------|
| 1 | `backend/app/main.py` does not exist — FastAPI app entry point absent | `backend/app/main.py` (missing) | App cannot start at all | 6 |
| 2 | `backend/Dockerfile` does not exist — cannot build container image | `backend/Dockerfile` (missing) | `docker compose up` fails immediately | 6 |
| 3 | `docker-compose.yml` does not exist — no orchestration | `docker-compose.yml` (missing) | `./run.sh` cannot execute | 6 |
| 4 | `run.sh` does not exist — entry point for local execution absent | `run.sh` (missing) | Acceptance Criteria 5 fails entirely | 6 |
| 5 | `from google.cloud.firestore import Increment` — `Increment` is not exported at this path | `backend/app/database/urls.py:3` | `ImportError` at startup; all DB writes fail | 1 |
| 6 | `backend/app/routes/redirect.py` missing — `redirect_router` cannot be imported | `backend/app/routes/redirect.py` (missing) | Redirect endpoint unavailable | 3 |
| 7 | `backend/app/routes/stats.py` missing — `stats_router` cannot be imported | `backend/app/routes/stats.py` (missing) | Stats endpoint unavailable | 4 |
| 8 | `backend/app/routes/delete.py` missing — `delete_router` cannot be imported | `backend/app/routes/delete.py` (missing) | Delete endpoint unavailable | 5 |
| 9 | Router exported as `router` not `shorten_router` — import in `main.py` will fail | `backend/app/routes/shorten.py:10` | `ImportError` when `main.py` does `from app.routes.shorten import shorten_router` | 2 |
| 10 | Stats/Delete return HTTP 400 for missing `api_key` instead of required 401 | `backend/app/routes/shorten.py:77,103` | Breaks Acceptance Criteria 3 & 4; API contract violation | 4, 5 |
| 11 | Health endpoint returns `{"status": "ok"}` instead of `{"status": "healthy"}` | `backend/app/routes/shorten.py:120` | Breaks Acceptance Criteria 5; Cloud Run health check fails | 6 |
| 12 | `requirements.txt` missing `uvicorn`, `python-dotenv`, `pydantic-settings` | `requirements.txt` | Container build produces non-runnable image | 6 |

---

## 4. VERIFICACIÓN DE ACCEPTANCE CRITERIA

| AC | Description | Status | Explanation |
|----|-------------|--------|-------------|
| AC1 | POST /shorten returns 201 with short_code, short_url, created_at | ⚠️ Partial | Route logic exists in `shorten.py` but `main.py` is missing so the app cannot start; also `Increment` import bug blocks DB layer |
| AC2 | GET /{short_code} redirects 302, increments clicks, 404 for unknown | ❌ Fail | `redirect.py` missing; `main.py` missing; `Increment` import bug; app cannot start |
| AC3 | GET /stats returns 200 with clicks/is_owner=true; 401 for missing key; 403 for wrong key | ❌ Fail | `stats.py` missing; missing `api_key` returns 400 not 401; `api_key_owner` not masked; app cannot start |
| AC4 | DELETE returns 200 and removes document; 403 for wrong key | ❌ Fail | `delete.py` missing; missing `api_key` returns 400 not 401; app cannot start |
| AC5 | System runs via `./run.sh`, all endpoints respond, `/health` returns healthy | ❌ Fail | `run.sh`, `docker-compose.yml`, `Dockerfile`, `main.py` all missing; health returns `"ok"` not `"healthy"` |

---

## 5. ARCHIVOS FALTANTES

| File | Criticality | Reason |
|------|-------------|--------|
| `backend/app/main.py` | 🔴 CRÍTICO | FastAPI application entry point; without it the app cannot start |
| `backend/Dockerfile` | 🔴 CRÍTICO | Required to build the container image |
| `docker-compose.yml` | 🔴 CRÍTICO | Required for `./run.sh` and local orchestration |
| `run.sh` | 🔴 CRÍTICO | Acceptance Criteria 5 explicitly requires `./run.sh` |
| `backend/app/routes/redirect.py` | 🔴 CRÍTICO | Declared in plan; `redirect_router` must be importable from here |
| `backend/app/routes/stats.py` | 🔴 CRÍTICO | Declared in plan; `stats_router` must be importable from here |
| `backend/app/routes/delete.py` | 🔴 CRÍTICO | Declared in plan; `delete_router` must be importable from here |
| `backend/app/routes/__init__.py` | 🟡 MEDIO | Package marker for routes module |
| `backend/app/__init__.py` | 🟡 MEDIO | Package marker for app module |
| `backend/app/services/__init__.py` | 🟡 MEDIO | Package marker for services module |
| `backend/app/database/__init__.py` | 🟡 MEDIO | Package marker for database module |
| `.env.example` | 🟡 MEDIO | Required by plan; needed for onboarding |
| `.gitignore` | 🟢 BAJO | Good practice; declared in plan |
| `README.md` | 🟢 BAJO | Documentation; declared in plan |

---

## 6. RECOMENDACIONES DE ACCIÓN

### 🔴 CRÍTICO — Create `backend/app/main.py`

```python
from fastapi import FastAPI
from app.routes.shorten import shorten_router
from app.routes.redirect import redirect_router
from app.routes.stats import stats_router
from app.routes.delete import delete_router

app = FastAPI(title="URL Shortener")

app.include_router(shorten_router)
app.include_router(redirect_router)
app.include_router(stats_router)
app.include_router(delete_router)

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

---

### 🔴 CRÍTICO — Fix `Increment` import in `backend/app/database/urls.py` (line 3)

Replace:
```python
from google.cloud.firestore import Increment
```
With:
```python
from google.cloud.firestore_v1 import Increment
```
Or alternatively use the `ArrayUnion`/`Increment` sentinel via:
```python
from google.cloud.firestore import firestore as fs_module
# then use: fs_module.Increment(1)
```

---

### 🔴 CRÍTICO — Create `backend/app/routes/redirect.py`

```python
from fastapi import APIRouter
from fastapi.responses import RedirectResponse, JSONResponse
from app.database.urls import get_url_entry
from app.services.tracking import record_click
from app.config import settings

redirect_router = APIRouter()

@redirect_router.get("/{short_code}")
async def redirect_short_url(short_code: str):
    if len(short_code) != settings.SHORT_CODE_LENGTH:
        return JSONResponse(status_code=400, content={"detail": "Invalid short_code format", "code": 400})
    entry = get_url_entry(short_code)
    if not entry:
        return JSONResponse(status_code=404, content={"detail": "Short URL not found", "code": 404})
    record_click(short_code)
    return RedirectResponse(url=entry["long_url"], status_code=302)
```

---

### 🔴 CRÍTICO — Create `backend/app/routes/stats.py`

```python
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from typing import Optional
from app.database.urls import get_url_entry
from app.models import StatsResponse
from app.config import settings

stats_router = APIRouter()

@stats_router.get("/stats/{short_code}", response_model=StatsResponse)
async def get_stats(short_code: str, api_key: Optional[str] = None):
    if not api_key:
        return JSONResponse(status_code=401, content={"detail": "Missing api_key query parameter", "code": 401})
    entry = get_url_entry(short_code)
    if not entry:
        return JSONResponse(status_code=404, content={"detail": "Short URL not found", "code": 404})
    if entry.get("api_key") != api_key:
        return JSONResponse(status_code=403, content={"detail": "Forbidden: incorrect api_key", "code": 403})
    masked = entry["api_key"][:8] + "..."
    return StatsResponse(
        short_code=short_code,
        long_url=entry["long_url"],
        created_at=entry["created_at"],
        clicks=entry.get("clicks", 0),
        api_key_owner=masked,
        is_owner=True,
    )
```

---

### 🔴 CRÍTICO — Create `backend/app/routes/delete.py`

```python
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from typing import Optional
from app.database.urls import get_url_entry, delete_url_entry
from app.models import DeleteResponse
from app.config import settings

delete_router = APIRouter()

@delete_router.delete("/{short_code}", response_model=DeleteResponse)
async def delete_short_url(short_code: str, api_key: Optional[str] = None):
    if not api_key:
        return JSONResponse(status_code=401, content={"detail": "Missing api_key query parameter", "code": 401})
    entry = get_url_entry(short_code)
    if not entry:
        return JSONResponse(status_code=404, content={"detail": "Short URL not found", "code": 404})
    if entry.get("api_key") != api_key:
        return JSONResponse(status_code=403, content={"detail": "Forbidden: incorrect api_key", "code": 403})
    delete_url_entry(short_code)
    return DeleteResponse(short_code=short_code, message="Short URL deleted successfully")
```

---

### 🔴 CRÍTICO — Create `backend/Dockerfile`

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ ./app/
EXPOSE 8001
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

---

### 🔴 CRÍTICO — Create `docker-compose.yml`

```yaml
version: "3.9"
services:
  url-shortener:
    build:
      context: ./backend
    ports:
      - "8001:8001"
    env_file:
      - .env
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 10s
      timeout: 5s
      retries: 5
```

---

### 🔴 CRÍTICO — Create `run.sh`

```bash
#!/bin/bash
set -e
if [ -f .env ]; then
  export $(cat .env | grep -v '^#' | xargs)
fi
docker-compose up --build
```

---

### 🔴 CRÍTICO — Rename router variable in `backend/app/routes/shorten.py` (line 10)

Change:
```python
router = APIRouter()
```
To:
```python
shorten_router = APIRouter()
```
And update all `@router.` decorators to `@shorten_router.` within that file. Remove the redirect/stats/delete routes from this file once the dedicated files are created.

---

### 🔴 CRÍTICO — Fix `requirements.txt` — add missing dependencies

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic-settings>=2.0.0
firebase-admin==6.2.0
google-api-core>=2.0.0
google-cloud-firestore>=2.0.0
python-dotenv==1.0.0
```

> `uvicorn` is the server; `pydantic-settings` is required for `BaseSettings` in Pydantic v2; `python-dotenv` is required for `.env` loading.

---

### 🟠 ALTO — Fix health endpoint response in `backend/app/routes/shorten.py` (line 120)

Change:
```python
return {"status": "ok"}
```
To:
```python
return {"status": "healthy"}
```

---

### 🟠 ALTO — Fix missing `api_key` response codes in `shorten.py` (lines 77, 103)

Both stats and delete handlers return `status_code=400` for missing `api_key`. Change both to `status_code=401` per SPEC §3 and API_CONTRACT.

---

### 🟡 MEDIO — Mask `api_key_owner` in stats response (`shorten.py` line 88)

Change:
```python
api_key_owner=entry.get("api_key", ""),
```
To:
```python
api_key_owner=entry.get("api_key", "")[:8] + "...",
```

---

### 🟡 MEDIO — Create all missing `__init__.py` package markers

Create empty files:
- `backend/app/__init__.py`
- `backend/app/routes/__init__.py`
- `backend/app/services/__init__.py`
- `backend/app/database/__init__.py`

---

### 🟢 BAJO — Create `.env.example`, `.gitignore`, `README.md`

These are declared in Item 6 and needed for project completeness and onboarding.

---

## MACHINE_READABLE_ISSUES
```json
[
  {
    "severity": "critical",
    "files": ["backend/app/main.py"],
    "description": "main.py does not exist — FastAPI application entry point is absent, app cannot start",
    "fix_hint": "Create backend/app/main.py with FastAPI instance, include shorten_router, redirect_router, stats_router, delete_router, and GET /health returning {\"status\": \"healthy\"}"
  },
  {
    "severity": "critical",
    "files": ["backend/Dockerfile"],
    "description": "Dockerfile does not exist — container image cannot be built",
    "fix_hint": "Create backend/Dockerfile: FROM python:3.11-slim, WORKDIR /app, COPY requirements.txt ., RUN pip install, COPY app/ ./app/, EXPOSE 8001, CMD [\"uvicorn\", \"app.main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8001\"]"
  },
  {
    "severity": "critical",
    "files": ["docker-compose.yml"],
    "description": "docker-compose.yml does not exist — local orchestration impossible, run.sh cannot work",
    "fix_hint": "Create docker-compose.yml with service url-shortener, build context ./backend, port 8001:8001, env_file .env, and healthcheck on /health"
  },
  {
    "severity": "critical",
    "files": ["run.sh"],
    "description": "run.sh does not exist — Acceptance Criteria 5 cannot be satisfied",
    "fix_hint": "Create run.sh: load .env with export $(cat .env | grep -v '^#' | xargs), then docker-compose up --build"
  },
  {
    "severity": "critical",
    "files": ["backend/app/routes/redirect.py"],
    "description": "redirect.py does not exist — redirect_router cannot be imported by main.py",
    "fix_hint": "Create backend/app/routes/redirect.py exporting redirect_router with GET /{short_code} returning 302 redirect, 404 for unknown, 400 for invalid format"
  },
  {
    "severity": "critical",
    "files": ["backend/app/routes/stats.py"],
    "description": "stats.py does not exist — stats_router cannot be imported by main.py",
    "fix_hint": "Create backend/app/routes/stats.py exporting stats_router with GET /stats/{short_code}, returning 401 for missing api_key, 403 for wrong key, 200 with masked api_key_owner"
  },
  {
    "severity": "critical",
    "files": ["backend/app/routes/delete.py"],
    "description": "delete.py does not exist — delete_router cannot be imported by main.py",
    "fix_hint": "Create backend/app/routes/delete.py exporting delete_router with DELETE /{short_code}, returning 401 for missing api_key, 403 for wrong key, 200 on success"
  },
  {
    "severity": "critical",
    "files": ["backend/app/database/urls.py"],
    "description": "Line 3: 'from google.cloud.firestore import Increment' — Increment is not exported at this path, causes ImportError at startup",
    "fix_hint": "Change to 'from google.cloud.firestore_v1 import Increment' or use 'from google.cloud.firestore import firestore as fs; fs.Increment(1)'"
  },
  {
    "severity": "critical",
    "files": ["backend/app/routes/shorten.py"],
    "description": "Line 10: router exported as 'router' not 'shorten_router' — main.py import of shorten_router will fail with ImportError",
    "fix_hint": "Rename 'router = APIRouter()' to 'shorten_router = APIRouter()' and update all @router. decorator references to @shorten_router."
  },
  {
    "severity": "critical",
    "files": ["requirements.txt"],
    "description": "requirements.txt missing uvicorn, pydantic-settings, and python-dotenv — container will build but app will not start",
    "fix_hint": "Add: uvicorn[standard]==0.24.0, pydantic-settings>=2.0.0, python-dotenv==1.0.0 to requirements.txt"
  },
  {
    "severity": "critical",
    "files": ["backend/app/routes/shorten.py"],
    "description": "Lines 77 and 103: missing api_key returns HTTP 400 instead of required HTTP 401 for stats and delete endpoints",
    "fix_hint": "Change status_code=400 to status_code=401 and update detail message to 'Missing api_key query parameter' in both stats and delete handlers"
  },
  {
    "severity": "critical",
    "files": ["backend/app/routes/shorten.py"],
    "description": "Line 120: health endpoint returns {\"status\": \"ok\"} instead of {\"status\": \"healthy\"} — Cloud Run health check will fail",
    "fix_hint": "Change return value to {\"status\": \"healthy\"}"
  }
]
```