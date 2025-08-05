# gruponos-meltano-native

**Type**: Specialized Service | **Status**: Development | **Dependencies**: flext-core, flext-meltano

Oracle WMS ETL pipeline implementation for GrupoNOS using Meltano orchestration platform.

> **⚠️ Development Status**: ETL pipeline working, Meltano integration functional, Oracle WMS connectivity established, production deployment validation needed

## Quick Start

```bash
# Install dependencies
poetry install

# Test basic functionality
python -c "from gruponos_meltano_native import cli; print('✅ Working')"

# Development setup
make setup

# Run ETL pipeline
make meltano-run
```

## Current Reality

**What Actually Works:**

- Complete Oracle WMS ETL pipeline with Meltano orchestration
- Two-job architecture (full sync + incremental sync)
- Oracle WMS REST API integration via flext-tap-oracle-wms
- Oracle database loading via flext-target-oracle
- DBT transformations for data modeling

**What Needs Work:**

- Production deployment validation and monitoring
- Performance optimization for large warehouse datasets
- Enhanced error recovery and pipeline resilience
- Comprehensive integration test coverage with real Oracle environments

## Architecture Role in FLEXT Ecosystem

### **Specialized Service Component**

GrupoNOS Meltano Native demonstrates FLEXT patterns in enterprise ETL:

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLEXT ECOSYSTEM (32 Projects)                 │
├─────────────────────────────────────────────────────────────────┤
│ Services: FlexCore(Go) | FLEXT Service(Go/Python) | Clients     │
├─────────────────────────────────────────────────────────────────┤
│ Applications: API | Auth | Web | CLI | Quality | Observability  │
├─────────────────────────────────────────────────────────────────┤
│ Infrastructure: Oracle | LDAP | LDIF | gRPC | Plugin | WMS      │
├─────────────────────────────────────────────────────────────────┤
│ Singer Ecosystem: Taps(5) | Targets(5) | DBT(4) | Extensions(1) │
├─────────────────────────────────────────────────────────────────┤
│ Specialized: ALGAR-OUD-MIG | [GRUPONOS-MELTANO]                 │
├─────────────────────────────────────────────────────────────────┤
│ Foundation: FLEXT-CORE (FlextResult | DI | Domain Patterns)     │
└─────────────────────────────────────────────────────────────────┘
```

### **Core Responsibilities**

1. **ETL Orchestration**: Complete Oracle WMS data pipeline management
2. **Data Integration**: WMS to Oracle database synchronization
3. **Business Logic**: Domain-specific warehouse operations modeling

## Key Features

### **Current Capabilities**

- **Meltano Integration**: Complete ETL orchestration with Meltano 3.8.0
- **Dual Pipeline Architecture**: Full sync (weekly) and incremental sync (2-hourly)
- **Oracle WMS Integration**: REST API connectivity via flext-tap-oracle-wms
- **DBT Transformations**: Business logic models and data transformations

### **Pipeline Architecture**

```bash
# Full sync pipeline (weekly)
tap-oracle-wms → target-oracle (append-only)

# Incremental sync pipeline (every 2 hours)
tap-oracle-wms → target-oracle (upsert with mod_ts replication)

# DBT transformations
raw → staging → intermediate → marts
```

## Installation & Usage

### Installation

```bash
# Clone and install
cd /path/to/gruponos-meltano-native
poetry install

# Development setup
make setup

# Environment setup
make env-setup
```

### Basic Usage

```bash
# Setup environment variables
export TAP_ORACLE_WMS_BASE_URL="https://your-wms.com"
export TAP_ORACLE_WMS_USERNAME="api_user"
export TAP_ORACLE_WMS_PASSWORD="password"
export FLEXT_TARGET_ORACLE_HOST="oracle-db.com"
export FLEXT_TARGET_ORACLE_USERNAME="etl_user"

# Run Meltano pipeline
make meltano-run

# Test connections
make oracle-test
make meltano-test
```

### CLI Operations

```bash
# CLI interface
python -m gruponos_meltano_native.cli --help
python -m gruponos_meltano_native.cli --dev

# Pipeline operations
make meltano-install      # Install Meltano plugins
make meltano-discover     # Discover schemas
make meltano-elt          # Run ELT process
```

## Development Commands

### Quality Gates (Zero Tolerance)

```bash
# Complete validation pipeline (run before commits)
make validate              # Full validation (lint + type + security + test)
make check                 # Quick lint + type check + security
make test                  # Run all tests (90% coverage requirement)
make lint                  # Code linting
make type-check            # Type checking
make format                # Code formatting
make security              # Security scanning
```

### ETL Operations

```bash
# Meltano operations
make meltano-run           # Execute full pipeline
make meltano-validate      # Validate configuration
make meltano-discover      # Schema discovery
make oracle-test           # Test Oracle connections
make enterprise-validate   # Full enterprise validation
```

### Testing

```bash
# Test categories
make test-unit             # Unit tests only
make test-integration      # Integration tests with Oracle
make test-fast             # Fast tests without coverage
make coverage-html         # Generate HTML coverage report

# Specific test markers
pytest -m "wms or oracle"  # WMS or Oracle tests
pytest -m "not slow"       # Exclude slow tests
```

## Configuration

### Environment Variables

```bash
# Oracle WMS REST API (Source)
export TAP_ORACLE_WMS_BASE_URL="https://your-wms.com"
export TAP_ORACLE_WMS_USERNAME="api_user"
export TAP_ORACLE_WMS_PASSWORD="password"
export TAP_ORACLE_WMS_COMPANY_CODE="company"
export TAP_ORACLE_WMS_FACILITY_CODE="facility"

# Oracle Database (Target)
export FLEXT_TARGET_ORACLE_HOST="oracle-db.com"
export FLEXT_TARGET_ORACLE_PORT="1521"
export FLEXT_TARGET_ORACLE_SERVICE_NAME="ORCL"
export FLEXT_TARGET_ORACLE_USERNAME="etl_user"
export FLEXT_TARGET_ORACLE_PASSWORD="password"
```

### Pipeline Configuration

```yaml
# meltano.yml
jobs:
  - name: wms-full-sync
    tasks:
      - tap-oracle-wms-full target-oracle-full
    interval: "@weekly"

  - name: wms-incremental-sync
    tasks:
      - tap-oracle-wms-incremental target-oracle-incremental
    interval: "0 */2 * * *"
```

## Quality Standards

### **Zero Tolerance Quality Gates**

- **Coverage**: 90% test coverage enforced
- **Type Safety**: Strict MyPy configuration with Python 3.13
- **Linting**: Ruff with comprehensive rules (ALL enabled)
- **Security**: Bandit + pip-audit scanning

## Integration with FLEXT Ecosystem

### **FLEXT Core Patterns**

```python
# ETL using FLEXT patterns
from gruponos_meltano_native import orchestrator
from flext_core import FlextResult

result = await orchestrator.run_pipeline("wms-full-sync")
if result.success:
    print(f"Pipeline completed: {result.data}")
else:
    print(f"Pipeline failed: {result.error}")
```

### **Service Integration**

- **flext-tap-oracle-wms**: Oracle WMS data extraction
- **flext-target-oracle**: Oracle database loading
- **flext-meltano**: Pipeline orchestration platform
- **flext-observability**: ETL monitoring and metrics

## Current Status

**Version**: 0.9.0 (Development)

**Completed**:

- ✅ Complete ETL pipeline with Meltano orchestration
- ✅ Dual pipeline architecture (full + incremental sync)
- ✅ Oracle WMS REST API integration
- ✅ DBT transformations for business logic

**In Progress**:

- 🔄 Production deployment validation
- 🔄 Performance optimization for large datasets
- 🔄 Enhanced error recovery mechanisms

**Planned**:

- 📋 Advanced monitoring and alerting
- 📋 Pipeline performance benchmarking
- 📋 Comprehensive integration testing

## Contributing

### Development Standards

- **FLEXT Core Integration**: Use established patterns
- **Type Safety**: All code must pass MyPy with Python 3.13
- **Testing**: Maintain 90% coverage
- **ETL Best Practices**: Follow Meltano and dbt conventions

### Development Workflow

```bash
# Setup and validate
make setup
make validate
make test
make meltano-test
```

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Links

- **[flext-core](../flext-core)**: Foundation library
- **[flext-meltano](../flext-meltano)**: Meltano integration
- **[CLAUDE.md](CLAUDE.md)**: Development guidance

---

_Specialized service within the FLEXT ecosystem - Enterprise data integration platform_
