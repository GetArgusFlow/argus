# argus/services/matcher/app/api/v1/schemas.py

from pydantic import BaseModel, Field
from typing import List, Optional, Tuple

from app.config import settings


class TestProductRequest(BaseModel):
    product_id: int
    store_id: int
    title: str = "Test Product"
    brand: Optional[str] = None
    contents: Optional[str] = None
    unit: Optional[str] = None


class MatchRequest(BaseModel):
    top_k: int = Field(settings.matcher.top_k_default, gt=0, le=100)
    allowed_store_ids: Optional[List[int]] = None


class MatchTextRequest(MatchRequest):
    text: str = Field(..., min_length=3)


class MatchIdRequest(MatchRequest):
    product_id: int


class ProductIdRequest(BaseModel):
    product_id: int


class MatchResponse(BaseModel):
    query: str
    matches: List[Tuple[int, float]]


class IdMatchResponse(BaseModel):
    query_id: int
    matches: List[Tuple[int, float]]


class StatusResponse(BaseModel):
    status: str
    product_id: int


class TrainingResponse(BaseModel):
    message: str
