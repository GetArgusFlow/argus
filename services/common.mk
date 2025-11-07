# argus/services/common.mk
# This Makefile is included by service-level Makefiles (e.g., matcher/Makefile)
# It assumes it's running from within a service directory (e.g., services/matcher/)

# Config
ROOT_DIR := ../..
# SERVICE_NAME must be defined in the Makefile that includes this one.

# Check docker version
COMPOSE_V1 := $(shell which docker-compose 2>/dev/null)
ifeq ($(COMPOSE_V1),)
    COMPOSE_CMD := docker compose
else
    COMPOSE_CMD := docker-compose
endif

# Add the local (service) compose file if it exists
BASE_FILES :=
ifneq ($(wildcard docker-compose.yml),)
  BASE_FILES += -f docker-compose.yml
endif

# docker-compose.pro.yml
PRO_FILES :=
ifneq ($(wildcard docker-compose.pro.yml),)
  PRO_FILES := -f docker-compose.pro.yml
endif

# PROD command (for 'make up', 'make build')
PROD_FILES := $(BASE_FILES)
ifneq ($(wildcard docker-compose.prod.yml),)
  PROD_FILES += -f docker-compose.prod.yml
endif

# DEV for specific environment variables and services
DEV_FILES := $(BASE_FILES)
ifneq ($(wildcard docker-compose.dev.yml),)
  DEV_FILES += -f docker-compose.dev.yml
endif

# TEST command (for 'make test')
# This uses dev files + a specific test override
TEST_FILES := $(DEV_FILES)
ifneq ($(wildcard docker-compose.test.yml),)
  TEST_FILES += -f docker-compose.test.yml
endif

# Define commands
COMPOSE_CMD_PROD := $(COMPOSE_CMD) $(PROD_FILES) $(PRO_FILES)
COMPOSE_CMD_DEV := $(COMPOSE_CMD) $(DEV_FILES) $(PRO_FILES)
COMPOSE_CMD_TEST := $(COMPOSE_CMD) $(TEST_FILES) $(PRO_FILES)
COMPOSE_CMD_ALL := $(COMPOSE_CMD) $(PROD_FILES) $(DEV_FILES) $(TEST_FILES) $(PRO_FILES)

# Standard Targets
.PHONY: help _common_help up up-dev down logs build build-dev test lint format clean health ensure-env ensure-network

help: _common_help

_common_help:
	@echo "Usage: make [target]"
	@echo "This is a service-level Makefile for $(SERVICE_NAME)."
	@echo "Run commands from here to affect ONLY this service."
	@echo ""
	@echo "Standard Targets:"
	@echo "  setup		 - Run $(SERVICE_NAME) setup."
	@echo "  up			- Start $(SERVICE_NAME) in PRODUCTION mode."
	@echo "  up-dev		- Start $(SERVICE_NAME) in DEVELOPMENT mode."
	@echo "  down		  - Stop and remove $(SERVICE_NAME) containers (and dev dependencies)."
	@echo "  logs		  - Show live logs for $(SERVICE_NAME)."
	@echo "  build		 - Build the PRODUCTION image for $(SERVICE_NAME)."
	@echo "  build-dev	 - Build the DEVELOPMENT image for $(SERVICE_NAME)."
	@echo "  test		  - Run tests for $(SERVICE_NAME)."
	@echo "  lint		  - Run the linter for $(SERVICE_NAME)."
	@echo "  format		- Format code for $(SERVICE_NAME)."
	@echo "  clean		 - Clean Python cache files."
	@echo "  health		- Check the /health endpoint of $(SERVICE_NAME)."

# Include the root .env file for shared vars
-include $(ROOT_DIR)/.env
# Include the local .env file for service-specific vars
-include .env
# Export all variables to sub-processes (like docker compose)
export

ensure-network:
	@docker network inspect argus_network >/dev/null 2>&1 || docker network create argus_network

# Create .env file for services
ensure-env:
	@echo "Checking for required .env files..."
	@if [ ! -f ".env" ] && [ -f ".env.example" ]; then \
		echo "Creating main .env from .env.example..."; \
		cp ".env.example" ".env"; \
	fi

setup: ensure-env
	@echo " $(SERVICE_NAME) setup..."

up: ensure-env ensure-network
	@echo "Starting $(SERVICE_NAME) in PRODUCTION mode..."
	$(COMPOSE_CMD_PROD) up --build -d $(SERVICE_NAME)

up-dev: ensure-env  ensure-network
	@echo "Starting $(SERVICE_NAME) in DEVELOPMENT mode..."
	SERVICE__ENVIRONMENT=development $(COMPOSE_CMD_DEV) up --build -d $(SERVICE_NAME)

down: ensure-env
	@echo "Stopping and removing $(SERVICE_NAME)..."
	# --remove-orphans is key to removing dev-only containers (like db-demo)
	$(COMPOSE_CMD_ALL) down --remove-orphans

logs: ensure-env
	@echo "Tailing logs for $(SERVICE_NAME)..."
	$(COMPOSE_CMD_ALL) logs -f $(SERVICE_NAME)

build: ensure-env
	@echo "Building PRODUCTION image for $(SERVICE_NAME)..."
	SERVICE__ENVIRONMENT=production $(COMPOSE_CMD_PROD) build $(SERVICE_NAME)

build-no-cache: ensure-env
	@echo "Building PRODUCTION image for $(SERVICE_NAME)..."
	SERVICE__ENVIRONMENT=production $(COMPOSE_CMD_PROD) build --no-cache $(SERVICE_NAME)

build-dev: ensure-env
	@echo "Building DEVELOPMENT image for $(SERVICE_NAME)..."
	SERVICE__ENVIRONMENT=development $(COMPOSE_CMD_DEV) build $(SERVICE_NAME)

build-dev-no-cache: ensure-env
	@echo "Building DEVELOPMENT image for $(SERVICE_NAME)..."
	SERVICE__ENVIRONMENT=development $(COMPOSE_CMD_DEV) build --no-cache $(SERVICE_NAME)

test: ensure-env
ifneq ($(wildcard tests),)
	@echo "'tests' directory found. Starting TEST environment for $(SERVICE_NAME)..."
	SERVICE__ENVIRONMENT=test $(COMPOSE_CMD_TEST) up --build -d $(SERVICE_NAME)
	@echo "Waiting for server to be ready..."
	@sleep 5

	@echo "Running tests for $(SERVICE_NAME)..."
	@( $(COMPOSE_CMD_TEST) exec $(SERVICE_NAME) pytest tests ) ; \
	EXIT_CODE=$$? ; \

	@echo "Stopping TEST environment for $(SERVICE_NAME)..." ; \
	$(COMPOSE_CMD_TEST) down --remove-orphans ; \
	(exit $$EXIT_CODE)
else
	@echo "No 'tests' directory found for $(SERVICE_NAME). Skipping test run."
endif

lint: ensure-env
	@echo "Running linter for $(SERVICE_NAME)..."
	$(COMPOSE_CMD_ALL) exec $(SERVICE_NAME) ruff check .

format: ensure-env
	@echo "Formatting code for $(SERVICE_NAME)..."
	$(COMPOSE_CMD_ALL) exec $(SERVICE_NAME) ruff format .

clean:
	@echo "Cleaning Python cache for $(SERVICE_NAME)..."
	@find . -type f -name "*.py[co]" -delete
	@find . -type d -name "__pycache__" -exec rm -rf {} +; \
	echo "Cleanup complete."

health: ensure-env
	@echo "- Checking service health at http://localhost:$(SERVICE_PORT)/health"; \
	curl -f http://localhost:$(SERVICE_PORT)/health || (echo "Health check failed." && exit 1)