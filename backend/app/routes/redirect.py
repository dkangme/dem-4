from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from ..database.urls import get_url_by_short_code
from ..services.encoding import is_valid_short_code

redirect_router = APIRouter()


@redirect_router.get("/{short_code}")
async def redirect_to_url(short_code: str):
    if not is_valid_short_code(short_code):
        raise HTTPException(status_code=400, detail="Invalid short code format")

    url_data = await get_url_by_short_code(short_code)
    if url_data is None:
        raise HTTPException(status_code=404, detail="Short URL not found")

    return RedirectResponse(url=url_data["original_url"], status_code=302)
