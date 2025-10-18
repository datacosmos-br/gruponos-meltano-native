# API Reference
## Table of Contents

- [API Reference](#api-reference)
  - [Core API Components](#core-api-components)
    - [🎯 Primary APIs](#-primary-apis)
    - [🔧 Integration APIs](#-integration-apis)
  - [Orchestrator API](#orchestrator-api)
    - [GruponosMeltanoOrchestrator](#gruponosmeltanoorchestrator)
    - [PipelineResult](#pipelineresult)
  - [Configuration API](#configuration-api)
    - [GruponosMeltanoSettings](#gruponosmeltanosettings)
    - [Configuration Factory Functions](#configuration-factory-functions)
  - [CLI API](#cli-api)
    - [Command-Line Interface](#command-line-interface)
    - [CLI Usage Examples](#cli-usage-examples)
- [Basic pipeline execution](#basic-pipeline-execution)
- [Development mode with debug logging](#development-mode-with-debug-logging)
- [Production environment with specific configuration](#production-environment-with-specific-configuration)
- [Complete system validation](#complete-system-validation)
- [Comprehensive diagnostics](#comprehensive-diagnostics)
  - [Monitoring API](#monitoring-api)
    - [Alert Manager](#alert-manager)
    - [Metrics Collection](#metrics-collection)
  - [Oracle WMS API](#oracle-wms-api)
    - [Connection Manager](#connection-manager)
  - [Data Validation API](#data-validation-api)
    - [Validator Classes](#validator-classes)
  - [Exception Handling](#exception-handling)
    - [Exception Hierarchy](#exception-hierarchy)
- [Base exception](#base-exception)
- [Specific exceptions](#specific-exceptions)
    - [Error Handling Patterns](#error-handling-patterns)
  - [Factory Functions](#factory-functions)
    - [Main Factory Functions](#main-factory-functions)


**GrupoNOS Meltano Native API Documentation** - Complete reference for all public APIs,
     configuration options, and integration patterns.

## Core API Components

### 🎯 Primary APIs

- **[Orchestrator API](#orchestrator-api)** - Main pipeline orchestration interface
- **[Configuration API](#configuration-api)** - Settings and environment management
- **[CLI API](#cli-api)** - Command-line interface operations
- **[Monitoring API](#monitoring-api)** - Observability and alerting

### 🔧 Integration APIs

- **[Oracle WMS API](#oracle-wms-api)** - Oracle WMS connection management
- **[Data Validation API](#data-validation-api)** - Business rule validation
- **[Exception Handling](#exception-handling)** - Error management patterns

---

## Orchestrator API

### GruponosMeltanoOrchestrator

Main orchestration class for executing ETL pipelines.

```python
from gruponos_meltano_native import GruponosMeltanoOrchestrator
from flext_core import FlextResult

class GruponosMeltanoOrchestrator:
    """Main pipeline orchestration interface following FLEXT patterns"""

    def __init__(self, settings: GruponosMeltanoSettings) -> None:
        """Initialize orchestrator with configuration"""

    def execute_full_sync(
        self,
        company_code: str,
        facility_code: str,
        enable_monitoring: bool = True,
        dry_run: bool = False
    ) -> FlextResult[PipelineResult]:
        """Execute complete data synchronization

        Args:
            company_code: Oracle WMS company identifier
            facility_code: Oracle WMS facility identifier
            enable_monitoring: Enable metrics and tracing
            dry_run: Execute without actual data changes

        Returns:
            FlextResult containing pipeline execution results

        Raises:
            GruponosMeltanoConnectionError: Oracle WMS/DB connection failed
            GruponosMeltanoProcessingError: Pipeline execution failed
        """

    def execute_incremental_sync(
        self,
        company_code: str,
        facility_code: str,
        since_timestamp: datetime,
        enable_monitoring: bool = True
    ) -> FlextResult[PipelineResult]:
        """Execute incremental data synchronization

        Args:
            company_code: Oracle WMS company identifier
            facility_code: Oracle WMS facility identifier
            since_timestamp: Extract changes since this timestamp
            enable_monitoring: Enable metrics and tracing

        Returns:
            FlextResult containing incremental sync results
        """

    def validate_pipeline_health(self) -> FlextResult[HealthCheckResult]:
        """Validate complete pipeline health

        Returns:
            FlextResult containing health check status for all components
        """
```

### PipelineResult

Pipeline execution result data model.

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, List, Optional

class PipelineResult(BaseModel):
    """Pipeline execution result following FLEXT result patterns"""

    pipeline_name: str
    execution_id: str
    start_time: datetime
    end_time: datetime
    duration_seconds: float

    # Data processing metrics
    records_extracted: int
    records_transformed: int
    records_loaded: int
    records_failed: int

    # Business metrics
    companies_processed: List[str]
    facilities_processed: List[str]
    entities_processed: List[str]

    # Quality metrics
    data_quality_score: float
    validation_errors: List[str]

    # Performance metrics
    avg_records_per_second: float
    peak_memory_usage_mb: float

    # Execution summary
    success: bool
    summary: str
    error_message: Optional[str] = None

class HealthCheckResult(BaseModel):
    """Pipeline health check result"""

    overall_health: str  # "healthy", "warning", "critical"
    oracle_wms_status: str
    oracle_db_status: str
    meltano_status: str

    health_checks: Dict[str, bool]
    warnings: List[str]
    errors: List[str]

    last_successful_sync: Optional[datetime]
    next_scheduled_sync: Optional[datetime]
```

---

## Configuration API

### GruponosMeltanoSettings

Main configuration class extending FLEXT base settings.

```python
from flext_core import FlextConfig
from pydantic import Field, SecretStr, validator
from typing import List, Optional

class GruponosMeltanoSettings(FlextConfig):
    """GrupoNOS Meltano configuration extending FLEXT base settings"""

    # FLEXT Core Settings (inherited)
    environment: str = Field(env="FLEXT_ENVIRONMENT", default="dev")
    log_level: str = Field(env="FLEXT_LOG_LEVEL", default="INFO")
    enable_metrics: bool = Field(env="FLEXT_ENABLE_METRICS", default=True)
    enable_tracing: bool = Field(env="FLEXT_ENABLE_TRACING", default=True)

    # Oracle WMS Configuration
    wms_base_url: str = Field(..., env="TAP_ORACLE_WMS_BASE_URL")
    wms_username: str = Field(..., env="TAP_ORACLE_WMS_USERNAME")
    wms_password: SecretStr = Field(..., env="TAP_ORACLE_WMS_PASSWORD")
    wms_company_code: str = Field(..., env="TAP_ORACLE_WMS_COMPANY_CODE")
    wms_facility_code: str = Field(..., env="TAP_ORACLE_WMS_FACILITY_CODE")
    wms_timeout: int = Field(300, env="TAP_ORACLE_WMS_TIMEOUT")
    wms_batch_size: int = Field(10000, env="TAP_ORACLE_WMS_BATCH_SIZE")

    # Oracle Target Database Configuration
    oracle_host: str = Field(..., env="FLEXT_TARGET_ORACLE_HOST")
    oracle_port: int = Field(1521, env="FLEXT_TARGET_ORACLE_PORT")
    oracle_service_name: str = Field(..., env="FLEXT_TARGET_ORACLE_SERVICE_NAME")
    oracle_username: str = Field(..., env="FLEXT_TARGET_ORACLE_USERNAME")
    oracle_password: SecretStr = Field(..., env="FLEXT_TARGET_ORACLE_PASSWORD")
    oracle_protocol: str = Field("tcp", env="FLEXT_TARGET_ORACLE_PROTOCOL")
    oracle_schema: str = Field(..., env="FLEXT_TARGET_ORACLE_SCHEMA")

    # Pipeline Configuration
    entities: List[str] = Field(
        default=["allocation", "order_hdr", "order_dtl"],
        env="TAP_ORACLE_WMS_ENTITIES"
    )
    enable_incremental: bool = Field(True, env="TAP_ORACLE_WMS_ENABLE_INCREMENTAL")
    replication_key: str = Field("mod_ts", env="TAP_ORACLE_WMS_REPLICATION_KEY")
    page_size: int = Field(500, env="TAP_ORACLE_WMS_PAGE_SIZE")
    max_retries: int = Field(3, env="TAP_ORACLE_WMS_MAX_RETRIES")

    # Data Quality Configuration
    enable_validation: bool = Field(True, env="GRUPONOS_ENABLE_VALIDATION")
    validation_threshold: float = Field(0.95, env="GRUPONOS_VALIDATION_THRESHOLD")

    @validator("wms_base_url")
    def validate_wms_url(cls, v: str) -> str:
        """Validate Oracle WMS base URL format"""
        if not v.startswith(("http://", "https://")):
            raise ValueError("WMS base URL must start with http:// or https://")
        return v

    @validator("oracle_protocol")
    def validate_oracle_protocol(cls, v: str) -> str:
        """Validate Oracle connection protocol"""
        if v not in ["tcp", "tcps"]:
            raise ValueError("Oracle protocol must be 'tcp' or 'tcps'")
        return v

    class Config:
        env_prefix = "GRUPONOS_"
        case_sensitive = False
        validate_assignment = True
        use_enum_values = True
```

### Configuration Factory Functions

```python
def create_gruponos_meltano_settings(
    environment: Optional[str] = None,
    config_file: Optional[Path] = None
) -> GruponosMeltanoSettings:
    """Create GrupoNOS Meltano settings with environment overrides

    Args:
        environment: Target environment (dev, staging, prod)
        config_file: Optional YAML configuration file

    Returns:
        Configured GruponosMeltanoSettings instance
    """

def load_settings_from_yaml(config_path: Path) -> GruponosMeltanoSettings:
    """Load settings from YAML configuration file

    Args:
        config_path: Path to YAML configuration file

    Returns:
        GruponosMeltanoSettings loaded from file

    Raises:
        GruponosMeltanoConfigurationError: Invalid configuration file
    """
```

---

## CLI API

### Command-Line Interface

```python
import click
from gruponos_meltano_native.cli import cli

@click.group()
@click.option("--environment", "-e", default="dev", help="Target environment")
@click.option("--config", "-c", type=click.Path(exists=True), help="Configuration file")
@click.option("--debug", is_flag=True, help="Enable debug logging")
@click.pass_context
def cli(ctx: click.Context, environment: str, config: str, debug: bool) -> None:
    """GrupoNOS Meltano Native CLI - Oracle WMS ETL Pipeline Management"""

@cli.command()
@click.option("--job", "-j", help="Specific job to execute")
@click.option("--dry-run", is_flag=True, help="Execute without data changes")
@click.option("--monitoring/--no-monitoring", default=True, help="Enable monitoring")
@click.pass_context
def run(ctx: click.Context, job: str, dry_run: bool, monitoring: bool) -> None:
    """Execute ETL pipeline jobs

    Examples:
        gruponos-meltano run --job full-sync-job
        gruponos-meltano run --job incremental-sync-job --dry-run
    """

@cli.command()
@click.option("--include-oracle-health", is_flag=True, help="Include Oracle health checks")
@click.option("--include-meltano-test", is_flag=True, help="Include Meltano tests")
@click.pass_context
def validate(ctx: click.Context, include_oracle_health: bool, include_meltano_test: bool) -> None:
    """Validate configuration and system health

    Examples:
        gruponos-meltano validate --include-oracle-health
        gruponos-meltano validate --include-meltano-test
    """

@cli.command()
@click.option("--include-dependencies", is_flag=True, help="Include dependency information")
@click.option("--include-performance", is_flag=True, help="Include performance metrics")
@click.pass_context
def diagnose(ctx: click.Context, include_dependencies: bool, include_performance: bool) -> None:
    """System diagnostics and troubleshooting

    Examples:
        gruponos-meltano diagnose --include-dependencies
        gruponos-meltano diagnose --include-performance
    """
```

### CLI Usage Examples

```bash
# Basic pipeline execution
poetry run python -m gruponos_meltano_native.cli run --job full-sync-job

# Development mode with debug logging
poetry run python -m gruponos_meltano_native.cli --debug run --dry-run

# Production environment with specific configuration
poetry run python -m gruponos_meltano_native.cli \
    --environment production \
    --config config/prod.yml \
    run --job incremental-sync-job

# Complete system validation
poetry run python -m gruponos_meltano_native.cli validate \
    --include-oracle-health \
    --include-meltano-test

# Comprehensive diagnostics
poetry run python -m gruponos_meltano_native.cli diagnose \
    --include-dependencies \
    --include-performance
```

---

## Monitoring API

### Alert Manager

```python
from gruponos_meltano_native.monitoring import GruponosMeltanoAlertManager
from flext_observability import AlertSeverity, AlertType

class GruponosMeltanoAlertManager:
    """Alert management following FLEXT observability patterns"""

    def __init__(self, settings: GruponosMeltanoSettings) -> None:
        """Initialize alert manager with configuration"""

    def create_pipeline_alert(
        self,
        title: str,
        message: str,
        severity: AlertSeverity,
        pipeline_name: str,
        company_code: str,
        facility_code: str,
        additional_context: Optional[FlextTypes.Dict] = None
    ) -> FlextResult[Alert]:
        """Create pipeline-specific alert

        Args:
            title: Alert title
            message: Detailed alert message
            severity: Alert severity (critical, warning, info)
            pipeline_name: Name of the pipeline that triggered alert
            company_code: Oracle WMS company code
            facility_code: Oracle WMS facility code
            additional_context: Additional context data

        Returns:
            FlextResult containing created alert
        """

    def check_pipeline_sla_compliance(
        self,
        pipeline_name: str,
        execution_duration: float,
        sla_threshold: float
    ) -> FlextResult[bool]:
        """Check if pipeline execution meets SLA requirements

        Args:
            pipeline_name: Name of executed pipeline
            execution_duration: Actual execution duration in seconds
            sla_threshold: Maximum allowed duration in seconds

        Returns:
            FlextResult indicating SLA compliance status
        """

class GruponosMeltanoAlert(BaseModel):
    """Pipeline alert data model"""

    alert_id: str
    title: str
    message: str
    severity: AlertSeverity
    alert_type: AlertType

    # Pipeline context
    pipeline_name: str
    company_code: str
    facility_code: str

    # Timing information
    created_at: datetime
    resolved_at: Optional[datetime] = None

    # Additional context
    context: FlextTypes.Dict
    tags: List[str]
```

### Metrics Collection

```python
from flext_observability import get_metrics_client, MetricsClient

class GruponosMeltanoMetrics:
    """Pipeline metrics collection following FLEXT patterns"""

    def __init__(self) -> None:
        self.metrics: MetricsClient = get_metrics_client()

    def track_pipeline_execution(
        self,
        pipeline_name: str,
        company_code: str,
        facility_code: str,
        duration_seconds: float,
        records_processed: int,
        success: bool
    ) -> None:
        """Track pipeline execution metrics"""

        # Execution counters
        self.metrics.counter("pipeline.executions.total").inc(
            labels={
                "pipeline": pipeline_name,
                "company": company_code,
                "facility": facility_code,
                "status": "success" if success else "failure"
            }
        )

        # Duration histogram
        self.metrics.histogram("pipeline.duration.seconds").observe(
            duration_seconds,
            labels={
                "pipeline": pipeline_name,
                "company": company_code,
                "facility": facility_code
            }
        )

        # Records processed gauge
        self.metrics.gauge("pipeline.records.processed").set(
            records_processed,
            labels={
                "pipeline": pipeline_name,
                "company": company_code,
                "facility": facility_code
            }
        )

    def track_data_quality_metrics(
        self,
        entity_name: str,
        total_records: int,
        valid_records: int,
        validation_errors: int
    ) -> None:
        """Track data quality metrics"""

        quality_score = valid_records / total_records if total_records > 0 else 0

        self.metrics.gauge("data.quality.score").set(
            quality_score,
            labels={"entity": entity_name}
        )

        self.metrics.counter("data.validation.errors.total").inc(
            validation_errors,
            labels={"entity": entity_name}
        )
```

---

## Oracle WMS API

### Connection Manager

```python
from gruponos_meltano_native.oracle import GruponosMeltanoOracleConnectionManager

class GruponosMeltanoOracleConnectionManager:
    """Oracle WMS and database connection management"""

    def __init__(self, settings: GruponosMeltanoSettings) -> None:
        """Initialize connection manager with configuration"""

    def test_wms_connection(self) -> FlextResult[bool]:
        """Test Oracle WMS API connectivity

        Returns:
            FlextResult indicating connection status

        Raises:
            GruponosMeltanoConnectionError: WMS connection failed
        """

    def test_database_connection(self) -> FlextResult[bool]:
        """Test Oracle target database connectivity

        Returns:
            FlextResult indicating database connection status

        Raises:
            GruponosMeltanoConnectionError: Database connection failed
        """

    def get_wms_entities_metadata(
        self,
        company_code: str,
        facility_code: str
    ) -> FlextResult[Dict[str, EntityMetadata]]:
        """Retrieve Oracle WMS entities metadata

        Args:
            company_code: Oracle WMS company identifier
            facility_code: Oracle WMS facility identifier

        Returns:
            FlextResult containing entity metadata dictionary
        """

    def validate_target_schema(self) -> FlextResult[bool]:
        """Validate Oracle target database schema exists and is accessible

        Returns:
            FlextResult indicating schema validation status
        """

class EntityMetadata(BaseModel):
    """Oracle WMS entity metadata"""

    entity_name: str
    table_name: str
    primary_keys: List[str]
    replication_key: Optional[str]
    fields: List[FieldMetadata]
    record_count: Optional[int]
    last_modified: Optional[datetime]

class FieldMetadata(BaseModel):
    """Entity field metadata"""

    field_name: str
    data_type: str
    nullable: bool
    max_length: Optional[int]
    description: Optional[str]
```

---

## Data Validation API

### Validator Classes

```python
from gruponos_meltano_native.validators import GruponosMeltanoDataValidator

class GruponosMeltanoDataValidator:
    """Business rule validation for Oracle WMS data"""

    def __init__(self, settings: GruponosMeltanoSettings) -> None:
        """Initialize validator with configuration"""

    def validate_allocation_data(
        self,
        allocation_records: List[FlextTypes.Dict]
    ) -> FlextResult[ValidationResult]:
        """Validate allocation data against business rules

        Args:
            allocation_records: List of allocation records to validate

        Returns:
            FlextResult containing validation results
        """

    def validate_order_data(
        self,
        order_headers: List[FlextTypes.Dict],
        order_details: List[FlextTypes.Dict]
    ) -> FlextResult[ValidationResult]:
        """Validate order data integrity and business rules

        Args:
            order_headers: List of order header records
            order_details: List of order detail records

        Returns:
            FlextResult containing validation results
        """

    def validate_data_freshness(
        self,
        entity_name: str,
        last_sync_timestamp: datetime,
        max_age_hours: int = 24
    ) -> FlextResult[bool]:
        """Validate data freshness requirements

        Args:
            entity_name: Name of the entity to check
            last_sync_timestamp: Timestamp of last successful sync
            max_age_hours: Maximum allowed age in hours

        Returns:
            FlextResult indicating if data meets freshness requirements
        """

class ValidationResult(BaseModel):
    """Data validation result"""

    entity_name: str
    total_records: int
    valid_records: int
    invalid_records: int
    validation_errors: List[ValidationError]
    quality_score: float
    passed_validation: bool

class ValidationError(BaseModel):
    """Individual validation error"""

    record_id: str
    field_name: str
    error_type: str
    error_message: str
    actual_value: object
    expected_value: Optional[object] = None
```

---

## Exception Handling

### Exception Hierarchy

```python
from gruponos_meltano_native.exceptions import (
    GruponosMeltanoError,
    GruponosMeltanoValidationError,
    GruponosMeltanoConnectionError,
    GruponosMeltanoProcessingError,
    GruponosMeltanoAuthenticationError,
    GruponosMeltanoTimeoutError
)

# Base exception
class GruponosMeltanoError(Exception):
    """Base exception for all GrupoNOS Meltano operations"""

    def __init__(self, message: str, context: Optional[FlextTypes.Dict] = None):
        super().__init__(message)
        self.context = context or {}

# Specific exceptions
class GruponosMeltanoValidationError(GruponosMeltanoError):
    """Data or configuration validation failed"""

class GruponosMeltanoConnectionError(GruponosMeltanoError):
    """Oracle WMS or database connection failed"""

class GruponosMeltanoProcessingError(GruponosMeltanoError):
    """Pipeline processing or transformation failed"""

class GruponosMeltanoAuthenticationError(GruponosMeltanoError):
    """Authentication to Oracle WMS failed"""

class GruponosMeltanoTimeoutError(GruponosMeltanoError):
    """Operation timed out"""
```

### Error Handling Patterns

```python
from flext_core import FlextResult

def handle_pipeline_execution() -> FlextResult[PipelineResult]:
    """Example of proper error handling with FlextResult"""

    try:
        # Execute pipeline operations
        result = orchestrator.execute_full_sync()
        return result

    except GruponosMeltanoConnectionError as e:
        logger.error("Connection failed", extra={"error": str(e), "context": e.context})
        return FlextResult[None].fail(f"Oracle connection failed: {e}")

    except GruponosMeltanoValidationError as e:
        logger.warning("Validation failed", extra={"error": str(e), "context": e.context})
        return FlextResult[None].fail(f"Data validation failed: {e}")

    except GruponosMeltanoProcessingError as e:
        logger.error("Processing failed", extra={"error": str(e), "context": e.context})
        return FlextResult[None].fail(f"Pipeline processing failed: {e}")

    except Exception as e:
        logger.error("Unexpected error", exc_info=True)
        return FlextResult[None].fail(f"Unexpected error: {e}")
```

---

## Factory Functions

### Main Factory Functions

```python
from gruponos_meltano_native import (
    create_gruponos_meltano_platform,
    create_gruponos_meltano_orchestrator,
    create_gruponos_meltano_settings
)

def create_gruponos_meltano_platform(
    environment: Optional[str] = None,
    config_file: Optional[Path] = None
) -> GruponosMeltanoOrchestrator:
    """Create complete GrupoNOS Meltano platform instance

    Args:
        environment: Target environment (dev, staging, prod)
        config_file: Optional configuration file path

    Returns:
        Fully configured GruponosMeltanoOrchestrator instance
    """

def create_gruponos_meltano_orchestrator(
    settings: GruponosMeltanoSettings
) -> GruponosMeltanoOrchestrator:
    """Create orchestrator with specific settings

    Args:
        settings: GrupoNOS Meltano configuration

    Returns:
        Configured orchestrator instance
    """
```

---

**Next**: [Configuration Guide](configuration.md) | [Testing Guide](testing.md) | [CLI Reference](cli.md)
