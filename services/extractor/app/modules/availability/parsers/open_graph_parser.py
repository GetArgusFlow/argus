# argus/services/extractor/app/modules/availability/parsers/open_graph_parser.py

from typing import Optional, Tuple
from loguru import logger
from app.core.models import FieldExtractionStatus
from app.core.context import shared_context
from app.modules.availability.utils import find_availability_status


def parse_open_graph() -> Tuple[Optional[str], str, FieldExtractionStatus, int]:
    """
    Extracts availability from the 'open_graph' data in shared_context.
    """
    logger.debug("Open Graph Parser: Searching for availability in OG data.")

    og_data = shared_context.get("open_graph")
    if not isinstance(og_data, dict):
        return None, "open_graph_parser", FieldExtractionStatus.NOT_FOUND, 0

    # Standard keys are 'og:availability' or 'product:availability'
    availability_raw = og_data.get("availability") or og_data.get(
        "product:availability"
    )

    if isinstance(availability_raw, str):
        status = find_availability_status(availability_raw)
        if status:
            logger.debug(
                f"Open Graph Parser: Found status '{status}' via 'og:availability'."
            )
            return status, "og:availability", FieldExtractionStatus.OPEN_GRAPH, 190

    logger.debug("Open Graph Parser: No availability found in OG data.")
    return None, "open_graph_parser", FieldExtractionStatus.NOT_FOUND, 0
