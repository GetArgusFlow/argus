# argus/services/extractor/app/modules/image/utils.py

import re
from typing import Optional
from loguru import logger


def is_valid_image_url(url: Optional[str]) -> bool:
    """
    Validates a URL as a valid image URL.
    """
    if not url:
        return False

    # Basic validation of the URL, must start with http(s) and have a common extension
    if not re.match(r"^https?://.*\.(jpg|jpeg|png|gif|webp|bmp)$", url, re.IGNORECASE):
        logger.debug(
            f"Image validation: URL '{url}' does not look like a valid image URL."
        )
        return False

    # URLs that are too short are often invalid or data URIs
    if len(url) < 10:
        logger.debug(f"Image validation: URL '{url}' is too short.")
        return False

    return True
