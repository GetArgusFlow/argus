# argus/services/extractor/app/modules/price/parsers/open_graph_parser.py

from typing import Optional, Tuple
from loguru import logger
from app.core.models import FieldExtractionStatus
from app.core.context import shared_context
from app.modules.price.utils import clean_price_text


def parse_open_graph() -> Tuple[Optional[float], str, FieldExtractionStatus, int]:
    """
    Extracts price from the 'open_graph' data in shared_context.
    """
    logger.debug("Open Graph Parser: Searching for price in OG data.")

    og_data = shared_context.get("open_graph")
    if not isinstance(og_data, dict):
        return None, "open_graph_parser", FieldExtractionStatus.NOT_FOUND, 0

    # Standard keys are 'og:price:amount' or 'product:price:amount'
    # We assume the open_graph module provides these as 'price:amount'
    price_raw = og_data.get("price:amount") or og_data.get("product:price:amount")

    if price_raw is not None:
        price_float = clean_price_text(str(price_raw))
        if price_float is not None:
            logger.debug(
                f"Open Graph Parser: Found price '{price_float}' via 'og:price:amount'."
            )
            return price_float, "og:price:amount", FieldExtractionStatus.OPEN_GRAPH, 190

    logger.debug("Open Graph Parser: No price found in OG data.")
    return None, "open_graph_parser", FieldExtractionStatus.NOT_FOUND, 0
