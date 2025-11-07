# argus/services/generalizer/app/api/v1/schemas.py

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional  # <-- IMPORT OPTIONAL


class GeneralizationRequest(BaseModel):
    title: str = Field(
        ..., min_length=3, description="The product title to generalize."
    )
    # Make language optional and remove the default
    language: Optional[str] = Field(
        None,
        min_length=2,
        max_length=10,
        description="ISO 639-1 language code (e.g., 'nl', 'en'). If omitted, service default is used.",
    )


class GeneralizationResponse(BaseModel):
    extracted_data: Dict[str, Any]
    process_time: float = Field(..., description="Processing time in seconds.")
