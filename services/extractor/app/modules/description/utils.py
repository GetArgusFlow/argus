# argus/services/extractor/app/modules/description/utils.py

import re
from typing import Optional, Any
from loguru import logger
from app.utils.pattern_manager import pattern_manager


def clean_and_validate_description(text: str, nlp_model: Any = None) -> Optional[str]:
    """
    Cleans up the description text and validates it generically based
    on the density of descriptive words (nouns and adjectives).
    """
    cleaned_text = text.strip()

    # Use the dynamic regex from PatternManager
    undesired_phrases_regex = pattern_manager.get_compiled_regex(
        "description_filter_regex"
    )

    cleaned_text = undesired_phrases_regex.sub("", cleaned_text).strip()
    cleaned_text = re.sub(r"\n\s*\n", "\n", cleaned_text)
    cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()

    if len(cleaned_text) < 50:
        logger.debug(
            f"Description validation: Text is too short ({len(cleaned_text)} characters). Skipping."
        )
        return None
    if len(cleaned_text) > 5000:
        logger.debug(
            f"Description validation: Text is too long ({len(cleaned_text)} characters). Cutting text."
        )
        cleaned_text = cleaned_text[:5000]

    if not nlp_model:
        logger.warning(
            "Description validation: NLP model not available, cannot perform generic validation. Skipping."
        )
        return cleaned_text

    try:
        doc = nlp_model(cleaned_text)

        noun_adj_count = sum(1 for token in doc if token.pos_ in ["NOUN", "ADJ"])
        total_tokens = len([token for token in doc if token.is_alpha])

        if total_tokens == 0:
            return None

        density = noun_adj_count / total_tokens

        MIN_DENSITY_THRESHOLD = 0.25
        MIN_ABSOLUTE_COUNT = 2

        logger.debug(
            f"Description validation: Noun/Adjective density={density:.2f}, count={noun_adj_count}"
        )

        if density >= MIN_DENSITY_THRESHOLD or noun_adj_count >= MIN_ABSOLUTE_COUNT:
            return cleaned_text
        else:
            logger.debug(
                "Description validation: Density and absolute count are too low. Skipping."
            )
            return None

    except Exception as e:
        logger.warning(f"Description validation: NLP analysis failed: {e}")
        return cleaned_text
