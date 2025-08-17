"""Unit tests for orchestrator functionality."""

import unittest.mock

import pytest

from gruponos_meltano_native import (
    GruponosMeltanoOracleConnectionConfig,
    GruponosMeltanoOrchestrator,
    GruponosMeltanoPipelineResult,
    GruponosMeltanoSettings,
    GruponosMeltanoTargetOracleConfig,
    GruponosMeltanoWMSSourceConfig,
)


class TestOrchestrator:
    """Test orchestrator functionality."""

    @pytest.fixture
    def valid_config(self) -> GruponosMeltanoSettings:
      """Create valid test configuration."""
      oracle_wms = GruponosMeltanoOracleConnectionConfig(
          host="wms.local",
          service_name="WMS",
          username="wms_user",
          password="wms_pass",
      )

      oracle_target = GruponosMeltanoOracleConnectionConfig(
          host="target.local",
          service_name="TARGET",
          username="target_user",
          password="target_pass",
      )

      return GruponosMeltanoSettings(
          wms_source=GruponosMeltanoWMSSourceConfig(oracle=oracle_wms),
          target_oracle=GruponosMeltanoTargetOracleConfig(
              oracle=oracle_target,
              schema_name="SYNC",
          ),
          meltano=GruponosMeltanoSettings(project_id="test", environment="dev"),
      )

    def test_orchestrator_initialization(
      self,
      valid_config: GruponosMeltanoSettings,
    ) -> None:
      """Test orchestrator initialization."""
      orchestrator = GruponosMeltanoOrchestrator(valid_config)

      if orchestrator.settings != valid_config:
          msg: str = f"Expected {valid_config}, got {orchestrator.settings}"
          raise AssertionError(msg)
      # Basic orchestrator should have basic methods
      assert hasattr(orchestrator, "run_pipeline")
      assert hasattr(orchestrator, "list_jobs")
      assert hasattr(orchestrator, "get_job_status")

    @pytest.mark.asyncio
    async def test_orchestrator_validation_success(
      self,
      valid_config: GruponosMeltanoSettings,
    ) -> None:
      """Test successful configuration validation."""
      orchestrator = GruponosMeltanoOrchestrator(valid_config)

      result = await orchestrator.validate_configuration()

      assert result.success
      assert result.error is None

    @pytest.mark.asyncio
    async def test_orchestrator_run_pipeline(
      self,
      valid_config: GruponosMeltanoSettings,
    ) -> None:
      """Test pipeline execution."""
      orchestrator = GruponosMeltanoOrchestrator(valid_config)

      # Mock the pipeline execution since it requires real Meltano setup

      with unittest.mock.patch.object(
          orchestrator.pipeline_runner,
          "run_pipeline",
      ) as mock_run:
          mock_result = GruponosMeltanoPipelineResult(
              success=True,
              job_name="test_pipeline",
              execution_time=1.0,
              output="Pipeline executed successfully",
              error=None,
              metadata={"records_processed": 100, "tables_updated": 3},
          )
          mock_run.return_value = mock_result

          result = await orchestrator.run_pipeline("test_pipeline")

          assert result.success
          assert result.job_name == "test_pipeline"
          assert result.error is None
          assert result.metadata is not None
          if "records_processed" not in result.metadata:
              msg: str = f"Expected 'records_processed' in {result.metadata}"
              raise AssertionError(msg)

    def test_orchestrator_job_status(
      self,
      valid_config: GruponosMeltanoSettings,
    ) -> None:
      """Test orchestrator job status functionality."""
      orchestrator = GruponosMeltanoOrchestrator(valid_config)

      status = orchestrator.get_job_status("test_job")

      assert "job_name" in status
      assert "available" in status
      assert "settings" in status
      assert status["job_name"] == "test_job"

    @pytest.mark.asyncio
    async def test_orchestrator_pipeline_execution(
      self,
      valid_config: GruponosMeltanoSettings,
    ) -> None:
      """Test orchestrator pipeline execution."""
      orchestrator = GruponosMeltanoOrchestrator(valid_config)

      # Test async pipeline execution
      result = await orchestrator.run_pipeline("test_pipeline")

      # Check result structure (even if it fails without actual meltano setup)
      assert hasattr(result, "success")
      assert hasattr(result, "job_name")
      assert hasattr(result, "execution_time")
      assert result.job_name == "test_pipeline"
