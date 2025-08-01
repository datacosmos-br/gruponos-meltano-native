"""GrupoNOS Meltano Native Exceptions.

All GrupoNOS-specific exceptions extending FLEXT core patterns.
Uses flext-core's create_module_exception_classes for DRY compliance.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import create_module_exception_classes

# DRY: Use flext-core's centralized exception factory to eliminate duplication
# This replaces 200+ lines of manual exception definitions with systematic generation
_exceptions = create_module_exception_classes("gruponos_meltano")

# Extract standard exception classes with proper names for backward compatibility
GruponosMeltanoError = _exceptions["GruponosMeltanoError"]
GruponosMeltanoValidationError = _exceptions["GruponosMeltanoValidationError"]
GruponosMeltanoConfigurationError = _exceptions["GruponosMeltanoConfigurationError"]
GruponosMeltanoConnectionError = _exceptions["GruponosMeltanoConnectionError"]
GruponosMeltanoProcessingError = _exceptions["GruponosMeltanoProcessingError"]
GruponosMeltanoAuthenticationError = _exceptions["GruponosMeltanoAuthenticationError"]
GruponosMeltanoTimeoutError = _exceptions["GruponosMeltanoTimeoutError"]


# Specialized domain-specific errors extending base classes
class GruponosMeltanoOrchestrationError(GruponosMeltanoError):
    """GrupoNOS orchestration error."""

    def __init__(
        self,
        message: str = "GrupoNOS orchestration failed",
        operation: str | None = None,
        stage: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize GrupoNOS orchestration error with context."""
        if operation is not None:
            kwargs["operation"] = operation
        if stage is not None:
            kwargs["stage"] = stage
        super().__init__(f"GrupoNOS orchestration: {message}", **kwargs)


class GruponosMeltanoPipelineError(GruponosMeltanoProcessingError):
    """GrupoNOS pipeline error."""

    def __init__(
        self,
        message: str = "GrupoNOS pipeline failed",
        pipeline_name: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize GrupoNOS pipeline error with context."""
        if pipeline_name is not None:
            kwargs["pipeline_name"] = pipeline_name
        super().__init__(f"GrupoNOS pipeline: {message}", **kwargs)


# Domain-specific error classes extending foundation hierarchy
class GruponosMeltanoAlertError(GruponosMeltanoError):
    """Alert system error."""


class GruponosMeltanoAlertDeliveryError(GruponosMeltanoAlertError):
    """Alert delivery error."""


class GruponosMeltanoDataError(GruponosMeltanoProcessingError):
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


__all__ = [
    "GruponosMeltanoAlertDeliveryError",
    "GruponosMeltanoAlertError",
    "GruponosMeltanoAuthenticationError",
    "GruponosMeltanoConfigurationError",
    "GruponosMeltanoConnectionError",
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
    "GruponosMeltanoProcessingError",
    "GruponosMeltanoSingerError",
    "GruponosMeltanoTapError",
    "GruponosMeltanoTargetError",
    "GruponosMeltanoTimeoutError",
    "GruponosMeltanoValidationError",
]
