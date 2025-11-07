# argus/services/extractor/app/modules/image/parsers/open_graph_parser.py

from typing import Optional, Tuple
from loguru import logger
from app.core.models import FieldExtractionStatus
from app.core.context import shared_context
from app.modules.image.utils import is_valid_image_url


def parse_open_graph() -> Tuple[Optional[str], str, FieldExtractionStatus, int]:
    """
    Extracts the image URL from the 'open_graph' data in shared_context.
    """
    logger.debug("Open Graph Parser: Searching for image in OG data.")

    og_data = shared_context.get("open_graph")
    if not isinstance(og_data, dict):
        return None, "open_graph_parser", FieldExtractionStatus.NOT_FOUND, 0

    # The open_graph module populates the 'image' key from 'og:image'
    image_url = og_data.get("image")

    if image_url and is_valid_image_url(image_url):
        logger.debug(f"Open Graph Parser: Found via og:image: {image_url}")
        # Give this a high score, just under JSON-LD
        return image_url, "og:image", FieldExtractionStatus.OPEN_GRAPH, 190

    logger.debug("Open Graph Parser: No image found in OG data.")
    return None, "open_graph_parser", FieldExtractionStatus.NOT_FOUND, 0
