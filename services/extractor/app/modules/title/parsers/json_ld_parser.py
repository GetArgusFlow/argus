# argus/services/extractor/app/modules/title/parsers/json_ld_parser.py

from typing import Optional, Tuple
from loguru import logger
from app.core.models import FieldExtractionStatus
from app.core.context import shared_context
from app.modules.title.utils import clean_title


def parse_json_ld() -> Tuple[Optional[str], str, FieldExtractionStatus, int]:
    """
    Extracts the title (name) from the 'json_ld' data in shared_context.
    """
    logger.debug("JSON-LD Parser: Searching for title (name) in JSON-LD data.")

    json_ld_data = shared_context.get("json_ld")
    if not isinstance(json_ld_data, list):
        return None, "json_ld_parser", FieldExtractionStatus.NOT_FOUND, 0

    for node in json_ld_data:
        if not isinstance(node, dict):
            continue

        # The 'name' key is used for title in Product, Offer, etc.
        title_text = node.get("name")

        if isinstance(title_text, str):
            cleaned_title = clean_title(title_text)
            if cleaned_title and len(cleaned_title) > 5:
                logger.debug(f"JSON-LD Parser: Found via json_ld.name: {cleaned_title}")
                # Give this the highest score
                return cleaned_title, "json_ld.name", FieldExtractionStatus.JSON_LD, 300

    logger.debug("JSON-LD Parser: No title (name) found in JSON-LD data.")
    return None, "json_ld_parser", FieldExtractionStatus.NOT_FOUND, 0
