# argus/services/extractor/app/modules/price/extract.py

from typing import Optional, Tuple, Any
from loguru import logger
from app.core.models import FieldExtractionStatus
from app.core.context import shared_context

from .parsers.json_ld_parser import parse_json_ld
from .parsers.open_graph_parser import parse_open_graph
from .parsers.itemprop_parser import parse_itemprop
from .parsers.class_parser import parse_price_classes
from .parsers.regex_section_parser import parse_regex_in_sections
from .parsers.regex_body_parser import parse_regex_in_body

FIELD_TYPE = Optional[float]
REQUIRES = ["json_ld", "open_graph"]


def extract() -> Tuple[Any, str, FieldExtractionStatus, int]:
    """
    The main extractor function that extracts the price by calling a series of parsers.
    """
    soup_to_use = shared_context.get("raw_soup")
    if not soup_to_use:
        logger.warning("Price Extractor: No valid BeautifulSoup objects to work with.")
        return None, "NOT_FOUND", FieldExtractionStatus.NOT_FOUND, 0

    logger.info("Price Extractor (Main): Starting price extraction.")

    processed_elements = shared_context.get("processed_elements", set())

    # Priority 1: JSON-LD (highest reliability)
    price, selector, status, score = parse_json_ld()
    if price is not None:
        logger.info(
            f"Price Extractor: Price successfully extracted with JSON-LD Parser. Score: {score}"
        )
        return price, selector, status, score

    # Priority 2: Open Graph (high reliability)
    price, selector, status, score = parse_open_graph()
    if price is not None:
        logger.info(
            f"Price Extractor: Price successfully extracted with Open Graph Parser. Score: {score}"
        )
        return price, selector, status, score

    # Priority 3: itemprop="price"
    price, selector, status, score = parse_itemprop(soup_to_use, processed_elements)
    if price is not None:
        logger.info(
            f"Price Extractor: Price successfully extracted with itemprop parser. Score: {score}"
        )
        return price, selector, status, score

    # Priority 4: Price-related classes/IDs
    price, selector, status, score = parse_price_classes(
        soup_to_use, processed_elements
    )
    if price is not None:
        logger.info(
            f"Price Extractor: Price successfully extracted with Class Parser. Score: {score}"
        )
        return price, selector, status, score

    # Priority 5: Regex in specific sections
    price, selector, status, score = parse_regex_in_sections(
        soup_to_use, processed_elements
    )
    if price is not None:
        logger.info(
            f"Price Extractor: Price successfully extracted with Regex Section Parser. Score: {score}"
        )
        return price, selector, status, score

    # Priority 6: Regex in the whole body (last resort)
    price, selector, status, score = parse_regex_in_body(
        soup_to_use, processed_elements
    )
    if price is not None:
        logger.info(
            f"Price Extractor: Price successfully extracted with Regex Body Parser. Score: {score}"
        )
        return price, selector, status, score

    logger.info("Price Extractor: No suitable price found.")
    return None, "NOT_FOUND", FieldExtractionStatus.NOT_FOUND, 0
