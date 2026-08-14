from __future__ import annotations

import uuid

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
        highlights = [Highlight(text=highlight) for highlight in data.highlights]
    )
    
    session.add(source)
    await session.flush()
    
    # because of lazy loading, we only want to get the columns with server defaults, and not wipe out the children
    await session.refresh(source, attribute_names=['last_checked', 'date_created'])
    return source

async def get_source(session: AsyncSession, source_id: uuid.UUID) -> Source | None:
    """Read a record in the source table via its primary key (source_id).

    Args:
        session (AsyncSession): The session relating to the database.
        source_id (uuid.UUID): The primary key for the record to get.

    Returns:
        Source | None: 
            The record with primary key source_id, or None if it does not exist.
    """
    
    return await session.get(Source, source_id)

async def delete_source(session: AsyncSession, source_id: uuid.UUID) -> bool:
    """Remove a record from the source table with primary key source_id.

    Args:
        session (AsyncSession): The session relating to the database.
        source_id (uuid.UUID): The primary key for the record to delete.

    Returns:
        bool: True if the record was successfully deleted, 
              False if no record was found with primary key source_id.
    """
    
    source = await session.get(Source, source_id)
    if source is None:
        return False
    await session.delete(source)
    await session.flush()
    return True
