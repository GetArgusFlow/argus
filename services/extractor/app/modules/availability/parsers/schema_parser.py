# argus/services/extractor/app/modules/availability/parsers/schema_parser.py

import re
from typing import Optional, Tuple
from bs4 import BeautifulSoup
from loguru import logger
from app.core.models import FieldExtractionStatus
from app.modules.availability.utils import find_availability_status


def parse_schema(
    soup: BeautifulSoup,
) -> Tuple[Optional[str], str, FieldExtractionStatus, int]:
    """
    Extracts the availability status from Schema.org microdata.
    """
    logger.debug("Schema Parser: Searching for itemprop='availability'.")

    # Find the link tag with itemprop="availability"
    avail_link_tag = soup.find("link", itemprop="availability")
    if avail_link_tag and avail_link_tag.get("href"):
        href = avail_link_tag["href"].lower()
        if "instock" in href:
            return (
                "In Stock",
                'link[itemprop="availability"]',
                FieldExtractionStatus.MODULE_HEURISTIC,
                100,
            )
        if "outofstock" in href:
            return (
                "Out of Stock",
                'link[itemprop="availability"]',
                FieldExtractionStatus.MODULE_HEURISTIC,
                100,
            )
        if "preorder" in href:
            return (
                "Pre-order",
                'link[itemprop="availability"]',
                FieldExtractionStatus.MODULE_HEURISTIC,
                100,
            )

    # Find other tags (span, div) with itemprop="availability"
    avail_tag = soup.find(re.compile(r"span|div|p"), itemprop="availability")
    if avail_tag:
        text = avail_tag.get_text(strip=True)
        content = avail_tag.get("content", "")

        combined_text = f"{text} {content}".strip()
        status = find_availability_status(combined_text)

        if status:
            return (
                status,
                f'{avail_tag.name}[itemprop="availability"]',
                FieldExtractionStatus.MODULE_HEURISTIC,
                98,
            )

    return None, "schema_parser", FieldExtractionStatus.NOT_FOUND, 0
