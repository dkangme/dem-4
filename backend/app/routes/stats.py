from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from backend.app.database.urls import get_url_by_short_code
from backend.app.config import settings

stats_router = APIRouter()


def mask_api_key_owner(owner: str) -> str:
    if not owner:
        return ""
    if len(owner) <= 4:
        return "*" * len(owner)
    return owner[:2] + "*" * (len(owner) - 4) + owner[-2:]


@stats_router.get("/stats/{short_code}")
async def get_stats(short_code: str, api_key: str = Query(default=None)):
    if not api_key:
        return JSONResponse(status_code=401, content={"detail": "Missing api_key"})

    if api_key != settings.api_key:
        return JSONResponse(status_code=403, content={"detail": "Invalid api_key"})

    url_data = await get_url_by_short_code(short_code)
    if not url_data:
        return JSONResponse(status_code=404, content={"detail": "Short code not found"})

    owner = url_data.get("api_key_owner", "")
    masked_owner = mask_api_key_owner(owner)

    return JSONResponse(status_code=200, content={
        "short_code": short_code,
        "original_url": url_data.get("original_url"),
        "clicks": url_data.get("clicks", 0),
        "api_key_owner": masked_owner,
        "created_at": str(url_data.get("created_at", ""))
    })
