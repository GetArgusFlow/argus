# argus/services/extractor/app/modules/availability/utils.py

from typing import Dict, List, Optional
from loguru import logger
from app.utils.pattern_manager import pattern_manager


def get_status_map() -> Dict[str, List[str]]:
    """Builds the status map dynamically from the PatternManager."""
    status_map = {
        "In Stock": pattern_manager.get_keyword_list("availability_in_stock"),
        "Out of Stock": pattern_manager.get_keyword_list("availability_out_of_stock"),
        "Pre-order": pattern_manager.get_keyword_list("availability_pre_order"),
    }

    # Add common schema.org terms (and their lowercase versions)
    # in case they are not in the patterns.yml. This fixes the
    # bug where 'InStock' from JSON-LD was not being found.
    status_map["In Stock"].extend(["InStock", "instock"])
    status_map["Out of Stock"].extend(["OutOfStock", "outofstock"])
    status_map["Pre-order"].extend(["PreOrder", "preorder"])

    return status_map


def find_availability_status(text: str) -> Optional[str]:
    """
    Searches for a valid availability status in the given text.
    Returns the status-key ('In Stock', 'Out of Stock', 'Pre-order') or None.
    """
    cleaned_text = text.lower()

    # Get the dynamic map for this request's language(s)
    STATUS_MAP = get_status_map()

    for status_key in ["Out of Stock", "Pre-order", "In Stock"]:
        if any(k.lower() in cleaned_text for k in STATUS_MAP[status_key]):
            if len(cleaned_text.split()) > 10:
                logger.debug(
                    f"Availability validation: Text '{cleaned_text[:50]}...' is too long. Skipping."
                )
                continue

            return status_key

    return None
