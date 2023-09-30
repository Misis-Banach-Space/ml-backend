from typing import Any
from pydantic import BaseModel, Field


class UrlRequest(BaseModel):
    id: int = Field(...)
    url: str = Field(...)


class UrlResponse(BaseModel):
    id: int = Field(...)
    url: str = Field(...)
    stats: dict = Field(...)
    category: str = Field(...)
    theme: str = Field(...)
