"""End-to-end integration tests for Oracle functionality.

These tests require real Oracle database connections and test complete workflows.
"""

from __future__ import annotations

import os

import pytest
from dotenv import load_dotenv

from gruponos_meltano_native import (
    GruponosMeltanoOracleConnectionConfig,
    GruponosMeltanoOracleConnectionManager,
    GruponosMeltanoSettings,
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
      self,
      oracle_config: GruponosMeltanoOracleConnectionConfig,
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
      # Test connection, skipping when DB is not reachable in CI
      precheck = connection_manager.test_connection()
      if not precheck.success:
          pytest.skip(f"Oracle not reachable in environment: {precheck.error}")
      result = precheck
      assert result.success, f"Connection test failed: {result.error}"

      # Validate result data
      assert result.data is not None
      if not (result.data["success"]):
          msg: str = f"Expected True, got {result.data['success']}"
          raise AssertionError(msg)
      if "oracle_version" not in result.data:
          msg: str = f"Expected {'oracle_version'} in {result.data}"
          raise AssertionError(msg)

    @pytest.mark.integration
    @pytest.mark.slow
    def test_oracle_query_execution(
      self,
      connection_manager: GruponosMeltanoOracleConnectionManager,
    ) -> None:
      """Test Oracle query execution."""
      # Pre-check connectivity; skip when DB is not reachable in CI
      precheck = connection_manager.test_connection()
      if not precheck.success:
          pytest.skip(f"Oracle not reachable in environment: {precheck.error}")

      # Get real Oracle API connection
      connection_result = connection_manager.get_connection()
      assert connection_result.success, (
          f"Failed to get connection: {connection_result.error}"
      )

      oracle_api = connection_result.data
      assert oracle_api is not None, "Oracle API connection is None"

      # Connect to database before executing queries
      oracle_api.connect()

      try:
          # Test simple query using real API
          result = oracle_api.query("SELECT 1 as test_col FROM DUAL")
          assert result.success, f"Query execution failed: {result.error}"
      finally:
          oracle_api.disconnect()

      # Validate result structure using real TDbOracleQueryResult format
      assert result.data is not None
      query_result = result.data
      assert hasattr(query_result, "rows"), "Query result should have rows attribute"
      assert hasattr(query_result, "columns"), (
          "Query result should have columns attribute"
      )

      # TDbOracleQueryResult.rows are TUPLES, not dicts: list[tuple[object, ...]]
      rows = query_result.rows
      if len(rows) != 1:
          msg: str = f"Expected {1}, got {len(rows)}"
          raise AssertionError(msg)

      # Access tuple data by index, not key: rows[0][0] for first column
      first_row = rows[0]
      if len(first_row) < 1:
          msg: str = f"Expected at least 1 column, got {len(first_row)}"
          raise AssertionError(msg)
      if first_row[0] != 1:
          msg: str = f"Expected {1}, got {first_row[0]}"
          raise AssertionError(msg)

      # Verify column name is available in columns list
      columns = query_result.columns
      if len(columns) < 1 or "TEST_COL" not in [col.upper() for col in columns]:
          msg: str = f"Expected TEST_COL in columns {columns}"
          raise AssertionError(msg)

    @pytest.mark.integration
    @pytest.mark.slow
    def test_oracle_command_execution(
      self,
      connection_manager: GruponosMeltanoOracleConnectionManager,
    ) -> None:
      """Test Oracle command execution."""
      # Pre-check connectivity; skip when DB is not reachable in CI
      precheck = connection_manager.test_connection()
      if not precheck.success:
          pytest.skip(f"Oracle not reachable in environment: {precheck.error}")
      # Get real Oracle API connection
      connection_result = connection_manager.get_connection()
      assert connection_result.success, (
          f"Failed to get connection: {connection_result.error}"
      )

      oracle_api = connection_result.data
      assert oracle_api is not None, "Oracle API connection is None"

      # Connect to database before executing operations
      oracle_api.connect()

      try:
          # Create a test table using real execute_ddl API
          create_result = oracle_api.execute_ddl(
              """
              CREATE TABLE test_flext_table (
                  id NUMBER PRIMARY KEY,
                  test_data VARCHAR2(100)
              )
              """,
          )
          assert create_result.success, (
              f"Table creation failed: {create_result.error}"
          )

          try:
              # Insert test data using real execute_ddl API for DML
              insert_result = oracle_api.execute_ddl(
                  "INSERT INTO test_flext_table VALUES (1, 'test')",
              )
              assert insert_result.success, f"Insert failed: {insert_result.error}"

              # Query the data back using real query API
              query_result = oracle_api.query(
                  "SELECT * FROM test_flext_table WHERE id = 1",
              )
              assert query_result.success, f"Query failed: {query_result.error}"

              # Validate result structure using real TDbOracleQueryResult format
              assert query_result.data is not None
              result_data = query_result.data
              assert hasattr(result_data, "rows"), (
                  "Query result should have rows attribute"
              )
              assert hasattr(result_data, "columns"), (
                  "Query result should have columns attribute"
              )

              # TDbOracleQueryResult.rows are TUPLES: list[tuple[object, ...]]
              rows = result_data.rows
              if len(rows) != 1:
                  msg: str = f"Expected {1}, got {len(rows)}"
                  raise AssertionError(msg)

              # Convert to dict for easier validation using built-in method
              dict_rows = result_data.to_dict_list()
              if len(dict_rows) != 1:
                  msg: str = f"Expected {1}, got {len(dict_rows)}"
                  raise AssertionError(msg)

              # Now we can access by column name (Oracle returns uppercase)
              row_dict = dict_rows[0]
              if "TEST_DATA" not in row_dict:
                  msg: str = f"Expected TEST_DATA column in {row_dict.keys()}"
                  raise AssertionError(msg)
              if row_dict["TEST_DATA"] != "test":
                  msg: str = f"Expected 'test', got {row_dict['TEST_DATA']}"
                  raise AssertionError(msg)

          finally:
              # Clean up - drop test table using real execute_ddl API
              drop_result = oracle_api.execute_ddl(
                  "DROP TABLE test_flext_table",
              )
              assert drop_result.success, f"Table cleanup failed: {drop_result.error}"
      finally:
          # Always disconnect
          oracle_api.disconnect()

    @pytest.mark.integration
    @pytest.mark.slow
    def test_connection_validation(
      self,
      connection_manager: GruponosMeltanoOracleConnectionManager,
    ) -> None:
      """Test connection configuration validation."""
      result = connection_manager.validate_configuration()
      assert result.success, f"Configuration validation failed: {result.error}"

    @pytest.mark.integration
    @pytest.mark.slow
    def test_connection_manager_lifecycle(
      self,
      connection_manager: GruponosMeltanoOracleConnectionManager,
    ) -> None:
      """Test full connection manager lifecycle."""
      # Pre-check connectivity; skip when DB is not reachable in CI
      precheck = connection_manager.test_connection()
      if not precheck.success:
          pytest.skip(f"Oracle not reachable in environment: {precheck.error}")
      # Connect
      connect_result = connection_manager.connect()
      assert connect_result.success, f"Connection failed: {connect_result.error}"

      # Check connection status
      assert connection_manager.is_connected()

      # Get connection info
      info = connection_manager.get_connection_info()
      if not (info["is_connected"]):
          msg: str = f"Expected True, got {info['is_connected']}"
          raise AssertionError(msg)
      if info["host"] != connection_manager.config.host:
          msg: str = f"Expected {connection_manager.config.host}, got {info['host']}"
          raise AssertionError(msg)

      # Disconnect
      disconnect_result = connection_manager.disconnect()
      assert disconnect_result.success, (
          f"Disconnection failed: {disconnect_result.error}"
      )

      # Verify disconnection
      assert not connection_manager.is_connected()


class TestSettingsIntegration:
    """Test configuration settings integration."""

    def test_settings_creation(self) -> None:
      """Test GruponosMeltanoSettings creation and validation."""
      settings = GruponosMeltanoSettings()

      # Basic validation
      if settings.app_name != "gruponos-meltano-native":
          msg: str = f"Expected {'gruponos-meltano-native'}, got {settings.app_name}"
          raise AssertionError(msg)
      assert settings.version == "0.9.0"
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
      if conn_str != "testuser/testpass@test.oracle.com:1522/TESTDB":
          msg: str = f"Expected {'testuser/testpass@test.oracle.com:1522/TESTDB'}, got {conn_str}"
          raise AssertionError(msg)
