"""GrupoNOS Meltano Native - Framework ETL Empresarial para integração Oracle WMS.

Copyright (c) 2025 Grupo Nós. Todos os direitos reservados. Licença: Proprietária
"""

from __future__ import annotations

import importlib.metadata
from typing import Final

# External library imports
from flext_core import (
    FlextConfig,
    FlextContainer,
    FlextModels,
    FlextResult,
    FlextTypes,
)

from gruponos_meltano_native import monitoring

# Local module imports
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
from gruponos_meltano_native.monitoring.alert_manager import (
    GruponosMeltanoAlert,
    GruponosMeltanoAlertManager,
    GruponosMeltanoAlertService,
    GruponosMeltanoAlertSeverity,
    GruponosMeltanoAlertType,
    create_gruponos_meltano_alert_manager,
)
from gruponos_meltano_native.oracle.connection_manager_enhanced import (
    GruponosMeltanoOracleConnectionManager,
    create_gruponos_meltano_oracle_connection_manager,
)
from gruponos_meltano_native.orchestrator import (
    GruponosMeltanoOrchestrator,
    GruponosMeltanoPipelineResult,
    create_gruponos_meltano_orchestrator,
    create_gruponos_meltano_pipeline_runner,
)
from gruponos_meltano_native.protocols import GruponosMeltanoNativeProtocols
from gruponos_meltano_native.validators import (
    DataValidator,
    ValidationError,
    ValidationRule,
    create_validator_for_environment,
)
from gruponos_meltano_native.version import VERSION, GruponosMeltanoNativeVersion

# Version handling
try:
    __version__ = importlib.metadata.version("gruponos-meltano-native")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.9.0"

# Type aliases
GruponosMeltanoSettings = GruponosMeltanoNativeConfig
PROJECT_VERSION: Final[GruponosMeltanoNativeVersion] = VERSION

__version__: str = VERSION.version
__version_info__: tuple[int | str, ...] = VERSION.version_info

__all__ = [
    "PROJECT_VERSION",
    "VERSION",
    "DataValidator",
    "FlextConfig",
    "FlextContainer",
    "FlextModels",
    "FlextResult",
    "FlextTypes",
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
    "GruponosMeltanoNativeVersion",
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
    "alert_manager",
    "create_gruponos_meltano_alert_manager",
    "create_gruponos_meltano_oracle_connection_manager",
    "create_gruponos_meltano_orchestrator",
    "create_gruponos_meltano_pipeline_runner",
    "create_gruponos_meltano_settings",
    "create_validator_for_environment",
    "gruponos_meltano_cli",
    "monitoring",
]
