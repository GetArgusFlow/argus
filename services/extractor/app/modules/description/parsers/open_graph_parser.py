# app/modules/description/parsers/open_graph_parser.py

from typing import Optional, Tuple, Any
from loguru import logger
from app.core.models import FieldExtractionStatus
from app.core.context import shared_context
from app.modules.description.utils import clean_and_validate_description


def parse_open_graph(
    nlp_model: Any = None,
) -> Tuple[Optional[str], str, FieldExtractionStatus, int]:
    """
    Extracts description from the 'open_graph' data in shared_context.
    """
    logger.debug("Open Graph Parser: Searching for description in OG data.")

    og_data = shared_context.get("open_graph")
    if not isinstance(og_data, dict):
        return None, "open_graph_parser", FieldExtractionStatus.NOT_FOUND, 0

    # The open_graph module populates the 'description' key
    desc_text = og_data.get("description")

    if isinstance(desc_text, str):
        cleaned_desc = clean_and_validate_description(desc_text, nlp_model)
        if cleaned_desc:
            logger.debug(
                f"Open Graph Parser: Found via og:description: {cleaned_desc[:100]}..."
            )
            # Give this a very high score, just under JSON-LD
            return cleaned_desc, "og:description", FieldExtractionStatus.OPEN_GRAPH, 275

    logger.debug("Open Graph Parser: No description found in OG data.")
    return None, "open_graph_parser", FieldExtractionStatus.NOT_FOUND, 0
