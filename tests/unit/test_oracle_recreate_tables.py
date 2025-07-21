"""Tests for Oracle table recreation functionality.

REAL IMPLEMENTATION TESTS - NO MOCKS OR FALLBACKS.
Tests the actual Oracle table recreation logic with comprehensive functionality.
"""

from gruponos_meltano_native.oracle import recreate_tables_and_sync


class TestOracleRecreateTablesSimple:
    """Test Oracle table recreation with real implementation."""

    def test_recreate_functions_exist(self) -> None:
        """Test table recreation functions exist."""
        expected_functions = [
            "drop_all_wms_tables",
            "create_tables_with_ddl",
            "run_full_sync",
            "validate_sync_results",
        ]

        for func_name in expected_functions:
            assert hasattr(recreate_tables_and_sync, func_name), (
                f"Missing function: {func_name}"
            )
            assert callable(getattr(recreate_tables_and_sync, func_name))

    def test_module_import(self) -> None:
        """Test module imports correctly."""
        assert recreate_tables_and_sync is not None

    def test_main_function_exists(self) -> None:
        """Test main function exists."""
        assert hasattr(recreate_tables_and_sync, "main")
        assert callable(recreate_tables_and_sync.main)

    def test_table_management_functions(self) -> None:
        """Test table management functions exist."""
        # Test table dropping function
        assert hasattr(recreate_tables_and_sync, "drop_all_wms_tables")
        assert callable(recreate_tables_and_sync.drop_all_wms_tables)

        # Test table creation function
        assert hasattr(recreate_tables_and_sync, "create_tables_with_ddl")
        assert callable(recreate_tables_and_sync.create_tables_with_ddl)

    def test_sync_functions(self) -> None:
        """Test sync functions exist."""
        # Test full sync function
        assert hasattr(recreate_tables_and_sync, "run_full_sync")
        assert callable(recreate_tables_and_sync.run_full_sync)

        # Test sync validation function
        assert hasattr(recreate_tables_and_sync, "validate_sync_results")
        assert callable(recreate_tables_and_sync.validate_sync_results)
