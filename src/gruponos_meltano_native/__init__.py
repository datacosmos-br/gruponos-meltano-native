"""GrupoNOS Meltano Native - Framework ETL Empresarial para integração Oracle WMS.

Copyright (c) 2025 Grupo Nós. Todos os direitos reservados. Licença: Proprietária
"""

from __future__ import annotations

from gruponos_meltano_native import monitoring
from gruponos_meltano_native.__version__ import __version__, __version_info__
from gruponos_meltano_native.cli import cli as gruponos_meltano_cli
from gruponos_meltano_native.config import (
    GruponosMeltanoAlertConfig,
    GruponosMeltanoJobConfig,
    GruponosMeltanoNativeConfig,
    GruponosMeltanoOracleConnectionConfig,
    GruponosMeltanoTargetOracleConfig,
    GruponosMeltanoWMSSourceConfig,
)
from gruponos_meltano_native.monitoring import alert_manager
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

__all__ = [
    "DataValidator",
    "GruponosMeltanoAlert",
    "GruponosMeltanoAlertConfig",
    "GruponosMeltanoAlertManager",
    "GruponosMeltanoAlertService",
    "GruponosMeltanoAlertSeverity",
    "GruponosMeltanoAlertType",
    "GruponosMeltanoJobConfig",
    "GruponosMeltanoNativeConfig",
    "GruponosMeltanoNativeProtocols",
    "GruponosMeltanoOracleConnectionConfig",
    "GruponosMeltanoOracleConnectionManager",
    "GruponosMeltanoOrchestrator",
    "GruponosMeltanoPipelineResult",
    "GruponosMeltanoTargetOracleConfig",
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
    "create_validator_for_environment",
    "gruponos_meltano_cli",
    "monitoring",
]
