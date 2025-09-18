# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Hierarchy**: This document provides project-specific standards based on workspace-level patterns defined in [../CLAUDE.md](../CLAUDE.md). For architectural principles, quality gates, and MCP server usage, reference the main workspace standards.

## 🔗 MCP SERVER INTEGRATION

| MCP Server              | Purpose                                                     | Status     |
| ----------------------- | ----------------------------------------------------------- | ---------- |
| **serena**              | Meltano project codebase analysis and ETL pipeline patterns | **ACTIVE** |
| **sequential-thinking** | Meltano architecture and data integration problem solving   | **ACTIVE** |
| **github**              | Meltano ecosystem integration and pipeline PRs              | **ACTIVE** |

**Usage**: `claude mcp list` for available servers, leverage for Meltano-specific development patterns and ETL pipeline analysis.

## Project Overview

GrupoNOS Meltano Native is an enterprise-grade ETL pipeline implementation for Grupo Nos. This project provides specialized Oracle WMS (Warehouse Management System) integration using Meltano 3.8.0 as the orchestration platform, with Python 3.13 and strict type safety.

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
make setup                # Complete project setup including pre-commit hooks

# Quality gates (run before committing)
make validate             # Complete validation: lint + type + security + test
make check                # Quick check: lint + type + security
make test                 # Run all tests with 90% minimum coverage
make lint                 # Run ruff linting with maximum rigor
make type-check           # Run mypy strict type checking
make format               # Auto-format code with ruff
make fix                  # Auto-fix linting issues
make security             # Run bandit security scan and pip-audit

# Testing variations
make test-unit            # Unit tests only (fast feedback)
make test-integration     # Integration tests only
make test-fast            # Run tests without coverage (for development)
make coverage-html        # Generate HTML coverage reports
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

### Diagnostic and Maintenance Commands

```bash
# Project diagnostics and health
make diagnose             # Show Python/Poetry/Meltano versions and env info
make doctor               # Full health check (diagnose + check)

# Dependency management
make deps-update          # Update all dependencies
make deps-show            # Show dependency tree
make deps-audit           # Security audit of dependencies

# Environment and connection testing
make env-setup            # Setup environment variables from template
make env-validate         # Validate environment configuration
make oracle-test          # Test Oracle WMS connection
make ldap-test            # Test LDAP connection (if available)
make validate-schemas     # Validate database schemas

# Cleanup and maintenance
make clean                # Clean build artifacts
make clean-all            # Deep clean including virtual environment
make reset                # Reset project (clean-all + setup)
```

### CLI Usage

```bash
# Direct CLI access
poetry run python -m gruponos_meltano_native.cli --help
poetry run python -m gruponos_meltano_native.cli --dev

# Open Python shell with project context
make shell                # Start Python shell with dependencies loaded
```

## Testing Strategy

The project uses pytest with comprehensive testing requirements:

- **Minimum 90% test coverage** enforced via `--cov-fail-under=90` (corrected from documented 85% to actual pyproject.toml setting)
- **Test markers**: `unit`, `integration`, `slow`, `smoke`, `e2e`, `wms`, `oracle`, `performance`, `destructive`, `memory`
- **Strict configuration**: `--strict-markers`, `--strict-config`, `--maxfail=1`

### Running Specific Tests

```bash
# By marker
pytest -m unit                    # Unit tests only
pytest -m integration             # Integration tests only
pytest -m "not slow"              # Exclude slow tests
pytest -m "wms or oracle"         # WMS or Oracle tests

# Single test file or test function
pytest tests/unit/test_cli.py -v                                    # Single test file
pytest tests/unit/test_cli.py::test_cli_help -v                    # Single test function
pytest tests/integration/test_end_to_end_oracle_integration.py -xvs # Integration test with stop-on-fail

# Development testing patterns
pytest --lf                       # Run only last failed tests (fast debugging)
pytest -x --tb=short             # Stop on first failure with short traceback
pytest --collect-only            # Show available tests without running
pytest --cov=src/gruponos_meltano_native --cov-report=html         # Coverage with HTML report
```

### Make Command Aliases

The Makefile provides single-letter aliases for common commands:

```bash
# Quick aliases for common operations
make t        # test
make l        # lint
make f        # format
make tc       # type-check
make c        # clean
make i        # install
make v        # validate

# Meltano aliases
make mi       # meltano-install
make mt       # meltano-test
make mr       # meltano-run
make mv       # meltano-validate
make md       # meltano-discover
make me       # meltano-elt
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
# Oracle WMS REST API Configuration (Source)
TAP_ORACLE_WMS_BASE_URL=...           # WMS REST API endpoint
TAP_ORACLE_WMS_USERNAME=...           # API authentication username
TAP_ORACLE_WMS_PASSWORD=...           # API authentication password
TAP_ORACLE_WMS_COMPANY_CODE=...       # WMS company identifier
TAP_ORACLE_WMS_FACILITY_CODE=...      # WMS facility identifier

# Target Oracle Database Configuration
FLEXT_TARGET_ORACLE_HOST=...          # Oracle database host
FLEXT_TARGET_ORACLE_PORT=...          # Oracle database port (typically 1521 or 1522)
FLEXT_TARGET_ORACLE_SERVICE_NAME=...  # Oracle service name or SID
FLEXT_TARGET_ORACLE_USERNAME=...      # Database connection username
FLEXT_TARGET_ORACLE_PASSWORD=...      # Database connection password
FLEXT_TARGET_ORACLE_PROTOCOL=...      # Connection protocol (tcp or tcps)
FLEXT_TARGET_ORACLE_SCHEMA=...        # Default target schema name
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
- **Coverage**: Minimum 90% test coverage enforced

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

## Architecture Details

### Key Configuration Files

- **pyproject.toml**: Python 3.13 with strict type checking and comprehensive tool configuration
- **meltano.yml**: Two-pipeline architecture (full sync + incremental sync)
- **transform/dbt_project.yml**: DBT transformations with Oracle-specific optimizations
- **Makefile**: 40+ commands for development, testing, and operations

### FLEXT Framework Integration

This project depends on several FLEXT framework components managed as local path dependencies:

- **flext-core**: Foundation patterns, logging, result handling
- **flext-observability**: Monitoring and metrics
- **flext-db-oracle**: Oracle database connectivity
- **flext-tap-oracle-wms**: Oracle WMS data extraction
- **flext-target-oracle**: Oracle data loading
- **flext-ldap**: LDAP connectivity (development dependency)
- **flext-ldif**: LDIF processing (development dependency)

### Development Environment Requirements

- **Python 3.13 (exact version)**: Required for async/typing features
- **Poetry**: Dependency management with lock file integrity
- **Parent FLEXT workspace**: Local path dependencies must be available
- **Oracle connections**: WMS source and target database access
- **Environment variables**: All secrets externalized
