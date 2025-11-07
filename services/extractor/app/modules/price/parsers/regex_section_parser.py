# argus/services/extractor/app/modules/price/parsers/regex_section_parser.py

import re
from typing import Optional, Tuple, Set
from bs4 import BeautifulSoup, Tag
from loguru import logger
from app.core.models import FieldExtractionStatus
from app.modules.price.utils import clean_price_text
from app.utils.pattern_manager import pattern_manager


def parse_regex_in_sections(
    soup: BeautifulSoup, processed_elements: Set[Tag]
) -> Tuple[Optional[float], str, FieldExtractionStatus, int]:
    """
    Searches for price formats with regex in specific sections of the page.
    """
    potential_price_sections = soup.find_all(
        ["div", "span", "section"],
        # Use dynamic regex for classes
        class_=pattern_manager.get_compiled_regex("price_section_class_regex"),
        limit=5,
    )

    # Use dynamic regex for price format
    price_regex = pattern_manager.get_compiled_regex("price_format_regex")

    for section in potential_price_sections:
        if section in processed_elements:
            continue

        section_text = section.get_text(strip=True)
        if len(section_text) > 1000:
            section_text = section_text[:1000]

        matches = re.finditer(price_regex, section_text, re.IGNORECASE)
        for match in matches:
            for group in match.groups():
                if group:
                    numerical_price = clean_price_text(group)
                    if numerical_price is not None:
                        selector_detail = f'{section.name}[class*="{section.get("class")[0] if section.get("class") else ""}"] (regex)'
                        logger.debug(
                            f"Regex Section Parser: Found via general regex in specific section: {numerical_price}"
                        )
                        processed_elements.add(section)
                        return (
                            numerical_price,
                            selector_detail,
                            FieldExtractionStatus.MODULE_REGEX,
                            70,
                        )

    return None, "regex_section_parser", FieldExtractionStatus.NOT_FOUND, 0
