# argus/services/extractor/app/modules/image/parsers/amazon_parser.py

from typing import Optional, Tuple, Set
from bs4 import BeautifulSoup, Tag
from loguru import logger
from app.core.models import FieldExtractionStatus
from app.modules.image.utils import is_valid_image_url


def parse_amazon_selectors(
    soup: BeautifulSoup, processed_elements: Set[Tag]
) -> Tuple[Optional[str], str, FieldExtractionStatus, int]:
    """
    Extracts the image from Amazon-specific HTML elements.
    """
    logger.debug("Amazon Parser: Searching in Amazon-specific selectors.")

    amazon_image_selectors = [
        "#landingImage",
        "#imgTagWrapperId img",
        "#main-image-container img",
        "#mainImage",
        ".a-dynamic-image",
        "#imgBlkFront",
    ]

    for selector_str in amazon_image_selectors:
        img_element = soup.select_one(selector_str)
        if img_element and img_element.get("src"):
            if img_element in processed_elements:
                continue

            src = img_element["src"].strip()
            hires_src = img_element.get("data-old-hires") or img_element.get(
                "data-a-image-src"
            )

            # Try the high-resolution image first
            if hires_src and is_valid_image_url(hires_src.strip()):
                logger.debug(
                    f"Amazon Parser: Found via Amazon selector '{selector_str}' (hires): {hires_src}"
                )
                processed_elements.add(img_element)
                return (
                    hires_src.strip(),
                    selector_str + " (hires)",
                    FieldExtractionStatus.MODULE_HEURISTIC,
                    180,
                )

            # Validate the standard src if there is no high-resolution version
            elif is_valid_image_url(src):
                logger.debug(
                    f"Amazon Parser: Found via Amazon selector '{selector_str}': {src}"
                )
                processed_elements.add(img_element)
                return src, selector_str, FieldExtractionStatus.MODULE_HEURISTIC, 175

    return None, "amazon_parser", FieldExtractionStatus.NOT_FOUND, 0
