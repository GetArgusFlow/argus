# argus/services/extractor/app/modules/title/parsers/title_tag_parser.py

from typing import Optional, Tuple, Set
from bs4 import BeautifulSoup, Tag
from loguru import logger
from app.core.models import FieldExtractionStatus
from app.modules.title.utils import clean_title


def parse_title_tag(
    soup: BeautifulSoup, processed_elements: Set[Tag]
) -> Tuple[Optional[str], str, FieldExtractionStatus, int]:
    """
    Extracts the title from the <title> tag in the HTML head.
    """
    title_tag = soup.find("title")
    if title_tag:
        extracted_title = title_tag.get_text(strip=True)
        cleaned_title = clean_title(extracted_title)
        if cleaned_title and len(cleaned_title) > 5:
            logger.debug(f"Title Tag Parser: Found via <title> tag: {cleaned_title}")
            processed_elements.add(title_tag)
            return (
                cleaned_title,
                "title (tag)",
                FieldExtractionStatus.MODULE_HEURISTIC,
                180,
            )

    return None, "title_tag_parser", FieldExtractionStatus.NOT_FOUND, 0
