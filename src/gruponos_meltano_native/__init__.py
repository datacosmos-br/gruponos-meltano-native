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
    get_flext_container,
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
    GruponosMeltanoOracleConnectionConfig,
    GruponosMeltanoSettings,
    GruponosMeltanoTargetOracleConfig,
    GruponosMeltanoWMSSourceConfig,
    create_gruponos_meltano_settings,
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
    """Cria instância da plataforma Meltano GrupoNOS com padrões empresariais."""
    settings = GruponosMeltanoSettings()
    return GruponosMeltanoOrchestrator(settings)


def create_gruponos_meltano_oracle_manager() -> GruponosMeltanoOracleConnectionManager:
    """Cria um gerenciador de conexão Oracle Meltano GrupoNOS."""
    return create_gruponos_meltano_oracle_connection_manager()


# ================================
# API PÚBLICA - PADRÃO APENAS
# ================================

__all__: FlextTypes.Core.StringList = [
    "FlextConfig",
    "FlextContainer",
    "FlextModels",
    "FlextResult",
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
    "create_gruponos_meltano_settings",
    "create_gruponos_meltano_validator_for_environment",
    "get_flext_container",
    "gruponos_meltano_cli",
]
