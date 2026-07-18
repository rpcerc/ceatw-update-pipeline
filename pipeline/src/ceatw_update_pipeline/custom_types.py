from pydantic import BaseModel
from enum import StrEnum

class ExaPayload(BaseModel):
    query: str
    includeDomains: list[str] | None = None

class SearchStrategy(StrEnum):
    NATIVE = "native_prompt"
    ENGLISH = "english_prompt"
    
class SourceData(BaseModel):
    country: str
    search_strategy: str
    url: str
    title: str | None = None
    published_date: str | None = None
    highlights: list[str] | None = None
    
class Decision(StrEnum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    PENDING = "pending"