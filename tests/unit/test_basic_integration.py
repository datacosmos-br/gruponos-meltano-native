"""Basic integration tests for GrupoNOS Meltano Native."""

from unittest.mock import AsyncMock, patch

import pytest
from flext_core import FlextResult

from gruponos_meltano_native import (
    GruponosMeltanoOracleConnectionConfig,
    GruponosMeltanoOrchestrator,
    GruponosMeltanoPipelineResult,
    GruponosMeltanoSettings,
    GruponosMeltanoTargetOracleConfig,
    GruponosMeltanoWMSSourceConfig,
)


class TestBasicIntegration:
    """Test basic FLEXT integration."""

    def test_config_creation(self) -> None:
      """Test that configurations can be created."""
      # Create Oracle connection config
      oracle_config = GruponosMeltanoOracleConnectionConfig(
          host="localhost",
          port=1521,
          service_name="TEST",
          username="test_user",
          password="test_pass",
      )

      if oracle_config.host != "localhost":
          msg: str = f"Expected {'localhost'}, got {oracle_config.host}"
          raise AssertionError(msg)
      assert oracle_config.port == 1521
      if oracle_config.service_name != "TEST":
          msg: str = f"Expected {'TEST'}, got {oracle_config.service_name}"
          raise AssertionError(msg)

    def test_wms_source_config(self) -> None:
      """Test WMS source configuration."""
      oracle_config = GruponosMeltanoOracleConnectionConfig(
          host="wms.local",
          service_name="WMS",
          username="user",
          password="pass",
      )

      wms_config = GruponosMeltanoWMSSourceConfig(
          oracle=oracle_config,
      )

      if wms_config.oracle.host != "wms.local":
          msg: str = f"Expected {'wms.local'}, got {wms_config.oracle.host}"
          raise AssertionError(msg)
      assert wms_config.api_enabled is True  # default value

    @pytest.mark.asyncio
    async def test_orchestrator_creation(self) -> None:
      """Test orchestrator can be created and configured."""
      # Create minimal config
      oracle_source = GruponosMeltanoOracleConnectionConfig(
          host="source.local",
          service_name="SOURCE",
          username="user",
          password="pass",
      )

      oracle_target = GruponosMeltanoOracleConnectionConfig(
          host="target.local",
          service_name="TARGET",
          username="user",
          password="pass",
      )

      wms_source = GruponosMeltanoWMSSourceConfig(oracle=oracle_source)
      target_oracle = GruponosMeltanoTargetOracleConfig(
          oracle=oracle_target,
          schema_name="TEST_SCHEMA",
      )

      # Add required Meltano config
      meltano_config = GruponosMeltanoSettings(
          project_id="test-project",
          environment="dev",
      )

      config = GruponosMeltanoSettings(
          wms_source=wms_source,
          target_oracle=target_oracle,
          meltano=meltano_config,
      )

      # Create orchestrator
      orchestrator = GruponosMeltanoOrchestrator(config)

      # Test validation
      result = await orchestrator.validate_configuration()
      assert result.success
      assert result.error is None

    @pytest.mark.asyncio
    @patch.object(GruponosMeltanoOrchestrator, "run_pipeline")
    async def test_orchestrator_pipeline_run(
      self,
      mock_run_pipeline: AsyncMock,
    ) -> None:
      """Test orchestrator can run a pipeline."""
      # Mock successful pipeline result

      mock_result = GruponosMeltanoPipelineResult(
          success=True,
          job_name="test_pipeline",
          execution_time=1.5,
          output="Pipeline executed successfully",
          error="",
          metadata={"pipeline": "test_pipeline", "status": "success"},
      )
      mock_run_pipeline.return_value = mock_result

      # Create minimal config
      oracle_source = GruponosMeltanoOracleConnectionConfig(
          host="source.local",
          service_name="SOURCE",
          username="user",
          password="pass",
      )

      oracle_target = GruponosMeltanoOracleConnectionConfig(
          host="target.local",
          service_name="TARGET",
          username="user",
          password="pass",
      )

      wms_source = GruponosMeltanoWMSSourceConfig(oracle=oracle_source)
      target_oracle = GruponosMeltanoTargetOracleConfig(
          oracle=oracle_target,
          schema_name="TEST_SCHEMA",
      )

      # Add required Meltano config
      meltano_config = GruponosMeltanoSettings(
          project_id="test-project",
          environment="dev",
      )

      config = GruponosMeltanoSettings(
          wms_source=wms_source,
          target_oracle=target_oracle,
          meltano=meltano_config,
      )

      orchestrator = GruponosMeltanoOrchestrator(config)

      # Run pipeline with mocking
      result = await orchestrator.run_pipeline("test_pipeline")
      assert result.success
      assert result.metadata is not None
      if result.metadata["pipeline"] != "test_pipeline":
          msg: str = f"Expected {'test_pipeline'}, got {result.metadata['pipeline']}"
          raise AssertionError(msg)
      assert result.metadata["status"] == "success"

      # Verify the mock was called correctly
      mock_run_pipeline.assert_called_once_with("test_pipeline")

    def test_service_result_pattern(self) -> None:
      """Test that FLEXT FlextResult pattern is used."""
      # Test success
      success_result = FlextResult.ok(data="test_value")
      assert success_result.success
      if success_result.data != "test_value":
          msg: str = f"Expected {'test_value'}, got {success_result.data}"
          raise AssertionError(msg)
      assert success_result.error is None

      # Test failure
      failure_result: FlextResult[str] = FlextResult.fail("test_error")
      assert not failure_result.success
      assert failure_result.data is None
      if failure_result.error != "test_error":
          msg: str = f"Expected {'test_error'}, got {failure_result.error}"
          raise AssertionError(msg)
