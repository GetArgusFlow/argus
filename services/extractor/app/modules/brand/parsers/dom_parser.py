# argus/services/extractor/app/modules/brand/parsers/dom_parser.py

import re
from typing import Optional, Tuple, Any
from bs4 import BeautifulSoup
from loguru import logger
from app.core.models import FieldExtractionStatus
from app.modules.brand.utils import is_plausible_brand, check_brand_in_main_title
from app.utils.pattern_manager import pattern_manager


def parse_with_dom_heuristics(
    soup: BeautifulSoup, nlp_model: Any
) -> Tuple[Optional[str], str, FieldExtractionStatus, int]:
    """
    Extracts the brand name using DOM-based heuristics (classes, IDs, labels).
    """
    logger.debug("DOM Parser: Starting search based on DOM heuristics.")

    # Proximity search based on keywords (Brand:, Manufacturer:, etc.)
    # Get the regex from the PatternManager
    brand_label_keywords_regex = pattern_manager.get_compiled_regex("brand_label_regex")

    for label_tag in soup.find_all(
        lambda tag: tag.name in ["span", "div", "p", "dt", "th"]
        and brand_label_keywords_regex.search(tag.get_text(strip=True))
    ):
        next_sibling = label_tag.find_next_sibling()
        if next_sibling:
            candidate_brand = next_sibling.get_text(strip=True)
            if is_plausible_brand(
                candidate_brand, nlp_model
            ) and check_brand_in_main_title(candidate_brand, soup):
                logger.debug(
                    f"DOM Parser: Found via sibling of label '{label_tag.get_text(strip=True)}': {candidate_brand}"
                )
                return (
                    candidate_brand,
                    f"{label_tag.name} + next sibling",
                    FieldExtractionStatus.MODULE_HEURISTIC,
                    120,
                )

        child_elements = label_tag.find_all(re.compile(r"span|div|a|strong|b"), limit=2)
        for child_elem in child_elements:
            candidate_brand = child_elem.get_text(strip=True)
            if is_plausible_brand(
                candidate_brand, nlp_model
            ) and check_brand_in_main_title(candidate_brand, soup):
                logger.debug(
                    f"DOM Parser: Found via child of label '{label_tag.get_text(strip=True)}': {candidate_brand}"
                )
                return (
                    candidate_brand,
                    f"{label_tag.name} > child",
                    FieldExtractionStatus.MODULE_HEURISTIC,
                    115,
                )

    # Direct search based on classes and IDs
    direct_brand_elements = soup.find_all(
        re.compile(r"a|span|div|p|strong|h[1-6]"),
        # Get the class regex from the PatternManager
        class_=pattern_manager.get_compiled_regex("brand_class_regex"),
    )

    # Get the generic text regex from the PatternManager
    generic_text_regex = pattern_manager.get_compiled_regex("generic_brand_text_regex")

    for elem in direct_brand_elements:
        text_content = elem.get_text(strip=True)
        # Skip generic links (e.g., "All brands")
        if generic_text_regex.search(text_content):
            continue

        if is_plausible_brand(text_content, nlp_model) and check_brand_in_main_title(
            text_content, soup
        ):
            logger.debug(f"DOM Parser: Found via direct class/id: {text_content}")
            return (
                text_content,
                f"{elem.name}.{'.'.join(elem.get('class', []))}",
                FieldExtractionStatus.MODULE_HEURISTIC,
                125,
            )

    return None, "dom_parser", FieldExtractionStatus.NOT_FOUND, 0
