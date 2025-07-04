# ============================================================================
# GRUPONOS MELTANO NATIVE - COMPREHENSIVE PRODUCTION MAKEFILE
# Enterprise-grade Meltano pipeline management with FLEXT integration
# 100% Meltano native approach with maximum automation and monitoring
# ============================================================================

.PHONY: help setup env build test lint format typecheck security validate run dev prod deploy clean health metrics docs install update

# ============================================================================
# ENVIRONMENT CONFIGURATION
# ============================================================================

# Core directories (FLEXT workspace integration)
PROJECT_DIR := $(CURDIR)
FLEXT_WORKSPACE := $(PROJECT_DIR)/..
VENV_PATH := $(FLEXT_WORKSPACE)/.venv
VENV_ACTIVATE := $(VENV_PATH)/bin/activate
ENV_FILE := $(PROJECT_DIR)/.env

# Project structure
SRC_DIR := $(PROJECT_DIR)/src
CONFIG_DIR := $(PROJECT_DIR)/config
TRANSFORM_DIR := $(PROJECT_DIR)/transform
TESTS_DIR := $(PROJECT_DIR)/tests
DOCS_DIR := $(PROJECT_DIR)/docs

# Output directories
LOG_DIR := $(PROJECT_DIR)/logs
OUTPUT_DIR := $(PROJECT_DIR)/output_files
STATE_DIR := $(PROJECT_DIR)/.meltano/run/state
METRICS_DIR := $(PROJECT_DIR)/metrics
COVERAGE_DIR := $(PROJECT_DIR)/htmlcov

# Environment setup (FLEXT workspace pattern)
PYTHON := $(VENV_PATH)/bin/python
PIP := $(VENV_PATH)/bin/pip
MELTANO := $(VENV_PATH)/bin/meltano
DBT := $(VENV_PATH)/bin/dbt
PYTEST := $(VENV_PATH)/bin/pytest
RUFF := $(VENV_PATH)/bin/ruff
MYPY := $(VENV_PATH)/bin/mypy
BANDIT := $(VENV_PATH)/bin/bandit

# Environment activation command
ACTIVATE_ENV := source $(VENV_ACTIVATE) && cd $(PROJECT_DIR)

# Timestamps and metadata
TIMESTAMP := $(shell date '+%Y%m%d_%H%M%S')
GIT_COMMIT := $(shell git rev-parse --short HEAD 2>/dev/null || echo "unknown")
GIT_BRANCH := $(shell git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
VERSION := $(shell grep '^version' pyproject.toml | cut -d'"' -f2)

# Meltano environments
MELTANO_ENV ?= dev
MELTANO_PROFILES_DIR := $(TRANSFORM_DIR)/profiles
DBT_PROFILES_DIR := $(MELTANO_PROFILES_DIR)

# ============================================================================
# HELP AND MAIN COMMANDS
# ============================================================================

help: ## Show this help message
	@echo "🏢 GrupoNOS Meltano Native - Enterprise Data Pipeline"
	@echo "✨ 100% Meltano Native with FLEXT Enterprise Integration"
	@echo "📊 Version: $(VERSION) | Branch: $(GIT_BRANCH) | Commit: $(GIT_COMMIT)"
	@echo ""
	@echo "🚀 QUICK START:"
	@echo "  make setup          ## Complete environment setup"
	@echo "  make dev            ## Start development environment"
	@echo "  make run            ## Run full pipeline"
	@echo "  make test           ## Run all tests"
	@echo ""
	@echo "🏗️ DEVELOPMENT:"
	@echo "  make build          ## Build project"
	@echo "  make install        ## Install dependencies"
	@echo "  make update         ## Update dependencies"
	@echo "  make format         ## Format code"
	@echo "  make lint           ## Run linting"
	@echo "  make typecheck      ## Run type checking"
	@echo "  make security       ## Run security analysis"
	@echo ""
	@echo "🔄 MELTANO PIPELINE:"
	@echo "  make extract        ## Run data extraction"
	@echo "  make load           ## Run data loading"
	@echo "  make transform      ## Run dbt transformations"
	@echo "  make full-refresh   ## Full pipeline refresh"
	@echo "  make incremental    ## Incremental pipeline run"
	@echo ""
	@echo "📊 MONITORING:"
	@echo "  make health         ## Health check"
	@echo "  make status         ## Pipeline status"
	@echo "  make metrics        ## Export metrics"
	@echo "  make logs           ## View recent logs"
	@echo "  make validate       ## Validate data quality"
	@echo ""
	@echo "🚀 DEPLOYMENT:"
	@echo "  make prod           ## Production deployment"
	@echo "  make deploy         ## Deploy to environment"
	@echo "  make rollback       ## Rollback deployment"
	@echo ""
	@echo "🧹 MAINTENANCE:"
	@echo "  make clean          ## Clean generated files"
	@echo "  make reset          ## Reset pipeline state"
	@echo "  make docs           ## Generate documentation"
	@echo ""

# ============================================================================
# SETUP AND ENVIRONMENT
# ============================================================================

setup: ## Complete project setup
	@echo "🚀 Setting up GrupoNOS Meltano Native project..."
	$(MAKE) install
	$(MAKE) init-meltano
	$(MAKE) validate-config
	@echo "✅ Setup complete!"

install: ## Install all dependencies
	@echo "📦 Installing dependencies..."
	test -f $(VENV_ACTIVATE) || (echo "❌ FLEXT workspace venv not found at $(VENV_PATH)" && exit 1)
	$(ACTIVATE_ENV) && $(PIP) install -e .
	$(ACTIVATE_ENV) && $(PIP) install -e .[dev]
	@echo "✅ Dependencies installed"

update: ## Update dependencies
	@echo "🔄 Updating dependencies..."
	$(ACTIVATE_ENV) && $(PIP) install --upgrade -e .
	$(ACTIVATE_ENV) && $(PIP) install --upgrade -e .[dev]
	@echo "✅ Dependencies updated"

init-meltano: ## Initialize Meltano configuration
	@echo "🎵 Initializing Meltano..."
	$(ACTIVATE_ENV) && $(MELTANO) install
	@echo "✅ Meltano initialized"

validate-config: ## Validate configuration
	@echo "🔍 Validating configuration..."
	test -f $(ENV_FILE) || (echo "❌ .env file not found" && exit 1)
	$(ACTIVATE_ENV) && $(MELTANO) config list
	@echo "✅ Configuration valid"

# ============================================================================
# BUILD AND DEVELOPMENT
# ============================================================================

build: format lint typecheck security ## Build project with all checks
	@echo "🏗️ Building project..."
	$(ACTIVATE_ENV) && $(PYTHON) -m compileall $(SRC_DIR) $(CONFIG_DIR)
	@echo "✅ Build complete"

dev: ## Start development environment
	@echo "💻 Starting development environment..."
	$(MAKE) validate-config
	$(MAKE) health
	@echo "🚀 Development environment ready"

env: ## Test environment
	@echo "🔧 Environment Status:"
	@echo "  Python: $$($(PYTHON) --version 2>/dev/null || echo 'Not found')"
	@echo "  Meltano: $$($(MELTANO) --version 2>/dev/null || echo 'Not found')"
	@echo "  dbt: $$($(DBT) --version 2>/dev/null | head -1 || echo 'Not found')"
	@echo "  Project: $(PROJECT_DIR)"
	@echo "  Environment: $(MELTANO_ENV)"
	@echo "  Version: $(VERSION)"
	@echo "  Branch: $(GIT_BRANCH)"
	@echo "  Commit: $(GIT_COMMIT)"

# ============================================================================
# CODE QUALITY
# ============================================================================

format: ## Format code with Ruff
	@echo "🎨 Formatting code..."
	$(ACTIVATE_ENV) && $(RUFF) format $(SRC_DIR) $(CONFIG_DIR) $(TESTS_DIR)
	@echo "✅ Code formatted"

lint: ## Run linting with Ruff
	@echo "🔍 Running linting..."
	$(ACTIVATE_ENV) && $(RUFF) check $(SRC_DIR) $(CONFIG_DIR) $(TESTS_DIR) --fix
	@echo "✅ Linting complete"

typecheck: ## Run type checking with MyPy
	@echo "🔍 Running type checking..."
	$(ACTIVATE_ENV) && $(MYPY) $(SRC_DIR) $(CONFIG_DIR)
	@echo "✅ Type checking complete"

security: ## Run security analysis with Bandit
	@echo "🔒 Running security analysis..."
	$(ACTIVATE_ENV) && $(BANDIT) -r $(SRC_DIR) $(CONFIG_DIR) -f json -o $(METRICS_DIR)/security.json || true
	$(ACTIVATE_ENV) && $(BANDIT) -r $(SRC_DIR) $(CONFIG_DIR)
	@echo "✅ Security analysis complete"

# ============================================================================
# TESTING
# ============================================================================

test: ## Run all tests
	@echo "🧪 Running tests..."
	mkdir -p $(METRICS_DIR)
	$(ACTIVATE_ENV) && $(PYTEST) $(TESTS_DIR) \
		--junitxml=$(METRICS_DIR)/junit.xml \
		--cov-report=json:$(METRICS_DIR)/coverage.json
	@echo "✅ Tests complete"

test-unit: ## Run unit tests only
	@echo "🧪 Running unit tests..."
	$(ACTIVATE_ENV) && $(PYTEST) $(TESTS_DIR) -m "unit" -v

test-integration: ## Run integration tests only
	@echo "🧪 Running integration tests..."
	$(ACTIVATE_ENV) && $(PYTEST) $(TESTS_DIR) -m "integration" -v

test-meltano: ## Run Meltano-specific tests
	@echo "🧪 Running Meltano tests..."
	$(ACTIVATE_ENV) && $(PYTEST) $(TESTS_DIR) -m "meltano" -v

test-oracle: ## Run Oracle connection tests
	@echo "🧪 Running Oracle tests..."
	$(ACTIVATE_ENV) && $(PYTEST) $(TESTS_DIR) -m "oracle" -v

# ============================================================================
# MELTANO PIPELINE OPERATIONS
# ============================================================================

run: ## Run complete pipeline
	@echo "🔄 Running complete pipeline..."
	$(ACTIVATE_ENV) && $(MELTANO) run tap-oracle-wms target-oracle dbt:run
	@echo "✅ Pipeline complete"

extract: ## Run data extraction only
	@echo "📥 Running data extraction..."
	$(ACTIVATE_ENV) && $(MELTANO) elt tap-oracle-wms target-oracle --dump=catalog

load: ## Run data loading only
	@echo "📤 Running data loading..."
	$(ACTIVATE_ENV) && $(MELTANO) invoke target-oracle

transform: ## Run dbt transformations
	@echo "🔄 Running transformations..."
	$(ACTIVATE_ENV) && cd $(TRANSFORM_DIR) && $(DBT) run --profiles-dir $(DBT_PROFILES_DIR)

full-refresh: ## Full pipeline refresh
	@echo "🔄 Running full refresh..."
	$(ACTIVATE_ENV) && $(MELTANO) run tap-oracle-wms target-oracle dbt:run --full-refresh

incremental: ## Incremental pipeline run
	@echo "📈 Running incremental pipeline..."
	$(ACTIVATE_ENV) && $(MELTANO) run tap-oracle-wms target-oracle dbt:run

# ============================================================================
# MONITORING AND HEALTH
# ============================================================================

health: ## System health check
	@echo "🏥 Running health check..."
	@echo "Environment: $(shell test -f $(VENV_ACTIVATE) && echo '✅ OK' || echo '❌ Missing')"
	@echo "Configuration: $(shell test -f $(ENV_FILE) && echo '✅ OK' || echo '❌ Missing')"
	@echo "Meltano: $(shell $(ACTIVATE_ENV) && $(MELTANO) --version >/dev/null 2>&1 && echo '✅ OK' || echo '❌ Error')"
	@echo "dbt: $(shell $(ACTIVATE_ENV) && cd $(TRANSFORM_DIR) && $(DBT) debug --profiles-dir $(DBT_PROFILES_DIR) >/dev/null 2>&1 && echo '✅ OK' || echo '❌ Error')"

status: ## Pipeline status
	@echo "📊 Pipeline Status - $(shell date)"
	@echo "Environment: $(MELTANO_ENV)"
	@echo "State directory: $(STATE_DIR)"
	@if [ -d "$(STATE_DIR)" ]; then \
		echo "Recent state files:"; \
		ls -la $(STATE_DIR) | tail -5; \
	else \
		echo "No state directory found"; \
	fi

metrics: ## Export metrics
	@echo "📈 Exporting metrics..."
	mkdir -p $(METRICS_DIR)
	$(ACTIVATE_ENV) && $(MELTANO) invoke tap-oracle-wms --about > $(METRICS_DIR)/tap-info.json
	$(ACTIVATE_ENV) && $(MELTANO) state list > $(METRICS_DIR)/state-list.txt
	@echo "✅ Metrics exported to $(METRICS_DIR)"

logs: ## View recent logs
	@echo "📋 Recent logs:"
	@if [ -d "$(LOG_DIR)" ]; then \
		tail -50 $(LOG_DIR)/meltano.log 2>/dev/null || echo "No meltano.log found"; \
	else \
		echo "No log directory found"; \
	fi

validate: ## Validate data quality
	@echo "✅ Running data validation..."
	$(ACTIVATE_ENV) && cd $(TRANSFORM_DIR) && $(DBT) test --profiles-dir $(DBT_PROFILES_DIR)
	@echo "✅ Data validation complete"

# ============================================================================
# DEPLOYMENT AND PRODUCTION
# ============================================================================

prod: ## Production deployment
	@echo "🚀 Deploying to production..."
	$(MAKE) validate
	$(MAKE) test
	$(ACTIVATE_ENV) && MELTANO_ENVIRONMENT=prod $(MELTANO) run tap-oracle-wms target-oracle dbt:run
	@echo "✅ Production deployment complete"

deploy: ## Deploy to specified environment
	@echo "🚀 Deploying to $(MELTANO_ENV)..."
	$(ACTIVATE_ENV) && MELTANO_ENVIRONMENT=$(MELTANO_ENV) $(MELTANO) install
	$(ACTIVATE_ENV) && MELTANO_ENVIRONMENT=$(MELTANO_ENV) $(MELTANO) run tap-oracle-wms target-oracle dbt:run
	@echo "✅ Deployment to $(MELTANO_ENV) complete"

rollback: ## Rollback deployment
	@echo "↩️ Rolling back deployment..."
	$(ACTIVATE_ENV) && $(MELTANO) state restore --force
	@echo "✅ Rollback complete"

# ============================================================================
# MAINTENANCE AND UTILITIES
# ============================================================================

clean: ## Clean generated files
	@echo "🧹 Cleaning generated files..."
	rm -rf $(COVERAGE_DIR)
	rm -rf $(METRICS_DIR)
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "✅ Cleanup complete"

reset: ## Reset pipeline state
	@echo "🔄 Resetting pipeline state..."
	$(ACTIVATE_ENV) && $(MELTANO) state clear
	@echo "✅ State reset complete"

reset-meltano: ## Recreate Meltano installation
	@echo "🔄 Recreating Meltano installation..."
	rm -rf .meltano
	$(MAKE) init-meltano
	@echo "✅ Meltano recreated"

docs: ## Generate documentation
	@echo "📚 Generating documentation..."
	mkdir -p $(DOCS_DIR)
	$(ACTIVATE_ENV) && cd $(TRANSFORM_DIR) && $(DBT) docs generate --profiles-dir $(DBT_PROFILES_DIR)
	@echo "✅ Documentation generated"

docs-serve: ## Serve documentation
	@echo "📚 Serving documentation..."
	$(ACTIVATE_ENV) && cd $(TRANSFORM_DIR) && $(DBT) docs serve --profiles-dir $(DBT_PROFILES_DIR)

# ============================================================================
# LEGACY COMPATIBILITY (Portuguese commands)
# ============================================================================

# Maintain compatibility with existing Portuguese commands
full-sync: run ## Legacy: full sync (same as run)
incremental-sync: incremental ## Legacy: incremental sync
validate-oracle: validate ## Legacy: validate Oracle
analyze-failures: logs ## Legacy: analyze failures
clean-logs: clean ## Legacy: clean logs
monitor: status ## Legacy: monitor
stop-sync: ## Legacy: stop sync (no-op in Meltano native)
	@echo "ℹ️ In Meltano native approach, pipelines are stateless - no process to stop"

recreate-tables: reset-meltano ## Legacy: recreate tables
native-recreate-tables: reset-meltano ## Legacy: native recreate tables
reset-state: reset ## Legacy: reset state
health-check: health ## Legacy: health check
validate-data: validate ## Legacy: validate data
validate-integration: health ## Legacy: validate integration

# ============================================================================
# DEVELOPMENT UTILITIES
# ============================================================================

shell: ## Open development shell
	@echo "🐚 Opening development shell..."
	$(ACTIVATE_ENV) && exec bash

jupyter: ## Start Jupyter lab
	@echo "📓 Starting Jupyter lab..."
	$(ACTIVATE_ENV) && jupyter lab --notebook-dir=$(PROJECT_DIR)

profile: ## Profile pipeline performance
	@echo "⚡ Profiling pipeline..."
	$(ACTIVATE_ENV) && py-spy record -o $(METRICS_DIR)/profile.svg -- $(MELTANO) run tap-oracle-wms target-oracle

memory: ## Memory profiling
	@echo "🧠 Memory profiling..."
	$(ACTIVATE_ENV) && mprof run $(MELTANO) run tap-oracle-wms target-oracle
	$(ACTIVATE_ENV) && mprof plot -o $(METRICS_DIR)/memory.png

# ============================================================================
# DEFAULT TARGETS
# ============================================================================

.DEFAULT_GOAL := help

# Create required directories
$(LOG_DIR) $(OUTPUT_DIR) $(METRICS_DIR) $(DOCS_DIR):
	mkdir -p $@