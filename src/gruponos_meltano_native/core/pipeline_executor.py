"""Pipeline executor for GrupoNOS Meltano Native.

This module contains the core pipeline execution logic and Meltano integration,
separated from the main orchestrator for better modularity and maintainability.

Copyright (c) 2025 Grupo Nós. Todos os direitos reservados. Licença: Proprietária
"""

from __future__ import annotations

import json
import os
import re
import uuid
from datetime import UTC, datetime
from pathlib import Path

from flext_core import FlextLogger, FlextResult, FlextTypes as t, FlextUtilities

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

    # Maximum allowed length for job names
    MAX_JOB_NAME_LENGTH = 100

    def __init__(self, config: GruponosMeltanoNativeConfig) -> None:
        """Initialize MeltanoPipelineExecutor.

        Args:
            config: Configuration for Meltano operations

        """
        self.config = config
        self.logger = FlextLogger.get_logger(__name__)

    def execute_pipeline(
        self, job_name: str, _config: PipelineConfiguration
    ) -> FlextResult[PipelineResult]:
        """Execute a Meltano pipeline job.

        Args:
            job_name: Name of the Meltano job to execute
            _config: Pipeline configuration (currently unused)

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
                pipeline_result = result.value
                self.logger.info(f"Pipeline execution completed: {job_name}")
                return FlextResult[PipelineResult].ok(pipeline_result)
            error_msg = f"Pipeline execution failed: {result.error}"
            self.logger.error(error_msg)
            return FlextResult[PipelineResult].fail(error_msg)

        except Exception as e:
            error_msg = f"Unexpected error during pipeline execution: {e!s}"
            self.logger.exception(error_msg)
            return FlextResult[PipelineResult].fail(error_msg)

    def get_job_status(
        self, job_name: str
    ) -> FlextResult[dict[str, t.GeneralValueType]]:
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
            exec_result = FlextUtilities.run_external_command(
                cmd, env=env, timeout=30.0
            )

            if exec_result.is_failure:
                if "timed out" in exec_result.error.lower():
                    return FlextResult[dict[str, t.GeneralValueType]].fail(
                        "Job status check timed out"
                    )
                return FlextResult[dict[str, t.GeneralValueType]].fail(
                    f"Failed to get job status: {exec_result.error}"
                )

            # Parse JSON output
            wrapper = exec_result.value
            jobs_data = json.loads(wrapper.stdout)

            # Find the specific job
            for job in jobs_data.get("jobs", []):
                if job.get("name") == job_name:
                    return FlextResult[dict[str, t.GeneralValueType]].ok(job)

            return FlextResult[dict[str, t.GeneralValueType]].fail(
                f"Job not found: {job_name}"
            )

        except json.JSONDecodeError as e:
            return FlextResult[dict[str, t.GeneralValueType]].fail(
                f"Invalid JSON response: {e!s}"
            )
        except Exception as e:
            return FlextResult[dict[str, t.GeneralValueType]].fail(
                f"Unexpected error: {e!s}"
            )

    def list_jobs(self) -> FlextResult[list[str]]:
        """List all available Meltano jobs.

        Returns:
            List of job names

        """
        try:
            env = self._build_meltano_environment()

            cmd = ["meltano", "job", "list", "--format", "json"]
            exec_result = FlextUtilities.run_external_command(
                cmd, env=env, timeout=30.0
            )

            if exec_result.is_failure:
                if "timed out" in exec_result.error.lower():
                    return FlextResult[list[str]].fail("Job listing timed out")
                return FlextResult[list[str]].fail(
                    f"Failed to list jobs: {exec_result.error}"
                )

            wrapper = exec_result.value
            jobs_data = json.loads(wrapper.stdout)
            job_names = [job["name"] for job in jobs_data.get("jobs", [])]

            return FlextResult[list[str]].ok(job_names)

        except json.JSONDecodeError as e:
            return FlextResult[list[str]].fail(f"Invalid JSON response: {e!s}")
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
            exec_result = FlextUtilities.run_external_command(
                cmd, env=env, timeout=30.0
            )

            if exec_result.is_failure:
                if "timed out" in exec_result.error.lower():
                    return FlextResult[list[str]].fail("Pipeline listing timed out")
                return FlextResult[list[str]].fail(
                    f"Failed to list pipelines: {exec_result.error}"
                )

            wrapper = exec_result.value
            pipelines_data = json.loads(wrapper.stdout)
            pipeline_names = [p["name"] for p in pipelines_data.get("pipelines", [])]

            return FlextResult[list[str]].ok(pipeline_names)

        except json.JSONDecodeError as e:
            return FlextResult[list[str]].fail(f"Invalid JSON response: {e!s}")
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
        if len(job_name) > self.MAX_JOB_NAME_LENGTH:
            return None

        # Check for valid characters (alphanumeric, hyphens, underscores)
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
            pipeline_id = str(uuid.uuid4())
            start_time = datetime.now(tz=UTC)
            metrics.record_extraction_start()

            # Execute Meltano job
            cmd = ["meltano", "run", job_name]
            self.logger.info(f"Executing command: {' '.join(cmd)}")

            exec_result = FlextUtilities.run_external_command(
                cmd,
                env=env,
                timeout=3600.0,  # 1 hour timeout
            )

            end_time = datetime.now(tz=UTC)
            duration = (end_time - start_time).total_seconds()

            # Check for timeout
            if exec_result.is_failure:
                if "timed out" in exec_result.error.lower():
                    return FlextResult[PipelineResult].fail(
                        "Pipeline execution timed out"
                    )
                # Still create result object for failure case
                return FlextResult[PipelineResult].fail(
                    f"Pipeline execution error: {exec_result.error}"
                )

            # Process successful result
            wrapper = exec_result.value
            success = wrapper.returncode == 0
            stdout = wrapper.stdout
            stderr = wrapper.stderr

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

        except Exception as e:
            return FlextResult[PipelineResult].fail(f"Pipeline execution error: {e!s}")

    def _build_meltano_environment(self) -> dict[str, str]:
        """Build environment variables for Meltano execution.

        Returns:
            Environment dictionary for external command execution

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
