# argus/services/extractor/app/modules/json_ld/parsers/breadcrumb_parser.py

from typing import Dict, Any
from loguru import logger
from app.modules.json_ld.utils import is_title_matching_breadcrumb


def parse_breadcrumbs(node: Dict[str, Any], extracted_fields: Dict[str, Any]):
    """
    Extracts breadcrumbs from a BreadcrumbList node.
    This populates the 'breadcrumbs' key within the 'json_ld' result object.
    It performs minimal filtering; the main 'breadcrumbs' module
    will re-validate this data for the final top-level field.
    """
    if node.get("@type", "").lower() != "breadcrumblist":
        return

    item_list_element = node.get("itemListElement")
    if not isinstance(item_list_element, list):
        return

    breadcrumbs = []

    # CRITICAL: Sort by position first to ensure correct order
    sorted_item_list = sorted(
        item_list_element,
        key=lambda x: x.get("position", 99) if isinstance(x, dict) else 99,
    )

    for item_data in sorted_item_list:
        crumb_name = None
        if (
            isinstance(item_data, dict)
            and "item" in item_data
            and isinstance(item_data["item"], dict)
        ):
            crumb_name = item_data["item"].get("name")
        elif isinstance(item_data, dict) and "name" in item_data:
            crumb_name = item_data.get("name")

        if crumb_name and isinstance(crumb_name, str):
            cleaned_crumb_name = crumb_name.strip()
            # Apply the original simple "home" filter
            if cleaned_crumb_name and cleaned_crumb_name.lower() != "home":
                breadcrumbs.append(cleaned_crumb_name)

    if breadcrumbs:
        # This logic was in the original file, so we keep it for the json_ld field
        extracted_title = extracted_fields.get("title")
        if extracted_title and is_title_matching_breadcrumb(
            extracted_title, breadcrumbs[-1]
        ):
            logger.debug(
                f"JSON-LD Breadcrumb Parser: Last crumb '{breadcrumbs[-1]}' matches title. Filtering for 'json_ld' field."
            )
            breadcrumbs.pop()

        if breadcrumbs:  # Check again if list is not empty
            extracted_fields["breadcrumbs"] = breadcrumbs
            logger.debug(
                f"JSON-LD Breadcrumb Parser: Found raw breadcrumbs for 'json_ld' field: {breadcrumbs}"
            )
