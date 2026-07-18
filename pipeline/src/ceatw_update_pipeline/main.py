from ceatw_update_pipeline.database.database import init_db, kill_engine, get_session
from ceatw_update_pipeline.database import query
from ceatw_update_pipeline.database.schemas import SourceCreate
from ceatw_update_pipeline.gather_sources import get_exa_sources
import asyncio

test_source = SourceCreate(
    source_url="https://example.com/",
    country= "Test Country",
    country_code= "TEST",
    content_hash= "fake_hash"
)
    
async def test_run(country: str) -> None:
    await init_db()
    async with get_session() as session:
        for source in await get_exa_sources(country):
            try:
                await query.insert_source(session, 
                    SourceCreate(
                        source_url=source.url,
                        country="Test Country",
                        country_code="TEST",
                        content_hash="fake_hash"
                    ))
            except Exception:
                continue
    
    async with get_session() as session:
        updatedDB = await query.get_pending_sources(session)
        print("-----")
        print(updatedDB)
        print("-----")
        
    await kill_engine()
    input("Hi!")
    
if __name__ == "__main__":
    asyncio.run(test_run("france"))