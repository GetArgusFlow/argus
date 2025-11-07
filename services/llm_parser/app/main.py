# app/main.py

from fastapi import FastAPI, HTTPException, Request
from contextlib import asynccontextmanager
from loguru import logger
from pathlib import Path
import sys

from app.config import settings
from app.core.model import load_model
from app.api.v1.endpoints import router as api_router

# Configure Loguru logger
log_level = settings.service.log_level.strip().upper()
log_dir = Path(settings.service.log_dir)
log_file = log_dir / "service.log"
logger.remove()
logger.add(sys.stderr, level=log_level)
logger.add(log_file, rotation="10 MB", level=log_level)


# De logger.add() functie accepteert dit Path-object direct.
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code to run on startup
    logger.info("Starting up service...")
    llm_instance, grammar_instance = load_model()

    # Debug logging
    logger.info(
        f"[DEBUG] In lifespan, direct na load_model. Type llm: {type(llm_instance)}"
    )
    logger.info(
        f"[DEBUG] In lifespan, direct na load_model. Type grammar: {type(grammar_instance)}"
    )

    app.state.llm = llm_instance
    app.state.grammar = grammar_instance
    logger.info("Model and grammar assigned to app.state.")
    yield
    # Code to run on shutdown
    logger.info("Shutting down service...")
    app.state.llm = None
    app.state.grammar = None


app = FastAPI(
    title="Argus LLM Parser",
    description="A service to parse HTML into structured JSON using an LLM.",
    version="2.0.0",
    lifespan=lifespan,
)


# Debug endpoint
@app.get("/debug-state", tags=["Debugging"])
async def debug_state(request: Request):
    llm_obj = getattr(request.app.state, "llm", "NIET GEVONDEN")
    grammar_obj = getattr(request.app.state, "grammar", "NIET GEVONDEN")

    logger.info(
        f"[DEBUG] /debug-state aangeroepen. llm in state is type: {type(llm_obj)}"
    )

    return {
        "llm_in_state": llm_obj != "NIET GEVONDEN",
        "llm_type": str(type(llm_obj)),
        "grammar_in_state": grammar_obj != "NIET GEVONDEN",
        "grammar_type": str(type(grammar_obj)),
    }


# Health endpoint
@app.get("/health", tags=["Monitoring"])
async def health_check(request: Request):  # Voeg 'request' toe
    # Check the state of the request object
    model_loaded = bool(
        getattr(request.app.state, "llm", None)
        and getattr(request.app.state, "grammar", None)
    )
    if not model_loaded:
        raise HTTPException(
            status_code=503, detail="Model is not available or failed to load."
        )
    return {"status": "ok", "model_loaded": True}


# Include the API router
app.include_router(api_router, prefix="/api/v1")

logger.info("Application setup complete.")
