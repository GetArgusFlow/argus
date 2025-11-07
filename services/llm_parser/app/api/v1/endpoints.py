# app/api/v1/endpoints.py

from fastapi import APIRouter, Request, HTTPException, Depends
from app.core.model import run_inference
from .schemas import ParseRequest
from loguru import logger
from .security import get_api_key

# All routes in this router will now require the API key
router = APIRouter(dependencies=[Depends(get_api_key)])


@router.post("/parse")
async def parse_html(request: Request, parse_req: ParseRequest):
    """(NEEDS KEY) Parses an HTML snippet using the LLM and grammar."""
    llm = getattr(request.app.state, "llm", None)
    grammar = getattr(request.app.state, "grammar", None)

    if not llm or not grammar:
        logger.warning("Parse request received but model is not available.")
        raise HTTPException(
            status_code=503, detail="Service is not ready, model not loaded."
        )

    try:
        # get the LLM and Grammar objects
        result = run_inference(
            html_snippet=parse_req.html_snippet, llm=llm, grammar=grammar
        )

        return result
    except Exception as e:
        logger.error(f"Inference failed: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to process the HTML snippet."
        )
