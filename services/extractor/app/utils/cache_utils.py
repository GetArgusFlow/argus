# argus/services/extractor/app/utils/cache_utils.py

import os
import json
import hashlib
import re
from urllib.parse import urlparse
from typing import Dict, Any
from bs4 import BeautifulSoup
from loguru import logger


def get_url_hash(url: str) -> str:
    """Generates a SHA256 hash of a URL for caching."""
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


def load_json_file(file_path: str) -> Dict[str, Any]:
    """Loads a JSON file, with error handling."""
    if not os.path.exists(file_path):
        logger.debug(
            f"Cache Utils: File not found: '{file_path}'. Returning empty dict."
        )
        return {}

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.debug(f"Cache Utils: JSON file loaded: '{file_path}'.")
        return data
    except json.JSONDecodeError as e:
        logger.error(f"Cache Utils: Error decoding JSON '{file_path}': {e}.")
        return {}
    except Exception as e:
        logger.error(f"Cache Utils: Unexpected error loading JSON '{file_path}': {e}.")
        return {}


def save_json_file(data: Dict[str, Any], file_path: str):
    """Saves data to a JSON file, with error handling."""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Cache Utils: Data saved to '{file_path}'.")
    except Exception as e:
        logger.error(f"Cache Utils: Error saving data to '{file_path}': {e}")


def save_preprocessed_html(
    soup: BeautifulSoup,
    source_identifier: str,
    output_dir: str = "preprocessed_html_output",
):
    """
    Saves a BeautifulSoup object as an HTML file with a unique, safe filename.
    The filename is based on the URL or another identifier.
    """
    if not soup:
        logger.warning("Cache Utils: Cannot save empty HTML.")
        return

    # Generate a safe and unique filename
    if source_identifier.startswith("http"):
        parsed_url = urlparse(source_identifier)
        # Remove disallowed characters for filenames
        safe_name = re.sub(
            r"[^a-zA-Z0-9_\-.]", "_", parsed_url.netloc + parsed_url.path
        )
        # Limit the filename length to avoid OS limits
        if len(safe_name) > 150:
            safe_name = safe_name[:150]
        # Add a short hash to ensure uniqueness
        url_hash = hashlib.md5(source_identifier.encode("utf-8")).hexdigest()[:8]
        file_name = f"{safe_name}_{url_hash}.html"
    else:
        file_name = f"{source_identifier}.html"

    output_path = os.path.join(output_dir, file_name)

    try:
        os.makedirs(output_dir, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(str(soup))
        logger.info(f"Cache Utils: Preprocessed HTML saved in '{output_path}'.")
    except IOError as e:
        logger.error(f"Cache Utils: Error writing to file '{output_path}': {e}")
    except Exception as e:
        logger.error(
            f"Cache Utils: Unexpected error saving HTML to '{output_path}': {e}"
        )
