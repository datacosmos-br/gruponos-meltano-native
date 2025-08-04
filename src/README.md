# Source Code Documentation

**GrupoNOS Meltano Native - Enterprise ETL Pipeline Framework**

This directory contains the complete source code for the GrupoNOS Meltano Native ETL pipeline, built on FLEXT framework standards with Clean Architecture and Domain-Driven Design patterns.

## Directory Structure

```
src/gruponos_meltano_native/
├── __init__.py                     # Public API and factory functions
├── cli.py                          # Command-line interface with Click
├── config.py                       # Configuration management with Pydantic
├── orchestrator.py                 # Main ETL pipeline orchestration
├── exceptions.py                   # Domain-specific exception hierarchy
├── infrastructure/                 # Cross-cutting infrastructure concerns
│   ├── __init__.py                # Infrastructure exports
│   └── di_container.py            # Dependency injection container
├── monitoring/                     # Monitoring and alerting
│   ├── __init__.py                # Monitoring exports
│   └── alert_manager.py           # Alert delivery and management
├── oracle/                         # Oracle database integration
│   ├── __init__.py                # Oracle integration exports
│   └── connection_manager_enhanced.py # Enhanced connection management
└── validators/                     # Data validation and quality
    ├── __init__.py                # Validator exports
    └── data_validator.py          # Core data validation logic
```

## Module Organization

### Foundation Layer (`__init__.py`)

- **Purpose**: Public API gateway with factory functions
- **Pattern**: Clean imports with FLEXT standard naming
- **Exports**: All public classes and factory functions
- **Integration**: Direct FLEXT core foundation imports

### Application Layer

- **`cli.py`**: Command-line interface with Click framework integration
- **`orchestrator.py`**: Main ETL pipeline orchestration with railway-oriented programming
- **`config.py`**: Configuration management using Pydantic models with environment awareness

### Domain Layer

- **`exceptions.py`**: Comprehensive exception hierarchy with context-rich error handling
- **Business Logic**: Embedded within orchestrator and validator components

### Infrastructure Layer

- **`infrastructure/`**: Cross-cutting concerns like dependency injection
- **`monitoring/`**: Alert management and performance monitoring
- **`oracle/`**: Oracle database connectivity and operations
- **`validators/`**: Data validation and quality assurance

## Key Patterns

### FLEXT Integration

All modules follow FLEXT ecosystem standards:

- **FlextResult**: Railway-oriented programming for error handling
- **FlextBaseSettings**: Configuration with environment variable support
- **FlextContainer**: Dependency injection for loose coupling
- **Naming Conventions**: GruponosMeltano prefix for all public APIs

### Clean Architecture

- **Dependency Direction**: Dependencies flow inward toward domain core
- **Layer Separation**: Clear boundaries between presentation, application, domain, and infrastructure
- **Testability**: All components designed for comprehensive unit and integration testing

### Error Handling

- **Consistent Patterns**: FlextResult used throughout for predictable error propagation
- **Rich Context**: Exceptions include detailed context for debugging and monitoring
- **Railway-Oriented**: Error handling chains prevent nested try/catch blocks

## Development Guidelines

### Code Quality Standards

- **Type Annotations**: Complete type hints with MyPy compliance (95%+ coverage)
- **Documentation**: Comprehensive docstrings with examples and integration notes
- **Testing**: 90% minimum test coverage with unit, integration, and E2E tests
- **Linting**: Ruff with comprehensive rule set for code quality

### Integration Patterns

- **FLEXT Dependencies**: Use FLEXT ecosystem components consistently
- **Configuration**: Environment-aware settings with validation
- **Monitoring**: Observable operations with metrics and health checks
- **Error Recovery**: Graceful degradation and retry mechanisms

### Module Creation Checklist

- [ ] **FLEXT Integration**: Uses FlextResult for all error handling
- [ ] **Clean Architecture**: Proper layer placement and dependency direction
- [ ] **Type Safety**: Complete type annotations with generic support
- [ ] **Documentation**: Enterprise-grade docstrings with examples
- [ ] **Testing**: Comprehensive test coverage with realistic scenarios
- [ ] **Configuration**: Environment-aware settings with validation
- [ ] **Monitoring**: Observable operations with appropriate logging
- [ ] **Error Handling**: Consistent exception patterns with context

## Usage Examples

### Basic ETL Pipeline

```python
from gruponos_meltano_native import create_gruponos_meltano_platform

# Initialize ETL platform
platform = create_gruponos_meltano_platform()

# Execute full synchronization
result = await platform.execute_full_sync("GNOS", "DC01")
if result.success:
    print(f"ETL completed: {result.data.records_processed} records")
else:
    print(f"ETL failed: {result.error}")
```

### Configuration Management

```python
from gruponos_meltano_native.config import GruponosMeltanoSettings

# Load environment-aware configuration
settings = GruponosMeltanoSettings()
print(f"Environment: {settings.environment}")
print(f"Oracle WMS URL: {settings.oracle_wms.base_url}")
```

### Oracle Connection Management

```python
from gruponos_meltano_native import create_gruponos_meltano_oracle_manager

# Create connection manager
manager = create_gruponos_meltano_oracle_manager()

# Get database connection
connection_result = await manager.get_connection()
if connection_result.success:
    # Use connection for database operations
    conn = connection_result.data
```

## Integration with FLEXT Ecosystem

### Dependencies

- **flext-core**: Foundation patterns and utilities
- **flext-observability**: Monitoring and metrics collection
- **flext-db-oracle**: Oracle database connectivity and operations

### Standards Compliance

- **Naming**: GruponosMeltano prefix for all public APIs
- **Error Handling**: FlextResult railway-oriented programming
- **Configuration**: FlextBaseSettings with environment awareness
- **Testing**: FLEXT testing patterns and utilities

---

**Version**: 0.9.0  
**Framework**: FLEXT Ecosystem  
**Architecture**: Clean Architecture + Domain-Driven Design  
**Standards**: Enterprise-grade with 90% test coverage
