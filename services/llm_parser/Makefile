# ArgusProject/argus/services/llm_parser/Makefile

SERVICE_NAME := llm_parser
SERVICE_PORT := 8002

include ../common.mk

.PHONY: help_override setup download-tools generate-grammar download-model _check_yq

# Override 'help' from common.mk to show service-specific commands
help: help_override
help_override:
	@echo "Usage: make [target]"
	@echo "Standard targets (from common.mk): up, up-dev, down, logs, build, build-dev, health, etc."
	@echo ""
	@echo "Service-specific targets:"
	@echo "  setup                 - Runs all download and generation tasks. Run this first."
	@echo "  download-tools        - Downloads the script for grammar generation."
	@echo "  generate-grammar      - Generates the GBNF grammar from the JSON schema."
	@echo "  download-model        - Downloads the required LLM model file."

PYTHON := python3
YQ := yq
TOOLS_DIR := ../../tools
MODELS_DIR := ../../models
DATA_DIR := data

SCHEMA_FILE := $(DATA_DIR)/schema.json
GRAMMAR_FILE := $(DATA_DIR)/grammar.gbnf
GRAMMAR_TOOL := $(TOOLS_DIR)/json_schema_to_grammar.py

setup: download-tools generate-grammar download-model
	@echo "All setup tasks for $(SERVICE_NAME) completed successfully."
	@echo "Checking for .env file..."
	@if [ ! -f ".env" ] && [ -f ".env.example" ]; then \
		echo "Creating .env from .env.example..."; \
		cp ".env.example" ".env"; \
	fi
	@if [ ! -f ".env" ]; then \
		echo "Error: .env file not found. Please create it from .env.example."; \
		exit 1; \
	fi

_check_yq:
	@command -v $(YQ) >/dev/null 2>&1 || { \
		echo "Error: 'yq' is not installed but is required by this Makefile."; \
		echo "Please install it from: https://github.com/mikefarah/yq#install"; \
		exit 1; \
	}

download-tools: _check_yq
	@echo "- Downloading tools..."; \
	set -e; \
	TOOL_URL=$$(yq -r '.tools.grammar_script_url' config/config.yml); \
	if [ -z "$$TOOL_URL" -o "$$TOOL_URL" = "null" ]; then \
		echo "Error: '.tools.grammar_script_url' not found in config/config.yml."; \
		exit 1; \
	fi; \
	if [ ! -f "$(GRAMMAR_TOOL)" ]; then \
		mkdir -p $(TOOLS_DIR); \
		curl --fail -s -L -o $(GRAMMAR_TOOL) "$$TOOL_URL"; \
		echo "Tool downloaded to $(GRAMMAR_TOOL)"; \
	else \
		echo "Tool file $$GRAMMAR_TOOL already exists. Skipping download."; \
	fi

generate-grammar: download-tools
	@echo "- Generating grammar..."; \
	rm -f $(GRAMMAR_FILE); \
	$(PYTHON) $(GRAMMAR_TOOL) $(SCHEMA_FILE) > $(GRAMMAR_FILE); \
	echo "Grammar generated at $(GRAMMAR_FILE)"

download-model: _check_yq
	@echo "- Downloading LLM model..."; \
	set -e; \
	MODEL_URL=$$(yq -r '.llm.source.url' config/config.yml); \
	MODEL_FILENAME=$$(yq -r '.llm.source.filename' config/config.yml); \
	\
	if [ -z "$$MODEL_URL" -o "$$MODEL_URL" = "null" -o -z "$$MODEL_FILENAME" -o "$$MODEL_FILENAME" = "null" ]; then \
		echo "Error: '.llm.source.url' or '.llm.source.filename' not found in config/config.yml."; \
		exit 1; \
	fi; \
	\
	MODEL_FILE_PATH="$(MODELS_DIR)/$$MODEL_FILENAME"; \
	mkdir -p "$(MODELS_DIR)"; \
	\
	if [ ! -f "$$MODEL_FILE_PATH" ]; then \
		echo "Downloading $$MODEL_FILENAME to $(MODELS_DIR)..."; \
		curl --fail -# -L -o "$$MODEL_FILE_PATH" "$$MODEL_URL"; \
		echo "Model downloaded successfully."; \
	else \
		echo "Model file $$MODEL_FILE_PATH already exists. Skipping download."; \
	fi