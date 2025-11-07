# argus/services/extractor/app/modules/breadcrumbs/parsers/regex_parser.py

import re
from typing import Optional, Tuple, List
from bs4 import BeautifulSoup
from loguru import logger
from app.core.models import FieldExtractionStatus
from app.modules.breadcrumbs.utils import clean_and_filter_breadcrumbs, is_unwanted_text

# Expanded regex to include '|' and '\' as separators
BREADCRUMB_SEP_REGEX = re.compile(r"\s*>\s*|\s*»\s*|\s*/\s*|\s*\|\s*|\\")


def parse_with_regex(
    soup: BeautifulSoup,
) -> Tuple[Optional[List[str]], str, FieldExtractionStatus, int]:
    """
    Finds breadcrumbs using a regex pattern based on separators,
    while safely ignoring script and style content.
    """

    # Search for text nodes containing any of the separators
    all_text_nodes = soup.body.find_all(string=BREADCRUMB_SEP_REGEX)

    for text_node in all_text_nodes:
        # Avoid extracting from noisy or irrelevant tags
        if text_node.parent.name in ["script", "style", "title", "head", "a", "option"]:
            continue

        text = text_node.strip()

        # Check for minimal length and unwanted patterns
        if not text or len(text) < 5 or is_unwanted_text(text):
            continue

        # Split the text based on the separators
        parts = re.split(BREADCRUMB_SEP_REGEX, text)
        cleaned_breadcrumbs = clean_and_filter_breadcrumbs(parts)

        if cleaned_breadcrumbs:
            selector_used = f"{text_node.parent.name} (text pattern)"
            logger.debug(f"Regex Parser: Found breadcrumbs: {cleaned_breadcrumbs}")
            return (
                cleaned_breadcrumbs,
                selector_used,
                FieldExtractionStatus.MODULE_HEURISTIC,
                80,
            )

    return None, "regex_parser", FieldExtractionStatus.NOT_FOUND, 0
