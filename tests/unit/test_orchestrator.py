"""Unit tests for orchestrator functionality."""

import pytest

from gruponos_meltano_native.config import (
    GruponosMeltanoOracleConnectionConfig,
    GruponosMeltanoSettings,
    GruponosMeltanoTargetOracleConfig,
    GruponosMeltanoWMSSourceConfig,
)
from gruponos_meltano_native.orchestrator import GruponosMeltanoOrchestrator


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

        if orchestrator.config != valid_config:
            msg = f"Expected {valid_config}, got {orchestrator.config}"
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
        if not (result.value):
            msg = f"Expected True, got {result.value}"
            raise AssertionError(msg)

    @pytest.mark.asyncio
    async def test_orchestrator_validation_missing_wms(self) -> None:
        """Test validation failure with missing WMS source."""
        config = GruponosMeltanoSettings(
            wms_source=None,
            target_oracle=None,
            meltano=GruponosMeltanoSettings(project_id="test", environment="dev"),
        )

        orchestrator = GruponosMeltanoOrchestrator(config)

        result = await orchestrator.validate_configuration()

        assert not result.success
        assert result.error is not None
        if "WMS source not configured" not in result.error:
            msg = f"Expected {'WMS source not configured'} in {result.error}"
            raise AssertionError(msg)

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

        orchestrator = GruponosMeltanoOrchestrator(config)

        result = await orchestrator.validate_configuration()

        assert not result.success
        assert result.error is not None
        if "Target Oracle not configured" not in result.error:
            msg = f"Expected {'Target Oracle not configured'} in {result.error}"
            raise AssertionError(msg)

    @pytest.mark.asyncio
    async def test_orchestrator_run_pipeline(
        self,
        valid_config: GruponosMeltanoSettings,
    ) -> None:
        """Test pipeline execution."""
        orchestrator = GruponosMeltanoOrchestrator(valid_config)

        result = await orchestrator.run_pipeline("test_pipeline")

        assert result.success
        assert result.value is not None
        if result.value["pipeline"] != "test_pipeline":
            msg = f"Expected {'test_pipeline'}, got {result.value['pipeline']}"
            raise AssertionError(msg)
        assert result.value["status"] == "success"
        if "records_processed" not in result.value:
            msg = f"Expected {'records_processed'} in {result.value}"
            raise AssertionError(msg)
        assert "errors" in result.value

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
