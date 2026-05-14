from datetime import datetime
from pydantic import BaseModel, HttpUrl, Field

class ShortenRequest(BaseModel):
    long_url: HttpUrl
    api_key: str = Field(min_length=32, max_length=64)

class ShortenResponse(BaseModel):
    short_code: str
    short_url: str
    long_url: HttpUrl
    created_at: datetime

class StatsResponse(BaseModel):
    short_code: str
    long_url: HttpUrl
    created_at: datetime
    clicks: int
    api_key_owner: str
    is_owner: bool

class DeleteResponse(BaseModel):
    short_code: str
    message: str

class ErrorResponse(BaseModel):
    detail: str
    code: int
