# argus/services/extractor/app/utils/data_utils.py

import re
import unicodedata
from typing import Union, Optional
from loguru import logger


def clean_price_text(price_str: Optional[Union[str, float]]) -> Optional[float]:
    """
    Cleans and converts a price string to a float.
    Supports various European notations (with period or comma as decimal separator).
    """
    if price_str is None:
        return None
    if isinstance(price_str, (int, float)):
        return float(price_str)

    s = unicodedata.normalize("NFKC", str(price_str)).strip()
    s = re.sub(r"[^\d.,]", "", s)

    if "," in s:
        if "." in s and s.rfind(",") > s.rfind("."):
            # Format: 1.234,56
            s = s.replace(".", "").replace(",", ".")
        else:
            # Format: 1,234.56 (or 1234,56)
            s = s.replace(",", ".")

    try:
        return float(s)
    except ValueError:
        logger.debug(f"Data Utils: Could not parse price '{price_str}' to a float.")
        return None


def normalize_ean_candidate(ean_candidate: str) -> str:
    """
    Normalizes an EAN candidate by removing all non-numeric characters
    and padding to standard GTIN lengths if necessary.
    """
    if not isinstance(ean_candidate, str):
        ean_candidate = str(ean_candidate)

    ean_candidate = re.sub(r"\D", "", ean_candidate).strip()

    length = len(ean_candidate)
    if length == 12:
        return "0" + ean_candidate
    elif 8 < length < 13:
        return ean_candidate.zfill(13)
    elif 13 < length < 14:
        return ean_candidate.zfill(14)
    else:
        return ean_candidate


def is_valid_ean_checksum(ean_candidate: str) -> bool:
    """
    Validates an EAN (GTIN-8, -12, -13, -14) using the checksum calculation.
    The input is assumed to be already normalized.
    """
    ean_candidate = ean_candidate.strip()
    length = len(ean_candidate)

    if length not in [8, 12, 13, 14] or not ean_candidate.isdigit():
        return False

    digits = [int(d) for d in ean_candidate]
    check_digit = digits[-1]

    total_sum = 0
    for i in range(length - 1):
        digit = digits[length - 2 - i]
        total_sum += digit * (3 if (i % 2) == 0 else 1)

    calculated_check_digit = (10 - (total_sum % 10)) % 10
    return calculated_check_digit == check_digit


def normalize_availability(availability_str: Optional[str]) -> Optional[str]:
    """
    Normalizes availability strings to a standard format ("In Stock", etc.).
    """
    if not availability_str:
        return None

    lower_val = availability_str.lower()
    if "/" in lower_val:
        lower_val = lower_val.split("/")[-1]

    # Dutch and English keywords
    if (
        "instock" in lower_val
        or "available" in lower_val
        or "beschikbaar" in lower_val
        or "op voorraad" in lower_val
        or "direct leverbaar" in lower_val
    ):
        return "In Stock"
    if (
        "outofstock" in lower_val
        or "not in stock" in lower_val
        or "niet op voorraad" in lower_val
        or "uitverkocht" in lower_val
        or "sold out" in lower_val
    ):
        return "Out of Stock"
    if (
        "preorder" in lower_val
        or "expected" in lower_val
        or "verwacht" in lower_val
        or "voorbestellen" in lower_val
        or "verwachte levertijd" in lower_val
    ):
        return "Pre-order"

    return availability_str


def clean_text_and_remove_unicode(text: str) -> str:
    """Cleans up text and removes unicode characters and excess whitespace."""
    if not isinstance(text, str):
        return ""
    text = text.replace("\xa0", " ").replace("\n", " ").strip()
    return re.sub(r"\s+", " ", text)
