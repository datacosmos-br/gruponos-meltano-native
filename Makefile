# =============================================================================
# GRUPONOS MELTANO NATIVE - MAKEFILE
# =============================================================================

.PHONY: help setup install test run clean docs health-check validate

# Default environment
ENV ?= dev

# Project directories
PROJECT_DIR := $(shell pwd)
VENV_DIR := $(PROJECT_DIR)/.venv
SCRIPTS_DIR := $(PROJECT_DIR)/scripts
TRANSFORM_DIR := $(PROJECT_DIR)/transform
LOGS_DIR := $(PROJECT_DIR)/logs

# Colors for output
BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
NC := \033[0m

# Default target
help: ## Show this help message
	@echo "$(BLUE)GrupoNOS WMS Meltano Native Pipeline$(NC)"
	@echo "$(BLUE)=====================================$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Examples:$(NC)"
	@echo "  make setup                 # Initial project setup"
	@echo "  make install               # Install dependencies"
	@echo "  make test                  # Run all tests"
	@echo "  make run                   # Run full pipeline"
	@echo "  make run-allocation        # Run allocation sync only"
	@echo "  make health-check          # Check system health"

## Setup and Installation

setup: ## Complete project setup (includes install)
	@echo "$(BLUE)Setting up GrupoNOS WMS Meltano Native Pipeline...$(NC)"
	./setup.sh
	@echo "$(GREEN)Setup completed successfully!$(NC)"

setup-with-airflow: ## Setup project with Airflow orchestration
	@echo "$(BLUE)Setting up with Airflow orchestration...$(NC)"
	./setup.sh --with-airflow
	@echo "$(GREEN)Setup with Airflow completed successfully!$(NC)"

install: ## Install Python dependencies
	@echo "$(BLUE)Installing dependencies...$(NC)"
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "$(YELLOW)Creating virtual environment...$(NC)"; \
		python3 -m venv $(VENV_DIR); \
	fi
	@. $(VENV_DIR)/bin/activate && \
		pip install --upgrade pip && \
		pip install -r requirements.txt
	@echo "$(GREEN)Dependencies installed successfully!$(NC)"

install-dev: ## Install development dependencies
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	@. $(VENV_DIR)/bin/activate && \
		pip install -r requirements.txt && \
		pip install -e ../flext-tap-oracle-wms && \
		pip install -e ../flext-target-oracle-wms
	@echo "$(GREEN)Development dependencies installed!$(NC)"

## Environment Management

env-check: ## Check environment configuration
	@echo "$(BLUE)Checking environment configuration...$(NC)"
	@if [ ! -f ".env" ]; then \
		echo "$(RED)Error: .env file not found. Copy from .env.example$(NC)"; \
		exit 1; \
	fi
	@. $(VENV_DIR)/bin/activate && \
		export $$(grep -v '^#' .env | xargs) && \
		meltano config list
	@echo "$(GREEN)Environment configuration OK$(NC)"

env-dev: ## Set development environment
	@echo "export MELTANO_ENVIRONMENT=dev" > .env.current
	@echo "$(GREEN)Environment set to development$(NC)"

env-staging: ## Set staging environment
	@echo "export MELTANO_ENVIRONMENT=staging" > .env.current
	@echo "$(GREEN)Environment set to staging$(NC)"

env-prod: ## Set production environment
	@echo "export MELTANO_ENVIRONMENT=prod" > .env.current
	@echo "$(GREEN)Environment set to production$(NC)"

## Pipeline Operations

run: env-check ## Run complete WMS pipeline
	@echo "$(BLUE)Running complete WMS pipeline (env: $(ENV))...$(NC)"
	@. $(VENV_DIR)/bin/activate && \
		export MELTANO_ENVIRONMENT=$(ENV) && \
		export $$(grep -v '^#' .env | xargs) && \
		meltano run tap-oracle-wms target-oracle && \
		meltano invoke dbt-oracle-wms:run && \
		meltano invoke dbt-oracle-wms:test
	@echo "$(GREEN)Pipeline completed successfully!$(NC)"

run-extract: env-check ## Run extraction only
	@echo "$(BLUE)Running WMS data extraction...$(NC)"
	@. $(VENV_DIR)/bin/activate && \
		export MELTANO_ENVIRONMENT=$(ENV) && \
		export $$(grep -v '^#' .env | xargs) && \
		meltano run tap-oracle-wms target-oracle
	@echo "$(GREEN)Extraction completed successfully!$(NC)"

run-transform: env-check ## Run dbt transformations only
	@echo "$(BLUE)Running dbt transformations...$(NC)"
	@. $(VENV_DIR)/bin/activate && \
		export MELTANO_ENVIRONMENT=$(ENV) && \
		export $$(grep -v '^#' .env | xargs) && \
		cd $(TRANSFORM_DIR) && \
		dbt run --profiles-dir profiles
	@echo "$(GREEN)Transformations completed successfully!$(NC)"

run-allocation: env-check ## Run allocation sync job
	@echo "$(BLUE)Running allocation synchronization...$(NC)"
	@. $(VENV_DIR)/bin/activate && \
		export MELTANO_ENVIRONMENT=$(ENV) && \
		export $$(grep -v '^#' .env | xargs) && \
		meltano run wms_allocation_sync
	@echo "$(GREEN)Allocation sync completed!$(NC)"

run-orders: env-check ## Run orders sync job
	@echo "$(BLUE)Running orders synchronization...$(NC)"
	@. $(VENV_DIR)/bin/activate && \
		export MELTANO_ENVIRONMENT=$(ENV) && \
		export $$(grep -v '^#' .env | xargs) && \
		meltano run wms_orders_daily_sync
	@echo "$(GREEN)Orders sync completed!$(NC)"

run-master-data: env-check ## Run master data sync job
	@echo "$(BLUE)Running master data synchronization...$(NC)"
	@. $(VENV_DIR)/bin/activate && \
		export MELTANO_ENVIRONMENT=$(ENV) && \
		export $$(grep -v '^#' .env | xargs) && \
		meltano run wms_master_data_weekly
	@echo "$(GREEN)Master data sync completed!$(NC)"

## Testing and Validation

test: env-check ## Run all tests
	@echo "$(BLUE)Running all tests...$(NC)"
	@make test-connections
	@make test-dbt
	@make test-data-quality
	@echo "$(GREEN)All tests passed!$(NC)"

test-connections: env-check ## Test database connections
	@echo "$(BLUE)Testing database connections...$(NC)"
	@. $(VENV_DIR)/bin/activate && \
		export MELTANO_ENVIRONMENT=$(ENV) && \
		export $$(grep -v '^#' .env | xargs) && \
		meltano invoke tap-oracle-wms --test-connection && \
		meltano invoke target-oracle --test-connection
	@echo "$(GREEN)Connection tests passed!$(NC)"

test-dbt: env-check ## Run dbt tests
	@echo "$(BLUE)Running dbt tests...$(NC)"
	@. $(VENV_DIR)/bin/activate && \
		export MELTANO_ENVIRONMENT=$(ENV) && \
		export $$(grep -v '^#' .env | xargs) && \
		cd $(TRANSFORM_DIR) && \
		dbt test --profiles-dir profiles
	@echo "$(GREEN)dbt tests passed!$(NC)"

test-data-quality: env-check ## Run data quality checks
	@echo "$(BLUE)Running data quality checks...$(NC)"
	@. $(VENV_DIR)/bin/activate && \
		export MELTANO_ENVIRONMENT=$(ENV) && \
		export $$(grep -v '^#' .env | xargs) && \
		cd $(TRANSFORM_DIR) && \
		dbt source freshness --profiles-dir profiles
	@echo "$(GREEN)Data quality checks passed!$(NC)"

validate: env-check ## Validate configuration and setup
	@echo "$(BLUE)Validating configuration...$(NC)"
	@. $(VENV_DIR)/bin/activate && \
		export MELTANO_ENVIRONMENT=$(ENV) && \
		export $$(grep -v '^#' .env | xargs) && \
		meltano config list && \
		meltano schedule list && \
		meltano job list
	@echo "$(GREEN)Configuration validation completed!$(NC)"

## Discovery and Schema

discover: env-check ## Discover WMS schema
	@echo "$(BLUE)Discovering WMS schema...$(NC)"
	@mkdir -p schema
	@. $(VENV_DIR)/bin/activate && \
		export MELTANO_ENVIRONMENT=$(ENV) && \
		export $$(grep -v '^#' .env | xargs) && \
		meltano invoke tap-oracle-wms --discover > schema/catalog.json
	@echo "$(GREEN)Schema discovery completed! Check schema/catalog.json$(NC)"

catalog-select: env-check ## Select streams in catalog
	@echo "$(BLUE)Selecting streams in catalog...$(NC)"
	@. $(VENV_DIR)/bin/activate && \
		export MELTANO_ENVIRONMENT=$(ENV) && \
		export $$(grep -v '^#' .env | xargs) && \
		meltano select tap-oracle-wms "*.*"
	@echo "$(GREEN)All streams selected$(NC)"

## Monitoring and Health

health-check: env-check ## Comprehensive system health check
	@echo "$(BLUE)Running system health check...$(NC)"
	@. $(VENV_DIR)/bin/activate && \
		export MELTANO_ENVIRONMENT=$(ENV) && \
		export $$(grep -v '^#' .env | xargs) && \
		echo "1. Testing WMS connection..." && \
		meltano invoke tap-oracle-wms --test-connection && \
		echo "2. Testing target connection..." && \
		meltano invoke target-oracle --test-connection && \
		echo "3. Checking dbt connection..." && \
		cd $(TRANSFORM_DIR) && dbt debug --profiles-dir profiles && \
		echo "4. Checking data freshness..." && \
		dbt source freshness --profiles-dir profiles
	@echo "$(GREEN)Health check completed successfully!$(NC)"

status: ## Show pipeline status
	@echo "$(BLUE)Pipeline Status$(NC)"
	@echo "$(BLUE)===============$(NC)"
	@echo "Environment: $(ENV)"
	@echo "Last run logs:"
	@if [ -f "$(LOGS_DIR)/meltano/meltano.log" ]; then \
		tail -5 $(LOGS_DIR)/meltano/meltano.log; \
	else \
		echo "$(YELLOW)No logs found$(NC)"; \
	fi

logs: ## Show recent logs
	@echo "$(BLUE)Recent Pipeline Logs$(NC)"
	@echo "$(BLUE)====================$(NC)"
	@if [ -f "$(LOGS_DIR)/meltano/meltano.log" ]; then \
		tail -20 $(LOGS_DIR)/meltano/meltano.log; \
	else \
		echo "$(YELLOW)No Meltano logs found$(NC)"; \
	fi
	@if [ -f "$(LOGS_DIR)/dbt/dbt.log" ]; then \
		echo "\n$(BLUE)dbt logs:$(NC)"; \
		tail -10 $(LOGS_DIR)/dbt/dbt.log; \
	fi

## Documentation

docs: ## Generate and serve documentation
	@echo "$(BLUE)Generating documentation...$(NC)"
	@. $(VENV_DIR)/bin/activate && \
		cd $(TRANSFORM_DIR) && \
		dbt docs generate --profiles-dir profiles && \
		dbt docs serve --profiles-dir profiles --port 8081
	@echo "$(GREEN)Documentation server started at http://localhost:8081$(NC)"

docs-generate: ## Generate documentation only
	@echo "$(BLUE)Generating dbt documentation...$(NC)"
	@. $(VENV_DIR)/bin/activate && \
		cd $(TRANSFORM_DIR) && \
		dbt docs generate --profiles-dir profiles
	@echo "$(GREEN)Documentation generated in transform/target/$(NC)"

## Development

dev-setup: ## Setup development environment
	@echo "$(BLUE)Setting up development environment...$(NC)"
	@make install-dev
	@make env-dev
	@echo "$(GREEN)Development environment ready!$(NC)"

format: ## Format code with ruff
	@echo "$(BLUE)Formatting code...$(NC)"
	@. $(VENV_DIR)/bin/activate && \
		ruff format . && \
		ruff check --fix .
	@echo "$(GREEN)Code formatting completed!$(NC)"

lint: ## Lint code with ruff and mypy
	@echo "$(BLUE)Linting code...$(NC)"
	@. $(VENV_DIR)/bin/activate && \
		ruff check . && \
		mypy --config-file pyproject.toml .
	@echo "$(GREEN)Linting completed!$(NC)"

pre-commit: ## Run pre-commit hooks
	@echo "$(BLUE)Running pre-commit hooks...$(NC)"
	@. $(VENV_DIR)/bin/activate && \
		pre-commit run --all-files
	@echo "$(GREEN)Pre-commit checks completed!$(NC)"

## Utilities

clean: ## Clean temporary files and caches
	@echo "$(BLUE)Cleaning temporary files...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true
	@rm -rf $(TRANSFORM_DIR)/target $(TRANSFORM_DIR)/dbt_packages
	@rm -rf .pytest_cache .coverage
	@echo "$(GREEN)Cleanup completed!$(NC)"

reset: ## Reset project state (clean + remove venv)
	@echo "$(YELLOW)Resetting project state...$(NC)"
	@make clean
	@rm -rf $(VENV_DIR)
	@rm -f .env.current
	@echo "$(GREEN)Project reset completed!$(NC)"

backup: ## Backup configuration and state
	@echo "$(BLUE)Creating backup...$(NC)"
	@mkdir -p backups
	@tar -czf backups/backup-$$(date +%Y%m%d_%H%M%S).tar.gz \
		.env meltano.yml transform/ schema/ --exclude=transform/target --exclude=transform/logs
	@echo "$(GREEN)Backup created in backups/$(NC)"

## Production Deployment

deploy-staging: ## Deploy to staging environment
	@echo "$(BLUE)Deploying to staging...$(NC)"
	@make env-staging
	@make test
	@make run
	@echo "$(GREEN)Staging deployment completed!$(NC)"

deploy-prod: ## Deploy to production environment
	@echo "$(BLUE)Deploying to production...$(NC)"
	@make env-prod
	@make test
	@make run
	@echo "$(GREEN)Production deployment completed!$(NC)"

## Scheduling (Airflow)

airflow-init: ## Initialize Airflow (if using Airflow)
	@echo "$(BLUE)Initializing Airflow...$(NC)"
	@. $(VENV_DIR)/bin/activate && \
		export AIRFLOW_HOME=$(PROJECT_DIR)/orchestrate && \
		airflow db init
	@echo "$(GREEN)Airflow initialized!$(NC)"

airflow-start: ## Start Airflow services
	@echo "$(BLUE)Starting Airflow services...$(NC)"
	@. $(VENV_DIR)/bin/activate && \
		export AIRFLOW_HOME=$(PROJECT_DIR)/orchestrate && \
		airflow webserver --port 8080 --daemon && \
		airflow scheduler --daemon
	@echo "$(GREEN)Airflow services started! Web UI: http://localhost:8080$(NC)"

airflow-stop: ## Stop Airflow services
	@echo "$(BLUE)Stopping Airflow services...$(NC)"
	@pkill -f "airflow webserver" || true
	@pkill -f "airflow scheduler" || true
	@echo "$(GREEN)Airflow services stopped!$(NC)"