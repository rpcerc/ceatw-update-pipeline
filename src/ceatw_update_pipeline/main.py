"""The main entry point for the pipeline."""

import asyncio
import datetime
import json
import logging
import os
import sys

import pycountry
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from ceatw_update_pipeline.configuration import CUSTOM_DATAWRAPPER_CODES, DATAWRAPPER_CODES, settings
from ceatw_update_pipeline.custom_types import Country, CountryCode, ExaPayload
from ceatw_update_pipeline.database import query
from ceatw_update_pipeline.database.database import get_session, kill_engine
from ceatw_update_pipeline.database.schemas import SourceCreate
from ceatw_update_pipeline.gather_sources import get_exa_sources

os.makedirs("logs", exist_ok=True)
logger_file_path = os.path.join("logs", f"{datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d')}-devlogs.log")
logging.basicConfig(level=logging.WARNING, 
                    handlers=[
                        logging.StreamHandler(sys.stdout),
                        logging.FileHandler(logger_file_path)
                    ])

logger = logging.getLogger(__name__)
    
async def insert_urls_for_one_country(country_code: CountryCode, native_prompts_cache: dict[str, ExaPayload]) -> None:
    """Gather the source urls for a country, then store them in a database.

    Args:
        country_code (CountryCode): A two letter country code.
        native_prompts_cache (dict[str, ExaPayload]): 
    """
    country = Country(country_code=country_code)
    results = await get_exa_sources(country.country_code, native_prompts_cache)
    duplicate_records = 0
    async with get_session() as session:
        for result in results:
            try:
                async with session.begin_nested():
                    await query.insert_source_and_highlights(session, 
                        SourceCreate(
                            title=result.title,
                            source_url=result.url,
                            country=country.name,
                            country_code=country.country_code,
                            content_hash="fake_hash",
                            published_date=datetime.datetime.fromisoformat(result.published_date) if result.published_date else None,
                            highlights=result.highlights or [],
                        ))
            except IntegrityError:
                duplicate_records += 1
        
    logger.info("Inserted %d records for %s. Duplicate count: %d", len(results), country.name, duplicate_records)
    
async def insert_countries(
    country_codes: list[CountryCode],
    native_prompts_cache: dict[CountryCode, ExaPayload]
) -> None:
    """Insert the sources for the given country codes into the database.

    Args:
        country_codes (list[CountryCode]): A list of country codes.
        native_prompts_cache (dict[CountryCode, ExaPayload]): The native prompts cache.
    """

    batch_size = int((settings.EXA_API_LIMIT-1)/2)
    logger.info("Inserting %d countries in batches of %d...", len(country_codes), batch_size)
    
    for i in range(0, len(country_codes), batch_size):
        current_batch = country_codes[i:i+batch_size]
        tasks = [insert_urls_for_one_country(cc, native_prompts_cache)
                 for cc in current_batch]
        
        # This is quite prone to breaking, due to API rate limits seemingly being lower than written.
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        for res in batch_results:
            if isinstance(res, Exception):
                logger.error("A country task failed in the batch: %s", res)
        
        logger.info("Batch finished, sleeping for 1s")
        
        await asyncio.sleep(1)
        
    logger.info("%d countries inserted successfully", len(country_codes)) 

    
    
def load_native_prompts_cache() -> dict[CountryCode, ExaPayload]:
    """Read the prompts cache from the file path given in the configuration file.

    Returns:
        dict[CountryCode, ExaPayload]: The native prompts cache.
    """
    prompts_cache: dict[CountryCode, ExaPayload] = {}
    try:
        with open(settings.NATIVE_LANGUAGE_PROMPTS_FILE, "r") as f:
            raw_json = json.load(f)
            for country_code, payload_dict in raw_json.items():
                prompts_cache[country_code] = ExaPayload.model_validate(payload_dict)
                
    except (json.JSONDecodeError, FileNotFoundError, ValidationError):
        logger.exception("Cache failed to load:")
    
    return prompts_cache

def add_custom_countries() -> None:
    for code, name in CUSTOM_DATAWRAPPER_CODES.items():
        pycountry.countries.add_entry(alpha_2=code, name=name)

async def run_pipeline() -> None:
    logger.info("Starting pipeline...")
    native_prompts_cache = load_native_prompts_cache()
    add_custom_countries()
    await insert_countries(DATAWRAPPER_CODES + list(CUSTOM_DATAWRAPPER_CODES.keys()),
                           native_prompts_cache)
    await kill_engine()
    
    
if __name__ == "__main__":
    asyncio.run(run_pipeline())