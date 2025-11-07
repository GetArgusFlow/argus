# argus/services/extractor/app/modules/breadcrumbs/utils.py

from typing import List, Optional
import re
from loguru import logger
from app.utils.pattern_manager import pattern_manager

# FILTER_UNWANTED_CRUMBS constant is removed


def clean_and_filter_breadcrumbs(breadcrumbs: List[str]) -> Optional[List[str]]:
    """
    Cleans up a list of breadcrumbs by removing empty, short, or generic items.
    Returns None if the resulting list is invalid.
    """
    # Get the dynamic filter list from PatternManager
    unwanted_crumbs = pattern_manager.get_keyword_list("breadcrumb_filter_keywords")
    unwanted_crumbs_lower = {k.lower() for k in unwanted_crumbs}

    # Filter empty strings and generic terms
    filtered = [
        b.strip()
        for b in breadcrumbs
        if b and b.strip() and b.strip().lower() not in unwanted_crumbs_lower
    ]

    # Deduplicate the list while preserving order
    deduplicated_breadcrumbs = []
    for item in filtered:
        if not deduplicated_breadcrumbs or item != deduplicated_breadcrumbs[-1]:
            deduplicated_breadcrumbs.append(item)

    # A valid set of breadcrumbs must have at least two items
    if len(deduplicated_breadcrumbs) >= 2:
        return deduplicated_breadcrumbs

    logger.debug(
        f"Breadcrumb validation: The found list ({deduplicated_breadcrumbs}) is too short or invalid."
    )
    return None


def is_unwanted_text(text: str) -> bool:
    """
    Checks if a piece of text is likely not a breadcrumb (e.g., address, date).
    """
    return bool(
        re.search(
            r"\d{4}\s*[a-zA-Z]{2}|\d{2}-\d{2}-\d{4}|email|tel:|fax:",
            text,
            re.IGNORECASE,
        )
    )
