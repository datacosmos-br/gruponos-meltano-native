# Python Module Organization & Semantic Patterns

**GrupoNOS Meltano Native - ETL Pipeline Architecture & Best Practices**

**Built on FLEXT Core Foundation | Clean Architecture + Domain-Driven Design**

---

## 🏗️ **Module Architecture Overview**

GrupoNOS Meltano Native implements a **Clean Architecture ETL pipeline** that extends FLEXT Core patterns for enterprise data integration. This structure provides a scalable foundation for Oracle WMS to Oracle Database ETL operations with comprehensive monitoring and validation.

### **Core Design Principles**

1. **FLEXT Foundation**: Built on flext-core patterns with FlextResult railway-oriented programming
2. **Clean Architecture**: Clear separation between business logic, orchestration, and infrastructure
3. **Domain-Driven Design**: Rich domain models for Oracle WMS business entities
4. **ETL-Specific Patterns**: Specialized patterns for data extraction, transformation, and loading
5. **Enterprise Monitoring**: Comprehensive observability and alerting throughout the pipeline

---

## 📁 **Module Structure & Responsibilities**

### **Foundation Layer**

```python
# Core application foundation
src/gruponos_meltano_native/
├── __init__.py              # 🎯 Public API gateway
├── version.py               # 🎯 Version management
└── constants.py             # 🎯 Application constants
```

**Responsibility**: Establish the foundational contracts and version management for the ETL application.

**Import Pattern**:

```python
# Standard application imports
from gruponos_meltano_native import __version__
from gruponos_meltano_native.config import create_gruponos_meltano_settings
from gruponos_meltano_native.orchestrator import GruponosMeltanoOrchestrator
```

### **Configuration & Settings Layer**

```python
# Configuration management with FLEXT integration
├── config.py                # ⚙️ Pydantic settings with FLEXT patterns
```

**Responsibility**: Handle application configuration using FLEXT BaseSettings patterns with ETL-specific validation.

**Configuration Pattern**:

```python
from flext_core import FlextConfig, FlextResult
from gruponos_meltano_native.config import GruponosMeltanoSettings

# Environment-aware configuration
settings = create_gruponos_meltano_settings()
assert settings.app_name == "gruponos-meltano-native"
assert settings.version == "0.9.9"

# Oracle WMS configuration with validation
wms_config = settings.oracle_wms
validation_result = wms_config.validate_connection()
assert validation_result.success
```

### **Domain Layer (Business Logic)**

```python
# ETL domain models and business rules
├── models/                  # 🏛️ Domain entities and value objects
│   ├── __init__.py         # Domain model exports
│   ├── allocation.py       # WMS allocation entity
│   ├── order_header.py     # Order header entity
│   ├── order_detail.py     # Order detail entity
│   └── base.py             # Base domain patterns
```

**Responsibility**: Define rich domain models for Oracle WMS business entities with validation and business rules.

**Domain Modeling Pattern**:

```python
from flext_core import FlextModels.Entity, FlextResult
from gruponos_meltano_native.models import WMSAllocation, OrderHeader

class WMSAllocation(FlextModels.Entity):
    """WMS allocation entity with business rules."""
    allocation_id: str
    item_code: str
    quantity: int
    facility_code: str
    location: str

    def validate_allocation_rules(self) -> FlextResult[None]:
        """Apply WMS business rules for allocation validation."""
        if self.quantity <= 0:
            return FlextResult[None].fail("Allocation quantity must be positive")

        if not self.facility_code:
            return FlextResult[None].fail("Facility code is required")

        return FlextResult[None].ok(None)

    def transform_for_target(self) -> FlextTypes.Dict:
        """Transform allocation for target database format."""
        return {
            "ALLOCATION_ID": self.allocation_id,
            "ITEM_CODE": self.item_code,
            "QTY": self.quantity,
            "FACILITY": self.facility_code,
            "LOC": self.location,
            "LOAD_TIMESTAMP": datetime.utcnow()
        }
```

### **Application Service Layer**

```python
# Application orchestration and use cases
├── orchestrator.py          # 📤 Main ETL orchestration service
├── cli.py                   # 📤 Command-line interface
```

**Responsibility**: Coordinate ETL workflows, handle Meltano integration, and provide user interfaces.

**Orchestration Pattern**:

```python
from flext_core import FlextResult
from gruponos_meltano_native.orchestrator import GruponosMeltanoOrchestrator

class GruponosMeltanoOrchestrator:
    """Main ETL pipeline orchestrator with FLEXT patterns."""

    def execute_full_sync(
        self,
        company_code: str,
        facility_code: str
    ) -> FlextResult[PipelineResult]:
        """Execute full synchronization pipeline."""
        return (
            self._validate_environment()
            .flat_map(lambda _: self._extract_wms_data(company_code, facility_code))
            .flat_map(lambda data: self._transform_data(data))
            .flat_map(lambda transformed: self._load_to_oracle(transformed))
            .map(lambda result: self._generate_pipeline_report(result))
        )
```

### **Infrastructure Layer**

```python
# External system integrations
├── oracle/                  # 🔧 Oracle database connectivity
│   ├── __init__.py         # Oracle integration exports
│   ├── connection.py       # Connection management
│   └── repository.py       # Data access patterns
├── monitoring/              # 🔧 Monitoring and alerting
│   ├── __init__.py         # Monitoring exports
│   ├── alert_manager.py    # Alert delivery system
│   └── metrics.py          # Performance metrics
└── infrastructure/          # 🔧 Cross-cutting infrastructure
    ├── __init__.py         # Infrastructure exports
    └── di_container.py     # Dependency injection
```

**Responsibility**: Handle external system integration, monitoring, and cross-cutting infrastructure concerns.

**Infrastructure Pattern**:

```python
from flext_core import FlextResult
from flext_db_oracle import FlextDbOracleApi
from gruponos_meltano_native.oracle import create_gruponos_meltano_oracle_connection_manager

# Oracle integration with FLEXT patterns
def create_oracle_repository(config: OracleConnectionConfig) -> FlextResult[OracleRepository]:
    """Create Oracle repository with connection management."""
    return (
        FlextResult[None].ok(config)
        .flat_map(lambda cfg: validate_oracle_config(cfg))
        .map(lambda cfg: create_gruponos_meltano_oracle_connection_manager(cfg))
        .map(lambda manager: OracleRepository(manager))
    )
```

### **Validation Layer**

```python
# Data validation and quality assurance
├── validators/              # 📋 Data validation components
│   ├── __init__.py         # Validator exports
│   ├── data_validator.py   # Core data validation
│   └── schema_validator.py # Schema validation
```

**Responsibility**: Ensure data quality and compliance with business rules throughout the ETL pipeline.

**Validation Pattern**:

```python
from flext_core import FlextResult
from gruponos_meltano_native.validators import DataValidator, ValidationRules

class WMSDataValidator(DataValidator):
    """WMS-specific data validation with FLEXT patterns."""

    def validate_allocation_data(
        self,
        data: List[dict]
    ) -> FlextResult[List[dict]]:
        """Validate allocation data with business rules."""
        return (
            self._validate_schema(data, AllocationSchema)
            .flat_map(lambda validated: self._validate_business_rules(validated))
            .flat_map(lambda clean_data: self._validate_data_quality(clean_data))
        )

    def _validate_business_rules(self, data: List[dict]) -> FlextResult[List[dict]]:
        """Apply WMS business validation rules."""
        validation_errors = []
        validated_data = []

        for record in data:
            if record.get('quantity', 0) <= 0:
                validation_errors.append(f"Invalid quantity in record {record.get('id')}")
                continue

            if not record.get('facility_code'):
                validation_errors.append(f"Missing facility code in record {record.get('id')}")
                continue

            validated_data.append(record)

        if validation_errors:
            return FlextResult[None].fail(f"Validation errors: {'; '.join(validation_errors)}")

        return FlextResult[None].ok(validated_data)
```

### **Exception Handling Layer**

```python
# Domain-specific exception hierarchy
├── exceptions.py            # 🚨 Complete exception hierarchy
```

**Responsibility**: Provide comprehensive exception handling with detailed context for ETL operations.

**Exception Pattern**:

```python
from gruponos_meltano_native.exceptions import (
    GruponosMeltanoError,
    GruponosMeltanoOracleConnectionError,
    GruponosMeltanoPipelineError,
    GruponosMeltanoDataValidationError
)

# Exception usage in ETL operations
def extract_wms_data(config: WMSConfig) -> FlextResult[List[dict]]:
    """Extract data from Oracle WMS with proper exception handling."""
    try:
        # WMS extraction logic
        return FlextResult[None].ok(extracted_data)
    except ConnectionError as e:
        error = GruponosMeltanoOracleConnectionError(
            "Failed to connect to Oracle WMS",
            error_code="WMS_CONN_001",
            context={
                "host": config.host,
                "port": config.port,
                "company_code": config.company_code
            }
        )
        return FlextResult[None].fail(str(error))
```

---

## 🎯 **Semantic Naming Conventions**

### **Module-Level Naming**

```python
# ETL-specific module naming patterns
config.py                   # Application configuration with Pydantic models
orchestrator.py             # Main ETL pipeline orchestration
cli.py                      # Command-line interface with Click
models/allocation.py        # WMS allocation domain entity
models/order_header.py      # Order header domain entity
validators/data_validator.py # Data validation components
oracle/connection.py        # Oracle database connectivity
monitoring/alert_manager.py # Alert delivery and management
exceptions.py               # Domain-specific exception hierarchy
```

**Pattern**: Clear, descriptive names that reflect ETL domain concepts and responsibilities.

### **Class Naming Conventions**

```python
# Domain entities follow business terminology
class WMSAllocation(FlextModels.Entity):           # Business entity from WMS domain
class OrderHeader(FlextModels.Entity):             # Order management entity
class AllocationPerformance(FlextModels.Entity):   # Performance tracking entity

# Service classes use descriptive names
class GruponosMeltanoOrchestrator:          # Main pipeline orchestrator
class OracleConnectionManager:              # Database connection management
class WMSDataValidator:                     # Data validation service
class AlertManager:                         # Monitoring and alerting

# Configuration classes reflect their scope
class GruponosMeltanoSettings:              # Application-wide settings
class OracleWMSSourceConfig:                # WMS source configuration
class OracleTargetConfig:                   # Target database configuration
```

### **Function and Method Naming**

```python
# ETL operation naming patterns
def extract_wms_allocations() -> FlextResult[List[WMSAllocation]]:
    """Extract allocation data from Oracle WMS."""

def transform_allocation_data() -> FlextResult[List[dict]]:
    """Transform WMS data for target database format."""

def load_to_oracle_target() -> FlextResult[LoadResult]:
    """Load transformed data to Oracle target database."""

def validate_data_quality() -> FlextResult[ValidationReport]:
    """Validate data quality against business rules."""

def execute_full_sync_pipeline() -> FlextResult[PipelineResult]:
    """Execute complete ETL pipeline with monitoring."""

# Configuration and setup methods
def create_gruponos_meltano_settings() -> GruponosMeltanoSettings:
    """Factory function for application settings."""

def create_oracle_connection_manager() -> OracleConnectionManager:
    """Factory function for Oracle connection management."""
```

---

## 📦 **Import Patterns & Best Practices**

### **Recommended Import Styles**

#### **1. FLEXT Foundation Imports**

```python
# Core FLEXT patterns - always import these first
from flext_core import FlextResult, FlextConfig, FlextLogger
from flext_observability import FlextMonitoringService
from flext_db_oracle import FlextDbOracleApi, FlextDbOracleConfig

# Application domain imports
from gruponos_meltano_native import __version__
from gruponos_meltano_native.config import (
    create_gruponos_meltano_settings,
    GruponosMeltanoSettings,
    OracleWMSSourceConfig,
    OracleTargetConfig
)
```

#### **2. Domain Model Imports**

```python
# Domain entities and value objects
from gruponos_meltano_native.models import (
    WMSAllocation,
    OrderHeader,
    OrderDetail,
    AllocationPerformance
)

# Domain services and validation
from gruponos_meltano_native.validators import (
    WMSDataValidator,
    ValidationRules,
    DataQualityChecker
)
```

#### **3. Infrastructure Imports**

```python
# Infrastructure and external integrations
from gruponos_meltano_native.oracle import (
    create_gruponos_meltano_oracle_connection_manager,
    OracleConnectionManager,
    OracleRepository
)

from gruponos_meltano_native.monitoring import (
    AlertManager,
    MetricsCollector,
    PerformanceTracker
)
```

#### **4. Application Service Imports**

```python
# Application orchestration and CLI
from gruponos_meltano_native.orchestrator import GruponosMeltanoOrchestrator
from gruponos_meltano_native.cli import create_cli_app

# Exception handling
from gruponos_meltano_native.exceptions import (
    GruponosMeltanoError,
    GruponosMeltanoOracleConnectionError,
    GruponosMeltanoPipelineError,
    GruponosMeltanoDataValidationError
)
```

### **Anti-Patterns (Forbidden)**

```python
# ❌ Don't import everything
from gruponos_meltano_native import *

# ❌ Don't use deep imports for internal modules
from gruponos_meltano_native.oracle.connection._internal import PrivateConnection

# ❌ Don't import test modules in production code
from gruponos_meltano_native.tests.fixtures import test_data

# ❌ Don't alias core types confusingly
from flext_core import FlextResult as Result  # Breaks FLEXT ecosystem consistency

# ❌ Don't import Meltano internals directly
from meltano.core.project import Project  # Use orchestrator abstraction instead
```

---

## 🏛️ **Clean Architecture Layers**

### **Layer Separation**

```python
# Clean Architecture with ETL specialization
┌─────────────────────────────────────┐
│        Presentation Layer           │  # cli.py
│     (CLI, API endpoints)            │
├─────────────────────────────────────┤
│        Application Layer            │  # orchestrator.py
│   (ETL Orchestration, Use Cases)    │  # Pipeline coordination
├─────────────────────────────────────┤
│          Domain Layer               │  # models/
│    (Business Logic, Entities)       │  # WMS business rules
├─────────────────────────────────────┤
│       Infrastructure Layer          │  # oracle/, monitoring/
│  (Database, External APIs, I/O)     │  # validators/, infrastructure/
├─────────────────────────────────────┤
│         Foundation Layer            │  # config.py, exceptions.py
│   (Configuration, Cross-cutting)    │  # FLEXT integration
└─────────────────────────────────────┘
```

### **Dependency Direction**

```python
# Dependencies flow inward (Clean Architecture principle)
CLI  →  Orchestrator  →  Domain Models  →  Foundation
 ↓         ↓              ↓                 ↓
Infrastructure  →  Validators  →  Configuration  (OK)
```

**Rule**: Higher layers depend on lower layers, never the reverse. Infrastructure adapts to domain needs.

---

## 🔄 **ETL-Specific Patterns**

### **Pipeline Orchestration Pattern**

```python
from flext_core import FlextResult
from typing import List, Dict

def execute_etl_pipeline(
    source_config: OracleWMSSourceConfig,
    target_config: OracleTargetConfig
) -> FlextResult[PipelineResult]:
    """ETL pipeline with railway-oriented programming."""

    return (
        extract_from_source(source_config)
        .flat_map(lambda data: validate_extracted_data(data))
        .flat_map(lambda validated: transform_data(validated))
        .flat_map(lambda transformed: validate_transformed_data(transformed))
        .flat_map(lambda final_data: load_to_target(final_data, target_config))
        .map(lambda result: generate_pipeline_metrics(result))
    )
```

### **Data Validation Chain Pattern**

```python
def validate_wms_data_pipeline(data: List[dict]) -> FlextResult[List[dict]]:
    """Comprehensive data validation chain."""

    return (
        validate_schema(data)
        .flat_map(lambda schema_valid: validate_business_rules(schema_valid))
        .flat_map(lambda business_valid: validate_data_quality(business_valid))
        .flat_map(lambda quality_valid: validate_referential_integrity(quality_valid))
        .map(lambda final_valid: enrich_with_metadata(final_valid))
    )
```

### **Connection Management Pattern**

```python
from contextlib import contextmanager
from flext_core import FlextResult

@contextmanager
def oracle_connection_context(config: OracleConnectionConfig):
    """Managed Oracle connection with proper cleanup."""

    connection_result = create_oracle_connection(config)
    if connection_result.is_failure:
        raise GruponosMeltanoOracleConnectionError(
            f"Failed to establish connection: {connection_result.error}"
        )

    connection = connection_result.data
    try:
        yield connection
    finally:
        connection.close()

# Usage in ETL operations
def load_allocation_data(data: List[dict]) -> FlextResult[LoadResult]:
    with oracle_connection_context(target_config) as conn:
        return conn.bulk_insert('WMS_ALLOCATIONS', data)
```

---

## 🧪 **Testing Patterns**

### **Test Organization**

```python
# Test structure mirrors source structure
tests/
├── unit/                    # Unit tests (isolated, fast)
│   ├── test_config.py      # Configuration tests
│   ├── test_orchestrator.py # Orchestrator unit tests
│   ├── test_models/        # Domain model tests
│   │   ├── test_allocation.py
│   │   └── test_order_header.py
│   ├── test_validators/    # Validation tests
│   │   └── test_data_validator.py
│   └── test_exceptions.py  # Exception hierarchy tests
├── integration/            # Integration tests (real connections)
│   ├── test_oracle_integration.py
│   ├── test_wms_integration.py
│   └── test_end_to_end_pipeline.py
├── performance/            # Performance and load tests
│   ├── test_pipeline_performance.py
│   └── test_data_volume_limits.py
└── conftest.py            # Test configuration and fixtures
```

### **ETL Testing Patterns**

```python
import pytest
from flext_core import FlextResult
from gruponos_meltano_native.orchestrator import GruponosMeltanoOrchestrator
from gruponos_meltano_native.models import WMSAllocation

class TestETLPipeline:
    """Test ETL pipeline operations with FLEXT patterns."""

    def test_successful_allocation_extraction(self):
        """Test successful data extraction from WMS."""
        orchestrator = GruponosMeltanoOrchestrator()

        result = orchestrator.extract_wms_allocations(
            company_code="TEST",
            facility_code="DC01"
        )

        assert result.success
        assert isinstance(result.data, list)
        assert all(isinstance(item, WMSAllocation) for item in result.data)

    def test_pipeline_failure_handling(self):
        """Test pipeline failure propagation."""
        orchestrator = GruponosMeltanoOrchestrator()

        # Simulate connection failure
        result = orchestrator.execute_full_sync(
            company_code="INVALID",
            facility_code="NONE"
        )

        assert result.is_failure
        assert "connection" in result.error.lower()

    def test_data_validation_chain(self):
        """Test complete data validation workflow."""
        test_data = [
            {"allocation_id": "A001", "quantity": 100, "facility_code": "DC01"},
            {"allocation_id": "A002", "quantity": -5, "facility_code": "DC01"},  # Invalid
            {"allocation_id": "A003", "quantity": 50, "facility_code": ""},      # Invalid
        ]

        validator = WMSDataValidator()
        result = validator.validate_allocation_data(test_data)

        assert result.is_failure  # Should fail due to invalid records
        assert "quantity" in result.error
        assert "facility" in result.error

@pytest.fixture
def mock_wms_data():
    """Provide test WMS data for validation tests."""
    return [
        {
            "allocation_id": "TEST001",
            "item_code": "ITEM001",
            "quantity": 100,
            "facility_code": "DC01",
            "location": "A1-B2-C3"
        }
    ]
```

---

## 📏 **Code Quality Standards**

### **Type Annotation Requirements**

```python
# ✅ Complete type annotations for ETL operations
from typing import List, Dict, Optional, Union

from flext_core import FlextResult

def extract_wms_allocations(
    company_code: str,
    facility_code: str,
    start_date: Optional[datetime] = None
) -> FlextResult[List[WMSAllocation]]:
    """Extract WMS allocations with complete type safety."""
    # Implementation with full type checking
    pass

def transform_allocation_data(
    allocations: List[WMSAllocation]
) -> FlextResult[List[FlextTypes.Dict]]:
    """Transform allocations for target database format."""
    # Implementation with type validation
    pass

# ✅ Generic type usage for reusable patterns
T = TypeVar('T')
U = TypeVar('U')

def validate_and_transform(
    data: List[T],
    validator: Callable[[List[T]], FlextResult[List[T]]],
    transformer: Callable[[List[T]], FlextResult[List[U]]]
) -> FlextResult[List[U]]:
    """Generic validation and transformation pattern."""
    return (
        validator(data)
        .flat_map(lambda validated: transformer(validated))
    )
```

### **Error Handling Standards**

```python
# ✅ Always use FlextResult for ETL operations
def extract_wms_data(config: WMSConfig) -> FlextResult[List[dict]]:
    """Extract data with comprehensive error handling."""
    try:
        # WMS API call
        response = wms_client.get_allocations(config)
        if response.status != 200:
            return FlextResult[None].fail(f"WMS API error: {response.status}")

        return FlextResult[None].ok(response.data)

    except ConnectionError as e:
        return FlextResult[None].fail(f"WMS connection failed: {str(e)}")
    except TimeoutError as e:
        return FlextResult[None].fail(f"WMS request timeout: {str(e)}")
    except Exception as e:
        return FlextResult[None].fail(f"Unexpected WMS error: {str(e)}")

# ✅ Chain ETL operations safely
def execute_etl_step(
    source_config: WMSConfig,
    target_config: OracleConfig
) -> FlextResult[PipelineResult]:
    """Execute ETL step with error propagation."""
    return (
        extract_wms_data(source_config)
        .flat_map(lambda data: validate_data_quality(data))
        .flat_map(lambda validated: transform_for_oracle(validated))
        .flat_map(lambda transformed: load_to_oracle(transformed, target_config))
    )
```

### **Documentation Standards**

```python
def execute_incremental_sync(
    company_code: str,
    facility_code: str,
    last_sync_timestamp: datetime,
    batch_size: int = 1000
) -> FlextResult[IncrementalSyncResult]:
    """
    Execute incremental synchronization from Oracle WMS to target database.

    This method implements incremental data synchronization using the mod_ts
    replication key to identify changed records since the last sync. It follows
    the FLEXT railway-oriented programming pattern for consistent error handling
    throughout the ETL pipeline.

    The synchronization process includes:
    1. Extract changed records from Oracle WMS since last_sync_timestamp
    2. Validate data quality and business rules
    3. Transform data for target Oracle database schema
    4. Load data using upsert operations
    5. Update synchronization metadata

    Args:
        company_code: WMS company identifier for data isolation
        facility_code: WMS facility identifier for location-specific data
        last_sync_timestamp: Timestamp of last successful synchronization
        batch_size: Number of records to process in each batch (default: 1000)

    Returns:
        FlextResult[IncrementalSyncResult]: Success contains sync statistics
        including records processed, errors encountered, and performance metrics.
        Failure contains detailed error information for troubleshooting.

    Raises:
        GruponosMeltanoOracleConnectionError: When WMS or target DB connection fails
        GruponosMeltanoPipelineTimeoutError: When sync exceeds configured timeout
        GruponosMeltanoDataValidationError: When data quality validation fails

    Example:
        >>> from datetime import datetime, timedelta
        >>> last_sync = datetime.utcnow() - timedelta(hours=2)
        >>> result = execute_incremental_sync("GNOS", "DC01", last_sync)
        >>> if result.success:
        ...     print(f"Synced {result.data.records_processed} records")
        ... else:
        ...     logger.error(f"Sync failed: {result.error}")
    """
    # Implementation follows documented pattern
    pass
```

---

## 🌐 **FLEXT Ecosystem Integration**

### **FLEXT Dependencies Integration**

```python
# ✅ Standard FLEXT ecosystem imports
from flext_core import FlextResult, FlextConfig, FlextLogger
from flext_observability import FlextMonitoringService, FlextMetricsCollector
from flext_db_oracle import FlextDbOracleApi, FlextDbOracleConfig

# ✅ Consistent error handling across FLEXT projects
def sync_with_flext_patterns(
    source_config: WMSConfig,
    target_config: OracleConfig
) -> FlextResult[SyncResult]:
    """Synchronization using consistent FLEXT patterns."""

    # Initialize FLEXT services
    logger = FlextLogger(__name__)
    monitoring = FlextMonitoringService()

    return (
        extract_wms_data(source_config)
        .map(lambda data: monitoring.track_extraction_metrics(data))
        .flat_map(lambda data: validate_with_flext_patterns(data))
        .flat_map(lambda validated: load_with_oracle_flext_api(validated, target_config))
        .map(lambda result: monitoring.track_completion_metrics(result))
    )
```

### **Configuration Integration**

```python
# ✅ Extend FlextConfig for all configuration
from flext_core import FlextConfig

class GruponosMeltanoSettings(FlextConfig):
    """GrupoNOS Meltano Native configuration with FLEXT patterns."""

    # Application metadata
    app_name: str = "gruponos-meltano-native"
    version: str = "0.9.9"
    environment: str = "dev"

    # FLEXT integration settings
    enable_monitoring: bool = True
    enable_metrics: bool = True
    log_level: str = "INFO"

    # ETL-specific configuration
    oracle_wms: OracleWMSSourceConfig = Field(default_factory=OracleWMSSourceConfig)
    oracle_target: OracleTargetConfig = Field(default_factory=OracleTargetConfig)
    pipeline: PipelineConfig = Field(default_factory=PipelineConfig)

    class Config:
        env_prefix = "GRUPONOS_"
        env_nested_delimiter = "__"

def create_gruponos_meltano_settings() -> GruponosMeltanoSettings:
    """Factory function for application settings with FLEXT integration."""
    return GruponosMeltanoSettings()
```

---

## 📋 **ETL Module Checklist**

### **Module Creation Checklist**

- [ ] **FLEXT Integration**: Uses FlextResult for all error handling
- [ ] **Clean Architecture**: Proper layer separation and dependency direction
- [ ] **Type Safety**: Complete type annotations with MyPy compliance
- [ ] **Domain Modeling**: Rich business entities with validation rules
- [ ] **Error Handling**: Comprehensive exception hierarchy with context
- [ ] **Documentation**: Complete docstrings with ETL-specific examples
- [ ] **Testing**: Unit, integration, and performance tests (90% coverage)
- [ ] **Configuration**: Environment-aware settings with validation
- [ ] **Monitoring**: Observable operations with metrics and alerts
- [ ] **Data Quality**: Validation rules and quality checks

### **ETL Quality Gates**

- [ ] **Pipeline Testing**: End-to-end pipeline validation
- [ ] **Data Validation**: Schema and business rule validation
- [ ] **Performance Testing**: Load testing with realistic data volumes
- [ ] **Error Recovery**: Graceful handling of connection failures
- [ ] **Monitoring Integration**: Comprehensive observability
- [ ] **Configuration Validation**: Environment-specific validation
- [ ] **Security Compliance**: Secure credential management
- [ ] **Documentation**: Complete API and workflow documentation

---

**Last Updated**: August 4, 2025  
**Target Audience**: GrupoNOS ETL developers and FLEXT ecosystem contributors  
**Scope**: Python module organization for enterprise ETL pipelines  
**Framework**: FLEXT Ecosystem v0.9.9 | Clean Architecture + Domain-Driven Design
