# argus/services/extractor/app/modules/open_graph/parsers/metadata_parser.py

from typing import Dict, Any
from loguru import logger


def parse_metadata(og_tags: Dict[str, Any], extracted_fields: Dict[str, Any]):
    """
    Extracts title, description, and image from the Open Graph tags.
    Modifies the 'extracted_fields' dictionary in-place.
    """
    logger.debug(
        "Metadata Parser: Starting extraction of title, description, and image."
    )

    # Title
    title = og_tags.get("title")
    if title:
        extracted_fields["title"] = title
        logger.debug(f"Metadata Parser: Title '{title}' found.")

    # Description
    description = og_tags.get("description")
    if description:
        extracted_fields["description"] = description
        logger.debug("Metadata Parser: Description found.")

    # Image
    image = og_tags.get("image")
    if image:
        extracted_fields["image"] = image
        logger.debug(f"Metadata Parser: Image '{image}' found.")
