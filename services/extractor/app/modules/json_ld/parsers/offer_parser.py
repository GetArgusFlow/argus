# argus/services/extractor/app/modules/json_ld/parsers/offer_parser.py

from typing import Dict, Any, List, Union
from loguru import logger
from app.modules.json_ld.utils import extract_value
from app.utils.data_utils import clean_price_text


def parse_offer_details(node: Dict[str, Any], extracted_fields: Dict[str, Any]):
    """
    Extracts price, currency, and availability from an Offer node or nested offers.
    Modifies the 'extracted_fields' dictionary in-place.
    """
    offers_data: Union[Dict[str, Any], List[Dict[str, Any]], None]

    if node.get("@type", "").lower() == "offer":
        offers_data = node
    else:
        offers_data = node.get("offers")

    offers_list: List[Dict[str, Any]] = []
    if isinstance(offers_data, dict):
        offers_list = [offers_data]
    elif isinstance(offers_data, list):
        offers_list = offers_data

    if not offers_list:
        logger.debug("Offer Parser: No offer data found in this node.")
        return

    # Process the first valid offer in the list
    offer = offers_list[0]

    # Price
    price_raw = offer.get("lowPrice") or offer.get("price")
    if price_raw is None:
        price_raw = extract_value(
            offer, "priceSpecification.minPrice"
        ) or extract_value(offer, "priceSpecification.price")

    if price_raw is not None and "price" not in extracted_fields:
        try:
            price_str_candidate = str(price_raw)
            price_float = clean_price_text(price_str_candidate)
            if price_float is not None:
                extracted_fields["price"] = price_float
                logger.debug(f"Offer Parser: Price found: {price_float}")
        except (ValueError, TypeError):
            logger.debug(
                f"Offer Parser: Error converting/cleaning price '{price_raw}'."
            )

    # Currency
    currency = offer.get("priceCurrency")
    if currency and "currency" not in extracted_fields:
        extracted_fields["currency"] = currency
        logger.debug(f"Offer Parser: Currency found: {currency}")

    # Availability
    availability_value = offer.get("availability")
    if isinstance(availability_value, str) and "availability" not in extracted_fields:
        availability_status = availability_value.split("/")[-1]
        valid_statuses = [
            "InStock",
            "OutOfStock",
            "PreOrder",
            "LimitedAvailability",
            "Discontinued",
            "SoldOut",
            "OnlineOnly",
            "InStoreOnly",
        ]
        if availability_status in valid_statuses:
            extracted_fields["availability"] = availability_status
            logger.debug(f"Offer Parser: Availability found: {availability_status}")
        else:
            logger.warning(
                f"Offer Parser: Unknown availability status in JSON-LD: '{availability_value}'."
            )
