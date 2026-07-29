import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from ceatw_update_pipeline.custom_types import Decision, CountryCode

class SourceCreate(BaseModel):
    source_url: str
    country: str = Field(max_length=256)
    country_code: CountryCode = Field(max_length=256)
    content_hash: str
    comments: str | None = None
    
class SourceUpdate(BaseModel):
    source_url: str | None = None
    country: str | None = Field(default=None, max_length=256)
    country_code: CountryCode | None = Field(default=None, max_length=256)
    content_hash: str | None = None
    comments: str | None = None
    
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
