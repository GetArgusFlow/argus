# app/api/v1/schemas.py

from pydantic import BaseModel, HttpUrl, Field
from typing import Dict, Any, Optional


class ExtractionRequest(BaseModel):
    """The request body for the /extract endpoint."""

    url: HttpUrl
    html_content: Optional[str] = None
    use_llm: bool = Field(
        default=False,
        description="Enable (true) or disable (false) the LLM parser for specifications. Default: false.",
    )


class ExtractionResponse(BaseModel):
    """
    The response body for the /extract endpoint.
    This can be expanded with more specific fields later.
    """

    data: Dict[str, Any]
    message: str
