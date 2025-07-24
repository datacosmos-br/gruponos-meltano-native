"""GrupoNOS Meltano Native - Enterprise Meltano Native Integration with simplified imports.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Version 0.7.0 - GrupoNOS Meltano Native with simplified public API:
- All common imports available from root: from gruponos_meltano_native import MeltanoRunner
- Built on flext-core foundation for robust enterprise data pipelines
- Deprecation warnings for internal imports
"""

from __future__ import annotations

import contextlib
import importlib.metadata
import warnings
from pathlib import Path

# Use dependency injection instead of direct imports for Clean Architecture compliance
from gruponos_meltano_native.infrastructure.di_container import (
    get_base_config,
    get_base_settings,
    get_config,
    get_service_result,
)

# Get dependencies via DI
ServiceResult = get_service_result()

# 🚨 ARCHITECTURAL COMPLIANCE: Use DI instead of direct imports
# Projects at level 6 (specific) CANNOT import abstractions directly.
# All dependencies must be injected from workspace DI container.

# Get dependencies via DI instead of direct import violations
try:
    config_di = get_config()
    base_config_di = get_base_config()
    base_settings_di = get_base_settings()

    # Use DI-provided implementations
    MeltanoBaseConfig = base_config_di

    # Try to get additional types via workspace DI container
    import os

    workspace_container_path = os.environ.get(
        "FLEXT_WORKSPACE_CONTAINER",
        "/home/marlonsc/flext/src/workspace_di_container.py",
    )

    if Path(workspace_container_path).exists():
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "workspace_di", workspace_container_path
        )
        if spec and spec.loader:
            workspace_di = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(workspace_di)

            # Get domain types via workspace DI
            BaseModel = (
                workspace_di.get_domain_base_model()
                if hasattr(workspace_di, "get_domain_base_model")
                else None
            )
            MeltanoError = (
                workspace_di.get_domain_error()
                if hasattr(workspace_di, "get_domain_error")
                else None
            )
            ValidationError = (
                workspace_di.get_validation_error()
                if hasattr(workspace_di, "get_validation_error")
                else None
            )

    # Fallback to generic implementations if workspace DI not available
    if not globals().get("BaseModel"):
        from pydantic import BaseModel

    if not globals().get("MeltanoError"):

        class MeltanoError(Exception):
            """Meltano-specific errors."""

    if not globals().get("ValidationError"):

        class ValidationError(ValueError):
            """Validation errors."""

except ImportError:
    # Fallback apenas se DI não estiver disponível
    from pydantic import BaseModel
    from pydantic_settings import BaseSettings as MeltanoBaseConfig

    class ServiceResult:
        """Fallback ServiceResult."""

        def __init__(
            self, success: bool, data: object = None, error: object = None
        ) -> None:
            self.is_success = success
            self.data = data
            self.error = error

    class MeltanoError(Exception):
        """Meltano-specific errors."""

    class ValidationError(ValueError):
        """Validation errors."""


try:
    __version__ = importlib.metadata.version("gruponos-meltano-native")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.7.0"

__version_info__ = tuple(int(x) for x in __version__.split(".") if x.isdigit())


class GruponosMeltanoNativeDeprecationWarning(DeprecationWarning):
    """Custom deprecation warning for GRUPONOS MELTANO NATIVE import changes."""


def _show_deprecation_warning(old_import: str, new_import: str) -> None:
    """Show deprecation warning for import paths."""
    message_parts = [
        f"⚠️  DEPRECATED IMPORT: {old_import}",
        f"✅ USE INSTEAD: {new_import}",
        "🔗 This will be removed in version 1.0.0",
        "📖 See GRUPONOS MELTANO NATIVE docs for migration guide",
    ]
    warnings.warn(
        "\n".join(message_parts),
        GruponosMeltanoNativeDeprecationWarning,
        stacklevel=3,
    )


# ================================
# SIMPLIFIED PUBLIC API EXPORTS
# ================================

# Core Application exports - simplified imports
with contextlib.suppress(ImportError):
    from gruponos_meltano_native.config import (
        Config,
        MeltanoConfig,
    )

# CLI exports - simplified imports
with contextlib.suppress(ImportError):
    from gruponos_meltano_native.cli import cli as cli_main

# Orchestration exports - simplified imports
with contextlib.suppress(ImportError):
    from gruponos_meltano_native.orchestrator import (
        MeltanoOrchestrator,
        PipelineRunner,
    )

# Oracle Integration exports - simplified imports
with contextlib.suppress(ImportError):
    from gruponos_meltano_native.oracle.connection_manager import (
        OracleConnectionManager,
    )
    from gruponos_meltano_native.oracle.connection_manager_enhanced import (
        EnhancedOracleConnectionManager,
    )

# Monitoring exports - simplified imports
with contextlib.suppress(ImportError):
    from gruponos_meltano_native.monitoring.alert_manager import AlertManager

# Validation exports - simplified imports
with contextlib.suppress(ImportError):
    from gruponos_meltano_native.validators.data_validator import DataValidator

# ================================
# PUBLIC API EXPORTS
# ================================

__all__ = [
    # Monitoring (simplified access)
    "AlertManager",  # from gruponos_meltano_native import AlertManager
    # Core Patterns (from flext-core)
    "BaseModel",  # from gruponos_meltano_native import BaseModel
    # Configuration (simplified access)
    "Config",  # from gruponos_meltano_native import Config
    # Validation (simplified access)
    "DataValidator",  # from gruponos_meltano_native import DataValidator
    # Oracle Integration (simplified access)
    "EnhancedOracleConnectionManager",  # from gruponos_meltano_native import EnhancedOracleConnectionManager
    # Deprecation utilities
    "GruponosMeltanoNativeDeprecationWarning",
    "MeltanoBaseConfig",  # from gruponos_meltano_native import MeltanoBaseConfig
    "MeltanoConfig",  # from gruponos_meltano_native import MeltanoConfig
    "MeltanoError",  # from gruponos_meltano_native import MeltanoError
    # Orchestration (simplified access)
    "MeltanoOrchestrator",  # from gruponos_meltano_native import MeltanoOrchestrator
    "OracleConnectionManager",  # from gruponos_meltano_native import OracleConnectionManager
    "PipelineRunner",  # from gruponos_meltano_native import PipelineRunner
    "ServiceResult",  # from gruponos_meltano_native import ServiceResult
    "ValidationError",  # from gruponos_meltano_native import ValidationError
    # Version
    "__version__",
    "__version_info__",
    # CLI (simplified access)
    "cli_main",  # from gruponos_meltano_native import cli_main
]
