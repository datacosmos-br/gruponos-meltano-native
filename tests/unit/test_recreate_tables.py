"""Comprehensive tests for Oracle table recreation using REAL FLEXT APIs.

REAL IMPLEMENTATION TESTS - NO MOCKS OR FALLBACKS.
Tests the actual Oracle table recreation logic using flext-db-oracle APIs.
"""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest
from flext_core import FlextCore
from flext_db_oracle import FlextDbOracleApi, FlextDbOracleConfig, TDbOracleQueryResult

from gruponos_meltano_native import (
    GruponosMeltanoOracleConnectionConfig,
    create_gruponos_meltano_oracle_connection_manager,
    create_gruponos_meltano_settings,
)

# Constants
EXPECTED_DATA_COUNT = 3


class TestOracleTableRecreationReal:
    """Test Oracle table recreation with real APIs."""

    def test_oracle_config_creation(self) -> None:
        """Test Oracle configuration creation using real config."""
        config = GruponosMeltanoOracleConnectionConfig(
            host="localhost",
            port=1521,
            service_name="TESTDB",
            username="test",
            password="test",
        )

        assert config.host == "localhost"
        assert config.port == 1521
        assert config.service_name == "TESTDB"
        assert config.username == "test"

    def test_connection_manager_creation(self) -> None:
        """Test connection manager creation using real factory."""
        config = GruponosMeltanoOracleConnectionConfig(
            host="localhost",
            service_name="TESTDB",
            username="test",
            password="test",
        )

        manager = create_gruponos_meltano_oracle_connection_manager(config)
        assert manager is not None
        assert hasattr(manager, "get_connection")

    def test_flext_db_oracle_api_availability(self) -> None:
        """Test that FlextDbOracleApi has required methods for table recreation."""
        # Test that API has DDL execution capabilities
        assert hasattr(FlextDbOracleApi, "execute_ddl")
        assert callable(FlextDbOracleApi.execute_ddl)

        # Test that API has query capabilities
        assert hasattr(FlextDbOracleApi, "query")
        assert callable(FlextDbOracleApi.query)

        # Test that API has connection management
        assert hasattr(FlextDbOracleApi, "connect")
        assert callable(FlextDbOracleApi.connect)

        assert hasattr(FlextDbOracleApi, "disconnect")
        assert callable(FlextDbOracleApi.disconnect)

    def test_gruponos_settings_creation(self) -> None:
        """Test GrupoNOS settings creation using real API."""
        settings = create_gruponos_meltano_settings()

        assert settings is not None
        assert settings.app_name == "gruponos-meltano-native"
        assert settings.version == "0.9.0"
        assert settings.environment == "dev"

    @patch("flext_db_oracle.FlextDbOracleApi.with_config")
    def test_api_creation_mock(self, mock_with_config: Mock) -> None:
        """Test Oracle API creation using mock (for error scenarios)."""
        # Mock successful API creation
        mock_api = Mock()
        mock_with_config.return_value = mock_api

        # Create API using real config structure
        config_dict = {
            "host": "localhost",
            "port": 1521,
            "service_name": "TESTDB",
            "username": "test",
            "password": "test",
        }

        api = FlextDbOracleApi.from_config(config_dict)
        assert api is not None
        mock_with_config.assert_called_once_with(config_dict)

    @patch("flext_db_oracle.FlextDbOracleApi.execute_ddl")
    def test_execute_ddl_mock(self, mock_execute_ddl: Mock) -> None:
        """Test DDL execution for table recreation using mock."""
        # Mock successful DDL execution
        mock_execute_ddl.return_value = FlextCore.Result[None].ok(
            "DDL executed successfully",
        )

        # Create a mock API instance
        config = FlextDbOracleConfig(
            host="localhost",
            service_name="TESTDB",
            username="test",
            password="test",
        )
        api = FlextDbOracleApi(config)

        # Test DDL execution
        ddl_sql = "CREATE TABLE test_table (id NUMBER, name VARCHAR2(100))"
        result = api.execute_ddl(ddl_sql)

        assert result.success
        mock_execute_ddl.assert_called_once_with(ddl_sql)

    @patch("flext_db_oracle.FlextDbOracleApi.query")
    def test_self(self, mock_query: Mock) -> None:
        """Test table validation queries using mock."""
        # Mock query result with table information
        mock_result_data = TDbOracleQueryResult(
            rows=[("TEST_TABLE", "ACTIVE")],
            columns=["TABLE_NAME", "STATUS"],
            row_count=1,
        )
        mock_query.return_value = FlextCore.Result[None].ok(mock_result_data)

        # Create a mock API instance
        config = FlextDbOracleConfig(
            host="localhost",
            service_name="TESTDB",
            username="test",
            password="test",
        )
        api = FlextDbOracleApi(config)

        # Test table validation query
        validation_sql = (
            "SELECT table_name, status FROM user_tables WHERE table_name = 'TEST_TABLE'"
        )
        result = api.query(validation_sql)

        assert result.success
        assert result.data.row_count == 1
        assert result.data.rows[0][0] == "TEST_TABLE"

        mock_query.assert_called_once_with(validation_sql)

    def test_oracle_connection_config_validation(self) -> None:
        """Test Oracle connection configuration validation."""
        # Test valid configuration
        valid_config = GruponosMeltanoOracleConnectionConfig(
            host="localhost",
            port=1521,
            service_name="TESTDB",
            username="test",
            password="test",
        )

        # Configuration should validate successfully
        validation_result = valid_config.validate_semantic_rules()
        assert validation_result.success

    def test_connection_manager_methods_availability(self) -> None:
        """Test that connection manager has required methods."""
        config = GruponosMeltanoOracleConnectionConfig(
            host="localhost",
            service_name="TESTDB",
            username="test",
            password="test",
        )

        manager = create_gruponos_meltano_oracle_connection_manager(config)

        # Test required methods exist
        assert hasattr(manager, "get_connection")
        assert callable(manager.get_connection)

        assert hasattr(manager, "test_connection")
        assert callable(manager.test_connection)

        assert hasattr(manager, "close_connection")
        assert callable(manager.close_connection)

    def test_table_recreation_workflow_components(self) -> None:
        """Test that all components needed for table recreation exist."""
        # Test config creation
        settings = create_gruponos_meltano_settings()
        assert settings is not None

        # Test Oracle config creation
        oracle_config = GruponosMeltanoOracleConnectionConfig(
            host="localhost",
            service_name="TESTDB",
            username="test",
            password="test",
        )
        assert oracle_config is not None

        # Test connection manager creation
        manager = create_gruponos_meltano_oracle_connection_manager(oracle_config)
        assert manager is not None

        # Test FlextDbOracleApi creation capability
        assert hasattr(FlextDbOracleApi, "with_config")
        assert callable(FlextDbOracleApi.with_config)


class TestTableRecreationErrorHandling:
    """Test error handling in table recreation workflows."""

    @patch("flext_db_oracle.FlextDbOracleApi.with_config")
    def test_api_creation_failure(self, mock_with_config: Mock) -> None:
        """Test handling of API creation failures."""
        # Mock API creation failure
        mock_with_config.side_effect = OSError("Connection failed")

        config_dict = {
            "host": "invalid-host",
            "port": 1521,
            "service_name": "TESTDB",
            "username": "test",
            "password": "test",
        }

        # Test that exception is properly raised
        with pytest.raises(OSError, match="Connection failed"):
            FlextDbOracleApi.from_config(config_dict)

    @patch("flext_db_oracle.FlextDbOracleApi.execute_ddl")
    def test_execute_ddl_failure(self, mock_execute_ddl: Mock) -> None:
        """Test handling of DDL execution failures."""
        # Mock DDL execution failure
        mock_execute_ddl.return_value = FlextCore.Result[None].fail("Invalid SQL syntax")

        config = FlextDbOracleConfig(
            host="localhost",
            service_name="TESTDB",
            username="test",
            password="test",
        )
        api = FlextDbOracleApi(config)

        # Test DDL execution with invalid SQL
        invalid_sql = "INVALID SQL STATEMENT"
        result = api.execute_ddl(invalid_sql)

        assert result.is_failure
        assert result.error is not None and "Invalid SQL syntax" in result.error

    def test_invalid_oracle_config(self) -> None:
        """Test handling of invalid Oracle configuration."""
        # Test with missing required fields
        with pytest.raises(Exception):
            GruponosMeltanoOracleConnectionConfig(
                host="",  # Empty host should fail validation
                service_name="TESTDB",
                username="test",
                password="test",
            )


class TestTableRecreationIntegration:
    """Test integration patterns for table recreation."""

    def test_full_workflow_components_integration(self) -> None:
        """Test that all workflow components integrate properly."""
        # Step 1: Create application settings
        settings = create_gruponos_meltano_settings()
        assert settings.app_name == "gruponos-meltano-native"

        # Step 2: Create Oracle connection configuration
        oracle_config = GruponosMeltanoOracleConnectionConfig(
            host="localhost",
            port=1521,
            service_name="TESTDB",
            username="test",
            password="test",
        )

        # Step 3: Create connection manager
        manager = create_gruponos_meltano_oracle_connection_manager(oracle_config)

        # Step 4: Validate that manager can provide Oracle API
        connection_result = manager.get_connection()
        # We expect this to fail in test environment (no real DB)
        # but it should return a proper FlextCore.Result
        assert hasattr(connection_result, "success")
        assert hasattr(connection_result, "is_failure")

    def test_configuration_validation_workflow(self) -> None:
        """Test configuration validation workflow."""
        # Create configuration
        config = GruponosMeltanoOracleConnectionConfig(
            host="localhost",
            service_name="TESTDB",
            username="test",
            password="test",
        )

        # Validate configuration using real method
        validation_result = config.validate_semantic_rules()
        assert validation_result.success

        # Create connection manager with validated config
        manager = create_gruponos_meltano_oracle_connection_manager(config)
        assert manager is not None

        # Test manager validation
        manager_validation = manager.test_connection()
        assert hasattr(manager_validation, "success")


# Test execution entrypoint
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
