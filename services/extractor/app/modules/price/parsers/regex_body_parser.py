# argus/services/extractor/app/modules/price/parsers/regex_body_parser.py

import re
from typing import Optional, Tuple, Set
from bs4 import BeautifulSoup, Tag
from loguru import logger
from app.core.models import FieldExtractionStatus
from app.modules.price.utils import clean_price_text
from app.utils.pattern_manager import pattern_manager


def parse_regex_in_body(
    soup: BeautifulSoup,
    processed_elements: Set[Tag],
) -> Tuple[Optional[float], str, FieldExtractionStatus, int]:
    """
    Searches for price formats with regex in the entire body of the page.
    """
    body_text = soup.body.get_text(strip=True) if soup.body else ""
    if len(body_text) > 10000:
        body_text = body_text[:10000]

    # Use dynamic regex for price format
    price_regex = pattern_manager.get_compiled_regex("price_format_regex")

    matches = re.finditer(price_regex, body_text, re.IGNORECASE)
    for match in matches:
        for group in match.groups():
            if group:
                numerical_price = clean_price_text(group)
                if numerical_price is not None:
                    logger.debug(
                        f"Regex Body Parser: Found via general regex in body: {numerical_price}"
                    )
                    return (
                        numerical_price,
                        "body (regex heuristic)",
                        FieldExtractionStatus.MODULE_REGEX,
                        50,
                    )

    return None, "regex_body_parser", FieldExtractionStatus.NOT_FOUND, 0
