# argus/services/generalizer/app/api/v1/endpoints.py

import time
from fastapi import APIRouter, HTTPException, Depends
from loguru import logger

from app.api.v1.schemas import GeneralizationRequest, GeneralizationResponse
from app.core.model import generalizer_model
from app.config import settings
from .security import get_api_key

# All routes in this router will now require the API key
router = APIRouter(dependencies=[Depends(get_api_key)])


@router.post("/generalize", response_model=GeneralizationResponse)
async def generalize_title(request: GeneralizationRequest):
    """
    (NEEDS KEY) Generalizes a product title into a structured JSON object.
    """
    if generalizer_model.llm is None:
        raise HTTPException(status_code=503, detail="Model is not loaded yet.")

    start_time = time.time()

    # Logic to determine language: use user's, or fall back to config default
    lang_to_use = request.language or settings.service.default_language

    try:
        # Pass the determined language to the predict method
        extracted_data = generalizer_model.predict(request.title, lang_to_use)

        end_time = time.time()
        process_time = end_time - start_time

        logger.info(
            f"Title '{request.title}' (lang={lang_to_use}) generalized in {process_time:.2f}s."
        )

        return GeneralizationResponse(
            extracted_data=extracted_data, process_time=process_time
        )
    except ValueError as e:
        logger.error(f"Prediction error: {e}")
        if "Unsupported language" in str(e):
            raise HTTPException(status_code=422, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during generalization: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")
