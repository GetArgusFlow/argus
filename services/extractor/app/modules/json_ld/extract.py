# argus/services/extractor/app/modules/json_ld/extract.py

from typing import Dict, Any, Optional, Tuple, List
from loguru import logger
from app.core.context import shared_context
from app.core.models import FieldExtractionStatus
from app.modules.json_ld.utils import parse_json_ld_scripts

REQUIRES = []
FIELD_TYPE = Optional[List[Dict[str, Any]]]


def extract() -> Tuple[Optional[List[Dict[str, Any]]], str, FieldExtractionStatus, int]:
    """
    Extracts all raw JSON-LD data from the page.
    This module acts as a data provider. Other modules (like 'price',
    'title', 'reviews') will depend on this module and consume this
    raw data from the shared_context.
    """
    soup_to_use = shared_context.get("raw_soup")
    selector = "script[type='application/ld+json']"

    if not soup_to_use:
        logger.warning("JSON_LD Extractor: No raw_soup found in context.")
        return None, selector, FieldExtractionStatus.NOT_FOUND, 0

    # Use the utility to find and parse all scripts
    all_parsed_json_data = parse_json_ld_scripts(soup_to_use)

    if not all_parsed_json_data:
        logger.info("JSON_LD Extractor: No valid JSON-LD data found on page.")
        return None, selector, FieldExtractionStatus.NOT_FOUND, 0

    logger.info(
        f"JSON_LD Extractor: Found {len(all_parsed_json_data)} raw JSON-LD nodes."
    )

    # Return the raw list.
    # The Analyzer will place this list on the shared_context['json_ld']
    # AND add it to the final 'json_ld' key in the API response.
    return all_parsed_json_data, selector, FieldExtractionStatus.JSON_LD, 200
