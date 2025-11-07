# argus/services/extractor/app/modules/json_ld/utils.py

import json
import re
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional, List
from loguru import logger


def parse_json_ld_scripts(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """
    Finds and parses all JSON-LD scripts on the page.
    Returns a list of all parsed dictionaries.
    """
    all_parsed_json_data: List[Dict[str, Any]] = []
    json_ld_scripts = soup.find_all("script", type="application/ld+json")

    if not json_ld_scripts:
        logger.debug("JSON_LD Utils: No JSON-LD scripts found.")
        return all_parsed_json_data

    logger.debug(f"JSON_LD Utils: {len(json_ld_scripts)} JSON-LD scripts found.")
    for script in json_ld_scripts:
        json_string_content: Optional[str] = None
        try:
            json_string_content = script.string
            if json_string_content:
                json_content = json.loads(json_string_content)
                if isinstance(json_content, list):
                    all_parsed_json_data.extend(json_content)
                elif isinstance(json_content, dict):
                    all_parsed_json_data.append(json_content)
        except (json.JSONDecodeError, TypeError) as e:
            logger.warning(f"JSON_LD Utils: Error parsing JSON-LD script: {e}")

    return all_parsed_json_data


def extract_value(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    """
    Retrieves a value from a dictionary, with support for nested paths.
    """
    keys = key.split(".")
    current_data = data
    for k in keys:
        if isinstance(current_data, dict) and k in current_data:
            current_data = current_data[k]
        elif isinstance(current_data, list):
            try:
                index = int(k)
                if 0 <= index < len(current_data):
                    current_data = current_data[index]
                else:
                    return default
            except (ValueError, IndexError):
                return default
        else:
            return default
    return current_data


def is_title_matching_breadcrumb(
    title: str, breadcrumb: str, fuzziness_threshold: float = 0.8
) -> bool:
    """
    Checks if a breadcrumb (the last one) matches the product title.
    """
    title_lower = title.lower()
    breadcrumb_lower = breadcrumb.lower()

    if title_lower == breadcrumb_lower:
        return True

    clean_title = re.sub(r"[^a-z0-9\s]", "", title_lower).strip()
    clean_breadcrumb = re.sub(r"[^a-z0-9\s]", "", breadcrumb_lower).strip()

    if not clean_title or not clean_breadcrumb:
        return False
    if clean_title == clean_breadcrumb:
        return True
    if clean_title in clean_breadcrumb or clean_breadcrumb in clean_title:
        return True

    title_tokens = set(clean_title.split())
    breadcrumb_tokens = set(clean_breadcrumb.split())

    if not title_tokens or not breadcrumb_tokens:
        return False

    intersection = len(title_tokens.intersection(breadcrumb_tokens))
    union = len(title_tokens.union(breadcrumb_tokens))
    jaccard_similarity = intersection / union if union > 0 else 0

    if jaccard_similarity >= fuzziness_threshold:
        return True

    return False
