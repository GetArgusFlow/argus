# argus/services/extractor/app/modules/availability/parsers/title_parser.py

from typing import Optional, Tuple
from bs4 import BeautifulSoup
from loguru import logger
from app.core.models import FieldExtractionStatus
from app.modules.availability.utils import find_availability_status


def parse_title(
    soup: BeautifulSoup,
) -> Tuple[Optional[str], str, FieldExtractionStatus, int]:
    """
    Extracts the availability status from the page title as a last resort.
    """
    logger.debug("Title Parser: Checking the title as a last resort.")
    title_tag = soup.find("title")

    if title_tag:
        title_text = title_tag.get_text(strip=True).lower()

        status = find_availability_status(title_text)

        if status:
            logger.debug(f"Title Parser: Found status '{status}' in the title.")
            return status, "title", FieldExtractionStatus.MODULE_HEURISTIC, 50

    return None, "title_parser", FieldExtractionStatus.NOT_FOUND, 0
