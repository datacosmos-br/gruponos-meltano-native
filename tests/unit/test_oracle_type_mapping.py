"""Tests for Oracle type mapping rules functionality.

REAL IMPLEMENTATION TESTS - NO MOCKS OR FALLBACKS.
Tests the actual Oracle type mapping logic with comprehensive type handling.
"""

from gruponos_meltano_native.oracle.type_mapping_rules import (
    FIELD_PATTERN_RULES,
    FIELD_PATTERNS_TO_ORACLE,
    WMS_METADATA_TO_ORACLE,
    convert_field_pattern_to_oracle,
    convert_field_to_oracle_new,
    convert_singer_schema_to_oracle,
    oracle_ddl_from_singer_schema,
)


class TestOracleTypeMappingRules:
    """Test Oracle type mapping rules with real implementation."""

    def test_wms_metadata_to_oracle_mapping(self) -> None:
        """Test WMS metadata type to Oracle type mapping."""
        # Test basic WMS metadata mappings
        assert WMS_METADATA_TO_ORACLE["pk"] == "NUMBER"
        assert WMS_METADATA_TO_ORACLE["varchar"] == "VARCHAR2(255 CHAR)"
        assert WMS_METADATA_TO_ORACLE["number"] == "NUMBER"
        assert WMS_METADATA_TO_ORACLE["datetime"] == "TIMESTAMP(6)"
        assert WMS_METADATA_TO_ORACLE["boolean"] == "NUMBER(1,0)"
        assert WMS_METADATA_TO_ORACLE["text"] == "VARCHAR2(4000 CHAR)"
        assert WMS_METADATA_TO_ORACLE["clob"] == "CLOB"

    def test_field_patterns_to_oracle_mapping(self) -> None:
        """Test field pattern to Oracle type mapping."""
        # Test pattern mappings
        assert FIELD_PATTERNS_TO_ORACLE["id_patterns"] == "NUMBER"
        assert FIELD_PATTERNS_TO_ORACLE["key_patterns"] == "VARCHAR2(255 CHAR)"
        assert FIELD_PATTERNS_TO_ORACLE["qty_patterns"] == "NUMBER"
        assert FIELD_PATTERNS_TO_ORACLE["date_patterns"] == "TIMESTAMP(6)"
        assert FIELD_PATTERNS_TO_ORACLE["flag_patterns"] == "NUMBER(1,0)"
        assert FIELD_PATTERNS_TO_ORACLE["set_patterns"] == "VARCHAR2(4000 CHAR)"

    def test_field_pattern_rules_structure(self) -> None:
        """Test field pattern rules structure."""
        # Test that pattern rules contain expected patterns
        assert "*_id" in FIELD_PATTERN_RULES["id_patterns"]
        assert "id" in FIELD_PATTERN_RULES["id_patterns"]
        assert "*_qty" in FIELD_PATTERN_RULES["qty_patterns"]
        assert "*_date" in FIELD_PATTERN_RULES["date_patterns"]
        assert "*_flg" in FIELD_PATTERN_RULES["flag_patterns"]
        assert "*_set" in FIELD_PATTERN_RULES["set_patterns"]

    def test_convert_field_pattern_to_oracle(self) -> None:
        """Test field pattern to Oracle type conversion."""
        # Test ID patterns
        result = convert_field_pattern_to_oracle("customer_id")
        assert result == "NUMBER"

        result = convert_field_pattern_to_oracle("id")
        assert result == "NUMBER"

        # Test quantity patterns
        result = convert_field_pattern_to_oracle("alloc_qty")
        assert result == "NUMBER"

        result = convert_field_pattern_to_oracle("order_quantity")
        assert result == "NUMBER"

        # Test date patterns
        result = convert_field_pattern_to_oracle("created_date")
        assert result == "TIMESTAMP(6)"

        result = convert_field_pattern_to_oracle("modified_time")
        assert result == "TIMESTAMP(6)"

        # Test flag patterns
        result = convert_field_pattern_to_oracle("active_flg")
        assert result == "NUMBER(1,0)"

        result = convert_field_pattern_to_oracle("enabled_flag")
        assert result == "NUMBER(1,0)"

        # Test set patterns (always 4000 CHAR)
        result = convert_field_pattern_to_oracle("permissions_set")
        assert result == "VARCHAR2(4000 CHAR)"

        # Test no pattern match
        result = convert_field_pattern_to_oracle("random_field")
        assert result is None

    def test_convert_field_pattern_to_oracle_with_max_length(self) -> None:
        """Test field pattern conversion with max length override."""
        # Test VARCHAR2 with max length
        result = convert_field_pattern_to_oracle("customer_key", max_length=100)
        assert result == "VARCHAR2(100 CHAR)"

        # Test set patterns ignore max_length
        result = convert_field_pattern_to_oracle("permissions_set", max_length=100)
        assert result == "VARCHAR2(4000 CHAR)"  # Should still be 4000 CHAR

        # Test max_length capped at 4000
        result = convert_field_pattern_to_oracle("description_desc", max_length=5000)
        assert result == "VARCHAR2(4000 CHAR)"

    def test_convert_field_to_oracle_new_with_metadata_type(self) -> None:
        """Test field conversion with WMS metadata type."""
        # Test metadata type priority
        result = convert_field_to_oracle_new(metadata_type="pk")
        assert result == "NUMBER"

        result = convert_field_to_oracle_new(metadata_type="varchar")
        assert result == "VARCHAR2(255 CHAR)"

        result = convert_field_to_oracle_new(metadata_type="boolean")
        assert result == "NUMBER(1,0)"

        # Test metadata type with max_length override
        result = convert_field_to_oracle_new(metadata_type="varchar", max_length=500)
        assert result == "VARCHAR2(500 CHAR)"

    def test_convert_field_to_oracle_new_with_column_name_pattern(self) -> None:
        """Test field conversion using column name patterns."""
        # Test pattern matching when no metadata type
        result = convert_field_to_oracle_new(column_name="customer_id")
        assert result == "NUMBER"

        result = convert_field_to_oracle_new(column_name="order_qty")
        assert result == "NUMBER"

        result = convert_field_to_oracle_new(column_name="created_date")
        assert result == "TIMESTAMP(6)"

    def test_convert_field_to_oracle_new_with_sample_value(self) -> None:
        """Test field conversion using sample value inference."""
        # Test string sample
        result = convert_field_to_oracle_new(sample_value="test string")
        assert "VARCHAR2" in result

        # Test number samples
        result = convert_field_to_oracle_new(sample_value=123)
        assert result == "NUMBER"

        result = convert_field_to_oracle_new(sample_value=123.45)
        assert result == "NUMBER"

        # Test boolean sample
        result = convert_field_to_oracle_new(sample_value=True)
        assert result == "NUMBER(1,0)"

    def test_convert_field_to_oracle_new_priority_order(self) -> None:
        """Test that conversion follows correct priority order."""
        # Metadata type should override pattern
        result = convert_field_to_oracle_new(
            metadata_type="clob",
            column_name="customer_id",  # This would normally be NUMBER
            sample_value="short string",
        )
        assert result == "CLOB"

        # Pattern should override sample value
        result = convert_field_to_oracle_new(
            column_name="customer_id",  # This should be NUMBER
            sample_value="not a number",  # This would normally be VARCHAR2
        )
        assert result == "NUMBER"

    def test_convert_singer_schema_to_oracle(self) -> None:
        """Test Singer schema to Oracle type conversion."""
        # Test string type
        result = convert_singer_schema_to_oracle("name", {"type": "string"})
        assert "VARCHAR2" in result

        # Test string with maxLength
        result = convert_singer_schema_to_oracle(
            "description",
            {"type": "string", "maxLength": 500},
        )
        assert result == "VARCHAR2(500 CHAR)"

        # Test integer type
        result = convert_singer_schema_to_oracle("count", {"type": "integer"})
        assert result == "NUMBER"

        # Test number type
        result = convert_singer_schema_to_oracle("price", {"type": "number"})
        assert result == "NUMBER"

        # Test boolean type
        result = convert_singer_schema_to_oracle("active", {"type": "boolean"})
        assert result == "NUMBER(1,0)"

        # Test date-time format
        result = convert_singer_schema_to_oracle(
            "created_at",
            {"type": "string", "format": "date-time"},
        )
        assert result == "TIMESTAMP(6)"

        # Test nullable type array
        result = convert_singer_schema_to_oracle(
            "optional_field",
            {"type": ["string", "null"]},
        )
        assert "VARCHAR2" in result

    def test_convert_singer_schema_to_oracle_with_patterns(self) -> None:
        """Test Singer schema conversion with field pattern recognition."""
        # Pattern should override Singer type inference
        result = convert_singer_schema_to_oracle("customer_id", {"type": "string"})
        assert result == "NUMBER"  # ID pattern overrides string type

        result = convert_singer_schema_to_oracle("allocation_qty", {"type": "string"})
        assert result == "NUMBER"  # Quantity pattern overrides string type

    def test_oracle_ddl_from_singer_schema(self) -> None:
        """Test Oracle DDL generation from Singer schema."""
        # Test basic schema
        schema = {"type": "string", "maxLength": 100}
        result = oracle_ddl_from_singer_schema(schema, "customer_name")
        assert "VARCHAR2" in result

        # Test schema with WMS metadata
        schema = {"type": "string", "x-wms-metadata": {"original_metadata_type": "pk"}}
        result = oracle_ddl_from_singer_schema(schema, "id")
        assert result == "NUMBER"

        # Test schema with max length override
        schema = {
            "type": "string",
            "maxLength": 200,
            "x-wms-metadata": {"original_metadata_type": "varchar"},
        }
        result = oracle_ddl_from_singer_schema(schema, "description")
        assert result == "VARCHAR2(200 CHAR)"

    def test_edge_cases_and_defaults(self) -> None:
        """Test edge cases and default behavior."""
        # Test empty/None inputs
        result = convert_field_to_oracle_new()
        assert result == "VARCHAR2(255 CHAR)"  # Default fallback

        result = convert_field_to_oracle_new(
            metadata_type="",
            column_name="",
            sample_value=None,
        )
        assert result == "VARCHAR2(255 CHAR)"  # Default fallback

        # Test unknown metadata type
        result = convert_field_to_oracle_new(metadata_type="unknown_type")
        assert result == "VARCHAR2(255 CHAR)"  # Should fall back to default

    def test_case_insensitive_pattern_matching(self) -> None:
        """Test that pattern matching is case insensitive."""
        # Test uppercase
        result = convert_field_pattern_to_oracle("CUSTOMER_ID")
        assert result == "NUMBER"

        # Test mixed case
        result = convert_field_pattern_to_oracle("Customer_Id")
        assert result == "NUMBER"

        # Test with metadata type (should be case insensitive)
        result = convert_field_to_oracle_new(metadata_type="VARCHAR")
        assert result == "VARCHAR2(255 CHAR)"

        result = convert_field_to_oracle_new(metadata_type="Varchar")
        assert result == "VARCHAR2(255 CHAR)"

    def test_complex_field_patterns(self) -> None:
        """Test complex field pattern matching."""
        # Test multiple underscores
        result = convert_field_pattern_to_oracle("cust_order_id")
        assert result == "NUMBER"

        # Test compound patterns
        result = convert_field_pattern_to_oracle("total_orig_ord_qty")
        assert result == "NUMBER"  # Should match qty pattern

        # Test date patterns with prefixes
        result = convert_field_pattern_to_oracle("cust_date_1")
        assert result == "TIMESTAMP(6)"

    def test_max_length_constraints(self) -> None:
        """Test max length constraint handling."""
        # Test length capping at 4000
        result = convert_field_to_oracle_new(metadata_type="varchar", max_length=5000)
        assert result == "VARCHAR2(4000 CHAR)"

        # Test reasonable length
        result = convert_field_to_oracle_new(metadata_type="varchar", max_length=500)
        assert result == "VARCHAR2(500 CHAR)"

        # Test zero or negative length (should use default)
        result = convert_field_to_oracle_new(metadata_type="varchar", max_length=0)
        assert result == "VARCHAR2(255 CHAR)"

    def test_sample_value_type_inference(self) -> None:
        """Test type inference from sample values."""
        # Test different string patterns
        result = convert_field_to_oracle_new(sample_value="2024-01-15")
        assert result == "TIMESTAMP(6)"  # Date-like string

        result = convert_field_to_oracle_new(sample_value="2024-01-15T10:30:00")
        assert result == "TIMESTAMP(6)"  # Datetime-like string

        result = convert_field_to_oracle_new(sample_value="01/15/2024")
        assert result == "TIMESTAMP(6)"  # US date format

        # Test numeric strings
        result = convert_field_to_oracle_new(sample_value="123")
        assert "VARCHAR2" in result  # String representation, not numeric

        # Test different sample types
        result = convert_field_to_oracle_new(sample_value=42.5)
        assert result == "NUMBER"

        result = convert_field_to_oracle_new(sample_value=False)
        assert result == "NUMBER(1,0)"
