# argus/services/extractor/app/modules/brand/parsers/json_ld_parser.py

from typing import Optional, Tuple, Any
from bs4 import BeautifulSoup
from loguru import logger
from app.core.models import FieldExtractionStatus
from app.core.context import shared_context
from app.modules.brand.utils import is_plausible_brand, check_brand_in_main_title


def parse_json_ld(
    soup: BeautifulSoup, nlp_model: Any
) -> Tuple[Optional[str], str, FieldExtractionStatus, int]:
    """
    Extracts brand from the 'json_ld' data in shared_context.
    """
    logger.debug("JSON-LD Parser: Searching for brand in JSON-LD data.")

    json_ld_data = shared_context.get("json_ld")
    if not isinstance(json_ld_data, list):
        return None, "json_ld_parser", FieldExtractionStatus.NOT_FOUND, 0

    for node in json_ld_data:
        if not isinstance(node, dict):
            continue

        # Check for brand info, which can be a string or an object
        for key in ["brand", "manufacturer"]:
            brand_node = node.get(key)
            brand_name_candidate = None

            if isinstance(brand_node, str):
                brand_name_candidate = brand_node
            elif isinstance(brand_node, dict):
                brand_name_candidate = brand_node.get("name")

            if brand_name_candidate:
                brand_name_candidate = brand_name_candidate.strip()
                # Validate it for plausibility and check if it's in the title
                if is_plausible_brand(
                    brand_name_candidate, nlp_model
                ) and check_brand_in_main_title(brand_name_candidate, soup):
                    logger.debug(
                        f"JSON-LD Parser: Found validated brand '{brand_name_candidate}' via 'json_ld.{key}'."
                    )
                    return (
                        brand_name_candidate,
                        f"json_ld.{key}",
                        FieldExtractionStatus.JSON_LD,
                        250,
                    )

    logger.debug("JSON-LD Parser: No brand found in JSON-LD data.")
    return None, "json_ld_parser", FieldExtractionStatus.NOT_FOUND, 0
