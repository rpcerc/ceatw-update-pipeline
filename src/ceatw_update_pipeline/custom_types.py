from typing import TypedDict, NotRequired

class ExaPayload(TypedDict):
    query: str
    includeDomains: NotRequired[list[str]]
    
    
class Source(TypedDict):
    url: str
    title: str | None
    published_date: str | None
    highlights: list[str] | None
    