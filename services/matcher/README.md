# Argus Product Matcher

**Argus Product Matcher** is a high-performance, secure-by-default microservice designed to find similar products using deep learning.
It leverages a fine-tuned **Sentence Transformer** model to convert product information into vector embeddings and uses a **FAISS** index for incredibly fast similarity searches.

The service provides a complete workflow — including a **secure API for matching**, **API-key-protected endpoints** for updating the index, and a **background training pipeline** to continuously improve the model's accuracy.

---

## Table of Contents

- [Features](#features)
- [Architecture](#️architecture)
  - [API Layers](#api-layers)
  - [Training Pipeline](#training-pipeline)
  - [Serving & Matching](#serving--matching)
- [Quick Start (Development)](#quick-start-development)
- [Production Deployment](#production-deployment)
- [Makefile Commands](#️makefile-commands)
- [API Endpoints](#api-endpoints)
  - [Health Check](#health-check)
  - [Main API Endpoints (API Key Required)](#main-api-endpoints-api-key-required)
  - [Development-Only (API Key Required)](#development-only-api-key-required)

---

## Features

- **FastAPI Backend:** A modern, high-performance web framework for building APIs.
- **Secure by Default:** **All API endpoints** (except `/health`) are protected by a mandatory `x-api-key` header.
- **Environment-Aware:** Test-only endpoints are loaded only in development and completely disabled in production for added security.
- **Vector-Based Matching:** Uses a SentenceTransformer model to understand the semantic meaning of product data.
- **Blazing-Fast Search:** Implements FAISS for efficient similarity search, capable of handling millions of vectors.
- **Flexible Database Integration:** Adapts to any SQL database by defining data extraction queries in `config/config.yml` or environment variables.
- **Fine-Tuning Pipeline:** Includes a background pipeline that fine-tunes the model using positive and hard-negative product pairs from your database.
- **Incremental Updates:** Add or remove individual products (`/update/product`, `/delete/product`) without rebuilding the entire index.
- **Background Training:** Training and retraining tasks (`/admin/train`) run asynchronously for uninterrupted API performance.
- **Robust Startup:** Fails fast if required resources (model, index) are missing.
- **Fully Containerized:** Multi-stage `Dockerfile` with separate, lean environments for development and production.
- **Professional Tooling:** Structured logging (Loguru), a comprehensive `Makefile`, and environment-based configuration.

---

## Architecture

### API Layers

The API is split into three distinct layers for clarity and security:

- **Main API Endpoints** — `/api/v1/...`
  - Includes all routes like `/match/text`, `/match/id`, `/update/product`, etc.
  - **All routes in this layer require a valid `x-api-key`**.
- **Development-Only Endpoints** — `/api/v1/admin/test/...`
  - Provides routes for testing, like adding/deleting test products from the DB and index.
  - Only active when `SERVICE__ENVIRONMENT` is not `"production"`.
  - Also requires a valid `x-api-key`.
- **Health Check** — `/health`
  - A single, unsecured endpoint for checking service status and resource load.

### Training Pipeline

- Can be triggered via the API (`/admin/retrain`) or the command line (`make retrain`).
- Executes the training logic defined in `app/core/engine.py`.
- Fetches product pairs using the configured `DATABASE_QUERIES__TRAINING_PAIRS_QUERY`.
- Fine-tunes the SentenceTransformer model and saves it to `models/model_finetuned`.
- Builds and stores a new FAISS index (`products.faiss`) and ID map (`products_index_ids.npy`) from all encoded products.

### Serving & Matching

- Loads the fine-tuned model and FAISS index into memory at startup.
- `/match/text`: Encodes query text → returns most similar products.
- `/match/id`: Fetches product data by its ID → uses its text to find similar products.
- Responses include the query and a list of matches, where each match is a tuple of `(product_id, score)`.

---

## Quick Start (Development)

This guide uses the included `docker-compose.dev.yml` to launch the service and a demo database.

### 1. Configure Environment

```bash
make setup
```

This command creates a `.env` file from `.env.example` if one doesn't exist. It also runs `check-db-connection`.

The default `.env` works with the demo database but can be edited for your own setup. You must define your SQL queries here (see `config/config.yml`).

### 2. Build Developement Image

```bash
make build-dev
```

### 3. Validate Database Connection

```bash
make check-db-connection
```

### 4. Train the Model (First Time)

```bash
make retrain
```

This connects to the database, trains the model, and saves the artifacts to `models/`.

### 5. Start the Service

```bash
make up-dev
```

The service runs at [http://localhost:8004](http://localhost:8004), with Swagger UI at [http://localhost:8004/docs](http://localhost:8004/docs).

---

## Production Deployment

### 1. Configure Production Environment

```env
SERVICE__ENVIRONMENT="production"
AUTH__API_KEY="your-strong-random-secret-key"
DATABASE__HOST="your-production-db-host"
DATABASE__USER="your-prod-user"
DATABASE__PASSWORD="your-prod-password"
DATABASE__NAME="your-prod-db-name"
DATABASE_QUERIES__INDEXING_QUERY="SELECT ..."
DATABASE_QUERIES__TRAINING_PAIRS_QUERY="SELECT ..."
DATABASE_QUERIES__PRODUCT_BY_ID_QUERY="SELECT ... WHERE product_id IN :ids"
```

Setting `SERVICE__ENVIRONMENT="production"` disables all dev-only endpoints.

### 2. Build and Run

```bash
make build
make up
```

> **Production Warning:** The service listens on `0.0.0.0`. While the use of this servies is restricted with a API Key, it is best to run it behind a firewall or API gateway and never expose it directly to the public internet. 

---

## Makefile Commands

| Command | Description |
| :--- | :--- |
| `make setup` | Creates `.env`, sets up directories, and checks DB connection. |
| `make check-db-connection` | Validates `.env` DB credentials. |
| `make train` | Runs fine-tuning and indexing. |
| `make retrain` | Deletes old artifacts, runs full training pipeline. |
| `make up-dev` | Starts the service in dev mode. |
| `make up` | Starts in production mode. |
| `make down` | Stops and removes containers. |
| `make logs` | Shows container logs. |
| `make build` | Builds production image. |
| `make test` | Runs pytest. |
| `make health` | Checks the `/health` endpoint. |
| `make lint` | Runs ruff linter. |
| `make format` | Formats code using ruff. |

---

## API Endpoints

### Health Check

**GET /health**  
Checks service status and resource load.  
**Auth:**  None

### Main API Endpoints (API Key Required)

All requests must include the `x-api-key` header.

**POST /api/v1/match/text**  
Body: `{"text": "query", "top_k": 10}`

**POST /api/v1/match/id**  
Body: `{"product_id": 12345, "top_k": 10}`

**POST /api/v1/update/product**  
Body: `{"product_id": 12345}`

**POST /api/v1/delete/product**  
Body: `{"product_id": 12345}`

**POST /api/v1/admin/train**  
Triggers background fine-tuning.

**POST /api/v1/admin/retrain**  
Triggers full retraining and index rebuild.

### Development-Only (API Key Required)

**POST /api/v1/admin/test/add_product**  
Body: `{"product_id": 999, "store_id": 1, "title": "Test Item"}`

**POST /api/v1/admin/test/delete_product**  
Body: `{"product_id": 999}`

---

© ArgusFlow
