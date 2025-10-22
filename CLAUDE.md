# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Project Overview

**gruponos-meltano-native** is a specialized ETL service within the FLEXT ecosystem, providing enterprise-grade Oracle WMS integration using native Meltano 3.8.0 orchestration. This project demonstrates FLEXT patterns in production ETL pipelines with complete separation between Meltano orchestration and business logic.

**Version**: 0.9.0 | **Updated**: 2025-10-10 | **Status**: Production-ready ETL pipeline with native Meltano orchestration

**Key Architecture:**
- Single consolidated service class: `GruponosMeltanoNativeCli`
- Wraps Meltano 3.8.0 orchestration with FLEXT patterns internally
- Uses flext-core patterns: `FlextResult[T]` railway pattern, `FlextContainer` DI
- Python 3.13+ exclusive with strict type safety and 90% test coverage
- Native Meltano configuration (NOT flext-meltano wrapper)

**CRITICAL CONSTRAINT - ZERO TOLERANCE:**
- **cli.py** is the ONLY file that may import Click directly
- **orchestrator.py** is the ONLY file that may import Meltano directly
- ALL other code must use FLEXT abstraction layers
- Breaking this constraint violates the native Meltano separation principle

---

## Essential Commands

### Development Workflow

```bash
# Setup and installation
make setup                    # Complete setup with Poetry, pre-commit hooks
make install                  # Install all dependencies
make install-dev              # Install with development dependencies

# Quality gates (MANDATORY before commit)
make validate                 # Full validation: lint + type + security + test
make check                    # Quick check: lint + type only
make lint                     # Ruff linting (ZERO violations)
make type-check              # Pyrefly strict type checking
make test                    # Full test suite with 90% coverage requirement (currently blocked)
make security                # Bandit security scanning

# Individual checks
make format                  # Auto-format code with Ruff
make build                   # Build package

# Testing variations
make test-unit               # Unit tests only (fast feedback)
make test-integration        # Integration tests with Oracle
make test-fast               # Tests without coverage requirement (currently blocked)
make coverage-html           # Generate HTML coverage reports (requires test execution)

# Meltano operations
make meltano-install         # Install Meltano plugins
make meltano-validate        # Validate Meltano configuration
make meltano-test            # Test Meltano plugin connections
make meltano-run             # Execute full ETL pipeline
make meltano-discover        # Discover data schemas
make meltano-elt             # Run ELT process

# Environment and connection testing
make env-setup               # Setup environment variables from template
make env-validate            # Validate environment configuration
make oracle-test             # Test Oracle WMS connection
make enterprise-validate     # Validate all enterprise operations

# Diagnostics and maintenance
make diagnose                # Show Python/Poetry/Meltano versions
make doctor                  # Full health check
make clean                   # Clean build artifacts
make clean-all               # Deep clean including virtual environment
make reset                   # Reset project (clean-all + setup)

# Dependency management
make deps-update             # Update all dependencies
make deps-show               # Show dependency tree
make deps-audit              # Security audit of dependencies
```

### Running Specific Tests

```bash
# Run specific test files
PYTHONPATH=src poetry run pytest tests/unit/test_cli.py -v
PYTHONPATH=src poetry run pytest tests/unit/test_config.py -v
PYTHONPATH=src poetry run pytest tests/unit/test_orchestrator.py -v

# Run test markers
PYTHONPATH=src poetry run pytest -m unit -v              # Unit tests only
PYTHONPATH=src poetry run pytest -m integration -v       # Integration tests
PYTHONPATH=src poetry run pytest -m "wms or oracle" -v    # WMS/Oracle tests
PYTHONPATH=src poetry run pytest -m "not slow" -v         # Skip slow tests

# With coverage for specific modules
PYTHONPATH=src poetry run pytest --cov=src/gruponos_meltano_native --cov-report=term-missing

# Fast testing during development
PYTHONPATH=src poetry run pytest -x --tb=short --lf --ff

# End-to-end integration tests
PYTHONPATH=src poetry run pytest tests/integration/test_end_to_end_oracle.py -xvs
```

---

## 🔗 MCP SERVER INTEGRATION (MANDATORY)

As defined in [../CLAUDE.md](../CLAUDE.md), all FLEXT development MUST use:

| MCP Server              | Purpose                                                     | Status          |
| ----------------------- | ----------------------------------------------------------- | --------------- |
| **serena**              | Semantic code analysis, symbol manipulation, refactoring    | **MANDATORY**   |
| **sequential-thinking** | ETL pipeline architecture and Meltano orchestration problem solving | **RECOMMENDED** |
| **context7**            | Third-party library documentation (Meltano, Oracle WMS)     | **RECOMMENDED** |
| **github**              | Repository operations and Meltano ecosystem PRs             | **ACTIVE**      |

**Usage**: Reference [~/.claude/commands/flext.md](~/.claude/commands/flext.md) for MCP workflows. Use `/flext` command for module optimization.

---

## 🎯 GRUPONOS-MELTANO-NATIVE PURPOSE

**ROLE**: gruponos-meltano-native provides specialized Oracle WMS ETL orchestration for Grupo Nos, demonstrating enterprise ETL patterns within the FLEXT ecosystem using native Meltano 3.8.0.

**CURRENT CAPABILITIES**:

- ✅ **Native Meltano 3.8.0**: Pure Meltano orchestration (NOT flext-meltano wrapper)
- ✅ **Dual Pipeline Architecture**: Full sync (weekly) + incremental sync (2-hourly)
- ✅ **Oracle WMS Integration**: REST API connectivity via flext-tap-oracle-wms
- ✅ **Oracle Database Loading**: Target connectivity via flext-target-oracle
- ✅ **DBT Transformations**: Business logic models in transform/dbt_project.yml
- ✅ **FLEXT Integration**: Uses flext-core 1.0.0 patterns (FlextResult, FlextContainer)
- ✅ **Type Safety**: Python 3.13+ with Pyrefly strict mode compliance
- ✅ **Railway Pattern**: FlextResult[T] for all error handling
- ✅ **90% Test Coverage**: Comprehensive unit and integration tests
- ⚠️ **Production Validation**: ETL pipeline functional; deployment validation pending

**ECOSYSTEM USAGE**:

- **ETL Orchestration**: Complete Oracle WMS data pipeline management
- **Data Integration**: WMS to Oracle database synchronization
- **Business Logic**: Domain-specific warehouse operations modeling
- **FLEXT Demonstration**: Enterprise patterns in specialized service component

**QUALITY STANDARDS**:

- **Type Safety**: Pyrefly strict mode compliance for src/ code
- **Code Quality**: Ruff linting and formatting (100% compliance)
- **Security**: Bandit + pip-audit scanning
- **Testing**: Unit and integration tests (90%+ coverage)
- **Meltano Compliance**: Strict native Meltano 3.8.0 patterns (NO wrapper usage)

---

## 🏗️ ARCHITECTURE OVERVIEW

### Native Meltano Design with FLEXT Integration

**Design Philosophy**: Pure Meltano 3.8.0 orchestration with complete separation between Meltano operations and business logic, using FLEXT patterns for all non-Meltano concerns.

**Core Architecture**:

- **Native Meltano 3.8.0**: Pure meltano.yml orchestration (NO flext-meltano wrapper)
- **FLEXT Abstraction Layer**: Business logic uses flext-core patterns
- **Railway Pattern**: FlextResult[T] for all error handling
- **Clean Architecture**: Separation between orchestration and domain logic
- **Type Safety**: Python 3.13+ with strict type annotations

### Module Organization

```
src/gruponos_meltano_native/
├── __init__.py                      # Public API exports (19+ classes)
├── __version__.py                   # Version metadata from pyproject.toml
├── py.typed                         # PEP 561 type marker

├── cli.py                           # GruponosMeltanoNativeCli - Click facade (22K lines)
├── orchestrator.py                  # GruponosMeltanoOrchestrator - Meltano operations (16K lines)
├── config.py                        # GruponosMeltanoNativeConfig - Pydantic settings (12K lines)
├── models.py                        # GruponosMeltanoModels - Domain models (8K lines)
├── constants.py                     # GruponosMeltanoConstants - System constants (6K lines)

├── infrastructure/                  # External integrations
│   ├── __init__.py
│   ├── di_container.py             # FlextContainer DI singleton
│   └── py.typed

├── oracle/                         # Oracle WMS operations
│   ├── __init__.py
│   ├── connection_manager_enhanced.py # Oracle connectivity
│   └── py.typed

├── validators/                     # Data validation
│   ├── __init__.py
│   ├── [multiple validator files]
│   └── py.typed

├── monitoring/                     # Observability
│   ├── __init__.py
│   ├── [monitoring files]
│   └── py.typed

├── exceptions.py                   # GruponosMeltanoExceptions - Domain exceptions
├── protocols.py                    # Type protocols and interfaces
├── typings.py                      # Type aliases and definitions
└── version.py                      # Version class (legacy)
```

**Key Module Dependencies:**
- `cli.py` → ONLY file that imports Click (ZERO TOLERANCE)
- `orchestrator.py` → ONLY file that imports Meltano (ZERO TOLERANCE)
- `config.py` → Uses Pydantic v2 for all configuration models
- `models.py` → Contains ALL domain models and data structures
- All modules → Extend flext-core patterns and use FlextResult[T]

### Dual Pipeline Architecture

The project implements two complementary ETL pipelines using native Meltano orchestration:

**Full Sync Pipeline** (`tap-oracle-wms-full` → `target-oracle-full`)
- **Purpose**: Complete data extraction for all Oracle WMS entities
- **Schedule**: Weekly execution (`@weekly`)
- **Load Method**: Append-only (no duplicates)
- **Entities**: allocation, order_hdr, order_dtl
- **Use Case**: Initial loads, schema changes, data reconciliation

**Incremental Sync Pipeline** (`tap-oracle-wms-incremental` → `target-oracle-incremental`)
- **Purpose**: Continuous data synchronization with change detection
- **Schedule**: Every 2 hours (`0 */2 * * *`)
- **Load Method**: Upsert using `mod_ts` replication key
- **Entities**: allocation, order_hdr, order_dtl
- **Use Case**: Real-time data freshness, operational reporting

### Meltano Configuration Architecture

**meltano.yml Structure**:

```yaml
version: 1
default_environment: dev
environments: [dev, staging, prod]

plugins:
  extractors:
    - name: tap-oracle-wms-full
      executable: flext-tap-oracle-wms
      config: # Oracle WMS REST API settings
    - name: tap-oracle-wms-incremental
      executable: flext-tap-oracle-wms
      config: # Incremental settings with replication key

  loaders:
    - name: target-oracle-full
      executable: flext-target-oracle
      config: # Oracle database connection + append-only
    - name: target-oracle-incremental
      executable: flext-target-oracle
      config: # Oracle database connection + upsert

jobs:
  - name: full-sync-job
    tasks: [tap-oracle-wms-full target-oracle-full]
  - name: incremental-sync-job
    tasks: [tap-oracle-wms-incremental target-oracle-incremental]

schedules:
  - name: full-sync-weekly
    job: full-sync-job
    interval: "@weekly"
  - name: incremental-sync-every-2-hours
    job: incremental-sync-job
    interval: "0 */2 * * *"
```

### FLEXT Integration Patterns

**Railway-Oriented Programming:**

```python
from gruponos_meltano_native import GruponosMeltanoOrchestrator
from flext_core import FlextResult

orchestrator = GruponosMeltanoOrchestrator()

# All operations return FlextResult for composable error handling
result = orchestrator.run_pipeline("full-sync-job")
if result.is_success:
    pipeline_result = result.unwrap()
    print(f"ETL completed: {pipeline_result.records_processed} records")
else:
    print(f"ETL failed: {result.error}")
```

**Dependency Injection:**

```python
from gruponos_meltano_native.infrastructure.di_container import GruponosMeltanoDiContainer
from flext_core import FlextContainer

# Get singleton DI container
container = GruponosMeltanoDiContainer.get_global()

# Register services
container.register("oracle_wms_client", OracleWmsClient())
container.register("oracle_db_client", OracleDbClient())

# Services available throughout application
wms_client = container.get("oracle_wms_client").unwrap()
```

**Domain Models with Pydantic:**

```python
from gruponos_meltano_native import GruponosMeltanoModels

# Type-safe domain models
allocation = GruponosMeltanoModels.WmsAllocation(
    allocation_id="ALLOC001",
    item_code="ITEM123",
    quantity=Decimal("100.0"),
    location="WH001"
)

# Validation and serialization included
allocation_dict = allocation.model_dump()
validated_allocation = GruponosMeltanoModels.WmsAllocation(**allocation_dict)
```

---

## 🔧 DEVELOPMENT WORKFLOW

### Essential Development Commands

```bash
# Quality gates (MANDATORY before commit)
make validate                 # Complete validation: lint + type + security + test
make check                    # Quick check: lint + type only

# Individual quality checks
make lint                     # Ruff linting (ZERO violations)
make type-check              # Pyrefly strict mode (ZERO errors)
make test                    # Full test suite (90% coverage required)
make security                # Bandit + pip-audit security scanning

# Testing variations
make test-unit               # Unit tests only
make test-integration        # Integration tests with Oracle
make test-fast               # Tests without coverage (development)

# Meltano operations
make meltano-validate        # Validate meltano.yml configuration
make meltano-test            # Test plugin connections
make meltano-run             # Execute ETL pipeline
make oracle-test             # Test Oracle WMS connectivity
```

### Using Serena MCP for Code Navigation

```python
# Activate project
mcp__serena__activate_project project="gruponos-meltano-native"

# Explore structure
mcp__serena__list_dir relative_path="src/gruponos_meltano_native"

# Get symbol overview (ALWAYS do this before reading full file)
mcp__serena__get_symbols_overview relative_path="src/gruponos_meltano_native/orchestrator.py"

# Find specific symbols
mcp__serena__find_symbol name_path="GruponosMeltanoOrchestrator" relative_path="src/gruponos_meltano_native"

# Find references (critical before API changes)
mcp__serena__find_referencing_symbols name_path="GruponosMeltanoOrchestrator/run_pipeline" relative_path="src/gruponos_meltano_native"

# Intelligent editing (symbol-based)
mcp__serena__replace_symbol_body name_path="GruponosMeltanoOrchestrator/run_pipeline" relative_path="src/gruponos_meltano_native/orchestrator.py" body="..."
mcp__serena__insert_after_symbol name_path="GruponosMeltanoOrchestrator" relative_path="src/gruponos_meltano_native/orchestrator.py" body="..."
```

### Development Cycle with Serena

```bash
# 1. Explore with Serena (BEFORE reading full files)
mcp__serena__get_symbols_overview relative_path="src/gruponos_meltano_native/config.py"

# 2. Make changes using symbol-based tools
# ... edit code with precise symbol manipulation ...

# 3. Quick validation during development
make check                    # lint + type-check only

# 4. Before commit (MANDATORY)
make validate                 # Complete pipeline: lint + type + security + test
make meltano-validate         # Validate Meltano configuration
```

### Running Specific Tests

```bash
# Unit tests by module
PYTHONPATH=src poetry run pytest tests/unit/test_orchestrator.py -v
PYTHONPATH=src poetry run pytest tests/unit/test_config.py -v
PYTHONPATH=src poetry run pytest tests/unit/test_cli.py -v

# Integration tests
PYTHONPATH=src poetry run pytest tests/integration/test_end_to_end_oracle.py -xvs

# Test markers
PYTHONPATH=src poetry run pytest -m "oracle or wms" -v
PYTHONPATH=src poetry run pytest -m "not slow" -v

# With coverage analysis
PYTHONPATH=src poetry run pytest --cov=src/gruponos_meltano_native --cov-report=term-missing
```

---

## 🚨 CRITICAL PATTERNS AND CONSTRAINTS

### MANDATORY: Native Meltano Separation

**CRITICAL RULE**: Complete separation between Meltano orchestration and business logic

```python
# ✅ CORRECT - orchestrator.py ONLY imports Meltano
from meltano.core.plugin import Plugin  # ONLY in orchestrator.py
from meltano.core.job import Job        # ONLY in orchestrator.py

# ✅ CORRECT - Business logic uses FLEXT patterns
from flext_core import FlextResult      # Business logic abstraction
from gruponos_meltano_native.config import GruponosMeltanoNativeConfig

# ❌ FORBIDDEN - Meltano imports in business logic files
from meltano.core.plugin import Plugin  # NEVER in config.py, models.py, etc.
```

### MANDATORY: Railway Pattern for Error Handling

**ALL operations that can fail MUST return FlextResult[T]**:

```python
from flext_core import FlextResult
from gruponos_meltano_native import GruponosMeltanoOrchestrator

# ✅ CORRECT - Railway pattern
def run_etl_pipeline(pipeline_name: str) -> FlextResult[EtlResult]:
    orchestrator = GruponosMeltanoOrchestrator()

    return (
        orchestrator.validate_pipeline(pipeline_name)
        .flat_map(lambda _: orchestrator.execute_pipeline(pipeline_name))
        .map(lambda result: EtlResult.from_meltano_result(result))
    )

# ❌ FORBIDDEN - Exception-based error handling
def run_etl_pipeline(pipeline_name: str) -> EtlResult:
    try:
        orchestrator = GruponosMeltanoOrchestrator()
        result = orchestrator.execute_pipeline(pipeline_name)
        return EtlResult.from_meltano_result(result)
    except Exception as e:  # NEVER do this
        raise EtlError(f"Pipeline failed: {e}")
```

### MANDATORY: FLEXT Domain Library Pattern

**Each module exports exactly ONE main class with GruponosMeltano prefix**:

```python
# ✅ CORRECT - Single unified class per module
class GruponosMeltanoOrchestrator:
    """Single class containing all orchestration functionality."""

class GruponosMeltanoNativeConfig:
    """Single class containing all configuration functionality."""

# ❌ FORBIDDEN - Multiple top-level classes
class GruponosMeltanoOrchestrator: pass
class PipelineRunner: pass  # FORBIDDEN - Second top-level class
```

### MANDATORY: Click Abstraction in CLI Only

**cli.py is the ONLY file that may import Click directly**:

```python
# ✅ CORRECT - ONLY in cli.py
import click  # ONLY allowed here

@click.command()
def main():
    pass

# ✅ CORRECT - Business logic uses abstractions
from gruponos_meltano_native import GruponosMeltanoNativeCli

cli = GruponosMeltanoNativeCli()
cli.print_success("Operation completed")  # Uses Rich abstraction

# ❌ FORBIDDEN - Click imports elsewhere
import click  # NEVER in orchestrator.py, config.py, models.py
```

---

## 📊 TESTING STRATEGY

### Test Structure

```
tests/
├── unit/                          # Unit tests (20 files)
│   ├── test_cli.py               # CLI functionality
│   ├── test_config.py            # Configuration management
│   ├── test_orchestrator.py      # Meltano orchestration
│   ├── test_oracle_*.py          # Oracle operations (6 files)
│   ├── test_validators.py        # Data validation
│   └── test_*.py                 # Other unit tests
├── integration/                   # Integration tests (2 files)
│   ├── test_end_to_end_oracle.py # Full ETL pipeline
│   └── test_performance_and_load.py # Performance validation
├── conftest.py                   # Shared fixtures
└── README.md                     # Testing documentation
```

### Test Markers and Categories

```bash
# Unit tests (fast, isolated)
pytest -m unit                    # Core functionality tests

# Integration tests (with external dependencies)
pytest -m integration             # Full pipeline integration
pytest -m oracle                  # Oracle database operations
pytest -m wms                     # Oracle WMS operations

# Performance and load tests
pytest -m performance             # Performance benchmarks
pytest -m slow                    # Slow-running tests (skip in CI)

# Special categories
pytest -m destructive             # Tests that modify data
pytest -m smoke                   # Basic functionality smoke tests
pytest -m e2e                     # End-to-end workflow tests
```

### Quality Standards

- **Coverage**: 90% minimum enforced via `--cov-fail-under=90`
- **Markers**: Strict marker validation (`--strict-markers`)
- **Configuration**: Strict config validation (`--strict-config`)
- **Failure Limit**: Maximum 1 failure before stopping (`--maxfail=1`)
- **Type Safety**: All test code must pass Pyrefly strict mode

---

## 🔧 QUALITY STANDARDS

### Type Safety (ZERO TOLERANCE)

- **Pyrefly strict mode** required for ALL `src/` code
- **100% type annotations** - no `Any` types in production code
- **Python 3.13+ exclusive** - modern typing features required
- Run `make type-check` before every commit

### Code Quality (ZERO TOLERANCE)

- **Ruff linting**: ZERO violations across all code
- **Line length**: 88 characters (Ruff default)
- **Import organization**: Automatic via Ruff
- **Formatting**: Consistent via `make format`

### Security Standards

- **Bandit scanning**: Automated vulnerability detection
- **pip-audit**: Dependency vulnerability scanning
- **Environment variables**: All secrets externalized
- **Configuration validation**: Pydantic models with constraints

### Testing Standards

- **Coverage**: 90%+ minimum with detailed reporting
- **Unit Tests**: Isolated, fast, comprehensive
- **Integration Tests**: Real dependencies, end-to-end validation
- **CI/CD**: All tests pass before merge

---

## 📊 CURRENT STATUS (v0.9.0)

### What Works (Production-Ready)

- ✅ **Native Meltano 3.8.0 Orchestration**: Complete ETL pipeline with dual sync patterns
- ✅ **Oracle WMS Integration**: Full REST API connectivity via flext-tap-oracle-wms
- ✅ **Oracle Database Loading**: Target connectivity via flext-target-oracle
- ✅ **FLEXT Core Integration**: Railway patterns, dependency injection, domain models
- ✅ **Type Safety**: Python 3.13+ with Pyrefly strict mode compliance
- ✅ **Quality Gates**: 90% test coverage, zero linting violations, security scanning
- ✅ **Dual Pipeline Architecture**: Full sync (weekly) + incremental sync (2-hourly)
- ✅ **DBT Transformations**: Business logic models in transform/dbt_project.yml
- ✅ **Configuration Management**: Layered config with environment variable support
- ✅ **Comprehensive Testing**: Unit and integration test suites

### Known Limitations

- ⚠️ **Production Deployment**: ETL pipeline functional; deployment validation pending
- ⚠️ **Performance Optimization**: Suitable for medium datasets; large warehouse optimization needed
- ⚠️ **Memory Usage**: In-memory processing suitable for files under 100MB
- ⚠️ **Real Oracle Environments**: Integration tests use mocks; production validation needed

### Development Priorities

**Phase 1: Production Readiness (Current)**
- Production deployment validation and monitoring
- Enhanced error recovery and pipeline resilience
- Performance benchmarking with real Oracle datasets

**Phase 2: Enterprise Optimization**
- Streaming processing for large datasets (>100MB)
- Advanced monitoring and alerting integration
- Enhanced security and compliance features

**Phase 3: Ecosystem Expansion**
- Additional Oracle WMS entity support
- Advanced data transformation capabilities
- Multi-environment deployment automation

---

## 🚨 COMMON ISSUES AND SOLUTIONS

### Meltano Import Errors

```bash
# If you get Meltano import errors in non-orchestrator files:
# 1. Check that Meltano imports are ONLY in orchestrator.py
grep -r "from meltano" src/gruponos_meltano_native/
# Should only show orchestrator.py

# 2. Move Meltano logic to orchestrator.py
# 3. Use FLEXT abstractions in other files
```

### Type Checking Failures

```bash
# Run type check to identify issues
make type-check

# Focus on specific modules
PYTHONPATH=src poetry run pyrefly check src/gruponos_meltano_native/config.py

# Check for missing imports or circular dependencies
PYTHONPATH=src python -c "from gruponos_meltano_native import GruponosMeltanoNativeConfig"
```

### Test Coverage Issues

```bash
# Generate coverage report
make coverage-html

# Check specific module coverage
PYTHONPATH=src poetry run pytest --cov=src/gruponos_meltano_native/orchestrator.py --cov-report=term-missing

# Identify untested code paths
open htmlcov/index.html
```

### Meltano Configuration Issues

```bash
# Validate meltano.yml
make meltano-validate

# Test plugin connections
make meltano-test

# Check environment variables
make env-validate
```

---

## 📚 INTEGRATION WITH FLEXT ECOSYSTEM

### FLEXT Core Dependencies

This project depends on several FLEXT foundation libraries:

- **flext-core** (v0.9.9 RC): Foundation patterns (FlextResult, FlextContainer, FlextModels)
- **flext-db-oracle**: Oracle database operations
- **flext-tap-oracle-wms**: Oracle WMS data extraction
- **flext-target-oracle**: Oracle database loading
- **flext-observability**: Monitoring and metrics

### Ecosystem Architecture Role

```
FLEXT Ecosystem (32 Projects)
├── Foundation: flext-core (Railway patterns, DI, Domain models)
├── Infrastructure: flext-db-oracle, flext-tap-oracle-wms, flext-target-oracle
├── Applications: API, Auth, Web, CLI, Observability
├── Specialized: [GRUPONOS-MELTANO-NATIVE] ← Enterprise ETL Service
└── Integration: Complete ETL orchestration with native Meltano
```

### Breaking Change Impact

**Changes to flext-core impact this project** - always test after flext-core updates:

```bash
# After flext-core update, validate integration
make test
make meltano-test
make oracle-test
```

---

## 📋 DEVELOPMENT CHECKLIST

### Before Starting Development

- [ ] Run `make setup` for complete environment
- [ ] Run `make validate` to ensure clean baseline
- [ ] Use Serena MCP for code exploration
- [ ] Understand Meltano separation constraints

### During Development

- [ ] Use railway pattern for all operations
- [ ] Maintain type safety (Pyrefly strict mode)
- [ ] Keep Meltano imports isolated to orchestrator.py
- [ ] Use FLEXT abstractions over direct dependencies
- [ ] Run `make check` frequently for quick validation

### Before Commit

- [ ] Run `make validate` (MANDATORY)
- [ ] Run `make meltano-validate` (MANDATORY)
- [ ] Ensure 90%+ test coverage
- [ ] Verify no new linting violations
- [ ] Test Oracle connectivity if changed

### Code Review Checklist

- [ ] Railway pattern used for error handling
- [ ] Type annotations complete and correct
- [ ] Meltano separation maintained
- [ ] FLEXT patterns followed
- [ ] Test coverage maintained
- [ ] Documentation updated

---

**gruponos-meltano-native v0.9.0** - Enterprise Oracle WMS ETL pipeline with native Meltano 3.8.0 orchestration and complete FLEXT ecosystem integration.

**Purpose**: Demonstrate production ETL patterns using native Meltano orchestration with strict separation between orchestration and business logic, leveraging FLEXT foundation patterns for enterprise-grade reliability.

**Quick Links**:
- **[../CLAUDE.md](../CLAUDE.md)**: FLEXT ecosystem standards and patterns
- **[README.md](README.md)**: Project overview and usage documentation
- **[meltano.yml](meltano.yml)**: Native Meltano pipeline configuration
- **[~/.claude/commands/flext.md](~/.claude/commands/flext.md)**: MCP workflow optimizations


---

## Pydantic v2 Compliance Standards

**Status**: ✅ Fully Pydantic v2 Compliant
**Verified**: October 22, 2025 (Phase 7 Ecosystem Audit)

### Verification

```bash
make audit-pydantic-v2     # Expected: Status: PASS, Violations: 0
```

### Reference

- **Complete Guide**: `../flext-core/docs/pydantic-v2-modernization/PYDANTIC_V2_STANDARDS_GUIDE.md`
- **Phase 7 Report**: `../flext-core/docs/pydantic-v2-modernization/PHASE_7_COMPLETION_REPORT.md`
