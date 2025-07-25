"""Unit tests for configuration functionality."""

import pytest
from pydantic import ValidationError

from gruponos_meltano_native.config import (
    GruponosMeltanoAlertConfig,
    GruponosMeltanoOracleConnectionConfig,
    GruponosMeltanoSettings,
    GruponosMeltanoTargetOracleConfig,
    GruponosMeltanoWMSSourceConfig,
)


class TestConfiguration:
    """Test configuration classes."""

    def test_oracle_connection_config_creation(self) -> None:
        """Test Oracle connection configuration creation."""
        config = GruponosMeltanoOracleConnectionConfig(
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
        config = GruponosMeltanoOracleConnectionConfig(
            host="localhost",
            service_name="XE",
            username="user",
            password="pass",
        )

        # Check defaults
        assert config.port == 1522
        assert config.protocol == "tcps"
        assert config.wallet_location == ""
        assert config.trust_store_location == ""
        assert config.key_store_location == ""

    def test_wms_source_config_creation(self) -> None:
        """Test WMS source configuration creation."""
        oracle_config = GruponosMeltanoOracleConnectionConfig(
            host="wms.local",
            service_name="WMS",
            username="user",
            password="pass",
        )

        wms_config = GruponosMeltanoWMSSourceConfig(
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
        oracle_config = GruponosMeltanoOracleConnectionConfig(
            host="wms.local",
            service_name="WMS",
            username="user",
            password="pass",
        )

        # Should fail when API enabled but no URL provided
        with pytest.raises(ValidationError):
            GruponosMeltanoWMSSourceConfig(
                oracle=oracle_config,
                api_enabled=True,
                api_base_url=None,
            )

    def test_target_oracle_config_creation(self) -> None:
        """Test target Oracle configuration creation."""
        GruponosMeltanoOracleConnectionConfig(
            host="target.local",
            service_name="TARGET",
            username="target_user",
            password="target_pass",
        )

        target_config = GruponosMeltanoTargetOracleConfig(
            target_schema="WMS_SYNC",
            drop_target_tables=True,
            enable_compression=False,
        )

        assert target_config.target_schema == "WMS_SYNC"
        assert target_config.drop_target_tables is True
        assert target_config.enable_compression is False

    def test_meltano_settings_creation(self) -> None:
        """Test main Meltano settings creation."""
        settings = GruponosMeltanoSettings(
            meltano_project_root="./test-project",
            meltano_environment="prod",
            meltano_state_backend="s3",
            debug=True,
        )

        assert settings.meltano_project_root.endswith("test-project")
        assert settings.meltano_environment == "prod"
        assert settings.meltano_state_backend == "s3"
        assert settings.debug is True

    def test_alert_config_creation(self) -> None:
        """Test alert configuration creation."""
        config = GruponosMeltanoAlertConfig(
            webhook_enabled=True,
            webhook_url="https://hooks.slack.com/webhook",
            email_enabled=True,
            email_recipients=["admin@example.com"],
            alert_threshold=10,
        )

        assert config.webhook_enabled is True
        assert config.webhook_url == "https://hooks.slack.com/webhook"
        assert config.email_enabled is True
        assert config.email_recipients == ["admin@example.com"]
        assert config.alert_threshold == 10

    def test_gruponos_config_creation(self) -> None:
        """Test main GrupoNOS configuration creation."""
        GruponosMeltanoOracleConnectionConfig(
            host="wms.local",
            service_name="WMS",
            username="wms_user",
            password="wms_pass",
        )

        GruponosMeltanoOracleConnectionConfig(
            host="target.local",
            service_name="TARGET",
            username="target_user",
            password="target_pass",
        )

        wms_source = GruponosMeltanoWMSSourceConfig()
        target_oracle = GruponosMeltanoTargetOracleConfig(target_schema="SYNC")
        alerts = GruponosMeltanoAlertConfig()

        config = GruponosMeltanoSettings(
            wms_source=wms_source,
            target_oracle=target_oracle,
            alerts=alerts,
            debug=True,
        )

        assert config.wms_source == wms_source
        assert config.target_oracle == target_oracle
        assert config.alerts == alerts
        assert config.debug is True

    def test_config_oracle_connection_string(self) -> None:
        """Test Oracle connection string generation."""
        oracle_config = GruponosMeltanoOracleConnectionConfig(
            host="wms.local",
            port=1521,
            service_name="WMS",
            username="wms_user",
            password="wms_pass",
        )

        config = GruponosMeltanoSettings(oracle=oracle_config)

        connection_string = config.get_oracle_connection_string()
        expected = "wms_user/wms_pass@wms.local:1521/WMS"
        assert connection_string == expected
