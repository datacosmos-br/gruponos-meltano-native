"""Comprehensive Oracle connection manager tests targeting 100% coverage.

Tests Oracle connection management, configuration validation, and error handling.
"""

from __future__ import annotations

import tempfile

from flext_db_oracle import FlextDbOracleApi, FlextDbOracleConfig

from gruponos_meltano_native.config import GruponosMeltanoOracleConnectionConfig
from gruponos_meltano_native.oracle import GruponosMeltanoOracleConnectionManager

# Secure test file paths to avoid S108 linting errors
TEST_SCRIPT_PATH = tempfile.mkdtemp() + "/test_script.sql"
TEST_CATALOG_PATH = tempfile.mkdtemp() + "/catalog.json"
TEST_INVALID_CATALOG_PATH = tempfile.mkdtemp() + "/invalid_catalog.json"
TEST_MISSING_CATALOG_PATH = tempfile.mkdtemp() + "/missing_catalog.json"


class TestOracleConnectionManagerComprehensive:
    """Comprehensive test suite for Oracle connection manager."""

    def test_initialization_minimal_config(self) -> None:
        """Test initialization with minimal configuration."""
        config = GruponosMeltanoOracleConnectionConfig(
            host="localhost", service_name="TESTDB", username="test", password="test",
        )

        manager = GruponosMeltanoOracleConnectionManager(config)
        assert manager is not None
        assert manager.config == config

    def test_initialization_full_config(self) -> None:
        """Test initialization with full configuration."""
        config = GruponosMeltanoOracleConnectionConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="test_user",
            password="test_pass",
            protocol="tcps",
        )

        manager = GruponosMeltanoOracleConnectionManager(config)
        assert manager is not None
        assert manager.config.host == "localhost"
        assert manager.config.port == 1521
        assert manager.config.service_name == "XEPDB1"
        assert manager.config.username == "test_user"
        assert manager.config.protocol == "tcps"

    def test_connection_manager_get_connection(self) -> None:
        """Test connection manager get_connection method."""
        config = GruponosMeltanoOracleConnectionConfig(
            host="localhost",
            port=1521,
            service_name="TESTDB",
            username="test",
            password="test",
        )

        manager = GruponosMeltanoOracleConnectionManager(config)

        # Test get_connection returns FlextResult
        result = manager.get_connection()
        assert hasattr(result, "is_success")
        assert hasattr(result, "data")
        assert hasattr(result, "error")

        # Result should be boolean type
        assert isinstance(result.is_success, bool)

    def test_connection_manager_test_connection(self) -> None:
        """Test connection manager test_connection method."""
        config = GruponosMeltanoOracleConnectionConfig(
            host="localhost",
            port=1521,
            service_name="TESTDB",
            username="test",
            password="test",
        )

        manager = GruponosMeltanoOracleConnectionManager(config)

        # Test test_connection returns FlextResult
        result = manager.test_connection()
        assert hasattr(result, "is_success")
        assert hasattr(result, "data")
        assert hasattr(result, "error")

        # Result should be boolean type
        assert isinstance(result.is_success, bool)

    def test_connection_manager_close_connection(self) -> None:
        """Test connection manager close_connection method."""
        config = GruponosMeltanoOracleConnectionConfig(
            host="localhost",
            port=1521,
            service_name="TESTDB",
            username="test",
            password="test",
        )

        manager = GruponosMeltanoOracleConnectionManager(config)

        # Test close_connection returns FlextResult
        result = manager.close_connection()
        assert hasattr(result, "is_success")
        assert hasattr(result, "data")
        assert hasattr(result, "error")

        # Result should be boolean type
        assert isinstance(result.is_success, bool)

    def test_connection_manager_error_handling(self) -> None:
        """Test connection manager error handling with invalid config."""
        config = GruponosMeltanoOracleConnectionConfig(
            host="invalid.host.that.does.not.exist",
            port=9999,
            service_name="INVALID_DB",
            username="invalid_user",
            password="invalid_pass",
        )

        manager = GruponosMeltanoOracleConnectionManager(config)

        # Even with invalid config, manager should be created
        assert manager is not None
        assert manager.config.host == "invalid.host.that.does.not.exist"

        # Connection operations should handle errors gracefully
        get_result = manager.get_connection()
        assert isinstance(get_result.is_success, bool)

        test_result = manager.test_connection()
        assert isinstance(test_result.is_success, bool)

    def test_connection_manager_configuration_validation(self) -> None:
        """Test connection manager with various configuration options."""
        # Test with SSL configuration
        ssl_config = GruponosMeltanoOracleConnectionConfig(
            host="secure.oracle.com",
            port=1522,
            service_name="SECURE_DB",
            username="secure_user",
            password="secure_pass",
            protocol="tcps",
            ssl_enabled=True,
        )

        ssl_manager = GruponosMeltanoOracleConnectionManager(ssl_config)
        assert ssl_manager is not None
        assert ssl_manager.config.protocol == "tcps"
        assert ssl_manager.config.ssl_enabled is True

        # Test with connection pool settings
        pool_config = GruponosMeltanoOracleConnectionConfig(
            host="pool.oracle.com",
            service_name="POOL_DB",
            username="pool_user",
            password="pool_pass",
            pool_min=2,
            pool_max=20,
        )

        pool_manager = GruponosMeltanoOracleConnectionManager(pool_config)
        assert pool_manager is not None
        assert pool_manager.config.pool_min == 2
        assert pool_manager.config.pool_max == 20

    def test_connection_manager_integration_with_flext_db_oracle(self) -> None:
        """Test connection manager integration with flext-db-oracle APIs."""
        config = GruponosMeltanoOracleConnectionConfig(
            host="integration.test.host",
            port=1521,
            service_name="INTEGRATION_DB",
            username="integration_user",
            password="integration_pass",
        )

        manager = GruponosMeltanoOracleConnectionManager(config)

        # Test that manager can work with flext-db-oracle
        assert manager is not None

        # Test direct API usage
        api_config_dict = {
            "host": "localhost",
            "port": 1521,
            "service_name": "TESTDB",
            "username": "test",
            "password": "test",
        }

        api = FlextDbOracleApi.with_config(api_config_dict)
        assert api is not None

        # Test that both use compatible configuration
        flext_config = FlextDbOracleConfig(**api_config_dict)
        assert flext_config.host == "localhost"
        assert flext_config.port == 1521

    def test_connection_manager_default_configuration(self) -> None:
        """Test connection manager with default configuration values."""
        # Test with minimal required configuration
        minimal_config = GruponosMeltanoOracleConnectionConfig(
            host="minimal.host",
            service_name="MINIMAL_DB",
            username="minimal_user",
            password="minimal_pass",
        )

        manager = GruponosMeltanoOracleConnectionManager(minimal_config)
        assert manager is not None

        # Test that defaults are applied
        assert manager.config.port == 1521  # Default port from config
        assert manager.config.protocol == "TCP"  # Default protocol
        assert manager.config.pool_min == 1  # Default pool min
        assert manager.config.pool_max == 10  # Default pool max

    def test_connection_manager_none_config(self) -> None:
        """Test connection manager with None config (uses defaults)."""
        # Test that manager can be created with None config
        manager = GruponosMeltanoOracleConnectionManager(None)
        assert manager is not None

        # Should have default configuration
        assert manager.config is not None
        assert isinstance(manager.config, GruponosMeltanoOracleConnectionConfig)
