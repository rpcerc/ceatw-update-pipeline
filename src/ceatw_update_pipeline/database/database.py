from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from ceatw_update_pipeline.configuration import settings


class Base(DeclarativeBase):
    """Declarative Base"""

# https://www.youtube.com/watch?v=u0KBmgs6jKY
async_engine = create_async_engine(
    settings.DATABASE_URL,
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
        
async def init_db() -> None:
    """Set up the database and define mappings between models and tables."""
    async with async_engine.begin() as async_connection:
        await async_connection.run_sync(Base.metadata.create_all)
        
async def kill_engine() -> None:
    """Stops the database and all connections."""
    await async_engine.dispose()
        