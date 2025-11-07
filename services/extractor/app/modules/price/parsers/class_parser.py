# argus/services/extractor/app/modules/price/parsers/class_parser.py

import re
from typing import Optional, Tuple, Set
from bs4 import BeautifulSoup, Tag
from loguru import logger
from app.core.models import FieldExtractionStatus
from app.modules.price.utils import clean_price_text


def _reconstruct_price_from_fragments(tag: BeautifulSoup) -> Optional[str]:
    """
    Finds all text fragments within a tag, validates them, and combines them
    into a correct decimal number. Only accepts digits and currency symbols.
    """
    # Find all text nodes, including in nested tags
    all_strings = tag.find_all(string=True)

    number_parts = []
    for s in all_strings:
        cleaned_s = s.strip()
        if not cleaned_s:
            continue

        # Check if the fragment only contains digits, dots, commas, or currency symbols.
        # If it contains other letters (like in "other text"), the price is invalid.
        if re.search(r"[a-zA-Z]", cleaned_s) and not re.fullmatch(
            r"[\s\d.,€$£]*", cleaned_s, re.IGNORECASE
        ):
            logger.trace(
                f"Price reconstructor: Invalid text fragment found: '{cleaned_s}'"
            )
            return None  # Invalid text found

        # Get only the digits from the fragment
        digits = re.findall(r"\d+", cleaned_s)
        if digits:
            number_parts.extend(digits)

    if not number_parts:
        return None

    # Join the numeric parts. If there is more than one part,
    # the last one is considered the fraction.
    if len(number_parts) == 2:
        # e.g., ['1', '25'] becomes '1.25'
        return f"{'.'.join(number_parts[:-1])}.{number_parts[-1]}"
    else:
        # e.g., ['1.25'] or ['1,25'] remains itself
        return number_parts[0]


def parse_price_classes(
    soup: BeautifulSoup, processed_elements: Set[Tag]
) -> Tuple[Optional[float], str, FieldExtractionStatus, int]:
    """
    Extracts the price based on relevant CSS classes and IDs,
    with special logic for split prices.
    """
    price_tags = soup.find_all(
        re.compile(r"div|span|p|b|section"), class_=re.compile(r"price", re.IGNORECASE)
    )

    for tag in price_tags:
        if tag in processed_elements:
            continue

        # First, try to intelligently reconstruct the price from fragments
        text = _reconstruct_price_from_fragments(tag)

        # If that fails, fall back to the old, simple method
        if text is None:
            text = tag.get_text(strip=True)

        if not text:
            continue

        # The rest of your logic for checking 'old price' remains the same
        is_old_price = False
        parent_with_old_price = tag.find_parent(
            class_=re.compile(
                r"old-price|original-price|price-old|compare-price", re.IGNORECASE
            )
        )
        if parent_with_old_price:
            logger.debug(
                f"Class Parser: Skipped tag inside old price container: {text[:50]}"
            )
            is_old_price = True

        if not is_old_price:
            numerical_price = clean_price_text(text)
            if numerical_price is not None:
                selector_detail = (
                    f'{tag.name}[class*="{tag.get("class")[0] if tag.get("class") else ""}"]'
                    if tag.get("class")
                    else tag.name
                )
                logger.debug(
                    f"Class Parser: Found via class '{selector_detail}': {numerical_price}"
                )
                processed_elements.add(tag)
                return (
                    numerical_price,
                    selector_detail,
                    FieldExtractionStatus.MODULE_HEURISTIC,
                    100,
                )

    return None, "class_parser", FieldExtractionStatus.NOT_FOUND, 0
