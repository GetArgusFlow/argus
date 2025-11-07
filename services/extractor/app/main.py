# argus/services/extractor/app/main.py
import sys
from loguru import logger
from fastapi import FastAPI, Request, HTTPException
from contextlib import asynccontextmanager
from app.config import settings
from app.core.analyzer import ProductPageAnalyzer
from app.api.v1.endpoints import router as api_v1_router
from pathlib import Path

# Configure Loguru logger
log_level = settings.service.log_level.strip().upper()
log_dir = Path(settings.service.log_dir)
log_file = log_dir / "service.log"
logger.remove()
logger.add(sys.stderr, level=log_level)
logger.add(log_file, rotation="10 MB", level=log_level)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code to run on startup
    logger.info("Starting up service and loading analyzer...")
    # Initialize the analyzer once and store it in the application state
    app.state.analyzer = ProductPageAnalyzer()
    logger.info("ProductPageAnalyzer loaded and stored in app.state.")
    yield
    # Code to run on shutdown
    logger.info("Shutting down service...")
    app.state.analyzer = None


app = FastAPI(
    title="Argus Extractor Service",
    description="A service to extract structured data from product pages.",
    version="2.0.0",
    lifespan=lifespan,
)


@app.get("/health", tags=["Monitoring"])
async def health_check(request: Request):
    # Check if the analyzer is in the application state
    analyzer_loaded = getattr(request.app.state, "analyzer", None) is not None
    if not analyzer_loaded:
        raise HTTPException(
            status_code=503, detail="Service is unhealthy: Analyzer not loaded."
        )
    return {"status": "ok", "analyzer_loaded": True}


# Add the API routers
app.include_router(api_v1_router, prefix="/api/v1", tags=["Extraction"])

logger.info("Application setup complete. Awaiting requests...")
