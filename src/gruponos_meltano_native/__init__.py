"""GrupoNOS Meltano Native - Enterprise Meltano Integration with FLEXT standards.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Version 0.8.0 - FLEXT-standardized GrupoNOS Meltano Native:
- Pure FLEXT naming conventions (GruponosMeltano prefix)
- Built on flext-core foundation for enterprise integration
- Root-level direct imports - NO legacy aliases or wrappers
- Clean Architecture compliance without duplications
"""

from __future__ import annotations

import importlib.metadata

# FLEXT Core Foundation - Direct imports only
from flext_core import (
    FlextContainer,
    FlextCoreSettings,
    FlextResult,
    FlextValueObject,
    get_flext_container,
)

# Version Management
try:
    __version__ = importlib.metadata.version("gruponos-meltano-native")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.8.0"

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

    Returns:
        Configured GruponosMeltanoOrchestrator instance

    """
    settings = GruponosMeltanoSettings()
    return GruponosMeltanoOrchestrator(settings)


def create_gruponos_meltano_oracle_manager() -> GruponosMeltanoOracleConnectionManager:
    """Create a GrupoNOS Meltano Oracle connection manager.

    Returns:
        Configured Oracle connection manager instance

    """
    return create_gruponos_meltano_oracle_connection_manager()


# ================================
# PUBLIC API - FLEXT STANDARD ONLY
# ================================

__all__ = [
    "FlextContainer",
    "FlextCoreSettings",
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
