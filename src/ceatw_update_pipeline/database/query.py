from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from ceatw_update_pipeline.database.models import Highlight, Source
from ceatw_update_pipeline.database.schemas import SourceCreate


def remove_null_bytes(s: str | None) -> str | None:
    return s.replace('\x00', '') if isinstance(s, str) else s

# https://docs.sqlalchemy.org/en/21/orm/session_basics.html
async def insert_source_and_highlights(session: AsyncSession, data: SourceCreate) -> Source:
    """Insert a record into the source table, and highlights in the highlights table.

    Args:
        session (AsyncSession): The session relating to the database.
        data (SourceCreate): The data to insert as a pydantic object.

    Returns:
        Source: The newly inserted row.
    """
    title_str = data.title if data.title != "" else None
    
    source = Source(
        title = remove_null_bytes(title_str),
        source_url = remove_null_bytes(data.source_url),
        country = remove_null_bytes(data.country),
        country_code = remove_null_bytes(data.country_code),
        content_hash = remove_null_bytes(data.content_hash),
        comments = remove_null_bytes(data.comments),
        published_date = data.published_date,
        highlights = [Highlight(text=highlight.replace('\x00', '')) for highlight in data.highlights if highlight]
    )
    
    session.add(source)
    await session.flush()
    
    # because of lazy loading, we only want to get the columns with server defaults, and not wipe out the children
    await session.refresh(source, attribute_names=['last_checked', 'date_created'])
    return source
