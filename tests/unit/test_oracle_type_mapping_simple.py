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
        if "pk" not in mappings:
            msg = f"Expected {'pk'} in {mappings}"
            raise AssertionError(msg)
        assert "varchar" in mappings
        if "number" not in mappings:
            msg = f"Expected {'number'} in {mappings}"
            raise AssertionError(msg)
        assert "datetime" in mappings

        # Test mapping values
        if mappings["pk"] != "NUMBER":
            msg = f"Expected {'NUMBER'}, got {mappings['pk']}"
            raise AssertionError(msg)
        if "VARCHAR2" not in mappings["varchar"]:
            msg = f"Expected {'VARCHAR2'} in {mappings['varchar']}"
            raise AssertionError(msg)
        if mappings["number"] != "NUMBER":
            msg = f"Expected {'NUMBER'}, got {mappings['number']}"
            raise AssertionError(msg)
        if "TIMESTAMP" not in mappings["datetime"]:
            msg = f"Expected {'TIMESTAMP'} in {mappings['datetime']}"
            raise AssertionError(msg)

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
        if mappings.get("pk") != "NUMBER":
            msg = f"Expected {'NUMBER'}, got {mappings.get('pk')}"
            raise AssertionError(msg)

        # Test boolean mapping
        if mappings.get("boolean") != "NUMBER(1,0)":
            msg = f"Expected {'NUMBER(1,0)'}, got {mappings.get('boolean')}"
            raise AssertionError(
                msg,
            )

        # Test text mapping
        if "VARCHAR2" not in mappings.get("text", ""):
            msg = f"Expected {'VARCHAR2'} in {mappings.get('text', '')}"
            raise AssertionError(msg)

        # Test CLOB mapping
        if mappings.get("clob") != "CLOB":
            msg = f"Expected {'CLOB'}, got {mappings.get('clob')}"
            raise AssertionError(msg)

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
            if required_type not in mappings:
                msg = (
                    f"Expected {required_type} in {mappings}"
                    f"Missing mapping for {required_type}"
                )
                raise AssertionError(
                    msg,
                )
