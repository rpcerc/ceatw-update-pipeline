from ceatw_update_pipeline.database.database import init_db, kill_engine, get_session
from ceatw_update_pipeline.database import query
from ceatw_update_pipeline.database.schemas import SourceCreate
from ceatw_update_pipeline.gather_sources import get_exa_sources
import asyncio
from sqlalchemy.exc import IntegrityError
import logging

logging.basicConfig(
    level=logging.INFO, # Set to DEBUG to see everything, INFO for normal operation
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)
    
async def test_run(country: str) -> None:
    await init_db()
    """
    async with get_session() as outer_session:
        async with outer_session.begin() as session:
            for source in await get_exa_sources(country):
                # https://stackoverflow.com/questions/72649194/how-to-rollback-only-the-last-session-add-action-in-sqlalchemy
                # https://docs.sqlalchemy.org/en/21/orm/session_transaction.html#using-savepoint
                try:
                    async with session.begin_nested():
                        await query.insert_source(
                            session, 
                            SourceCreate(
                                source_url=source.url,
                                country="Test Country",
                                country_code="TEST",
                                content_hash="fake_hash"
                            )
                        )
                except IntegrityError:
                    # URL already inside database
                    logger.debug("Integrity error:", exc_info=True)
                    logger.info("Country: %s - URL %s already in sources table",
                                source.country, source.url[:50]) """

    async with get_session() as session:
        updatedDB = await query.get_pending_sources(session)
        print("-----")
        print(updatedDB)
        print("-----")
        
    await kill_engine()
    input("Hi!")
    
if __name__ == "__main__":
    asyncio.run(test_run("france"))