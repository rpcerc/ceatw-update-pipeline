import uuid
from collections.abc import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ceatw_update_pipeline.database.schemas import SourceCreate
from ceatw_update_pipeline.database.models import Source
from ceatw_update_pipeline.custom_types import Decision

async def create_source(session: AsyncSession, data: SourceCreate) -> Source:
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
    return await session.get(Source, source_id)

async def get_pending_sources(session: AsyncSession) -> Sequence[Source]:
    query = (select(Source)
             .where(Source.decision.is_(Decision.PENDING)))
    result = await session.execute(query)
    
    return result.scalars().all()

async def delete_source(session: AsyncSession, source_id: uuid.UUID) -> bool:
    source = await session.get(Source, source_id)
    if source is None:
        return False
    await session.delete(source)
    await session.flush()
    return True
