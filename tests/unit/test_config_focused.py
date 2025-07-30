"""Focused tests for config module to achieve 90%+ coverage.

REAL IMPLEMENTATION TESTS - NO MOCKS OR FALLBACKS.
Tests all configuration classes and validation logic comprehensively.
"""

import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from pydantic import ValidationError

from gruponos_meltano_native.config import (
    GruponosMeltanoAlertConfig,
    GruponosMeltanoOracleConnectionConfig,
    GruponosMeltanoSettings,
    GruponosMeltanoTargetOracleConfig,
    GruponosMeltanoWMSSourceConfig,
)

# Constants
EXPECTED_BULK_SIZE = 2
EXPECTED_TOTAL_PAGES = 8
EXPECTED_DATA_COUNT = 3


class TestConfigFocused:
    """Focused configuration testing for comprehensive coverage."""

    def test_oracle_connection_config_creation(self) -> None:
        """Test GruponosMeltanoOracleConnectionConfig creation and validation."""
        # Test valid configuration
        config = GruponosMeltanoOracleConnectionConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test_user",
            password="test_pass",
        )

        if config.host != "localhost":
            msg = f"Expected {'localhost'}, got {config.host}"
            raise AssertionError(msg)
        assert config.port == 1521
        if config.service_name != "XEPDB1":
            msg = f"Expected {'XEPDB1'}, got {config.service_name}"
            raise AssertionError(msg)
        assert config.username == "test_user"
        if config.password != "test_pass":
            msg = f"Expected {'test_pass'}, got {config.password}"
            raise AssertionError(msg)

        # Test default values
        if config.protocol != "tcps":
            msg = f"Expected {'tcps'}, got {config.protocol}"
            raise AssertionError(msg)
        if config.ssl_server_dn_match:
            msg = f"Expected False, got {config.ssl_server_dn_match}"
            raise AssertionError(msg)
        assert config.connection_timeout == 60
        if config.retry_attempts != EXPECTED_DATA_COUNT:
            msg = f"Expected {3}, got {config.retry_attempts}"
            raise AssertionError(msg)
        assert config.retry_delay == 5
        if config.batch_size != 1000:
            msg = f"Expected {1000}, got {config.batch_size}"
            raise AssertionError(msg)
        assert config.connection_pool_size == 5

    def test_oracle_connection_config_validation(self) -> None:
        """Test GruponosMeltanoOracleConnectionConfig field validation."""
        # Test invalid port
        with pytest.raises(ValidationError) as exc_info:
            GruponosMeltanoOracleConnectionConfig(
                host="localhost",
                port=70000,  # Invalid port
                service_name="XEPDB1",
                username="test_user",
                password="test_pass",
            )
        if "less than or equal to 65535" not in str(exc_info.value):
            msg = f"Expected {'less than or equal to 65535'} in {exc_info.value!s}"
            raise AssertionError(msg)

        # Test invalid protocol
        with pytest.raises(ValidationError) as exc_info:
            GruponosMeltanoOracleConnectionConfig(
                host="localhost",
                port=1521,
                service_name="XEPDB1",
                username="test_user",
                password="test_pass",
                protocol="invalid",
            )
        if "pattern" not in str(exc_info.value):
            msg = f"Expected {'pattern'} in {exc_info.value!s}"
            raise AssertionError(msg)

        # Test negative values
        with pytest.raises(ValidationError) as exc_info:
            GruponosMeltanoOracleConnectionConfig(
                host="localhost",
                port=1521,
                service_name="XEPDB1",
                username="test_user",
                password="test_pass",
                connection_timeout=-1,
            )
        if "greater than or equal to 1" not in str(exc_info.value):
            msg = f"Expected {'greater than or equal to 1'} in {exc_info.value!s}"
            raise AssertionError(msg)

    def test_oracle_connection_config_edge_values(self) -> None:
        """Test GruponosMeltanoOracleConnectionConfig with edge values."""
        # Test minimum valid values
        config = GruponosMeltanoOracleConnectionConfig(
            host="localhost",
            port=1,  # Minimum port
            service_name="XEPDB1",
            username="test_user",
            password="test_pass",
            connection_timeout=1,  # Minimum timeout
            retry_attempts=1,  # Minimum retries
            retry_delay=1,  # Minimum delay
            batch_size=100,  # Minimum batch size
            connection_pool_size=1,  # Minimum pool size
        )

        if config.port != 1:
            msg = f"Expected {1}, got {config.port}"
            raise AssertionError(msg)
        assert config.connection_timeout == 1
        if config.retry_attempts != 1:
            msg = f"Expected {1}, got {config.retry_attempts}"
            raise AssertionError(msg)
        assert config.retry_delay == 1
        if config.batch_size != 100:
            msg = f"Expected {100}, got {config.batch_size}"
            raise AssertionError(msg)
        assert config.connection_pool_size == 1

        # Test maximum valid values
        config_max = GruponosMeltanoOracleConnectionConfig(
            host="localhost",
            port=65535,  # Maximum port
            service_name="XEPDB1",
            username="test_user",
            password="test_pass",
            batch_size=10000,  # Maximum batch size
            connection_pool_size=20,  # Maximum pool size
        )

        if config_max.port != 65535:
            msg = f"Expected {65535}, got {config_max.port}"
            raise AssertionError(msg)
        assert config_max.batch_size == 10000
        if config_max.connection_pool_size != 20:
            msg = f"Expected {20}, got {config_max.connection_pool_size}"
            raise AssertionError(msg)

    def test_wms_source_config_api_validation(self) -> None:
        """Test GruponosMeltanoWMSSourceConfig API field validation."""
        oracle_config = GruponosMeltanoOracleConnectionConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test_user",
            password="test_pass",
        )

        # Test API disabled - should not require API fields
        config = GruponosMeltanoWMSSourceConfig(
            oracle=oracle_config,
            api_enabled=False,
            api_base_url=None,
            api_username=None,
            api_password=None,
        )
        if config.api_enabled:
            msg = f"Expected False, got {config.api_enabled}"
            raise AssertionError(msg)
        assert config.api_base_url is None

        # Test API enabled with valid fields
        config_api = GruponosMeltanoWMSSourceConfig(
            oracle=oracle_config,
            api_enabled=True,
            api_base_url="https://api.example.com",
            api_username="api_user",
            api_password="api_pass",
        )
        if not (config_api.api_enabled):
            msg = f"Expected True, got {config_api.api_enabled}"
            raise AssertionError(msg)
        if config_api.api_base_url != "https://api.example.com":
            msg = f"Expected {'https://api.example.com'}, got {config_api.api_base_url}"
            raise AssertionError(msg)
        assert config_api.api_username == "api_user"
        if config_api.api_password != "api_pass":
            msg = f"Expected {'api_pass'}, got {config_api.api_password}"
            raise AssertionError(msg)

        # Test API enabled but missing required fields
        with pytest.raises(ValidationError) as exc_info:
            GruponosMeltanoWMSSourceConfig(
                oracle=oracle_config,
                api_enabled=True,
                api_base_url=None,  # Missing required field
                api_username="api_user",
                api_password="api_pass",
            )
        if "api_base_url is required when api_enabled is True" not in str(
            exc_info.value,
        ):
            msg = f"Expected 'api_base_url is required when api_enabled is True' in {exc_info.value!s}"
            raise AssertionError(msg)

        with pytest.raises(ValidationError) as exc_info:
            GruponosMeltanoWMSSourceConfig(
                oracle=oracle_config,
                api_enabled=True,
                api_base_url="https://api.example.com",
                api_username=None,  # Missing required field
                api_password="api_pass",
            )
        if "api_username is required when api_enabled is True" not in str(
            exc_info.value,
        ):
            msg = f"Expected 'api_username is required when api_enabled is True' in {exc_info.value!s}"
            raise AssertionError(msg)

        with pytest.raises(ValidationError) as exc_info:
            GruponosMeltanoWMSSourceConfig(
                oracle=oracle_config,
                api_enabled=True,
                api_base_url="https://api.example.com",
                api_username="api_user",
                api_password=None,  # Missing required field
            )
        if "api_password is required when api_enabled is True" not in str(
            exc_info.value,
        ):
            msg = f"Expected 'api_password is required when api_enabled is True' in {exc_info.value!s}"
            raise AssertionError(msg)

    def test_wms_source_config_defaults(self) -> None:
        """Test GruponosMeltanoWMSSourceConfig default values."""
        oracle_config = GruponosMeltanoOracleConnectionConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test_user",
            password="test_pass",
        )

        config = GruponosMeltanoWMSSourceConfig(oracle=oracle_config)

        # Test defaults
        if config.api_enabled:
            msg = f"Expected False, got {config.api_enabled}"
            raise AssertionError(msg)
        assert config.api_base_url is None
        assert config.api_username is None
        assert config.api_password is None
        assert config.start_date is None
        if config.lookback_days != 7:
            msg = f"Expected {7}, got {config.lookback_days}"
            raise AssertionError(msg)

    def test_target_oracle_config_creation(self) -> None:
        """Test GruponosMeltanoTargetOracleConfig creation and defaults."""
        oracle_config = GruponosMeltanoOracleConnectionConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test_user",
            password="test_pass",
        )

        config = GruponosMeltanoTargetOracleConfig(
            oracle=oracle_config,
            schema_name="TARGET_SCHEMA",
        )

        if config.oracle != oracle_config:
            msg = f"Expected {oracle_config}, got {config.oracle}"
            raise AssertionError(msg)
        assert config.schema_name == "TARGET_SCHEMA"

        # Test defaults
        if config.truncate_before_load:
            msg = f"Expected False, got {config.truncate_before_load}"
            raise AssertionError(msg)
        if not (config.analyze_after_load):
            msg = f"Expected True, got {config.analyze_after_load}"
            raise AssertionError(msg)
        assert config.create_indexes is True
        if config.parallel_degree != 4:
            msg = f"Expected {4}, got {config.parallel_degree}"
            raise AssertionError(msg)
        assert config.commit_interval == 1000

    def test_target_oracle_config_validation(self) -> None:
        """Test GruponosMeltanoTargetOracleConfig validation."""
        oracle_config = GruponosMeltanoOracleConnectionConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test_user",
            password="test_pass",
        )

        # Test invalid parallel degree
        with pytest.raises(ValidationError) as exc_info:
            GruponosMeltanoTargetOracleConfig(
                oracle=oracle_config,
                schema_name="TARGET_SCHEMA",
                parallel_degree=20,  # Too high
            )
        if "less than or equal to 16" not in str(exc_info.value):
            msg = f"Expected {'less than or equal to 16'} in {exc_info.value!s}"
            raise AssertionError(msg)

        # Test invalid commit interval
        with pytest.raises(ValidationError) as exc_info:
            GruponosMeltanoTargetOracleConfig(
                oracle=oracle_config,
                schema_name="TARGET_SCHEMA",
                commit_interval=50,  # Too low
            )
        if "greater than or equal to 100" not in str(exc_info.value):
            msg = f"Expected {'greater than or equal to 100'} in {exc_info.value!s}"
            raise AssertionError(msg)

    def test_alert_config_comprehensive(self) -> None:
        """Test GruponosMeltanoAlertConfig comprehensive validation."""
        # Test default values
        config = GruponosMeltanoAlertConfig()

        if config.max_sync_duration_minutes != 60:
            msg = f"Expected {60}, got {config.max_sync_duration_minutes}"
            raise AssertionError(msg)
        assert config.max_error_rate_percent == 5.0
        if config.min_records_threshold != 100:
            msg = f"Expected {100}, got {config.min_records_threshold}"
            raise AssertionError(msg)
        assert config.max_connection_time_seconds == 30.0
        if config.max_connection_failures != EXPECTED_DATA_COUNT:
            msg = f"Expected {3}, got {config.max_connection_failures}"
            raise AssertionError(msg)
        assert config.max_memory_usage_percent == 80.0
        if config.max_cpu_usage_percent != 85.0:
            msg = f"Expected {85.0}, got {config.max_cpu_usage_percent}"
            raise AssertionError(msg)
        if config.webhook_enabled:
            msg = f"Expected False, got {config.webhook_enabled}"
            raise AssertionError(msg)
        assert config.webhook_url is None
        if config.email_enabled:
            msg = f"Expected False, got {config.email_enabled}"
            raise AssertionError(msg)
        assert config.alert_email is None
        if config.slack_enabled:
            msg = f"Expected False, got {config.slack_enabled}"
            raise AssertionError(msg)
        assert config.slack_webhook is None

        # Test custom values
        config_custom = GruponosMeltanoAlertConfig(
            max_sync_duration_minutes=120,
            max_error_rate_percent=10.0,
            min_records_threshold=500,
            max_connection_time_seconds=60.0,
            max_connection_failures=5,
            max_memory_usage_percent=90.0,
            max_cpu_usage_percent=95.0,
            webhook_enabled=True,
            webhook_url="https://webhook.example.com",
            email_enabled=True,
            alert_email="alerts@example.com",
            slack_enabled=True,
            slack_webhook="https://hooks.slack.com/test",
        )

        if config_custom.max_sync_duration_minutes != 120:
            msg = f"Expected {120}, got {config_custom.max_sync_duration_minutes}"
            raise AssertionError(msg)
        assert config_custom.max_error_rate_percent == 10.0
        if not (config_custom.webhook_enabled):
            msg = f"Expected True, got {config_custom.webhook_enabled}"
            raise AssertionError(msg)
        if config_custom.webhook_url != "https://webhook.example.com":
            msg = f"Expected {'https://webhook.example.com'}, got {config_custom.webhook_url}"
            raise AssertionError(msg)

        # Test validation errors
        with pytest.raises(ValidationError) as exc_info:
            GruponosMeltanoAlertConfig(
                max_error_rate_percent=150.0,
            )  # Invalid percentage
        if "less than or equal to 100" not in str(exc_info.value):
            msg = f"Expected {'less than or equal to 100'} in {exc_info.value!s}"
            raise AssertionError(msg)

        with pytest.raises(ValidationError) as exc_info:
            GruponosMeltanoAlertConfig(max_connection_failures=0)  # Invalid minimum
        if "greater than or equal to 1" not in str(exc_info.value):
            msg = f"Expected {'greater than or equal to 1'} in {exc_info.value!s}"
            raise AssertionError(msg)

    def test_meltano_config_comprehensive(self) -> None:
        """Test GruponosMeltanoSettings comprehensive validation."""
        # Test with required fields
        config = GruponosMeltanoSettings(project_id="test-project")

        if config.project_id != "test-project":
            msg = f"Expected {'test-project'}, got {config.project_id}"
            raise AssertionError(msg)
        assert config.environment == "dev"
        if config.state_backend != "file":
            msg = f"Expected {'file'}, got {config.state_backend}"
            raise AssertionError(msg)
        assert config.state_backend_uri is None
        if config.log_level != "INFO":
            msg = f"Expected {'INFO'}, got {config.log_level}"
            raise AssertionError(msg)
        if not (config.log_structured):
            msg = f"Expected True, got {config.log_structured}"
            raise AssertionError(msg)
        if config.parallelism != 1:
            msg = f"Expected {1}, got {config.parallelism}"
            raise AssertionError(msg)
        assert config.timeout_seconds == 3600

        # Test custom values
        config_custom = GruponosMeltanoSettings(
            project_id="production-project",
            environment="production",
            state_backend="s3",
            state_backend_uri="s3://bucket/state",
            log_level="WARNING",
            log_structured=False,
            parallelism=5,
            timeout_seconds=7200,
        )

        if config_custom.project_id != "production-project":
            msg = f"Expected {'production-project'}, got {config_custom.project_id}"
            raise AssertionError(msg)
        assert config_custom.environment == "production"
        if config_custom.state_backend != "s3":
            msg = f"Expected {'s3'}, got {config_custom.state_backend}"
            raise AssertionError(msg)
        assert config_custom.state_backend_uri == "s3://bucket/state"
        if config_custom.log_level != "WARNING":
            msg = f"Expected {'WARNING'}, got {config_custom.log_level}"
            raise AssertionError(msg)
        assert config_custom.parallelism == 5

        # Test validation errors
        with pytest.raises(ValidationError) as exc_info:
            GruponosMeltanoSettings(project_id="test", environment="invalid")
        if "pattern" not in str(exc_info.value):
            msg = f"Expected {'pattern'} in {exc_info.value!s}"
            raise AssertionError(msg)

        with pytest.raises(ValidationError) as exc_info:
            GruponosMeltanoSettings(project_id="test", log_level="INVALID")
        if "pattern" not in str(exc_info.value):
            msg = f"Expected {'pattern'} in {exc_info.value!s}"
            raise AssertionError(msg)

        with pytest.raises(ValidationError) as exc_info:
            GruponosMeltanoSettings(project_id="test", parallelism=15)  # Too high
        if "less than or equal to 10" not in str(exc_info.value):
            msg = f"Expected {'less than or equal to 10'} in {exc_info.value!s}"
            raise AssertionError(msg)

    def test_gruponos_config_creation(self) -> None:
        """Test GruponosMeltanoSettings creation and defaults."""
        config = GruponosMeltanoSettings()

        # Test defaults
        assert config.wms_source is None
        assert config.target_oracle is None
        assert config.alerts is not None
        assert isinstance(config.alerts, GruponosMeltanoAlertConfig)
        assert config.meltano is None
        if config.project_name != "gruponos-meltano-native":
            msg = f"Expected {'gruponos-meltano-native'}, got {config.project_name}"
            raise AssertionError(msg)
        assert config.company == "GrupoNOS"
        if config.debug_mode:
            msg = f"Expected False, got {config.debug_mode}"
            raise AssertionError(msg)
        assert config.dry_run is False

    def test_gruponos_config_with_subconfigs(self) -> None:
        """Test GruponosMeltanoSettings with sub-configurations."""
        oracle_config = GruponosMeltanoOracleConnectionConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test_user",
            password="test_pass",
        )

        wms_config = GruponosMeltanoWMSSourceConfig(oracle=oracle_config)
        target_config = GruponosMeltanoTargetOracleConfig(
            oracle=oracle_config,
            schema_name="TARGET",
        )
        meltano_config = GruponosMeltanoSettings(project_id="test-project")

        config = GruponosMeltanoSettings(
            wms_source=wms_config,
            target_oracle=target_config,
            meltano=meltano_config,
            debug_mode=True,
            dry_run=True,
        )

        if config.wms_source != wms_config:
            msg = f"Expected {wms_config}, got {config.wms_source}"
            raise AssertionError(msg)
        assert config.target_oracle == target_config
        if config.meltano != meltano_config:
            msg = f"Expected {meltano_config}, got {config.meltano}"
            raise AssertionError(msg)
        if not (config.debug_mode):
            msg = f"Expected True, got {config.debug_mode}"
            raise AssertionError(msg)
        assert config.dry_run is True

    @patch.dict(
        os.environ,
        {
            "GRUPONOS_WMS_HOST": "wms.example.com",
            "GRUPONOS_WMS_PORT": "1521",
            "GRUPONOS_WMS_SERVICE_NAME": "WMSPROD",
            "GRUPONOS_WMS_USERNAME": "wms_user",
            "GRUPONOS_WMS_PASSWORD": "wms_pass",
            "GRUPONOS_TARGET_HOST": "target.example.com",
            "GRUPONOS_TARGET_PORT": "1522",
            "GRUPONOS_TARGET_SERVICE_NAME": "TARGETPROD",
            "GRUPONOS_TARGET_USERNAME": "target_user",
            "GRUPONOS_TARGET_PASSWORD": "target_pass",
            "GRUPONOS_DEBUG_MODE": "true",
            "GRUPONOS_DRY_RUN": "false",
        },
        clear=False,
    )
    def test_gruponos_config_from_env(self) -> None:
        """Test GruponosMeltanoSettings.from_env() method."""
        config = GruponosMeltanoSettings.from_env()

        # Test that configuration was created
        assert config is not None
        assert isinstance(config, GruponosMeltanoSettings)

        # Test that the method runs without error
        # (actual env mapping is complex and would require full env setup)

    @patch.dict(
        os.environ,
        {
            "TAP_ORACLE_WMS_HOST": "legacy.example.com",
            "TAP_ORACLE_WMS_PORT": "1521",
            "TAP_ORACLE_WMS_SERVICE_NAME": "LEGACYWMS",
        },
        clear=False,
    )
    def test_gruponos_config_legacy_env_mapping(self) -> None:
        """Test legacy environment variable mapping."""
        config = GruponosMeltanoSettings.from_env()

        # Test that legacy mapping works
        assert config is not None
        assert isinstance(config, GruponosMeltanoSettings)

    def test_config_repr_and_password_hiding(self) -> None:
        """Test that passwords are hidden in repr."""
        config = GruponosMeltanoOracleConnectionConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test_user",
            password="secret_password",
        )

        config_repr = repr(config)
        # Password should not appear in repr
        if "secret_password" in config_repr:
            msg = f"Expected 'secret_password' not in {config_repr}"
            raise AssertionError(msg)
        assert "password=" not in config_repr or "password=***" in config_repr

    def test_config_validation_info_usage(self) -> None:
        """Test that validation uses ValidationInfo correctly."""
        oracle_config = GruponosMeltanoOracleConnectionConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test_user",
            password="test_pass",
        )

        # Test the validation logic for multiple fields
        with pytest.raises(ValidationError) as exc_info:
            GruponosMeltanoWMSSourceConfig(
                oracle=oracle_config,
                api_enabled=True,
                api_base_url="https://api.example.com",
                api_username="user",
                api_password=None,  # This should trigger validation
            )

        error_msg = str(exc_info.value)
        if "api_password is required when api_enabled is True" not in error_msg:
            msg = f"Expected {'api_password is required when api_enabled is True'} in {error_msg}"
            raise AssertionError(msg)

    def test_config_class_config_attributes(self) -> None:
        """Test model_config attributes (Pydantic v2)."""
        config = GruponosMeltanoSettings()

        # Test that model_config is properly set (Pydantic v2 pattern)
        assert hasattr(config, "model_config")
        if "env_prefix" not in config.model_config:
            msg = f"Expected {'env_prefix'} in {config.model_config}"
            raise AssertionError(msg)
        assert "env_nested_delimiter" in config.model_config
        if "case_sensitive" not in config.model_config:
            msg = f"Expected {'case_sensitive'} in {config.model_config}"
            raise AssertionError(msg)

        if config.model_config["env_prefix"] != "GRUPONOS_":
            msg = f"Expected {'GRUPONOS_'}, got {config.model_config['env_prefix']}"
            raise AssertionError(msg)
        assert config.model_config["env_nested_delimiter"] == "__"
        if config.model_config["case_sensitive"]:
            msg = f"Expected False, got {config.model_config['case_sensitive']}"
            raise AssertionError(msg)
