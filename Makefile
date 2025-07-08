# GRUPONOS-MELTANO-NATIVE Makefile - Enterprise Application
# ============================================================

.PHONY: help install test clean lint format build docs dev security type-check pre-commit

# Default target
help: ## Show this help message
	@echo "🏗️  FLEXT Gruponos Meltano Native - Enterprise Application"
	@echo "========================================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Installation & Setup
install: ## Install dependencies with Poetry
	@echo "📦 Installing dependencies for gruponos-meltano-native..."
	poetry install --all-extras

install-dev: ## Install with dev dependencies
	@echo "🛠️  Installing dev dependencies..."
	poetry install --all-extras --group dev --group test --group security

# Testing
test: ## Run tests
	@echo "🧪 Running tests for gruponos-meltano-native..."
	@if [ -d tests ]; then \
		python -m pytest tests/ -v; \
	else \
		echo "No tests directory found"; \
	fi

test-coverage: ## Run tests with coverage
	@echo "🧪 Running tests with coverage for gruponos-meltano-native..."
	@python -m pytest tests/ --cov=src --cov-report=html --cov-report=term

# Code Quality - Maximum Strictness
lint: ## Run all linters with maximum strictness
	@echo "🔍 Running maximum strictness linting for gruponos-meltano-native..."
	poetry run ruff check . --output-format=verbose
	@echo "✅ Ruff linting complete"

format: ## Format code with strict standards
	@echo "🎨 Formatting code with strict standards..."
	poetry run black .
	poetry run ruff check --fix .
	@echo "✅ Code formatting complete"

type-check: ## Run strict type checking
	@echo "🎯 Running strict MyPy type checking..."
	poetry run mypy src/gruponos_meltano_native --strict --show-error-codes
	@echo "✅ Type checking complete"

security: ## Run security analysis
	@echo "🔒 Running security analysis..."
	poetry run bandit -r src/ -f json -o reports/security.json || true
	poetry run bandit -r src/ -f txt
	@echo "✅ Security analysis complete"

pre-commit: ## Run pre-commit hooks
	@echo "🎣 Running pre-commit hooks..."
	poetry run pre-commit run --all-files
	@echo "✅ Pre-commit checks complete"

check: lint type-check security test ## Run all quality checks
	@echo "✅ All quality checks complete for gruponos-meltano-native!"

# Build & Distribution
build: ## Build the package with Poetry
	@echo "🔨 Building gruponos-meltano-native package..."
	poetry build
	@echo "📦 Package built successfully"

build-clean: clean build ## Clean then build
	@echo "🔄 Clean build for gruponos-meltano-native..."

publish-test: build ## Publish to TestPyPI
	@echo "🚀 Publishing to TestPyPI..."
	poetry publish --repository testpypi

publish: build ## Publish to PyPI
	@echo "🚀 Publishing gruponos-meltano-native to PyPI..."
	poetry publish

# Documentation
docs: ## Generate documentation
	@echo "📚 Generating documentation for gruponos-meltano-native..."
	@if [ -f docs/conf.py ]; then \
		cd docs && make html; \
	else \
		echo "No docs configuration found"; \
	fi

# Cleanup
clean: ## Clean build artifacts
	@echo "🧹 Cleaning build artifacts for gruponos-meltano-native..."
	@rm -rf build/ dist/ *.egg-info/
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true
	@find . -name "*.pyo" -delete 2>/dev/null || true

# Development Workflow
dev-setup: install-dev ## Complete development setup
	@echo "🎯 Setting up development environment for gruponos-meltano-native..."
	poetry run pre-commit install
	mkdir -p reports
	@echo "✅ Development setup complete!"

dev: ## Run in development mode
	@echo "🔧 Starting gruponos-meltano-native in development mode..."
	PYTHONPATH=src poetry run python -m gruponos_meltano_native --debug

dev-test: ## Quick development test cycle
	@echo "⚡ Quick test cycle for development..."
	poetry run pytest tests/ -v --tb=short

# Environment variables
export PYTHONPATH := $(PWD)/src:$(PYTHONPATH)
export GRUPONOS_MELTANO_NATIVE_DEV := true
