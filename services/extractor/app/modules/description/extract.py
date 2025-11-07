# argus/services/extractor/app/modules/description/extract.py

from typing import Optional, Tuple, Any, List
from loguru import logger
from app.core.models import FieldExtractionStatus
from app.core.context import shared_context

from .parsers.json_ld_parser import parse_json_ld
from .parsers.open_graph_parser import parse_open_graph
from .parsers.amazon_parser import parse_amazon_sections
from .parsers.meta_parser import parse_meta_tags
from .parsers.general_parser import parse_general_sections
from .parsers.fallback_parser import parse_generic_fallback

FIELD_TYPE = Optional[str]

REQUIRES = ["json_ld", "open_graph"]


def extract() -> Tuple[Any, str, FieldExtractionStatus, int]:
    """
    The orchestrator function that extracts the product description by calling a series
    of parsers, collecting all results, and returning the one with the highest score.
    """
    soup_to_use = shared_context.get("raw_soup")
    nlp_model = shared_context.get("resources", {}).get("nlp_model")

    if not soup_to_use:
        logger.warning(
            "Description Extractor: No valid BeautifulSoup objects to work with."
        )
        return None, "NOT_FOUND", FieldExtractionStatus.NOT_FOUND, 0

    logger.info(
        "Description Extractor (Main): Starting product description extraction."
    )

    # Step 1: Initialize a list to store all found results.
    results: List[Tuple[Any, str, FieldExtractionStatus, int]] = []

    # Step 2: Call all parsers and add their results to the list.

    # Parser 1: JSON-LD (highest reliability)
    description, selector, status, score = parse_json_ld(nlp_model)
    if description:
        results.append((description, selector, status, score))

    # Parser 2: Open Graph (high reliability)
    description, selector, status, score = parse_open_graph(nlp_model)
    if description:
        results.append((description, selector, status, score))

    # Parser 3: Amazon-specific sections (high score HTML)
    description, selector, status, score = parse_amazon_sections(soup_to_use, nlp_model)
    if description:
        results.append((description, selector, status, score))

    # Parser 4: Meta-tags (Schema.org / name="description")
    description, selector, status, score = parse_meta_tags(soup_to_use, nlp_model)
    if description:
        results.append((description, selector, status, score))

    # Parser 5: General sections on the page
    description, selector, status, score = parse_general_sections(
        soup_to_use, nlp_model
    )
    if description:
        results.append((description, selector, status, score))

    # Parser 6: Fallback (large text blocks)
    description, selector, status, score = parse_generic_fallback(
        soup_to_use, nlp_model
    )
    if description:
        results.append((description, selector, status, score))

    # Step 7: Determine the best result from the list.
    if not results:
        logger.info(
            "Description Extractor: No parser could find a suitable description."
        )
        return None, "NOT_FOUND", FieldExtractionStatus.NOT_FOUND, 0

    # Use max() to find the result (tuple) with the highest score (the 4th element, index 3).
    best_result = max(results, key=lambda item: item[3])

    logger.success(
        f"Description Extractor: Best description found via '{best_result[1]}' with score {best_result[3]}."
    )
    return best_result
