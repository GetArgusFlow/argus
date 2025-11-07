# argus/services/extractor/app/modules/brand/parsers/meta_parser.py

import re
from typing import Optional, Tuple, Any
from bs4 import BeautifulSoup
from loguru import logger
from app.core.models import FieldExtractionStatus
from app.modules.brand.utils import is_plausible_brand, check_brand_in_main_title


def parse_meta_tags(
    soup: BeautifulSoup, nlp_model: Any
) -> Tuple[Optional[str], str, FieldExtractionStatus, int]:
    """
    Extracts the brand name from <meta> tags and itemprop attributes.
    (Open Graph logic has been moved to open_graph_parser.py)
    """
    logger.debug("Meta Parser: Searching in <meta> tags and itemprop attributes.")

    # Priority 1: Amazon-specific 'byline' link
    byline_link = soup.select_one("#bylineInfo, #brand")
    if byline_link:
        brand_name_candidate = byline_link.get_text(strip=True)
        # Sometimes it says "Bezoek de XXXXX Store" (Visit the XXXXX Store)
        match_store = re.search(
            r"Bezoek de\s*(.*?)\s*Store", brand_name_candidate, re.IGNORECASE
        )
        if match_store:
            brand_name_candidate = match_store.group(1).strip()

        if is_plausible_brand(
            brand_name_candidate, nlp_model
        ) and check_brand_in_main_title(brand_name_candidate, soup):
            logger.debug(
                f"Meta Parser: Found via byline link ({byline_link.get('id') or byline_link.name}): {brand_name_candidate}"
            )
            return (
                brand_name_candidate,
                f"#{byline_link.get('id') or byline_link.name}",
                FieldExtractionStatus.MODULE_HEURISTIC,
                200,
            )

    # Priority 2: General itemprop-meta tag
    brand_itemprop_meta = soup.find("meta", itemprop="brand")
    if brand_itemprop_meta and brand_itemprop_meta.get("content"):
        brand_name_candidate = brand_itemprop_meta["content"].strip()
        if is_plausible_brand(
            brand_name_candidate, nlp_model
        ) and check_brand_in_main_title(brand_name_candidate, soup):
            logger.debug(
                f"Meta Parser: Found via meta[itemprop='brand']: {brand_name_candidate}"
            )
            return (
                brand_name_candidate,
                'meta[itemprop="brand"]',
                FieldExtractionStatus.MODULE_HEURISTIC,
                190,
            )

    # Priority 3: itemprop-tag (span, div, etc.)
    brand_itemprop_tag = soup.find(
        re.compile(r"span|div|p|a|strong|b"), itemprop="brand"
    )
    if brand_itemprop_tag and brand_itemprop_tag.get_text(strip=True):
        brand_name_candidate = brand_itemprop_tag.get_text(strip=True)
        if is_plausible_brand(
            brand_name_candidate, nlp_model
        ) and check_brand_in_main_title(brand_name_candidate, soup):
            logger.debug(
                f"Meta Parser: Found via {brand_itemprop_tag.name}[itemprop='brand']: {brand_name_candidate}"
            )
            return (
                brand_name_candidate,
                f'{brand_itemprop_tag.name}[itemprop="brand"]',
                FieldExtractionStatus.MODULE_HEURISTIC,
                185,
            )

    # REMOVED OPEN GRAPH PARSING
    # The 'og:brand' logic was here, but is now handled by open_graph_parser.py

    return None, "meta_parser", FieldExtractionStatus.NOT_FOUND, 0
