# argus/services/extractor/app/modules/title/utils.py

import re
from app.utils.pattern_manager import pattern_manager


def clean_title(title_text: str) -> str:
    """Cleans up the title from common website-specific additions."""
    if not title_text:
        return ""

    # Get dynamic regex patterns to remove site names, etc.
    clean_patterns = pattern_manager.get_keyword_list("title_clean_patterns_regex")
    for pattern in clean_patterns:
        title_text = re.sub(pattern, "", title_text, flags=re.IGNORECASE).strip()

    # Get dynamic regex patterns to remove filter phrases
    undesired_phrases = pattern_manager.get_keyword_list("title_filter_phrases_regex")
    for phrase_regex in undesired_phrases:
        title_text = re.sub(phrase_regex, "", title_text, flags=re.IGNORECASE).strip()

    title_text = re.sub(r"\s+", " ", title_text).strip()

    return title_text
