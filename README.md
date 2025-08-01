# GrupoNOS Meltano Native - Enterprise ETL Pipeline

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Meltano 3.8.0](https://img.shields.io/badge/Meltano-3.8.0-blue.svg)](https://meltano.com)
[![Oracle WMS](https://img.shields.io/badge/Oracle-WMS-red.svg)](https://www.oracle.com/applications/supply-chain-management/warehouse-management/)
[![Clean Architecture](https://img.shields.io/badge/Architecture-Clean%20Architecture%20%2B%20DDD-green.svg)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
[![Coverage](https://img.shields.io/badge/coverage-85%25+-brightgreen.svg)](https://pytest.org)

Enterprise-grade ETL pipeline implementation for Grupo Nos, built on the FLEXT framework ecosystem. Provides specialized Oracle WMS (Warehouse Management System) integration using Meltano 3.8.0 as the orchestration platform with Clean Architecture principles.

## Overview

GrupoNOS Meltano Native delivers a comprehensive ETL solution specifically designed for Grupo Nos' Oracle WMS environment. The platform provides automated data extraction, transformation, and loading with enterprise-grade monitoring, scheduling, and data quality validation.

### Key Features

- **Enterprise Oracle WMS Integration**: Specialized Oracle Warehouse Management System connectivity
- **Meltano 3.8.0 Orchestration**: Modern data integration platform with Singer ecosystem
- **Automated Scheduling**: Full sync weekly, incremental sync every 2 hours
- **Data Quality Validation**: Comprehensive data validation and quality checks
- **Clean Architecture**: Domain-driven design with strict layer separation
- **Real-time Monitoring**: Enterprise observability with alerting and metrics
- **Production Ready**: 85% test coverage with comprehensive integration testing

## Quick Start

### Prerequisites

- **Python 3.13+** installed
- **Oracle WMS** access credentials
- **Oracle Database** target connection
- **Poetry** for dependency management

### Installation

```bash
# Clone and setup
git clone <repository-url>
cd gruponos-meltano-native

# Install dependencies
poetry install

# Setup development environment
make dev-setup

# Configure environment variables
cp .env.example .env
# Edit .env with your Oracle WMS and database credentials
```

### First Pipeline Run

```bash
# Install Meltano plugins
make meltano-install

# Validate configuration
make meltano-validate

# Test connections
make oracle-test

# Execute full pipeline
make meltano-run
```

## Architecture

### FLEXT Framework Integration

The project leverages the FLEXT ecosystem for enterprise reliability:

- **flext-core**: Foundation patterns, FlextResult, logging, dependency injection
- **flext-observability**: Monitoring, metrics, and distributed tracing
- **flext-db-oracle**: Oracle database connectivity and operations
- **flext-tap-oracle-wms**: Oracle WMS data extraction capabilities
- **flext-target-oracle**: Oracle database loading and upsert operations

### Project Structure

```
src/gruponos_meltano_native/
   cli.py                   # Command-line interface with Click framework
   config.py                # Configuration management with Pydantic models
   orchestrator.py          # Meltano pipeline orchestration
   exceptions.py            # Domain-specific exception handling
   infrastructure/          # External system integrations
      di_container.py      # Dependency injection container
   oracle/                  # Oracle WMS connection management
   validators/              # Data validation components
   monitoring/              # Alert management and observability
```

### Meltano Pipeline Architecture

#### Pipeline Jobs

1. **Full Sync Job** (`tap-oracle-wms-full` ' `target-oracle-full`)

   - Complete data extraction for all entities
   - Scheduled weekly via `@weekly` cron
   - Uses append-only load method for historical data

2. **Incremental Sync Job** (`tap-oracle-wms-incremental` ' `target-oracle-incremental`)
   - Incremental updates using `mod_ts` replication key
   - Scheduled every 2 hours via `0 */2 * * *` cron
   - Uses upsert load method for real-time updates

#### Data Entities

- **allocation**: Warehouse allocation and pick data
- **order_hdr**: Order headers with customer information
- **order_dtl**: Order line items and product details
- **inventory**: Real-time inventory positions
- **item_master**: Product master data
- **location**: Warehouse location management

## Development Commands

### Quality Gates (Zero Tolerance)

```bash
# Complete validation pipeline (run before commits)
make validate                # lint + type + security + test + meltano-test

# Essential checks
make check                   # lint + type + security + oracle-test

# Individual quality gates
make lint                    # Ruff linting (ALL rules enabled)
make type-check              # MyPy strict mode
make security                # Bandit + pip-audit + detect-secrets
make format                  # Format code with Ruff
```

### Meltano Operations

```bash
# Core Meltano workflow
make meltano-install         # Install all Meltano plugins
make meltano-validate        # Validate Meltano configuration
make meltano-test            # Test plugin connections
make meltano-run             # Execute full pipeline
make meltano-discover        # Discover schemas from taps
make meltano-elt             # Run ELT process

# GrupoNOS-specific operations
make gruponos-full-sync      # Execute complete data synchronization
make gruponos-incremental    # Run incremental updates
make gruponos-validate-data  # Validate data quality and integrity
make gruponos-monitoring     # Check monitoring and alerting status
```

### Testing

```bash
# Complete test suite
make test                    # All tests with 85% coverage requirement
make test-unit               # Unit tests only
make test-integration        # Integration tests with Oracle WMS
make coverage-html           # Generate HTML coverage report

# Test categories
pytest -m unit               # Unit tests
pytest -m integration        # Integration tests
pytest -m wms                # WMS-specific tests
pytest -m oracle             # Oracle database tests
pytest -m performance        # Performance tests
pytest -m "not slow"         # Exclude slow tests for fast feedback
```

### Setup and Installation

```bash
# Complete development setup
make dev-setup               # Install tools, dependencies, and pre-commit hooks
make install                 # Install dependencies with Poetry
make install-dev             # Development environment setup
make pre-commit              # Setup pre-commit hooks
```

## Configuration

### Oracle WMS Connection

Configure Oracle WMS connection via environment variables:

```bash
# Oracle WMS Configuration
export TAP_ORACLE_WMS_BASE_URL="https://wms.gruponos.com/api/v1"
export TAP_ORACLE_WMS_USERNAME="gruponos_etl_user"
export TAP_ORACLE_WMS_PASSWORD="secure_password"
export TAP_ORACLE_WMS_COMPANY_CODE="GNOS"
export TAP_ORACLE_WMS_FACILITY_CODE="DC01"
export TAP_ORACLE_WMS_TIMEOUT="300"
export TAP_ORACLE_WMS_BATCH_SIZE="10000"

# Target Oracle Database
export FLEXT_TARGET_ORACLE_HOST="oracle-dw.gruponos.com"
export FLEXT_TARGET_ORACLE_PORT="1521"
export FLEXT_TARGET_ORACLE_SERVICE_NAME="GNOSDW"
export FLEXT_TARGET_ORACLE_USERNAME="gruponos_etl"
export FLEXT_TARGET_ORACLE_PASSWORD="secure_password"
export FLEXT_TARGET_ORACLE_SCHEMA="WMS_STAGE"
```

### Meltano Configuration

The `meltano.yml` file defines the complete pipeline configuration:

```yaml
version: 1
default_environment: dev
project_id: gruponos-meltano-native

environments:
  - name: dev
    config:
      plugins:
        extractors:
          - name: tap-oracle-wms
            config:
              base_url: ${TAP_ORACLE_WMS_BASE_URL}
              username: ${TAP_ORACLE_WMS_USERNAME}
              password: ${TAP_ORACLE_WMS_PASSWORD}
              company_code: ${TAP_ORACLE_WMS_COMPANY_CODE}
              facility_code: ${TAP_ORACLE_WMS_FACILITY_CODE}
        loaders:
          - name: target-oracle
            config:
              host: ${FLEXT_TARGET_ORACLE_HOST}
              port: ${FLEXT_TARGET_ORACLE_PORT}
              service_name: ${FLEXT_TARGET_ORACLE_SERVICE_NAME}
              username: ${FLEXT_TARGET_ORACLE_USERNAME}
              password: ${FLEXT_TARGET_ORACLE_PASSWORD}
              default_target_schema: ${FLEXT_TARGET_ORACLE_SCHEMA}

jobs:
  - name: gruponos-full-sync
    tasks:
      - tap-oracle-wms-full target-oracle-full
    schedule:
      interval: "@weekly"

  - name: gruponos-incremental-sync
    tasks:
      - tap-oracle-wms-incremental target-oracle-incremental
    schedule:
      interval: "0 */2 * * *"
```

### dbt Integration

Data transformation models in the `dbt/` directory:

#### Staging Models

```sql
-- models/staging/stg_wms_allocation.sql
-- Oracle WMS allocation data standardization
{{ config(materialized='view') }}

SELECT
    allocation_id,
    company_code,
    facility_code,
    order_dtl_id,
    item_code,
    location,
    allocated_quantity,
    packed_quantity,
    allocation_status,
    created_timestamp,
    modified_timestamp,
    {{ generate_surrogate_key(['allocation_id', 'company_code']) }} as allocation_key
FROM {{ source('oracle_wms_raw', 'allocation') }}
WHERE allocation_id IS NOT NULL
```

#### Mart Models

```sql
-- models/marts/warehouse/fact_allocation_performance.sql
-- Allocation performance analytics
{{ config(
    materialized='table',
    indexes=[
        {'columns': ['facility_code', 'business_date']},
        {'columns': ['allocation_key']}
    ]
) }}

WITH allocation_metrics AS (
    SELECT
        facility_code,
        business_date,
        COUNT(*) as total_allocations,
        SUM(allocated_quantity) as total_allocated_qty,
        SUM(packed_quantity) as total_packed_qty,
        AVG(DATEDIFF('second', created_timestamp, packed_timestamp)) as avg_processing_time_seconds
    FROM {{ ref('stg_wms_allocation') }}
    WHERE allocation_status = 'COMPLETED'
    GROUP BY facility_code, business_date
)

SELECT
    facility_code,
    business_date,
    total_allocations,
    total_allocated_qty,
    total_packed_qty,
    ROUND(total_packed_qty::DECIMAL / total_allocated_qty * 100, 2) as fulfillment_rate_pct,
    avg_processing_time_seconds,
    current_timestamp as dbt_updated_at
FROM allocation_metrics
```

## Monitoring and Observability

### Enterprise Monitoring

The platform includes comprehensive monitoring capabilities:

```python
# src/gruponos_meltano_native/monitoring/alerts.py
from flext_observability import get_metrics_client, create_alert

class GrupoNOSMonitoring:
    def __init__(self):
        self.metrics = get_metrics_client()

    async def monitor_pipeline_health(self):
        """Monitor pipeline execution health"""
        pipeline_status = await self.check_pipeline_status()

        # Track pipeline metrics
        self.metrics.counter('pipeline.executions.total').inc()
        self.metrics.gauge('pipeline.last_run_duration_seconds').set(
            pipeline_status.duration_seconds
        )

        # Create alerts for failures
        if pipeline_status.failed:
            await create_alert(
                title="GrupoNOS Pipeline Failure",
                message=f"Pipeline failed: {pipeline_status.error}",
                severity="critical"
            )
```

### Performance Metrics

- **Pipeline Execution Time**: Track ELT execution duration
- **Data Volume Metrics**: Monitor extracted/loaded record counts
- **Error Rates**: Track failure rates and error patterns
- **Data Quality Scores**: Monitor data validation results
- **Resource Utilization**: Track CPU, memory, and network usage

## CLI Usage

### Command-Line Interface

```bash
# Main CLI operations
poetry run python -m gruponos_meltano_native.cli --help

# Development mode
poetry run python -m gruponos_meltano_native.cli --dev

# Execute specific operations
poetry run python -m gruponos_meltano_native.cli run --job gruponos-full-sync
poetry run python -m gruponos_meltano_native.cli validate --environment prod
poetry run python -m gruponos_meltano_native.cli diagnose --include-oracle-health
```

### Programmatic Usage

```python
from gruponos_meltano_native import GrupoNOSOrchestrator
from pathlib import Path

# Initialize orchestrator
orchestrator = GrupoNOSOrchestrator(
    config_path=Path("config/prod.yml"),
    meltano_dir=Path(".")
)

# Execute full synchronization
result = await orchestrator.execute_full_sync(
    company_code="GNOS",
    facility_code="DC01",
    enable_monitoring=True
)

if result.is_success():
    print(f"Sync completed: {result.value.summary}")
else:
    print(f"Sync failed: {result.error}")
```

## Testing Strategy

### Test Architecture

```
tests/
- unit/                    # Fast unit tests with mocks
   --- test_cli.py          # CLI component tests
   --- test_orchestrator.py # Orchestration logic tests
   --- test_config.py       # Configuration tests
- integration/             # Tests with real Oracle WMS/DB
   --- test_oracle_wms_integration.py
   --- test_meltano_pipeline.py
- e2e/                     # End-to-end pipeline tests
   --- test_complete_etl_pipeline.py
- fixtures/                # Test data and configurations
   --- sample_wms_data/
   --- test_configs/
- helpers/                 # Test utilities and generators
   --- wms_data_generators.py
```

### Coverage Requirements

- **Minimum**: 85% test coverage enforced
- **Unit Tests**: Fast tests with comprehensive mocking
- **Integration Tests**: Real Oracle WMS and database testing
- **E2E Tests**: Complete pipeline execution validation
- **Performance Tests**: Benchmarking for large datasets

### Running Tests

```bash
# All tests
make test                    # Python + Meltano tests with coverage

# Specific test categories
pytest -m unit               # Unit tests only
pytest -m integration        # Integration tests only
pytest -m wms                # WMS-specific tests
pytest -m oracle             # Oracle database tests
pytest -m performance        # Performance tests

# With coverage reporting
make coverage-html           # HTML report in reports/coverage/
```

## Quality Standards

### Zero Tolerance Quality Gates

- **Test Coverage**: Minimum 85% Python test coverage
- **Type Safety**: Strict MyPy with no untyped code
- **Linting**: Ruff with ALL rules enabled
- **Security**: Bandit scanning + pip-audit for vulnerabilities
- **Meltano Tests**: All pipeline tests must pass
- **Oracle Connectivity**: All Oracle integration tests must pass
- **Pre-commit**: Automated quality checks on every commit

### Code Standards

- **Python 3.13+**: Latest Python with modern type hints
- **Clean Architecture**: Strict layer separation following FLEXT patterns
- **Domain-Driven Design**: Rich domain entities with ETL business logic
- **Meltano Best Practices**: Proper Singer protocol implementation

## Dependencies

### FLEXT Ecosystem Dependencies

- **flext-core**: Foundation patterns, FlextResult, logging, dependency injection
- **flext-observability**: Monitoring, metrics, and distributed tracing
- **flext-db-oracle**: Oracle database connectivity and operations
- **flext-tap-oracle-wms**: Oracle WMS data extraction capabilities
- **flext-target-oracle**: Oracle database loading and upsert operations

### External Dependencies

- **Meltano 3.8.0**: Data integration and orchestration platform
- **dbt-core**: Data transformation framework
- **Click**: CLI framework for command-line interface
- **Pydantic**: Data validation and settings management
- **Poetry**: Dependency management and packaging

## Troubleshooting

### Common Pipeline Issues

```bash
# Connection problems
make oracle-test             # Test Oracle WMS connectivity
make meltano-validate        # Check Meltano configuration

# Pipeline validation
make gruponos-validate-data  # Validate data quality and integrity

# Performance issues
make gruponos-monitoring     # Check monitoring and alerting status

# Data quality issues
make meltano-discover        # Rediscover schemas from sources
```

### Quality Gate Failures

```bash
# Fix linting automatically
make format

# Type checking issues
poetry run mypy src/ --show-error-codes

# Security vulnerabilities
poetry run pip-audit --fix

# Test coverage below 85%
make coverage-html           # View detailed coverage report
```

### Meltano Issues

```bash
# Plugin installation problems
meltano install --force

# Configuration validation
meltano config list

# Pipeline debugging
meltano invoke tap-oracle-wms --discover
meltano run tap-oracle-wms target-oracle --dry-run
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/gruponos-enhancement`)
3. Develop and test changes
4. Run quality gates (`make validate`)
5. Update documentation
6. Commit changes (`git commit -m 'Add GrupoNOS ETL enhancement'`)
7. Push to branch (`git push origin feature/gruponos-enhancement`)
8. Open a Pull Request

## License

MIT License - see [LICENSE](LICENSE) for details.

## Documentation

### Architecture & Development

- [CLAUDE.md](CLAUDE.md) - Development guidance and architectural patterns
- [config/](config/) - Configuration files and examples
- [dbt/](dbt/) - Data transformation models

### Meltano Documentation

```bash
# View Meltano configuration
meltano config list

# Check Meltano environment
meltano environment list

# View available commands
meltano --help
```

### Related Projects

- [../../flext-core/](../../flext-core/) - Foundation library with shared patterns
- [../../flext-observability/](../../flext-observability/) - Monitoring and logging
- [../../flext-db-oracle/](../../flext-db-oracle/) - Oracle database connectivity
- [../../flext-tap-oracle-wms/](../../flext-tap-oracle-wms/) - Oracle WMS data extraction
- [../../flext-target-oracle/](../../flext-target-oracle/) - Oracle database loading

### Ecosystem Integration

- [../../flext-meltano/](../../flext-meltano/) - Meltano integration platform

---

**Framework**: FLEXT Ecosystem | **Technology**: Meltano 3.8.0 + Python 3.13+ | **Architecture**: Clean Architecture + DDD | **Updated**: 2025-07-30
