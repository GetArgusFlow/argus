# Argus LLM Parser

Argus LLM Parser is a standalone microservice designed to parse HTML snippets into structured JSON data using a local Large Language Model (LLM). It leverages a JSON schema to generate a strict grammar, ensuring that the LLM's output is always valid and conforms to the desired structure.

This service is containerized with Docker for easy deployment and environment consistency, following modern development standards.

---

## Table of Contents

- [Features](#features)
- [Security](#security)
- [Prerequisites](#prerequisites)
- [Quick Start (Development)](#quick-start-development)
- [Production Deployment](#production-deployment)
- [Stopping the Service](#stopping-the-service)
- [API Usage](#api-usage)

---

## Features

- **FastAPI Backend** — A modern, high-performance web framework.
- **Secure by Default** — All API endpoints (except `/health`) are protected by a mandatory `x-api-key` header.
- **LLM Integration** — Uses `llama-cpp-python` for efficient inference on CPU or GPU.
- **Strict Output Guarantee** — Employs a GBNF grammar generated from a JSON schema to ensure valid, structured JSON output.
- **Fully Dockerized** — Includes a multi-stage Dockerfile and `docker-compose.yml` for fast, reproducible setup.
- **Professional Tooling:**
  - Configuration via YAML (`config/config.yml`) and `.env` files.
  - Structured logging with Loguru.
  - Modular project organization (`app/core`, `app/api`).
  - Automated setup and testing tasks via a Makefile.

---

## Security

All API endpoints (except for `/health`) require a valid API key passed in the `x-api-key` header.

- **Development:** The default key is `default_dev_key` (set in `config.yml`).
- **Production:** You **must** override this by setting the `AUTH__API_KEY` environment variable to a strong, randomly generated key.

> **Production Warning:** The service listens on `0.0.0.0`. It is strongly recommended to run it behind a firewall or API gateway and not expose it directly to the public internet.

---

## Prerequisites

- Docker and Docker Compose
- `make` (available on Linux/macOS, or via Chocolatey/WSL on Windows)
- `yq` (required by the Makefile; see [installation guide](https://github.com/mikefarah/yq#install))

---

## Quick Start (Development)

All commands should be executed from the `services/llm_parser/` directory.

### 1. Configuration

Create a local environment configuration file from the example template:

```bash
cp .env.example .env
```

> Note: `.env.example` may not be included; use this as a setup reference.

### 2. Initial Setup (One-Time Only)

Run the setup command to perform all initialization tasks:

```bash
make setup
```

This will:
- Download the `json_schema_to_grammar.py` utility.
- Generate the `grammar.gbnf` file from `data/schema.json`.
- Download the default LLM model.

### 3. Start the Service

Start the service in development mode (with live reloading):

```bash
make up-dev
```

Access the service at [http://localhost:8002](http://localhost:8002)

Interactive API documentation is available at [http://localhost:8002/docs](http://localhost:8002/docs)

---

## Production Deployment

### 1. Build the Production Image

From the `services/llm_parser/` directory:

```bash
make build
```

### 2. Start the Production Service

```bash
make up
```

The service now runs in optimized production mode.

---

## Stopping the Service

To stop and remove all containers associated with this service:

```bash
make down
```

---

## API Usage

### POST `/api/v1/parse`

(Requires API key) Parses an HTML snippet using the local LLM with grammar constraints.

#### Headers

```
x-api-key: YOUR_API_KEY
```

#### Request Body

```json
{
  "html_snippet": "<div><h1>Specification</h1><div><div>Size</div></div><div>xxl</div></div>"
}
```

#### Example Response (200 OK)

```json
{
  "category": "Specification",
  "details": {
    "Size": "xxl"
  }
}
```

#### Example with curl

```bash
curl -X POST "http://localhost:8002/api/v1/parse"    -H "Content-Type: application/json"    -H "x-api-key: default_dev_key"    -d '{"html_snippet": "<div><h1>Specification</h1><div><div>Size</div></div><div>xxl</div></div>"}'
```

---

© ArgusFlow
