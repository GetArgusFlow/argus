# argus/services/extractor/app/modules/title/parsers/open_graph_parser.py

from typing import Optional, Tuple
from loguru import logger
from app.core.models import FieldExtractionStatus
from app.core.context import shared_context
from app.modules.title.utils import clean_title


def parse_open_graph() -> Tuple[Optional[str], str, FieldExtractionStatus, int]:
    """
    Extracts the title from the 'open_graph' data in shared_context.
    """
    logger.debug("Open Graph Parser: Searching for title in OG data.")

    og_data = shared_context.get("open_graph")
    if not isinstance(og_data, dict):
        return None, "open_graph_parser", FieldExtractionStatus.NOT_FOUND, 0

    # The open_graph module populates the 'title' key from 'og:title'
    title_text = og_data.get("title")

    if isinstance(title_text, str):
        cleaned_title = clean_title(title_text)
        if cleaned_title and len(cleaned_title) > 5:
            logger.debug(f"Open Graph Parser: Found via og:title: {cleaned_title}")
            # Give this a high score, just under JSON-LD
            return cleaned_title, "og:title", FieldExtractionStatus.OPEN_GRAPH, 275

    logger.debug("Open Graph Parser: No title found in OG data.")
    return None, "open_graph_parser", FieldExtractionStatus.NOT_FOUND, 0
