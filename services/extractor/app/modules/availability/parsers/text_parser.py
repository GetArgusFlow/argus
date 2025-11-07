# argus/services/extractor/app/modules/availability/parsers/text_parser.py

import re
from typing import Optional, Tuple
from bs4 import BeautifulSoup
from loguru import logger
from app.core.models import FieldExtractionStatus
from app.modules.availability.utils import find_availability_status
from app.utils.pattern_manager import pattern_manager


def parse_textual_indicators(
    soup: BeautifulSoup,
) -> Tuple[Optional[str], str, FieldExtractionStatus, int]:
    """
    Extracts the availability status based on text in relevant elements.
    """
    logger.debug("Text Parser: Searching for textual indicators in relevant sections.")

    check_tags = soup.find_all(
        re.compile(r"div|span|p|button|a"),
        # Use the dynamic regex from PatternManager instead of a hardcoded one
        class_=pattern_manager.get_compiled_regex("availability_class_regex"),
        limit=10,
    )

    for tag in check_tags:
        text = (
            tag.get_text(strip=True).lower()
            or tag.get("title", "").lower()
            or tag.get("value", "").lower()
        )
        if not text:
            continue

        status = find_availability_status(text)
        if status:
            selector_detail = f"{tag.name}"
            if tag.get("class"):
                selector_detail += f".{'.'.join(tag['class'])}"
            elif tag.get("id"):
                selector_detail += f"#{tag['id']}"

            logger.debug(
                f"Text Parser: Found status '{status}' via textual indicator: {text[:50]}"
            )
            return (
                status,
                f"{selector_detail} (textual)",
                FieldExtractionStatus.MODULE_HEURISTIC,
                90,
            )

    return None, "text_parser", FieldExtractionStatus.NOT_FOUND, 0
