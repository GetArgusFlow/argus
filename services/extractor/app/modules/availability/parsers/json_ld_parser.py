# argus/services/extractor/app/modules/availability/parsers/json_ld_parser.py

from typing import Optional, Tuple
from loguru import logger
from app.core.models import FieldExtractionStatus
from app.core.context import shared_context
from app.modules.availability.utils import find_availability_status


def parse_json_ld() -> Tuple[Optional[str], str, FieldExtractionStatus, int]:
    """
    Extracts availability from the 'json_ld' data in shared_context.
    """
    logger.debug("JSON-LD Parser: Searching for availability in JSON-LD data.")

    # Get the raw list of JSON-LD nodes
    json_ld_data = shared_context.get("json_ld")
    if not isinstance(json_ld_data, list):
        return None, "json_ld_parser", FieldExtractionStatus.NOT_FOUND, 0

    for node in json_ld_data:
        if not isinstance(node, dict):
            continue

        # Look for availability in an 'offers' node (dict or list)
        offers = node.get("offers")
        offer_list = []
        if isinstance(offers, dict):
            offer_list = [offers]
        elif isinstance(offers, list):
            offer_list = offers

        for offer in offer_list:
            if not isinstance(offer, dict):
                continue

            availability_raw = offer.get("availability")
            if isinstance(availability_raw, str):
                # The value is often a URL like 'http://schema.org/InStock'
                # We just want the last part.
                status_text = availability_raw.split("/")[-1]
                status = find_availability_status(status_text)
                if status:
                    logger.debug(
                        f"JSON-LD Parser: Found status '{status}' via 'offers.availability'."
                    )
                    return (
                        status,
                        "json_ld.offers.availability",
                        FieldExtractionStatus.JSON_LD,
                        200,
                    )

    logger.debug("JSON-LD Parser: No availability found in JSON-LD data.")
    return None, "json_ld_parser", FieldExtractionStatus.NOT_FOUND, 0
