# argus/services/extractor/app/modules/image/parsers/meta_parser.py

from typing import Optional, Tuple, Set
from bs4 import BeautifulSoup, Tag
from loguru import logger
from app.core.models import FieldExtractionStatus
from app.modules.image.utils import is_valid_image_url


def parse_meta_tags(
    soup: BeautifulSoup, processed_elements: Set[Tag]
) -> Tuple[Optional[str], str, FieldExtractionStatus, int]:
    """
    Extracts the image from Schema.org microdata meta-tags.
    (Open Graph logic is now handled by open_graph_parser.py)
    """
    logger.debug("Meta Parser: Searching in Schema.org meta tags.")

    # Look for Schema.org microdata tag
    schema_image = soup.find("meta", itemprop="image")
    if (
        schema_image
        and schema_image.get("content")
        and is_valid_image_url(schema_image["content"])
    ):
        logger.debug(
            f"Meta Parser: Found via itemprop='image': {schema_image['content']}"
        )
        processed_elements.add(schema_image)
        # This is now the highest-priority HTML-based meta tag
        return (
            schema_image["content"],
            'meta[itemprop="image"]',
            FieldExtractionStatus.MODULE_HEURISTIC,
            180,
        )

    return None, "meta_parser", FieldExtractionStatus.NOT_FOUND, 0
