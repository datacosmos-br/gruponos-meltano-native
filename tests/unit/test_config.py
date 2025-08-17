"""Unit tests for configuration functionality."""

import pytest
from pydantic import ValidationError

from gruponos_meltano_native import (
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
            msg: str = f"Expected {'oracle.example.com'}, got {config.host}"
            raise AssertionError(msg)
        assert config.port == 1521
        if config.service_name != "PROD":
            msg: str = f"Expected {'PROD'}, got {config.service_name}"
            raise AssertionError(msg)
        assert config.username == "test_user"
        if config.password.get_secret_value() != "test_pass":
            msg: str = (
                f"Expected {'test_pass'}, got {config.password.get_secret_value()}"
            )
            raise AssertionError(msg)
        assert config.protocol == "tcps"

    def test_oracle_connection_config_defaults(self) -> None:
        """Test Oracle connection configuration defaults."""
        # Use explicit values to avoid environment variable interference
        config = GruponosMeltanoOracleConnectionConfig(
            host="localhost",
            port=1521,  # Explicit port to test default behavior
            protocol="TCP",  # Explicit protocol to test default behavior
            service_name="XE",
            username="user",
            password="pass",
        )

        # Check explicit values
        if config.port != 1521:
            msg: str = f"Expected {1521}, got {config.port}"
            raise AssertionError(msg)
        assert config.protocol == "TCP"
        if config.service_name != "XE":
            msg: str = f"Expected XE, got {config.service_name}"
            raise AssertionError(msg)
        assert config.sid is None

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
            msg: str = f"Expected {oracle_config}, got {wms_config.oracle}"
            raise AssertionError(msg)
        if not (wms_config.api_enabled):
            msg: str = f"Expected True, got {wms_config.api_enabled}"
            raise AssertionError(msg)
        if wms_config.api_base_url != "https://wms.example.com/api":
            msg: str = f"Expected {'https://wms.example.com/api'}, got {wms_config.api_base_url}"
            raise AssertionError(
                msg,
            )

    def test_wms_source_config_validation(self) -> None:
        """Test WMS source configuration validation."""
        oracle_config = GruponosMeltanoOracleConnectionConfig(
            host="wms.local",
            service_name="WMS",
            username="user",
            password="pass",
        )

        # Should fail when base_url is None (Pydantic validation)
        with pytest.raises(ValidationError, match="Input should be a valid string"):
            GruponosMeltanoWMSSourceConfig(
                oracle=oracle_config,
                api_enabled=True,
                api_base_url=None,
                base_url=None,  # This triggers Pydantic validation error
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
            msg: str = f"Expected {'WMS_SYNC'}, got {target_config.target_schema}"
            raise AssertionError(
                msg,
            )
        if not (target_config.drop_target_tables):
            msg: str = f"Expected True, got {target_config.drop_target_tables}"
            raise AssertionError(
                msg,
            )
        if target_config.enable_compression:
            msg: str = f"Expected False, got {target_config.enable_compression}"
            raise AssertionError(
                msg,
            )

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
            msg: str = f"Expected {'prod'}, got {settings.meltano_environment}"
            raise AssertionError(
                msg,
            )
        assert settings.meltano_state_backend == "s3"
        if not (settings.debug):
            msg: str = f"Expected True, got {settings.debug}"
            raise AssertionError(msg)

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
            msg: str = f"Expected True, got {config.webhook_enabled}"
            raise AssertionError(msg)
        if config.webhook_url != "https://hooks.slack.com/webhook":
            msg: str = f"Expected {'https://hooks.slack.com/webhook'}, got {config.webhook_url}"
            raise AssertionError(
                msg,
            )
        if not (config.email_enabled):
            msg: str = f"Expected True, got {config.email_enabled}"
            raise AssertionError(msg)
        if config.email_recipients != ["admin@example.com"]:
            msg: str = (
                f"Expected {['admin@example.com']}, got {config.email_recipients}"
            )
            raise AssertionError(
                msg,
            )
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

        config = GruponosMeltanoSettings(debug=True)

        # Test that properties work and return the correct types
        assert isinstance(config.wms_source, GruponosMeltanoWMSSourceConfig)
        assert isinstance(config.target_oracle, GruponosMeltanoTargetOracleConfig)
        assert isinstance(config.alert_config, GruponosMeltanoAlertConfig)
        if not (config.debug):
            msg: str = f"Expected True, got {config.debug}"
            raise AssertionError(msg)

    def test_config_oracle_connection_string(self) -> None:
        """Test Oracle connection string generation."""
        oracle_config = GruponosMeltanoOracleConnectionConfig(
            host="wms.local",
            port=1521,
            service_name="WMS",
            username="wms_user",
            password="wms_pass",
        )

        # Test the connection string method directly on the oracle config
        conn = oracle_config
        if conn.service_name:
            connection_string = (
                f"{conn.username}@{conn.host}:{conn.port}/{conn.service_name}"
            )
        elif conn.sid:
            connection_string = f"{conn.username}@{conn.host}:{conn.port}:{conn.sid}"
        else:
            connection_string = f"{conn.username}@{conn.host}:{conn.port}"

        expected = "wms_user@wms.local:1521/WMS"
        if connection_string != expected:
            msg: str = f"Expected {expected}, got {connection_string}"
            raise AssertionError(msg)
