"""Basic integration tests for GrupoNOS Meltano Native."""

import pytest

from gruponos_meltano_native.config import (
    GrupoNOSConfig,
    MeltanoConfig,
    OracleConnectionConfig,
    TargetOracleConfig,
    WMSSourceConfig,
)

# 🚨 ARCHITECTURAL VIOLATION FIXED: Level 6 projects cannot import from flext-core
# ✅ SOLUTION: Use Dependency Injection - ServiceResult provided via DI container
from gruponos_meltano_native.infrastructure.di_container import get_service_result
from gruponos_meltano_native.orchestrator import GrupoNOSMeltanoOrchestrator

# Get ServiceResult via dependency injection
ServiceResult = get_service_result()


class TestBasicIntegration:
    """Test basic FLEXT integration."""

    def test_config_creation(self) -> None:
        """Test that configurations can be created."""
        # Create Oracle connection config
        oracle_config = OracleConnectionConfig(
            host="localhost",
            port=1521,
            service_name="TEST",
            username="test_user",
            password="test_pass",
        )

        assert oracle_config.host == "localhost"
        assert oracle_config.port == 1521
        assert oracle_config.service_name == "TEST"

    def test_wms_source_config(self) -> None:
        """Test WMS source configuration."""
        oracle_config = OracleConnectionConfig(
            host="wms.local",
            service_name="WMS",
            username="user",
            password="pass",
        )

        wms_config = WMSSourceConfig(
            oracle=oracle_config,
        )

        assert wms_config.oracle.host == "wms.local"
        assert wms_config.api_enabled is False  # default value

    @pytest.mark.asyncio
    async def test_orchestrator_creation(self) -> None:
        """Test orchestrator can be created and configured."""
        # Create minimal config
        oracle_source = OracleConnectionConfig(
            host="source.local",
            service_name="SOURCE",
            username="user",
            password="pass",
        )

        oracle_target = OracleConnectionConfig(
            host="target.local",
            service_name="TARGET",
            username="user",
            password="pass",
        )

        wms_source = WMSSourceConfig(oracle=oracle_source)
        target_oracle = TargetOracleConfig(
            oracle=oracle_target,
            schema_name="TEST_SCHEMA",
        )

        # Add required Meltano config
        meltano_config = MeltanoConfig(
            project_id="test-project",
            environment="dev",
        )

        config = GrupoNOSConfig(
            wms_source=wms_source,
            target_oracle=target_oracle,
            meltano=meltano_config,
        )

        # Create orchestrator
        orchestrator = GrupoNOSMeltanoOrchestrator(config)

        # Test validation
        result = await orchestrator.validate_configuration()
        assert result.success
        assert result.data is True

    @pytest.mark.asyncio
    async def test_orchestrator_pipeline_run(self) -> None:
        """Test orchestrator can run a pipeline."""
        # Create minimal config
        oracle_source = OracleConnectionConfig(
            host="source.local",
            service_name="SOURCE",
            username="user",
            password="pass",
        )

        oracle_target = OracleConnectionConfig(
            host="target.local",
            service_name="TARGET",
            username="user",
            password="pass",
        )

        wms_source = WMSSourceConfig(oracle=oracle_source)
        target_oracle = TargetOracleConfig(
            oracle=oracle_target,
            schema_name="TEST_SCHEMA",
        )

        # Add required Meltano config
        meltano_config = MeltanoConfig(
            project_id="test-project",
            environment="dev",
        )

        config = GrupoNOSConfig(
            wms_source=wms_source,
            target_oracle=target_oracle,
            meltano=meltano_config,
        )

        orchestrator = GrupoNOSMeltanoOrchestrator(config)

        # Run pipeline
        result = await orchestrator.run_pipeline("test_pipeline")
        assert result.success
        assert result.data is not None
        assert result.data["pipeline"] == "test_pipeline"
        assert result.data["status"] == "success"

    def test_service_result_pattern(self) -> None:
        """Test that FLEXT ServiceResult pattern is used."""
        # Test success
        success_result = ServiceResult.ok(data="test_value")
        assert success_result.success
        assert success_result.data == "test_value"
        assert success_result.error is None

        # Test failure
        failure_result: ServiceResult[str] = ServiceResult.fail("test_error")
        assert not failure_result.success
        assert failure_result.data is None
        assert failure_result.error == "test_error"
