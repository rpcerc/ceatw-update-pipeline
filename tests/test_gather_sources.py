from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ceatw_update_pipeline.configuration import GENERIC_TLD_DOMAINS, settings
from ceatw_update_pipeline.custom_types import Country, ExaPayload
from ceatw_update_pipeline.gather_sources import (
    get_exa_sources,
    get_prompt_from_cache,
    get_relevant_tlds,
)

COUNTRIES = [
    "JP",
    "DE",
    "ZW",
]

def test_get_relevant_tlds():
    assert (set(get_relevant_tlds([".fake", ".fake", ".testtld"])) 
            == set(GENERIC_TLD_DOMAINS + [".fake", ".testtld"]))

@pytest.mark.anyio
@patch('ceatw_update_pipeline.gather_sources.AsyncExa')
async def test_retry_logic(mock_exa):
    mock_exa.return_value.search = AsyncMock()
    mock_search = mock_exa.return_value.search
    
    # Reach max retry limit
    mock_search.side_effect = RuntimeError("API search error")
    with pytest.raises(RuntimeError):
        await get_exa_sources("GB", {"GB": ExaPayload(query="", include_domains=[".gov.uk"])})
    assert mock_search.call_count == settings.MAX_RETRIES, f"Should attempt to search {settings.MAX_RETRIES} times."

    # Succeed on last retry
    mock_result_item = MagicMock()
    mock_result_item.title = "Official UK Government Website"
    mock_result_item.url = "https://www.gov.uk/example"
    mock_result_item.published_date = None 
    mock_result_item.highlights = None   
    
    mock_success_response = MagicMock()
    mock_success_response.results = [mock_result_item]
    
    mock_search.reset_mock()
    mock_search.side_effect = ([RuntimeError("API Rate limit") for i in range(settings.MAX_RETRIES-1)] 
                            + [mock_success_response, mock_success_response])
    
    await get_exa_sources("GB", {"GB": ExaPayload(query="", include_domains=[".gov.uk"])})
    
    # Four, because two calls are made to Exa.api for the english and natural prompt.
    assert mock_search.call_count == 4, "Should have failed twice and succeeded on the third attempt."

@pytest.mark.anyio
@patch('ceatw_update_pipeline.gather_sources.generate_exa_payload', new_callable=AsyncMock)
async def test_cache(mock_generate):
    cached_result = ExaPayload(query="a", include_domains=[])
    non_cached_result = ExaPayload(query="b", include_domains=[])
    mock_generate.return_value = non_cached_result
    
    # In cache
    first_result = await get_prompt_from_cache(Country(country_code="GB"),
                                         {"GB": cached_result})
    
    assert first_result == cached_result, "Did not pull exa payload from cache"
    assert mock_generate.call_count == 0, "Called generate despite pulling from cache"
    
    # Not in cache
    second_result = await get_prompt_from_cache(Country(country_code="GB"),
                                         {"GD": cached_result})
    
    assert second_result == non_cached_result, "Should have generated the exa payload"
    mock_generate.assert_called_once()


@pytest.mark.anyio
@patch('ceatw_update_pipeline.gather_sources.AsyncExa')
async def test_get_prompt_return_structure(mock_exa):
    mock_result_item = MagicMock()
    mock_result_item.title = "Sample Title"
    mock_result_item.url = "https://example.gov.jp"
    mock_result_item.published_date = None
    mock_result_item.highlights = ["highlight 1"]
    
    mock_response = MagicMock()
    mock_response.results = [mock_result_item]
    
    mock_exa.return_value.search = AsyncMock(return_value=mock_response)
    
    for cc in COUNTRIES[:1]:
        result = await get_exa_sources(cc, {cc: ExaPayload(query="test", include_domains=[".jp"])})
        
        # Check the logic for the return length
        assert isinstance(result, list), f"List expected, got {type(result)}."
        assert 0 < len(result) <= 2 * settings.MAX_URL_COUNT, (
            f"Expected 1-{2 * settings.MAX_URL_COUNT} URLs, got {len(result)}).")
        
        # Check the logic for correct data mapping
        for item in result:
            assert item.country.country_code == cc, (
                f"Wrong country code - expected: {cc}, got: {item.country.country_code}")
            assert item.search_strategy is not None