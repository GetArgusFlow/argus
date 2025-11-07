# argus/services/extractor/app/modules/open_graph/parsers/availability_parser.py

from typing import Dict, Any
from loguru import logger
from app.utils.data_utils import normalize_availability


def parse_availability(og_tags: Dict[str, Any], extracted_fields: Dict[str, Any]):
    """
    Extracts and normalizes the availability status from the Open Graph tags.
    Modifies the 'extracted_fields' dictionary in-place.
    """
    logger.debug("Availability Parser: Starting availability extraction.")

    availability_og = og_tags.get("availability")
    if availability_og:
        normalized_availability = normalize_availability(availability_og)
        if normalized_availability:
            extracted_fields["availability"] = normalized_availability
            logger.debug(
                f"Availability Parser: Availability '{normalized_availability}' found."
            )
        else:
            logger.debug(
                f"Availability Parser: Could not normalize availability '{availability_og}'."
            )
