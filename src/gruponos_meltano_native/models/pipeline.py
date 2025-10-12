"""Pipeline models for GrupoNOS Meltano Native.

This module contains all pipeline-related domain models and data structures
used by the GrupoNOS Meltano Native orchestrator.

Copyright (c) 2025 Grupo Nós. Todos os direitos reservados. Licença: Proprietária
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from gruponos_meltano_native.constants import GruponosMeltanoConstants


@dataclass
class PipelineResult:
    """Resultado de uma execução de pipeline Meltano GrupoNOS.

    Contém todas as métricas e informações sobre a execução
    de um pipeline ETL, seguindo padrões FLEXT.
    """

    # Identificação
    pipeline_id: str
    pipeline_name: str
    job_name: str

    # Status e timing
    status: str  # SUCCESS, FAILED, RUNNING, etc.
    start_time: datetime
    end_time: datetime | None = None
    duration_seconds: float | None = None

    # Métricas de processamento
    records_extracted: int = 0
    records_transformed: int = 0
    records_loaded: int = 0
    records_failed: int = 0

    # Métricas de qualidade
    data_quality_score: float = 0.0
    completeness_score: float = 0.0
    accuracy_score: float = 0.0
    consistency_score: float = 0.0

    # Performance metrics
    throughput_records_per_second: float = 0.0
    memory_peak_mb: float = 0.0
    cpu_average_percent: float = 0.0

    # Erros e warnings
    errors: list[dict[str, Any]] = None
    warnings: list[str] = None

    # Metadata adicional
    metadata: dict[str, Any] = None

    def __post_init__(self) -> None:
        """Initialize defaults for mutable fields."""
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
        if self.metadata is None:
            self.metadata = {}

    @property
    def is_success(self) -> bool:
        """Check if pipeline execution was successful."""
        return self.status == GruponosMeltanoConstants.Status.SUCCESS

    @property
    def is_failed(self) -> bool:
        """Check if pipeline execution failed."""
        return self.status == GruponosMeltanoConstants.Status.FAILED

    @property
    def is_running(self) -> bool:
        """Check if pipeline is currently running."""
        return self.status == GruponosMeltanoConstants.Status.RUNNING

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        total_processed = self.records_extracted
        if total_processed == 0:
            return 100.0
        successful_records = self.records_loaded
        return (successful_records / total_processed) * 100.0

    @property
    def error_rate(self) -> float:
        """Calculate error rate as percentage."""
        total_processed = self.records_extracted
        if total_processed == 0:
            return 0.0
        return (self.records_failed / total_processed) * 100.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "pipeline_id": self.pipeline_id,
            "pipeline_name": self.pipeline_name,
            "job_name": self.job_name,
            "status": self.status,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration_seconds,
            "records_extracted": self.records_extracted,
            "records_transformed": self.records_transformed,
            "records_loaded": self.records_loaded,
            "records_failed": self.records_failed,
            "data_quality_score": self.data_quality_score,
            "completeness_score": self.completeness_score,
            "accuracy_score": self.accuracy_score,
            "consistency_score": self.consistency_score,
            "throughput_records_per_second": self.throughput_records_per_second,
            "memory_peak_mb": self.memory_peak_mb,
            "cpu_average_percent": self.cpu_average_percent,
            "errors": self.errors,
            "warnings": self.warnings,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PipelineResult:
        """Create instance from dictionary."""
        # Convert ISO strings back to datetime
        start_time = None
        if data.get("start_time"):
            start_time = datetime.fromisoformat(data["start_time"])

        end_time = None
        if data.get("end_time"):
            end_time = datetime.fromisoformat(data["end_time"])

        return cls(
            pipeline_id=data["pipeline_id"],
            pipeline_name=data["pipeline_name"],
            job_name=data["job_name"],
            status=data["status"],
            start_time=start_time,
            end_time=end_time,
            duration_seconds=data.get("duration_seconds"),
            records_extracted=data.get("records_extracted", 0),
            records_transformed=data.get("records_transformed", 0),
            records_loaded=data.get("records_loaded", 0),
            records_failed=data.get("records_failed", 0),
            data_quality_score=data.get("data_quality_score", 0.0),
            completeness_score=data.get("completeness_score", 0.0),
            accuracy_score=data.get("accuracy_score", 0.0),
            consistency_score=data.get("consistency_score", 0.0),
            throughput_records_per_second=data.get("throughput_records_per_second", 0.0),
            memory_peak_mb=data.get("memory_peak_mb", 0.0),
            cpu_average_percent=data.get("cpu_average_percent", 0.0),
            errors=data.get("errors", []),
            warnings=data.get("warnings", []),
            metadata=data.get("metadata", {})
        )


@dataclass
class PipelineMetrics:
    """Metrics collected during pipeline execution."""

    # Performance metrics
    extraction_start_time: datetime | None = None
    extraction_end_time: datetime | None = None
    transformation_start_time: datetime | None = None
    transformation_end_time: datetime | None = None
    loading_start_time: datetime | None = None
    loading_end_time: datetime | None = None

    # Resource usage
    memory_start_mb: float = 0.0
    memory_peak_mb: float = 0.0
    memory_end_mb: float = 0.0
    cpu_average_percent: float = 0.0

    # Throughput metrics
    records_extracted: int = 0
    records_transformed: int = 0
    records_loaded: int = 0
    records_failed: int = 0

    # Quality metrics
    data_quality_score: float = 0.0
    validation_errors: int = 0
    transformation_errors: int = 0
    loading_errors: int = 0

    def record_extraction_start(self) -> None:
        """Record extraction phase start."""
        self.extraction_start_time = datetime.now()

    def record_extraction_end(self, record_count: int) -> None:
        """Record extraction phase end."""
        self.extraction_end_time = datetime.now()
        self.records_extracted = record_count

    def record_transformation_start(self) -> None:
        """Record transformation phase start."""
        self.transformation_start_time = datetime.now()

    def record_transformation_end(self, record_count: int, errors: int = 0) -> None:
        """Record transformation phase end."""
        self.transformation_end_time = datetime.now()
        self.records_transformed = record_count
        self.transformation_errors = errors

    def record_loading_start(self) -> None:
        """Record loading phase start."""
        self.loading_start_time = datetime.now()

    def record_loading_end(self, record_count: int, errors: int = 0) -> None:
        """Record loading phase end."""
        self.loading_end_time = datetime.now()
        self.records_loaded = record_count
        self.loading_errors = errors

    def calculate_throughput(self) -> float:
        """Calculate overall throughput in records per second."""
        total_duration = self.get_total_duration_seconds()
        if total_duration > 0:
            return self.records_loaded / total_duration
        return 0.0

    def get_total_duration_seconds(self) -> float:
        """Get total pipeline duration in seconds."""
        if self.loading_end_time and self.extraction_start_time:
            return (self.loading_end_time - self.extraction_start_time).total_seconds()
        return 0.0

    def get_extraction_duration(self) -> float | None:
        """Get extraction phase duration in seconds."""
        if self.extraction_end_time and self.extraction_start_time:
            return (self.extraction_end_time - self.extraction_start_time).total_seconds()
        return None

    def get_transformation_duration(self) -> float | None:
        """Get transformation phase duration in seconds."""
        if self.transformation_end_time and self.transformation_start_time:
            return (self.transformation_end_time - self.transformation_start_time).total_seconds()
        return None

    def get_loading_duration(self) -> float | None:
        """Get loading phase duration in seconds."""
        if self.loading_end_time and self.loading_start_time:
            return (self.loading_end_time - self.loading_start_time).total_seconds()
        return None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "extraction_start_time": self.extraction_start_time.isoformat() if self.extraction_start_time else None,
            "extraction_end_time": self.extraction_end_time.isoformat() if self.extraction_end_time else None,
            "transformation_start_time": self.transformation_start_time.isoformat() if self.transformation_start_time else None,
            "transformation_end_time": self.transformation_end_time.isoformat() if self.transformation_end_time else None,
            "loading_start_time": self.loading_start_time.isoformat() if self.loading_start_time else None,
            "loading_end_time": self.loading_end_time.isoformat() if self.loading_end_time else None,
            "memory_start_mb": self.memory_start_mb,
            "memory_peak_mb": self.memory_peak_mb,
            "memory_end_mb": self.memory_end_mb,
            "cpu_average_percent": self.cpu_average_percent,
            "records_extracted": self.records_extracted,
            "records_transformed": self.records_transformed,
            "records_loaded": self.records_loaded,
            "records_failed": self.records_failed,
            "data_quality_score": self.data_quality_score,
            "validation_errors": self.validation_errors,
            "transformation_errors": self.transformation_errors,
            "loading_errors": self.loading_errors
        }


@dataclass
class PipelineConfiguration:
    """Configuration for a pipeline execution."""

    name: str
    job_name: str
    environment: str = "dev"

    # Extractor configuration
    extractor_name: str = ""
    extractor_config: dict[str, Any] = None

    # Loader configuration
    loader_name: str = ""
    loader_config: dict[str, Any] = None

    # Pipeline settings
    batch_size: int = 5000
    timeout_seconds: int = 1800
    max_retries: int = 3
    enable_incremental: bool = False

    # Quality settings
    enable_quality_checks: bool = True
    quality_threshold: float = 95.0

    # Monitoring settings
    enable_monitoring: bool = True
    collect_metrics: bool = True

    def __post_init__(self) -> None:
        """Initialize defaults for mutable fields."""
        if self.extractor_config is None:
            self.extractor_config = {}
        if self.loader_config is None:
            self.loader_config = {}

    def is_full_sync(self) -> bool:
        """Check if this is a full sync pipeline."""
        return not self.enable_incremental

    def is_incremental_sync(self) -> bool:
        """Check if this is an incremental sync pipeline."""
        return self.enable_incremental

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "job_name": self.job_name,
            "environment": self.environment,
            "extractor_name": self.extractor_name,
            "extractor_config": self.extractor_config,
            "loader_name": self.loader_name,
            "loader_config": self.loader_config,
            "batch_size": self.batch_size,
            "timeout_seconds": self.timeout_seconds,
            "max_retries": self.max_retries,
            "enable_incremental": self.enable_incremental,
            "enable_quality_checks": self.enable_quality_checks,
            "quality_threshold": self.quality_threshold,
            "enable_monitoring": self.enable_monitoring,
            "collect_metrics": self.collect_metrics
        }


class PipelineStatus:
    """Enumeration of pipeline execution statuses."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    TIMEOUT = "TIMEOUT"
    PARTIAL_SUCCESS = "PARTIAL_SUCCESS"
