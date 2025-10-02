"""GrupoNOS Meltano Native - Framework ETL Empresarial para integração Oracle WMS.

Copyright (c) 2025 Grupo Nós. Todos os direitos reservados. Licença: Proprietária
"""

from __future__ import annotations

import importlib.metadata

# Bibliotecas base - Importações diretas apenas
from flext_core import (
    FlextConfig,
    FlextContainer,
    FlextModels,
    FlextResult,
    FlextTypes,
)

# Version Management
try:
    __version__ = importlib.metadata.version("gruponos-meltano-native")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.9.0"

__version_info__ = tuple(int(x) for x in __version__.split(".") if x.isdigit())

# ================================
# IMPORTAÇÕES DIRETAS PADRÃO
# ================================

# Configuration Management
# CLI
from gruponos_meltano_native.cli import cli as gruponos_meltano_cli
from gruponos_meltano_native.config import (
    GruponosMeltanoAlertConfig,
    GruponosMeltanoJobConfig,
    GruponosMeltanoNativeConfig,
    GruponosMeltanoOracleConnectionConfig,
    GruponosMeltanoTargetOracleConfig,
    GruponosMeltanoWMSSourceConfig,
    create_gruponos_meltano_settings,
)

# Alias for backward compatibility
GruponosMeltanoSettings = GruponosMeltanoNativeConfig

# Exceptions
from gruponos_meltano_native.exceptions import (
    GruponosMeltanoAlertDeliveryError,
    GruponosMeltanoAlertError,
    GruponosMeltanoAuthenticationError,
    GruponosMeltanoConfigurationError,
    GruponosMeltanoConnectionError,
    GruponosMeltanoDataError,
    GruponosMeltanoDataQualityError,
    GruponosMeltanoDataValidationError,
    GruponosMeltanoError,
    GruponosMeltanoMissingConfigError,
    GruponosMeltanoMonitoringError,
    GruponosMeltanoOracleConnectionError,
    GruponosMeltanoOracleError,
    GruponosMeltanoOracleQueryError,
    GruponosMeltanoOracleTimeoutError,
    GruponosMeltanoOrchestrationError,
    GruponosMeltanoPipelineError,
    GruponosMeltanoPipelineTimeoutError,
    GruponosMeltanoPipelineValidationError,
    GruponosMeltanoProcessingError,
    GruponosMeltanoSingerError,
    GruponosMeltanoTapError,
    GruponosMeltanoTargetError,
    GruponosMeltanoTimeoutError,
    GruponosMeltanoValidationError,
)

# Factory functions will be added when needed
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
from gruponos_meltano_native.protocols import GruponosMeltanoNativeProtocols

# Data Validation
from gruponos_meltano_native.validators import (
    DataValidator,
    ValidationError,
    ValidationRule,
    create_validator_for_environment,
)

# ================================
# API PÚBLICA - PADRÃO APENAS
# ================================

__all__: FlextTypes.Core.StringList = [
    "DataValidator",
    "FlextConfig",
    "FlextContainer",
    "FlextModels",
    "FlextResult",
    "GruponosMeltanoAlert",
    "GruponosMeltanoAlertConfig",
    "GruponosMeltanoAlertDeliveryError",
    "GruponosMeltanoAlertError",
    "GruponosMeltanoAlertManager",
    "GruponosMeltanoAlertService",
    "GruponosMeltanoAlertSeverity",
    "GruponosMeltanoAlertType",
    "GruponosMeltanoAuthenticationError",
    "GruponosMeltanoConfigurationError",
    "GruponosMeltanoConnectionError",
    "GruponosMeltanoDataError",
    "GruponosMeltanoDataQualityError",
    "GruponosMeltanoDataValidationError",
    "GruponosMeltanoError",
    "GruponosMeltanoJobConfig",
    "GruponosMeltanoMissingConfigError",
    "GruponosMeltanoMonitoringError",
    "GruponosMeltanoNativeConfig",
    "GruponosMeltanoNativeProtocols",
    "GruponosMeltanoOracleConnectionConfig",
    "GruponosMeltanoOracleConnectionError",
    "GruponosMeltanoOracleConnectionManager",
    "GruponosMeltanoOracleError",
    "GruponosMeltanoOracleQueryError",
    "GruponosMeltanoOracleTimeoutError",
    "GruponosMeltanoOrchestrationError",
    "GruponosMeltanoOrchestrator",
    "GruponosMeltanoPipelineError",
    "GruponosMeltanoPipelineResult",
    "GruponosMeltanoPipelineRunner",
    "GruponosMeltanoPipelineTimeoutError",
    "GruponosMeltanoPipelineValidationError",
    "GruponosMeltanoProcessingError",
    "GruponosMeltanoSettings",
    "GruponosMeltanoSingerError",
    "GruponosMeltanoTapError",
    "GruponosMeltanoTargetError",
    "GruponosMeltanoTargetOracleConfig",
    "GruponosMeltanoTimeoutError",
    "GruponosMeltanoValidationError",
    "GruponosMeltanoWMSSourceConfig",
    "ValidationError",
    "ValidationRule",
    "__version__",
    "__version_info__",
    "create_gruponos_meltano_alert_manager",
    "create_gruponos_meltano_oracle_connection_manager",
    "create_gruponos_meltano_orchestrator",
    "create_gruponos_meltano_pipeline_runner",
    "create_gruponos_meltano_settings",
    "create_validator_for_environment",
    "gruponos_meltano_cli",
]
