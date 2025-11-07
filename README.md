# ArgusFlow

**ArgusFlow** is a modular, microservice-based data extraction platform designed for **high performance, flexibility, and scalability**.  
It provides a unified framework for extracting structured data from websites using a collection of independent yet interconnected services.  
All services are containerized and orchestrated via **Docker Compose**, with a central **Makefile** providing full project automation.

---

## Table of Contents

- [Core Services](#core-services)  
- [Prerequisites](#prerequisites)  
- [Getting Started](#getting-started)  
- [Main Commands](#main-commands)  
- [Project Structure](#project-structure)  
- [Argus Pro](#argus-pro)

---

## Core Services

ArgusFlow consists of four primary containerized microservices, each with a specific purpose:

| Service | Port | Description |
|----------|------|-------------|
| **Extractor** | `:8001` | Extracts structured data (price, brand, etc.) from product HTML using a modular, "scoreboard-based" parser system. |
| **LLM Parser** | `:8002` | Uses a local LLM and GBNF grammar to convert complex HTML snippets (e.g., specification tables) into strict JSON. |
| **Generalizer** | `:8003` | Transforms unstructured product titles into rich, structured JSON using local LLMs and dynamic language grammars. |
| **Matcher** | `:8004` | Finds similar products in your database using a fine-tuned Sentence Transformer and a high-speed FAISS index. |

---

## Prerequisites

Before you begin, ensure you have the following installed:

- **Docker**
- **Docker Compose**
- **make**

---

## Getting Started

### 1. Clone the Repository

```bash
mkdir argus && cd argus && curl -L https://get.argusflow.com | tar -xz --strip-components=1
```

Or via Git:

```bash
git clone https://github.com/getargusflow/argus.git
cd argus
```

---

### 2. Initial Project Setup

Run the setup command once to prepare the environment.  
This will create `.env` files from the examples and execute each service’s one-time setup (e.g., downloading models):

```bash
make setup
```

---

### 3. Start the Services

To start all services in detached mode (builds images if needed):

```bash
make up
```

The services will start in the background.  
Check their status with:

```bash
docker ps
```

---

## Main Commands

All project operations are managed through the **top-level Makefile** in the `argus/` directory.

### Project Setup

| Command | Description |
|----------|-------------|
| `make setup` | Initializes the project, creates `.env` files, and runs setup tasks for all services. |

### Production Environment

| Command | Description |
|----------|-------------|
| `make build` | Builds optimized Docker images for production. |
| `make up` | Starts all services in production mode. |

### Development Environment

| Command | Description |
|----------|-------------|
| `make build-dev` | Builds development images (with debuggers, live reload, etc.). |
| `make up-dev` | Starts all services in development mode. |

### General Commands

| Command | Description |
|----------|-------------|
| `make down` | Stops and removes all running service containers. |
| `make logs` | Displays live logs for all services. |
| `make test` | Runs all test suites. |
| `make lint` | Runs lint checks for code quality. |
| `make clean` | Cleans up temporary files and caches. |

---

## Targeting a Specific Service

To run a command (like logs or test) on a single service:

```bash
cd services/extractor
make logs
```

Or for the LLM Parser:

```bash
cd services/llm_parser
make test
```

---

## Project Structure

```
argus/
├── Makefile                  # Central control hub for the project
└── services/
    ├── extractor/            # Generic HTML Extractor microservice
    ├── llm_parser/           # LLM-based HTML Snippet Parser
    ├── generalizer/          # LLM-based Title Generalizer
    └── matcher/              # Vector-based Product Matcher
```

---

## Argus Pro

**Argus Pro** is the closed-source commercial extension that unlocks advanced extraction capabilities for enterprise users.

### Why Upgrade?

- **Advanced Modules:** 

    Gain access to specialized modules for extracting complex data (EAN/SKU, Product Specifications, Original Price, Currency, etc.).
- **Optimized Performance:** 

    Enhanced pipelines and models for production-scale workloads.

### Installation

To install Argus Pro:

```bash
make install-pro
```

The script will prompt for your **license key** and automatically install the Pro extensions.  
After installation, restart all services:

```bash
make down
make up
```

---

© ArgusFlow
