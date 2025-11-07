# argus/services/extractor/app/utils/html_utils.py

from bs4 import BeautifulSoup, Comment
from loguru import logger
from typing import List


def preprocess_html_for_extraction(
    html_content: str, hidden_selectors: List[str]
) -> BeautifulSoup:
    """
    Removes unnecessary tags and comments from HTML to simplify the extraction
    of structured data. Returns a BeautifulSoup object.
    """
    if not html_content:
        return BeautifulSoup("", "lxml")

    soup = BeautifulSoup(html_content, "lxml")

    # Remove tags that cause noise
    for selector in ["script", "style", "noscript", "meta", "link", "template"]:
        for element in soup.find_all(selector):
            element.decompose()

    # Remove HTML comments
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()

    # Remove hidden elements based on CSS classes or attributes
    for selector in hidden_selectors:
        for element in soup.select(selector):
            element.decompose()

    logger.debug("HTML Utils: HTML successfully preprocessed for extraction.")
    return soup


def preprocess_html_for_llm(
    html_content: str, noise_selectors: List[str], max_chars: int
) -> str:
    """
    Converts HTML to clean, truncated text for use with an LLM.
    Removes an extensive list of selectors considered to be noise.
    """
    if not html_content:
        return ""

    soup = BeautifulSoup(html_content, "lxml")

    for selector in noise_selectors:
        if callable(selector):  # To handle lambda functions for comments
            # This part of bs4 logic is a bit different for callables
            for element in soup.find_all(string=selector):
                element.extract()
        else:
            for element in soup.select(selector):
                element.decompose()

    clean_text = " ".join(soup.get_text(separator=" ", strip=True).split())

    if len(clean_text) > max_chars:
        logger.warning(
            f"HTML Utils: Text truncated for LLM: from {len(clean_text)} to {max_chars} chars."
        )
        clean_text = clean_text[:max_chars] + " [TRUNCATED FOR LLM]"

    return clean_text
