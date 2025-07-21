"""Unit tests for configuration functionality."""

import pytest
from pydantic import ValidationError

from gruponos_meltano_native.config import (
    AlertConfig,
    GrupoNOSConfig,
    MeltanoConfig,
    OracleConnectionConfig,
    TargetOracleConfig,
    WMSSourceConfig,
)


class TestConfiguration:
    """Test configuration classes."""

    def test_oracle_connection_config_creation(self) -> None:
        """Test Oracle connection configuration creation."""
        config = OracleConnectionConfig(
            host="oracle.example.com",
            port=1521,
            service_name="PROD",
            username="test_user",
            password="test_pass",
            protocol="tcps",
        )

        assert config.host == "oracle.example.com"
        assert config.port == 1521
        assert config.service_name == "PROD"
        assert config.username == "test_user"
        assert config.password == "test_pass"
        assert config.protocol == "tcps"

    def test_oracle_connection_config_defaults(self) -> None:
        """Test Oracle connection configuration defaults."""
        config = OracleConnectionConfig(
            host="localhost",
            service_name="XE",
            username="user",
            password="pass",
        )

        # Check defaults
        assert config.port == 1522
        assert config.protocol == "tcps"
        assert config.retry_attempts == 3
        assert config.connection_timeout == 60
        assert config.batch_size == 1000
        assert config.connection_pool_size == 5

    def test_wms_source_config_creation(self) -> None:
        """Test WMS source configuration creation."""
        oracle_config = OracleConnectionConfig(
            host="wms.local",
            service_name="WMS",
            username="user",
            password="pass",
        )

        wms_config = WMSSourceConfig(
            oracle=oracle_config,
            api_enabled=True,
            api_base_url="https://wms.example.com/api",
            api_username="api_user",
            api_password="api_pass",
        )

        assert wms_config.oracle == oracle_config
        assert wms_config.api_enabled is True
        assert wms_config.api_base_url == "https://wms.example.com/api"

    def test_wms_source_config_validation(self) -> None:
        """Test WMS source configuration validation."""
        oracle_config = OracleConnectionConfig(
            host="wms.local",
            service_name="WMS",
            username="user",
            password="pass",
        )

        # Should fail when API enabled but no URL provided
        with pytest.raises(ValidationError):
            WMSSourceConfig(
                oracle=oracle_config,
                api_enabled=True,
                api_base_url=None,
            )

    def test_target_oracle_config_creation(self) -> None:
        """Test target Oracle configuration creation."""
        oracle_config = OracleConnectionConfig(
            host="target.local",
            service_name="TARGET",
            username="target_user",
            password="target_pass",
        )

        target_config = TargetOracleConfig(
            oracle=oracle_config,
            schema_name="WMS_SYNC",
            truncate_before_load=True,
            analyze_after_load=False,
        )

        assert target_config.oracle == oracle_config
        assert target_config.schema_name == "WMS_SYNC"
        assert target_config.truncate_before_load is True
        assert target_config.analyze_after_load is False

    def test_meltano_config_creation(self) -> None:
        """Test Meltano configuration creation."""
        config = MeltanoConfig(
            project_id="test-project",
            environment="prod",
            state_backend="s3",
            state_backend_uri="s3://bucket/state",
            log_level="DEBUG",
        )

        assert config.project_id == "test-project"
        assert config.environment == "prod"
        assert config.state_backend == "s3"
        assert config.log_level == "DEBUG"

    def test_alert_config_creation(self) -> None:
        """Test alert configuration creation."""
        config = AlertConfig(
            max_sync_duration_minutes=120,
            max_error_rate_percent=10.0,
            webhook_enabled=True,
            webhook_url="https://hooks.slack.com/webhook",
            email_enabled=True,
            alert_email="admin@example.com",
        )

        assert config.max_sync_duration_minutes == 120
        assert config.max_error_rate_percent == 10.0
        assert config.webhook_enabled is True
        assert config.email_enabled is True

    def test_gruponos_config_creation(self) -> None:
        """Test main GrupoNOS configuration creation."""
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

        wms_source = WMSSourceConfig(oracle=oracle_wms)
        target_oracle = TargetOracleConfig(oracle=oracle_target, schema_name="SYNC")
        meltano = MeltanoConfig(project_id="test", environment="dev")
        alerts = AlertConfig()

        config = GrupoNOSConfig(
            wms_source=wms_source,
            target_oracle=target_oracle,
            meltano=meltano,
            alerts=alerts,
            debug_mode=True,
        )

        assert config.wms_source == wms_source
        assert config.target_oracle == target_oracle
        assert config.meltano == meltano
        assert config.alerts == alerts
        assert config.debug_mode is True

    def test_config_to_legacy_env(self) -> None:
        """Test configuration to legacy environment variables."""
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

        config = GrupoNOSConfig(
            wms_source=WMSSourceConfig(oracle=oracle_wms),
            target_oracle=TargetOracleConfig(oracle=oracle_target, schema_name="SYNC"),
            meltano=MeltanoConfig(project_id="test", environment="dev"),
        )

        legacy_env = config.to_legacy_env()

        assert legacy_env["TAP_ORACLE_WMS_HOST"] == "wms.local"
        assert legacy_env["FLEXT_TARGET_ORACLE_HOST"] == "target.local"
        assert legacy_env["MELTANO_PROJECT_ID"] == "test"
