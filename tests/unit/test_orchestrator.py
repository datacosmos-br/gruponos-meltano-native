"""Unit tests for orchestrator functionality."""

import pytest

from gruponos_meltano_native.config import (
    GruponosMeltanoOracleConnectionConfig,
    GruponosMeltanoSettings,
    GruponosMeltanoTargetOracleConfig,
    GruponosMeltanoWMSSourceConfig,
)
from gruponos_meltano_native.orchestrator import GrupoNOSMeltanoOrchestrator


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
            target_oracle=GruponosMeltanoTargetOracleConfig(oracle=oracle_target, schema_name="SYNC"),
            meltano=GruponosMeltanoSettings(project_id="test", environment="dev"),
        )

    def test_orchestrator_initialization(self, valid_config: GruponosMeltanoSettings) -> None:
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
        valid_config: GruponosMeltanoSettings,
    ) -> None:
        """Test successful configuration validation."""
        orchestrator = GrupoNOSMeltanoOrchestrator(valid_config)

        result = await orchestrator.validate_configuration()

        assert result.success
        assert result.value is True

    @pytest.mark.asyncio
    async def test_orchestrator_validation_missing_wms(self) -> None:
        """Test validation failure with missing WMS source."""
        config = GruponosMeltanoSettings(
            wms_source=None,
            target_oracle=None,
            meltano=GruponosMeltanoSettings(project_id="test", environment="dev"),
        )

        orchestrator = GrupoNOSMeltanoOrchestrator(config)

        result = await orchestrator.validate_configuration()

        assert not result.success
        assert result.error is not None
        assert "WMS source not configured" in result.error

    @pytest.mark.asyncio
    async def test_orchestrator_validation_missing_target(self) -> None:
        """Test validation failure with missing target."""
        oracle_wms = GruponosMeltanoOracleConnectionConfig(
            host="wms.local",
            service_name="WMS",
            username="wms_user",
            password="wms_pass",
        )

        config = GruponosMeltanoSettings(
            wms_source=GruponosMeltanoWMSSourceConfig(oracle=oracle_wms),
            target_oracle=None,
            meltano=GruponosMeltanoSettings(project_id="test", environment="dev"),
        )

        orchestrator = GrupoNOSMeltanoOrchestrator(config)

        result = await orchestrator.validate_configuration()

        assert not result.success
        assert result.error is not None
        assert "Target Oracle not configured" in result.error

    @pytest.mark.asyncio
    async def test_orchestrator_run_pipeline(
        self,
        valid_config: GruponosMeltanoSettings,
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

    def test_orchestrator_stop(self, valid_config: GruponosMeltanoSettings) -> None:
        """Test orchestrator stop functionality."""
        orchestrator = GrupoNOSMeltanoOrchestrator(valid_config)
        orchestrator._running = True

        orchestrator.stop()

        assert not orchestrator._running

    @pytest.mark.asyncio
    async def test_orchestrator_running_state(
        self,
        valid_config: GruponosMeltanoSettings,
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
