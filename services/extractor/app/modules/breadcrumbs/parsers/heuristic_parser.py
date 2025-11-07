# argus/services/extractor/app/modules/breadcrumbs/parsers/heuristic_parser.py

from typing import Optional, Tuple, List
from bs4 import BeautifulSoup, Tag
from loguru import logger
from app.core.models import FieldExtractionStatus
from app.modules.breadcrumbs.utils import clean_and_filter_breadcrumbs
from app.utils.pattern_manager import pattern_manager


def is_breadcrumb_container(tag: Tag) -> bool:
    """
    Checks if a tag is a likely breadcrumb container by
    scanning attributes for keywords or standard ARIA roles/labels.
    """
    if tag.name not in ["nav", "ul", "ol", "div"]:
        return False

    # Priority 1: Check standard ARIA accessibility attributes
    aria_label = tag.get("aria-label", "").lower()
    if "breadcrumb" in aria_label:
        return True

    if tag.get("role") == "navigation" and "breadcrumb" in aria_label:
        return True

    # Priority 2: Check all attribute values (class, id, etc.)
    all_attribute_values = []
    for attr_value in tag.attrs.values():
        if isinstance(attr_value, list):
            all_attribute_values.extend(attr_value)
        else:
            all_attribute_values.append(str(attr_value))

    attributes_string = " ".join(all_attribute_values).lower()

    # Use the dynamic regex from PatternManager
    container_regex = pattern_manager.get_compiled_regex("breadcrumb_container_regex")
    return bool(container_regex.search(attributes_string))


def _extract_text_from_li(item: Tag) -> Optional[str]:
    """
    Smarter text extraction from an <li> item.
    It prioritizes <a> tags to avoid grabbing separators.
    """
    # Try to find a link first, this is the most common
    link = item.find("a")
    if link:
        return link.get_text(strip=True)

    # Fallback for non-link items (often the last item)
    # Try to find a span, which might also hold the item
    span = item.find("span")
    if span:
        return span.get_text(strip=True)

    # Last resort: get the whole text of the li
    return item.get_text(strip=True)


def parse_with_heuristics(
    soup: BeautifulSoup,
) -> Tuple[Optional[List[str]], str, FieldExtractionStatus, int]:
    """
    Extracts breadcrumbs using heuristics to find the container and the items,
    regardless of the specific HTML tags used.
    """
    containers = soup.find_all(is_breadcrumb_container, limit=5)

    for container in containers:
        found_breadcrumbs = []

        # Heuristic A: Find <li> items (most common structure)
        list_items = container.find_all("li")
        if len(list_items) > 1:
            for item in list_items:
                text = _extract_text_from_li(item)
                if text:
                    found_breadcrumbs.append(text)

        # Heuristic B: No <li>? Find direct <a> children
        if not found_breadcrumbs:
            links = container.find_all("a", recursive=False)
            if len(links) > 1:
                for link in links:
                    found_breadcrumbs.append(link.get_text(strip=True))
            else:
                # Try recursive search if no direct children
                links = container.find_all("a")
                if len(links) > 1:
                    for link in links:
                        found_breadcrumbs.append(link.get_text(strip=True))

        # Heuristic C: No <li> or <a>? Find direct children (e.g., <span>)
        if not found_breadcrumbs:
            children = [child for child in container.children if isinstance(child, Tag)]
            if len(children) > 1:
                for child in children:
                    text = child.get_text(strip=True)
                    if len(text) > 1:
                        found_breadcrumbs.append(text)

        cleaned = clean_and_filter_breadcrumbs(found_breadcrumbs)
        if cleaned:
            selector = f"{container.name} (heuristic search: aria/class/id)"
            logger.debug(f"Heuristic Parser: Breadcrumbs found: {cleaned}")
            return cleaned, selector, FieldExtractionStatus.MODULE_HEURISTIC, 100

    return None, "heuristic_parser", FieldExtractionStatus.NOT_FOUND, 0
