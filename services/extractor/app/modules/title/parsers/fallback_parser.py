# argus/services/extractor/app/modules/title/parsers/fallback_parser.py

from typing import Optional, Tuple, Set
from bs4 import BeautifulSoup, Tag
from loguru import logger
from app.core.models import FieldExtractionStatus
from app.modules.title.utils import clean_title


def parse_generic_fallback(
    soup: BeautifulSoup, processed_elements: Set[Tag]
) -> Tuple[Optional[str], str, FieldExtractionStatus, int]:
    """
    Searches for the title in general elements as a last resort.
    """
    potential_title_elements = soup.select(
        'span[id*="title"], div[id*="title"], strong[id*="title"], h2.title, p.title'
    )

    for elem in potential_title_elements:
        if elem in processed_elements:
            continue

        extracted_title = elem.get_text(strip=True)
        cleaned_title = clean_title(extracted_title)

        if cleaned_title and 10 < len(cleaned_title) < 200:
            logger.debug(
                f"Fallback Parser: Found via general elements: {cleaned_title}"
            )
            processed_elements.add(elem)
            selector = (
                f"{elem.name}#{elem.get('id')}"
                if elem.get("id")
                else f"{elem.name}.{elem.get('class', [''])[0]}"
            )
            return cleaned_title, selector, FieldExtractionStatus.GENERIC_FALLBACK, 80

    return None, "fallback_parser", FieldExtractionStatus.NOT_FOUND, 0
