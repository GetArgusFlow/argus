# argus/services/extractor/app/modules/price/parsers/json_ld_parser.py

from typing import Optional, Tuple
from loguru import logger
from app.core.models import FieldExtractionStatus
from app.core.context import shared_context
from app.modules.price.utils import clean_price_text


def parse_json_ld() -> Tuple[Optional[float], str, FieldExtractionStatus, int]:
    """
    Extracts price from the 'json_ld' data in shared_context.
    """
    logger.debug("JSON-LD Parser: Searching for price in JSON-LD data.")

    json_ld_data = shared_context.get("json_ld")
    if not isinstance(json_ld_data, list):
        return None, "json_ld_parser", FieldExtractionStatus.NOT_FOUND, 0

    for node in json_ld_data:
        if not isinstance(node, dict):
            continue

        # Look for price in an 'offers' node (dict or list)
        offers = node.get("offers")
        offer_list = []
        if isinstance(offers, dict):
            offer_list = [offers]
        elif isinstance(offers, list):
            offer_list = offers

        for offer in offer_list:
            if not isinstance(offer, dict):
                continue

            # Find the price, looking at 'lowPrice' first, then 'price'
            price_raw = offer.get("lowPrice") or offer.get("price")

            # If not found, check a nested 'priceSpecification'
            if price_raw is None:
                price_spec = offer.get("priceSpecification")
                if isinstance(price_spec, dict):
                    price_raw = price_spec.get("minPrice") or price_spec.get("price")

            if price_raw is not None:
                price_float = clean_price_text(str(price_raw))
                if price_float is not None:
                    logger.debug(
                        f"JSON-LD Parser: Found price '{price_float}' via 'json_ld.offers'."
                    )
                    return (
                        price_float,
                        "json_ld.offers.price",
                        FieldExtractionStatus.JSON_LD,
                        200,
                    )

    logger.debug("JSON-LD Parser: No price found in JSON-LD data.")
    return None, "json_ld_parser", FieldExtractionStatus.NOT_FOUND, 0
