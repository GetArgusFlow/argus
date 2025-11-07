# argus/services/extractor/app/modules/open_graph/utils.py

from typing import Dict, Any
from bs4 import BeautifulSoup


def find_og_tags(soup: BeautifulSoup) -> Dict[str, Any]:
    """
    Finds all Open Graph meta-tags and returns them as a dictionary.
    The 'og:' prefix is removed from the keys.
    """
    og_tags: Dict[str, Any] = {}
    for tag in soup.find_all("meta", property=True):
        prop = tag.get("property")
        content = tag.get("content")
        if prop and content and prop.startswith("og:"):
            # 'og:title' -> 'title'
            key = prop.replace("og:", "")
            og_tags[key] = content.strip()
    return og_tags
