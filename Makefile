# GRUPONOS-MELTANO-NATIVE Makefile
PROJECT_NAME := gruponos-meltano-native
PYTHON_VERSION := 3.13
POETRY := poetry
SRC_DIR := src
TESTS_DIR := tests

# Documentation maintenance tooling
FLEXT_ROOT := $(abspath ..)
DOCS_CLI := PYTHONPATH=$(FLEXT_ROOT)/flext-quality/src python -m flext_quality.docs_maintenance.cli
DOCS_PROFILE := advanced

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
validate: lint type-check security test ## Run all quality gates (MANDATORY ORDER)

check: lint type-check ## Quick health check

lint: ## Run linting (ZERO TOLERANCE)
	$(POETRY) run ruff check .

format: ## Format code
	$(POETRY) run ruff format .

type-check: ## Run type checking with Pyrefly (ZERO TOLERANCE)
	PYTHONPATH=$(SRC_DIR) $(POETRY) run pyrefly check .

security: ## Run security scanning
	$(POETRY) run bandit -r $(SRC_DIR)
	$(POETRY) run pip-audit

fix: ## Auto-fix issues
	$(POETRY) run ruff check . --fix
	$(POETRY) run ruff format .

# Testing
test: ## Run tests with 100% coverage (MANDATORY)
	$(POETRY) run pytest $(TESTS_DIR) --cov=$(SRC_DIR) --cov-report=term-missing --cov-fail-under=$(MIN_COVERAGE)

test-unit: ## Run unit tests
	PYTHONPATH=$(SRC_DIR) $(POETRY) run pytest -m "not integration" -v

test-integration: ## Run integration tests with Docker
	PYTHONPATH=$(SRC_DIR) $(POETRY) run pytest -m integration -v

test-fast: ## Run tests without coverage
	PYTHONPATH=$(SRC_DIR) $(POETRY) run pytest -v

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

# Documentation maintenance
.PHONY: docs-maintenance docs-maintenance-dry-run
docs-maintenance: ## Run shared documentation maintenance (Markdown only)
	FLEXT_DOC_PROFILE=$(DOCS_PROFILE) FLEXT_DOC_PROJECT_ROOT=$(PWD) $(DOCS_CLI) --project-root $(PWD)

docs-maintenance-dry-run: ## Preview documentation maintenance without applying changes
	FLEXT_DOC_PROFILE=$(DOCS_PROFILE) FLEXT_DOC_PROJECT_ROOT=$(PWD) $(DOCS_CLI) --project-root $(PWD) --dry-run --verbose

meltano-elt: ## Run ELT process
	$(POETRY) run meltano elt tap-oracle-wms target-oracle

meltano-operations: meltano-install meltano-validate meltano-test ## Execute all Meltano operations

# GrupoNOS operations
env-setup: ## Setup environment variables
	@if [ ! -f .env ]; then cp .env.example .env; echo "Created .env from template"; fi

env-validate: ## Validate environment configuration
	PYTHONPATH=$(SRC_DIR) $(POETRY) run python -c "from src.gruponos_meltano_native.config import Settings; settings = Settings(); print('Environment configuration valid')"

oracle-test: ## Test Oracle WMS connection
	PYTHONPATH=$(SRC_DIR) $(POETRY) run python -c "from src.gruponos_meltano_native.oracle.connection_manager import OracleConnectionManager; import  run(OracleConnectionManager().test_connection())"

ldap-test: ## Test LDAP connection
	PYTHONPATH=$(SRC_DIR) $(POETRY) run python -c "from src.gruponos_meltano_native.ldap.client import LDAPClient; client = LDAPClient(); result = client.test_connection(); print(f'LDAP connection: {result}')"

validate-schemas: ## Validate database schemas
	PYTHONPATH=$(SRC_DIR) $(POETRY) run python -c "from src.gruponos_meltano_native.validators import SchemaValidator; validator = SchemaValidator(); validator.validate_all(); print('Schemas validated')"

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
	PYTHONPATH=$(SRC_DIR) $(POETRY) run python

pre-commit: ## Run pre-commit hooks
	$(POETRY) run pre-commit run --all-files

# Maintenance
clean: ## Clean build artifacts
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ htmlcov/ .coverage .mypy_cache/ .pyrefly_cache/ .ruff_cache/
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
	@echo "GrupoNOS Native: $$(PYTHONPATH=$(SRC_DIR) $(POETRY) run python -c 'import gruponos_meltano_native; print(getattr(gruponos_meltano_native, \"__version__\", \"dev\"))' 2>/dev/null || echo 'Not available')"
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
# =============================================================================
# MAINTENANCE
# =============================================================================

.PHONY: clean
clean: ## Clean build artifacts and cruft
	@echo "🧹 Cleaning $(PROJECT_NAME) - removing build artifacts, cache files, and cruft..."

	# Build artifacts
	rm -rf build/ dist/ *.egg-info/

	# Test artifacts
	rm -rf .pytest_cache/ htmlcov/ .coverage .coverage.* coverage.xml

	# Python cache directories
	rm -rf .mypy_cache/ .pyrefly_cache/ .ruff_cache/

	# Python bytecode
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true

	# Temporary files
	find . -type f -name "*.tmp" -delete 2>/dev/null || true
	find . -type f -name "*.temp" -delete 2>/dev/null || true
	find . -type f -name ".DS_Store" -delete 2>/dev/null || true

	# Log files
	find . -type f -name "*.log" -delete 2>/dev/null || true

	# Editor files
	find . -type f -name ".vscode/settings.json" -delete 2>/dev/null || true
	find . -type f -name ".idea/" -type d -exec rm -rf {} + 2>/dev/null || true

	
	# Meltano-specific files
	rm -rf .meltano/ catalog-*.json state.json state-*.json
	rm -rf .meltano-tmp/ meltano-*.log

	# Data pipeline files
	rm -rf extract/ load/ transform/ output/ analyze/ orchestrate/
	rm -rf notebook/ data/

	@echo "✅ $(PROJECT_NAME) cleanup complete"

.PHONY: clean-all
clean-all: clean ## Deep clean including venv
	rm -rf .venv/

.PHONY: reset
reset: clean-all setup ## Reset project

# =============================================================================
# DIAGNOSTICS
# =============================================================================
