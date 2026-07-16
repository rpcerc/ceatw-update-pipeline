"""Functions for ensuring the link exists and is scrapable."""

import requests

def is_valid_url(url: str) -> bool:
<<<<<<< HEAD
    """Checks whether a given URL is valid.
=======
    """Checks if a URL is a valid link. Note, this doesn't work sometimes. It might be because
       of anti-bot measures.
>>>>>>> george-development

    Args:
        url (str): The given URL to check.

    Raises:
        RuntimeError: An non-request related error.

    Returns:
        bool: Whether the given url is valid or not.
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.head(url, allow_redirects=True, timeout=5, headers=headers)
        response.raise_for_status()
        return True
    except requests.RequestException:
        return False
    except Exception as e:
        raise RuntimeError(f"An unexpected error occured: {e}")
        