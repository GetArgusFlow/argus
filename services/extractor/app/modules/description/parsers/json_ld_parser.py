# argus/services/extractor/app/modules/description/parsers/json_ld_parser.py

from typing import Optional, Tuple, Any
from loguru import logger
from app.core.models import FieldExtractionStatus
from app.core.context import shared_context
from app.modules.description.utils import clean_and_validate_description


def parse_json_ld(
    nlp_model: Any = None,
) -> Tuple[Optional[str], str, FieldExtractionStatus, int]:
    """
    Extracts description from the 'json_ld' data in shared_context.
    """
    logger.debug("JSON-LD Parser: Searching for description in JSON-LD data.")

    json_ld_data = shared_context.get("json_ld")
    if not isinstance(json_ld_data, list):
        return None, "json_ld_parser", FieldExtractionStatus.NOT_FOUND, 0

    for node in json_ld_data:
        if not isinstance(node, dict):
            continue

        # The description can be at the top level of any node
        desc_text = node.get("description")
        if isinstance(desc_text, str):
            cleaned_desc = clean_and_validate_description(desc_text, nlp_model)
            if cleaned_desc:
                logger.debug(
                    f"JSON-LD Parser: Found via json_ld.description: {cleaned_desc[:100]}..."
                )
                # Give this the highest score
                return (
                    cleaned_desc,
                    "json_ld.description",
                    FieldExtractionStatus.JSON_LD,
                    300,
                )

    logger.debug("JSON-LD Parser: No description found in JSON-LD data.")
    return None, "json_ld_parser", FieldExtractionStatus.NOT_FOUND, 0
