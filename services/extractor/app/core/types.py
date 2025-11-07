# argus/services/extractor/app/core/types.py

from pydantic import BaseModel
from enum import Enum
from typing import Dict, Any, List, Union
from functools import total_ordering


@total_ordering
class FieldExtractionStatus(Enum):
    """
    Defines the reliability status of an extracted field.
    """

    NOT_FOUND = 0
    GENERIC_FALLBACK = 1
    NLP_HEURISTIC = 2
    MODULE_HEURISTIC = 3
    MODULE_REGEX = 4
    FOUND_IN_SPECS = 5
    DOMAIN_MAPPING = 6
    OPEN_GRAPH = 7
    JSON_LD = 8
    FOUND_IN_SHARED_CONTEXT = 9

    def __lt__(self, other):
        if not isinstance(other, FieldExtractionStatus):
            return NotImplemented
        return self.value < other.value

    def __eq__(self, other):
        if not isinstance(other, FieldExtractionStatus):
            return NotImplemented
        return self.value == other.value


class SpecificationCategory(BaseModel):
    category: str
    details: Union[Dict[str, Any], List[Any]]


class ExtractionResult(BaseModel):
    """A model to capture a single extraction result and its metadata."""

    value: Any
    source: str
    score: int
    status: FieldExtractionStatus
