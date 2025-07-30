# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GrupoNOS Meltano Native is an enterprise-grade ETL pipeline implementation for Grupo Nos, built on the FLEXT framework ecosystem. This project provides specialized Oracle WMS (Warehouse Management System) integration using Meltano 3.8.0 as the orchestration platform, with Python 3.13 and strict type safety.

## Key Technologies

- **Python 3.13**: Core language with strict typing and async support
- **Meltano 3.8.0**: Data integration and orchestration platform
- **FLEXT Framework**: Enterprise patterns with Clean Architecture and DDD
- **Oracle WMS**: Primary data source via REST API integration
- **Poetry**: Dependency management and packaging
- **pytest**: Testing framework with comprehensive coverage requirements

## Architecture Overview

This project follows FLEXT standards with Clean Architecture principles:

- **src/gruponos_meltano_native/**: Main application code
  - `cli.py`: Command-line interface with Click framework
  - `config.py`: Configuration management with Pydantic models
  - `orchestrator.py`: Meltano pipeline orchestration
  - `exceptions.py`: Domain-specific exception handling
- **infrastructure/**: External system integrations
  - `di_container.py`: Dependency injection container
- **oracle/**: Oracle WMS connection management
- **validators/**: Data validation components
- **monitoring/**: Alert management and observability

## Development Commands

### Essential Commands

```bash
# Setup and installation
make install-dev          # Install all dependencies including dev tools
make dev-setup            # Complete development environment setup

# Quality gates (run before committing)
make validate             # Complete validation: lint + type + security + test
make check                # Quick check: lint + type + security
make test                 # Run all tests with 85% minimum coverage
make lint                 # Run ruff linting with maximum rigor
make type-check           # Run mypy strict type checking
make format               # Auto-format code with ruff

# Testing variations
make test-unit            # Unit tests only (fast feedback)
make test-integration     # Integration tests only
make test-coverage        # Generate HTML coverage reports
```

### Meltano Operations

```bash
# Meltano pipeline management
make meltano-install      # Install all Meltano plugins
make meltano-validate     # Validate Meltano configuration
make meltano-test         # Test plugin connections
make meltano-run          # Execute full pipeline
make meltano-discover     # Discover schemas from taps
make meltano-elt          # Run ELT process

# Environment operations
make env-setup            # Setup environment variables
make oracle-test          # Test Oracle WMS connection
make enterprise-validate  # Validate all enterprise operations
```

### CLI Usage

```bash
# Direct CLI access
poetry run python -m gruponos_meltano_native.cli --help
poetry run python -m gruponos_meltano_native.cli --dev

# Via Make shortcuts
make dev                  # Run in development mode
make dev-test             # Quick development test cycle
```

## Testing Strategy

The project uses pytest with comprehensive testing requirements:

- **Minimum 85% test coverage** enforced via `--cov-fail-under=85`
- **Test markers**: `unit`, `integration`, `slow`, `smoke`, `e2e`, `wms`, `oracle`, `performance`, `destructive`, `memory`
- **Strict configuration**: `--strict-markers`, `--strict-config`, `--maxfail=1`

### Running Specific Tests

```bash
# By marker
pytest -m unit                    # Unit tests only
pytest -m integration             # Integration tests only
pytest -m "not slow"              # Exclude slow tests
pytest -m "wms or oracle"         # WMS or Oracle tests

# Specific test files
pytest tests/unit/test_cli.py -v
pytest tests/integration/ -xvs

# With coverage
pytest --cov=src/gruponos_meltano_native --cov-report=html
```

## Configuration Management

The project uses layered configuration with Pydantic models:

- **Environment Variables**: All secrets and environment-specific settings
- **config/**: YAML configuration files
  - `project.yml`: Project-level settings
  - `wms_integration.yml`: Oracle WMS specific configuration
  - `environments/`: Per-environment configuration (dev.yml, prod.yml)
- **meltano.yml**: Meltano pipeline configuration with extractors and loaders

### Key Environment Variables

```bash
# Oracle WMS Configuration
TAP_ORACLE_WMS_BASE_URL=...
TAP_ORACLE_WMS_USERNAME=...
TAP_ORACLE_WMS_PASSWORD=...
TAP_ORACLE_WMS_COMPANY_CODE=...
TAP_ORACLE_WMS_FACILITY_CODE=...

# Target Oracle Database
FLEXT_TARGET_ORACLE_HOST=...
FLEXT_TARGET_ORACLE_SERVICE_NAME=...
FLEXT_TARGET_ORACLE_USERNAME=...
FLEXT_TARGET_ORACLE_PASSWORD=...
```

## Meltano Pipeline Architecture

The project defines two main job patterns:

1. **Full Sync Job** (`tap-oracle-wms-full` → `target-oracle-full`)

   - Complete data extraction for all entities
   - Scheduled weekly via `@weekly` cron
   - Uses append-only load method

2. **Incremental Sync Job** (`tap-oracle-wms-incremental` → `target-oracle-incremental`)
   - Incremental updates using `mod_ts` replication key
   - Scheduled every 2 hours via `0 */2 * * *` cron
   - Uses upsert load method

### Data Entities

- **allocation**: Warehouse allocation data
- **order_hdr**: Order headers
- **order_dtl**: Order details

## Quality Standards

### Code Quality Requirements

- **Ruff**: Maximum rigor with `ALL` rules enabled, specific ignores for practical development
- **MyPy**: Strict mode with comprehensive type checking
- **Bandit**: Security analysis for vulnerability detection
- **Coverage**: Minimum 85% test coverage enforced

### Pre-commit Hooks

```bash
make pre-commit              # Run all pre-commit hooks
poetry run pre-commit install  # Install hooks for automatic execution
```

## DBT Integration

The project includes dbt models for data transformation:

- **staging/**: Raw data cleaning and initial transformations
  - `stg_wms_allocation.sql`, `stg_wms_orders.sql`, etc.
- **intermediate/**: Business logic transformations
  - `int_allocation_performance.sql`
- **marts/**: Final business-ready models
  - `core/dim_items.sql`
  - `inventory/fact_inventory_movement.sql`
  - `warehouse/fact_allocation_performance.sql`

## Troubleshooting

### Common Issues

**Environment Setup:**

```bash
make diagnose                # Full system diagnostics
make info                    # Project information
make workspace-validate      # Validate workspace compliance
```

**Dependency Issues:**

```bash
make clean && make install-dev  # Clean reinstall
poetry env remove --all         # Remove virtual environment
poetry install --all-extras     # Fresh installation
```

**Meltano Plugin Issues:**

```bash
make meltano-validate           # Check configuration
meltano config list             # List all configurations
meltano install --force         # Force reinstall plugins
```

**Testing Issues:**

```bash
pytest --lf                     # Run only last failed tests
pytest -x --tb=short           # Stop on first failure with short traceback
pytest --collect-only          # Show available tests without running
```

## Development Workflow

1. **Setup**: `make dev-setup` for complete environment
2. **Development**: Use `make dev-test` for quick feedback cycle
3. **Quality Check**: `make check` before committing changes
4. **Full Validation**: `make validate` before pull requests
5. **Testing**: Focus on unit tests (`make test-unit`) for speed, integration tests for completeness

## Integration with FLEXT Ecosystem

This project depends on several FLEXT framework components:

- **flext-core**: Foundation patterns, logging, result handling
- **flext-observability**: Monitoring and metrics
- **flext-db-oracle**: Oracle database connectivity
- **flext-tap-oracle-wms**: Oracle WMS data extraction
- **flext-target-oracle**: Oracle data loading

These are managed as local path dependencies and should be available in the parent FLEXT workspace.
