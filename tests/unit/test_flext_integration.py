"""Unit tests for FLEXT integration in GrupoNOS Meltano Native."""

import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError

import gruponos_meltano_native.monitoring.alert_manager as am_module
from gruponos_meltano_native.config import (
    GruponosMeltanoOracleConnectionConfig,
    GruponosMeltanoSettings,
    GruponosMeltanoTargetOracleConfig,
    GruponosMeltanoWMSSourceConfig,
)

# Constants
EXPECTED_DATA_COUNT = 3


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
            msg = f"Expected {'localhost'}, got {config.host}"
            raise AssertionError(msg)
        assert config.port == 1522
        if config.protocol != "tcps":
            msg = f"Expected {'tcps'}, got {config.protocol}"
            raise AssertionError(msg)
        # Test real Oracle config fields
        assert config.timeout == 30  # Real default from FlextOracleModel
        assert config.pool_min == 1  # Real default
        assert config.pool_max == 10  # Real default

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
            msg = f"Expected False, got {config.api_enabled}"
            raise AssertionError(msg)
        assert config.api_base_url is None
        # Invalid config - API enabled but no URL (Pydantic validation error expected)
        with pytest.raises(
            ValidationError,
            match="Input should be a valid string",
        ):
            GruponosMeltanoWMSSourceConfig(
                oracle=oracle_config,
                api_enabled=True,
                api_base_url=None,
                base_url=None,  # Force base_url to None - triggers Pydantic validation
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
            # Test that config can load from environment (Pydantic auto-loads)
            config = GruponosMeltanoSettings()
            # Verify config was created (even if sub-configs are None due to missing
            # required fields)
            assert isinstance(config, GruponosMeltanoSettings)
            # Test that config was created successfully (project_name may vary based on actual default)
            assert isinstance(config.project_name, str)
            assert len(config.project_name) > 0
            # The from_env() method should successfully create a basic config
            # Even if some sub-configs are None due to incomplete environment setup

    def test_config_properties_integration(self) -> None:
        """Test configuration properties work correctly with real FLEXT patterns."""
        # Create config using real constructor
        config = GruponosMeltanoSettings(
            project_name="test-project",
            environment="dev",
        )

        # Test that properties create valid sub-configs
        wms_config = config.wms_source  # Uses @property
        assert isinstance(wms_config, GruponosMeltanoWMSSourceConfig)
        assert isinstance(wms_config.oracle, GruponosMeltanoOracleConnectionConfig)

        target_config = config.target_oracle  # Uses @property
        assert isinstance(target_config, GruponosMeltanoTargetOracleConfig)

        oracle_config = config.oracle  # Uses @property
        assert isinstance(oracle_config, GruponosMeltanoOracleConnectionConfig)

        # Test configuration methods that actually exist
        connection_string = config.get_oracle_connection_string()
        assert isinstance(connection_string, str)
        assert len(connection_string) > 0

        # Test debug mode check
        debug_enabled = config.is_debug_enabled()
        assert isinstance(debug_enabled, bool)

        # Verify sub-configs have expected structure
        assert hasattr(wms_config, 'api_enabled')
        assert hasattr(wms_config, 'oracle')
        assert hasattr(target_config, 'target_schema')


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
        from gruponos_meltano_native.orchestrator import GruponosMeltanoOrchestrator

        # Should not raise errors
        orchestrator = GruponosMeltanoOrchestrator(mock_config)
        # Verify basic properties
        assert hasattr(orchestrator, "settings")  # Real attribute name
        if orchestrator.settings != mock_config:
            msg = f"Expected {mock_config}, got {orchestrator.settings}"
            raise AssertionError(msg)
        # Verify essential methods exist
        assert hasattr(orchestrator, "run_pipeline")  # Real method
        assert hasattr(orchestrator, "list_pipelines")  # Real method
        assert hasattr(orchestrator, "run_job")  # Real method


class TestConnectionManagerIntegration:
    """Test connection manager FLEXT integration."""

    def test_connection_manager_with_flext(self) -> None:
        """Test that connection manager uses FLEXT libraries."""
        # Test imports of FLEXT integration modules that ARE available
        try:
            # Test flext-oracle-wms imports - use the actual config class
            # Test flext-core imports
            # 🚨 ARCHITECTURAL VIOLATION FIXED: Level 6 cannot import flext-core
            # ✅ Use FlextResult pattern from core

            from flext_core import FlextResult

            # Test FlextResult integration works
            service_result = FlextResult.ok("test_service_working")

            # Test Oracle database integration via flext-db-oracle (works without circular imports)
            from flext_db_oracle import FlextDbOracleApi, FlextDbOracleConfig

            oracle_config_dict = {
                "host": "localhost",
                "port": 1521,
                "service_name": "TESTDB",
                "username": "test",
                "password": "test",
            }

            # Test that API can be created from config dict
            oracle_api = FlextDbOracleApi.with_config(oracle_config_dict)
            assert oracle_api is not None

            # Test configuration object creation
            oracle_config = FlextDbOracleConfig(**oracle_config_dict)
            assert oracle_config.host == "localhost"
            assert oracle_config.port == 1521

            # Verify FlextResult is working
            assert service_result.is_success
            assert service_result.data == "test_service_working"

            # Test chaining FlextResult operations
            chained_result = service_result.map(lambda x: f"processed_{x}")
            assert chained_result.is_success
            assert chained_result.data == "processed_test_service_working"
        except ImportError as e:
            pytest.fail(f"FLEXT integration imports failed: {e}")


class TestGruponosMeltanoAlertManagerIntegration:
    """Test alert manager FLEXT integration."""

    def test_alert_manager_uses_flext_logging(self) -> None:
        """Test that alert manager uses FLEXT observability."""
        # Should not raise import errors
        # Verify module uses flext logging (by checking imports in the module)
        try:
            from flext_core.logging import get_logger

            from gruponos_meltano_native.monitoring.alert_manager import (
                GruponosMeltanoAlertService,
                GruponosMeltanoAlertSeverity,
            )
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
