"""GrupoNOS Meltano Native - Enterprise ETL Pipeline Framework.

A production-ready ETL pipeline implementation built on the FLEXT framework ecosystem,
designed specifically for Oracle WMS to Oracle Database data integration operations.
This module provides comprehensive orchestration, monitoring, and data validation
capabilities with enterprise-grade reliability and observability.

Key Components:
    - Orchestrator: Main ETL pipeline orchestration with railway-oriented programming
    - Configuration: Environment-aware settings with Pydantic validation
    - Oracle Integration: Native Oracle database connectivity and operations
    - Monitoring: Alert management and performance tracking
    - Data Validation: Multi-layer validation with business rules enforcement

Architecture:
    Built on Clean Architecture principles with Domain-Driven Design patterns,
    the module implements FLEXT core standards for consistent error handling,
    dependency injection, and observability across the data pipeline.

Integration:
    - Built on flext-core foundation patterns (FlextResult, FlextContainer)
    - Integrates with flext-observability for comprehensive monitoring
    - Uses flext-db-oracle for optimized Oracle database operations
    - Coordinates with Singer/Meltano ecosystem for data pipeline execution

Example:
    Basic ETL pipeline execution:

    >>> from gruponos_meltano_native import create_gruponos_meltano_platform
    >>> orchestrator = create_gruponos_meltano_platform()
    >>> result = await orchestrator.execute_full_sync("GNOS", "DC01")
    >>> if result.success:
    ...     print(f"Processed {result.data.records_processed} records")

Author: GrupoNOS FLEXT Team
Version: 0.9.0
License: MIT

"""

from __future__ import annotations

import importlib.metadata

# FLEXT Core Foundation - Direct imports only
from flext_core import (
    FlextSettings,
    FlextContainer,
    FlextResult,
    FlextValueObject,
    get_flext_container,
)

# Version Management
try:
    __version__ = importlib.metadata.version("gruponos-meltano-native")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.9.0"

__version_info__ = tuple(int(x) for x in __version__.split(".") if x.isdigit())

# ================================
# DIRECT FLEXT-STANDARD IMPORTS
# ================================

# Configuration Management
# CLI
from gruponos_meltano_native.cli import cli as gruponos_meltano_cli
from gruponos_meltano_native.config import (
    GruponosMeltanoAlertConfig,
    GruponosMeltanoJobConfig,
    GruponosMeltanoOracleConnectionConfig,
    GruponosMeltanoSettings,
    GruponosMeltanoTargetOracleConfig,
    GruponosMeltanoWMSSourceConfig,
)

# Monitoring & Alerts
from gruponos_meltano_native.monitoring.alert_manager import (
    GruponosMeltanoAlert,
    GruponosMeltanoAlertManager,
    GruponosMeltanoAlertService,
    GruponosMeltanoAlertSeverity,
    GruponosMeltanoAlertType,
    create_gruponos_meltano_alert_manager,
)

# Oracle Integration
from gruponos_meltano_native.oracle.connection_manager_enhanced import (
    GruponosMeltanoOracleConnectionManager,
    create_gruponos_meltano_oracle_connection_manager,
)

# Orchestration
from gruponos_meltano_native.orchestrator import (
    GruponosMeltanoOrchestrator,
    GruponosMeltanoPipelineResult,
    GruponosMeltanoPipelineRunner,
    create_gruponos_meltano_orchestrator,
    create_gruponos_meltano_pipeline_runner,
)

# Data Validation
from gruponos_meltano_native.validators import (
    GruponosMeltanoDataValidator,
    create_gruponos_meltano_validator_for_environment,
)

# ================================
# FACTORY FUNCTIONS
# ================================


def create_gruponos_meltano_platform() -> GruponosMeltanoOrchestrator:
    """Create a GrupoNOS Meltano platform instance with FLEXT standards.

    This factory function initializes a complete ETL platform orchestrator with
    enterprise-grade configuration, monitoring, and error handling capabilities.
    The orchestrator integrates with the FLEXT ecosystem for consistent patterns
    across all data pipeline operations.

    The platform provides:
    - Full and incremental sync capabilities
    - Oracle WMS to Oracle Database ETL operations
    - Comprehensive data validation and quality checks
    - Enterprise monitoring and alerting
    - Railway-oriented error propagation

    Returns:
        GruponosMeltanoOrchestrator: Fully configured orchestrator instance
        ready for ETL pipeline execution with enterprise monitoring and
        error handling capabilities.

    Example:
        >>> platform = create_gruponos_meltano_platform()
        >>> result = await platform.execute_full_sync("GNOS", "DC01")
        >>> if result.success:
        ...     print(f"ETL completed: {result.data.summary}")

    """
    settings = GruponosMeltanoSettings()
    return GruponosMeltanoOrchestrator(settings)


def create_gruponos_meltano_oracle_manager() -> GruponosMeltanoOracleConnectionManager:
    """Create a GrupoNOS Meltano Oracle connection manager.

    This factory function initializes an Oracle database connection manager
    optimized for ETL operations with connection pooling, health monitoring,
    and automatic failover capabilities. The manager integrates with the
    FLEXT database abstraction layer for consistent error handling.

    Features:
    - Connection pooling for high-performance ETL operations
    - Health monitoring with automatic reconnection
    - Query optimization for large data volumes
    - Transaction management with rollback capabilities
    - Integration with FLEXT observability patterns

    Returns:
        GruponosMeltanoOracleConnectionManager: Configured Oracle connection
        manager with enterprise-grade connection pooling and monitoring.

    Example:
        >>> manager = create_gruponos_meltano_oracle_manager()
        >>> connection_result = await manager.get_connection()
        >>> if connection_result.success:
        ...     conn = connection_result.data
        ...     # Use connection for ETL operations

    """
    return create_gruponos_meltano_oracle_connection_manager()


# ================================
# PUBLIC API - FLEXT STANDARD ONLY
# ================================

__all__: list[str] = [
    "FlextSettings",
    "FlextContainer",
    "FlextResult",
    "FlextValueObject",
    "GruponosMeltanoAlert",
    "GruponosMeltanoAlertConfig",
    "GruponosMeltanoAlertManager",
    "GruponosMeltanoAlertService",
    "GruponosMeltanoAlertSeverity",
    "GruponosMeltanoAlertType",
    "GruponosMeltanoDataValidator",
    "GruponosMeltanoJobConfig",
    "GruponosMeltanoOracleConnectionConfig",
    "GruponosMeltanoOracleConnectionManager",
    "GruponosMeltanoOrchestrator",
    "GruponosMeltanoPipelineResult",
    "GruponosMeltanoPipelineRunner",
    "GruponosMeltanoSettings",
    "GruponosMeltanoTargetOracleConfig",
    "GruponosMeltanoWMSSourceConfig",
    "__version__",
    "__version_info__",
    "create_gruponos_meltano_alert_manager",
    "create_gruponos_meltano_oracle_connection_manager",
    "create_gruponos_meltano_oracle_manager",
    "create_gruponos_meltano_orchestrator",
    "create_gruponos_meltano_pipeline_runner",
    "create_gruponos_meltano_platform",
    "create_gruponos_meltano_validator_for_environment",
    "get_flext_container",
    "gruponos_meltano_cli",
]

# Library metadata
__author__ = "GrupoNOS FLEXT Team"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2025 GrupoNOS FLEXT Team"
