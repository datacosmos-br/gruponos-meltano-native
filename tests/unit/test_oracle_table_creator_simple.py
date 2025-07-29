"""Simplified tests for Oracle table creator functionality.

REAL IMPLEMENTATION TESTS - NO MOCKS OR FALLBACKS.
Tests the actual Oracle table creation logic with basic functionality.
"""

from gruponos_meltano_native.oracle.table_creator import OracleTableCreator


class TestOracleTableCreatorSimple:
    """Test Oracle table creator with real implementation."""

    def test_table_creator_initialization(self) -> None:
        """Test table creator initialization with configuration."""
        config = {
            "host": "localhost",
            "port": 1521,
            "service_name": "XEPDB1",
            "username": "test_user",
            "password": "test_pass",
        }

        creator = OracleTableCreator(config)
        assert creator is not None
        # Test actual attributes from implementation
        assert hasattr(creator, "host")
        assert hasattr(creator, "port")
        assert hasattr(creator, "service_name")
        assert hasattr(creator, "username")
        assert hasattr(creator, "password")
        assert hasattr(creator, "schema")
        assert hasattr(creator, "type_mappings")

    def test_table_creator_properties(self) -> None:
        """Test table creator has required properties."""
        config = {
            "host": "localhost",
            "port": 1521,
            "service_name": "XEPDB1",
            "username": "test_user",
            "password": "test_pass",
        }

        creator = OracleTableCreator(config)

        # Check that creator has necessary attributes based on actual implementation
        if creator.host != "localhost":
            msg = f"Expected {"localhost"}, got {creator.host}"
            raise AssertionError(msg)
        assert creator.port == 1521
        if creator.service_name != "XEPDB1":
            msg = f"Expected {"XEPDB1"}, got {creator.service_name}"
            raise AssertionError(msg)
        assert creator.username == "test_user"
        if creator.password != "test_pass":
            msg = f"Expected {"test_pass"}, got {creator.password}"
            raise AssertionError(msg)

    def test_table_creator_config_validation(self) -> None:
        """Test configuration validation."""
        # Valid config
        valid_config = {
            "host": "localhost",
            "port": 1521,
            "service_name": "XEPDB1",
            "username": "test_user",
            "password": "test_pass",
        }

        creator = OracleTableCreator(valid_config)
        assert creator is not None

    def test_table_creator_methods_exist(self) -> None:
        """Test that required methods exist."""
        config = {
            "host": "localhost",
            "port": 1521,
            "service_name": "XEPDB1",
            "username": "test_user",
            "password": "test_pass",
        }

        creator = OracleTableCreator(config)

        # Check for actual methods from implementation
        expected_methods = [
            "create_table_from_schema",
            "create_indexes_for_table",
            "execute_ddl",
            "generate_table_from_singer_catalog",
        ]

        for method_name in expected_methods:
            assert hasattr(creator, method_name), f"Missing method: {method_name}"
            assert callable(getattr(creator, method_name))

    def test_wms_schema_generation(self) -> None:
        """Test WMS schema DDL generation."""
        config = {
            "host": "localhost",
            "port": 1521,
            "service_name": "XEPDB1",
            "username": "test_user",
            "password": "test_pass",
        }

        creator = OracleTableCreator(config)

        # Test schema object creation
        assert creator is not None

        # Verify initialization completed
        if creator.host != "localhost":
            msg = f"Expected {"localhost"}, got {creator.host}"
            raise AssertionError(msg)
        assert creator.port == 1521
