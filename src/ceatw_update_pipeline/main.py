from ceatw_update_pipeline.gather_sources import get_exa_sources
import asyncio
import logging

logging.basicConfig(
    level=logging.INFO, # Set to DEBUG to see everything, INFO for normal operation
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)
    
async def test_run(country: str) -> None:
    print("hello")
    
if __name__ == "__main__":
    asyncio.run(test_run("france"))