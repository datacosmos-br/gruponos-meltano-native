"""Unit tests for FLEXT integration in GrupoNOS Meltano Native."""

import os
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

import pytest
from flext_core.domain.types import ServiceResult

from gruponos_meltano_native.config import (
    GrupoNOSConfig,
    OracleConnectionConfig,
    WMSSourceConfig,
    TargetOracleConfig,
    AlertConfig,
    MeltanoConfig,
)
from gruponos_meltano_native.orchestrator import GrupoNOSMeltanoOrchestrator


class TestFlextConfig:
    """Test FLEXT configuration integration."""
    
    def test_oracle_connection_config(self):
        """Test Oracle connection configuration."""
        config = OracleConnectionConfig(
            host="localhost",
            port=1522,
            service_name="TESTDB",
            username="test_user",
            password="test_pass",
            protocol="tcps",
            batch_size=1000,
        )
        
        assert config.host == "localhost"
        assert config.port == 1522
        assert config.protocol == "tcps"
        assert config.batch_size == 1000
        assert config.retry_attempts == 3  # default
    
    def test_wms_source_config_validation(self):
        """Test WMS source configuration validation."""
        # Valid config without API
        oracle_config = OracleConnectionConfig(
            host="wms.local",
            service_name="WMS",
            username="user",
            password="pass",
        )
        
        config = WMSSourceConfig(
            oracle=oracle_config,
            api_enabled=False,
        )
        assert config.api_enabled is False
        assert config.api_base_url is None
        
        # Invalid config - API enabled but no URL
        with pytest.raises(ValueError):
            WMSSourceConfig(
                oracle=oracle_config,
                api_enabled=True,
                api_base_url=None,
            )
    
    def test_config_from_env(self, monkeypatch):
        """Test configuration loading from environment variables."""
        # Set required environment variables
        env_vars = {
            "TAP_ORACLE_WMS_HOST": "wms.test.local",
            "TAP_ORACLE_WMS_SERVICE_NAME": "WMSTEST",
            "TAP_ORACLE_WMS_USERNAME": "wms_user",
            "TAP_ORACLE_WMS_PASSWORD": "wms_pass",
            "FLEXT_TARGET_ORACLE_HOST": "target.test.local",
            "FLEXT_TARGET_ORACLE_SERVICE_NAME": "TARGETTEST",
            "FLEXT_TARGET_ORACLE_USERNAME": "target_user",
            "FLEXT_TARGET_ORACLE_PASSWORD": "target_pass",
            "FLEXT_TARGET_ORACLE_SCHEMA": "WMS_SYNC",
            "MELTANO_PROJECT_ID": "test-project",
            "MELTANO_ENVIRONMENT": "test",
        }
        
        for key, value in env_vars.items():
            monkeypatch.setenv(key, value)
        
        # Load config
        config = GrupoNOSConfig.from_env()
        
        # Verify WMS source
        assert config.wms_source.oracle.host == "wms.test.local"
        assert config.wms_source.oracle.service_name == "WMSTEST"
        assert config.wms_source.oracle.username == "wms_user"
        
        # Verify target Oracle
        assert config.target_oracle.oracle.host == "target.test.local"
        assert config.target_oracle.schema == "WMS_SYNC"
        
        # Verify Meltano config
        assert config.meltano.project_id == "test-project"
        assert config.meltano.environment == "test"
    
    def test_config_to_legacy_env(self):
        """Test converting config back to legacy environment variables."""
        # Create minimal config
        wms_oracle = OracleConnectionConfig(
            host="wms.local",
            service_name="WMS",
            username="user",
            password="pass",
        )
        target_oracle = OracleConnectionConfig(
            host="target.local",
            service_name="TARGET",
            username="target_user",
            password="target_pass",
        )
        
        config = GrupoNOSConfig(
            wms_source=WMSSourceConfig(oracle=wms_oracle),
            target_oracle=TargetOracleConfig(
                oracle=target_oracle,
                schema="WMS_SYNC",
            ),
            meltano=MeltanoConfig(
                project_id="test-project",
                environment="dev",
            ),
        )
        
        # Convert to legacy
        legacy_env = config.to_legacy_env()
        
        # Verify mappings
        assert legacy_env["TAP_ORACLE_WMS_HOST"] == "wms.local"
        assert legacy_env["FLEXT_TARGET_ORACLE_HOST"] == "target.local"
        assert legacy_env["FLEXT_TARGET_ORACLE_SCHEMA"] == "WMS_SYNC"
        assert legacy_env["MELTANO_PROJECT_ID"] == "test-project"


class TestGrupoNOSOrchestrator:
    """Test GrupoNOS Meltano orchestrator."""
    
    @pytest.fixture
    def mock_config(self):
        """Create mock configuration."""
        wms_oracle = OracleConnectionConfig(
            host="wms.local",
            service_name="WMS",
            username="user",
            password="pass",
        )
        target_oracle = OracleConnectionConfig(
            host="target.local",
            service_name="TARGET",
            username="target_user",
            password="target_pass",
        )
        
        return GrupoNOSConfig(
            wms_source=WMSSourceConfig(oracle=wms_oracle),
            target_oracle=TargetOracleConfig(
                oracle=target_oracle,
                schema="WMS_SYNC",
            ),
            meltano=MeltanoConfig(
                project_id="test-project",
                environment="test",
            ),
        )
    
    @pytest.fixture
    def orchestrator(self, mock_config):
        """Create orchestrator with mocked dependencies."""
        with patch("gruponos_meltano_native.orchestrator.get_config", return_value=mock_config):
            with patch("gruponos_meltano_native.orchestrator.MeltanoProjectManager"):
                with patch("gruponos_meltano_native.orchestrator.UnifiedMeltanoAntiCorruptionLayer"):
                    return GrupoNOSMeltanoOrchestrator()
    
    @pytest.mark.asyncio
    async def test_run_full_sync(self, orchestrator):
        """Test running full sync."""
        # Mock ACL response
        mock_result = ServiceResult.success({
            "records_processed": 1000,
            "duration_seconds": 45.5,
        })
        orchestrator.acl.run_pipeline = AsyncMock(return_value=mock_result)
        
        # Run full sync
        result = await orchestrator.run_full_sync("allocation")
        
        # Verify
        assert result.is_success
        assert result.value["records_processed"] == 1000
        orchestrator.acl.run_pipeline.assert_called_once()
        
        # Check correct tap name was used
        call_args = orchestrator.acl.run_pipeline.call_args
        assert call_args.kwargs["extractor"] == "tap-oracle-wms-allocation-full"
        assert call_args.kwargs["loader"] == "target-oracle-full"
    
    @pytest.mark.asyncio
    async def test_run_incremental_sync(self, orchestrator):
        """Test running incremental sync."""
        # Mock ACL response
        mock_result = ServiceResult.success({
            "records_processed": 250,
            "duration_seconds": 12.3,
        })
        orchestrator.acl.run_pipeline = AsyncMock(return_value=mock_result)
        
        # Run incremental sync
        result = await orchestrator.run_incremental_sync("order_hdr")
        
        # Verify
        assert result.is_success
        assert result.value["records_processed"] == 250
        
        # Check correct tap name
        call_args = orchestrator.acl.run_pipeline.call_args
        assert call_args.kwargs["extractor"] == "tap-oracle-wms-order_hdr-incremental"
    
    @pytest.mark.asyncio
    async def test_run_dbt_transform(self, orchestrator):
        """Test running dbt transformations."""
        # Mock project manager response
        mock_result = ServiceResult.success({
            "stdout": "dbt run completed",
            "return_code": 0,
        })
        orchestrator.project_manager.run_command = AsyncMock(return_value=mock_result)
        
        # Run transform
        result = await orchestrator.run_dbt_transform()
        
        # Verify
        assert result.is_success
        orchestrator.project_manager.run_command.assert_called_once()
        
        # Check command
        call_args = orchestrator.project_manager.run_command.call_args
        assert call_args.kwargs["command"] == ["run", "dbt:run"]
        assert call_args.kwargs["environment"] == "test"
    
    @pytest.mark.asyncio
    async def test_validate_project(self, orchestrator):
        """Test project validation."""
        # Mock validation response
        mock_result = ServiceResult.success({
            "valid": True,
            "issues": [],
        })
        orchestrator.project_manager.validate_project = AsyncMock(return_value=mock_result)
        
        # Run validation
        result = await orchestrator.validate_project()
        
        # Verify
        assert result.is_success
        orchestrator.project_manager.validate_project.assert_called_once()
    
    def test_prepare_environment(self, orchestrator, monkeypatch):
        """Test environment variable preparation."""
        # Set some existing env vars
        monkeypatch.setenv("EXISTING_VAR", "value")
        
        # Prepare environment
        env_vars = orchestrator._prepare_environment()
        
        # Verify legacy vars are included
        assert "TAP_ORACLE_WMS_HOST" in env_vars
        assert env_vars["TAP_ORACLE_WMS_HOST"] == "wms.local"
        
        # Verify Meltano vars
        assert env_vars["MELTANO_ENVIRONMENT"] == "test"
        assert "MELTANO_PROJECT_ROOT" in env_vars
        
        # Verify existing vars preserved
        assert env_vars["EXISTING_VAR"] == "value"


class TestConnectionManagerIntegration:
    """Test connection manager FLEXT integration."""
    
    def test_connection_manager_with_flext(self):
        """Test that connection manager uses FLEXT libraries."""
        from src.oracle.connection_manager import OracleConnectionManager, OracleConnectionConfig
        
        # Verify imports work (flext libraries installed)
        config = OracleConnectionConfig(
            host="localhost",
            service_name="TEST",
            username="user",
            password="pass",
        )
        
        # Verify it has FLEXT config conversion
        assert hasattr(config, "to_flext_config")
        
        # Create manager
        manager = OracleConnectionManager(config)
        
        # Verify FLEXT attributes
        assert hasattr(manager, "_flext_config")
        assert hasattr(manager, "_connection_service")


class TestAlertManagerIntegration:
    """Test alert manager FLEXT integration."""
    
    def test_alert_manager_uses_flext_logging(self):
        """Test that alert manager uses FLEXT observability."""
        from src.monitoring.alert_manager import AlertManager
        
        # Should not raise import errors
        manager = AlertManager.__module__
        
        # Verify module uses flext logging (by checking imports in the module)
        import src.monitoring.alert_manager as am_module
        assert hasattr(am_module, "get_logger")
        assert not hasattr(am_module, "logging")  # Standard logging should not be imported


if __name__ == "__main__":
    pytest.main([__file__, "-v"])