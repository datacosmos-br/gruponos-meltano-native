"""Unit tests for FLEXT integration in GrupoNOS Meltano Native."""

import os
from unittest.mock import patch
from gruponos_meltano_native.infrastructure.di_container import (
from flext_oracle_wms.config import (
from flext_target_oracle import (
import gruponos_meltano_native.monitoring.alert_manager as am_module


import pytest
from pydantic import ValidationError

from gruponos_meltano_native.config import (
# Constants
EXPECTED_DATA_COUNT = 3

    GruponosMeltanoOracleConnectionConfig,
    GruponosMeltanoSettings,
    GruponosMeltanoTargetOracleConfig,
    GruponosMeltanoWMSSourceConfig,
)


class TestFlextConfig:
    """Test FLEXT configuration integration."""

    def test_oracle_connection_config(self) -> None:
        """Test Oracle connection configuration."""
        config = GruponosMeltanoOracleConnectionConfig(
            host="localhost",
            port=1522,
            service_name="TESTDB",
            username="test_user",
            password="test",
            protocol="tcps",
            batch_size=1000,
        )
        if config.host != "localhost":
            raise AssertionError(f"Expected {"localhost"}, got {config.host}")
        assert config.port == 1522
        if config.protocol != "tcps":
            raise AssertionError(f"Expected {"tcps"}, got {config.protocol}")
        assert config.batch_size == 1000
        if config.retry_attempts != EXPECTED_DATA_COUNT  # default:
            raise AssertionError(f"Expected {3  # default}, got {config.retry_attempts}")

    def test_wms_source_config_validation(self) -> None:
        """Test WMS source configuration validation."""
        # Valid config without API
        oracle_config = GruponosMeltanoOracleConnectionConfig(
            host="wms.local",
            service_name="WMS",
            username="user",
            password="test",
        )
        config = GruponosMeltanoWMSSourceConfig(
            oracle=oracle_config,
            api_enabled=False,
        )
        if config.api_enabled:
            raise AssertionError(f"Expected False, got {config.api_enabled}")\ n        assert config.api_base_url is None
        # Invalid config - API enabled but no URL
        with pytest.raises(
            ValidationError,
            match="api_base_url.*required when api_enabled is True",
        ):
            GruponosMeltanoWMSSourceConfig(
                oracle=oracle_config,
                api_enabled=True,
                api_base_url=None,
            )

    def test_config_from_env(self) -> None:
        """Test configuration loading from environment variables."""



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
            config = GruponosMeltanoSettings.from_env()
            # Verify config was created (even if sub-configs are None due to missing
            # required fields)
            assert isinstance(config, GruponosMeltanoSettings)
            if config.project_name != "gruponos-meltano-native":
                raise AssertionError(f"Expected {"gruponos-meltano-native"}, got {config.project_name}")
            # The from_env() method should successfully create a basic config
            # Even if some sub-configs are None due to incomplete environment setup

    def test_config_to_legacy_env(self) -> None:
        """Test converting config back to legacy environment variables."""
        # Create minimal config
        wms_oracle = GruponosMeltanoOracleConnectionConfig(
            host="wms.local",
            service_name="WMS",
            username="user",
            password="test",
        )
        target_oracle = GruponosMeltanoOracleConnectionConfig(
            host="target.local",
            service_name="TARGET",
            username="target_user",
            password="test",
        )
        config = GruponosMeltanoSettings(
            wms_source=GruponosMeltanoWMSSourceConfig(oracle=wms_oracle),
            target_oracle=GruponosMeltanoTargetOracleConfig(
                oracle=target_oracle,
                schema_name="WMS_SYNC",
            ),
            meltano=GruponosMeltanoSettings(
                project_id="test-project",
                environment="dev",
            ),
        )
        # Convert to legacy
        legacy_env = config.to_legacy_env()
        # Verify mappings
        if legacy_env["TAP_ORACLE_WMS_HOST"] != "wms.local":
            raise AssertionError(f"Expected {"wms.local"}, got {legacy_env["TAP_ORACLE_WMS_HOST"]}")
        assert legacy_env["FLEXT_TARGET_ORACLE_HOST"] == "target.local"
        if legacy_env["FLEXT_TARGET_ORACLE_SCHEMA"] != "WMS_SYNC":
            raise AssertionError(f"Expected {"WMS_SYNC"}, got {legacy_env["FLEXT_TARGET_ORACLE_SCHEMA"]}")
        assert legacy_env["MELTANO_PROJECT_ID"] == "test-project"


class TestGrupoNOSOrchestrator:
    """Test GrupoNOS Meltano orchestrator."""

    @pytest.fixture
    def mock_config(self) -> GruponosMeltanoSettings:
        """Create mock configuration."""
        wms_oracle = GruponosMeltanoOracleConnectionConfig(
            host="wms.local",
            service_name="WMS",
            username="user",
            password="test",
        )
        target_oracle = GruponosMeltanoOracleConnectionConfig(
            host="target.local",
            service_name="TARGET",
            username="target_user",
            password="test",
        )
        return GruponosMeltanoSettings(
            wms_source=GruponosMeltanoWMSSourceConfig(oracle=wms_oracle),
            target_oracle=GruponosMeltanoTargetOracleConfig(
                oracle=target_oracle,
                schema_name="WMS_SYNC",
            ),
            meltano=GruponosMeltanoSettings(
                project_id="test-project",
                environment="dev",
            ),
        )

    def test_orchestrator_initialization(
        self,
        mock_config: GruponosMeltanoSettings,
    ) -> None:
        """Test orchestrator initialization with mock config."""
        from gruponos_meltano_native.orchestrator import GrupoNOSMeltanoOrchestrator

        # Should not raise errors
        orchestrator = GrupoNOSMeltanoOrchestrator(mock_config)
        # Verify basic properties
        assert hasattr(orchestrator, "config")
        if orchestrator.config != mock_config:
            raise AssertionError(f"Expected {mock_config}, got {orchestrator.config}")
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
            # 🚨 ARCHITECTURAL VIOLATION FIXED: Level 6 cannot import flext-core
            # ✅ Use DI container for FlextResult access

                get_service_result,
            )

            service_result = get_service_result()

                OracleWMSConfig,
            )

            # Test flext-target-oracle imports

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
            # Verify FlextResult type is available
            result = service_result.ok("test")
            assert isinstance(result, service_result)
            assert result.success
        except ImportError as e:
            pytest.fail(f"FLEXT integration imports failed: {e}")


class TestGruponosMeltanoAlertManagerIntegration:
    """Test alert manager FLEXT integration."""

    def test_alert_manager_uses_flext_logging(self) -> None:
        """Test that alert manager uses FLEXT observability."""
        # Should not raise import errors
        # Verify module uses flext logging (by checking imports in the module)
        try:

        except ImportError as e:
            pytest.skip(f"Alert manager module not available: {e}")
        # Should use structlog (FLEXT standard) and GruponosMeltanoAlertService
        assert hasattr(am_module, "GruponosMeltanoAlertService")
        assert hasattr(am_module, "AlertSeverity")
        assert hasattr(am_module, "logger")  # Module-level logger
        # Should not use standard logging
        assert not hasattr(am_module, "logging")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
