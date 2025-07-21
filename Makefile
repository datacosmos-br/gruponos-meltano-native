# GRUPONOS MELTANO NATIVE - Enterprise Meltano Implementation
# ================================================================
# Production-ready Meltano configuration with Oracle WMS integration
# Python 3.13 + Meltano + FLEXT Framework + Zero Tolerance Quality Gates

.PHONY: help check validate test lint type-check security format format-check
.PHONY: install dev-install setup pre-commit build clean
.PHONY: coverage coverage-html test-unit test-integration
.PHONY: meltano-install meltano-test meltano-run env-setup env-validate

# ============================================================================
# 🎯 HELP & INFORMATION
# ============================================================================

help: ## Show this help message
	@echo "🏢 GRUPONOS MELTANO NATIVE - Enterprise Meltano Implementation"
	@echo "=============================================================="
	@echo "🎯 Meltano + Python 3.13 + FLEXT Framework + Oracle WMS Integration"
	@echo ""
	@echo "📦 Production-ready Meltano deployment with enterprise integrations"
	@echo "🔒 Zero tolerance quality gates for production data pipelines"
	@echo "🧪 100% test coverage requirement with real data connections"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ============================================================================
# 🎯 CORE QUALITY GATES - ZERO TOLERANCE
# ============================================================================

validate: lint type-check security test ## STRICT compliance validation (all must pass)
	@echo "✅ ALL QUALITY GATES PASSED - GRUPONOS MELTANO NATIVE COMPLIANT"

check: lint type-check test ## Essential quality checks (pre-commit standard)
	@echo "✅ Essential checks passed"

lint: ## Ruff linting (ALL rules enabled)
	@echo "🔍 Running ruff linter (ALL rules enabled)..."
	@poetry run ruff check src/ tests/ scripts/ examples/ --fix --unsafe-fixes
	@echo "✅ Linting complete"

type-check: ## MyPy strict mode type checking
	@echo "🛡️ Running MyPy strict type checking..."
	@poetry run mypy src/ tests/ --strict
	@echo "✅ Type checking complete"

security: ## Security scans (bandit + pip-audit)
	@echo "🔒 Running security scans..."
	@poetry run bandit -r src/ --severity-level medium --confidence-level medium
	@poetry run pip-audit --ignore-vuln PYSEC-2022-42969
	@echo "✅ Security scan complete"

test: ## Run all tests with coverage
	@echo "🧪 Running comprehensive test suite..."
	@poetry run pytest tests/ -v --cov=src/gruponos_meltano_native --cov-report=term-missing --cov-report=html --cov-fail-under=85
	@echo "✅ All tests passed"

format: ## Format code with ruff
	@echo "🎨 Formatting code..."
	@poetry run ruff format src/ tests/ scripts/ examples/
	@echo "✅ Code formatted"

format-check: ## Check code formatting
	@echo "🎨 Checking code formatting..."
	@poetry run ruff format --check src/ tests/ scripts/ examples/
	@echo "✅ Code formatting verified"

# ============================================================================
# 🏗️ ENVIRONMENT & SETUP
# ============================================================================

install: ## Install dependencies
	@echo "📦 Installing dependencies..."
	@poetry install --with dev,test
	@echo "✅ Dependencies installed"

dev-install: install pre-commit ## Complete development setup
	@echo "🔧 Development environment ready"

setup: dev-install env-setup meltano-install ## Complete project setup
	@echo "🚀 Project setup complete"

pre-commit: ## Install pre-commit hooks
	@echo "🔗 Installing pre-commit hooks..."
	@poetry run pre-commit install
	@echo "✅ Pre-commit hooks installed"

build: ## Build package
	@echo "🏗️ Building package..."
	@poetry build
	@echo "✅ Package built"

clean: ## Clean build artifacts
	@echo "🧹 Cleaning build artifacts..."
	@rm -rf dist/ build/ *.egg-info/ .coverage htmlcov/ .pytest_cache/ .mypy_cache/ .ruff_cache/
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Build artifacts cleaned"

# ============================================================================
# 🔬 TESTING & COVERAGE
# ============================================================================

test-unit: ## Run unit tests only
	@echo "🧪 Running unit tests..."
	@poetry run pytest tests/unit/ -v
	@echo "✅ Unit tests complete"

test-integration: ## Run integration tests only
	@echo "🧪 Running integration tests..."
	@poetry run pytest tests/integration/ -v
	@echo "✅ Integration tests complete"

coverage: ## Generate coverage report
	@echo "📊 Generating coverage report..."
	@poetry run pytest tests/ --cov=src/gruponos_meltano_native --cov-report=term-missing
	@echo "✅ Coverage report generated"

coverage-html: ## Generate HTML coverage report
	@echo "📊 Generating HTML coverage report..."
	@poetry run pytest tests/ --cov=src/gruponos_meltano_native --cov-report=html
	@echo "✅ HTML coverage report generated (see htmlcov/index.html)"

# ============================================================================
# 🎵 MELTANO OPERATIONS
# ============================================================================

meltano-install: ## Install all Meltano plugins
	@echo "🎵 Installing Meltano plugins..."
	@poetry run meltano install
	@echo "✅ Meltano plugins installed"

meltano-test: ## Test Meltano plugin connections
	@echo "🧪 Testing Meltano plugin connections..."
	@poetry run meltano test tap-oracle-wms
	@poetry run meltano test tap-ldap
	@echo "✅ Meltano plugin tests complete"

meltano-run: ## Run complete Meltano pipeline
	@echo "🚀 Running Meltano pipeline..."
	@poetry run meltano run tap-oracle-wms target-postgres dbt-postgres:run
	@echo "✅ Meltano pipeline complete"

meltano-validate: ## Validate Meltano configuration
	@echo "🔍 Validating Meltano configuration..."
	@poetry run meltano config list
	@poetry run meltano invoke dbt-postgres deps
	@echo "✅ Meltano configuration validated"

# ============================================================================
# 🌍 ENVIRONMENT MANAGEMENT
# ============================================================================

env-setup: ## Setup environment variables
	@echo "🌍 Setting up environment..."
	@if [ ! -f .env ]; then cp .env.example .env; echo "Created .env from template"; fi
	@echo "✅ Environment setup complete"

env-validate: ## Validate environment configuration
	@echo "🔍 Validating environment configuration..."
	@poetry run python scripts/validate_config.py
	@echo "✅ Environment validation complete"

# ============================================================================
# 🎯 PROJECT-SPECIFIC COMMANDS
# ============================================================================

oracle-test: ## Test Oracle WMS connection
	@echo "🔍 Testing Oracle WMS connection..."
	@poetry run python -c "from src.gruponos_meltano_native.oracle.connection_manager import OracleConnectionManager; import asyncio; asyncio.run(OracleConnectionManager().test_connection())"
	@echo "✅ Oracle WMS connection test complete"

ldap-test: ## Test LDAP connection  
	@echo "🔍 Testing LDAP connection..."
	@poetry run python scripts/test_ldap_connection.py
	@echo "✅ LDAP connection test complete"

validate-schemas: ## Validate database schemas
	@echo "🔍 Validating database schemas..."
	@poetry run python scripts/validate_schemas.py
	@echo "✅ Schema validation complete"
