"""Non-standard tests that shouldn't be caught with pytest."""

from ceatw_update_pipeline.filter import is_valid_url

if __name__ == "__main__":
    assert is_valid_url("https://www.education.gouv.fr/bo/19/Hebdo37/MENE1915146D.htm") is True