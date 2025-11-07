# argus/services/extractor/app/modules/brand/parsers/open_graph_parser.py

from typing import Optional, Tuple, Any
from bs4 import BeautifulSoup
from loguru import logger
from app.core.models import FieldExtractionStatus
from app.core.context import shared_context
from app.modules.brand.utils import is_plausible_brand, check_brand_in_main_title


def parse_open_graph(
    soup: BeautifulSoup, nlp_model: Any
) -> Tuple[Optional[str], str, FieldExtractionStatus, int]:
    """
    Extracts brand from the 'open_graph' data in shared_context.
    """
    logger.debug("Open Graph Parser: Searching for brand in OG data.")

    og_data = shared_context.get("open_graph")
    if not isinstance(og_data, dict):
        return None, "open_graph_parser", FieldExtractionStatus.NOT_FOUND, 0

    # Standard keys are 'og:brand' or 'product:brand'
    brand_name_candidate = og_data.get("brand") or og_data.get("product:brand")

    if isinstance(brand_name_candidate, str):
        brand_name_candidate = brand_name_candidate.strip()
        # Validate it
        if is_plausible_brand(
            brand_name_candidate, nlp_model
        ) and check_brand_in_main_title(brand_name_candidate, soup):
            logger.debug(
                f"Open Graph Parser: Found validated brand '{brand_name_candidate}' via 'og:brand'."
            )
            return (
                brand_name_candidate,
                "og:brand",
                FieldExtractionStatus.OPEN_GRAPH,
                240,
            )

    logger.debug("Open Graph Parser: No brand found in OG data.")
    return None, "open_graph_parser", FieldExtractionStatus.NOT_FOUND, 0
