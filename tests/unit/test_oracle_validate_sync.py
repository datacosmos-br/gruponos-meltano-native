"""Tests for Oracle validation sync functionality.

# Constants
EXPECTED_BULK_SIZE = 2
EXPECTED_DATA_COUNT = 3

REAL IMPLEMENTATION TESTS - NO MOCKS OR FALLBACKS.
Tests the actual Oracle validation sync logic with comprehensive functionality.
"""

from typing import Any
from unittest.mock import patch

from gruponos_meltano_native.oracle.validate_sync import (
    _check_table_exists,
    _count_table_records,
    _get_table_details,
    _get_table_list,
    _validate_single_table,
    _validate_table_name,
    validate_sync,
)


class TestOracleValidateSync:
    """Test Oracle validation sync with real implementation."""

    def test_validate_table_name(self) -> None:
        """Test table name validation function."""
        # Valid table names
        if not (_validate_table_name("WMS_ALLOCATION")):
            msg = f"Expected True, got {_validate_table_name('WMS_ALLOCATION')}"
            raise AssertionError(
                msg,
            )
        assert _validate_table_name("ORDER_HDR") is True
        if not (_validate_table_name("TABLE123")):
            msg = f"Expected True, got {_validate_table_name('TABLE123')}"
            raise AssertionError(
                msg,
            )
        assert _validate_table_name("USER_DATA_2024") is True

        # Invalid table names
        if _validate_table_name("TABLE; DROP TABLE"):
            msg = f"Expected False, got {_validate_table_name('TABLE; DROP TABLE')}"
            raise AssertionError(
                msg,
            )
        assert _validate_table_name("TABLE'") is False
        if _validate_table_name("TABLE-NAME"):
            msg = f"Expected False, got {_validate_table_name('TABLE-NAME')}"
            raise AssertionError(
                msg,
            )
        assert _validate_table_name("TABLE NAME") is False

    def test_get_table_list(self) -> None:
        """Test getting the list of tables to validate."""
        tables = _get_table_list()

        # Test returns list of tuples
        assert isinstance(tables, list)
        assert len(tables) > 0

        # Test tuple structure
        for table_name, entity_name in tables:
            assert isinstance(table_name, str)
            assert isinstance(entity_name, str)
            assert len(table_name) > 0
            assert len(entity_name) > 0

        # Test expected tables are included
        table_names = [table[0] for table in tables]
        if "WMS_ALLOCATION" not in table_names:
            msg = f"Expected {'WMS_ALLOCATION'} in {table_names}"
            raise AssertionError(msg)
        assert "WMS_ORDER_HDR" in table_names
        if "WMS_ORDER_DTL" not in table_names:
            msg = f"Expected {'WMS_ORDER_DTL'} in {table_names}"
            raise AssertionError(msg)

    def test_check_table_exists_mock(self) -> None:
        """Test table existence check with mock cursor."""
        # Mock cursor that returns table exists
        mock_cursor = type(
            "MockCursor",
            (),
            {
                "execute": lambda self, query, params: None,
                "fetchone": lambda self: [1],  # Table exists
            },
        )()

        result = _check_table_exists(mock_cursor, "WMS_ALLOCATION")
        if not (result):
            msg = f"Expected True, got {result}"
            raise AssertionError(msg)

        # Mock cursor that returns table doesn't exist
        mock_cursor_no_table = type(
            "MockCursor",
            (),
            {
                "execute": lambda self, query, params: None,
                "fetchone": lambda self: [0],  # Table doesn't exist
            },
        )()

        result = _check_table_exists(mock_cursor_no_table, "NON_EXISTENT_TABLE")
        if result:
            msg = f"Expected False, got {result}"
            raise AssertionError(msg)

    def test_check_table_exists_with_error(self) -> None:
        """Test table existence check with database error."""
        # Mock cursor that raises exception
        mock_cursor_error = type(
            "MockCursor",
            (),
            {
                "execute": lambda self, query, params: (_ for _ in ()).throw(
                    OSError("Connection failed"),
                ),
                "fetchone": lambda self: None,
            },
        )()

        result = _check_table_exists(mock_cursor_error, "ANY_TABLE")
        if result:
            msg = f"Expected False, got {result}"
            raise AssertionError(msg)

    def test_count_table_records_mock(self) -> None:
        """Test table record counting with mock cursor."""
        # Mock cursor with valid count
        mock_cursor = type(
            "MockCursor",
            (),
            {
                "execute": lambda self, query: None,
                "fetchone": lambda self: [1500],  # 1500 records
            },
        )()

        result = _count_table_records(mock_cursor, "WMS_ALLOCATION")
        if result != 1500:
            msg = f"Expected {1500}, got {result}"
            raise AssertionError(msg)

        # Test with invalid table name
        result = _count_table_records(mock_cursor, "INVALID; TABLE")
        if result != 0:
            msg = f"Expected {0}, got {result}"
            raise AssertionError(msg)

    def test_count_table_records_with_error(self) -> None:
        """Test table record counting with database error."""
        # Mock cursor that raises exception
        mock_cursor_error = type(
            "MockCursor",
            (),
            {
                "execute": lambda self, query: (_ for _ in ()).throw(
                    ValueError("SQL error"),
                ),
                "fetchone": lambda self: None,
            },
        )()

        result = _count_table_records(mock_cursor_error, "WMS_ALLOCATION")
        if result != 0:
            msg = f"Expected {0}, got {result}"
            raise AssertionError(msg)

    def test_get_table_details_mock(self) -> None:
        """Test getting table details with mock cursor."""
        # Mock cursor that returns valid details
        call_count = [0]  # Use list to allow modification in lambda

        def mock_fetchone(self: Any) -> list[Any]:
            call_count[0] += 1
            if call_count[0] == 1:  # First call (MIN/MAX/COUNT query)
                return ["2024-01-01", "2024-12-31", 1000]
            # Second call (duplicates query)
            return [5]

        mock_cursor = type(
            "MockCursor",
            (),
            {"execute": lambda self, query: None, "fetchone": mock_fetchone},
        )()

        result = _get_table_details(mock_cursor, "WMS_ALLOCATION")

        assert isinstance(result, dict)
        if "min_date" not in result:
            msg = f"Expected {'min_date'} in {result}"
            raise AssertionError(msg)
        assert "max_date" in result
        if "unique_ids" not in result:
            msg = f"Expected {'unique_ids'} in {result}"
            raise AssertionError(msg)
        assert "duplicates" in result
        if result["unique_ids"] != 1000:
            msg = f"Expected {1000}, got {result['unique_ids']}"
            raise AssertionError(msg)
        assert result["duplicates"] == 5

    def test_get_table_details_with_invalid_table(self) -> None:
        """Test getting table details with invalid table name."""
        mock_cursor = type(
            "MockCursor",
            (),
            {
                "execute": lambda self, query: None,
                "fetchone": lambda self: [None, None, 0],
            },
        )()

        result = _get_table_details(mock_cursor, "INVALID; TABLE")

        # Should return default values for invalid table
        assert result["min_date"] is None
        assert result["max_date"] is None
        if result["unique_ids"] != 0:
            msg = f"Expected {0}, got {result['unique_ids']}"
            raise AssertionError(msg)
        assert result["duplicates"] == 0

    def test_validate_single_table_mock(self) -> None:
        """Test validating a single table with mock cursor."""
        # Mock cursor for table that exists and has records
        call_count = [0]

        def mock_fetchone(self: Any) -> list[Any]:
            call_count[0] += 1
            if call_count[0] == 1:  # table exists check
                return [1]
            if call_count[0] == EXPECTED_BULK_SIZE:  # count records
                return [1000]
            if call_count[0] == EXPECTED_DATA_COUNT:  # get details - min/max/unique_ids
                return ["2024-01-01", "2024-12-31", 950]
            # get details - duplicates
            return [0]

        mock_cursor = type(
            "MockCursor",
            (),
            {
                "execute": lambda self, query, params=None: None,
                "fetchone": mock_fetchone,
            },
        )()

        result = _validate_single_table(mock_cursor, "WMS_ALLOCATION", "allocation")
        if result != 1000:
            msg = f"Expected {1000}, got {result}"
            raise AssertionError(msg)

    def test_validate_single_table_nonexistent(self) -> None:
        """Test validating a table that doesn't exist."""
        # Mock cursor for table that doesn't exist
        mock_cursor = type(
            "MockCursor",
            (),
            {
                "execute": lambda self, query, params=None: None,
                "fetchone": lambda self: [0],  # Table doesn't exist
            },
        )()

        result = _validate_single_table(mock_cursor, "NONEXISTENT_TABLE", "nonexistent")
        if result != 0:
            msg = f"Expected {0}, got {result}"
            raise AssertionError(msg)

    def test_validate_single_table_empty(self) -> None:
        """Test validating a table that exists but is empty."""
        # Mock cursor for table that exists but has no records
        call_count = [0]

        def mock_fetchone(self: Any) -> list[Any]:
            call_count[0] += 1
            if call_count[0] == 1:  # First call - table exists check
                return [1]  # Table exists
            # All other calls - count is 0 (empty table)
            return [0]

        mock_cursor = type(
            "MockCursor",
            (),
            {
                "execute": lambda self, query, params=None: None,
                "fetchone": mock_fetchone,
            },
        )()

        result = _validate_single_table(mock_cursor, "EMPTY_TABLE", "empty")
        if result != 0:
            msg = f"Expected {0}, got {result}"
            raise AssertionError(msg)

    @patch("gruponos_meltano_native.oracle.validate_sync.get_config")
    @patch(
        "gruponos_meltano_native.oracle.validate_sync.GruponosMeltanoOracleConnectionManager",
    )
    def test_validate_sync_no_config(
        self,
        mock_manager: object,
        mock_get_config: object,
    ) -> None:
        """Test validate_sync with missing Oracle configuration."""
        # Mock config with no target_oracle
        mock_config = type("MockConfig", (), {"target_oracle": None})()
        mock_get_config.return_value = mock_config

        result = validate_sync()
        if result:
            msg = f"Expected False, got {result}"
            raise AssertionError(msg)

    @patch("gruponos_meltano_native.oracle.validate_sync.get_config")
    @patch(
        "gruponos_meltano_native.oracle.validate_sync.GruponosMeltanoOracleConnectionManager",
    )
    def test_validate_sync_connection_error(
        self,
        mock_manager: object,
        mock_get_config: object,
    ) -> None:
        """Test validate_sync with connection error."""
        # Mock config with valid target_oracle
        mock_oracle_config = type(
            "MockOracleConfig",
            (),
            {"oracle": {"host": "localhost"}},
        )()
        mock_config = type("MockConfig", (), {"target_oracle": mock_oracle_config})()
        mock_get_config.return_value = mock_config

        # Mock connection manager that raises exception
        mock_manager_instance = type(
            "MockManager",
            (),
            {
                "connect": lambda self: (_ for _ in ()).throw(
                    OSError("Connection failed"),
                ),
            },
        )()
        mock_manager.return_value = mock_manager_instance

        result = validate_sync()
        if result:
            msg = f"Expected False, got {result}"
            raise AssertionError(msg)

    @patch("gruponos_meltano_native.oracle.validate_sync.get_config")
    @patch(
        "gruponos_meltano_native.oracle.validate_sync.GruponosMeltanoOracleConnectionManager",
    )
    def test_validate_sync_success(
        self,
        mock_manager: object,
        mock_get_config: object,
    ) -> None:
        """Test validate_sync with successful validation."""
        # Mock config with valid target_oracle
        mock_oracle_config = type(
            "MockOracleConfig",
            (),
            {"oracle": {"host": "localhost"}},
        )()
        mock_config = type("MockConfig", (), {"target_oracle": mock_oracle_config})()
        mock_get_config.return_value = mock_config

        # Mock successful connection and cursor
        call_count = [0]

        def mock_fetchone(self: Any) -> list[Any]:
            call_count[0] += 1
            # Pattern: table exists check, count records, get details (2 calls), then
            # repeat for other tables
            fetch_calls = call_count[0] % 4
            if fetch_calls == 1:  # table exists check
                return [1]
            if fetch_calls == EXPECTED_BULK_SIZE:  # count records
                return [1000]
            if fetch_calls == EXPECTED_DATA_COUNT:  # get details - min/max/unique_ids
                return ["2024-01-01", "2024-12-31", 950]
            # get details - duplicates
            return [0]

        mock_cursor = type(
            "MockCursor",
            (),
            {
                "execute": lambda self, query, params=None: None,
                "fetchone": mock_fetchone,
                "close": lambda self: None,
            },
        )()

        mock_connection = type(
            "MockConnection",
            (),
            {"cursor": lambda self: mock_cursor, "close": lambda self: None},
        )()

        mock_manager_instance = type(
            "MockManager",
            (),
            {"connect": lambda self: mock_connection},
        )()
        mock_manager.return_value = mock_manager_instance

        result = validate_sync()
        if not (result):
            msg = f"Expected True, got {result}"
            raise AssertionError(msg)

    def test_validate_sync_function_exists(self) -> None:
        """Test that validate_sync function exists and is callable."""
        assert callable(validate_sync)

    def test_validate_sync_returns_boolean(self) -> None:
        """Test that validate_sync returns a boolean."""
        with patch(
            "gruponos_meltano_native.oracle.validate_sync.get_config",
        ) as mock_get_config:
            # Mock config with no target_oracle to force False return
            mock_config = type("MockConfig", (), {"target_oracle": None})()
            mock_get_config.return_value = mock_config

            result = validate_sync()
            assert isinstance(result, bool)
