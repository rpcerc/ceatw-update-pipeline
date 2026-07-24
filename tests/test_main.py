
from unittest.mock import MagicMock, patch, mock_open
from ceatw_update_pipeline.main import (load_native_prompts_cache, get_gemini_prompts,
    get_n_random_countries, insert_urls_for_one_country)
from ceatw_update_pipeline.custom_types import ExaPayload
from sqlalchemy.exc import IntegrityError
import pytest
import pycountry

@patch("builtins.open", new_callable=mock_open, read_data="""{
    "VN": {
        "query": "Chương trình giáo dục phổ thông môn Tin học cấp tiểu học, trung học cơ sở và trung học phổ thông",
        "includeDomains": [
            "gov.vn",
            "edu.vn"
        ]
    }}""")
def test_load_native_prompts_cache_ok(mock_open):
    data = load_native_prompts_cache()    

    assert "VN" in data, "Country code not in the data"
    
    values = data["VN"].model_dump()
    
    assert "query" in values, "query is not a field"
    assert "includeDomains" in values, "includeDomains is not a field"
    assert values["includeDomains"] == ["gov.vn", "edu.vn"], "wrong domains"
    assert isinstance(values["query"], str), "query malformed"
    
    
@patch("builtins.open", new_callable=mock_open, read_data="""{
    "VN": {
        "bananas": "Chương trình giáo dục phổ thông môn Tin học cấp tiểu học, trung học cơ sở và trung học phổ thông",
        "includeDomains": [
            "gov.vn",
            "edu.vn"
        ]
    }}""")
def test_load_native_prompts_not_ok(mock_open):
    data = load_native_prompts_cache()    
    assert data == {}

@pytest.mark.asyncio
@patch("ceatw_update_pipeline.main.generate_exa_payload")
@patch("json.dump")
@patch("ceatw_update_pipeline.main.logger.info")
@patch("ceatw_update_pipeline.main.load_native_prompts_cache")
@patch("pycountry.countries", [
    pycountry.countries.get(alpha_2="GB"), 
    pycountry.countries.get(alpha_2="DE")
])
async def test_get_gemini_prompts(mock_cache, mock_logger, mock_write, mock_generate):
    mock_cache.return_value = {"GB": ExaPayload(query="fake-query", includeDomains=["gov.uk"])}
    mock_generate.return_value = ExaPayload(query="germany", includeDomains=[".de"])
    
    result = await get_gemini_prompts()
    
    # Should skip writing for GB
    mock_logger.assert_any_call("Native prompt already cached for country: %s",
                                "United Kingdom")
    mock_write.assert_called_once()
    
    # New result added
    assert "DE" in result
    assert result["DE"].query is not None
    assert len(result["DE"].includeDomains) == 1 and result["DE"].includeDomains[0] == ".de"
    
    # Cached result still there
    assert "GB" in result
    assert result["GB"] == mock_cache.return_value["GB"]

# ==========================================
# 2. Tests for get_n_random_countries
# ==========================================

@pytest.mark.asyncio
@patch("ceatw_update_pipeline.main.insert_urls_for_one_country")
@patch("asyncio.sleep")
async def test_get_n_random_countries_rate_limiting(mock_sleep, mock_insert):
    """
    Test that rate limit chunking works. 
    12 countries should result in 3 batches (5, 5, 2) and 3 sleeps.
    """
    # We mock the DB insert to do nothing so the test runs instantly
    mock_insert.return_value = None 
    mock_cache = {}
    
    await get_n_random_countries(12, mock_cache)    
    assert mock_sleep.call_count == 3
    assert mock_insert.call_count == 12


# ==========================================
# 3. Tests for insert_urls_for_one_country
# ==========================================

@pytest.mark.asyncio
@patch("ceatw_update_pipeline.main.query.insert_source")
@patch("ceatw_update_pipeline.main.get_session")
@patch("ceatw_update_pipeline.main.get_exa_sources")
async def test_insert_urls_integrity_error_recovery(mock_get_sources,
                                                    mock_get_session, mock_insert_source):
    """
    Test that a duplicate URL (IntegrityError) does not crash the loop,
    and subsequent URLs are still processed.
    """
    # 1. Create two fake results from Exa
    mock_result_1 = MagicMock(url="http://duplicate.com")
    mock_result_2 = MagicMock(url="http://new-url.com")
    mock_get_sources.return_value = [mock_result_1, mock_result_2]

    # 2. Setup the DB session mock to support the 'with' context manager
    mock_session = MagicMock()
    mock_get_session.return_value.__enter__.return_value = mock_session

    # 3. Simulate an IntegrityError on the FIRST insert, but success on the SECOND
    # The type returned should technically be Source, but it doesn't matter for this test.
    mock_insert_source.side_effect = [
        IntegrityError(statement="INSERT...", params={}, orig=Exception()), 
        None
    ]
    
    await insert_urls_for_one_country("GB", {})
    
    # 5. Assertions: ensure insert_source was called twice despite the first failure
    assert mock_insert_source.call_count == 2
    
    
    
    
    
