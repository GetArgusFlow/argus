# argus/services/extractor/app/modules/breadcrumbs/extract.py

from typing import Optional, Tuple, Any, List
from loguru import logger
from app.core.models import FieldExtractionStatus
from app.core.context import shared_context

from app.modules.breadcrumbs.parsers.json_ld_parser import parse_from_json_ld
from app.modules.breadcrumbs.parsers.itemprop_parser import parse_itemprop_schema
from app.modules.breadcrumbs.parsers.heuristic_parser import parse_with_heuristics
from app.modules.breadcrumbs.parsers.regex_parser import parse_with_regex

FIELD_TYPE = Optional[List[str]]
REQUIRES = ["json_ld"]


def extract() -> Tuple[Any, str, FieldExtractionStatus, int]:
    """
    The orchestrator function that extracts the breadcrumb navigation by calling a series of parsers.
    """
    logger.info("Breadcrumbs Extractor (Main): Starting breadcrumbs extraction.")

    # Priority 1: JSON-LD (from shared_context)
    # This parser reads the results from the 'json_ld' module,
    # so it does not depend on the soup object.
    breadcrumbs, selector, status, score = parse_from_json_ld()
    if breadcrumbs:
        logger.info(
            f"Breadcrumbs Extractor: Breadcrumbs successfully extracted with JSON-LD Parser. Score: {score}"
        )
        return breadcrumbs, selector, status, score

    # HTML parsers (itemprop, heuristic, regex) need the soup
    soup_to_use = shared_context.get("raw_soup")
    if not soup_to_use:
        logger.warning(
            "Breadcrumbs Extractor: No valid BeautifulSoup objects to work with (and JSON-LD failed)."
        )
        return None, "NOT_FOUND", FieldExtractionStatus.NOT_FOUND, 0

    # Priority 2: Schema.org itemprop-microdata
    breadcrumbs, selector, status, score = parse_itemprop_schema(soup_to_use)
    if breadcrumbs:
        logger.info(
            f"Breadcrumbs Extractor: Breadcrumbs successfully extracted with Itemprop Parser. Score: {score}"
        )
        return breadcrumbs, selector, status, score

    # Priority 3: General classes and IDs
    breadcrumbs, selector, status, score = parse_with_heuristics(soup_to_use)
    if breadcrumbs:
        logger.info(
            f"Breadcrumbs Extractor: Breadcrumbs successfully extracted with Heuristics Parser. Score: {score}"
        )
        return breadcrumbs, selector, status, score

    # Priority 4: Regex on separators
    breadcrumbs, selector, status, score = parse_with_regex(soup_to_use)
    if breadcrumbs:
        logger.info(
            f"Breadcrumbs Extractor: Breadcrumbs successfully extracted with Regex Parser. Score: {score}"
        )
        return breadcrumbs, selector, status, score

    logger.info("Breadcrumbs Extractor: No suitable breadcrumbs found.")
    return None, "NOT_FOUND", FieldExtractionStatus.NOT_FOUND, 0
