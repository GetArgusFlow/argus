# argus/services/extractor/app/utils/shared_resources.py

import threading
from typing import Dict, Any
from loguru import logger

from app.utils.nlp_utils import get_nlp_model, unload_nlp_model
from app.config import settings

_shared_resources: Dict[str, Any] = {}
_resources_lock = threading.Lock()


def get_resources() -> Dict[str, Any]:
    global _shared_resources
    if _shared_resources:
        return _shared_resources

    with _resources_lock:
        if _shared_resources:
            return _shared_resources

        logger.info("Shared Resources: Loading all global resources...")
        _shared_resources["nlp_model"] = get_nlp_model(settings.models.nlp)
        logger.info("Shared Resources: Global resources loaded.")

    return _shared_resources


def unload_resources():
    global _shared_resources
    with _resources_lock:
        if not _shared_resources:
            return

        logger.info("Shared Resources: Unloading all global resources...")
        unload_nlp_model()
        _shared_resources.clear()
        logger.info("Shared Resources: Global resources unloaded.")
