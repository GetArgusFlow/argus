# argus/services/extractor/app/modules/breadcrumbs/parsers/json_ld_parser.py

from typing import Optional, Tuple, List
from loguru import logger
from app.core.models import FieldExtractionStatus
from app.core.context import shared_context
from app.modules.breadcrumbs.utils import clean_and_filter_breadcrumbs


def parse_from_json_ld() -> Tuple[Optional[List[str]], str, FieldExtractionStatus, int]:
    """
    Parses breadcrumbs from the raw 'json_ld' list in shared_context.
    It finds the 'BreadcrumbList' node and extracts the items.
    """

    # 1. Get the RAW LIST of nodes from the 'json_ld' module
    json_ld_data_list = shared_context.get("json_ld")

    if not isinstance(json_ld_data_list, list):
        logger.debug("Breadcrumbs JSON-LD Parser: No 'json_ld' list found in context.")
        return None, "json_ld_parser", FieldExtractionStatus.NOT_FOUND, 0

    found_breadcrumbs = []

    # 2. Find the BreadcrumbList node in the raw list
    for node in json_ld_data_list:
        if not isinstance(node, dict):
            continue

        if node.get("@type", "").lower() == "breadcrumblist":
            item_list_element = node.get("itemListElement")
            if not isinstance(item_list_element, list):
                continue

            # Sort by position to ensure correct order
            sorted_item_list = sorted(
                item_list_element,
                key=lambda x: x.get("position", 99) if isinstance(x, dict) else 99,
            )

            # 3. Extract the name from each item
            for item_data in sorted_item_list:
                crumb_name = None
                if isinstance(item_data, dict):
                    # Item can be a nested object
                    item_node = item_data.get("item")
                    if isinstance(item_node, dict):
                        crumb_name = item_node.get("name")
                    # Or the name can be directly on the list element
                    elif "name" in item_data:
                        crumb_name = item_data.get("name")

                if crumb_name and isinstance(crumb_name, str):
                    found_breadcrumbs.append(crumb_name.strip())

            # If we found a list, stop processing other nodes
            if found_breadcrumbs:
                break

    if not found_breadcrumbs:
        logger.debug(
            "Breadcrumbs JSON-LD Parser: No 'BreadcrumbList' node found in 'json_ld' data."
        )
        return None, "json_ld_parser", FieldExtractionStatus.NOT_FOUND, 0

    logger.debug(
        f"Breadcrumbs JSON-LD Parser: Found raw list: {found_breadcrumbs}. Applying strict validation..."
    )

    # 4. Apply the SHARED, strict validation
    cleaned = clean_and_filter_breadcrumbs(found_breadcrumbs)

    if cleaned:
        logger.debug(f"Breadcrumbs JSON-LD Parser: Validation passed: {cleaned}")
        return (
            cleaned,
            "json-ld(@type=BreadcrumbList)",
            FieldExtractionStatus.JSON_LD,
            150,
        )

    logger.debug(
        "Breadcrumbs JSON-LD Parser: Raw list failed strict validation (e.g., too short)."
    )
    return None, "json_ld_parser", FieldExtractionStatus.NOT_FOUND, 0
