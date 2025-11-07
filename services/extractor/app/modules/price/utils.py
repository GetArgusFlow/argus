# argus/services/extractor/app/modules/price/utils.py

import re
from typing import Optional


def clean_price_text(text: str) -> Optional[float]:
    """
    Cleans up the price string and converts it to a float.
    Supports different notations (with commas or periods as decimal separators).
    """
    if not text:
        return None

    cleaned_text = re.sub(
        r"[^\d.,]+", "", text
    )  # Remove everything except digits, periods, and commas
    cleaned_text = cleaned_text.replace("\u200e", "").replace("\u200f", "").strip()

    if not cleaned_text:
        return None

    # First, check if the last comma or period is the decimal separator.
    # If there is more than one period, and a comma, then the comma is the decimal separator.
    if "," in cleaned_text and "." in cleaned_text:
        if cleaned_text.rfind(",") > cleaned_text.rfind("."):
            # Format: 1.234,56
            cleaned_text = cleaned_text.replace(".", "").replace(",", ".")
        else:
            # Format: 1,234.56
            cleaned_text = cleaned_text.replace(",", "")
    elif "," in cleaned_text:
        # Format: 1234,56 or 1,234
        cleaned_text = cleaned_text.replace(",", ".")

    try:
        price = float(cleaned_text)
        return price
    except ValueError:
        return None
