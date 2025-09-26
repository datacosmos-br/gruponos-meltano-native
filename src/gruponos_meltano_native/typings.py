"""GrupoNOS Meltano Native Types - Domain-specific Meltano ETL type definitions.

This module provides GrupoNOS Meltano Native-specific type definitions extending FlextTypes.
Follows FLEXT standards:
- Domain-specific complex types only
- No simple aliases to primitive types
- Python 3.13+ syntax
- Extends FlextTypes properly

Copyright (c) 2025 Grupo Nós. Todos os direitos reservados.
SPDX-License-Identifier: Proprietary
"""

from __future__ import annotations

from typing import Literal

from flext_core import FlextTypes

# =============================================================================
# GRUPONOS MELTANO NATIVE-SPECIFIC TYPE VARIABLES - Domain-specific TypeVars for Meltano ETL operations
# =============================================================================


# GrupoNOS Meltano Native domain TypeVars
class GruponosMeltanoNativeTypes(FlextTypes):
    """GrupoNOS Meltano Native-specific type definitions extending FlextTypes.

    Domain-specific type system for GrupoNOS Oracle WMS integration via Meltano ETL pipelines.
    Contains ONLY complex Meltano and Oracle WMS-specific types, no simple aliases.
    Uses Python 3.13+ type syntax and patterns.
    """

    # =========================================================================
    # MELTANO PIPELINE TYPES - Meltano orchestration and pipeline types
    # =========================================================================

    class MeltanoPipeline:
        """Meltano pipeline complex types."""

        type PipelineConfiguration = dict[
            str, FlextTypes.Core.JsonValue | dict[str, object]
        ]
        type ExtractorConfig = dict[str, str | int | bool | dict[str, object]]
        type LoaderConfig = dict[str, str | int | bool | dict[str, object]]
        type TransformConfig = dict[
            str, FlextTypes.Core.ConfigValue | dict[str, object]
        ]
        type ScheduleConfig = dict[
            str, str | bool | dict[str, FlextTypes.Core.JsonValue]
        ]
        type PluginDefinition = dict[str, str | dict[str, FlextTypes.Core.JsonValue]]
        type EnvironmentConfig = dict[str, FlextTypes.Core.ConfigValue | object]

    # =========================================================================
    # ORACLE WMS TYPES - Oracle Warehouse Management System integration types
    # =========================================================================

    class OracleWms:
        """Oracle WMS integration complex types."""

        type WmsApiResponse = dict[
            str, FlextTypes.Core.JsonValue | list[dict[str, object]]
        ]
        type WmsEntityData = dict[str, str | int | float | bool | dict[str, object]]
        type AllocationData = dict[str, FlextTypes.Core.JsonValue | list[str]]
        type OrderHeaderData = dict[str, FlextTypes.Core.JsonValue | dict[str, object]]
        type OrderDetailData = dict[
            str, FlextTypes.Core.JsonValue | list[dict[str, object]]
        ]
        type InventoryData = dict[
            str, str | int | float | dict[str, FlextTypes.Core.JsonValue]
        ]
        type WarehouseMetrics = dict[str, int | float | dict[str, object]]
        type FacilityConfiguration = dict[
            str, str | dict[str, FlextTypes.Core.JsonValue]
        ]

    # =========================================================================
    # ETL PROCESSING TYPES - Data extraction, transformation, and loading types
    # =========================================================================

    class EtlProcessing:
        """ETL processing complex types."""

        type ExtractionResult = dict[
            str, list[dict[str, FlextTypes.Core.JsonValue]] | dict[str, object]
        ]
        type TransformationRules = dict[str, str | list[str] | dict[str, object]]
        type LoadingStrategy = dict[
            str, str | bool | dict[str, FlextTypes.Core.JsonValue]
        ]
        type DataValidation = dict[
            str, bool | str | dict[str, FlextTypes.Core.JsonValue]
        ]
        type ProcessingMetrics = dict[str, int | float | dict[str, object]]
        type ErrorHandling = dict[str, str | bool | list[str] | dict[str, object]]

    # =========================================================================
    # DATA QUALITY TYPES - Data validation and quality assessment types
    # =========================================================================

    class DataQuality:
        """Data quality complex types."""

        type ValidationRules = dict[str, bool | str | list[str] | dict[str, object]]
        type QualityMetrics = dict[
            str, int | float | dict[str, FlextTypes.Core.JsonValue]
        ]
        type DataProfiler = dict[str, str | dict[str, FlextTypes.Core.JsonValue]]
        type AnomalyDetection = dict[str, bool | float | dict[str, object]]
        type QualityReport = dict[str, FlextTypes.Core.JsonValue | dict[str, object]]
        type ComplianceRules = dict[
            str, bool | str | dict[str, FlextTypes.Core.JsonValue]
        ]

    # =========================================================================
    # MONITORING TYPES - Pipeline monitoring and observability types
    # =========================================================================

    class Monitoring:
        """Monitoring and observability complex types."""

        type PipelineMetrics = dict[str, int | float | str | dict[str, object]]
        type AlertConfiguration = dict[
            str, bool | str | dict[str, FlextTypes.Core.JsonValue]
        ]
        type PerformanceMetrics = dict[str, float | dict[str, object]]
        type LogAggregation = dict[
            str, str | list[str] | dict[str, FlextTypes.Core.JsonValue]
        ]
        type HealthChecks = dict[str, bool | str | dict[str, object]]
        type MetricsDashboard = dict[str, FlextTypes.Core.JsonValue | dict[str, object]]

    # =========================================================================
    # ORCHESTRATION TYPES - Pipeline orchestration and workflow types
    # =========================================================================

    class Orchestration:
        """Orchestration and workflow complex types."""

        type WorkflowDefinition = dict[
            str, str | list[dict[str, FlextTypes.Core.JsonValue]]
        ]
        type JobConfiguration = dict[
            str, FlextTypes.Core.ConfigValue | dict[str, object]
        ]
        type SchedulingRules = dict[
            str, str | bool | dict[str, FlextTypes.Core.JsonValue]
        ]
        type DependencyGraph = dict[str, list[str] | dict[str, object]]
        type ExecutionContext = dict[str, FlextTypes.Core.JsonValue | dict[str, object]]
        type WorkflowState = dict[
            str, str | bool | dict[str, FlextTypes.Core.JsonValue]
        ]

    # =========================================================================
    # GRUPONOS PROJECT TYPES - Domain-specific project types extending FlextTypes
    # =========================================================================

    class Project(FlextTypes.Project):
        """GrupoNOS Meltano Native-specific project types extending FlextTypes.Project.

        Adds GrupoNOS Meltano ETL-specific project types while inheriting
        generic types from FlextTypes. Follows domain separation principle:
        GrupoNOS domain owns Oracle WMS and Meltano ETL-specific types.
        """

        # GrupoNOS Meltano Native-specific project types extending the generic ones
        type ProjectType = Literal[
            # Generic types inherited from FlextTypes.Project
            "library",
            "application",
            "service",
            # GrupoNOS Meltano Native-specific types
            "meltano-native",
            "oracle-wms-etl",
            "meltano-pipeline",
            "wms-integration",
            "etl-orchestration",
            "data-warehouse",
            "oracle-connector",
            "meltano-tap",
            "meltano-target",
            "wms-analytics",
            "inventory-etl",
            "allocation-pipeline",
            "order-processing",
            "warehouse-analytics",
            "meltano-dbt",
            "oracle-wms-native",
            "gruponos-etl",
            "enterprise-meltano",
            "wms-data-pipeline",
            "oracle-integration",
        ]

        # GrupoNOS Meltano Native-specific project configurations
        type GruponosMeltanoConfig = dict[str, FlextTypes.Core.ConfigValue | object]
        type OracleWmsConfig = dict[str, str | int | bool | dict[str, object]]
        type MeltanoPipelineConfig = dict[str, FlextTypes.Core.ConfigValue | object]
        type EtlOrchestrationConfig = dict[str, bool | str | dict[str, object]]


# =============================================================================
# PUBLIC API EXPORTS - GrupoNOS Meltano Native TypeVars and types
# =============================================================================

__all__: list[str] = [
    "GruponosMeltanoNativeTypes",
]
