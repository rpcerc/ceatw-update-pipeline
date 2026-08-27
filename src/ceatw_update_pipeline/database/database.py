import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from ceatw_update_pipeline.configuration import settings

logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    """Declarative Base"""

url = settings.DATABASE_URL

if (settings.ADD_PSYCOPG_TO_URL):
    if (settings.DATABASE_URL[10] != ":"):
        logger.warning("The database url does not start with postgres://..., skipping adding +psycopg...")
    else:    
        url = settings.DATABASE_URL[:10] + "+psycopg" + settings.DATABASE_URL[10:]

# https://www.youtube.com/watch?v=u0KBmgs6jKY
async_engine = create_async_engine(
    url,
    echo=settings.DATABASE_ECHO,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True
)

AsyncSessionFactory = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autoflush=True,
    expire_on_commit=False
)

@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession]:
    """A context manager for creating async queries.

    Returns:
        AsyncGenerator[AsyncSession]:
            A wrapper to be used for queries. Returns a session when using 'with'.
            https://docs.sqlalchemy.org/en/21/orm/session_basics.html

    Yields:
        Iterator[AsyncGenerator[AsyncSession]]: 
            https://www.geeksforgeeks.org/python/context-manager-using-contextmanager-decorator/
    """
    session = AsyncSessionFactory()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
        
async def kill_engine() -> None:
    """Stops the database and all connections."""
    await async_engine.dispose()
        