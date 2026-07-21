from ceatw_update_pipeline.gather_sources import get_exa_sources
from ceatw_update_pipeline.database.database import init_db, kill_engine, get_session
from ceatw_update_pipeline.database.query import get_pending_sources, insert_source
import asyncio
import logging

logging.basicConfig(
    level=logging.INFO, # Set to DEBUG to see everything, INFO for normal operation
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)
    
async def test_run(country: str) -> None:
    init_db()
    with 
    kill_engine()
    
if __name__ == "__main__":
    asyncio.run(test_run("france"))