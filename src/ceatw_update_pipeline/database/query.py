from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from ceatw_update_pipeline.database.models import Highlight, Source
from ceatw_update_pipeline.database.schemas import SourceCreate


# https://docs.sqlalchemy.org/en/21/orm/session_basics.html
async def insert_source_and_highlights(session: AsyncSession, data: SourceCreate) -> Source:
    """Insert a record into the source table, and highlights in the highlights table.

    Args:
        session (AsyncSession): The session relating to the database.
        data (SourceCreate): The data to insert as a pydantic object.

    Returns:
        Source: The newly inserted row.
    """
    source = Source(
        title = data.title if data.title != "" else None,
        source_url = data.source_url,
        country = data.country,
        country_code = data.country_code,
        content_hash = data.content_hash,
        comments = data.comments,
        published_date = data.published_date,
        highlights = [Highlight(text=highlight) for highlight in data.highlights]
    )
    
    session.add(source)
    await session.flush()
    
    # because of lazy loading, we only want to get the columns with server defaults, and not wipe out the children
    await session.refresh(source, attribute_names=['last_checked', 'date_created'])
    return source
