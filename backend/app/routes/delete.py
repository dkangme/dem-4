from fastapi import APIRouter, Header, HTTPException
from typing import Optional
from ..database.urls import get_url, delete_url
from ..config import settings

delete_router = APIRouter()


@delete_router.delete("/{short_code}")
async def delete_short_url(
    short_code: str,
    api_key: Optional[str] = Header(None)
):
    if api_key is None:
        raise HTTPException(status_code=401, detail="API key required")

    if api_key != settings.api_key:
        raise HTTPException(status_code=403, detail="Invalid API key")

    url_data = get_url(short_code)
    if url_data is None:
        raise HTTPException(status_code=404, detail="Short code not found")

    delete_url(short_code)

    return {"message": "URL deleted successfully"}
