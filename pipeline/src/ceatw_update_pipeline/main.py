from ceatw_update_pipeline.database.database import init_db, kill_engine, get_session
from ceatw_update_pipeline.database import query
from ceatw_update_pipeline.database.schemas import SourceCreate
import asyncio

test_source = SourceCreate(
    source_url="https://example.com/",
    country= "Test Country",
    country_code= "TEST",
    content_hash= "fake_hash"
)

async def check_database() -> None:
    await init_db()
    
    async with get_session() as session:
        await query.create_source(session, test_source)
        result = await query.get_pending_sources(session)
        print("-----------------------------")
        print(result)
        print("-----------------------------")
        
    await kill_engine()
    input("Hi!")

if __name__ == "__main__":
    asyncio.run(check_database())