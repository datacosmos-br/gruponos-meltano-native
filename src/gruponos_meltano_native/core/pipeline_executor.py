"""Pipeline executor for GrupoNOS Meltano Native.

This module contains the core pipeline execution logic and Meltano integration,
separated from the main orchestrator for better modularity and maintainability.

Copyright (c) 2025 Grupo Nós. Todos os direitos reservados. Licença: Proprietária
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any

from gruponos_meltano_native.config import GruponosMeltanoNativeConfig
from gruponos_meltano_native.models.pipeline import (
    PipelineConfiguration,
    PipelineMetrics,
    PipelineResult,
)


class MeltanoPipelineExecutor:
    """Executor for Meltano pipeline operations.

    Handles the low-level interaction with Meltano CLI and process management.
    Separated from orchestrator for better testability and maintainability.
    """

    def __init__(self, config: GruponosMeltanoNativeConfig) -> None:
        self.config = config
        self.logger = FlextLogger.get_logger(__name__)

    def execute_pipeline(
        self, job_name: str, config: PipelineConfiguration
    ) -> FlextResult[PipelineResult]:
        """Execute a Meltano pipeline job.

        Args:
            job_name: Name of the Meltano job to execute
            config: Pipeline configuration

        Returns:
            PipelineResult with execution details

        """
        try:
            self.logger.info(f"Starting pipeline execution: {job_name}")

            # Validate job name
            validated_job_name = self._validate_job_name(job_name)
            if not validated_job_name:
                return FlextResult[PipelineResult].fail(f"Invalid job name: {job_name}")

            # Build environment
            env = self._build_meltano_environment()

            # Execute pipeline
            result = self._execute_meltano_pipeline(validated_job_name, env)

            if result.is_success:
                pipeline_result = result.unwrap()
                self.logger.info(f"Pipeline execution completed: {job_name}")
                return FlextResult[PipelineResult].ok(pipeline_result)
            error_msg = f"Pipeline execution failed: {result.error}"
            self.logger.error(error_msg)
            return FlextResult[PipelineResult].fail(error_msg)

        except Exception as e:
            error_msg = f"Unexpected error during pipeline execution: {e!s}"
            self.logger.exception(error_msg)
            return FlextResult[PipelineResult].fail(error_msg)

    def get_job_status(self, job_name: str) -> FlextResult[dict[str, Any]]:
        """Get status of a Meltano job.

        Args:
            job_name: Name of the job to check

        Returns:
            Job status information

        """
        try:
            # Build environment
            env = self._build_meltano_environment()

            # Run meltano job list to get status
            cmd = ["meltano", "job", "list", "--format", "json"]
            result = subprocess.run(
                cmd, check=False, capture_output=True, text=True, env=env, timeout=30
            )

            if result.returncode != 0:
                return FlextResult[dict[str, Any]].fail(
                    f"Failed to get job status: {result.stderr}"
                )

            # Parse JSON output
            import json

            jobs_data = json.loads(result.stdout)

            # Find the specific job
            for job in jobs_data.get("jobs", []):
                if job.get("name") == job_name:
                    return FlextResult[dict[str, Any]].ok(job)

            return FlextResult[dict[str, Any]].fail(f"Job not found: {job_name}")

        except subprocess.TimeoutExpired:
            return FlextResult[dict[str, Any]].fail("Job status check timed out")
        except json.JSONDecodeError as e:
            return FlextResult[dict[str, Any]].fail(f"Invalid JSON response: {e!s}")
        except Exception as e:
            return FlextResult[dict[str, Any]].fail(f"Unexpected error: {e!s}")

    def list_jobs(self) -> FlextResult[list[str]]:
        """List all available Meltano jobs.

        Returns:
            List of job names

        """
        try:
            env = self._build_meltano_environment()

            cmd = ["meltano", "job", "list", "--format", "json"]
            result = subprocess.run(
                cmd, check=False, capture_output=True, text=True, env=env, timeout=30
            )

            if result.returncode != 0:
                return FlextResult[list[str]].fail(
                    f"Failed to list jobs: {result.stderr}"
                )

            import json

            jobs_data = json.loads(result.stdout)
            job_names = [job["name"] for job in jobs_data.get("jobs", [])]

            return FlextResult[list[str]].ok(job_names)

        except Exception as e:
            return FlextResult[list[str]].fail(f"Failed to list jobs: {e!s}")

    def list_pipelines(self) -> FlextResult[list[str]]:
        """List all available Meltano pipelines.

        Returns:
            List of pipeline names

        """
        try:
            env = self._build_meltano_environment()

            cmd = ["meltano", "pipeline", "list", "--format", "json"]
            result = subprocess.run(
                cmd, check=False, capture_output=True, text=True, env=env, timeout=30
            )

            if result.returncode != 0:
                return FlextResult[list[str]].fail(
                    f"Failed to list pipelines: {result.stderr}"
                )

            import json

            pipelines_data = json.loads(result.stdout)
            pipeline_names = [p["name"] for p in pipelines_data.get("pipelines", [])]

            return FlextResult[list[str]].ok(pipeline_names)

        except Exception as e:
            return FlextResult[list[str]].fail(f"Failed to list pipelines: {e!s}")

    def _validate_job_name(self, job_name: str) -> str | None:
        """Validate job name format and constraints.

        Args:
            job_name: Job name to validate

        Returns:
            Validated job name or None if invalid

        """
        if not job_name or not isinstance(job_name, str):
            return None

        # Check length
        if len(job_name) > 100:  # MAX_JOB_NAME_LENGTH
            return None

        # Check for valid characters (alphanumeric, hyphens, underscores)
        import re

        if not re.match(r"^[a-zA-Z0-9_-]+$", job_name):
            return None

        return job_name

    def _execute_meltano_pipeline(
        self, job_name: str, env: dict[str, str]
    ) -> FlextResult[PipelineResult]:
        """Execute Meltano pipeline and collect results.

        Args:
            job_name: Name of the job to execute
            env: Environment variables for Meltano

        Returns:
            Pipeline execution result

        """
        try:
            # Initialize metrics collection
            metrics = PipelineMetrics()

            # Record start time
            import uuid
            from datetime import datetime

            pipeline_id = str(uuid.uuid4())
            start_time = datetime.now()
            metrics.record_extraction_start()

            # Execute Meltano job
            cmd = ["meltano", "run", job_name]
            self.logger.info(f"Executing command: {' '.join(cmd)}")

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
                cwd=Path.cwd(),
            )

            # Monitor process execution
            stdout, stderr = process.communicate(timeout=3600)  # 1 hour timeout

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            # Analyze results
            success = process.returncode == 0

            # Create pipeline result
            result = PipelineResult(
                pipeline_id=pipeline_id,
                pipeline_name=job_name,
                job_name=job_name,
                status="SUCCESS" if success else "FAILED",
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration,
                errors=[{"message": stderr.strip()}]
                if stderr.strip() and not success
                else [],
            )

            # Add stdout parsing for metrics (simplified)
            if success and stdout:
                # Parse metrics from stdout if available
                # This would be enhanced based on actual Meltano output format
                pass

            return FlextResult[PipelineResult].ok(result)

        except subprocess.TimeoutExpired:
            return FlextResult[PipelineResult].fail("Pipeline execution timed out")
        except Exception as e:
            return FlextResult[PipelineResult].fail(f"Pipeline execution error: {e!s}")

    def _build_meltano_environment(self) -> dict[str, str]:
        """Build environment variables for Meltano execution.

        Returns:
            Environment dictionary for subprocess execution

        """
        env = os.environ.copy()

        # Add Meltano-specific environment variables
        env.update({
            "MELTANO_ENVIRONMENT": getattr(self.config, "environment", "dev"),
            "MELTANO_PROJECT_ROOT": str(Path.cwd()),
            "PYTHONPATH": os.environ.get("PYTHONPATH", "")
            + ":"
            + str(Path.cwd() / "src"),
        })

        # Add database environment variables if configured
        if hasattr(self.config, "oracle") and self.config.oracle:
            oracle_config = self.config.oracle
            env.update({
                "TAP_ORACLE_WMS_BASE_URL": getattr(oracle_config, "base_url", ""),
                "TAP_ORACLE_WMS_USERNAME": getattr(oracle_config, "username", ""),
                "TAP_ORACLE_WMS_PASSWORD": getattr(oracle_config, "password", ""),
                "TAP_ORACLE_WMS_COMPANY_CODE": getattr(
                    oracle_config, "company_code", ""
                ),
                "TAP_ORACLE_WMS_FACILITY_CODE": getattr(
                    oracle_config, "facility_code", ""
                ),
            })

        return env
