# Argus Extractor

Argus Extractor is a microservice designed to extract structured product information—such as price, brand, EAN, and specifications—from the HTML of a product page.

The service utilizes a modular architecture with various parsers and a “best-score-wins” mechanism to identify the most reliable data.

This project is fully containerized with Docker for easy deployment and consistent environments, following modern development standards.

-----

## Table of Contents

- [Features](#features)
- [Security](#security)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start (Development)](#quick-start-development)
- [Production Deployment](#production-deployment)
- [Stopping the Service](#stopping-the-service)
- [API Usage](#api-usage)
- [Multilingual Support & Customization](#multilingual-support--customization)

-----

## Features

- **FastAPI Backend** — A modern, high-performance web framework for building APIs.
- **Secure by Default** — **All API endpoints** (except `/health`) are protected by a mandatory `x-api-key` header.
- **Modular Parsers** — A scalable architecture where multiple, independent parsers can exist for each data field (e.g., price, brand).
- **Intelligent Data Selection** — A “scoreboard” system weighs results from all parsers and selects the data with the highest confidence score.
- **Advanced HTML Analysis** — Uses BeautifulSoup for HTML parsing and a spaCy NLP model for smarter text analysis.
- **Browser Automation** — Integrates with Playwright to retrieve dynamically loaded (JavaScript) content.
- **Fully Containerized** — Includes multi-stage Docker builds and docker-compose.yml files for both development and production.
- **Professional Tooling:**
  - Configuration via YAML (`config/config.yml`) and `.env` files.
  - Structured logging with Loguru.
  - Automated tasks via a Makefile (linting, testing, etc.).
  - Code quality enforcement with Ruff.

-----

## Security

All API endpoints (except for the `/health` check) require a valid API key to be passed in the `x-api-key` header.

- **Development**: The default key is `default_dev_key`.
- **Production**: You **must** override this by setting the `AUTH__API_KEY` environment variable to a strong, randomly generated key.

> **Production Warning**: This service is configured to listen on `0.0.0.0`. For production, it is strongly recommended to place this service behind a firewall or API gateway and restrict network access. Do not expose it directly to the public internet.

-----

## Architecture

Argus Extractor operates in several phases to extract structured data:

### 1. HTML Pre-processing
The raw HTML is cleaned by removing “noise” (headers, footers, sidebars) based on `noise_selectors` in `config/config.yml`.

### 2. Modules
Each parser module targets a specific field (e.g., title, price). Each parser returns a result with a score. General data extractors (like `json_ld` and `open_graph`) are stored in a shared context and immediately added to the scoreboard.

### 3. Enrichment
Extracted specifications are scanned for known aliases (e.g., `"Manufacturer" → "brand"`) to fill in missing fields.

### 4. Resolving
For each field, the result with the highest score is chosen as the final output.

-----

## Prerequisites

- Docker and Docker Compose
- `make` (available on Linux/macOS; installable on Windows via WSL or Chocolatey)

-----

## Quick Start (Development)

This setup is optimized for local development with live-reloading and debugging.

### 1. Configuration

From the `argus/services/extractor/` directory, create a local configuration file from the example template:

```bash
cp .env.example .env
```

Then open `.env` to override settings from `config/config.yml` if needed.

### 2. Start the Service

Ensure you are in the `argus/services/extractor/` directory, then run:

```bash
make build-dev
```

```bash
make up-dev
```

The service will be available at:  
**http://localhost:8001**

Interactive API docs (Swagger UI):  
**http://localhost:8001/docs**

-----

## Production Deployment

For production, the service uses optimized, minimal images.

### 1. Build the Production Image

From the `argus/services/extractor/` directory:

```bash
make build
```

### 2. Start the Production Service

```bash
make up
```

The service is now running in production mode.

-----

## Stopping the Service

To stop and remove all containers associated with this service (for both dev and prod):

```bash
make down
```

-----

## API Usage

### POST `/api/v1/extract`

(Requires API key) Extracts data from a URL or provided HTML content.

All requests must include a valid API key in the header:  
`x-api-key: YOUR_API_KEY`

This endpoint has two modes:

- **Fetch Mode** — If `html_content` is null or empty, the service fetches content from the URL using Playwright.  
- **Direct Mode** — If `html_content` is provided, the service parses it directly.

#### Request Body

```json
{
  "url": "https://www.example.com/product/123",
  "html_content": "<!DOCTYPE html>...",
  "use_llm": false
}
```

#### Example (Fetch Mode)

```bash
curl -X POST "http://localhost:8001/api/v1/extract"    -H "Content-Type: application/json"    -H "x-api-key: default_dev_key"    -d '{
        "url": "https://www.domain.nl/product/1234/product.html",
        "html_content": null,
        "use_llm": true
      }'
```

#### Example (Direct Mode)

```bash
curl -X POST "http://localhost:8001/api/v1/extract"    -H "Content-Type: application/json"    -H "x-api-key: default_dev_key"    -d '{
        "url": "https://www.domain.nl/product/1234/product.html",
        "html_content": "<!DOCTYPE html><html><body>...</body></html>",
        "use_llm": false
      }'
```

#### Success Response (200 OK)

```json
{
  "data": {
    "title": "An amazing product",
    "brand": "ExampleBrand",
    "price": 123.45,
    "original_price": null,
    "currency": "USD",
    "specifications": []
  },
  "message": "Extraction successful"
}
```

-----

## Multilingual Support & Customization

The extractor supports multilingual extraction by separating language-specific keywords and regex patterns from the core logic.

### Configuration Files

1. **`config/patterns.yml` (Default)**  
   Contains the base patterns (keywords and regex) for supported languages (e.g., `en`, `nl`).  
   Note: Do not edit this file directly — updates may overwrite your changes.

2. **`config/custom_patterns.yml` (Extender)**  
   Loaded after `patterns.yml` and merged intelligently.  
   This file is `.gitignore`d, keeping your changes safe.

You can:

- Add support for a new language (e.g., `de` for German)
- Extend existing language patterns
- Override regex patterns

#### Example: Adding German Keywords

```yaml
# config/custom_patterns.yml
de:
  availability_in_stock:
    - 'auf lager'
    - 'sofort lieferbar'
  brand_label_regex: '\b(marke|hersteller)\b'
```

No code changes are required — the extractor automatically picks it up.

### Smart Fallback

If a page mixes languages, the extractor merges patterns from the detected language (e.g., `nl`) with the default fallback (`en`).  
This allows it to detect both `class="merknaam"` (from `nl`) and `class="brand"` (from `en`) on the same page.

-----

© ArgusFlow
