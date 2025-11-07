# argus/services/extractor/app/modules/open_graph/extract.py

from typing import Dict, Any, Tuple, Optional
from loguru import logger

from app.core.context import shared_context
from app.core.types import FieldExtractionStatus
from .utils import find_og_tags

REQUIRES = []
FIELD_TYPE = Optional[Dict[str, Any]]


def extract() -> Tuple[Optional[Dict[str, Any]], str, FieldExtractionStatus, int]:
    """
    Extracts all raw Open Graph (og:) data from the page's meta tags.

    This module acts as a data provider. Other modules (like 'price',
    'title', 'image') will depend on this module and consume this
    raw dictionary from the shared_context.
    """
    raw_soup = shared_context.get("raw_soup")
    selector_used = "meta[property^='og:']"

    if not raw_soup:
        logger.warning("Open Graph Extractor: No raw_soup found in context.")
        return None, selector_used, FieldExtractionStatus.NOT_FOUND, 0

    # Call the utility function to find all tags
    og_tags = find_og_tags(raw_soup)

    if not og_tags:
        logger.info("Open Graph Extractor: No Open Graph tags found.")
        return None, selector_used, FieldExtractionStatus.NOT_FOUND, 0

    logger.info(f"Open Graph Extractor: Found {len(og_tags)} raw OG tags.")

    # Return the raw dictionary.
    # The Analyzer will place this dict on the shared_context['open_graph']
    # AND add it to the final 'open_graph' key in the API response.
    return og_tags, selector_used, FieldExtractionStatus.OPEN_GRAPH, 200
