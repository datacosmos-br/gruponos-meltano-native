"""GrupoNOS Meltano Native Exceptions - consolidated in flext-meltano.

This module is now a compatibility layer that imports from flext-meltano.
All new development should use flext_meltano.exceptions directly.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core.exceptions import FlextError

# Import consolidated components from flext-meltano and create local aliases
from flext_meltano.exceptions import (
    FlextMeltanoConfigurationError,
    FlextMeltanoOrchestrationError,
    FlextMeltanoPipelineError,
    FlextMeltanoValidationError,
)


# GrupoNOS-specific errors
class GruponosMeltanoError(FlextError):
    """Base GrupoNOS Meltano error."""


class GruponosMeltanoConfigurationError(FlextMeltanoConfigurationError):
    """GrupoNOS configuration error."""


class GruponosMeltanoOrchestrationError(FlextMeltanoOrchestrationError):
    """GrupoNOS orchestration error."""


class GruponosMeltanoPipelineError(FlextMeltanoPipelineError):
    """GrupoNOS pipeline error."""


class GruponosMeltanoValidationError(FlextMeltanoValidationError):
    """GrupoNOS validation error."""


class GruponosMeltanoAlertError(GruponosMeltanoError):
    """Alert system error."""


class GruponosMeltanoAlertDeliveryError(GruponosMeltanoAlertError):
    """Alert delivery error."""


class GruponosMeltanoDataError(GruponosMeltanoError):
    """Data processing error."""


class GruponosMeltanoDataQualityError(GruponosMeltanoDataError):
    """Data quality error."""


class GruponosMeltanoDataValidationError(GruponosMeltanoDataError):
    """Data validation error."""


class GruponosMeltanoMissingConfigError(GruponosMeltanoConfigurationError):
    """Missing configuration error."""


class GruponosMeltanoMonitoringError(GruponosMeltanoError):
    """Monitoring system error."""


class GruponosMeltanoOracleError(GruponosMeltanoError):
    """Oracle database error."""


class GruponosMeltanoOracleConnectionError(GruponosMeltanoOracleError):
    """Oracle connection error."""


class GruponosMeltanoOracleQueryError(GruponosMeltanoOracleError):
    """Oracle query error."""


class GruponosMeltanoOracleTimeoutError(GruponosMeltanoOracleError):
    """Oracle timeout error."""


class GruponosMeltanoPipelineTimeoutError(GruponosMeltanoPipelineError):
    """Pipeline timeout error."""


class GruponosMeltanoPipelineValidationError(GruponosMeltanoPipelineError):
    """Pipeline validation error."""


class GruponosMeltanoSingerError(GruponosMeltanoError):
    """Singer protocol error."""


class GruponosMeltanoTapError(GruponosMeltanoSingerError):
    """Tap execution error."""


class GruponosMeltanoTargetError(GruponosMeltanoSingerError):
    """Target execution error."""


# Re-export for backward compatibility
__all__ = [
    "GruponosMeltanoAlertDeliveryError",
    "GruponosMeltanoAlertError",
    "GruponosMeltanoConfigurationError",
    "GruponosMeltanoDataError",
    "GruponosMeltanoDataQualityError",
    "GruponosMeltanoDataValidationError",
    "GruponosMeltanoError",
    "GruponosMeltanoMissingConfigError",
    "GruponosMeltanoMonitoringError",
    "GruponosMeltanoOracleConnectionError",
    "GruponosMeltanoOracleError",
    "GruponosMeltanoOracleQueryError",
    "GruponosMeltanoOracleTimeoutError",
    "GruponosMeltanoOrchestrationError",
    "GruponosMeltanoPipelineError",
    "GruponosMeltanoPipelineTimeoutError",
    "GruponosMeltanoPipelineValidationError",
    "GruponosMeltanoSingerError",
    "GruponosMeltanoTapError",
    "GruponosMeltanoTargetError",
    "GruponosMeltanoValidationError",
]
