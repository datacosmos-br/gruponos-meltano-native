"""Pipeline executor for GrupoNOS Meltano Native.

This module contains the core pipeline execution logic and Meltano integration,
separated from the main orchestrator for better modularity and maintainability.

Copyright (c) 2025 Grupo Nós. Todos os direitos reservados. Licença: Proprietária
"""

from __future__ import annotations

import os
import re
import uuid
from datetime import UTC, datetime
from pathlib import Path

from flext_core import FlextLogger, FlextProtocols as p, FlextResult, FlextTypes as t
from pydantic import TypeAdapter, ValidationError

from gruponos_meltano_native.config import GruponosMeltanoNativeConfig
from gruponos_meltano_native.core.external_command import run_external_command
from gruponos_meltano_native.models import GruponosMeltanoNativeModels as m

# Typed JSON adapter for parsing JSON responses as dicts
_JsonDictAdapter: TypeAdapter[dict[str, object]] = TypeAdapter(dict[str, object])


class MeltanoPipelineExecutor:
    """Executor for Meltano pipeline operations.

    Handles the low-level interaction with Meltano CLI and process management.
    Separated from orchestrator for better testability and maintainability.
    """

    MAX_JOB_NAME_LENGTH: int = 100
    config: GruponosMeltanoNativeConfig
    logger: p.Log.StructlogLogger

    def __init__(self, config: GruponosMeltanoNativeConfig) -> None:
        """Initialize MeltanoPipelineExecutor."""
        self.config = config
        self.logger = FlextLogger.get_logger(__name__)

    def execute_pipeline(
        self, job_name: str, _config: m.PipelineConfiguration
    ) -> FlextResult[m.PipelineResult]:
        """Execute a Meltano pipeline job."""
        try:
            self.logger.info(f"Starting pipeline execution: {job_name}")

            validated_job_name = self._validate_job_name(job_name)
            if not validated_job_name:
                return FlextResult[m.PipelineResult].fail(
                    f"Invalid job name: {job_name}"
                )

            env = self._build_meltano_environment()
            result = self._execute_meltano_pipeline(validated_job_name, env)

            if result.is_success:
                pipeline_result = result.value
                self.logger.info(f"Pipeline execution completed: {job_name}")
                return FlextResult[m.PipelineResult].ok(pipeline_result)
            error_msg = f"Pipeline execution failed: {result.error}"
            self.logger.error(error_msg)
            return FlextResult[m.PipelineResult].fail(error_msg)

        except Exception as e:
            error_msg = f"Unexpected error during pipeline execution: {e!s}"
            self.logger.exception(error_msg)
            return FlextResult[m.PipelineResult].fail(error_msg)

    def get_job_status(
        self, job_name: str
    ) -> FlextResult[dict[str, t.GeneralValueType]]:
        """Get status of a Meltano job."""
        try:
            env = self._build_meltano_environment()

            cmd = ["meltano", "job", "list", "--format", "json"]
            exec_result = run_external_command(cmd, env=env, timeout=30.0)

            if exec_result.is_failure:
                error_msg = exec_result.error or ""
                if "timed out" in error_msg.lower():
                    return FlextResult[dict[str, t.GeneralValueType]].fail(
                        "Job status check timed out"
                    )
                return FlextResult[dict[str, t.GeneralValueType]].fail(
                    f"Failed to get job status: {error_msg}"
                )

            wrapper = exec_result.value
            try:
                raw_data = _JsonDictAdapter.validate_json(wrapper.stdout)
            except ValidationError:
                return FlextResult[dict[str, t.GeneralValueType]].fail(
                    "Invalid response format"
                )

            jobs_list = raw_data.get("jobs", [])
            if not isinstance(jobs_list, list):
                jobs_list = []

            for job in jobs_list:
                if isinstance(job, dict) and job.get("name") == job_name:
                    job_result: dict[str, t.GeneralValueType] = {
                        key: value for key, value in job.items() if isinstance(key, str)
                    }
                    return FlextResult[dict[str, t.GeneralValueType]].ok(job_result)

            return FlextResult[dict[str, t.GeneralValueType]].fail(
                f"Job not found: {job_name}"
            )

        except Exception as e:
            return FlextResult[dict[str, t.GeneralValueType]].fail(
                f"Unexpected error: {e!s}"
            )

    def list_jobs(self) -> FlextResult[list[str]]:
        """List all available Meltano jobs."""
        try:
            env = self._build_meltano_environment()

            cmd = ["meltano", "job", "list", "--format", "json"]
            exec_result = run_external_command(cmd, env=env, timeout=30.0)

            if exec_result.is_failure:
                error_msg = exec_result.error or ""
                if "timed out" in error_msg.lower():
                    return FlextResult[list[str]].fail("Job listing timed out")
                return FlextResult[list[str]].fail(f"Failed to list jobs: {error_msg}")

            wrapper = exec_result.value
            try:
                raw_data = _JsonDictAdapter.validate_json(wrapper.stdout)
            except ValidationError:
                return FlextResult[list[str]].fail("Invalid JSON response format")

            jobs_list = raw_data.get("jobs", [])
            if not isinstance(jobs_list, list):
                return FlextResult[list[str]].fail("Invalid jobs data format")
            job_names: list[str] = []
            for job in jobs_list:
                if isinstance(job, dict):
                    name = job.get("name")
                    if isinstance(name, str):
                        job_names.append(name)

            return FlextResult[list[str]].ok(job_names)

        except Exception as e:
            return FlextResult[list[str]].fail(f"Failed to list jobs: {e!s}")

    def list_pipelines(self) -> FlextResult[list[str]]:
        """List all available Meltano pipelines."""
        try:
            env = self._build_meltano_environment()

            cmd = ["meltano", "pipeline", "list", "--format", "json"]
            exec_result = run_external_command(cmd, env=env, timeout=30.0)

            if exec_result.is_failure:
                error_msg = exec_result.error or ""
                if "timed out" in error_msg.lower():
                    return FlextResult[list[str]].fail("Pipeline listing timed out")
                return FlextResult[list[str]].fail(
                    f"Failed to list pipelines: {error_msg}"
                )

            wrapper = exec_result.value
            try:
                raw_pipelines = _JsonDictAdapter.validate_json(wrapper.stdout)
            except ValidationError:
                return FlextResult[list[str]].fail("Invalid JSON response format")

            pipelines_list = raw_pipelines.get("pipelines", [])
            if not isinstance(pipelines_list, list):
                return FlextResult[list[str]].fail("Invalid pipelines data format")
            pipeline_names: list[str] = []
            for pipeline in pipelines_list:
                if isinstance(pipeline, dict):
                    name = pipeline.get("name")
                    if isinstance(name, str):
                        pipeline_names.append(name)

            return FlextResult[list[str]].ok(pipeline_names)

        except Exception as e:
            return FlextResult[list[str]].fail(f"Failed to list pipelines: {e!s}")

    def _validate_job_name(self, job_name: str) -> str | None:
        """Validate job name format and constraints."""
        if not job_name:
            return None

        if len(job_name) > self.MAX_JOB_NAME_LENGTH:
            return None

        if not re.match(r"^[a-zA-Z0-9_-]+$", job_name):
            return None

        return job_name

    def _execute_meltano_pipeline(
        self, job_name: str, env: dict[str, str]
    ) -> FlextResult[m.PipelineResult]:
        """Execute Meltano pipeline and collect results."""
        try:
            metrics = m.PipelineMetrics(
                extraction_start_time=None,
                extraction_end_time=None,
                transformation_start_time=None,
                transformation_end_time=None,
                loading_start_time=None,
                loading_end_time=None,
            )

            pipeline_id = str(uuid.uuid4())
            start_time = datetime.now(tz=UTC)
            metrics.record_extraction_start()

            cmd = ["meltano", "run", job_name]
            self.logger.info(f"Executing command: {' '.join(cmd)}")

            exec_result = run_external_command(
                cmd,
                env=env,
                timeout=3600.0,
            )

            end_time = datetime.now(tz=UTC)
            duration = (end_time - start_time).total_seconds()

            if exec_result.is_failure:
                error_msg = exec_result.error or ""
                if "timed out" in error_msg.lower():
                    return FlextResult[m.PipelineResult].fail(
                        "Pipeline execution timed out"
                    )
                return FlextResult[m.PipelineResult].fail(
                    f"Pipeline execution error: {error_msg}"
                )

            wrapper = exec_result.value
            success = wrapper.returncode == 0
            stdout = wrapper.stdout
            stderr = wrapper.stderr

            error_list: list[t.GeneralValueType] = []
            if stderr.strip() and not success:
                error_list = [{"message": stderr.strip()}]

            result = m.PipelineResult(
                pipeline_id=pipeline_id,
                pipeline_name=job_name,
                job_name=job_name,
                status="SUCCESS" if success else "FAILED",
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration,
                errors=error_list,
            )

            if success and stdout:
                pass

            return FlextResult[m.PipelineResult].ok(result)

        except Exception as e:
            return FlextResult[m.PipelineResult].fail(
                f"Pipeline execution error: {e!s}"
            )

    def _build_meltano_environment(self) -> dict[str, str]:
        """Build environment variables for Meltano execution."""
        env = os.environ.copy()

        env.update({
            "MELTANO_ENVIRONMENT": getattr(self.config, "environment", "dev"),
            "MELTANO_PROJECT_ROOT": str(Path.cwd()),
            "PYTHONPATH": os.environ.get("PYTHONPATH", "")
            + ":"
            + str(Path.cwd() / "src"),
        })

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
