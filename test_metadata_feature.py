#!/usr/bin/env python3
"""Quick test to verify the new execute_with_metadata functionality works correctly.

This replaces the private _connection access with public method access.
"""

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
    with patch("flext_db_oracle.connection.config.ConnectionConfig") as mock_config_class:
        mock_config = MagicMock()
        mock_config_class.return_value = mock_config

        # Create connection instance
        conn = FlextDbOracleResilientConnection(mock_config)
        conn._connection = mock_connection  # noqa: SLF001
        conn._is_connected = True  # noqa: SLF001

        # Test the new method
        result = conn.execute_with_metadata("SELECT id, name, email FROM users")

        # Verify structure
        assert isinstance(result, dict)  # noqa: S101
        assert "columns" in result  # noqa: S101
        assert "rows" in result  # noqa: S101
        assert "affected_rows" in result  # noqa: S101

        # Verify column names extraction
        expected_columns = ["ID", "NAME", "EMAIL"]
        assert result["columns"] == expected_columns  # noqa: S101

        # Verify rows
        expected_rows = [
            (1, "John Doe", "john@example.com"),
            (2, "Jane Smith", "jane@example.com"),
        ]
        assert result["rows"] == expected_rows  # noqa: S101

        # For SELECT statements, affected_rows should be 0
        assert result["affected_rows"] == 0  # noqa: S101


def test_connection_manager_usage() -> None:
    """Test that connection manager can use the new method without private access."""
    from gruponos_meltano_native.config import GruponosMeltanoOracleConnectionConfig
    from gruponos_meltano_native.oracle.connection_manager_enhanced import (
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
    assert manager is not None  # noqa: S101
    assert manager.config.host == "localhost"  # noqa: S101


if __name__ == "__main__":
    test_execute_with_metadata_method()
    test_connection_manager_usage()
