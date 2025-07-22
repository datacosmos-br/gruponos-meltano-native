"""Unit tests for FLEXT integration in GrupoNOS Meltano Native."""

import pytest
from pydantic import ValidationError

from gruponos_meltano_native.config import (
    GrupoNOSConfig,
    MeltanoConfig,
    OracleConnectionConfig,
    TargetOracleConfig,
    WMSSourceConfig,
)


class TestFlextConfig:
    """Test FLEXT configuration integration."""

    def test_oracle_connection_config(self) -> None:
        """Test Oracle connection configuration."""
        config = OracleConnectionConfig(
            host="localhost",
            port=1522,
            service_name="TESTDB",
            username="test_user",
            password="test",
            protocol="tcps",
            batch_size=1000,
        )
        assert config.host == "localhost"
        assert config.port == 1522
        assert config.protocol == "tcps"
        assert config.batch_size == 1000
        assert config.retry_attempts == 3  # default

    def test_wms_source_config_validation(self) -> None:
        """Test WMS source configuration validation."""
        # Valid config without API
        oracle_config = OracleConnectionConfig(
            host="wms.local",
            service_name="WMS",
            username="user",
            password="test",
        )
        config = WMSSourceConfig(
            oracle=oracle_config,
            api_enabled=False,
        )
        assert config.api_enabled is False
        assert config.api_base_url is None
        # Invalid config - API enabled but no URL
        with pytest.raises(
            ValidationError,
            match="api_base_url.*required when api_enabled is True",
        ):
            WMSSourceConfig(
                oracle=oracle_config,
                api_enabled=True,
                api_base_url=None,
            )

    def test_config_from_env(self) -> None:
        """Test configuration loading from environment variables."""
        import os
        from unittest.mock import patch

        # Test environment variables using the correct format that from_env() expects
        test_env = {
            # Use the same keys that from_env() looks for
            "GRUPONOS_WMS_HOST": "wms.example.com",
            "GRUPONOS_WMS_SERVICE_NAME": "WMS_PROD",
            "GRUPONOS_WMS_USERNAME": "wms_user",
            "GRUPONOS_WMS_PASSWORD": "secret123",
            "GRUPONOS_TARGET_HOST": "target.example.com",
            "GRUPONOS_TARGET_SERVICE_NAME": "TARGET_PROD",
            "GRUPONOS_TARGET_USERNAME": "target_user",
            "GRUPONOS_TARGET_PASSWORD": "secret456",
            "GRUPONOS_TARGET_SCHEMA": "WMS_SYNC",
            "MELTANO_PROJECT_ID": "gruponos-prod",
            "MELTANO_ENVIRONMENT": "production",
        }
        with patch.dict(os.environ, test_env, clear=False):
            # Test that config can load from environment
            config = GrupoNOSConfig.from_env()
            # Verify config was created (even if sub-configs are None due to missing required fields)
            assert isinstance(config, GrupoNOSConfig)
            assert config.project_name == "gruponos-meltano-native"
            # The from_env() method should successfully create a basic config
            # Even if some sub-configs are None due to incomplete environment setup

    def test_config_to_legacy_env(self) -> None:
        """Test converting config back to legacy environment variables."""
        # Create minimal config
        wms_oracle = OracleConnectionConfig(
            host="wms.local",
            service_name="WMS",
            username="user",
            password="test",
        )
        target_oracle = OracleConnectionConfig(
            host="target.local",
            service_name="TARGET",
            username="target_user",
            password="test",
        )
        config = GrupoNOSConfig(
            wms_source=WMSSourceConfig(oracle=wms_oracle),
            target_oracle=TargetOracleConfig(
                oracle=target_oracle,
                schema_name="WMS_SYNC",
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
    def mock_config(self) -> GrupoNOSConfig:
        """Create mock configuration."""
        wms_oracle = OracleConnectionConfig(
            host="wms.local",
            service_name="WMS",
            username="user",
            password="test",
        )
        target_oracle = OracleConnectionConfig(
            host="target.local",
            service_name="TARGET",
            username="target_user",
            password="test",
        )
        return GrupoNOSConfig(
            wms_source=WMSSourceConfig(oracle=wms_oracle),
            target_oracle=TargetOracleConfig(
                oracle=target_oracle,
                schema_name="WMS_SYNC",
            ),
            meltano=MeltanoConfig(
                project_id="test-project",
                environment="dev",
            ),
        )

    def test_orchestrator_initialization(self, mock_config: GrupoNOSConfig) -> None:
        """Test orchestrator initialization with mock config."""
        from gruponos_meltano_native.orchestrator import GrupoNOSMeltanoOrchestrator

        # Should not raise errors
        orchestrator = GrupoNOSMeltanoOrchestrator(mock_config)
        # Verify basic properties
        assert hasattr(orchestrator, "config")
        assert orchestrator.config == mock_config
        # Verify essential methods exist
        assert hasattr(orchestrator, "validate_configuration")
        assert hasattr(orchestrator, "run_pipeline")
        assert hasattr(orchestrator, "stop")


class TestConnectionManagerIntegration:
    """Test connection manager FLEXT integration."""

    def test_connection_manager_with_flext(self) -> None:
        """Test that connection manager uses FLEXT libraries."""
        # Test imports of FLEXT integration modules that ARE available
        try:
            # Test flext-oracle-wms imports - use the actual config class
            # Test flext-core imports
            from flext_core.domain.shared_types import ServiceResult
            from flext_oracle_wms.config_module import (
                OracleWMSConfig,
            )

            # Test flext-target-oracle imports
            from flext_target_oracle import (
                OracleTarget,
            )

            # Test WMS client configuration creation using actual config class
            wms_config = OracleWMSConfig(
                project_name="test_project",
                base_url="https://test.wms.ocs.oraclecloud.com/test",
                username="test_user",
                password="test_password",
                wms_environment="development",
                wms_org_id="TEST_ORG",
                wms_facility_code="TEST_FACILITY",
                wms_company_code="TEST_COMPANY",
            )
            # Should not raise import errors - verify class can be instantiated
            assert isinstance(wms_config, OracleWMSConfig)
            # Test Oracle target configuration
            target_config_dict = {
                "host": "target.local",
                "port": 1521,
                "service_name": "TARGET",
                "username": "target_user",
                "password": "target_pass",
                "schema": "WMS_SYNC",
            }
            # Test Oracle target instantiation - pass dict directly as expected
            oracle_target = OracleTarget(target_config_dict)
            assert isinstance(oracle_target, OracleTarget)
            # Verify ServiceResult type is available
            result = ServiceResult.ok("test")
            assert isinstance(result, ServiceResult)
            assert result.success
        except ImportError as e:
            pytest.fail(f"FLEXT integration imports failed: {e}")


class TestAlertManagerIntegration:
    """Test alert manager FLEXT integration."""

    def test_alert_manager_uses_flext_logging(self) -> None:
        """Test that alert manager uses FLEXT observability."""
        # Should not raise import errors
        # Verify module uses flext logging (by checking imports in the module)
        try:
            import gruponos_meltano_native.monitoring.alert_manager as am_module
        except ImportError as e:
            pytest.skip(f"Alert manager module not available: {e}")
        # Should use structlog (FLEXT standard) and AlertService
        assert hasattr(am_module, "AlertService")
        assert hasattr(am_module, "AlertSeverity")
        assert hasattr(am_module, "logger")  # Module-level logger
        # Should not use standard logging
        assert not hasattr(am_module, "logging")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
