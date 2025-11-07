# argus/services/extractor/app/modules/brand/extract.py

from typing import Optional, Tuple, Any
from loguru import logger
from app.core.models import FieldExtractionStatus
from app.core.context import shared_context

from .parsers.json_ld_parser import parse_json_ld
from .parsers.open_graph_parser import parse_open_graph
from .parsers.meta_parser import parse_meta_tags
from .parsers.nlp_parser import parse_with_nlp
from .parsers.dom_parser import parse_with_dom_heuristics
from .parsers.title_parser import parse_from_title
from .parsers.general_fallback_parser import parse_general_fallback

FIELD_TYPE = Optional[str]
REQUIRES = ["json_ld", "open_graph"]


def extract() -> Tuple[Any, str, FieldExtractionStatus, int]:
    """
    The orchestrator function that extracts the brand name by calling a series of parsers.
    """
    soup_to_use = shared_context.get("raw_soup")
    nlp_model = shared_context.get("resources", {}).get("nlp_model")

    logger.info("Brand Extractor (Main): Starting brand name extraction.")
    if not soup_to_use:
        logger.warning("Brand Extractor: No valid BeautifulSoup objects to work with.")
        return None, "NOT_FOUND", FieldExtractionStatus.NOT_FOUND, 0

    # Priority 1: JSON-LD (highest reliability)
    brand, selector, status, score = parse_json_ld(soup_to_use, nlp_model)
    if brand:
        return brand, selector, status, score

    # Priority 2: Open Graph (high reliability)
    brand, selector, status, score = parse_open_graph(soup_to_use, nlp_model)
    if brand:
        return brand, selector, status, score

    # Priority 3: Meta tags and structured microdata (from HTML)
    brand, selector, status, score = parse_meta_tags(soup_to_use, nlp_model)
    if brand:
        return brand, selector, status, score

    # Priority 4: DOM-based heuristics
    brand, selector, status, score = parse_with_dom_heuristics(soup_to_use, nlp_model)
    if brand:
        return brand, selector, status, score

    # Priority 5: Pattern recognition in the title
    brand, selector, status, score = parse_from_title(soup_to_use, nlp_model)
    if brand:
        return brand, selector, status, score

    # Priority 6: NLP-based extraction (run after DOM/Title heuristics)
    brand, selector, status, score = parse_with_nlp(soup_to_use, nlp_model)
    if brand:
        return brand, selector, status, score

    # Priority 7: General fallback search
    brand, selector, status, score = parse_general_fallback(soup_to_use, nlp_model)
    if brand:
        return brand, selector, status, score

    logger.info("Brand Extractor: No brand name found via any method.")
    return None, "NOT_FOUND", FieldExtractionStatus.NOT_FOUND, 0
