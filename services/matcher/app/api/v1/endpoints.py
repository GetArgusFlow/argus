# argus/services/matcher/app/api/v1/endpoints.py

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from loguru import logger

from app.core.engine import engine
from app.api.v1 import schemas
from app.api.v1.security import get_api_key

# Create routers

# 1. Main API routes, require API key, available in all environments
api_router = APIRouter(dependencies=[Depends(get_api_key)])

# 2. Dev-only routes, require API key, only loaded in dev
dev_only_router = APIRouter(
    prefix="/admin/test",
    tags=["Testing (Dev Only)"],
    dependencies=[Depends(get_api_key)],
)


# 1. Main API Routes (Key REQUIRED)


@api_router.post("/match/text", response_model=schemas.MatchResponse, tags=["Matcher"])
async def match_by_text(request: schemas.MatchTextRequest):
    """(NEEDS KEY) Matches products based on input text."""
    try:
        matches = engine.search(
            query_text=request.text,
            k=request.top_k,
            allowed_store_ids=request.allowed_store_ids,
        )
        return schemas.MatchResponse(query=request.text, matches=matches)
    except Exception as e:
        logger.error(f"Error during text matching: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/match/id", response_model=schemas.IdMatchResponse, tags=["Matcher"])
async def match_by_id(request: schemas.MatchIdRequest):
    """(NEEDS KEY) Matches products based on a product ID."""
    try:
        product_text = engine.get_text_for_id(request.product_id)
        product_data = engine.get_data_for_id(request.product_id)

        if not product_text or not product_data:
            raise HTTPException(
                status_code=404,
                detail=f"Product with ID {request.product_id} not found.",
            )

        matches = engine.search(
            query_text=product_text,
            k=request.top_k,
            query_data=product_data,
            allowed_store_ids=request.allowed_store_ids,
        )
        return schemas.IdMatchResponse(query_id=request.product_id, matches=matches)
    except Exception as e:
        logger.error(f"Error during ID matching: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post(
    "/update/product", response_model=schemas.StatusResponse, tags=["Admin"]
)
async def update_product(request: schemas.ProductIdRequest):
    """(NEEDS KEY) Adds or updates a product in the index."""
    try:
        engine.add_product_to_index(request.product_id)
        return schemas.StatusResponse(status="added", product_id=request.product_id)
    except Exception as e:
        logger.error(f"Error updating product {request.product_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@api_router.post(
    "/delete/product", response_model=schemas.StatusResponse, tags=["Admin"]
)
async def delete_product(request: schemas.ProductIdRequest):
    """(NEEDS KEY) Deletes a product from the index."""
    try:
        engine.delete_product_from_index(request.product_id)
        return schemas.StatusResponse(status="deleted", product_id=request.product_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting product {request.product_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post(
    "/admin/train",
    status_code=202,
    response_model=schemas.TrainingResponse,
    tags=["Admin"],
)
async def train_model(background_tasks: BackgroundTasks):
    """(NEEDS KEY) Starts the standard training pipeline as a background task."""
    logger.info("Training request received. Starting task in background.")
    background_tasks.add_task(engine.run_training_pipeline, retrain=False)
    return schemas.TrainingResponse(
        message="Training has been started in the background. Check logs for progress."
    )


@api_router.post(
    "/admin/retrain",
    status_code=202,
    response_model=schemas.TrainingResponse,
    tags=["Admin"],
)
async def retrain_model(background_tasks: BackgroundTasks):
    """(NEEDS KEY) Starts the full re-training pipeline as a background task."""
    logger.info("Re-training request received. Starting task in background.")
    background_tasks.add_task(engine.run_training_pipeline, retrain=True)
    return schemas.TrainingResponse(
        message="Re-training has been started in the background. Check logs for progress."
    )


# 2. Dev-Only Test Routes (Key REQUIRED)


@dev_only_router.post("/add_product", response_model=schemas.StatusResponse)
async def add_test_product(request: schemas.TestProductRequest):
    """
    (FOR TESTING) Adds a product to the DB *and* the index.
    """
    try:
        engine.add_test_product(request.model_dump())
        return schemas.StatusResponse(
            status="added_test_product", product_id=request.product_id
        )
    except Exception as e:
        logger.error(f"Error adding test product {request.product_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@dev_only_router.post("/delete_product", response_model=schemas.StatusResponse)
async def delete_test_product(request: schemas.ProductIdRequest):
    """
    (FOR TESTING) Deletes a product from the DB *and* the index.
    """
    try:
        engine.delete_test_product(request.product_id)
        return schemas.StatusResponse(
            status="deleted_test_product", product_id=request.product_id
        )
    except Exception as e:
        logger.error(f"Error deleting test product {request.product_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
