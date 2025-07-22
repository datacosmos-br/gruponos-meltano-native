"""Unit tests for orchestrator functionality."""

import pytest

from gruponos_meltano_native.config import (
    GrupoNOSConfig,
    MeltanoConfig,
    OracleConnectionConfig,
    TargetOracleConfig,
    WMSSourceConfig,
)
from gruponos_meltano_native.orchestrator import GrupoNOSMeltanoOrchestrator


class TestOrchestrator:
    """Test orchestrator functionality."""

    @pytest.fixture
    def valid_config(self) -> GrupoNOSConfig:
        """Create valid test configuration."""
        oracle_wms = OracleConnectionConfig(
            host="wms.local",
            service_name="WMS",
            username="wms_user",
            password="wms_pass",
        )

        oracle_target = OracleConnectionConfig(
            host="target.local",
            service_name="TARGET",
            username="target_user",
            password="target_pass",
        )

        return GrupoNOSConfig(
            wms_source=WMSSourceConfig(oracle=oracle_wms),
            target_oracle=TargetOracleConfig(oracle=oracle_target, schema_name="SYNC"),
            meltano=MeltanoConfig(project_id="test", environment="dev"),
        )

    def test_orchestrator_initialization(self, valid_config: GrupoNOSConfig) -> None:
        """Test orchestrator initialization."""
        orchestrator = GrupoNOSMeltanoOrchestrator(valid_config)

        assert orchestrator.config == valid_config
        assert not orchestrator._running
        assert hasattr(orchestrator, "run_pipeline")
        assert hasattr(orchestrator, "validate_configuration")
        assert hasattr(orchestrator, "stop")

    @pytest.mark.asyncio
    async def test_orchestrator_validation_success(
        self,
        valid_config: GrupoNOSConfig,
    ) -> None:
        """Test successful configuration validation."""
        orchestrator = GrupoNOSMeltanoOrchestrator(valid_config)

        result = await orchestrator.validate_configuration()

        assert result.success
        assert result.value is True

    @pytest.mark.asyncio
    async def test_orchestrator_validation_missing_wms(self) -> None:
        """Test validation failure with missing WMS source."""
        config = GrupoNOSConfig(
            wms_source=None,
            target_oracle=None,
            meltano=MeltanoConfig(project_id="test", environment="dev"),
        )

        orchestrator = GrupoNOSMeltanoOrchestrator(config)

        result = await orchestrator.validate_configuration()

        assert not result.success
        assert result.error is not None
        assert "WMS source not configured" in result.error

    @pytest.mark.asyncio
    async def test_orchestrator_validation_missing_target(self) -> None:
        """Test validation failure with missing target."""
        oracle_wms = OracleConnectionConfig(
            host="wms.local",
            service_name="WMS",
            username="wms_user",
            password="wms_pass",
        )

        config = GrupoNOSConfig(
            wms_source=WMSSourceConfig(oracle=oracle_wms),
            target_oracle=None,
            meltano=MeltanoConfig(project_id="test", environment="dev"),
        )

        orchestrator = GrupoNOSMeltanoOrchestrator(config)

        result = await orchestrator.validate_configuration()

        assert not result.success
        assert result.error is not None
        assert "Target Oracle not configured" in result.error

    @pytest.mark.asyncio
    async def test_orchestrator_run_pipeline(
        self,
        valid_config: GrupoNOSConfig,
    ) -> None:
        """Test pipeline execution."""
        orchestrator = GrupoNOSMeltanoOrchestrator(valid_config)

        result = await orchestrator.run_pipeline("test_pipeline")

        assert result.success
        assert result.value is not None
        assert result.value["pipeline"] == "test_pipeline"
        assert result.value["status"] == "success"
        assert "records_processed" in result.value
        assert "errors" in result.value

    def test_orchestrator_stop(self, valid_config: GrupoNOSConfig) -> None:
        """Test orchestrator stop functionality."""
        orchestrator = GrupoNOSMeltanoOrchestrator(valid_config)
        orchestrator._running = True

        orchestrator.stop()

        assert not orchestrator._running

    @pytest.mark.asyncio
    async def test_orchestrator_running_state(
        self,
        valid_config: GrupoNOSConfig,
    ) -> None:
        """Test orchestrator running state management."""
        orchestrator = GrupoNOSMeltanoOrchestrator(valid_config)

        # Initially not running
        assert not orchestrator._running

        # Should be running during pipeline execution
        result = await orchestrator.run_pipeline("test_pipeline")

        # Should not be running after completion
        assert not orchestrator._running
        assert result.success
