from ceatw_update_pipeline.keyword_filter import generate_filter_keywords
from ceatw_update_pipeline.custom_types import Source

def contains_computing_curriculum(source: Source) -> bool:
    """Checks if Exa highlights contain relevant computing or curriculum terms.
    
    Args:
        highlights (list[str] | None): List of text snippets from Exa.
        
    Returns:
        bool: True if relevant terms are found, False otherwise.
    """
    # 1. Get the dynamic country keywords
    keywords = generate_filter_keywords(source)
    tech_filters = keywords["tech_keywords"]
    edu_filters = keywords["edu_keywords"]

    # 2. Inside your highlight check
    combined_highlights = " ".join(source["highlights"]).lower()

    has_tech = any(tk in combined_highlights for tk in tech_filters)
    has_edu = any(ek in combined_highlights for ek in edu_filters)

    if has_tech and has_edu:
        # This is a highly confident match!