from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from ceatw_update_pipeline.configuration import settings


class Base(DeclarativeBase):
    """Declarative Base"""

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True
)

SessionFactory = sessionmaker(
    bind=engine,
    autoflush=True,
    expire_on_commit=False
)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """A context manager for creating synchronous queries.

    Returns:
        Generator[Session, None, None]:
            A wrapper to be used for queries. Returns a session when using 'with'.
            https://docs.sqlalchemy.org/en/20/orm/session_basics.html
    """
    session = SessionFactory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db() -> None:
    """Set up the database and define mappings between models and tables."""
    # This import is needed to let SQLAlchemy know these models exist, even if it is unused.
    import ceatw_update_pipeline.database.models as models # noqa: F401
    Base.metadata.create_all(bind=engine)


def kill_engine() -> None:
    """Stops the database and all connections."""
    engine.dispose()