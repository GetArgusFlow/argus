# argus/services/extractor/app/modules/title/extract.py

from typing import Optional, Tuple, Any, List
from loguru import logger
from app.core.models import FieldExtractionStatus
from app.core.context import shared_context

from .parsers.json_ld_parser import parse_json_ld
from .parsers.open_graph_parser import parse_open_graph
from .parsers.h1_parser import parse_h1_tags
from .parsers.title_tag_parser import parse_title_tag
from .parsers.meta_parser import parse_meta_tags
from .parsers.fallback_parser import parse_generic_fallback

FIELD_TYPE = Optional[str]
REQUIRES = ["json_ld", "open_graph"]


def extract() -> Tuple[Any, str, FieldExtractionStatus, int]:
    """
    The main extractor function that extracts the title by calling a series of parsers,
    collects all results, and returns the one with the highest score.
    """
    soup_to_use = shared_context.get("raw_soup")
    processed_elements = shared_context.get("processed_elements", set())

    logger.info("Title Extractor (Main): Starting product title extraction.")

    if not soup_to_use:
        logger.warning("Title Extractor: No valid BeautifulSoup objects to work with.")
        return None, "NOT_FOUND", FieldExtractionStatus.NOT_FOUND, 0

    # Step 1: Initialize a list to store all found results.
    results: List[Tuple[Any, str, FieldExtractionStatus, int]] = []

    # Step 2: Call all parsers and add their results to the list.

    # Parser 1: JSON-LD (highest reliability)
    title, selector, status, score = parse_json_ld()
    if title:
        results.append((title, selector, status, score))

    # Parser 2: Open Graph (high reliability)
    title, selector, status, score = parse_open_graph()
    if title:
        results.append((title, selector, status, score))

    # Parser 3: H1 tags
    title, selector, status, score = parse_h1_tags(soup_to_use, processed_elements)
    if title:
        results.append((title, selector, status, score))

    # Parser 4: <title> tag
    title, selector, status, score = parse_title_tag(soup_to_use, processed_elements)
    if title:
        results.append((title, selector, status, score))

    # Parser 5: Meta tags (itemprop='name')
    title, selector, status, score = parse_meta_tags(soup_to_use, processed_elements)
    if title:
        results.append((title, selector, status, score))

    # Parser 6: Generic fallback
    title, selector, status, score = parse_generic_fallback(
        soup_to_use, processed_elements
    )
    if title:
        results.append((title, selector, status, score))

    # Step 3: Determine the best result from the list.
    if not results:
        logger.info("Title Extractor: No suitable product title found.")
        return None, "NOT_FOUND", FieldExtractionStatus.NOT_FOUND, 0

    # Use max() to find the result (tuple) with the highest score (the 4th element, index 3).
    best_result = max(results, key=lambda item: item[3])

    logger.success(
        f"Title Extractor: Best title found via '{best_result[1]}' with score {best_result[3]}."
    )
    return best_result
