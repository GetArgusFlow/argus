# argus/services/extractor/app/utils/nlp_utils.py

import spacy
from typing import Optional
import threading
from loguru import logger

SpacyModel = spacy.language.Language

_nlp_model: Optional[SpacyModel] = None
_nlp_lock = threading.Lock()


def get_nlp_model(model_name: str) -> Optional[SpacyModel]:
    """
    Loads the specified spaCy model if needed and returns it.
    """
    global _nlp_model
    if _nlp_model is not None:
        return _nlp_model

    with _nlp_lock:
        if _nlp_model is not None:
            return _nlp_model

        logger.info(f"NLP_Utils: Loading spaCy model '{model_name}'...")
        try:
            _nlp_model = spacy.load(model_name)
            logger.info(f"NLP_Utils: spaCy model '{model_name}' loaded successfully.")
        except OSError:
            logger.error(
                f"NLP_Utils: SpaCy model '{model_name}' not found. "
                f"Run 'python -m spacy download {model_name}'."
            )
            _nlp_model = None
        except Exception as e:
            logger.error(
                f"NLP_Utils: Unexpected error loading spaCy model: {e}", exc_info=True
            )
            _nlp_model = None

    return _nlp_model


def unload_nlp_model():
    """Unloads the spaCy model to free up memory."""
    global _nlp_model
    with _nlp_lock:
        if _nlp_model is not None:
            logger.info("NLP_Utils: Unloading spaCy NLP model.")
            _nlp_model = None
