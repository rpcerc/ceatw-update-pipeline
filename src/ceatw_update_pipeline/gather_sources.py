"""Uses Exa.ai API to generate possible source URLs for computing curricula."""

from ceatw_update_pipeline.configuration import MAX_URL_COUNT
from ceatw_update_pipeline.get_prompt import generate_exa_payload
from ceatw_update_pipeline.custom_types import Source
from ceatw_update_pipeline.filter import is_valid_url
from exa_py import Exa
from exa_py.api import Result

def create_source(exa_result: Result) -> Source:
    """Takes a singular exa_result, and returns a Source object.

    Args:
        exa_result (Result): One result from an exa.ai call.

    Returns:
        Source: The result in a Source object form.
    """
    highlights = getattr(exa_result, "highlights", None)
    
    return {
        "url": exa_result.url,
        "title": exa_result.title,
        "published_date": getattr(exa_result, "published_date", None),
        "highlights": highlights
    }

def get_exa_sources(country: str) -> list[Source]:
    
    try:
        exa = Exa()
    except Exception as e:
        raise RuntimeError(f"Failed to initialize Exa client: {e}")
        
    intent = ("Find official primary school, kindergarten, and high school "
              f"computing or computer science curricula for {country}. "
              "Restrict to official government/education domains if possible.")
    
    payload = generate_exa_payload(intent)

    try:
        response = exa.search(
            query=payload["query"],
            type="auto",
            num_results=MAX_URL_COUNT,
            include_domains=payload.get("includeDomains"),
            contents={
                "highlights": True,
            },
        )
        
        sources = []
        for result in response.results:
            if (is_valid_url(result.url)):
                sources.append(create_source(result))
        return sources
    
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve URLs from Exa: {e}")