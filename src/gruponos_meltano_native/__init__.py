"""GrupoNOS Meltano Native - Enterprise ETL Pipeline Framework for Oracle WMS integration."""

from __future__ import annotations

import importlib.metadata

# FLEXT Core Foundation - Direct imports only
from flext_core import (
    FlextConfig,
    FlextContainer,
    FlextResult,
    FlextModels,
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
    """Cria instância da plataforma Meltano GrupoNOS com padrões FLEXT.

    Esta função factory inicializa um orquestrador completo de plataforma ETL com
    configuração empresarial, monitoramento e capacidades de tratamento de erro.
    O orquestrador integra com o ecossistema FLEXT para padrões consistentes
    em todas as operações de pipeline de dados.

    A plataforma fornece:
    - Capacidades de sincronização completa e incremental
    - Operações ETL Oracle WMS para Oracle Database
    - Validação de dados abrangente e verificações de qualidade
    - Monitoramento e alertas empresariais
    - Propagação de erro orientada por railway

    Returns:
      GruponosMeltanoOrchestrator: Instância do orquestrador totalmente configurada
      pronta para execução de pipeline ETL com monitoramento empresarial e
      capacidades de tratamento de erro.

    Example:
      >>> platform = create_gruponos_meltano_platform()
      >>> result = await platform.execute_full_sync("GNOS", "DC01")
      >>> if result.success:
      ...     print(f"ETL completado: {result.data.summary}")

    """
    settings = GruponosMeltanoSettings()
    return GruponosMeltanoOrchestrator(settings)


def create_gruponos_meltano_oracle_manager() -> GruponosMeltanoOracleConnectionManager:
    """Cria um gerenciador de conexão Oracle Meltano GrupoNOS.

    Esta função factory inicializa um gerenciador de conexão de banco de dados Oracle
    otimizado para operações ETL com pooling de conexões, monitoramento de saúde
    e capacidades de failover automático. O gerenciador integra com a
    camada de abstração de banco FLEXT para tratamento consistente de erros.

    Recursos:
    - Pooling de conexões para operações ETL de alta performance
    - Monitoramento de saúde com reconexão automática
    - Otimização de consultas para grandes volumes de dados
    - Gerenciamento de transações com capacidades de rollback
    - Integração com padrões de observabilidade FLEXT

    Returns:
      GruponosMeltanoOracleConnectionManager: Gerenciador de conexão Oracle
      configurado com pooling de conexões e monitoramento de nível empresarial.

    Example:
      >>> manager = create_gruponos_meltano_oracle_manager()
      >>> connection_result = await manager.get_connection()
      >>> if connection_result.success:
      ...     conn = connection_result.data
      ...     # Usar conexão para operações ETL

    """
    return create_gruponos_meltano_oracle_connection_manager()


# ================================
# PUBLIC API - FLEXT STANDARD ONLY
# ================================

__all__: list[str] = [
    "FlextConfig",
    "FlextContainer",
    "FlextResult",
    "FlextModels",
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
