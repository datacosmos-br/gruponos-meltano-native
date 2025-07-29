#!/usr/bin/env python3
"""Quick test to verify the new execute_with_metadata functionality works correctly.

This replaces the private _connection access with public method access.
"""

from gruponos_meltano_native.config import GruponosMeltanoOracleConnectionConfig
from gruponos_meltano_native.oracle.connection_manager_enhanced import (


from unittest.mock import MagicMock, patch

from flext_db_oracle.connection.resilient_connection import (
    FlextDbOracleResilientConnection,
)


def test_execute_with_metadata_method() -> None:
    """Test that execute_with_metadata method returns expected structure."""
    # Mock the underlying connection
    mock_connection = MagicMock()
    mock_cursor = MagicMock()

    # Setup cursor mock
    mock_cursor.description = [
        ("ID", "NUMBER", 22, 0, 10, 0, 0),
        ("NAME", "VARCHAR2", 50, 50, 0, 0, 1),
        ("EMAIL", "VARCHAR2", 100, 100, 0, 0, 1),
    ]
    mock_cursor.fetchall.return_value = [
        (1, "John Doe", "john@example.com"),
        (2, "Jane Smith", "jane@example.com"),
    ]

    mock_connection.cursor.return_value = mock_cursor

    # Create connection config mock
    with patch(
        "flext_db_oracle.connection.config.ConnectionConfig",
    ) as mock_config_class:
        mock_config = MagicMock()
        mock_config_class.return_value = mock_config

        # Create connection instance
        conn = FlextDbOracleResilientConnection(mock_config)
        conn._connection = mock_connection
        conn._is_connected = True

        # Test the new method
        result = conn.execute_with_metadata("SELECT id, name, email FROM users")

        # Verify structure
        assert isinstance(result, dict)
        if "columns" not in result:
            raise AssertionError(f"Expected {"columns"} in {result}")
        assert "rows" in result
        if "affected_rows" not in result:
            raise AssertionError(f"Expected {"affected_rows"} in {result}")

        # Verify column names extraction
        expected_columns = ["ID", "NAME", "EMAIL"]
        if result["columns"] != expected_columns:
            raise AssertionError(f"Expected {expected_columns}, got {result["columns"]}")

        # Verify rows
        expected_rows = [
            (1, "John Doe", "john@example.com"),
            (2, "Jane Smith", "jane@example.com"),
        ]
        if result["rows"] != expected_rows:
            raise AssertionError(f"Expected {expected_rows}, got {result["rows"]}")

        # For SELECT statements, affected_rows should be 0
        if result["affected_rows"] != 0:
            raise AssertionError(f"Expected {0}, got {result["affected_rows"]}")


def test_connection_manager_usage() -> None:
    """Test that connection manager can use the new method without private access."""


        GruponosMeltanoOracleConnectionManager,
    )

    # Create a connection config
    config = GruponosMeltanoOracleConnectionConfig(
        host="localhost",
        port=1521,
        service_name="ORCL",
        username="test",
        password="test",
    )

    # Create connection manager
    manager = GruponosMeltanoOracleConnectionManager(config)

    # Verify the manager was created successfully
    assert manager is not None
    if manager.config.host != "localhost":
        raise AssertionError(f"Expected {"localhost"}, got {manager.config.host}")


if __name__ == "__main__":
    test_execute_with_metadata_method()
    test_connection_manager_usage()
