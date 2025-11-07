# argus/services/extractor/app/modules/breadcrumbs/parsers/itemprop_parser.py

import re
from typing import Optional, Tuple, List
from bs4 import BeautifulSoup, Tag
from loguru import logger
from app.core.models import FieldExtractionStatus
from app.modules.breadcrumbs.utils import clean_and_filter_breadcrumbs


def _find_breadcrumb_container(soup: BeautifulSoup) -> Optional[Tag]:
    """
    Finds a breadcrumb container by checking both itemprop and itemtype attributes.
    """
    # Find tags with 'itemtype' containing 'BreadcrumbList'
    # This is a very reliable indicator.
    itemtype_containers = soup.find_all(
        re.compile(r"ol|ul|nav|div"),
        itemtype=re.compile(r"BreadcrumbList", re.IGNORECASE),
    )
    if itemtype_containers:
        return itemtype_containers[0]  # Return the first match

    # Fallback: Find tags with 'itemprop' containing 'breadcrumb'
    # This is less common for the list itself but still valid.
    itemprop_containers = soup.find_all(
        re.compile(r"ol|ul|nav|div"),
        itemprop=re.compile(r"breadcrumb|itemList", re.IGNORECASE),
    )
    if itemprop_containers:
        return itemprop_containers[0]

    return None


def parse_itemprop_schema(
    soup: BeautifulSoup,
) -> Tuple[Optional[List[str]], str, FieldExtractionStatus, int]:
    """
    Extracts breadcrumbs from Schema.org (BreadcrumbList) microdata,
    checking both itemprop and itemtype.
    """
    breadcrumb_list_container = _find_breadcrumb_container(soup)

    if not breadcrumb_list_container:
        return None, "itemprop_parser", FieldExtractionStatus.NOT_FOUND, 0

    found_breadcrumbs = []

    # Find all elements marked as 'itemListElement' or 'item'
    list_items = breadcrumb_list_container.find_all(
        itemprop=re.compile(r"itemListElement|item", re.IGNORECASE)
    )

    if not list_items:
        # Fallback: sometimes items are direct children without itemprop
        list_items = breadcrumb_list_container.find_all("li", recursive=False)

    if list_items:
        for item in list_items:
            # Find the name of the item (the text)
            name_tag = item.find(itemprop="name")
            if name_tag and name_tag.get_text(strip=True):
                found_breadcrumbs.append(name_tag.get_text(strip=True))
            else:
                # Fallback: search in an <a> tag
                link_tag = item.find("a")
                if link_tag and link_tag.get_text(strip=True):
                    found_breadcrumbs.append(link_tag.get_text(strip=True))
                # Fallback: get text of the item itself, excluding sub-items
                elif item.get_text(strip=True):
                    # Try to get text only from the item, not nested tags
                    main_text = "".join(
                        item.find_all(string=True, recursive=False)
                    ).strip()
                    if main_text:
                        found_breadcrumbs.append(main_text)
                    elif link_tag is None:  # Only if no link was found
                        found_breadcrumbs.append(item.get_text(strip=True))

    # Clean up and validate the found list
    cleaned_breadcrumbs = clean_and_filter_breadcrumbs(found_breadcrumbs)
    if cleaned_breadcrumbs:
        selector = (
            f'{breadcrumb_list_container.name}[itemprop/itemtype="BreadcrumbList"]'
        )
        logger.debug(f"Itemprop Parser: Found breadcrumbs: {cleaned_breadcrumbs}")
        return (
            cleaned_breadcrumbs,
            selector,
            FieldExtractionStatus.MODULE_HEURISTIC,
            120,
        )

    return None, "itemprop_parser", FieldExtractionStatus.NOT_FOUND, 0
