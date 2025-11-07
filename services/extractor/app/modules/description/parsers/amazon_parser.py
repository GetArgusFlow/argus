# argus/services/extractor/app/modules/description/parsers/amazon_parser.py

from typing import Optional, Tuple, Any
from bs4 import BeautifulSoup
from loguru import logger
from app.core.models import FieldExtractionStatus
from app.modules.description.utils import clean_and_validate_description


def parse_amazon_sections(
    soup: BeautifulSoup, nlp_model: Any = None
) -> Tuple[Optional[str], str, FieldExtractionStatus, int]:
    """
    Extracts the description from Amazon-specific sections.
    """
    logger.debug("Amazon Parser: Searching in Amazon-specific description sections.")

    # 1. Product Description Block
    product_description_div = soup.select_one("#productDescription")
    if product_description_div:
        description_text = product_description_div.get_text(separator=" ", strip=True)
        cleaned_desc = clean_and_validate_description(description_text, nlp_model)
        if cleaned_desc:
            logger.debug(
                f"Amazon Parser: Found via #productDescription: {cleaned_desc[:100]}..."
            )
            return (
                cleaned_desc,
                "#productDescription",
                FieldExtractionStatus.MODULE_HEURISTIC,
                250,
            )

    # 2. Feature Bullets
    feature_bullets_ul = soup.select_one("#feature-bullets ul")
    if feature_bullets_ul:
        bullets = [
            li.get_text(strip=True)
            for li in feature_bullets_ul.find_all("li")
            if li.get_text(strip=True)
        ]
        if bullets:
            combined_description = "\n".join(bullets)
            cleaned_desc = clean_and_validate_description(
                combined_description, nlp_model
            )
            if cleaned_desc:
                logger.debug(
                    f"Amazon Parser: Found via #feature-bullets: {cleaned_desc[:100]}..."
                )
                return (
                    cleaned_desc,
                    "#feature-bullets ul",
                    FieldExtractionStatus.MODULE_HEURISTIC,
                    220,
                )

    # 3. 'About this item' section
    about_item_section = soup.select_one(
        "#productOverview_feature_div .a-section.a-spacing-small"
    )
    if about_item_section:
        about_text = about_item_section.get_text(separator="\n", strip=True)
        cleaned_desc = clean_and_validate_description(about_text, nlp_model)
        if cleaned_desc:
            logger.debug(
                f"Amazon Parser: Found via 'About this item' section: {cleaned_desc[:100]}..."
            )
            return (
                cleaned_desc,
                "#productOverview_feature_div",
                FieldExtractionStatus.MODULE_HEURISTIC,
                210,
            )

    return None, "amazon_parser", FieldExtractionStatus.NOT_FOUND, 0
