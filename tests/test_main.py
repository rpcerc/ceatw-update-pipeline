
from unittest.mock import MagicMock, patch, mock_open
from ceatw_update_pipeline.main import (load_native_prompts_cache,
    insert_countries, insert_urls_for_one_country)
from sqlalchemy.exc import IntegrityError
import pytest

@patch("builtins.open", new_callable=mock_open, read_data="""{
    "VN": {
        "query": "Chương trình giáo dục phổ thông môn Tin học cấp tiểu học, trung học cơ sở và trung học phổ thông",
        "include_domains": [
            "gov.vn",
            "edu.vn"
        ]
    }}""")
def test_load_native_prompts_cache_ok(mock_open):
    data = load_native_prompts_cache()    

    assert "VN" in data, "Country code not in the data"
    
    values = data["VN"].model_dump()
    
    assert "query" in values, "query is not a field"
    assert "include_domains" in values, "include_domains is not a field"
    assert values["include_domains"] == ["gov.vn", "edu.vn"], "wrong domains"
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

# ==========================================
# 2. Tests for insert_countries
# ==========================================

@pytest.mark.asyncio
@patch("ceatw_update_pipeline.main.insert_urls_for_one_country")
@patch("asyncio.sleep")
async def test_insert_countries(mock_sleep, mock_insert):
    """
    Test that rate limit chunking works. 
    12 countries should result in 3 batches (5, 5, 2) and 3 sleeps.
    """
    # We mock the DB insert to do nothing so the test runs instantly
    mock_insert.return_value = None 
    mock_cache = {}
    
    await insert_countries(range(12), mock_cache)    
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
    
    
    
    
    
