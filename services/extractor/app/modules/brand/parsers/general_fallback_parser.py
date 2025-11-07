# argus/services/extractor/app/modules/brand/parsers/general_fallback_parser.py

import re
from typing import Optional, Tuple, Any
from bs4 import BeautifulSoup
from loguru import logger
from app.core.models import FieldExtractionStatus
from app.modules.brand.utils import is_plausible_brand, check_brand_in_main_title
from app.utils.pattern_manager import pattern_manager


def parse_general_fallback(
    soup: BeautifulSoup, nlp_model: Any
) -> Tuple[Optional[str], str, FieldExtractionStatus, int]:
    """
    The last resort parser that searches in general elements.
    """
    logger.debug("General Fallback Parser: Last resort search.")

    brand_elements_fallback = soup.find_all(
        re.compile(r"a|span|div|p"),
        # Use the consistent name 'brand_class_regex'
        class_=pattern_manager.get_compiled_regex("brand_class_regex"),
        limit=5,
    )

    # Get the generic text regex from the PatternManager
    generic_text_regex = pattern_manager.get_compiled_regex("generic_brand_text_regex")

    for elem in brand_elements_fallback:
        brand_name_candidate = elem.get_text(strip=True)
        # Skip generic elements
        if generic_text_regex.search(brand_name_candidate) or re.search(
            r"filter|list|nav|menu|category",
            " ".join(elem.get("class", [])).lower() + " " + elem.get("id", "").lower(),
            re.IGNORECASE,
        ):
            continue

        if is_plausible_brand(
            brand_name_candidate, nlp_model
        ) and check_brand_in_main_title(brand_name_candidate, soup):
            logger.debug(
                f"General Fallback Parser: Found via class/id (fallback) validated by title: {brand_name_candidate}"
            )
            selector = f"{elem.name}"
            if elem.get("class"):
                selector += f".{'.'.join(elem['class'])}"
            elif elem.get("id"):
                selector += f"#{elem['id']}"
            return (
                brand_name_candidate,
                selector + " (fallback)",
                FieldExtractionStatus.MODULE_HEURISTIC,
                70,
            )

    return None, "general_fallback_parser", FieldExtractionStatus.NOT_FOUND, 0
