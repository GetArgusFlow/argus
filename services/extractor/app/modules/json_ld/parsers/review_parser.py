# argus/services/extractor/app/modules/json_ld/parsers/review_parser.py

from typing import Dict, Any, List, Optional
from loguru import logger
from app.utils.data_utils import clean_text_and_remove_unicode


def _parse_single_review(review_node: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Parses a single review node and extracts the relevant fields."""
    if not isinstance(review_node, dict):
        return None

    extracted_review = {}

    # Extract the author's name
    author_node = review_node.get("author")
    if isinstance(author_node, dict):
        extracted_review["name"] = clean_text_and_remove_unicode(
            author_node.get("name")
        )
    elif isinstance(author_node, str):
        extracted_review["name"] = clean_text_and_remove_unicode(author_node)

    # Extract the rating
    rating_node = review_node.get("reviewRating")
    if isinstance(rating_node, dict):
        rating = rating_node.get("ratingValue")
        if rating is not None:
            extracted_review["rating"] = float(rating)

    # Extract the review text and date
    review_text = review_node.get("reviewBody")
    if review_text:
        extracted_review["review_text"] = clean_text_and_remove_unicode(review_text)

    date_published = review_node.get("datePublished")
    if date_published:
        extracted_review["date"] = clean_text_and_remove_unicode(date_published)

    # Only return if there is at least a review text or a rating
    if (
        extracted_review.get("review_text")
        or extracted_review.get("rating") is not None
    ):
        return extracted_review
    return None


def parse_reviews(json_ld_data: List[Dict[str, Any]], extracted_fields: Dict[str, Any]):
    """
    Finds and parses review data from a list of JSON-LD nodes.
    This function processes both single Review objects and nested lists of reviews.
    """
    all_reviews = []

    for node in json_ld_data:
        reviews = node.get("review")
        if isinstance(reviews, dict):
            # A single review node
            parsed_review = _parse_single_review(reviews)
            if parsed_review:
                all_reviews.append(parsed_review)
        elif isinstance(reviews, list):
            # A list of review nodes
            for review_item in reviews:
                parsed_review = _parse_single_review(review_item)
                if parsed_review:
                    all_reviews.append(parsed_review)

    if all_reviews:
        extracted_fields["reviews"] = all_reviews
        logger.info(f"JSON_LD Reviews Parser: {len(all_reviews)} reviews extracted.")
