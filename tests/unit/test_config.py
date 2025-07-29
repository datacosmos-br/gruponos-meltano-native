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

        if config.host != "oracle.example.com":

            raise AssertionError(f"Expected {"oracle.example.com"}, got {config.host}")
        assert config.port == 1521
        if config.service_name != "PROD":
            raise AssertionError(f"Expected {"PROD"}, got {config.service_name}")
        assert config.username == "test_user"
        if config.password != "test_pass":
            raise AssertionError(f"Expected {"test_pass"}, got {config.password}")
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
        if config.port != 1522:
            raise AssertionError(f"Expected {1522}, got {config.port}")
        assert config.protocol == "tcps"
        if config.wallet_location != "":
            raise AssertionError(f"Expected {""}, got {config.wallet_location}")
        assert config.trust_store_location == ""
        if config.key_store_location != "":
            raise AssertionError(f"Expected {""}, got {config.key_store_location}")

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

        if wms_config.oracle != oracle_config:

            raise AssertionError(f"Expected {oracle_config}, got {wms_config.oracle}")
        if not (wms_config.api_enabled):
            raise AssertionError(f"Expected True, got {wms_config.api_enabled}")
        if wms_config.api_base_url != "https://wms.example.com/api":
            raise AssertionError(f"Expected {"https://wms.example.com/api"}, got {wms_config.api_base_url}")

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

        if target_config.target_schema != "WMS_SYNC":

            raise AssertionError(f"Expected {"WMS_SYNC"}, got {target_config.target_schema}")
        if not (target_config.drop_target_tables):
            raise AssertionError(f"Expected True, got {target_config.drop_target_tables}")
        if target_config.enable_compression:
            raise AssertionError(f"Expected False, got {target_config.enable_compression}")\ n
    def test_meltano_settings_creation(self) -> None:
        """Test main Meltano settings creation."""
        settings = GruponosMeltanoSettings(
            meltano_project_root="./test-project",
            meltano_environment="prod",
            meltano_state_backend="s3",
            debug=True,
        )

        assert settings.meltano_project_root.endswith("test-project")
        if settings.meltano_environment != "prod":
            raise AssertionError(f"Expected {"prod"}, got {settings.meltano_environment}")
        assert settings.meltano_state_backend == "s3"
        if not (settings.debug):
            raise AssertionError(f"Expected True, got {settings.debug}")

    def test_alert_config_creation(self) -> None:
        """Test alert configuration creation."""
        config = GruponosMeltanoAlertConfig(
            webhook_enabled=True,
            webhook_url="https://hooks.slack.com/webhook",
            email_enabled=True,
            email_recipients=["admin@example.com"],
            alert_threshold=10,
        )

        if not (config.webhook_enabled):

            raise AssertionError(f"Expected True, got {config.webhook_enabled}")
        if config.webhook_url != "https://hooks.slack.com/webhook":
            raise AssertionError(f"Expected {"https://hooks.slack.com/webhook"}, got {config.webhook_url}")
        if not (config.email_enabled):
            raise AssertionError(f"Expected True, got {config.email_enabled}")
        if config.email_recipients != ["admin@example.com"]:
            raise AssertionError(f"Expected {["admin@example.com"]}, got {config.email_recipients}")
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

        if config.wms_source != wms_source:

            raise AssertionError(f"Expected {wms_source}, got {config.wms_source}")
        assert config.target_oracle == target_oracle
        if config.alerts != alerts:
            raise AssertionError(f"Expected {alerts}, got {config.alerts}")
        if not (config.debug):
            raise AssertionError(f"Expected True, got {config.debug}")

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
        if connection_string != expected:
            raise AssertionError(f"Expected {expected}, got {connection_string}")
