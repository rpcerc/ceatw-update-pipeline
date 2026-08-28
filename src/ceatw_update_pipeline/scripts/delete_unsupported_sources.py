"""Script to delete sources from the database whose country codes are not in Datawrapper or custom codes."""
from __future__ import annotations

import asyncio
import datetime
import logging
import os
import sys

from sqlalchemy import delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ceatw_update_pipeline.configuration import (
    CUSTOM_DATAWRAPPER_CODES,
    DATAWRAPPER_CODES,
)
from ceatw_update_pipeline.database.database import get_session, kill_engine
from ceatw_update_pipeline.database.models import Highlight, Source

os.makedirs("logs", exist_ok=True)
logger_file_path = os.path.join(
    "logs",
    f"{datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d')}-devlogs.log",
)
logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(logger_file_path),
    ],
)

logger = logging.getLogger(__name__)


def get_allowed_country_codes() -> set[str]:
    """Returns the set of allowed country codes (Datawrapper codes + custom codes)."""
    return set(DATAWRAPPER_CODES) | set(CUSTOM_DATAWRAPPER_CODES.keys())


async def delete_unsupported_sources(session: AsyncSession) -> int:
    """Deletes all sources and highlights not in Datawrapper or custom country codes.

    Args:
        session (AsyncSession): The active database session.

    Returns:
        int: Number of source rows deleted.
    """
    allowed_codes = get_allowed_country_codes()

    # Query which unsupported country codes exist and their counts for logging
    unsupported_query = (
        select(Source.country_code, func.count(Source.id))
        .where(
            or_(
                Source.country_code.not_in(allowed_codes),
                Source.country_code.is_(None),
            )
        )
        .group_by(Source.country_code)
    )
    unsupported_summary = (await session.execute(unsupported_query)).all()

    if not unsupported_summary:
        logger.info("No unsupported sources found in database. Nothing to delete.")
        return 0

    logger.info("Found unsupported country records to delete:")
    for country_code, count in unsupported_summary:
        logger.info("  - Country code '%s': %d records", country_code, count)

    # Subquery for source IDs to delete
    sources_to_delete_subquery = (
        select(Source.id).where(
            or_(
                Source.country_code.not_in(allowed_codes),
                Source.country_code.is_(None),
            )
        )
    )

    # Delete child highlights first
    highlight_result = await session.execute(
        delete(Highlight).where(Highlight.source_id.in_(sources_to_delete_subquery))
    )
    logger.info("Deleted %d associated highlight records.", highlight_result.rowcount)

    # Delete parent sources
    source_result = await session.execute(
        delete(Source).where(
            or_(
                Source.country_code.not_in(allowed_codes),
                Source.country_code.is_(None),
            )
        )
    )
    deleted_count = source_result.rowcount
    logger.info("Successfully deleted %d source records.", deleted_count)
    return deleted_count


async def run() -> None:
    logger.info("Starting cleanup of unsupported country source records...")
    allowed_codes = get_allowed_country_codes()
    logger.info(
        "Allowed country codes count: %d (%d Datawrapper + %d custom)",
        len(allowed_codes),
        len(DATAWRAPPER_CODES),
        len(CUSTOM_DATAWRAPPER_CODES),
    )

    async with get_session() as session:
        await delete_unsupported_sources(session)

    await kill_engine()
    logger.info("Cleanup completed.")


if __name__ == "__main__":
    asyncio.run(run())

