"""End-to-end integration tests for Oracle functionality.

These tests require real Oracle database connections and test complete workflows.
"""

from __future__ import annotations

import os

import pytest
from dotenv import load_dotenv

from gruponos_meltano_native.config import (
    GruponosMeltanoOracleConnectionConfig,
    GruponosMeltanoSettings,
)
from gruponos_meltano_native.oracle.connection_manager_enhanced import (
    GruponosMeltanoOracleConnectionManager,
)

# Load environment variables from .env file for integration tests
load_dotenv()


class TestOracleConnectionIntegration:
    """Test real Oracle database connections and operations."""

    @pytest.fixture
    def oracle_config(self) -> GruponosMeltanoOracleConnectionConfig:
        """Create Oracle configuration from environment variables."""
        required_vars = [
            "FLEXT_TARGET_ORACLE_HOST",
            "FLEXT_TARGET_ORACLE_SERVICE_NAME",
            "FLEXT_TARGET_ORACLE_USERNAME",
            "FLEXT_TARGET_ORACLE_PASSWORD",
        ]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            pytest.skip(f"Missing required environment variables: {missing_vars}")

        return GruponosMeltanoOracleConnectionConfig(
            host=os.environ["FLEXT_TARGET_ORACLE_HOST"],
            service_name=os.environ["FLEXT_TARGET_ORACLE_SERVICE_NAME"],
            username=os.environ["FLEXT_TARGET_ORACLE_USERNAME"],
            password=os.environ["FLEXT_TARGET_ORACLE_PASSWORD"],
            port=int(os.getenv("FLEXT_TARGET_ORACLE_PORT", "1522")),
            protocol=os.getenv("FLEXT_TARGET_ORACLE_PROTOCOL", "tcps"),
        )

    @pytest.fixture
    def connection_manager(
        self, oracle_config: GruponosMeltanoOracleConnectionConfig,
    ) -> GruponosMeltanoOracleConnectionManager:
        """Create connection manager with real Oracle config."""
        return GruponosMeltanoOracleConnectionManager(oracle_config)

    @pytest.mark.integration
    @pytest.mark.slow
    def test_oracle_connection_test(
        self,
        connection_manager: GruponosMeltanoOracleConnectionManager,
    ) -> None:
        """Test Oracle connection establishment."""
        # Test connection
        result = connection_manager.test_connection()
        assert result.is_success, f"Connection test failed: {result.error}"

        # Validate result data
        assert result.data is not None
        assert result.data["success"] is True
        assert "oracle_version" in result.data

    @pytest.mark.integration
    @pytest.mark.slow
    def test_oracle_query_execution(
        self,
        connection_manager: GruponosMeltanoOracleConnectionManager,
    ) -> None:
        """Test Oracle query execution."""
        # Test simple query
        result = connection_manager.execute_query("SELECT 1 as test_col FROM DUAL")
        assert result.is_success, f"Query execution failed: {result.error}"

        # Validate result structure
        assert result.data is not None
        assert len(result.data) == 1
        assert "test_col" in result.data[0]
        assert result.data[0]["test_col"] == 1

    @pytest.mark.integration
    @pytest.mark.slow
    def test_oracle_command_execution(
        self,
        connection_manager: GruponosMeltanoOracleConnectionManager,
    ) -> None:
        """Test Oracle command execution."""
        # Create a test table
        create_result = connection_manager.execute_command(
            """
            CREATE TABLE test_flext_table (
                id NUMBER PRIMARY KEY,
                test_data VARCHAR2(100)
            )
            """,
        )
        assert create_result.is_success, f"Table creation failed: {create_result.error}"

        try:
            # Insert test data
            insert_result = connection_manager.execute_command(
                "INSERT INTO test_flext_table VALUES (1, 'test')",
            )
            assert insert_result.is_success, f"Insert failed: {insert_result.error}"
            assert insert_result.data == 1  # 1 row affected

            # Query the data back
            query_result = connection_manager.execute_query(
                "SELECT * FROM test_flext_table WHERE id = 1",
            )
            assert query_result.is_success, f"Query failed: {query_result.error}"
            assert len(query_result.data) == 1
            assert query_result.data[0]["TEST_DATA"] == "test"

        finally:
            # Clean up - drop test table
            drop_result = connection_manager.execute_command(
                "DROP TABLE test_flext_table",
            )
            assert drop_result.is_success, f"Table cleanup failed: {drop_result.error}"

    @pytest.mark.integration
    @pytest.mark.slow
    def test_connection_validation(
        self,
        connection_manager: GruponosMeltanoOracleConnectionManager,
    ) -> None:
        """Test connection configuration validation."""
        result = connection_manager.validate_configuration()
        assert result.is_success, f"Configuration validation failed: {result.error}"

    @pytest.mark.integration
    @pytest.mark.slow
    def test_connection_manager_lifecycle(
        self,
        connection_manager: GruponosMeltanoOracleConnectionManager,
    ) -> None:
        """Test full connection manager lifecycle."""
        # Connect
        connect_result = connection_manager.connect()
        assert connect_result.is_success, f"Connection failed: {connect_result.error}"

        # Check connection status
        assert connection_manager.is_connected()

        # Get connection info
        info = connection_manager.get_connection_info()
        assert info["is_connected"] is True
        assert info["host"] == connection_manager.config.host

        # Disconnect
        disconnect_result = connection_manager.disconnect()
        assert disconnect_result.is_success, f"Disconnection failed: {disconnect_result.error}"

        # Verify disconnection
        assert not connection_manager.is_connected()


class TestSettingsIntegration:
    """Test configuration settings integration."""

    def test_settings_creation(self) -> None:
        """Test GruponosMeltanoSettings creation and validation."""
        settings = GruponosMeltanoSettings()

        # Basic validation
        assert settings.app_name == "gruponos-meltano-native"
        assert settings.version == "0.7.0"
        assert hasattr(settings, "oracle")
        assert hasattr(settings, "meltano_project_root")

    def test_oracle_config_validation(self) -> None:
        """Test Oracle configuration validation."""
        config = GruponosMeltanoOracleConnectionConfig(
            host="test.oracle.com",
            service_name="TESTDB",
            username="testuser",
            password="testpass",
        )

        # Should not raise exception
        config.validate_domain_rules()

        # Test connection string generation
        conn_str = config.get_connection_string()
        assert conn_str == "testuser/testpass@test.oracle.com:1522/TESTDB"
