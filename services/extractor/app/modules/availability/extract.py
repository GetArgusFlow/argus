# argus/services/extractor/app/modules/availability/extract.py

from typing import Optional, Tuple, Any
from loguru import logger
from app.core.models import FieldExtractionStatus
from app.core.context import shared_context

from .parsers.json_ld_parser import parse_json_ld
from .parsers.open_graph_parser import parse_open_graph
from .parsers.schema_parser import parse_schema
from .parsers.text_parser import parse_textual_indicators
from .parsers.meta_parser import parse_meta_tags
from .parsers.title_parser import parse_title

FIELD_TYPE = Optional[str]
REQUIRES = ["json_ld", "open_graph"]


def extract() -> Tuple[Any, str, FieldExtractionStatus, int]:
    """
    The orchestrator function that extracts the availability status by calling a series of parsers.
    """
    soup_to_use = shared_context.get("raw_soup")
    logger.info(
        "Availability Extractor (Main): Starting extraction of availability status."
    )

    if not soup_to_use:
        logger.warning(
            "Availability Extractor: No valid BeautifulSoup objects to work with."
        )
        return None, "NOT_FOUND", FieldExtractionStatus.NOT_FOUND, 0

    # Priority 1: JSON-LD (highest reliability structured data)
    availability, selector, status, score = parse_json_ld()
    if availability:
        logger.info(
            f"Availability Extractor: Status successfully extracted with JSON-LD Parser. Score: {score}"
        )
        return availability, selector, status, score

    # Priority 2: Open Graph (high reliability structured data)
    availability, selector, status, score = parse_open_graph()
    if availability:
        logger.info(
            f"Availability Extractor: Status successfully extracted with Open Graph Parser. Score: {score}"
        )
        return availability, selector, status, score

    # Priority 3: Schema.org microdata (HTML fallback)
    availability, selector, status, score = parse_schema(soup_to_use)
    if availability:
        logger.info(
            f"Availability Extractor: Status successfully extracted with Schema Parser. Score: {score}"
        )
        return availability, selector, status, score

    # Priority 4: Textual indicators in relevant DOM elements
    availability, selector, status, score = parse_textual_indicators(soup_to_use)
    if availability:
        logger.info(
            f"Availability Extractor: Status successfully extracted with Text Parser. Score: {score}"
        )
        return availability, selector, status, score

    # Priority 5: General meta-tags
    availability, selector, status, score = parse_meta_tags(soup_to_use)
    if availability:
        logger.info(
            f"Availability Extractor: Status successfully extracted with Meta Parser. Score: {score}"
        )
        return availability, selector, status, score

    # Priority 6: Page title (lowest reliability)
    availability, selector, status, score = parse_title(soup_to_use)
    if availability:
        logger.info(
            f"Availability Extractor: Status successfully extracted with Title Parser. Score: {score}"
        )
        return availability, selector, status, score

    logger.info("Availability Extractor: No clear availability status found.")
    return None, "NOT_FOUND", FieldExtractionStatus.NOT_FOUND, 0
