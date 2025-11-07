# argus/services/extractor/app/modules/description/parsers/fallback_parser.py

from typing import Optional, Tuple, Any
from bs4 import BeautifulSoup
from loguru import logger
from app.core.context import shared_context
from app.core.models import FieldExtractionStatus
from app.modules.description.utils import clean_and_validate_description


def parse_generic_fallback(
    soup: BeautifulSoup, nlp_model: Any = None
) -> Tuple[Optional[str], str, FieldExtractionStatus, int]:
    """
    Extracts a description by searching for large, general text blocks.
    """
    logger.debug("Fallback Parser: Last fallback: Large text blocks.")

    main_content_area = soup.find("div", id="dp") or soup.find("body")
    if main_content_area:
        potential_texts = main_content_area.find_all(["p", "div", "span"], string=True)
        for p_tag in potential_texts:
            # Skip elements that are likely already processed
            if p_tag.parent and (
                p_tag.parent.name == "li"
                or "feature-bullets" in (p_tag.parent.get("id") or "")
                or "feature-bullets" in " ".join(p_tag.parent.get("class", []))
            ):
                continue

            text_content = p_tag.get_text(strip=True)
            cleaned_desc = clean_and_validate_description(text_content, nlp_model)

            # Prevent duplication of other extracted fields
            if cleaned_desc and cleaned_desc not in [
                shared_context.get("title"),
                shared_context.get("price"),
            ]:
                logger.debug(
                    f"Fallback Parser: Found via general text block: {cleaned_desc[:100]}..."
                )
                return (
                    cleaned_desc,
                    f"{p_tag.name} (generic text block)",
                    FieldExtractionStatus.GENERIC_FALLBACK,
                    80,
                )

    return None, "fallback_parser", FieldExtractionStatus.NOT_FOUND, 0
