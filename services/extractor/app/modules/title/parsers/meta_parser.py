# argus/services/extractor/app/modules/title/parsers/meta_parser.py

from typing import Optional, Tuple, Set
from bs4 import BeautifulSoup, Tag
from loguru import logger
from app.core.models import FieldExtractionStatus
from app.modules.title.utils import clean_title


def parse_meta_tags(
    soup: BeautifulSoup, processed_elements: Set[Tag]
) -> Tuple[Optional[str], str, FieldExtractionStatus, int]:
    """
    Extracts the title from Schema.org microdata meta-tags.
    (Open Graph logic is now handled by open_graph_parser.py)
    """
    # Look for Schema.org microdata tag
    schema_name = soup.find("meta", itemprop="name")
    if (
        schema_name
        and schema_name.get("content")
        and schema_name not in processed_elements
    ):
        extracted_title = schema_name["content"].strip()
        cleaned_title = clean_title(extracted_title)
        if cleaned_title and len(cleaned_title) > 5:
            logger.debug(f"Meta Parser: Found via itemprop='name': {cleaned_title}")
            processed_elements.add(schema_name)
            return (
                cleaned_title,
                'meta[itemprop="name"]',
                FieldExtractionStatus.MODULE_HEURISTIC,
                140,
            )

    return None, "meta_parser", FieldExtractionStatus.NOT_FOUND, 0
