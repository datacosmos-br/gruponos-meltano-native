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

# Re-export commonly used imports from flext-core
# Foundation patterns - ALWAYS from flext-core
from flext_core import (
    BaseConfig as MeltanoBaseConfig,  # Configuration base
    DomainBaseModel as BaseModel,  # Base for meltano models
    DomainError as MeltanoError,  # Meltano-specific errors
    ServiceResult,  # Service operation results
    ValidationError as ValidationError,  # Validation errors
)

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
    "AlertManager",        # from gruponos_meltano_native import AlertManager
    # Core Patterns (from flext-core)
    "BaseModel",           # from gruponos_meltano_native import BaseModel
    # Configuration (simplified access)
    "Config",              # from gruponos_meltano_native import Config
    # Validation (simplified access)
    "DataValidator",       # from gruponos_meltano_native import DataValidator
    # Oracle Integration (simplified access)
    "EnhancedOracleConnectionManager",  # from gruponos_meltano_native import EnhancedOracleConnectionManager
    # Deprecation utilities
    "GruponosMeltanoNativeDeprecationWarning",
    "MeltanoBaseConfig",   # from gruponos_meltano_native import MeltanoBaseConfig
    "MeltanoConfig",       # from gruponos_meltano_native import MeltanoConfig
    "MeltanoError",        # from gruponos_meltano_native import MeltanoError
    # Orchestration (simplified access)
    "MeltanoOrchestrator",  # from gruponos_meltano_native import MeltanoOrchestrator
    "OracleConnectionManager",  # from gruponos_meltano_native import OracleConnectionManager
    "PipelineRunner",      # from gruponos_meltano_native import PipelineRunner
    "ServiceResult",       # from gruponos_meltano_native import ServiceResult
    "ValidationError",     # from gruponos_meltano_native import ValidationError
    # Version
    "__version__",
    "__version_info__",
    # CLI (simplified access)
    "cli_main",            # from gruponos_meltano_native import cli_main
]
