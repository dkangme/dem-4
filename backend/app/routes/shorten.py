from fastapi import APIRouter, HTTPException, status, Request, Response
from fastapi.responses import RedirectResponse, JSONResponse
from app.config import settings
from app.models import ShortenRequest, ShortenResponse, ErrorResponse, StatsResponse, DeleteResponse
from app.services.encoding import generate_short_code
from app.database.urls import create_url_entry, get_url_entry, increment_clicks, delete_url_entry
from typing import Optional
from datetime import datetime

shorten_router = APIRouter()

class ConflictError(Exception):
    pass

@shorten_router.post(
    "/shorten",
    response_model=ShortenResponse,
    status_code=status.HTTP_201_CREATED,
    responses={409: {"model": ErrorResponse}, 422: {"model": ErrorResponse}}
)
async def create_short_url(request: ShortenRequest):
    max_attempts = 5
    for _ in range(max_attempts):
        code = generate_short_code(settings.SHORT_CODE_LENGTH)
        try:
            create_url_entry(code, str(request.long_url), request.api_key)
            entry = get_url_entry(code)
            if not entry:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to retrieve created entry"
                )
            created_at = entry['created_at'].to_datetime() if hasattr(
                entry['created_at'], 'to_datetime'
            ) else entry['created_at']
            short_url = f"{settings.BASE_URL}/{code}"
            return ShortenResponse(
                short_code=code,
                short_url=short_url,
                long_url=request.long_url,
                created_at=created_at
            )
        except HTTPException:
            raise
        except Exception as e:
            err_str = str(e).lower()
            if 'conflict' in err_str or 'already exists' in err_str or 'duplicate' in err_str or 'unique' in err_str:
                continue
            raise
    raise HTTPException(
        status_code=409,
        detail="Collision: short_code already exists (retry)"
    )

@shorten_router.get(
    "/{short_code}",
    responses={
        302: {"description": "Redirect to original URL"},
        404: {"model": ErrorResponse},
        400: {"model": ErrorResponse}
    }
)
async def redirect_short_url(short_code: str):
    if len(short_code) != settings.SHORT_CODE_LENGTH:
        return JSONResponse(status_code=400, content={"detail": "Invalid short_code format", "code": 400})
    entry = get_url_entry(short_code)
    if not entry:
        return JSONResponse(status_code=404, content={"detail": "Short URL not found", "code": 404})
    increment_clicks(short_code)
    return RedirectResponse(url=entry["long_url"], status_code=302)

@shorten_router.get(
    "/stats/{short_code}",
    response_model=StatsResponse,
    responses={
        200: {"model": StatsResponse},
        404: {"model": ErrorResponse},
        400: {"model": ErrorResponse},
        403: {"model": ErrorResponse}
    }
)
async def get_stats(short_code: str, api_key: Optional[str] = None):
    if len(short_code) != settings.SHORT_CODE_LENGTH:
        return JSONResponse(status_code=400, content={"detail": "Invalid short_code format", "code": 400})
    if not api_key:
        return JSONResponse(status_code=401, content={"detail": "Missing api_key query parameter", "code": 401})
    entry = get_url_entry(short_code)
    if not entry:
        return JSONResponse(status_code=404, content={"detail": "Short URL not found", "code": 404})
    is_owner = (entry.get("api_key") == api_key)
    if not is_owner:
        return JSONResponse(status_code=403, content={"detail": "Forbidden: not the owner", "code": 403})
    created_at = entry['created_at'].to_datetime() if hasattr(entry['created_at'], 'to_datetime') else entry['created_at']
    return StatsResponse(
        short_code=short_code,
        long_url=entry["long_url"],
        created_at=created_at,
        clicks=entry.get("clicks", 0),
        api_key_owner=entry.get("api_key", ""),
        is_owner=is_owner
    )

@shorten_router.delete(
    "/{short_code}",
    response_model=DeleteResponse,
    responses={
        200: {"model": DeleteResponse},
        404: {"model": ErrorResponse},
        400: {"model": ErrorResponse},
        403: {"model": ErrorResponse}
    }
)
async def delete_short_url(short_code: str, api_key: Optional[str] = None):
    if len(short_code) != settings.SHORT_CODE_LENGTH:
        return JSONResponse(status_code=400, content={"detail": "Invalid short_code format", "code": 400})
    if not api_key:
        return JSONResponse(status_code=401, content={"detail": "Missing api_key query parameter", "code": 401})
    entry = get_url_entry(short_code)
    if not entry:
        return JSONResponse(status_code=404, content={"detail": "Short URL not found", "code": 404})
    is_owner = (entry.get("api_key") == api_key)
    if not is_owner:
        return JSONResponse(status_code=403, content={"detail": "Forbidden: not the owner", "code": 403})
    delete_url_entry(short_code)
    return DeleteResponse(short_code=short_code, message="Short URL deleted successfully")

@shorten_router.get("/health")
async def health():
    return {"status": "healthy"}
