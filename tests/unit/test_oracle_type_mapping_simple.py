"""Simplified tests for Oracle type mapping rules functionality.

REAL IMPLEMENTATION TESTS - NO MOCKS OR FALLBACKS.
Tests the actual Oracle type mapping logic with basic functionality.
"""

from gruponos_meltano_native.oracle import type_mapping_rules


class TestOracleTypeMappingSimple:
    """Test Oracle type mapping with real implementation."""

    def test_type_mapping_constants_exist(self) -> None:
        """Test type mapping constants exist."""
        assert hasattr(type_mapping_rules, "WMS_METADATA_TO_ORACLE")
        assert isinstance(type_mapping_rules.WMS_METADATA_TO_ORACLE, dict)

    def test_wms_to_oracle_mappings(self) -> None:
        """Test WMS to Oracle type mappings."""
        mappings = type_mapping_rules.WMS_METADATA_TO_ORACLE

        # Test basic mappings exist
        assert "pk" in mappings
        assert "varchar" in mappings
        assert "number" in mappings
        assert "datetime" in mappings

        # Test mapping values
        assert mappings["pk"] == "NUMBER"
        assert "VARCHAR2" in mappings["varchar"]
        assert mappings["number"] == "NUMBER"
        assert "TIMESTAMP" in mappings["datetime"]

    def test_oracle_type_constants(self) -> None:
        """Test Oracle type constants."""
        mappings = type_mapping_rules.WMS_METADATA_TO_ORACLE

        # Verify all values are valid Oracle types
        oracle_types = ["NUMBER", "VARCHAR2", "CHAR", "TIMESTAMP", "CLOB"]

        for mapping_value in mappings.values():
            # Check if any Oracle type is present in the mapping
            has_oracle_type = any(
                oracle_type in mapping_value for oracle_type in oracle_types
            )
            assert has_oracle_type, f"Invalid Oracle type: {mapping_value}"

    def test_specific_type_mappings(self) -> None:
        """Test specific type mapping values."""
        mappings = type_mapping_rules.WMS_METADATA_TO_ORACLE

        # Test primary key mapping
        assert mappings.get("pk") == "NUMBER"

        # Test boolean mapping
        assert mappings.get("boolean") == "NUMBER(1,0)"

        # Test text mapping
        assert "VARCHAR2" in mappings.get("text", "")

        # Test CLOB mapping
        assert mappings.get("clob") == "CLOB"

    def test_mapping_completeness(self) -> None:
        """Test mapping completeness for WMS data types."""
        mappings = type_mapping_rules.WMS_METADATA_TO_ORACLE

        required_types = [
            "pk",
            "varchar",
            "char",
            "number",
            "decimal",
            "integer",
            "boolean",
            "datetime",
            "date",
            "text",
        ]

        for required_type in required_types:
            assert required_type in mappings, f"Missing mapping for {required_type}"
