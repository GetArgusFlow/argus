# argus/services/generalizer/app/main.py

from fastapi import FastAPI
from loguru import logger
import uvicorn

from app.api.v1.endpoints import router as api_router
from app.core.model import generalizer_model
from app.config import settings

app = FastAPI(
    title="Generalizer Service",
    description="A service to generalize product titles into structured JSON.",
    version="1.0.0",
)


@app.on_event("startup")
async def startup_event():
    """Loads the model when the service starts."""
    logger.info("Service startup: Loading model...")
    generalizer_model.load()


app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["Health Check"])
def health_check():
    return {"status": "ok", "model_loaded": generalizer_model.llm is not None}


if __name__ == "__main__":
    # Use the settings from the pydantic object
    uvicorn.run(
        "app.main:app",
        host=settings.service.host,
        port=settings.service.port,
        log_level=settings.service.log_level.lower(),
        reload=True,
    )
