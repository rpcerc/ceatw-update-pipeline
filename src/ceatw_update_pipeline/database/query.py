import uuid
from collections.abc import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ceatw_update_pipeline.database.schemas import SourceCreate
from ceatw_update_pipeline.database.models import Source
from ceatw_update_pipeline.custom_types import Decision

async def insert_source(session: AsyncSession, data: SourceCreate) -> Source:
    """Insert a record into the source table.

    Args:
        session (AsyncSession): The session relating to the database.
        data (SourceCreate): The data to insert as a pydantic object.

    Returns:
        Source: The newly inserted row.
    """
    
    source = Source(
        source_url = data.source_url,
        country = data.country,
        country_code = data.country_code,
        content_hash = data.content_hash,
        comments = data.comments,
    )
    
    session.add(source)
    await session.flush()
    await session.refresh(source)
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

async def get_pending_sources(session: AsyncSession) -> Sequence[Source]:
    """Get all records from the source table which are still pending reviewal.

    Args:
        session (AsyncSession): The session relating to the database.

    Returns:
        Sequence[Source]: _description_
    """
    
    # is_. operator is only for None, True, False.
    query = (select(Source)
             .where(Source.decision == Decision.PENDING))
    result = await session.execute(query)
    
    return result.scalars().all()

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
