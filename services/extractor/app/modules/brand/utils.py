# argus/services/extractor/app/modules/brand/utils.py

import re
from typing import Optional, Tuple, Any
from bs4 import BeautifulSoup
from loguru import logger

GENERIC_STOP_WORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "for",
    "with",
    "plus",
    "pro",
    "max",
    "mini",
    "ultra",
    "lite",
    "premium",
    "standard",
    "original",
    "official",
    "generic",
    "compatible",
    "universal",
    "charger",
    "adapter",
    "cable",
    "power",
    "output",
    "input",
    "watt",
    "volt",
    "amp",
    "store",
    "website",
    "visit",
    "page",
    "product",
}


def _is_likely_model_number(text: str) -> bool:
    """
    A specific heuristic to check if a string looks like a model number.
    A model number typically contains a mix of letters and digits.
    """
    # Rule 1: Must contain at least one digit.
    if not any(char.isdigit() for char in text):
        return False

    # Rule 2: Must contain at least one letter.
    if not any(char.isalpha() for char in text):
        return False

    # Rule 3: Check for common model number patterns (e.g., ABC-123, 123-ABC, X1)
    # This regex is more specific: it looks for sequences of letters/numbers mixed together.
    if re.fullmatch(r"([A-Z0-9]+[-./]?[A-Z0-9]+)+", text, re.IGNORECASE):
        return True

    return False


def is_plausible_brand(candidate_brand: Optional[str], nlp_model: Any) -> bool:
    """
    Validates if a candidate string could plausibly be a brand name using a series
    of linguistic and rule-based heuristics.
    """
    if not candidate_brand:
        return False

    cleaned_brand = candidate_brand.strip()

    # Rule-based Heuristics (Fast Checks)

    # 1. Check length
    if not (2 <= len(cleaned_brand) <= 50):
        return False

    # 2. NEW: Check if it's likely a model number using our smarter function
    if _is_likely_model_number(cleaned_brand):
        logger.debug(
            f"Brand validation: '{cleaned_brand}' looks like a model number. Rejected."
        )
        return False

    # 3. Reject if purely numeric
    if cleaned_brand.isdigit():
        return False

    # 4. Reject if it's a generic stop word
    if cleaned_brand.lower() in GENERIC_STOP_WORDS:
        return False

    # 5. Reject if it's too many words
    if len(cleaned_brand.split()) > 4:
        return False

    # Linguistic Heuristics (Smarter Checks)
    if not nlp_model:
        logger.warning(
            "Brand validation: NLP model not provided, skipping linguistic checks."
        )
        return True  # Fallback to true if NLP model is missing

    doc = nlp_model(cleaned_brand)

    # A plausible brand name must contain at least one Proper Noun (PROPN).
    if not any(token.pos_ == "PROPN" for token in doc):
        logger.debug(
            f"Brand validation: '{cleaned_brand}' rejected: contains no proper nouns."
        )
        return False

    return True


def get_main_title_content(soup: BeautifulSoup) -> Tuple[Optional[str], str]:
    """
    Finds the main title of the page (H1 or <title> tag).
    """
    title_selectors = [
        'h1[itemprop="name"]',
        "h1.product-title",
        "h1.item-name",
        "h1.product__title",
        "h1.pdp-title",
        "h1",
    ]
    for selector in title_selectors:
        element = soup.select_one(selector)
        if element:
            return element.get_text(strip=True), selector

    # Fallback to the main <title> tag
    if soup.title and soup.title.string:
        return soup.title.get_text(strip=True), "title"

    return None, "NO_TITLE_FOUND"


def check_brand_in_main_title(candidate_brand: str, soup: BeautifulSoup) -> bool:
    """
    Checks if the candidate brand name (approximately) appears in the H1 or TITLE tag.
    """
    title_text_content, _ = get_main_title_content(soup)
    if not title_text_content:
        return False

    # Create a regex pattern to find the brand as a whole word
    pattern = r"\b" + re.escape(candidate_brand) + r"\b"
    if re.search(pattern, title_text_content, re.IGNORECASE):
        logger.debug(
            f"Brand validation: Candidate '{candidate_brand}' validated in page title."
        )
        return True

    return False


def find_explicit_brands(soup: BeautifulSoup) -> set[str]:
    """
    Finds all potential brand names from elements that are explicitly
    marked with brand-related classes or itemprop attributes.
    Returns a set of cleaned, lowercased brand candidates.
    """
    explicit_brands = set()

    # Search for elements with itemprop="brand"
    brand_itemprop_tags = soup.find_all(itemprop="brand")
    for tag in brand_itemprop_tags:
        text = tag.get("content") or tag.get_text(strip=True)
        if text:
            explicit_brands.add(text.strip().lower())

    # Search for common brand-related class names
    brand_class_regex = re.compile(
        r"brand|manufacturer|vendor|product-brand", re.IGNORECASE
    )
    brand_elements = soup.find_all(class_=brand_class_regex)
    for element in brand_elements:
        text = element.get_text(strip=True)
        if text:
            explicit_brands.add(text.strip().lower())

    return explicit_brands
