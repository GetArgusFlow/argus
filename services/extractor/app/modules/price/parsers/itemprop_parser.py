# argus/services/extractor/app/modules/price/parsers/itemprop_parser.py

import re
from typing import Optional, Tuple, Set
from bs4 import BeautifulSoup, Tag
from loguru import logger
from app.core.models import FieldExtractionStatus
from app.modules.price.utils import clean_price_text


def parse_itemprop(
    soup: BeautifulSoup, processed_elements: Set[Tag]
) -> Tuple[Optional[float], str, FieldExtractionStatus, int]:
    """
    Extracts the price using itemprop="price" microdata.
    """
    # Priority 1a: meta tag
    price_meta = soup.find("meta", itemprop="price")
    if price_meta and price_meta.get("content"):
        price_val = clean_price_text(price_meta["content"].strip())
        if price_val is not None:
            logger.debug(
                f"Itemprop Parser: Found via meta[itemprop='price'] (content): {price_val}"
            )
            processed_elements.add(price_meta)
            return (
                price_val,
                'meta[itemprop="price"]',
                FieldExtractionStatus.MODULE_HEURISTIC,
                120,
            )

    # Priority 1b: other tags
    price_tag = soup.find(re.compile(r"span|div|b|p"), itemprop="price")
    if price_tag and price_tag.get_text(strip=True):
        price_val = clean_price_text(price_tag.get_text(strip=True))
        if price_val is not None:
            logger.debug(
                f"Itemprop Parser: Found via span/div[itemprop='price'] (text): {price_val}"
            )
            selector_detail = f'{price_tag.name}[itemprop="price"]'
            if price_tag.get("class"):
                selector_detail += f".{'.'.join(price_tag['class'])}"
            processed_elements.add(price_tag)
            return (
                price_val,
                selector_detail,
                FieldExtractionStatus.MODULE_HEURISTIC,
                115,
            )

    return None, "itemprop_parser", FieldExtractionStatus.NOT_FOUND, 0
