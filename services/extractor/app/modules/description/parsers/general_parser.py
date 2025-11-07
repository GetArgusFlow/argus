# argus/services/extractor/app/modules/description/parsers/general_parser.py

import re
from typing import Optional, Tuple, Any
from bs4 import BeautifulSoup
from loguru import logger
from app.core.models import FieldExtractionStatus
from app.modules.description.utils import clean_and_validate_description


def parse_general_sections(
    soup: BeautifulSoup, nlp_model: Any = None
) -> Tuple[Optional[str], str, FieldExtractionStatus, int]:
    """
    Extracts the description from general sections related to the description.
    """
    logger.debug("General Parser: Searching for general description sections.")

    general_desc_elements = soup.find_all(
        ["div", "p", "section", "span"],
        class_=re.compile(r"description|details|info|content|main-text", re.IGNORECASE),
        id=re.compile(r"description|details|info|content|main-text", re.IGNORECASE),
    )

    for elem in general_desc_elements:
        text_content = elem.get_text(separator=" ", strip=True)
        cleaned_desc = clean_and_validate_description(text_content, nlp_model)
        if cleaned_desc:
            logger.debug(
                f"General Parser: Found via general element: {cleaned_desc[:100]}..."
            )
            selector = (
                f"{elem.name}#{elem.get('id') or ''} (class={elem.get('class', [])})"
            )
            return cleaned_desc, selector, FieldExtractionStatus.MODULE_HEURISTIC, 150

    return None, "general_parser", FieldExtractionStatus.NOT_FOUND, 0
