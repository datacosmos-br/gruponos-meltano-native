"""GrupoNOS Meltano Native Protocols - Type protocols for the project.

Provides type protocols and interfaces for GrupoNOS Meltano Native components.
Uses flext-core protocol patterns for consistency and enterprise-grade type safety.

Copyright (c) 2025 Grupo Nós. Todos os direitos reservados.
SPDX-License-Identifier: Proprietary
"""

from __future__ import annotations

from typing import Protocol

from flext_core import FlextCore


class GruponosMeltanoNativeProtocols(FlextCore.Protocols):
    """GrupoNOS Meltano Native Protocols namespace class.

    Contains protocol definitions for the GrupoNOS Meltano Native project.
    Extends FlextCore.Protocols for consistency with FLEXT ecosystem and enterprise patterns.

    All protocols follow Railway Pattern with FlextCore.Result for error handling.
    """

    class ConfigValidator(Protocol):
        """Protocol for configuration validation with enterprise error handling."""

        def validate_config(self, config: FlextCore.Types.Dict) -> FlextCore.Result[bool]:
            """Validate configuration using Railway Pattern.

            Args:
                config: Configuration dictionary to validate

            Returns:
                FlextCore.Result[bool]: Success with validation result or failure with errors

            """
            ...

    class PipelineExecutor(Protocol):
        """Protocol for pipeline execution with comprehensive error handling."""

        def execute_pipeline(
            self, pipeline_name: str, **kwargs: object
        ) -> FlextCore.Result[FlextCore.Types.Dict]:
            """Execute a pipeline by name with Railway Pattern error handling.

            Args:
                pipeline_name: Name of the pipeline to execute
                **kwargs: Additional execution parameters

            Returns:
                FlextCore.Result[Dict]: Success with execution results or failure with errors

            """
            ...

    class Orchestrator(Protocol):
        """Protocol for Meltano orchestration operations."""

        def run_full_sync(self) -> FlextCore.Result[FlextCore.Types.Dict]:
            """Execute full synchronization pipeline.

            Returns:
                FlextCore.Result[Dict]: Success with sync results or failure with errors

            """
            ...

        def run_incremental_sync(self) -> FlextCore.Result[FlextCore.Types.Dict]:
            """Execute incremental synchronization pipeline.

            Returns:
                FlextCore.Result[Dict]: Success with sync results or failure with errors

            """
            ...

        def validate_configuration(self) -> FlextCore.Result[None]:
            """Validate orchestrator configuration.

            Returns:
                FlextCore.Result[None]: Success or failure with validation errors

            """
            ...

    class AlertHandler(Protocol):
        """Protocol for enterprise alert handling with severity levels."""

        def send_alert(
            self, message: str, severity: str, metadata: FlextCore.Types.Dict | None = None
        ) -> FlextCore.Result[None]:
            """Send an alert with Railway Pattern error handling.

            Args:
                message: Alert message
                severity: Alert severity level (INFO, WARNING, ERROR, CRITICAL)
                metadata: Additional alert metadata

            Returns:
                FlextCore.Result[None]: Success or failure with alert sending errors

            """
            ...

    class DataValidator(Protocol):
        """Protocol for comprehensive data validation."""

        def validate_batch(
            self, data: list[FlextCore.Types.Dict], schema: FlextCore.Types.Dict
        ) -> FlextCore.Result[list[str]]:
            """Validate batch of data against schema with detailed error reporting.

            Args:
                data: List of data dictionaries to validate
                schema: Validation schema definition

            Returns:
                FlextCore.Result[List[str]]: Success with empty list or failure with validation errors

            """
            ...

    class MonitoringService(Protocol):
        """Protocol for enterprise monitoring and observability."""

        def record_metric(
            self, name: str, value: float, tags: FlextCore.Types.Dict | None = None
        ) -> FlextCore.Result[None]:
            """Record a metric with optional tags.

            Args:
                name: Metric name
                value: Metric value
                tags: Optional metric tags

            Returns:
                FlextCore.Result[None]: Success or failure with metric recording errors

            """
            ...

        def start_timer(self, name: str) -> FlextCore.Result[str]:
            """Start a timer for performance monitoring.

            Args:
                name: Timer name

            Returns:
                FlextCore.Result[str]: Success with timer ID or failure with errors

            """
            ...

        def stop_timer(self, timer_id: str) -> FlextCore.Result[float]:
            """Stop a timer and return elapsed time.

            Args:
                timer_id: Timer ID returned from start_timer

            Returns:
                FlextCore.Result[float]: Success with elapsed time or failure with errors

            """
            ...


# Export protocols namespace
__all__ = ["GruponosMeltanoNativeProtocols"]
