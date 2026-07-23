import uuid
from collections.abc import Sequence
from sqlalchemy import select
from sqlalchemy.orm import Session
from ceatw_update_pipeline.database.schemas import SourceCreate
from ceatw_update_pipeline.database.models import Source
from ceatw_update_pipeline.custom_types import Decision, Country

def insert_source(session: Session, data: SourceCreate) -> Source:
    """Insert a record into the source table.

    Args:
        session (Session): The session relating to the database.
        data (SourceCreate): The data to insert as a pydantic object.

    Returns:
        Source: The newly inserted row.
    """
    country = Country(country_code=data.country_code)
    
    source = Source(
        source_url = data.source_url,
        country = country.name,
        country_code = country.country_code,
        content_hash = data.content_hash,
        comments = data.comments,
    )
    
    session.add(source)
    session.flush()
    session.refresh(source)
    return source

def get_source(session: Session, source_id: uuid.UUID) -> Source | None:
    """Read a record in the source table via its primary key (source_id).

    Args:
        session (AsyncSession): The session relating to the database.
        source_id (uuid.UUID): The primary key for the record to get.

    Returns:
        Source | None: 
            The record with primary key source_id, or None if it does not exist.
    """
    
    return session.get(Source, source_id)

def get_pending_sources(session: Session) -> Sequence[Source]:
    """Get all records from the source table which are still pending reviewal.

    Args:
        session (Session): The session relating to the database.

    Returns:
        Sequence[Source]: _description_
    """
    
    query = (select(Source)
             .where(Source.decision == Decision.PENDING))
    result = session.execute(query)
    
    return result.scalars().all()

def delete_source(session: Session, source_id: uuid.UUID) -> bool:
    """Remove a record from the source table with primary key source_id.

    Args:
        session (Session): The session relating to the database.
        source_id (uuid.UUID): The primary key for the record to delete.

    Returns:
        bool: True if the record was successfully deleted, 
              False if no record was found with primary key source_id.
    """
    
    source = session.get(Source, source_id)
    if source is None:
        return False
    session.delete(source)
    session.flush()
    return True
