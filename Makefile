# GRUPONOS-MELTANO-NATIVE Makefile
PROJECT_NAME := gruponos-meltano-native
PYTHON_VERSION := 3.13
POETRY := poetry
SRC_DIR := src
TESTS_DIR := tests

# Quality standards
MIN_COVERAGE := 85

# Help
help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\\033[36m%-20s\\033[0m %s\\n", $$1, $$2}'

# Installation
install: ## Install dependencies
	$(POETRY) install

install-dev: ## Install dev dependencies
	$(POETRY) install --with dev,test,docs

setup: install-dev ## Complete project setup
	$(POETRY) run pre-commit install

# Quality gates
validate: lint type-check security test ## Run all quality gates

check: lint type-check ## Quick health check

lint: ## Run linting
	$(POETRY) run ruff check $(SRC_DIR) $(TESTS_DIR)

format: ## Format code
	$(POETRY) run ruff format $(SRC_DIR) $(TESTS_DIR)

type-check: ## Run type checking
	$(POETRY) run mypy $(SRC_DIR) --strict

security: ## Run security scanning
	$(POETRY) run bandit -r $(SRC_DIR)
	$(POETRY) run pip-audit

fix: ## Auto-fix issues
	$(POETRY) run ruff check $(SRC_DIR) $(TESTS_DIR) --fix
	$(POETRY) run ruff format $(SRC_DIR) $(TESTS_DIR)

# Testing
test: ## Run tests with coverage
	$(POETRY) run pytest $(TESTS_DIR) --cov=$(SRC_DIR) --cov-report=term-missing --cov-fail-under=$(MIN_COVERAGE)

test-unit: ## Run unit tests
	$(POETRY) run pytest $(TESTS_DIR) -m "not integration" -v

test-integration: ## Run integration tests
	$(POETRY) run pytest $(TESTS_DIR) -m integration -v

test-fast: ## Run tests without coverage
	$(POETRY) run pytest $(TESTS_DIR) -v

coverage-html: ## Generate HTML coverage report
	$(POETRY) run pytest $(TESTS_DIR) --cov=$(SRC_DIR) --cov-report=html

# Meltano operations
meltano-install: ## Install Meltano plugins
	$(POETRY) run meltano install

meltano-test: ## Test Meltano plugin connections
	$(POETRY) run meltano test tap-oracle-wms || echo "Tap test failed"
	$(POETRY) run meltano test tap-ldap || echo "LDAP test failed"

meltano-run: ## Execute full Meltano pipeline
	$(POETRY) run meltano run tap-oracle-wms-full target-oracle-full

meltano-validate: ## Validate Meltano configuration
	$(POETRY) run meltano config list
	$(POETRY) run meltano invoke dbt-postgres deps || echo "DBT deps failed"

meltano-discover: ## Discover schemas from taps
	$(POETRY) run meltano discover tap-oracle-wms
	$(POETRY) run meltano discover tap-ldap

meltano-elt: ## Run ELT process
	$(POETRY) run meltano elt tap-oracle-wms target-oracle

meltano-operations: meltano-install meltano-validate meltano-test ## Execute all Meltano operations

# GrupoNOS operations
env-setup: ## Setup environment variables
	@if [ ! -f .env ]; then cp .env.example .env; echo "Created .env from template"; fi

env-validate: ## Validate environment configuration
	$(POETRY) run python -c "from src.gruponos_meltano_native.config import Settings; settings = Settings(); print('Environment configuration valid')"

oracle-test: ## Test Oracle WMS connection
	$(POETRY) run python -c "from src.gruponos_meltano_native.oracle.connection_manager import OracleConnectionManager; import asyncio; asyncio.run(OracleConnectionManager().test_connection())"

ldap-test: ## Test LDAP connection
	$(POETRY) run python -c "from src.gruponos_meltano_native.ldap.client import LDAPClient; client = LDAPClient(); result = client.test_connection(); print(f'LDAP connection: {result}')"

validate-schemas: ## Validate database schemas
	$(POETRY) run python -c "from src.gruponos_meltano_native.validators import SchemaValidator; validator = SchemaValidator(); validator.validate_all(); print('Schemas validated')"

enterprise-validate: env-validate oracle-test ldap-test validate-schemas ## Validate all enterprise operations

# Build
build: ## Build package
	$(POETRY) build

build-clean: clean build ## Clean and build

# Documentation
docs: ## Build documentation
	$(POETRY) run mkdocs build

docs-serve: ## Serve documentation
	$(POETRY) run mkdocs serve

# Dependencies
deps-update: ## Update dependencies
	$(POETRY) update

deps-show: ## Show dependency tree
	$(POETRY) show --tree

deps-audit: ## Audit dependencies
	$(POETRY) run pip-audit

# Development
shell: ## Open Python shell
	$(POETRY) run python

pre-commit: ## Run pre-commit hooks
	$(POETRY) run pre-commit run --all-files

# Maintenance
clean: ## Clean build artifacts
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ htmlcov/ .coverage .mypy_cache/ .ruff_cache/
	rm -rf .meltano/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

clean-all: clean ## Deep clean including venv
	rm -rf .venv/

reset: clean-all setup ## Reset project

# Diagnostics
diagnose: ## Project diagnostics
	@echo "Python: $$(python --version)"
	@echo "Poetry: $$($(POETRY) --version)"
	@echo "Meltano: $$($(POETRY) run meltano --version 2>/dev/null || echo 'Not available')"
	@echo "GrupoNOS Native: $$($(POETRY) run python -c 'import gruponos_meltano_native; print(getattr(gruponos_meltano_native, \"__version__\", \"dev\"))' 2>/dev/null || echo 'Not available')"
	@$(POETRY) env info

doctor: diagnose check ## Health check

# Aliases
t: test
l: lint
f: format
tc: type-check
c: clean
i: install
v: validate
mi: meltano-install
mt: meltano-test
mr: meltano-run
mv: meltano-validate
md: meltano-discover
me: meltano-elt
mo: meltano-operations
es: env-setup
ev: env-validate
ot: oracle-test
lt: ldap-test
vs: validate-schemas
evald: enterprise-validate

.DEFAULT_GOAL := help
.PHONY: help install install-dev setup validate check lint format type-check security fix test test-unit test-integration test-fast coverage-html meltano-install meltano-test meltano-run meltano-validate meltano-discover meltano-elt meltano-operations env-setup env-validate oracle-test ldap-test validate-schemas enterprise-validate build build-clean docs docs-serve deps-update deps-show deps-audit shell pre-commit clean clean-all reset diagnose doctor t l f tc c i v mi mt mr mv md me mo es ev ot lt vs evald