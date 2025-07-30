"""GrupoNOS Meltano Native Exceptions.

All GrupoNOS-specific exceptions extending FLEXT core patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core.exceptions import FlextError


# GrupoNOS-specific errors - base hierarchy
class GruponosMeltanoError(FlextError):
    """Base GrupoNOS Meltano error."""


class GruponosMeltanoConfigurationError(GruponosMeltanoError):
    """GrupoNOS configuration error."""


class GruponosMeltanoOrchestrationError(GruponosMeltanoError):
    """GrupoNOS orchestration error."""


class GruponosMeltanoPipelineError(GruponosMeltanoError):
    """GrupoNOS pipeline error."""


class GruponosMeltanoValidationError(GruponosMeltanoError):
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
