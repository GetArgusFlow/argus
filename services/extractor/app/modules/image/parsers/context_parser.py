# argus/services/extractor/app/modules/image/parsers/context_parser.py

import re
from typing import Optional, Tuple, Set
from bs4 import BeautifulSoup, Tag
from loguru import logger
from app.core.models import FieldExtractionStatus
from app.modules.image.utils import is_valid_image_url


def parse_from_product_context(
    soup: BeautifulSoup, processed_elements: Set[Tag]
) -> Tuple[Optional[str], str, FieldExtractionStatus, int]:
    """
    Extracts the first reasonable image from product-related sections.
    """
    logger.debug("Context Parser: Searching in general product-related sections.")

    product_section_elements = soup.select(
        'div[id*="product"], div[class*="product"], main, article'
    )
    for section in product_section_elements:
        if section in processed_elements:
            continue

        # We search for all images, not just the first one, to have a better chance
        image_tags = section.find_all("img", src=re.compile(r"https?://"))
        for img_tag in image_tags:
            img_src = img_tag.get("src")
            if not img_src or not is_valid_image_url(img_src):
                continue

            width = img_tag.get("width")
            height = img_tag.get("height")

            # If we have dimensions, we validate them.
            if width and height:
                try:
                    # Remove 'px' etc. and convert to int
                    w = int(re.sub(r"\D", "", width))
                    h = int(re.sub(r"\D", "", height))

                    # If the image is PROVEN to be too small, we skip it.
                    if w < 50 or h < 50:
                        logger.debug(
                            f"Context Parser: Image skipped due to being too small: {w}x{h}"
                        )
                        continue  # Continue to the next image in the section
                except (ValueError, TypeError):
                    # Dimensions are not a valid number, so we ignore them and proceed.
                    pass

            # If the image is large enough, OR if there are no dimensions,
            # we accept it and stop searching.
            logger.debug(f"Context Parser: Found in product section: {img_src}")
            processed_elements.add(img_tag)
            return (
                img_src,
                "img_in_product_section",
                FieldExtractionStatus.MODULE_HEURISTIC,
                100,
            )

    return None, "context_parser", FieldExtractionStatus.NOT_FOUND, 0
