# argus/Makefile
# This Makefile delegates all commands to the service-level Makefiles.
# It does NOT run docker-compose commands itself.

SHELL := /bin/bash
.DEFAULT_GOAL := help

SETUP_MARKER := .setup_complete

# Automatic Service Detection
FOUND_MAKEFILES := $(wildcard services/*/Makefile)
SERVICE_DIRS := $(dir $(FOUND_MAKEFILES))
SERVICES := $(patsubst services/%/,%,$(SERVICE_DIRS))

.PHONY: help up up-dev down logs build build-dev test lint format clean install-pro setup check-setup _check_yq

# example: sudo dnf install yq
_check_yq:
	@command -v $(YQ) >/dev/null 2>&1 || { \
		echo "Error: 'yq' is not installed but is required by this Makefile."; \
		echo "Please install it from: https://github.com/mikefarah/yq#install"; \
		exit 1; \
	}

help:
	@echo "Usage: make [target]"
	@echo "This is the global Makefile. Commands run from here affect ALL services."
	@echo "To run a command on a single service, 'cd' into its directory (e..g., 'services/matcher')."
	@echo ""
	@echo "Global Commands:"
	@echo "  up, up-dev, down, logs, build, build-dev"
	@echo "  test, lint, format, clean, setup"
	@echo ""
	@echo "Available Services: $(SERVICES)"

check-setup:
	@if [ ! -f "$(SETUP_MARKER)" ]; then \
		echo "Project is not yet initialized."; \
		echo "   Please run 'make setup' once before you begin."; \
		exit 1; \
	fi

setup: _check_yq
	@echo "Running '$@' on ALL services: $(SERVICES)"
	@for s in $(SERVICES); do \
		echo ""; \
		echo "===== Running '$@' on service '$$s' ====="; \
		$(MAKE) -C services/$$s $@; \
	done; \
	touch $(SETUP_MARKER);
	@echo ""
	@echo "Setup has finished!";
	@echo ""

# Global Docker Commands
up up-dev down restart logs build build-dev test lint format clean: check-setup
	@echo "Running '$@' on ALL services: $(SERVICES)"
	@for s in $(SERVICES); do \
		echo ""; \
		echo "===== Running '$@' on service '$$s' ====="; \
		$(MAKE) -C services/$$s $@; \
	done; \

# Pro

-include .env
export

install-pro:
	@echo "Preparing Argus Pro Installation"
	@rm -rf ../argus-pro;
	@mkdir -p ../argus-pro;

	@read -p "Enter your Argus Pro license key: " LICENSE_KEY; \
	if [ -z "$${LICENSE_KEY}" ]; then echo "Error: No token provided."; exit 1; fi; \
	\
	INSTALLER_URL="https://pro.argusflow.com"; \
	\
	mkdir -p ../argus-pro; \
	echo "Verifying license and downloading Argus Pro from $${INSTALLER_URL}..."; \
	if curl -sSLf "$${INSTALLER_URL}?key=$${LICENSE_KEY}" | tar -xzf - -C ../argus-pro --strip-components=1; then \
		echo "Argus Pro downloaded successfully."; \
	else \
		echo "\nError: Installation failed. Please check your license key or network connection."; \
		rm -rf ../argus-pro; \
		exit 1; \
	fi; \
	chmod +x ../argus-pro/setup.sh; \
	if [ -x "../argus-pro/setup.sh" ]; then \
		echo "Running Pro setup script to configure services..."; \
		../argus-pro/setup.sh .; \
		echo "Argus Pro is now configured! Please restart your services with 'make down' then 'make up'."; \
	else \
		echo "Error: setup.sh not found in the downloaded package."; \
		rm -rf ../argus-pro; \
		exit 1; \
	fi;