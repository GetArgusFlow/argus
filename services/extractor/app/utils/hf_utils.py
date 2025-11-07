# argus/services/extractor/app/utils/hf_utils.py

import torch
from transformers import pipeline
from typing import Any, Optional
import threading
from loguru import logger

_hf_classifier: Optional[Any] = None
_hf_lock = threading.Lock()


def get_hf_classifier(model_name: str) -> Optional[Any]:
    """
    Loads and caches a Hugging Face zero-shot classification pipeline.
    """
    global _hf_classifier
    if _hf_classifier is not None:
        return _hf_classifier

    with _hf_lock:
        if _hf_classifier is not None:
            return _hf_classifier

        logger.info(f"HF_Utils: Loading Hugging Face model '{model_name}'...")
        try:
            device = 0 if torch.cuda.is_available() else -1
            if device != -1:
                logger.info(f"HF_Utils: GPU (CUDA) detected. Using device {device}.")
            else:
                logger.warning("HF_Utils: No GPU (CUDA) detected. Falling back to CPU.")

            _hf_classifier = pipeline(
                "zero-shot-classification", model=model_name, device=device
            )
            logger.info(
                f"HF_Utils: Hugging Face model '{model_name}' loaded successfully."
            )
        except Exception as e:
            logger.error(
                f"HF_Utils: Error loading Hugging Face model '{model_name}': {e}",
                exc_info=True,
            )
            _hf_classifier = None

    return _hf_classifier


def unload_hf_classifier():
    """Unloads the Hugging Face classifier to free up memory."""
    global _hf_classifier
    with _hf_lock:
        if _hf_classifier is not None:
            logger.info("HF_Utils: Unloading Hugging Face classifier.")
            _hf_classifier = None
