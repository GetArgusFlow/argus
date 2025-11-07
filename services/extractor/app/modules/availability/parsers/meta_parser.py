# argus/services/extractor/app/modules/availability/parsers/meta_parser.py

import re
from typing import Optional, Tuple
from bs4 import BeautifulSoup
from loguru import logger
from app.core.models import FieldExtractionStatus
from app.modules.availability.utils import find_availability_status


def parse_meta_tags(
    soup: BeautifulSoup,
) -> Tuple[Optional[str], str, FieldExtractionStatus, int]:
    """
    Extracts the availability status from general meta-tags.
    """
    logger.debug("Meta Parser: Searching in general meta-tags.")

    meta_name_avail = soup.find(
        "meta",
        attrs={
            "name": re.compile(
                r"availability|product:availability|item:availability", re.IGNORECASE
            )
        },
    )

    if meta_name_avail and meta_name_avail.get("content"):
        content = meta_name_avail["content"].lower()
        status = find_availability_status(content)

        if status:
            logger.debug(
                f"Meta Parser: Found status '{status}' via meta-tag: {content}"
            )
            return (
                status,
                f'meta[name="{meta_name_avail["name"]}"]',
                FieldExtractionStatus.MODULE_HEURISTIC,
                80,
            )

    return None, "meta_parser", FieldExtractionStatus.NOT_FOUND, 0
