# argus/services/extractor/app/modules/brand/parsers/title_parser.py

import re
from typing import Optional, Tuple, Any
from bs4 import BeautifulSoup
from loguru import logger
from app.core.types import FieldExtractionStatus
from app.modules.brand.utils import (
    is_plausible_brand,
    get_main_title_content,
    find_explicit_brands,
)


def parse_from_title(
    soup: BeautifulSoup, nlp_model: Any
) -> Tuple[Optional[str], str, FieldExtractionStatus, int]:
    """
    Extracts the brand name based on patterns in the product title.
    """
    logger.debug("Title Parser: Checking title for brand patterns.")
    main_title_text, selector_title = get_main_title_content(soup)
    if not main_title_text:
        return None, "title_parser", FieldExtractionStatus.NOT_FOUND, 0

    # First, find any explicitly mentioned brands on the page to use for validation.
    explicit_brands_on_page = find_explicit_brands(soup)
    if not explicit_brands_on_page:
        logger.debug(
            "Title Parser: No explicit brands found on page for validation. Skipping Heuristic 1."
        )
    else:
        # Heuristic 1: Check N-grams (word combinations) from the title against explicit brands.
        # We iterate from the longest possible word combination (the whole title)
        # down to single words, returning the first (and therefore longest)
        # plausible match that is also in the explicit_brands_on_page set.

        words = main_title_text.split(" ")
        n_words = len(words)

        for length in range(n_words, 0, -1):  # From n_words down to 1
            for i in range(n_words - length + 1):  # Sliding window start index
                j = i + length  # Sliding window end index

                # Construct the candidate phrase
                candidate_phrase = " ".join(words[i:j])

                # Basic cleaning: remove leading/trailing punctuation and whitespace
                # This handles cases like " (Brand) " or "Brand,"
                candidate_phrase = candidate_phrase.strip().strip(".,;:|()[]{}")

                if not candidate_phrase:  # Skip if stripping left an empty string
                    continue

                candidate_lower = candidate_phrase.lower()

                # VALIDATION: Check if this phrase is one of the explicit brands
                if candidate_lower in explicit_brands_on_page:
                    # PLAUSIBILITY: Check if it's a plausible brand name
                    if is_plausible_brand(candidate_phrase, nlp_model):
                        logger.debug(
                            f"Title Parser: Found via title (n-gram, validated): '{candidate_phrase}'"
                        )
                        return (
                            candidate_phrase,
                            f"{selector_title} (n-gram match)",
                            FieldExtractionStatus.MODULE_HEURISTIC,
                            110,
                        )
                    else:
                        logger.debug(
                            f"Title Parser: N-gram candidate '{candidate_phrase}' matched explicit brand, but failed plausibility. Continuing search..."
                        )
                        # We continue, because a shorter sub-phrase might be plausible
                        # e.g., "Douwe Egberts Junk" might match but fail plausibility,
                        # while "Douwe Egberts" will match and pass later.

        logger.debug(
            "Title Parser: Heuristic 1 (n-gram match) found no validated brand."
        )

    # Heuristic 2: Pattern "Brand - Product"
    match = re.match(r"(.+?)\s*[-–—]\s*(.+)", main_title_text)
    if match:
        candidate_brand = match.group(1).strip()
        if is_plausible_brand(candidate_brand, nlp_model):
            logger.debug(
                f"Title Parser: Found via title pattern 'Brand - Product': {candidate_brand}"
            )
            return (
                candidate_brand,
                f'{selector_title} (pattern "Brand - Product")',
                FieldExtractionStatus.MODULE_HEURISTIC,
                100,
            )

    # Heuristic 3: Pattern "Product (Brand)"
    match = re.search(r"\(([^)]+)\)$", main_title_text)
    if match:
        candidate_brand = match.group(1).strip()
        if is_plausible_brand(candidate_brand, nlp_model):
            logger.debug(
                f"Title Parser: Found via title pattern 'Product (Brand)': {candidate_brand}"
            )
            return (
                candidate_brand,
                f'{selector_title} (pattern "Product (Brand)")',
                FieldExtractionStatus.MODULE_HEURISTIC,
                95,
            )

    return None, "title_parser", FieldExtractionStatus.NOT_FOUND, 0
