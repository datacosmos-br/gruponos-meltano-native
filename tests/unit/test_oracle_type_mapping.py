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
        if WMS_METADATA_TO_ORACLE["pk"] != "NUMBER":
            raise AssertionError(f"Expected {"NUMBER"}, got {WMS_METADATA_TO_ORACLE["pk"]}")
        assert WMS_METADATA_TO_ORACLE["varchar"] == "VARCHAR2(255 CHAR)"
        if WMS_METADATA_TO_ORACLE["number"] != "NUMBER":
            raise AssertionError(f"Expected {"NUMBER"}, got {WMS_METADATA_TO_ORACLE["number"]}")
        assert WMS_METADATA_TO_ORACLE["datetime"] == "TIMESTAMP(6)"
        if WMS_METADATA_TO_ORACLE["boolean"] != "NUMBER(1,0)":
            raise AssertionError(f"Expected {"NUMBER(1,0)"}, got {WMS_METADATA_TO_ORACLE["boolean"]}")
        assert WMS_METADATA_TO_ORACLE["text"] == "VARCHAR2(4000 CHAR)"
        if WMS_METADATA_TO_ORACLE["clob"] != "CLOB":
            raise AssertionError(f"Expected {"CLOB"}, got {WMS_METADATA_TO_ORACLE["clob"]}")

    def test_field_patterns_to_oracle_mapping(self) -> None:
        """Test field pattern to Oracle type mapping."""
        # Test pattern mappings
        if FIELD_PATTERNS_TO_ORACLE["id_patterns"] != "NUMBER":
            raise AssertionError(f"Expected {"NUMBER"}, got {FIELD_PATTERNS_TO_ORACLE["id_patterns"]}")
        assert FIELD_PATTERNS_TO_ORACLE["key_patterns"] == "VARCHAR2(255 CHAR)"
        if FIELD_PATTERNS_TO_ORACLE["qty_patterns"] != "NUMBER":
            raise AssertionError(f"Expected {"NUMBER"}, got {FIELD_PATTERNS_TO_ORACLE["qty_patterns"]}")
        assert FIELD_PATTERNS_TO_ORACLE["date_patterns"] == "TIMESTAMP(6)"
        if FIELD_PATTERNS_TO_ORACLE["flag_patterns"] != "NUMBER(1,0)":
            raise AssertionError(f"Expected {"NUMBER(1,0)"}, got {FIELD_PATTERNS_TO_ORACLE["flag_patterns"]}")
        assert FIELD_PATTERNS_TO_ORACLE["set_patterns"] == "VARCHAR2(4000 CHAR)"

    def test_field_pattern_rules_structure(self) -> None:
        """Test field pattern rules structure."""
        # Test that pattern rules contain expected patterns
        if "*_id" not in FIELD_PATTERN_RULES["id_patterns"]:
            raise AssertionError(f"Expected {"*_id"} in {FIELD_PATTERN_RULES["id_patterns"]}")
        assert "id" in FIELD_PATTERN_RULES["id_patterns"]
        if "*_qty" not in FIELD_PATTERN_RULES["qty_patterns"]:
            raise AssertionError(f"Expected {"*_qty"} in {FIELD_PATTERN_RULES["qty_patterns"]}")
        assert "*_date" in FIELD_PATTERN_RULES["date_patterns"]
        if "*_flg" not in FIELD_PATTERN_RULES["flag_patterns"]:
            raise AssertionError(f"Expected {"*_flg"} in {FIELD_PATTERN_RULES["flag_patterns"]}")
        assert "*_set" in FIELD_PATTERN_RULES["set_patterns"]

    def test_convert_field_pattern_to_oracle(self) -> None:
        """Test field pattern to Oracle type conversion."""
        # Test ID patterns
        result = convert_field_pattern_to_oracle("customer_id")
        if result != "NUMBER":
            raise AssertionError(f"Expected {"NUMBER"}, got {result}")

        result = convert_field_pattern_to_oracle("id")
        if result != "NUMBER":
            raise AssertionError(f"Expected {"NUMBER"}, got {result}")

        # Test quantity patterns
        result = convert_field_pattern_to_oracle("alloc_qty")
        if result != "NUMBER":
            raise AssertionError(f"Expected {"NUMBER"}, got {result}")

        result = convert_field_pattern_to_oracle("order_quantity")
        if result != "NUMBER":
            raise AssertionError(f"Expected {"NUMBER"}, got {result}")

        # Test date patterns
        result = convert_field_pattern_to_oracle("created_date")
        if result != "TIMESTAMP(6)":
            raise AssertionError(f"Expected {"TIMESTAMP(6)"}, got {result}")

        result = convert_field_pattern_to_oracle("modified_time")
        if result != "TIMESTAMP(6)":
            raise AssertionError(f"Expected {"TIMESTAMP(6)"}, got {result}")

        # Test flag patterns
        result = convert_field_pattern_to_oracle("active_flg")
        if result != "NUMBER(1,0)":
            raise AssertionError(f"Expected {"NUMBER(1,0)"}, got {result}")

        result = convert_field_pattern_to_oracle("enabled_flag")
        if result != "NUMBER(1,0)":
            raise AssertionError(f"Expected {"NUMBER(1,0)"}, got {result}")

        # Test set patterns (always 4000 CHAR)
        result = convert_field_pattern_to_oracle("permissions_set")
        if result != "VARCHAR2(4000 CHAR)":
            raise AssertionError(f"Expected {"VARCHAR2(4000 CHAR)"}, got {result}")

        # Test no pattern match
        result = convert_field_pattern_to_oracle("random_field")
        assert result is None

    def test_convert_field_pattern_to_oracle_with_max_length(self) -> None:
        """Test field pattern conversion with max length override."""
        # Test VARCHAR2 with max length
        result = convert_field_pattern_to_oracle("customer_key", max_length=100)
        if result != "VARCHAR2(100 CHAR)":
            raise AssertionError(f"Expected {"VARCHAR2(100 CHAR)"}, got {result}")

        # Test set patterns ignore max_length
        result = convert_field_pattern_to_oracle("permissions_set", max_length=100)
        if result != "VARCHAR2(4000 CHAR)"  # Should still be 4000 CHAR:
            raise AssertionError(f"Expected {"VARCHAR2(4000 CHAR)"  # Should still be 4000 CHAR}, got {result}")

        # Test max_length capped at 4000
        result = convert_field_pattern_to_oracle("description_desc", max_length=5000)
        if result != "VARCHAR2(4000 CHAR)":
            raise AssertionError(f"Expected {"VARCHAR2(4000 CHAR)"}, got {result}")

    def test_convert_field_to_oracle_new_with_metadata_type(self) -> None:
        """Test field conversion with WMS metadata type."""
        # Test metadata type priority
        result = convert_field_to_oracle_new(metadata_type="pk")
        if result != "NUMBER":
            raise AssertionError(f"Expected {"NUMBER"}, got {result}")

        result = convert_field_to_oracle_new(metadata_type="varchar")
        if result != "VARCHAR2(255 CHAR)":
            raise AssertionError(f"Expected {"VARCHAR2(255 CHAR)"}, got {result}")

        result = convert_field_to_oracle_new(metadata_type="boolean")
        if result != "NUMBER(1,0)":
            raise AssertionError(f"Expected {"NUMBER(1,0)"}, got {result}")

        # Test metadata type with max_length override
        result = convert_field_to_oracle_new(metadata_type="varchar", max_length=500)
        if result != "VARCHAR2(500 CHAR)":
            raise AssertionError(f"Expected {"VARCHAR2(500 CHAR)"}, got {result}")

    def test_convert_field_to_oracle_new_with_column_name_pattern(self) -> None:
        """Test field conversion using column name patterns."""
        # Test pattern matching when no metadata type
        result = convert_field_to_oracle_new(column_name="customer_id")
        if result != "NUMBER":
            raise AssertionError(f"Expected {"NUMBER"}, got {result}")

        result = convert_field_to_oracle_new(column_name="order_qty")
        if result != "NUMBER":
            raise AssertionError(f"Expected {"NUMBER"}, got {result}")

        result = convert_field_to_oracle_new(column_name="created_date")
        if result != "TIMESTAMP(6)":
            raise AssertionError(f"Expected {"TIMESTAMP(6)"}, got {result}")

    def test_convert_field_to_oracle_new_with_sample_value(self) -> None:
        """Test field conversion using sample value inference."""
        # Test string sample
        result = convert_field_to_oracle_new(sample_value="test string")
        if "VARCHAR2" not in result:
            raise AssertionError(f"Expected {"VARCHAR2"} in {result}")

        # Test number samples
        result = convert_field_to_oracle_new(sample_value=123)
        if result != "NUMBER":
            raise AssertionError(f"Expected {"NUMBER"}, got {result}")

        result = convert_field_to_oracle_new(sample_value=123.45)
        if result != "NUMBER":
            raise AssertionError(f"Expected {"NUMBER"}, got {result}")

        # Test boolean sample
        result = convert_field_to_oracle_new(sample_value=True)
        if result != "NUMBER(1,0)":
            raise AssertionError(f"Expected {"NUMBER(1,0)"}, got {result}")

    def test_convert_field_to_oracle_new_priority_order(self) -> None:
        """Test that conversion follows correct priority order."""
        # Metadata type should override pattern
        result = convert_field_to_oracle_new(
            metadata_type="clob",
            column_name="customer_id",  # This would normally be NUMBER
            sample_value="short string",
        )
        if result != "CLOB":
            raise AssertionError(f"Expected {"CLOB"}, got {result}")

        # Pattern should override sample value
        result = convert_field_to_oracle_new(
            column_name="customer_id",  # This should be NUMBER
            sample_value="not a number",  # This would normally be VARCHAR2
        )
        if result != "NUMBER":
            raise AssertionError(f"Expected {"NUMBER"}, got {result}")

    def test_convert_singer_schema_to_oracle(self) -> None:
        """Test Singer schema to Oracle type conversion."""
        # Test string type
        result = convert_singer_schema_to_oracle("name", {"type": "string"})
        if "VARCHAR2" not in result:
            raise AssertionError(f"Expected {"VARCHAR2"} in {result}")

        # Test string with maxLength
        result = convert_singer_schema_to_oracle(
            "description",
            {"type": "string", "maxLength": 500},
        )
        if result != "VARCHAR2(500 CHAR)":
            raise AssertionError(f"Expected {"VARCHAR2(500 CHAR)"}, got {result}")

        # Test integer type
        result = convert_singer_schema_to_oracle("count", {"type": "integer"})
        if result != "NUMBER":
            raise AssertionError(f"Expected {"NUMBER"}, got {result}")

        # Test number type
        result = convert_singer_schema_to_oracle("price", {"type": "number"})
        if result != "NUMBER":
            raise AssertionError(f"Expected {"NUMBER"}, got {result}")

        # Test boolean type
        result = convert_singer_schema_to_oracle("active", {"type": "boolean"})
        if result != "NUMBER(1,0)":
            raise AssertionError(f"Expected {"NUMBER(1,0)"}, got {result}")

        # Test date-time format
        result = convert_singer_schema_to_oracle(
            "created_at",
            {"type": "string", "format": "date-time"},
        )
        if result != "TIMESTAMP(6)":
            raise AssertionError(f"Expected {"TIMESTAMP(6)"}, got {result}")

        # Test nullable type array
        result = convert_singer_schema_to_oracle(
            "optional_field",
            {"type": ["string", "null"]},
        )
        if "VARCHAR2" not in result:
            raise AssertionError(f"Expected {"VARCHAR2"} in {result}")

    def test_convert_singer_schema_to_oracle_with_patterns(self) -> None:
        """Test Singer schema conversion with field pattern recognition."""
        # Pattern should override Singer type inference
        result = convert_singer_schema_to_oracle("customer_id", {"type": "string"})
        if result != "NUMBER"  # ID pattern overrides string type:
            raise AssertionError(f"Expected {"NUMBER"  # ID pattern overrides string type}, got {result}")

        result = convert_singer_schema_to_oracle("allocation_qty", {"type": "string"})
        if result != "NUMBER"  # Quantity pattern overrides string type:
            raise AssertionError(f"Expected {"NUMBER"  # Quantity pattern overrides string type}, got {result}")

    def test_oracle_ddl_from_singer_schema(self) -> None:
        """Test Oracle DDL generation from Singer schema."""
        # Test basic schema
        schema = {"type": "string", "maxLength": 100}
        result = oracle_ddl_from_singer_schema(schema, "customer_name")
        if "VARCHAR2" not in result:
            raise AssertionError(f"Expected {"VARCHAR2"} in {result}")

        # Test schema with WMS metadata
        schema = {"type": "string", "x-wms-metadata": {"original_metadata_type": "pk"}}
        result = oracle_ddl_from_singer_schema(schema, "id")
        if result != "NUMBER":
            raise AssertionError(f"Expected {"NUMBER"}, got {result}")

        # Test schema with max length override
        schema = {
            "type": "string",
            "maxLength": 200,
            "x-wms-metadata": {"original_metadata_type": "varchar"},
        }
        result = oracle_ddl_from_singer_schema(schema, "description")
        if result != "VARCHAR2(200 CHAR)":
            raise AssertionError(f"Expected {"VARCHAR2(200 CHAR)"}, got {result}")

    def test_edge_cases_and_defaults(self) -> None:
        """Test edge cases and default behavior."""
        # Test empty/None inputs
        result = convert_field_to_oracle_new()
        if result != "VARCHAR2(255 CHAR)"  # Default fallback:
            raise AssertionError(f"Expected {"VARCHAR2(255 CHAR)"  # Default fallback}, got {result}")

        result = convert_field_to_oracle_new(
            metadata_type="",
            column_name="",
            sample_value=None,
        )
        if result != "VARCHAR2(255 CHAR)"  # Default fallback:
            raise AssertionError(f"Expected {"VARCHAR2(255 CHAR)"  # Default fallback}, got {result}")

        # Test unknown metadata type
        result = convert_field_to_oracle_new(metadata_type="unknown_type")
        if result != "VARCHAR2(255 CHAR)"  # Should fall back to default:
            raise AssertionError(f"Expected {"VARCHAR2(255 CHAR)"  # Should fall back to default}, got {result}")

    def test_case_insensitive_pattern_matching(self) -> None:
        """Test that pattern matching is case insensitive."""
        # Test uppercase
        result = convert_field_pattern_to_oracle("CUSTOMER_ID")
        if result != "NUMBER":
            raise AssertionError(f"Expected {"NUMBER"}, got {result}")

        # Test mixed case
        result = convert_field_pattern_to_oracle("Customer_Id")
        if result != "NUMBER":
            raise AssertionError(f"Expected {"NUMBER"}, got {result}")

        # Test with metadata type (should be case insensitive)
        result = convert_field_to_oracle_new(metadata_type="VARCHAR")
        if result != "VARCHAR2(255 CHAR)":
            raise AssertionError(f"Expected {"VARCHAR2(255 CHAR)"}, got {result}")

        result = convert_field_to_oracle_new(metadata_type="Varchar")
        if result != "VARCHAR2(255 CHAR)":
            raise AssertionError(f"Expected {"VARCHAR2(255 CHAR)"}, got {result}")

    def test_complex_field_patterns(self) -> None:
        """Test complex field pattern matching."""
        # Test multiple underscores
        result = convert_field_pattern_to_oracle("cust_order_id")
        if result != "NUMBER":
            raise AssertionError(f"Expected {"NUMBER"}, got {result}")

        # Test compound patterns
        result = convert_field_pattern_to_oracle("total_orig_ord_qty")
        if result != "NUMBER"  # Should match qty pattern:
            raise AssertionError(f"Expected {"NUMBER"  # Should match qty pattern}, got {result}")

        # Test date patterns with prefixes
        result = convert_field_pattern_to_oracle("cust_date_1")
        if result != "TIMESTAMP(6)":
            raise AssertionError(f"Expected {"TIMESTAMP(6)"}, got {result}")

    def test_max_length_constraints(self) -> None:
        """Test max length constraint handling."""
        # Test length capping at 4000
        result = convert_field_to_oracle_new(metadata_type="varchar", max_length=5000)
        if result != "VARCHAR2(4000 CHAR)":
            raise AssertionError(f"Expected {"VARCHAR2(4000 CHAR)"}, got {result}")

        # Test reasonable length
        result = convert_field_to_oracle_new(metadata_type="varchar", max_length=500)
        if result != "VARCHAR2(500 CHAR)":
            raise AssertionError(f"Expected {"VARCHAR2(500 CHAR)"}, got {result}")

        # Test zero or negative length (should use default)
        result = convert_field_to_oracle_new(metadata_type="varchar", max_length=0)
        if result != "VARCHAR2(255 CHAR)":
            raise AssertionError(f"Expected {"VARCHAR2(255 CHAR)"}, got {result}")

    def test_sample_value_type_inference(self) -> None:
        """Test type inference from sample values."""
        # Test different string patterns
        result = convert_field_to_oracle_new(sample_value="2024-01-15")
        if result != "TIMESTAMP(6)"  # Date-like string:
            raise AssertionError(f"Expected {"TIMESTAMP(6)"  # Date-like string}, got {result}")

        result = convert_field_to_oracle_new(sample_value="2024-01-15T10:30:00")
        if result != "TIMESTAMP(6)"  # Datetime-like string:
            raise AssertionError(f"Expected {"TIMESTAMP(6)"  # Datetime-like string}, got {result}")

        result = convert_field_to_oracle_new(sample_value="01/15/2024")
        if result != "TIMESTAMP(6)"  # US date format:
            raise AssertionError(f"Expected {"TIMESTAMP(6)"  # US date format}, got {result}")

        # Test numeric strings
        result = convert_field_to_oracle_new(sample_value="123")
        if "VARCHAR2" not in result  # String representation, not numeric:
            raise AssertionError(f"Expected {"VARCHAR2"} in {result  # String representation, not numeric}")

        # Test different sample types
        result = convert_field_to_oracle_new(sample_value=42.5)
        if result != "NUMBER":
            raise AssertionError(f"Expected {"NUMBER"}, got {result}")

        result = convert_field_to_oracle_new(sample_value=False)
        if result != "NUMBER(1,0)":
            raise AssertionError(f"Expected {"NUMBER(1,0)"}, got {result}")
