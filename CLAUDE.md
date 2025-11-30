# Gruponos-Meltano-Native Project Guidelines

**Reference**: See [../CLAUDE.md](../CLAUDE.md) for FLEXT ecosystem standards and general rules.

---

## Project Overview

**gruponos-meltano-native** is a specialized ETL service within the FLEXT ecosystem, providing enterprise-grade Oracle WMS integration using native Meltano 3.8.0 orchestration. This project demonstrates FLEXT patterns in production ETL pipelines with complete separation between Meltano orchestration and business logic.

**Version**: 0.9.0  
**Status**: Production-ready  
**Python**: 3.13+  
**Coverage Target**: 90%

**Key Architecture**:
- Single consolidated service class: `GruponosMeltanoNativeCli`
- Wraps Meltano 3.8.0 orchestration with FLEXT patterns internally
- Uses flext-core patterns: `FlextResult[T]` railway pattern, `FlextContainer` DI
- Native Meltano configuration (NOT flext-meltano wrapper)

**CRITICAL CONSTRAINT - ZERO TOLERANCE**:
- **cli.py** is the ONLY file that may import Click directly
- **orchestrator.py** is the ONLY file that may import Meltano directly
- ALL other code must use FLEXT abstraction layers
- Breaking this constraint violates the native Meltano separation principle

---

## Essential Commands

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
make test                    # Full test suite with 90% coverage requirement
make security                # Bandit security scanning
```

---

## Key Patterns

### Native Meltano Orchestration

```python
from flext_core import FlextResult
from gruponos_meltano_native import GruponosMeltanoNativeCli

cli = GruponosMeltanoNativeCli()

# Execute ETL pipeline
result = cli.execute_pipeline(config={...})
if result.is_success:
    output = result.unwrap()
```

---

## Critical Development Rules

### ZERO TOLERANCE Policies

**ABSOLUTELY FORBIDDEN**:
- ❌ Direct Click imports outside cli.py
- ❌ Direct Meltano imports outside orchestrator.py
- ❌ Exception-based error handling (use FlextResult)
- ❌ Type ignores or `Any` types
- ❌ Mockpatch in tests

**MANDATORY**:
- ✅ Use `FlextResult[T]` for all operations
- ✅ Complete type annotations
- ✅ Zero Ruff violations
- ✅ 90%+ test coverage
- ✅ Use FLEXT abstraction layers

---

**Additional Resources**: [../CLAUDE.md](../CLAUDE.md) (workspace), [README.md](README.md) (overview)
