# argus/services/extractor/app/utils/html_processor.py

from bs4 import BeautifulSoup, Comment
from loguru import logger
from app.config import settings

import re


def clean_html_for_extraction(raw_html_content: str) -> BeautifulSoup:
    """
    Preprocesses HTML by removing noise and normalizing whitespace,
    without polluting the logic with I/O operations.
    """
    if not raw_html_content:
        logger.warning("HTML Processor: Received empty HTML content.")
        return BeautifulSoup("", "lxml")

    soup = BeautifulSoup(raw_html_content, "lxml")

    logger.info("HTML Processor: Starting HTML cleanup.")

    # Step 1: Remove known noise tags
    for tag_name in [
        "script",
        "style",
        "noscript",
        "link",
        "template",
        "svg",
        "iframe",
        "button",
    ]:
        for element in soup.find_all(tag_name):
            element.decompose()

    # Step 2: Remove HTML comments
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()
    logger.debug("HTML Processor: All HTML comments removed.")

    # Step 3: Remove noise sections based on selectors, including the function selector
    for selector in settings.html_preprocessing.noise_selectors:
        try:
            if isinstance(selector, str):
                for element in soup.select(selector):
                    logger.debug(
                        f"HTML Processor: Removing element by selector '{selector}'."
                    )
                    element.decompose()
            elif callable(selector):
                # If it's a function, call it to find the elements
                for element in soup.find_all(selector):
                    logger.debug(
                        f"HTML Processor: Removing element by function '{selector}'."
                    )
                    element.decompose()
            else:
                logger.warning(
                    f"HTML Processor: Skipping invalid selector type: {type(selector)}."
                )
        except Exception as e:
            logger.error(
                f"HTML Processor: Error during removal with selector '{selector}': {e}",
                exc_info=True,
            )

    # Step 4: Normalize whitespace and remove empty tags
    if soup.body:
        # Loop through the tags in reverse order, from inside out
        for tag in soup.body.find_all(True, reverse=False):
            if tag.name in ["img", "br", "hr", "input", "meta"]:
                continue

            # Use get_text() to get all nested text
            raw_text = tag.get_text(strip=True)

            # Remove all whitespace (spaces, newlines, tabs) and check if anything remains
            if not re.sub(r"\s+", "", raw_text):
                # The tag is empty, remove it unless it's an excluded tag
                tag.decompose()

    for tag in soup.find_all():
        if (
            not tag.contents
            and not tag.get_text(strip=True)
            and tag.name not in ["img", "br", "hr", "meta", "input"]
        ):
            tag.decompose()

    logger.info("HTML Processor: Cleanup complete.")
    return soup
