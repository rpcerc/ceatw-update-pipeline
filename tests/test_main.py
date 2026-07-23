
from unittest.mock import MagicMock, patch, mock_open
from ceatw_update_pipeline.main import load_native_prompts_cache
from ceatw_update_pipeline.custom_types import ExaPayload, SearchStrategy
import pytest
import json

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
    
