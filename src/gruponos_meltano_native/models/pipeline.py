"""Pipeline models for GrupoNOS Meltano Native - Unified FLEXT Architecture.

All pipeline-related domain models consolidated into GruponosMeltanoNativeModels
following FLEXT unified patterns with Pydantic v2 validation, FlextModels integration,
and railway-oriented programming patterns.

Copyright (c) 2025 Grupo Nós. Todos os direitos reservados. Licença: Proprietária

"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum

from flext_core import FlextModels, FlextResult, FlextTypes
from pydantic import ConfigDict, Field, computed_field

from gruponos_meltano_native.constants import GruponosMeltanoNativeConstants


class GruponosMeltanoNativeModels(FlextModels):
    """Unified pipeline models for GrupoNOS Meltano Native following FLEXT architecture.

    Single source of truth for all pipeline-related domain entities including:
    - Pipeline execution results and metrics
    - Pipeline configurations and settings
    - Pipeline status enumeration and validation
    - Railway-oriented factory methods for safe object creation

    All nested classes inherit FlextModels validation and patterns.
    """

    # =========================================================================
    # ENUMERATIONS - Pipeline status and configuration definitions
    # =========================================================================

    class PipelineStatus(StrEnum):
        """Enumeration of pipeline execution statuses using constants."""

        PENDING = GruponosMeltanoNativeConstants.Status.PENDING
        RUNNING = GruponosMeltanoNativeConstants.Status.RUNNING
        COMPLETED = GruponosMeltanoNativeConstants.Status.COMPLETED
        FAILED = GruponosMeltanoNativeConstants.Status.FAILED
        CANCELLED = GruponosMeltanoNativeConstants.Status.CANCELLED
        PAUSED = GruponosMeltanoNativeConstants.Status.PAUSED
        RETRYING = GruponosMeltanoNativeConstants.Status.RETRYING
        TIMEOUT = GruponosMeltanoNativeConstants.Status.TIMEOUT
        VALIDATING = GruponosMeltanoNativeConstants.Status.VALIDATING
        TRANSFORMING = GruponosMeltanoNativeConstants.Status.TRANSFORMING

    # =========================================================================
    # DOMAIN MODELS - Core business entities for pipeline execution
    # =========================================================================

    class PipelineResult(FlextModels.Entity):
        """Pipeline execution result with comprehensive metrics and validation.

        Contains all metrics and information about a GrupoNOS Meltano pipeline
        ETL execution, following FLEXT patterns with Pydantic v2 validation
        and domain-driven design principles.
        """

        model_config = ConfigDict(
            validate_assignment=True,
            validate_return=True,
            validate_default=True,
            use_enum_values=True,
            arbitrary_types_allowed=True,
            extra="forbid",
            frozen=False,
            strict=True,
            str_strip_whitespace=True,
            ser_json_timedelta="iso8601",
            ser_json_bytes="base64",
            hide_input_in_errors=True,
        )

        # Core identification
        pipeline_id: str = Field(..., description="Unique pipeline identifier")
        pipeline_name: str = Field(..., description="Human-readable pipeline name")
        job_name: str = Field(..., description="Associated job name for execution")

        # Status and timing with validation
        status: GruponosMeltanoNativeModels.PipelineStatus = Field(
            default="PENDING",
            description="Current pipeline execution status"
        )
        start_time: datetime = Field(..., description="Pipeline execution start timestamp")
        end_time: datetime | None = Field(None, description="Pipeline execution end timestamp")
        duration_seconds: float | None = Field(None, ge=0, description="Total execution duration in seconds")

        # Processing metrics with validation
        records_extracted: int = Field(
            default=0, ge=0, description="Number of records extracted from source"
        )
        records_transformed: int = Field(
            default=0, ge=0, description="Number of records successfully transformed"
        )
        records_loaded: int = Field(
            default=0, ge=0, description="Number of records successfully loaded to target"
        )
        records_failed: int = Field(
            default=0, ge=0, description="Number of records that failed processing"
        )

        # Quality metrics with percentage validation
        data_quality_score: float = Field(
            default=0.0, ge=0.0, le=100.0, description="Overall data quality score (0-100%)"
        )
        completeness_score: float = Field(
            default=0.0, ge=0.0, le=100.0, description="Data completeness score (0-100%)"
        )
        accuracy_score: float = Field(
            default=0.0, ge=0.0, le=100.0, description="Data accuracy score (0-100%)"
        )
        consistency_score: float = Field(
            default=0.0, ge=0.0, le=100.0, description="Data consistency score (0-100%)"
        )

        # Performance metrics
        throughput_records_per_second: float = Field(
            default=0.0, ge=0.0, description="Average processing throughput (records/second)"
        )
        memory_peak_mb: float = Field(
            default=0.0, ge=0.0, description="Peak memory usage in megabytes"
        )
        cpu_average_percent: float = Field(
            default=0.0, ge=0.0, le=100.0, description="Average CPU utilization percentage"
        )

        # Error handling and metadata
        errors: FlextTypes.List = Field(
            default_factory=list, description="List of errors encountered during execution"
        )
        warnings: FlextTypes.StringList = Field(
            default_factory=list, description="List of warnings generated during execution"
        )
        metadata: FlextTypes.Dict = Field(
            default_factory=dict, description="Additional execution metadata and context"
        )

        @computed_field
        @property
        def is_success(self) -> bool:
            """Check if pipeline execution was successful."""
            return self.status == GruponosMeltanoNativeModels.PipelineStatus.COMPLETED

        @computed_field
        @property
        def is_failed(self) -> bool:
            """Check if pipeline execution failed."""
            return self.status == GruponosMeltanoNativeModels.PipelineStatus.FAILED

        @computed_field
        @property
        def is_running(self) -> bool:
            """Check if pipeline is currently running."""
            return self.status == GruponosMeltanoNativeModels.PipelineStatus.RUNNING

        @computed_field
        @property
        def success_rate(self) -> float:
            """Calculate success rate as percentage (0-100)."""
            total_processed = self.records_extracted
            if total_processed == 0:
                return 100.0
            successful_records = self.records_loaded
            return (successful_records / total_processed) * 100.0

        @computed_field
        @property
        def error_rate(self) -> float:
            """Calculate error rate as percentage (0-100)."""
            total_processed = self.records_extracted
            if total_processed == 0:
                return 0.0
            return (self.records_failed / total_processed) * 100.0

    class PipelineMetrics(FlextModels.Value):
        """Pipeline execution metrics with comprehensive performance tracking.

        Immutable value object containing detailed metrics collected during
        pipeline execution phases including timing, resource usage, and
        throughput measurements with automatic calculations.
        """

        model_config = ConfigDict(
            validate_assignment=True,
            validate_return=True,
            validate_default=True,
            use_enum_values=True,
            arbitrary_types_allowed=True,
            extra="forbid",
            frozen=False,  # Allow method calls for recording
            strict=True,
            str_strip_whitespace=True,
            ser_json_timedelta="iso8601",
            ser_json_bytes="base64",
            hide_input_in_errors=True,
        )

        # Phase timing with automatic timestamp management
        extraction_start_time: datetime | None = Field(None, description="Extraction phase start timestamp")
        extraction_end_time: datetime | None = Field(None, description="Extraction phase end timestamp")
        transformation_start_time: datetime | None = Field(None, description="Transformation phase start timestamp")
        transformation_end_time: datetime | None = Field(None, description="Transformation phase end timestamp")
        loading_start_time: datetime | None = Field(None, description="Loading phase start timestamp")
        loading_end_time: datetime | None = Field(None, description="Loading phase end timestamp")

        # Resource usage metrics
        memory_start_mb: float = Field(default=0.0, ge=0.0, description="Memory usage at start (MB)")
        memory_peak_mb: float = Field(default=0.0, ge=0.0, description="Peak memory usage during execution (MB)")
        memory_end_mb: float = Field(default=0.0, ge=0.0, description="Memory usage at end (MB)")
        cpu_average_percent: float = Field(default=0.0, ge=0.0, le=100.0, description="Average CPU utilization (%)")

        # Throughput and processing metrics
        records_extracted: int = Field(default=0, ge=0, description="Total records extracted")
        records_transformed: int = Field(default=0, ge=0, description="Total records transformed")
        records_loaded: int = Field(default=0, ge=0, description="Total records loaded")
        records_failed: int = Field(default=0, ge=0, description="Total records failed")

        # Quality and error tracking
        data_quality_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Overall data quality score")
        validation_errors: int = Field(default=0, ge=0, description="Number of validation errors")
        transformation_errors: int = Field(default=0, ge=0, description="Number of transformation errors")
        loading_errors: int = Field(default=0, ge=0, description="Number of loading errors")

        def record_extraction_start(self) -> None:
            """Record extraction phase start timestamp."""
            self.extraction_start_time = datetime.now(UTC)

        def record_extraction_end(self, record_count: int) -> None:
            """Record extraction phase completion with record count."""
            self.extraction_end_time = datetime.now(UTC)
            self.records_extracted = record_count

        def record_transformation_start(self) -> None:
            """Record transformation phase start timestamp."""
            self.transformation_start_time = datetime.now(UTC)

        def record_transformation_end(self, record_count: int, errors: int = 0) -> None:
            """Record transformation phase completion with metrics."""
            self.transformation_end_time = datetime.now(UTC)
            self.records_transformed = record_count
            self.transformation_errors = errors

        def record_loading_start(self) -> None:
            """Record loading phase start timestamp."""
            self.loading_start_time = datetime.now(UTC)

        def record_loading_end(self, record_count: int, errors: int = 0) -> None:
            """Record loading phase completion with metrics."""
            self.loading_end_time = datetime.now(UTC)
            self.records_loaded = record_count
            self.loading_errors = errors

        @computed_field
        @property
        def total_duration_seconds(self) -> float:
            """Get total pipeline duration in seconds."""
            if self.loading_end_time and self.extraction_start_time:
                return (self.loading_end_time - self.extraction_start_time).total_seconds()
            return 0.0

        @computed_field
        @property
        def extraction_duration_seconds(self) -> float | None:
            """Get extraction phase duration in seconds."""
            if self.extraction_end_time and self.extraction_start_time:
                return (self.extraction_end_time - self.extraction_start_time).total_seconds()
            return None

        @computed_field
        @property
        def transformation_duration_seconds(self) -> float | None:
            """Get transformation phase duration in seconds."""
            if self.transformation_end_time and self.transformation_start_time:
                return (self.transformation_end_time - self.transformation_start_time).total_seconds()
            return None

        @computed_field
        @property
        def loading_duration_seconds(self) -> float | None:
            """Get loading phase duration in seconds."""
            if self.loading_end_time and self.loading_start_time:
                return (self.loading_end_time - self.loading_start_time).total_seconds()
            return None

        @computed_field
        @property
        def throughput_records_per_second(self) -> float:
            """Calculate overall throughput in records per second."""
            total_duration = self.total_duration_seconds
            if total_duration > 0:
                return self.records_loaded / total_duration
            return 0.0

    class PipelineConfiguration(FlextModels.Value):
        """Pipeline execution configuration with comprehensive validation.

        Immutable value object containing all configuration settings for
        pipeline execution including extractor/loader settings, performance
        parameters, and quality monitoring configuration.
        """

        model_config = ConfigDict(
            validate_assignment=True,
            validate_return=True,
            validate_default=True,
            use_enum_values=True,
            arbitrary_types_allowed=True,
            extra="forbid",
            frozen=True,  # Immutable configuration
            strict=True,
            str_strip_whitespace=True,
            ser_json_timedelta="iso8601",
            ser_json_bytes="base64",
            hide_input_in_errors=True,
        )

        # Core identification
        name: str = Field(..., description="Pipeline configuration name")
        job_name: str = Field(..., description="Associated job name")
        environment: str = Field(default="dev", description="Execution environment (dev/staging/prod)")

        # Extractor configuration with validation
        extractor_name: str = Field(default="", description="Name of the extractor to use")
        extractor_config: FlextTypes.Dict = Field(
            default_factory=dict, description="Extractor-specific configuration parameters"
        )

        # Loader configuration with validation
        loader_name: str = Field(default="", description="Name of the loader to use")
        loader_config: FlextTypes.Dict = Field(
            default_factory=dict, description="Loader-specific configuration parameters"
        )

        # Pipeline execution settings
        batch_size: int = Field(
            default=5000, ge=1, le=100000, description="Number of records to process in each batch"
        )
        timeout_seconds: int = Field(
            default=1800, ge=60, le=86400, description="Maximum execution time in seconds"
        )
        max_retries: int = Field(
            default=3, ge=0, le=10, description="Maximum number of retry attempts"
        )
        enable_incremental: bool = Field(
            default=False, description="Whether to use incremental sync mode"
        )

        # Quality assurance settings
        enable_quality_checks: bool = Field(
            default=True, description="Whether to perform data quality checks"
        )
        quality_threshold: float = Field(
            default=95.0, ge=0.0, le=100.0, description="Minimum quality score required (%)"
        )

        # Monitoring and metrics settings
        enable_monitoring: bool = Field(
            default=True, description="Whether to enable pipeline monitoring"
        )
        collect_metrics: bool = Field(
            default=True, description="Whether to collect detailed execution metrics"
        )

        @computed_field
        @property
        def is_full_sync(self) -> bool:
            """Check if this configuration uses full sync mode."""
            return not self.enable_incremental

        @computed_field
        @property
        def is_incremental_sync(self) -> bool:
            """Check if this configuration uses incremental sync mode."""
            return self.enable_incremental

    # =========================================================================
    # FACTORY METHODS - Railway-oriented creation patterns
    # =========================================================================

    @classmethod
    def create_pipeline_result(
        cls,
        pipeline_id: str,
        pipeline_name: str,
        job_name: str,
        status: GruponosMeltanoNativeModels.PipelineStatus | None = None,
    ) -> FlextResult[GruponosMeltanoNativeModels.PipelineResult]:
        """Create a new pipeline result with validation using railway pattern.

        Args:
            pipeline_id: Unique pipeline identifier
            pipeline_name: Human-readable pipeline name
            job_name: Associated job name
            status: Optional initial status (defaults to PENDING)

        Returns:
            FlextResult[PipelineResult]: Success with validated result or failure

        Example:
            >>> result = GruponosMeltanoNativeModels.create_pipeline_result(
            ...     pipeline_id="pipe-123",
            ...     pipeline_name="Customer Data Pipeline",
            ...     job_name="daily-sync",
            ...     status=GruponosMeltanoNativeModels.PipelineStatus.RUNNING
            ... )
            >>> if result.is_success:
            ...     pipeline_result = result.unwrap()
            ...     print(f"Created result for: {pipeline_result.pipeline_name}")

        """
        try:
            pipeline_result = cls.PipelineResult(
                pipeline_id=pipeline_id,
                pipeline_name=pipeline_name,
                job_name=job_name,
                status=status or cls.PipelineStatus.PENDING,
                start_time=datetime.now(UTC),
            )
            return FlextResult[cls.PipelineResult].ok(pipeline_result)
        except Exception as e:
            return FlextResult[cls.PipelineResult].fail(f"Failed to create pipeline result: {e!s}")

    @classmethod
    def create_pipeline_config(
        cls,
        name: str,
        job_name: str,
        extractor_name: str,
        loader_name: str,
        environment: str = "dev",
    ) -> FlextResult[GruponosMeltanoNativeModels.PipelineConfiguration]:
        """Create a new pipeline configuration with validation.

        Args:
            name: Configuration name
            job_name: Associated job name
            extractor_name: Name of the extractor
            loader_name: Name of the loader
            environment: Execution environment

        Returns:
            FlextResult[PipelineConfiguration]: Success with validated config or failure

        Example:
            >>> result = GruponosMeltanoNativeModels.create_pipeline_config(
            ...     name="customer-etl",
            ...     job_name="daily-extract",
            ...     extractor_name="tap-mysql",
            ...     loader_name="target-postgres",
            ...     environment="production"
            ... )

        """
        try:
            config = cls.PipelineConfiguration(
                name=name,
                job_name=job_name,
                extractor_name=extractor_name,
                loader_name=loader_name,
                environment=environment,
            )
            return FlextResult[cls.PipelineConfiguration].ok(config)
        except Exception as e:
            return FlextResult[cls.PipelineConfiguration].fail(f"Failed to create pipeline config: {e!s}")


# =========================================================================
# MODULE EXPORTS - Unified access pattern
# =========================================================================

__all__ = ["GruponosMeltanoNativeModels"]
