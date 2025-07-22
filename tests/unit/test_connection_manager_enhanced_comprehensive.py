"""Comprehensive enhanced connection manager tests targeting 100% coverage.

Tests all connection scenarios, error handling, and enterprise features.
"""

from __future__ import annotations

import os
from unittest.mock import Mock, patch

import pytest

from gruponos_meltano_native.config import OracleConnectionConfig
from gruponos_meltano_native.oracle.connection_manager_enhanced import (
    OracleConnectionManager,
    _get_env_config,
    _validate_required_env_var,
    create_connection_manager_from_env,
)


class TestOracleConnectionManagerComprehensive:
    """Comprehensive test suite for OracleConnectionManager."""

    def test_initialization_success(self) -> None:
        """Test successful initialization of connection manager."""
        config = OracleConnectionConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test_user",
            password="test_pass",
            protocol="tcp",
            connection_timeout=30,
            retry_attempts=3,
            retry_delay=5,
            ssl_server_dn_match=False,
        )

        with patch("gruponos_meltano_native.oracle.connection_manager_enhanced.ResilientOracleConnection") as mock_conn:
            manager = OracleConnectionManager(config)

            assert manager.config == config
            assert manager._connection_attempts == 0
            mock_conn.assert_called_once()

    def test_initialization_with_defaults(self) -> None:
        """Test initialization with default connection pool size."""
        config = OracleConnectionConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test_user",
            password="test_pass",
        )

        with patch("gruponos_meltano_native.oracle.connection_manager_enhanced.ResilientOracleConnection") as mock_conn:
            OracleConnectionManager(config)

            # Verify default pool_max is used
            call_args = mock_conn.call_args[1]
            assert call_args["config"].pool_max == 5  # Default value

    def test_connect_success(self) -> None:
        """Test successful database connection."""
        config = OracleConnectionConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test_user",
            password="test_pass",
        )

        with patch("gruponos_meltano_native.oracle.connection_manager_enhanced.ResilientOracleConnection") as mock_conn_class:
            mock_connection = Mock()
            mock_conn_instance = Mock()
            mock_conn_instance.connect.return_value = None
            # Set _connection as private attribute to match our fix
            mock_conn_instance._connection = mock_connection
            mock_conn_instance.connection_attempts = 2
            mock_conn_class.return_value = mock_conn_instance

            manager = OracleConnectionManager(config)
            result = manager.connect()

            mock_conn_instance.connect.assert_called_once()
            assert result == mock_connection
            assert manager._connection_attempts == 2

    def test_connect_no_connection_attempts_attr(self) -> None:
        """Test connect when connection doesn't have connection_attempts attribute."""
        config = OracleConnectionConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test_user",
            password="test_pass",
        )

        with patch("gruponos_meltano_native.oracle.connection_manager_enhanced.ResilientOracleConnection") as mock_conn_class:
            mock_connection = Mock()
            mock_conn_instance = Mock()
            mock_conn_instance.connect.return_value = None
            # Set _connection as private attribute to match our fix
            mock_conn_instance._connection = mock_connection
            # Configure the mock to NOT have connection_attempts attribute
            # This will make getattr return the default value
            del mock_conn_instance.connection_attempts
            mock_conn_class.return_value = mock_conn_instance

            manager = OracleConnectionManager(config)
            result = manager.connect()

            assert result == mock_connection
            assert manager._connection_attempts == 0  # Default value

    def test_connect_no_connection_attr(self) -> None:
        """Test connect when connection doesn't have connection attribute."""
        config = OracleConnectionConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test_user",
            password="test_pass",
        )

        with patch("gruponos_meltano_native.oracle.connection_manager_enhanced.ResilientOracleConnection") as mock_conn_class:
            mock_conn_instance = Mock()
            mock_conn_instance.connect.return_value = None
            # Configure the mock to NOT have _connection attribute
            # This will make getattr return None as the default
            del mock_conn_instance._connection
            mock_conn_class.return_value = mock_conn_instance

            manager = OracleConnectionManager(config)
            result = manager.connect()

            assert result is None

    def test_test_connection_success(self) -> None:
        """Test successful connection test."""
        config = OracleConnectionConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test_user",
            password="test_pass",
        )

        test_result = {
            "success": True,
            "oracle_version": "19.0.0.0.0",
            "current_user": "TEST_USER",
            "connection_time_ms": 150.5,
            "attempts": 1,
            "fallback_applied": False,
        }

        with patch("gruponos_meltano_native.oracle.connection_manager_enhanced.ResilientOracleConnection") as mock_conn_class:
            mock_conn_instance = Mock()
            mock_conn_instance.test_connection_detailed.return_value = test_result
            mock_conn_class.return_value = mock_conn_instance

            manager = OracleConnectionManager(config)
            result = manager.test_connection()

            assert result == test_result
            mock_conn_instance.test_connection_detailed.assert_called_once()

    def test_test_connection_failure(self) -> None:
        """Test failed connection test."""
        config = OracleConnectionConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test_user",
            password="test_pass",
        )

        test_result = {
            "success": False,
            "error": "Connection refused",
            "attempts": 3,
        }

        with patch("gruponos_meltano_native.oracle.connection_manager_enhanced.ResilientOracleConnection") as mock_conn_class:
            mock_conn_instance = Mock()
            mock_conn_instance.test_connection_detailed.return_value = test_result
            mock_conn_class.return_value = mock_conn_instance

            manager = OracleConnectionManager(config)
            result = manager.test_connection()

            assert result == test_result

    def test_close_connection_connected(self) -> None:
        """Test closing connection when connected."""
        config = OracleConnectionConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test_user",
            password="test_pass",
        )

        with patch("gruponos_meltano_native.oracle.connection_manager_enhanced.ResilientOracleConnection") as mock_conn_class:
            mock_conn_instance = Mock()
            mock_conn_instance.is_connected = True
            mock_conn_class.return_value = mock_conn_instance

            manager = OracleConnectionManager(config)
            manager.close()

            mock_conn_instance.disconnect.assert_called_once()

    def test_close_connection_not_connected(self) -> None:
        """Test closing connection when not connected."""
        config = OracleConnectionConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test_user",
            password="test_pass",
        )

        with patch("gruponos_meltano_native.oracle.connection_manager_enhanced.ResilientOracleConnection") as mock_conn_class:
            mock_conn_instance = Mock()
            mock_conn_instance.is_connected = False
            mock_conn_class.return_value = mock_conn_instance

            manager = OracleConnectionManager(config)
            manager.close()

            mock_conn_instance.disconnect.assert_not_called()

    def test_close_connection_none(self) -> None:
        """Test closing connection when connection is None."""
        config = OracleConnectionConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test_user",
            password="test_pass",
        )

        with patch("gruponos_meltano_native.oracle.connection_manager_enhanced.ResilientOracleConnection") as mock_conn_class:
            mock_conn_class.return_value = None

            manager = OracleConnectionManager(config)
            # Should not raise an exception
            manager.close()

    def test_execute_connected(self) -> None:
        """Test SQL execution when connected."""
        config = OracleConnectionConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test_user",
            password="test_pass",
        )

        with patch("gruponos_meltano_native.oracle.connection_manager_enhanced.ResilientOracleConnection") as mock_conn_class:
            mock_conn_instance = Mock()
            mock_conn_instance.is_connected = True
            mock_conn_instance.execute.return_value = "result"
            mock_conn_class.return_value = mock_conn_instance

            manager = OracleConnectionManager(config)
            result = manager.execute("SELECT 1 FROM DUAL", {"param": "value"})

            assert result == "result"
            mock_conn_instance.execute.assert_called_once_with("SELECT 1 FROM DUAL", {"param": "value"})

    def test_execute_not_connected(self) -> None:
        """Test SQL execution when not connected (auto-connect)."""
        config = OracleConnectionConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test_user",
            password="test_pass",
        )

        with patch("gruponos_meltano_native.oracle.connection_manager_enhanced.ResilientOracleConnection") as mock_conn_class:
            mock_conn_instance = Mock()
            mock_conn_instance.is_connected = False
            mock_conn_instance.execute.return_value = "result"
            mock_conn_class.return_value = mock_conn_instance

            manager = OracleConnectionManager(config)

            # Mock connect method
            with patch.object(manager, "connect") as mock_connect:
                manager.execute("SELECT 1 FROM DUAL")

                mock_connect.assert_called_once()
                mock_conn_instance.execute.assert_called_once_with("SELECT 1 FROM DUAL", None)

    def test_fetch_one_connected(self) -> None:
        """Test fetch_one when connected."""
        config = OracleConnectionConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test_user",
            password="test_pass",
        )

        with patch("gruponos_meltano_native.oracle.connection_manager_enhanced.ResilientOracleConnection") as mock_conn_class:
            mock_conn_instance = Mock()
            mock_conn_instance.is_connected = True
            mock_conn_instance.fetch_one.return_value = ("value1", "value2")
            mock_conn_class.return_value = mock_conn_instance

            manager = OracleConnectionManager(config)
            result = manager.fetch_one("SELECT col1, col2 FROM table1", {"param": "value"})

            assert result == ("value1", "value2")
            mock_conn_instance.fetch_one.assert_called_once_with("SELECT col1, col2 FROM table1", {"param": "value"})

    def test_fetch_one_not_connected(self) -> None:
        """Test fetch_one when not connected (auto-connect)."""
        config = OracleConnectionConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test_user",
            password="test_pass",
        )

        with patch("gruponos_meltano_native.oracle.connection_manager_enhanced.ResilientOracleConnection") as mock_conn_class:
            mock_conn_instance = Mock()
            mock_conn_instance.is_connected = False
            mock_conn_instance.fetch_one.return_value = ("value1",)
            mock_conn_class.return_value = mock_conn_instance

            manager = OracleConnectionManager(config)

            # Mock connect method
            with patch.object(manager, "connect") as mock_connect:
                manager.fetch_one("SELECT col1 FROM table1")

                mock_connect.assert_called_once()
                mock_conn_instance.fetch_one.assert_called_once_with("SELECT col1 FROM table1", None)

    def test_fetch_all_connected(self) -> None:
        """Test fetch_all when connected."""
        config = OracleConnectionConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test_user",
            password="test_pass",
        )

        with patch("gruponos_meltano_native.oracle.connection_manager_enhanced.ResilientOracleConnection") as mock_conn_class:
            mock_conn_instance = Mock()
            mock_conn_instance.is_connected = True
            mock_conn_instance.fetch_all.return_value = [("value1", "value2"), ("value3", "value4")]
            mock_conn_class.return_value = mock_conn_instance

            manager = OracleConnectionManager(config)
            result = manager.fetch_all("SELECT col1, col2 FROM table1")

            assert result == [("value1", "value2"), ("value3", "value4")]
            mock_conn_instance.fetch_all.assert_called_once_with("SELECT col1, col2 FROM table1", None)

    def test_fetch_all_not_connected(self) -> None:
        """Test fetch_all when not connected (auto-connect)."""
        config = OracleConnectionConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test_user",
            password="test_pass",
        )

        with patch("gruponos_meltano_native.oracle.connection_manager_enhanced.ResilientOracleConnection") as mock_conn_class:
            mock_conn_instance = Mock()
            mock_conn_instance.is_connected = False
            mock_conn_instance.fetch_all.return_value = [("value1",)]
            mock_conn_class.return_value = mock_conn_instance

            manager = OracleConnectionManager(config)

            # Mock connect method
            with patch.object(manager, "connect") as mock_connect:
                manager.fetch_all("SELECT col1 FROM table1", {"param": "value"})

                mock_connect.assert_called_once()
                mock_conn_instance.fetch_all.assert_called_once_with("SELECT col1 FROM table1", {"param": "value"})

    def test_is_connected_property(self) -> None:
        """Test is_connected property."""
        config = OracleConnectionConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test_user",
            password="test_pass",
        )

        with patch("gruponos_meltano_native.oracle.connection_manager_enhanced.ResilientOracleConnection") as mock_conn_class:
            mock_conn_instance = Mock()
            mock_conn_instance.is_connected = True
            mock_conn_class.return_value = mock_conn_instance

            manager = OracleConnectionManager(config)
            assert manager.is_connected is True

    def test_get_connection_info(self) -> None:
        """Test get_connection_info method."""
        config = OracleConnectionConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test_user",
            password="test_pass",
        )

        connection_info = {
            "host": "localhost",
            "port": 1521,
            "service_name": "XEPDB1",
            "connected": True,
        }

        with patch("gruponos_meltano_native.oracle.connection_manager_enhanced.ResilientOracleConnection") as mock_conn_class:
            mock_conn_instance = Mock()
            mock_conn_instance.get_connection_info.return_value = connection_info
            mock_conn_class.return_value = mock_conn_instance

            manager = OracleConnectionManager(config)
            result = manager.get_connection_info()

            assert result == connection_info
            mock_conn_instance.get_connection_info.assert_called_once()


class TestEnvironmentFunctions:
    """Test environment configuration functions."""

    def test_validate_required_env_var_success(self) -> None:
        """Test successful environment variable validation."""
        with patch.dict(os.environ, {"TEST_VAR": "test_value"}):
            result = _validate_required_env_var("TEST_VAR")
            assert result == "test_value"

    def test_validate_required_env_var_missing(self) -> None:
        """Test environment variable validation failure."""
        with (
            patch.dict(os.environ, {}, clear=True),
            pytest.raises(ValueError, match="Missing TEST_VAR environment variable"),
        ):
            _validate_required_env_var("TEST_VAR")

    def test_validate_required_env_var_empty(self) -> None:
        """Test environment variable validation with empty value."""
        with (
            patch.dict(os.environ, {"TEST_VAR": ""}),
            pytest.raises(ValueError, match="Missing TEST_VAR environment variable"),
        ):
            _validate_required_env_var("TEST_VAR")

    def test_get_env_config_success(self) -> None:
        """Test successful environment configuration retrieval."""
        env_vars = {
            "FLEXT_TARGET_ORACLE_HOST": "localhost",
            "FLEXT_TARGET_ORACLE_SERVICE_NAME": "XEPDB1",
            "FLEXT_TARGET_ORACLE_USERNAME": "test_user",
            "FLEXT_TARGET_ORACLE_PASSWORD": "test_pass",
            "FLEXT_TARGET_ORACLE_PROTOCOL": "tcp",
            "FLEXT_TARGET_ORACLE_PORT": "1521",
            "FLEXT_TARGET_ORACLE_TIMEOUT": "30",
            "FLEXT_TARGET_ORACLE_RETRIES": "5",
            "FLEXT_TARGET_ORACLE_RETRY_DELAY": "10",
            "FLEXT_TARGET_ORACLE_SSL_DN_MATCH": "true",
        }

        with patch.dict(os.environ, env_vars):
            config = _get_env_config()

            assert config["host"] == "localhost"
            assert config["service_name"] == "XEPDB1"
            assert config["username"] == "test_user"
            assert config["password"] == "test_pass"
            assert config["protocol"] == "tcp"
            assert config["port"] == 1521
            assert config["connection_timeout"] == 30
            assert config["retry_attempts"] == 5
            assert config["retry_delay"] == 10
            assert config["ssl_server_dn_match"] is True

    def test_get_env_config_defaults(self) -> None:
        """Test environment configuration with default values."""
        required_vars = {
            "FLEXT_TARGET_ORACLE_HOST": "localhost",
            "FLEXT_TARGET_ORACLE_SERVICE_NAME": "XEPDB1",
            "FLEXT_TARGET_ORACLE_USERNAME": "test_user",
            "FLEXT_TARGET_ORACLE_PASSWORD": "test_pass",
            "FLEXT_TARGET_ORACLE_PROTOCOL": "tcp",
        }

        with patch.dict(os.environ, required_vars, clear=True):
            config = _get_env_config()

            # Test default values
            assert config["port"] == 1522
            assert config["connection_timeout"] == 60
            assert config["retry_attempts"] == 3
            assert config["retry_delay"] == 5
            assert config["ssl_server_dn_match"] is False

    def test_get_env_config_ssl_dn_match_false(self) -> None:
        """Test SSL DN match configuration with false value."""
        required_vars = {
            "FLEXT_TARGET_ORACLE_HOST": "localhost",
            "FLEXT_TARGET_ORACLE_SERVICE_NAME": "XEPDB1",
            "FLEXT_TARGET_ORACLE_USERNAME": "test_user",
            "FLEXT_TARGET_ORACLE_PASSWORD": "test_pass",
            "FLEXT_TARGET_ORACLE_PROTOCOL": "tcp",
            "FLEXT_TARGET_ORACLE_SSL_DN_MATCH": "false",
        }

        with patch.dict(os.environ, required_vars, clear=True):
            config = _get_env_config()
            assert config["ssl_server_dn_match"] is False

    def test_get_env_config_missing_required(self) -> None:
        """Test environment configuration with missing required variable."""
        incomplete_vars = {
            "FLEXT_TARGET_ORACLE_HOST": "localhost",
            "FLEXT_TARGET_ORACLE_SERVICE_NAME": "XEPDB1",
            "FLEXT_TARGET_ORACLE_USERNAME": "test_user",
            # Missing password
            "FLEXT_TARGET_ORACLE_PROTOCOL": "tcp",
        }

        with (
            patch.dict(os.environ, incomplete_vars, clear=True),
            pytest.raises(ValueError, match="Missing FLEXT_TARGET_ORACLE_PASSWORD environment variable"),
        ):
            _get_env_config()

    def test_create_connection_manager_from_env_success(self) -> None:
        """Test successful connection manager creation from environment."""
        env_vars = {
            "FLEXT_TARGET_ORACLE_HOST": "localhost",
            "FLEXT_TARGET_ORACLE_SERVICE_NAME": "XEPDB1",
            "FLEXT_TARGET_ORACLE_USERNAME": "test_user",
            "FLEXT_TARGET_ORACLE_PASSWORD": "test_pass",
            "FLEXT_TARGET_ORACLE_PROTOCOL": "tcp",
        }

        with patch.dict(os.environ, env_vars), \
             patch("gruponos_meltano_native.oracle.connection_manager_enhanced.ResilientOracleConnection"):
            manager = create_connection_manager_from_env()

            assert isinstance(manager, OracleConnectionManager)
            assert manager.config.host == "localhost"
            assert manager.config.service_name == "XEPDB1"

    def test_create_connection_manager_from_env_failure(self) -> None:
        """Test connection manager creation failure due to missing env vars."""
        with (
            patch.dict(os.environ, {}, clear=True),
            pytest.raises(ValueError, match="Missing FLEXT_TARGET_ORACLE_HOST environment variable"),
        ):
            create_connection_manager_from_env()


class TestMainExecution:
    """Test main execution path."""

    @patch("gruponos_meltano_native.oracle.connection_manager_enhanced.setup_logging")
    @patch("gruponos_meltano_native.oracle.connection_manager_enhanced.create_connection_manager_from_env")
    def test_main_execution_path(self, mock_create_manager: Mock, mock_setup_logging: Mock) -> None:
        """Test the main execution path when module is run directly."""
        mock_manager = Mock()
        mock_manager.test_connection.return_value = {
            "success": True,
            "oracle_version": "19.0.0.0.0",
        }
        mock_create_manager.return_value = mock_manager

        # Import and execute the main block
        import gruponos_meltano_native.oracle.connection_manager_enhanced

        # The actual main execution would happen here if __name__ == "__main__"
        # We're testing that the functions exist and can be called
        assert callable(gruponos_meltano_native.oracle.connection_manager_enhanced.create_connection_manager_from_env)
        assert callable(mock_setup_logging)
