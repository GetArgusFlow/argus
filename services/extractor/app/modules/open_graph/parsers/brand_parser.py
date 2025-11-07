# argus/services/extractor/app/modules/open_graph/parsers/brand_parser.py

from typing import Dict, Any
from loguru import logger


def parse_brand(og_tags: Dict[str, Any], extracted_fields: Dict[str, Any]):
    """
    Extracts the brand from the non-standard og:brand tag.
    Modifies the 'extracted_fields' dictionary in-place.
    """
    logger.debug("Brand Parser: Starting brand extraction.")

    brand = og_tags.get("brand")
    if brand:
        extracted_fields["brand"] = brand
        logger.debug(f"Brand Parser: Brand '{brand}' found.")
