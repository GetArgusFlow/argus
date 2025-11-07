# argus/services/extractor/app/modules/image/extract.py

from typing import Optional, Tuple, Any
from loguru import logger
from app.core.models import FieldExtractionStatus
from app.core.context import shared_context

from .parsers.json_ld_parser import parse_json_ld
from .parsers.open_graph_parser import parse_open_graph
from .parsers.meta_parser import parse_meta_tags
from .parsers.amazon_parser import parse_amazon_selectors
from .parsers.context_parser import parse_from_product_context
from .parsers.fallback_parser import parse_largest_image_fallback

FIELD_TYPE = Optional[str]

REQUIRES = ["json_ld", "open_graph"]


def extract() -> Tuple[Any, str, FieldExtractionStatus, int]:
    """
    The orchestrator function that extracts the image URL by calling a series of parsers.
    """
    soup_to_use = shared_context.get("raw_soup")
    processed_elements = shared_context.get("processed_elements", set())
    if not soup_to_use:
        logger.warning("Image Extractor: No valid BeautifulSoup objects to work with.")
        return None, "NOT_FOUND", FieldExtractionStatus.NOT_FOUND, 0

    logger.info("Image Extractor (Main): Starting image URL extraction.")

    # Priority 1: JSON-LD (highest reliability)
    image_url, selector, status, score = parse_json_ld()
    if image_url:
        logger.info(
            f"Image Extractor: Image URL successfully extracted with JSON-LD Parser. Score: {score}"
        )
        return image_url, selector, status, score

    # Priority 2: Open Graph (high reliability)
    image_url, selector, status, score = parse_open_graph()
    if image_url:
        logger.info(
            f"Image Extractor: Image URL successfully extracted with Open Graph Parser. Score: {score}"
        )
        return image_url, selector, status, score

    # Priority 3: Schema.org Microdata (HTML)
    image_url, selector, status, score = parse_meta_tags(
        soup_to_use, processed_elements
    )
    if image_url:
        logger.info(
            f"Image Extractor: Image URL successfully extracted with Meta Parser. Score: {score}"
        )
        return image_url, selector, status, score

    # Priority 4: Amazon-specific selectors (HTML)
    image_url, selector, status, score = parse_amazon_selectors(
        soup_to_use, processed_elements
    )
    if image_url:
        logger.info(
            f"Image Extractor: Image URL successfully extracted with Amazon Parser. Score: {score}"
        )
        return image_url, selector, status, score

    # Priority 5: Image in product context (HTML)
    image_url, selector, status, score = parse_from_product_context(
        soup_to_use, processed_elements
    )
    if image_url:
        logger.info(
            f"Image Extractor: Image URL successfully extracted with Context Parser. Score: {score}"
        )
        return image_url, selector, status, score

    # Priority 6: Fallback (largest image, HTML)
    image_url, selector, status, score = parse_largest_image_fallback(
        soup_to_use, processed_elements
    )
    if image_url:
        logger.info(
            f"Image Extractor: Image URL successfully extracted with Fallback Parser. Score: {score}"
        )
        return image_url, selector, status, score

    logger.info("Image Extractor: No suitable image URL found.")
    return None, "NOT_FOUND", FieldExtractionStatus.NOT_FOUND, 0
