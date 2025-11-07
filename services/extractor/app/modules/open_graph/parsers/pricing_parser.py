# argus/services/extractor/app/modules/open_graph/parsers/pricing_parser.py

from typing import Dict, Any
from loguru import logger
from app.utils.data_utils import clean_price_text


def parse_pricing(og_tags: Dict[str, Any], extracted_fields: Dict[str, Any]):
    """
    Extracts price and currency from the Open Graph tags.
    Modifies the 'extracted_fields' dictionary in-place.
    """
    logger.debug("Pricing Parser: Starting price and currency extraction.")

    # Price
    price_amount_str = og_tags.get("price:amount")
    if price_amount_str:
        cleaned_price = clean_price_text(price_amount_str)
        if cleaned_price is not None:
            extracted_fields["price"] = cleaned_price
            logger.debug(f"Pricing Parser: Price {cleaned_price} found.")
        else:
            logger.debug(
                f"Pricing Parser: Could not convert price '{price_amount_str}' to float."
            )

    # Currency
    currency = og_tags.get("price:currency")
    if currency:
        extracted_fields["currency"] = currency
        logger.debug(f"Pricing Parser: Currency '{currency}' found.")
