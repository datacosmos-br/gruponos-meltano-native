# GrupoNOS Meltano Native Module

**Enterprise ETL Pipeline Framework with FLEXT Integration**

This module provides a complete ETL pipeline implementation for Oracle WMS to Oracle Database data integration, built on FLEXT framework standards with Clean Architecture and railway-oriented programming patterns.

## Core Components

### Main Application Files

#### `__init__.py` - Public API Gateway
- **Purpose**: Centralized public API with factory functions
- **Pattern**: Direct FLEXT imports with no legacy wrappers
- **Exports**: All public classes, factory functions, and FLEXT components
- **Usage**: Primary entry point for all external integrations

```python
from gruponos_meltano_native import (
    create_gruponos_meltano_platform,
    GruponosMeltanoOrchestrator,
    GruponosMeltanoSettings
)
```

#### `cli.py` - Command-Line Interface
- **Framework**: Click with comprehensive command structure
- **Features**: Interactive and non-interactive execution modes
- **Integration**: Direct orchestrator integration with progress tracking
- **Commands**: sync, validate, config, status, version

```python
from gruponos_meltano_native.cli import gruponos_meltano_cli
```

#### `config.py` - Configuration Management
- **Framework**: Pydantic models with environment variable support
- **Validation**: Business rule validation with detailed error messages
- **Structure**: Hierarchical configuration with nested models
- **Security**: Secure credential handling with field exclusion

```python
from gruponos_meltano_native.config import (
    GruponosMeltanoSettings,
    GruponosMeltanoOracleConnectionConfig,
    GruponosMeltanoWMSSourceConfig
)
```

#### `orchestrator.py` - ETL Pipeline Orchestration
- **Pattern**: Railway-oriented programming with FlextResult
- **Architecture**: Clean Architecture with clear use case separation
- **Features**: Full sync, incremental sync, data validation, monitoring
- **Integration**: Singer/Meltano ecosystem coordination

```python
from gruponos_meltano_native.orchestrator import (
    GruponosMeltanoOrchestrator,
    create_gruponos_meltano_orchestrator
)
```

#### `exceptions.py` - Exception Hierarchy
- **Pattern**: Rich exception hierarchy with contextual information
- **Integration**: FLEXT standard exception patterns
- **Context**: Detailed error context for debugging and monitoring
- **Coverage**: Complete ETL pipeline error scenarios

```python
from gruponos_meltano_native.exceptions import (
    GruponosMeltanoError,
    GruponosMeltanoOracleConnectionError,
    GruponosMeltanoPipelineError
)
```

## Specialized Modules

### `infrastructure/` - Cross-Cutting Concerns
Enterprise infrastructure patterns for dependency injection and system integration.

#### `di_container.py` - Dependency Injection
- **Pattern**: FLEXT container integration with service location
- **Features**: Singleton management, lifecycle control, type safety
- **Usage**: Service registration and resolution throughout the application

### `monitoring/` - Observability and Alerting
Comprehensive monitoring solution with enterprise alerting capabilities.

#### `alert_manager.py` - Alert Management
- **Features**: Multi-channel alert delivery (email, Slack, webhooks)
- **Patterns**: Severity-based routing, rate limiting, retry mechanisms
- **Integration**: FLEXT observability standards with correlation IDs

### `oracle/` - Database Integration
Oracle database connectivity optimized for ETL operations.

#### `connection_manager_enhanced.py` - Connection Management
- **Features**: Connection pooling, health monitoring, failover handling
- **Performance**: Optimized for large data volume ETL operations
- **Integration**: FLEXT database abstraction layer compatibility

### `validators/` - Data Quality Assurance
Multi-layer data validation with business rule enforcement.

#### `data_validator.py` - Core Validation
- **Layers**: Schema validation, business rules, data quality checks
- **Pattern**: Railway-oriented validation chains with detailed error reporting
- **Features**: Configurable thresholds, performance monitoring

## Architecture Patterns

### Clean Architecture Implementation
```
┌─────────────────────────────────────┐
│        Presentation Layer           │  # cli.py
│     (CLI, External Interfaces)      │
├─────────────────────────────────────┤
│        Application Layer            │  # orchestrator.py
│   (ETL Orchestration, Use Cases)    │  # Pipeline coordination
├─────────────────────────────────────┤
│          Domain Layer               │  # Business logic embedded
│    (Business Rules, Entities)       │  # in orchestrator/validators
├─────────────────────────────────────┤
│       Infrastructure Layer          │  # infrastructure/, monitoring/
│  (Database, External Systems)       │  # oracle/, validators/
├─────────────────────────────────────┤
│         Foundation Layer            │  # config.py, exceptions.py
│   (Configuration, Cross-cutting)    │  # FLEXT integration
└─────────────────────────────────────┘
```

### Railway-Oriented Programming
```python
# ETL pipeline with error propagation
result = (
    await extract_wms_data(source_config)
    .flat_map_async(lambda data: validate_data_quality(data))
    .flat_map_async(lambda validated: transform_for_oracle(validated))
    .flat_map_async(lambda transformed: load_to_target(transformed))
    .map_async(lambda loaded: generate_completion_report(loaded))
)
```

## Integration Examples

### Basic ETL Execution
```python
from gruponos_meltano_native import create_gruponos_meltano_platform

# Create platform instance
platform = create_gruponos_meltano_platform()

# Execute full synchronization
result = await platform.execute_full_sync(
    company_code="GNOS",
    facility_code="DC01"
)

if result.is_success:
    print(f"Records processed: {result.data.records_processed}")
    print(f"Duration: {result.data.duration_seconds}s")
else:
    print(f"ETL failed: {result.error}")
```

### Configuration with Validation
```python
from gruponos_meltano_native.config import GruponosMeltanoSettings

# Load configuration with validation
settings = GruponosMeltanoSettings()

# Validate Oracle WMS connection
wms_validation = settings.oracle_wms.validate_connection()
if wms_validation.is_success:
    print("WMS connection validated successfully")
else:
    print(f"WMS validation failed: {wms_validation.error}")
```

### Custom Alert Configuration
```python
from gruponos_meltano_native.monitoring import create_gruponos_meltano_alert_manager

# Create alert manager with custom configuration
alert_config = GruponosMeltanoAlertConfig(
    email_enabled=True,
    slack_webhook_url="https://hooks.slack.com/...",
    severity_threshold="WARNING"
)

alert_manager = create_gruponos_meltano_alert_manager(alert_config)

# Send custom alert
await alert_manager.send_alert(
    title="ETL Pipeline Completed",
    message="Full sync completed successfully",
    severity=GruponosMeltanoAlertSeverity.INFO
)
```

## Development Standards

### Code Quality Requirements
- **Type Annotations**: 95%+ coverage with strict MyPy validation
- **Documentation**: Comprehensive docstrings with examples and integration notes
- **Testing**: 90% minimum test coverage across unit, integration, and E2E tests
- **Error Handling**: FlextResult patterns throughout with rich context

### FLEXT Integration Standards
- **Naming**: GruponosMeltano prefix for all public APIs
- **Error Handling**: Railway-oriented programming with FlextResult
- **Configuration**: FlextBaseSettings with environment awareness
- **Dependencies**: Use FLEXT ecosystem components consistently

### Testing Patterns
- **Unit Tests**: Fast, isolated tests for business logic
- **Integration Tests**: Real database and external system integration
- **E2E Tests**: Complete pipeline validation with monitoring
- **Performance Tests**: Load testing with enterprise data volumes

---

**Framework**: FLEXT Ecosystem v0.9.0  
**Architecture**: Clean Architecture + Domain-Driven Design  
**Testing**: 90% coverage with comprehensive validation  
**Documentation**: Enterprise-grade with practical examples