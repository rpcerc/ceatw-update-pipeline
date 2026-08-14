from __future__ import annotations

from pydantic import BaseModel, Field

from ceatw_update_pipeline.custom_types import CountryCode


class SourceCreate(BaseModel):
    # Essentially a type.
    title: str | None = None
    source_url: str
    country: str
    country_code: CountryCode = Field(max_length=256)
    content_hash: str
    comments: str | None = None
    highlights: list[str] = []
