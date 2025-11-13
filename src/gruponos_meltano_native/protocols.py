"""GrupoNOS Meltano Native Protocols - Type protocols for the project.

Provides type protocols and interfaces for GrupoNOS Meltano Native components.
Uses flext-core protocol patterns for consistency and enterprise-grade type safety.

Copyright (c) 2025 Grupo Nós. Todos os direitos reservados.
SPDX-License-Identifier: Proprietary
"""

from __future__ import annotations

from typing import Protocol

from flext_core import FlextProtocols, FlextResult


class GruponosMeltanoNativeProtocols(FlextProtocols):
    """GrupoNOS Meltano Native Protocols namespace class.

    Contains protocol definitions for the GrupoNOS Meltano Native project.
    Extends FlextProtocols for consistency with FLEXT ecosystem and enterprise patterns.

    All protocols follow Railway Pattern with FlextResult for error handling.
    """

    class ConfigValidator(Protocol):
        """Protocol for configuration validation with enterprise error handling."""

        def validate_config(self, config: dict[str, object]) -> FlextResult[bool]:
            """Validate configuration using Railway Pattern.

            Args:
                config: Configuration dictionary to validate

            Returns:
                FlextResult[bool]: Success with validation result or failure with errors

            """
            ...

    class PipelineExecutor(Protocol):
        """Protocol for pipeline execution with comprehensive error handling."""

        def execute_pipeline(
            self, pipeline_name: str, **kwargs: object
        ) -> FlextResult[dict[str, object]]:
            """Execute a pipeline by name with Railway Pattern error handling.

            Args:
                pipeline_name: Name of the pipeline to execute
                **kwargs: Additional execution parameters

            Returns:
                FlextResult[Dict]: Success with execution results or failure with errors

            """
            ...

    class Orchestrator(Protocol):
        """Protocol for Meltano orchestration operations."""

        def run_full_sync(self) -> FlextResult[dict[str, object]]:
            """Execute full synchronization pipeline.

            Returns:
                FlextResult[Dict]: Success with sync results or failure with errors

            """
            ...

        def run_incremental_sync(self) -> FlextResult[dict[str, object]]:
            """Execute incremental synchronization pipeline.

            Returns:
                FlextResult[Dict]: Success with sync results or failure with errors

            """
            ...

        def validate_configuration(self) -> FlextResult[None]:
            """Validate orchestrator configuration.

            Returns:
                FlextResult[None]: Success or failure with validation errors

            """
            ...

    class AlertHandler(Protocol):
        """Protocol for enterprise alert handling with severity levels."""

        def send_alert(
            self,
            message: str,
            severity: str,
            metadata: dict[str, object] | None = None,
        ) -> FlextResult[None]:
            """Send an alert with Railway Pattern error handling.

            Args:
                message: Alert message
                severity: Alert severity level (INFO, WARNING, ERROR, CRITICAL)
                metadata: Additional alert metadata

            Returns:
                FlextResult[None]: Success or failure with alert sending errors

            """
            ...

    class DataValidator(Protocol):
        """Protocol for comprehensive data validation."""

        def validate_batch(
            self, data: list[dict[str, object]], schema: dict[str, object]
        ) -> FlextResult[list[str]]:
            """Validate batch of data against schema with detailed error reporting.

            Args:
                data: List of data dictionaries to validate
                schema: Validation schema definition

            Returns:
                FlextResult[List[str]]: Success with empty list or failure with validation errors

            """
            ...

    class MonitoringService(Protocol):
        """Protocol for enterprise monitoring and observability."""

        def record_metric(
            self, name: str, value: float, tags: dict[str, object] | None = None
        ) -> FlextResult[None]:
            """Record a metric with optional tags.

            Args:
                name: Metric name
                value: Metric value
                tags: Optional metric tags

            Returns:
                FlextResult[None]: Success or failure with metric recording errors

            """
            ...

        def start_timer(self, name: str) -> FlextResult[str]:
            """Start a timer for performance monitoring.

            Args:
                name: Timer name

            Returns:
                FlextResult[str]: Success with timer ID or failure with errors

            """
            ...

        def stop_timer(self, timer_id: str) -> FlextResult[float]:
            """Stop a timer and return elapsed time.

            Args:
                timer_id: Timer ID returned from start_timer

            Returns:
                FlextResult[float]: Success with elapsed time or failure with errors

            """
            ...


# Export protocols namespace
__all__ = ["GruponosMeltanoNativeProtocols"]
