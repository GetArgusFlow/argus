# argus/services/extractor/app/modules/image/parsers/fallback_parser.py

import re
from typing import Optional, Tuple, Set
from bs4 import BeautifulSoup, Tag
from loguru import logger
from app.core.models import FieldExtractionStatus
from app.modules.image.utils import is_valid_image_url


def parse_largest_image_fallback(
    soup: BeautifulSoup, processed_elements: Set[Tag]
) -> Tuple[Optional[str], str, FieldExtractionStatus, int]:
    """
    Searches for the largest image in the body as a last resort.
    """
    logger.debug("Fallback Parser: Searching for largest image in body.")

    all_images = soup.find_all("img", src=re.compile(r"https?://"))
    best_image_url = None
    max_area = 0

    for img in all_images:
        if img in processed_elements:
            continue

        src = img.get("src")
        if not is_valid_image_url(src):
            continue

        width = img.get("width")
        height = img.get("height")
        if width and height:
            try:
                w = int(width)
                h = int(height)
                area = w * h
                if area > max_area and area > 10000:  # Minimum 100x100 pixels
                    max_area = area
                    best_image_url = src
            except ValueError:
                pass

    if best_image_url:
        logger.debug(f"Fallback Parser: Found via largest image: {best_image_url}")
        return (
            best_image_url,
            "largest_img_in_body",
            FieldExtractionStatus.GENERIC_FALLBACK,
            50,
        )

    return None, "fallback_parser", FieldExtractionStatus.NOT_FOUND, 0
