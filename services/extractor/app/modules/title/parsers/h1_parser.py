# argus/services/extractor/app/modules/title/parsers/h1_parser.py

import re
from typing import Optional, Tuple, Set
from bs4 import BeautifulSoup, Tag
from loguru import logger
from app.core.models import FieldExtractionStatus
from app.modules.title.utils import clean_title


def parse_h1_tags(
    soup: BeautifulSoup, processed_elements: Set[Tag]
) -> Tuple[Optional[str], str, FieldExtractionStatus, int]:
    """
    Extracts the title from <h1> tags, including specific patterns and a generic fallback.
    """
    # Priority 1a: Specific Amazon H1 tag
    amazon_title_h1 = soup.select_one("#productTitle")
    if amazon_title_h1:
        extracted_title = amazon_title_h1.get_text(strip=True)
        cleaned_title = clean_title(extracted_title)
        if cleaned_title:
            logger.debug(f"H1 Parser: Found via Amazon #productTitle: {cleaned_title}")
            processed_elements.add(amazon_title_h1)
            return (
                cleaned_title,
                "#productTitle",
                FieldExtractionStatus.MODULE_HEURISTIC,
                250,
            )

    # Priority 1b: General H1 tags with specific attributes
    h1_with_attrs = soup.find("h1", itemprop="name") or soup.find(
        "h1",
        class_=re.compile(
            r"product-title|item-name|title|product__title", re.IGNORECASE
        ),
    )
    if h1_with_attrs and h1_with_attrs not in processed_elements:
        extracted_title = h1_with_attrs.get_text(strip=True)
        cleaned_title = clean_title(extracted_title)
        if cleaned_title and len(cleaned_title) > 5:
            logger.debug(
                f"H1 Parser: Found via H1 with specific attributes: {cleaned_title}"
            )
            processed_elements.add(h1_with_attrs)
            selector = (
                f'{h1_with_attrs.name}[itemprop="name"]'
                if h1_with_attrs.get("itemprop")
                else f"{h1_with_attrs.name}[class]"
            )
            return cleaned_title, selector, FieldExtractionStatus.MODULE_HEURISTIC, 220

    # Priority 1c: Generic <h1> tag fallback
    all_h1s = [
        h
        for h in soup.find_all("h1")
        if h not in processed_elements and h.get_text(strip=True)
    ]

    if len(all_h1s) == 1:
        # High confidence if there's only one H1 on the page
        h1_tag = all_h1s[0]
        cleaned_title = clean_title(h1_tag.get_text(strip=True))
        if cleaned_title:
            logger.debug(f"H1 Parser: Found single, unambiguous H1: {cleaned_title}")
            processed_elements.add(h1_tag)
            return (
                cleaned_title,
                "h1 (single)",
                FieldExtractionStatus.MODULE_HEURISTIC,
                200,
            )

    elif len(all_h1s) > 1:
        # Lower confidence if there are multiple H1s; we take the first one.
        h1_tag = all_h1s[0]
        cleaned_title = clean_title(h1_tag.get_text(strip=True))
        if cleaned_title:
            logger.debug(
                f"H1 Parser: Found multiple H1s, taking first one: {cleaned_title}"
            )
            processed_elements.add(h1_tag)
            return (
                cleaned_title,
                "h1 (first of many)",
                FieldExtractionStatus.MODULE_HEURISTIC,
                150,
            )

    return None, "h1_parser", FieldExtractionStatus.NOT_FOUND, 0
