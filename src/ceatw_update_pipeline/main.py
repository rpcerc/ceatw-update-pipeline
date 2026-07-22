from ceatw_update_pipeline.database.database import init_db, kill_engine, get_session
from ceatw_update_pipeline.database import query
from ceatw_update_pipeline.database.schemas import SourceCreate
from ceatw_update_pipeline.gather_sources import get_exa_sources
from sqlalchemy.exc import IntegrityError
import asyncio

test_source = SourceCreate(
    source_url="https://example.com/",
    country= "Test Country",
    country_code= "TEST",
    content_hash= "fake_hash"
)
    
async def test_run(country: str) -> None:
    init_db()
    results = await get_exa_sources(country)
    with get_session() as session:
        for result in results:
            try:
                with session.begin_nested():
                    query.insert_source(session, 
                        SourceCreate(
                            source_url=result.url,
                            country=country,
                            country_code="TEST",
                            content_hash="fake_hash"
                        ))
            except IntegrityError:
                print("Skipped")
    
    with get_session() as session:
        updatedDB = query.get_pending_sources(session)
        print("-----")
        print(updatedDB)
        print("-----")
        
    kill_engine()
    input("Hi!")
    
if __name__ == "__main__":
    asyncio.run(test_run("france"))