# ArgusProject/argus/services/generalizer/Makefile

SERVICE_NAME := generalizer
SERVICE_PORT := 8003

include ../common.mk

.PHONY: help_override setup download-tools generate-grammars download-model _check_yq

# Override 'help' from common.mk to show service-specific commands
help: help_override
help_override:
	@echo "Usage: make [target]"
	@echo "Standard targets (from common.mk): up, up-dev, down, logs, build, build-dev, health, etc."
	@echo ""
	@echo "Service-specific targets:"
	@echo "  setup                 - Runs all download and generation tasks. Run this first."
	@echo "  download-tools        - Downloads the script for grammar generation."
	@echo "  generate-grammars     - Generates GBNF grammars for all languages from their schemas."
	@echo "  download-model        - Downloads the required LLM model file."

PYTHON := python3
YQ := yq
TOOLS_DIR := ../../tools
MODELS_DIR := ../../models
DATA_DIR := data

# Define the source template
SCHEMA_TEMPLATE := $(DATA_DIR)/schema.template.json
GRAMMAR_TOOL := $(TOOLS_DIR)/json_schema_to_grammar.py

PROMPT_DIR := app/prompts
# Correctly find language directory names (nl, en, etc.)
LANG_DIRS := $(wildcard $(PROMPT_DIR)/*/categories.yml)
LANGS := $(notdir $(patsubst %/categories.yml,%,$(LANG_DIRS)))

setup: download-tools generate-grammars download-model
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
	@command -v $(YQ) >/dev/null 2_check_yq:
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
		echo "Downloading grammar tool to $(GRAMMAR_TOOL)..."; \
		curl --fail -s -L -o $(GRAMMAR_TOOL) "$$TOOL_URL"; \
	else \
		echo "Tool $(GRAMMAR_TOOL) already exists. Skipping download."; \
	fi

generate-grammars: download-tools _check_yq
	@echo "- Generating grammars for languages: $(LANGS)..."
	@set -e; \
	if [ -z "$(LANGS)" ]; then \
		echo "Error: No language directories found in $(PROMPT_DIR) containing categories.yml"; \
		exit 1; \
	fi; \
	for lang in $(LANGS); do \
		echo "  - Processing $$lang..."; \
		LANG_DIR=$(PROMPT_DIR)/$$lang; \
		CATEGORIES_FILE=$$LANG_DIR/categories.yml; \
		SCHEMA_FILE=$$LANG_DIR/schema.json; \
		GRAMMAR_FILE=$$LANG_DIR/grammar.gbnf; \
		\
		echo "    - Generating $$SCHEMA_FILE from template and $$CATEGORIES_FILE"; \
		$(YQ) eval \
			'. as $$schema | load("'$$CATEGORIES_FILE'") as $$cats | $$schema.properties.category = {"type": ["string", "null"], "enum": $$cats} | $$schema.required += "category" | $$schema' \
			$(SCHEMA_TEMPLATE) > $$SCHEMA_FILE; \
		\
		echo "    - Generating $$GRAMMAR_FILE from $$SCHEMA_FILE"; \
		rm -f $$GRAMMAR_FILE; \
		$(PYTHON) $(GRAMMAR_TOOL) $$SCHEMA_FILE > $$GRAMMAR_FILE; \
	done; \
	echo "All grammars generated successfully."

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