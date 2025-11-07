# argus/services/extractor/app/api/v1/endpoints.py

from fastapi import APIRouter, Request, HTTPException, Depends  # MODIFIED
from loguru import logger
from playwright.async_api import (
    async_playwright,
    TimeoutError as PlaywrightTimeoutError,
)
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
import json

from app.api.v1.schemas import ExtractionRequest, ExtractionResponse
from app.core.analyzer import ProductPageAnalyzer
from app.config import settings
from .security import get_api_key

router = APIRouter(dependencies=[Depends(get_api_key)])

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"


@router.post("/extract", response_model=ExtractionResponse)
async def extract_data(request: Request, payload: ExtractionRequest):
    """
    (NEEDS KEY) Extracts structured data from a product page.

    - If 'html_content' is provided (and not empty), it's used directly for analysis.
    - If 'html_content' is null or empty, the 'url' parameter is used to fetch
      the page content via Playwright, which is then analyzed.
    """
    # Get the analyzer instance that was loaded on startup
    analyzer: ProductPageAnalyzer = getattr(request.app.state, "analyzer", None)

    if not analyzer:
        logger.error("API: /extract called but analyzer is not available in app.state.")
        raise HTTPException(
            status_code=503,  # Service Unavailable
            detail="The analysis service is not ready. The analyzer failed to load on startup.",
        )

    logger.info(f"API: Received extraction request for URL: {payload.url}")

    html_content = payload.html_content
    # Ensure url is a string for all operations
    url = str(payload.url)

    # If no HTML content is provided (falsy check for None or ""), fetch it
    if not html_content:
        logger.info(f"No html_content provided for {url}. Fetching with Playwright...")
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                context = await browser.new_context(
                    viewport={"width": 1920, "height": 1080}, user_agent=USER_AGENT
                )
                page = await context.new_page()
                logger.info(f"Navigating to {url} with Playwright...")
                await page.goto(url, wait_until="networkidle", timeout=30000)

                # Assign fetched content to html_content
                html_content = await page.content()
                await browser.close()
                logger.info(
                    f"Successfully retrieved HTML for {url}. Content length: {len(html_content)}"
                )

        except PlaywrightTimeoutError:
            logger.error(f"Playwright timed out while trying to load {url}")
            raise HTTPException(
                status_code=408,
                detail=f"Timeout: The page at {url} took too long to load.",
            )
        except Exception as e:
            logger.error(
                f"An unexpected error occurred with Playwright for {url}: {e}",
                exc_info=True,
            )
            raise HTTPException(
                status_code=500,
                detail=f"An internal error occurred while fetching the page content: {e}",
            )
    else:
        logger.info(f"Using provided html_content for {url}.")

    # At this point, html_content is populated either from the payload or Playwright
    try:
        # Call the analyze method on the shared analyzer instance
        extracted_data = analyzer.analyze(
            html_content=html_content,
            url=url,
            use_llm=payload.use_llm,  # Pass the flag here
        )

        # Log extracted data in development mode
        # Check environment setting (adjust 'development' if your setting is different)
        if settings.service.environment == "development":
            try:
                log_dir = Path(settings.service.log_dir)
                log_dir.mkdir(parents=True, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                sanitized_domain = urlparse(url).netloc.replace(".", "_")
                # Save as .json
                filename = f"{timestamp}_{sanitized_domain}.json"
                file_path = log_dir / filename

                # Serialize the Pydantic model to a JSON string
                file_path.write_text(
                    json.dumps(extracted_data, indent=2), encoding="utf-8"
                )

                # Update success message
                logger.success(f"Extracted data successfully saved to: {file_path}")
            except Exception as e:
                logger.warning(f"Could not save extracted_data to file. Reason: {e}")
        # End save data

        # Return the successful response
        return ExtractionResponse(data=extracted_data, message="Extraction successful")

    except Exception as e:
        logger.error(
            f"API: An unexpected error occurred during analysis for {url}: {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500, detail="An internal error occurred during analysis."
        )
