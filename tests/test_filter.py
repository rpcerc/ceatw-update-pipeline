import pytest
from unittest.mock import patch
from ceatw_update_pipeline.filter import is_valid_url

# ==========================================
# 1. TEST VALID URLs (Expected to return True)
# ==========================================
@pytest.mark.parametrize("url, description", [
    ("https://www.google.com", "Standard 200 OK"),
    ("http://github.com", "HTTP redirecting to HTTPS (301 -> 200)"),
    ("https://httpbingo.org/status/200", "Explicit 200 OK response"),
    ("https://httpbingo.org/absolute-redirect/1", "Explicit redirect handled successfully"),
    ("https://httpbingo.org/image/jpeg", "Image"),
    ("https://pdfobject.com/pdf/sample.pdf", "PDF"),
])
def test_is_valid_url_success(url, description):
    # The description parameter is just to make the test output easier to read
    # if one of them fails, so you know exactly what scenario broke.
    assert is_valid_url(url) is True


# ==========================================
# 2. TEST INVALID URLs (Expected to return False)
# ==========================================
@pytest.mark.parametrize("url, description", [
    ("https://httpbingo.org/status/404", "404 Not Found"),
    ("https://httpbingo.org/status/403", "403 Forbidden"),
    ("https://httpbingo.org/status/500", "500 Internal Server Error"),
    ("https://this-domain-is-completely-fake-123456.com", "DNS/Connection Failure"),
    ("htpas/:", "Malformed Schema (InvalidSchema)"),
    ("not_a_url_at_all", "Missing Schema (MissingSchema)"),
    ("https://httpbingo.org/delay/6", "Timeout (Takes 6s, limit is 5s)"),
    ("https://example.com/fake.pdf", "PDF"),
])
def test_is_valid_url_failures(url, description):
    assert is_valid_url(url) is False


# ==========================================
# 3. TEST SYSTEM ERRORS (Expected to raise RuntimeError)
# ==========================================
def test_is_valid_url_unexpected_error():
    # Passing None or an integer will cause a TypeError/AttributeError 
    # before requests even tries to make a network call, 
    # proving that our final 'except Exception as e:' block works.
    with patch('requests.head', side_effect=ValueError("Fake value error")):
        with pytest.raises(RuntimeError) as exc_info:
            is_valid_url(None)
    
        assert "unexpected" in str(exc_info.value)
        
if __name__ == "__main__":
    test_is_valid_url_unexpected_error()