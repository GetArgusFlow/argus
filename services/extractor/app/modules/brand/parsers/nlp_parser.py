# argus/services/extractor/app/modules/brand/parsers/nlp_parser.py

from typing import Optional, Tuple, Any
from bs4 import BeautifulSoup
from loguru import logger
from app.core.types import FieldExtractionStatus
from app.modules.brand.utils import is_plausible_brand, get_main_title_content


def parse_with_nlp(
    soup: BeautifulSoup, nlp_model: Any
) -> Tuple[Optional[str], str, FieldExtractionStatus, int]:
    """
    Extracts a brand name using the spaCy NER model.
    """
    if not nlp_model:
        logger.debug("NLP Parser: spaCy model not available. Skipping.")
        return None, "nlp_parser", FieldExtractionStatus.NOT_FOUND, 0

    main_title_text, main_title_selector = get_main_title_content(soup)

    if not main_title_text:
        return None, "nlp_parser", FieldExtractionStatus.NOT_FOUND, 0

    logger.debug("NLP Parser: Running NLP extraction with spaCy.")
    doc = nlp_model(main_title_text)
    for ent in doc.ents:
        # We look for organizations, as brands are typically classified as such.
        if ent.label_ == "ORG" and is_plausible_brand(ent.text.strip(), nlp_model):
            logger.info(
                f"NLP Parser: Brand found via NLP in title: '{ent.text.strip()}' (Label: {ent.label_})"
            )
            return (
                ent.text.strip(),
                f"{main_title_selector} (NLP - {ent.label_})",
                FieldExtractionStatus.NLP_HEURISTIC,
                75,
            )

    logger.debug("NLP Parser: No valid brand found with spaCy NER.")
    return None, "nlp_parser", FieldExtractionStatus.NOT_FOUND, 0
