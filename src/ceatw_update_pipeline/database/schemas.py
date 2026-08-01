from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from ceatw_update_pipeline.custom_types import CountryCode, Decision


class SourceCreate(BaseModel):
    title: str | None = None
    source_url: str
    country: str = Field(max_length=256)
    country_code: CountryCode = Field(max_length=256)
    content_hash: str
    comments: str | None = None
    highlights: list[str] = []
    
class SourceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    source_url: str
    country: str
    country_code: CountryCode
    decision: Decision
    content_hash: str
    comments: str | None
    last_checked: datetime
    date_created: datetime
