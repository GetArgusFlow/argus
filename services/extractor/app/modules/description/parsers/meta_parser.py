# argus/services/extractor/app/modules/description/parsers/meta_parser.py

from typing import Optional, Tuple, Any
from bs4 import BeautifulSoup
from loguru import logger
from app.core.models import FieldExtractionStatus
from app.modules.description.utils import clean_and_validate_description


def parse_meta_tags(
    soup: BeautifulSoup, nlp_model: Any = None
) -> Tuple[Optional[str], str, FieldExtractionStatus, int]:
    """
    Extracts the description from Open Graph and Schema.org meta-tags.
    """
    logger.debug("Meta Parser: Searching in Open Graph / Schema.org meta tags.")

    # 1. Schema.org
    schema_description = soup.find("meta", itemprop="description")
    if schema_description and schema_description.get("content"):
        desc_text = schema_description["content"].strip()
        cleaned_desc = clean_and_validate_description(desc_text, nlp_model)
        if cleaned_desc:
            logger.debug(
                f"Meta Parser: Found itemprop='description': {cleaned_desc[:100]}..."
            )
            return (
                cleaned_desc,
                'meta[itemprop="description"]',
                FieldExtractionStatus.MODULE_HEURISTIC,
                175,
            )

    # 2. Meta name
    meta_description = soup.find("meta", attrs={"name": "description"})
    if meta_description and meta_description.get("content"):
        desc_text = meta_description["content"].strip()
        logger.debug(f"Meta Parser: Found via name='description': {desc_text[:100]}...")
        return (
            desc_text,
            'meta[name="description"]',
            FieldExtractionStatus.MODULE_HEURISTIC,
            100,
        )

    return None, "meta_parser", FieldExtractionStatus.NOT_FOUND, 0
