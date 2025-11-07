# argus/services/matcher/app/main.py

from fastapi import FastAPI
from loguru import logger
import uvicorn

from app.api.v1.endpoints import api_router, dev_only_router
from app.core.engine import engine
from app.config import settings

app = FastAPI(
    title="Product Matcher Service",
    description="A service to find, update, and train product matches.",
    version="2.0.0",
)


@app.on_event("startup")
async def startup_event():
    """Load ML resources on service startup."""
    logger.info("Service starting up. Loading matching engine resources...")

    # Let the app fail fast if resources can't be loaded.
    # engine.load_resources() will log the critical error itself.
    engine.load_resources()


# Always include the main API router (all routes require API key)
app.include_router(api_router, prefix="/api/v1")

# Only include the dev-only (test) routes if we are NOT in production
if settings.service.environment != "production":
    app.include_router(dev_only_router, prefix="/api/v1")
    logger.warning(
        f"Service running in '{settings.service.environment}' mode. Admin/Test endpoints are ENABLED."
    )
else:
    logger.info(
        "Service running in 'production' mode. Admin/Test endpoints are DISABLED."
    )


@app.get("/health", tags=["Health Check"])
def health_check():
    model_loaded = engine.model is not None and engine.index is not None
    return {
        "status": "ok" if model_loaded else "error",
        "resources_loaded": model_loaded,
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.service.host,
        port=settings.service.port,
        log_level=settings.service.log_level.lower(),
        reload=True,
    )
