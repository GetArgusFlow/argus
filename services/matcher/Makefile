# argus/services/matcher/Makefile

# This service's name (must match the service name in docker-compose.yml)
SERVICE_NAME := matcher
# This is used by the 'health' target in common.mk
SERVICE_PORT := 8004

# Include common targets
include ../common.mk

# Service-Specific Targets

.PHONY: help_override setup check-db-connection train retrain

# Override 'help' from common.mk to show service-specific commands
help: help_override
help_override:
	@echo "Usage: make [target]"
	@echo "Standard targets (from common.mk): up, up-dev, down, logs, build, build-dev, health, etc."
	@echo ""
	@echo "Service-specific targets:"
	@echo "  setup                 - Creates .env, prepares directories."
	@echo "  check-db-connection   - Validates the database credentials in the .env file."
	@echo "  train                 - (Production) Runs fine-tuning using the .env config."
	@echo "  retrain               - (Production) Runs full re-training using the .env config."
	@echo "  train-dev             - (Development) Runs fine-tuning using the *demo DB*."
	@echo "  retrain-dev           - (Development) Runs full re-training using the *demo DB*."

setup: ensure-env
	@echo "Creating local directories..."
	@mkdir -p models

check-db-connection: ensure-env
	@echo "Checking database connection..."
	@set -a; \
	source .env; \
	set +a; \
	docker run --rm --network host mysql:8.0 \
	mysql -h$${DATABASE_HOST} -u$${DATABASE_USER} -p$${DATABASE_PASSWORD} -e "SELECT 1;" > /dev/null 2>&1 || \
	(echo "Error: Database connection failed. Please check your .env credentials." && exit 1)
	@echo "Database connection successful."

train: build
	@echo "Starting training for $(SERVICE_NAME) (using .env config)..."
	docker-compose $(COMPOSE_FILE) run --rm $(SERVICE_NAME) python -m app.core.engine --train

retrain: build
	@echo "Starting retrain for $(SERVICE_NAME) (using .env config)..."
	docker-compose $(COMPOSE_FILE) run --rm $(SERVICE_NAME) python -m app.core.engine --retrain

train-dev: build-dev
	@echo "Starting training for $(SERVICE_NAME) using demo DB..."
	$(COMPOSE_CMD_DEV) run --rm $(SERVICE_NAME) python -m app.core.engine --train

retrain-dev: build-dev
	@echo "Starting retrain for $(SERVICE_NAME) using demo DB..."
	$(COMPOSE_CMD_DEV) run --rm $(SERVICE_NAME) python -m app.core.engine --retrain