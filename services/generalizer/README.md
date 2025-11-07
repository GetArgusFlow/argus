# Argus Generalizer

Argus Generalizer is a microservice designed to transform an unstructured product title or description into a fully structured, multi-language JSON object. The service utilizes a local Large Language Model (LLM), whose output is constrained by a dynamically generated, language-specific formal grammar (GBNF) to ensure accurate and consistently formatted data extraction.

This project is containerized with Docker for easy deployment and a consistent environment, following modern development standards.

---

## Table of Contents

- [Features](#features)
- [Security](#security)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start (Development)](#quick-start-development)
- [Production Deployment](#production-deployment)
- [Stopping the Service](#stopping-the-service)
- [Makefile Commands](#makefile-commands)
- [API Usage](#api-usage)
- [Multi-language Support](#multi-language-support)

---

## Features

- **FastAPI Backend** – A modern, high-performance web framework for building APIs.  
- **Secure by Default** – All API endpoints (except `/health`) are protected by a mandatory `x-api-key` header.  
- **Multi-language by Design** – Dynamically loads language-specific prompts, examples, categories, and grammars.  
- **LLM-Powered Extraction** – Uses a local, efficient Large Language Model (via `llama-cpp-python`) to understand and extract product information.  
- **Dynamic Grammar-Constrained Output** – Output is strictly defined by a language-specific GBNF grammar dynamically generated from a JSON schema.  
- **Few-Shot Prompting** – Improves accuracy with curated, language-specific few-shot examples.  
- **Fully Containerized** – A multi-stage Dockerfile and docker-compose setup for dev and prod.  
- **Professional Tooling** – YAML config, Loguru logging, Makefile automation, and Ruff linting.

---

## Security

All API endpoints (except `/health`) require a valid API key in the `x-api-key` header.

- **Development:** Default key – `default_dev_key` (in `config.yml`).  
- **Production:** Override with the environment variable `AUTH__API_KEY` set to a strong random key.

**Production Warning:** The service listens on `0.0.0.0`. Always place it behind a firewall or API gateway; do **not** expose it directly to the public internet.

---

## Architecture

Argus Generalizer operates in several steps:

1. **Language Identification** – Determines the request language or falls back to the default.  
2. **Dynamic Asset Loading** – Loads prompt, examples, and grammar from `app/prompts/{lang}/`.  
3. **Prompt Construction** – Builds a complete prompt using system and example text.  
4. **Model Invocation & Grammar Enforcement** – The LLM generates JSON following the grammar.  
5. **Response Delivery** – Returns a guaranteed-valid, structured JSON.

---

## Prerequisites

- Docker & Docker Compose  
- `make` (Linux/macOS; installable on Windows)  
- `yq` (for YAML manipulation in Makefile)

---

## Quick Start (Development)

Run all commands from the `services/generalizer/` directory.

### 1. Configure

```bash
cp .env.example .env
```

(Optional) Change the default language in `.env`:

```bash
SERVICE__DEFAULT_LANGUAGE=nl
```

### 2. Setup

Download models and generate grammars:

```bash
make setup
```

### 3. Start

Run the service:

```bash
make up-dev
```

Access the API at [http://localhost:8003](http://localhost:8003) and docs at `/docs`.

---

## Production Deployment

### 1. Build Image

```bash
make build
```

### 2. Run Service

```bash
make up
```

Optimized production build with a lean image.

---

## Stopping the Service

Stop and remove containers:

```bash
make down
```

---

## Makefile Commands

### Service-Specific

| Command | Description |
|----------|-------------|
| `make setup` | Run download and generation tasks. |
| `make download-tools` | Download grammar generation tools. |
| `make generate-grammars` | Generate grammars from schemas. |
| `make download-model` | Download required LLM model. |

### Standard Commands

| Command | Description |
|----------|-------------|
| `make up` | Start in PRODUCTION mode. |
| `make up-dev` | Start in DEVELOPMENT mode. |
| `make down` | Stop and remove containers. |
| `make logs` | Show live logs. |
| `make build` | Build production image. |
| `make build-dev` | Build development image. |
| `make test` | Run tests. |
| `make lint` | Lint code. |
| `make format` | Format code. |
| `make health` | Check `/health` endpoint. |

---

## API Usage

### Endpoint

`POST /api/v1/generalize`  
Transforms a product title into structured JSON.

#### Headers

```
x-api-key: YOUR_API_KEY
Content-Type: application/json
```

#### Request Example

```json
{
  "language": "en",
  "title": "Solid oak dining table 200x100 cm natural finish"
}
```

#### Response Example

```json
{
  "extracted_data": {
    "material": "oak",
    "type": "dining table",
    "dimensions": "200x100 cm",
    "finish": "natural"
  },
  "process_time": 1.25
}
```

#### Example cURL

```bash
# English
curl -X POST "http://localhost:8003/api/v1/generalize"    -H "Content-Type: application/json"    -H "x-api-key: default_dev_key"    -d '{"language":"en","title":"solid oak table"}'

# Dutch
curl -X POST "http://localhost:8003/api/v1/generalize"    -H "Content-Type: application/json"    -H "x-api-key: default_dev_key"    -d '{"language":"nl","title":"eiken eettafel 200x100"}'
```

---

## Multi-language Support

### How It Works

Each language lives under `app/prompts/{lang}/` (e.g., `en/`, `nl/`, etc.).  
`make generate-grammars` builds GBNF grammars dynamically from localized templates.

### Add a New Language

```bash
mkdir -p app/prompts/fr
```

Add the following files:

- `prompt.py` – translated system prompt.  
- `examples.py` – few-shot examples.  
- `categories.yml` – translated categories.

Generate the grammar:

```bash
make generate-grammars
```

Restart the service:

```bash
make down && make up-dev
```

You can now send requests with `"language": "fr"`.

---

© ArgusFlow
