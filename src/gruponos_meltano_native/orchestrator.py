"""GrupoNOS Meltano Native Orchestrator - GRUPONOS specific implementation.

This module provides all GrupoNOS-specific orchestration for Meltano pipelines
with Oracle WMS systems, built on FLEXT foundation patterns.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from gruponos_meltano_native.config import GruponosMeltanoSettings

# =============================================
# GRUPONOS PIPELINE RESULTS
# =============================================


@dataclass
class GruponosMeltanoPipelineResult:
    """Result of a GrupoNOS Meltano pipeline execution."""

    success: bool
    job_name: str
    execution_time: float
    output: str
    error: str | None = None
    metadata: dict[str, Any] | None = None


# =============================================
# GRUPONOS PIPELINE RUNNER
# =============================================


class GruponosMeltanoPipelineRunner:
    """GrupoNOS-specific Meltano pipeline runner."""

    def __init__(self, settings: GruponosMeltanoSettings) -> None:
        """Initialize pipeline runner with GrupoNOS settings."""
        self.settings = settings
        self.project_root = Path(settings.meltano_project_root)

    def run_pipeline(
        self, job_name: str, **kwargs: Any,
    ) -> GruponosMeltanoPipelineResult:
        """Run a GrupoNOS Meltano pipeline."""
        import time

        start_time = time.time()

        try:
            # Build meltano command
            cmd = ["meltano", "run", job_name]

            # Set environment variables for GrupoNOS
            env = self._build_environment()

            # Execute pipeline
            result = subprocess.run(
                cmd,
                check=False,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                env=env,
                timeout=3600,  # 1 hour timeout
            )

            execution_time = time.time() - start_time

            if result.returncode == 0:
                return GruponosMeltanoPipelineResult(
                    success=True,
                    job_name=job_name,
                    execution_time=execution_time,
                    output=result.stdout,
                    metadata={"return_code": result.returncode},
                )
            return GruponosMeltanoPipelineResult(
                success=False,
                job_name=job_name,
                execution_time=execution_time,
                output=result.stdout,
                error=result.stderr,
                metadata={"return_code": result.returncode},
            )

        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            return GruponosMeltanoPipelineResult(
                success=False,
                job_name=job_name,
                execution_time=execution_time,
                output="",
                error="Pipeline execution timed out",
                metadata={"timeout": True},
            )
        except Exception as e:
            execution_time = time.time() - start_time
            return GruponosMeltanoPipelineResult(
                success=False,
                job_name=job_name,
                execution_time=execution_time,
                output="",
                error=str(e),
                metadata={"exception": type(e).__name__},
            )

    def _build_environment(self) -> dict[str, str]:
        """Build environment variables for GrupoNOS pipelines."""
        import os

        env = os.environ.copy()

        # Add GrupoNOS-specific environment variables
        env.update(
            {
                "MELTANO_ENVIRONMENT": self.settings.meltano_environment,
                "MELTANO_PROJECT_ROOT": str(self.project_root),
                # Oracle WMS configuration
                "TAP_ORACLE_WMS_BASE_URL": self.settings.wms_source.base_url,
                "TAP_ORACLE_WMS_USERNAME": self.settings.wms_source.username,
                "TAP_ORACLE_WMS_PASSWORD": self.settings.wms_source.password.get_secret_value(),
                "TAP_ORACLE_WMS_COMPANY_CODE": self.settings.wms_source.company_code,
                "TAP_ORACLE_WMS_FACILITY_CODE": self.settings.wms_source.facility_code,
                # Oracle target configuration
                "FLEXT_TARGET_ORACLE_HOST": self.settings.oracle_connection.host,
                "FLEXT_TARGET_ORACLE_PORT": str(self.settings.oracle_connection.port),
                "FLEXT_TARGET_ORACLE_USERNAME": self.settings.oracle_connection.username,
                "FLEXT_TARGET_ORACLE_PASSWORD": self.settings.oracle_connection.password.get_secret_value(),
                "FLEXT_TARGET_ORACLE_SCHEMA": self.settings.target_oracle.target_schema,
            },
        )

        # Add service name or SID
        if self.settings.oracle_connection.service_name:
            env["FLEXT_TARGET_ORACLE_SERVICE_NAME"] = (
                self.settings.oracle_connection.service_name
            )
        elif self.settings.oracle_connection.sid:
            env["FLEXT_TARGET_ORACLE_SID"] = self.settings.oracle_connection.sid

        return env

    async def run_with_retry(
        self, job_name: str, max_retries: int = 3, **kwargs: Any,
    ) -> GruponosMeltanoPipelineResult:
        """Run pipeline with retry logic."""
        import asyncio

        last_result = None
        for attempt in range(max_retries + 1):
            try:
                # Execute in thread pool to avoid blocking
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None, self.run_pipeline, job_name, **kwargs,
                )

                if result.success:
                    return result

                last_result = result
                if attempt < max_retries:
                    await asyncio.sleep(2**attempt)  # Exponential backoff

            except Exception as e:
                last_result = GruponosMeltanoPipelineResult(
                    success=False,
                    job_name=job_name,
                    execution_time=0.0,
                    output="",
                    error=str(e),
                    metadata={"attempt": attempt + 1, "exception": type(e).__name__},
                )

                if attempt < max_retries:
                    await asyncio.sleep(2**attempt)

        return last_result or GruponosMeltanoPipelineResult(
            success=False,
            job_name=job_name,
            execution_time=0.0,
            output="",
            error="All retry attempts failed",
            metadata={"max_retries": max_retries},
        )


# =============================================
# GRUPONOS ORCHESTRATOR
# =============================================


class GruponosMeltanoOrchestrator:
    """Main GrupoNOS Meltano orchestrator."""

    def __init__(self, settings: GruponosMeltanoSettings | None = None) -> None:
        """Initialize orchestrator with GrupoNOS settings."""
        self.settings = settings or GruponosMeltanoSettings()
        self.pipeline_runner = GruponosMeltanoPipelineRunner(self.settings)

    def run_full_sync(self) -> GruponosMeltanoPipelineResult:
        """Run full sync job for GrupoNOS."""
        return self.pipeline_runner.run_pipeline("full-sync-job")

    def run_incremental_sync(self) -> GruponosMeltanoPipelineResult:
        """Run incremental sync job for GrupoNOS."""
        return self.pipeline_runner.run_pipeline("incremental-sync-job")

    def run_job(self, job_name: str) -> GruponosMeltanoPipelineResult:
        """Run specific job by name."""
        return self.pipeline_runner.run_pipeline(job_name)

    def list_jobs(self) -> list[str]:
        """List available jobs."""
        # Based on meltano.yml configuration
        return ["full-sync-job", "incremental-sync-job"]

    def list_pipelines(self) -> list[str]:
        """List available pipelines (alias for list_jobs)."""
        return self.list_jobs()

    async def run_pipeline(
        self, pipeline_name: str, **kwargs: Any,
    ) -> GruponosMeltanoPipelineResult:
        """Run pipeline asynchronously (compatibility method)."""
        import asyncio

        # Execute in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self.pipeline_runner.run_pipeline, pipeline_name, **kwargs,
        )

    def get_job_status(self, job_name: str) -> dict[str, Any]:
        """Get status of a specific job."""
        return {
            "job_name": job_name,
            "available": job_name in self.list_jobs(),
            "settings": self.settings.dict(),
        }


# =============================================
# FACTORY FUNCTIONS
# =============================================


def create_gruponos_meltano_orchestrator(
    settings: GruponosMeltanoSettings | None = None,
) -> GruponosMeltanoOrchestrator:
    """Create GrupoNOS Meltano orchestrator instance."""
    return GruponosMeltanoOrchestrator(settings)


def create_gruponos_meltano_pipeline_runner(
    settings: GruponosMeltanoSettings | None = None,
) -> GruponosMeltanoPipelineRunner:
    """Create GrupoNOS pipeline runner instance."""
    pipeline_settings = settings or GruponosMeltanoSettings()
    return GruponosMeltanoPipelineRunner(pipeline_settings)


# Re-export for backward compatibility
__all__ = [
    "GruponosMeltanoOrchestrator",
    "GruponosMeltanoPipelineResult",
    "GruponosMeltanoPipelineRunner",
    "create_gruponos_meltano_orchestrator",
    "create_gruponos_meltano_pipeline_runner",
]
