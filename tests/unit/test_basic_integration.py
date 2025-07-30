"""Basic integration tests for GrupoNOS Meltano Native."""

import pytest

# FLEXT Core Standards - Direct imports allowed from Level 6 projects
from flext_core import FlextResult

from gruponos_meltano_native.config import (
    GruponosMeltanoOracleConnectionConfig,
    GruponosMeltanoSettings,
    GruponosMeltanoTargetOracleConfig,
    GruponosMeltanoWMSSourceConfig,
)
from gruponos_meltano_native.orchestrator import GruponosMeltanoOrchestrator


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
            msg = f"Expected {'localhost'}, got {oracle_config.host}"
            raise AssertionError(msg)
        assert oracle_config.port == 1521
        if oracle_config.service_name != "TEST":
            msg = f"Expected {'TEST'}, got {oracle_config.service_name}"
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
            msg = f"Expected {'wms.local'}, got {wms_config.oracle.host}"
            raise AssertionError(msg)
        assert wms_config.api_enabled is False  # default value

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
        if not (result.data):
            msg = f"Expected True, got {result.data}"
            raise AssertionError(msg)

    @pytest.mark.asyncio
    async def test_orchestrator_pipeline_run(self) -> None:
        """Test orchestrator can run a pipeline."""
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

        # Run pipeline
        result = await orchestrator.run_pipeline("test_pipeline")
        assert result.success
        assert result.data is not None
        if result.data["pipeline"] != "test_pipeline":
            msg = f"Expected {'test_pipeline'}, got {result.data['pipeline']}"
            raise AssertionError(msg)
        assert result.data["status"] == "success"

    def test_service_result_pattern(self) -> None:
        """Test that FLEXT FlextResult pattern is used."""
        # Test success
        success_result = FlextResult.ok(data="test_value")
        assert success_result.success
        if success_result.data != "test_value":
            msg = f"Expected {'test_value'}, got {success_result.data}"
            raise AssertionError(msg)
        assert success_result.error is None

        # Test failure
        failure_result: FlextResult[str] = FlextResult.fail("test_error")
        assert not failure_result.success
        assert failure_result.data is None
        if failure_result.error != "test_error":
            msg = f"Expected {'test_error'}, got {failure_result.error}"
            raise AssertionError(msg)
