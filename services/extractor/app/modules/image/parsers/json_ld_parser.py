# argus/services/extractor/app/modules/image/parsers/json_ld_parser.py

from typing import Optional, Tuple
from loguru import logger
from app.core.models import FieldExtractionStatus
from app.core.context import shared_context
from app.modules.image.utils import is_valid_image_url


def parse_json_ld() -> Tuple[Optional[str], str, FieldExtractionStatus, int]:
    """
    Extracts the image URL from the 'json_ld' data in shared_context.
    """
    logger.debug("JSON-LD Parser: Searching for image in JSON-LD data.")

    json_ld_data = shared_context.get("json_ld")
    if not isinstance(json_ld_data, list):
        return None, "json_ld_parser", FieldExtractionStatus.NOT_FOUND, 0

    for node in json_ld_data:
        if not isinstance(node, dict):
            continue

        image_data = node.get("image")
        image_url = None

        if isinstance(image_data, str):
            image_url = image_data
        elif isinstance(image_data, dict):
            image_url = image_data.get("url")
        elif isinstance(image_data, list) and image_data:
            if isinstance(image_data[0], str):
                image_url = image_data[0]
            elif isinstance(image_data[0], dict):
                image_url = image_data[0].get("url")

        if image_url and is_valid_image_url(image_url):
            logger.debug(f"JSON-LD Parser: Found via json_ld.image: {image_url}")
            # Give this the highest score
            return image_url, "json_ld.image", FieldExtractionStatus.JSON_LD, 200

    logger.debug("JSON-LD Parser: No image found in JSON-LD data.")
    return None, "json_ld_parser", FieldExtractionStatus.NOT_FOUND, 0
