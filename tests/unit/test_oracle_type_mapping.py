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
        expected_number = "NUMBER"
        if WMS_METADATA_TO_ORACLE["pk"] != expected_number:
            msg = f"Expected {expected_number}, got {WMS_METADATA_TO_ORACLE['pk']}"
            raise AssertionError(
                msg,
            )
        assert WMS_METADATA_TO_ORACLE["varchar"] == "VARCHAR2(255 CHAR)"
        expected_number = "NUMBER"
        if WMS_METADATA_TO_ORACLE["number"] != expected_number:
            msg = f"Expected {expected_number}, got {WMS_METADATA_TO_ORACLE['number']}"
            raise AssertionError(
                msg,
            )
        assert WMS_METADATA_TO_ORACLE["datetime"] == "TIMESTAMP(6)"
        expected_bool = "NUMBER(1,0)"
        if WMS_METADATA_TO_ORACLE["boolean"] != expected_bool:
            msg = f"Expected {expected_bool}, got {WMS_METADATA_TO_ORACLE['boolean']}"
            raise AssertionError(
                msg,
            )
        assert WMS_METADATA_TO_ORACLE["text"] == "VARCHAR2(4000 CHAR)"
        expected_clob = "CLOB"
        if WMS_METADATA_TO_ORACLE["clob"] != expected_clob:
            msg = f"Expected {expected_clob}, got {WMS_METADATA_TO_ORACLE['clob']}"
            raise AssertionError(
                msg,
            )

    def test_field_patterns_to_oracle_mapping(self) -> None:
        """Test field pattern to Oracle type mapping."""
        # Test pattern mappings
        expected_number = "NUMBER"
        if FIELD_PATTERNS_TO_ORACLE["id_patterns"] != expected_number:
            msg = f"Expected {expected_number}, got {FIELD_PATTERNS_TO_ORACLE['id_patterns']}"
            raise AssertionError(
                msg,
            )
        assert FIELD_PATTERNS_TO_ORACLE["key_patterns"] == "VARCHAR2(255 CHAR)"
        expected_number = "NUMBER"
        if FIELD_PATTERNS_TO_ORACLE["qty_patterns"] != expected_number:
            msg = f"Expected {expected_number}, got {FIELD_PATTERNS_TO_ORACLE['qty_patterns']}"
            raise AssertionError(
                msg,
            )
        assert FIELD_PATTERNS_TO_ORACLE["date_patterns"] == "TIMESTAMP(6)"
        expected_flag = "NUMBER(1,0)"
        if FIELD_PATTERNS_TO_ORACLE["flag_patterns"] != expected_flag:
            msg = f"Expected {expected_flag}, got {FIELD_PATTERNS_TO_ORACLE['flag_patterns']}"
            raise AssertionError(
                msg,
            )
        assert FIELD_PATTERNS_TO_ORACLE["set_patterns"] == "VARCHAR2(4000 CHAR)"

    def test_field_pattern_rules_structure(self) -> None:
        """Test field pattern rules structure."""
        # Test that pattern rules contain expected patterns
        expected_pattern = "*_id"
        if expected_pattern not in FIELD_PATTERN_RULES["id_patterns"]:
            msg = f"Expected {expected_pattern} in {FIELD_PATTERN_RULES['id_patterns']}"
            raise AssertionError(
                msg,
            )
        assert "id" in FIELD_PATTERN_RULES["id_patterns"]
        expected_qty = "*_qty"
        if expected_qty not in FIELD_PATTERN_RULES["qty_patterns"]:
            msg = f"Expected {expected_qty} in {FIELD_PATTERN_RULES['qty_patterns']}"
            raise AssertionError(
                msg,
            )
        assert "*_date" in FIELD_PATTERN_RULES["date_patterns"]
        expected_flg = "*_flg"
        if expected_flg not in FIELD_PATTERN_RULES["flag_patterns"]:
            msg = f"Expected {expected_flg} in {FIELD_PATTERN_RULES['flag_patterns']}"
            raise AssertionError(
                msg,
            )
        assert "*_set" in FIELD_PATTERN_RULES["set_patterns"]

    def test_convert_field_pattern_to_oracle(self) -> None:
        """Test field pattern to Oracle type conversion."""
        # Test ID patterns
        result = convert_field_pattern_to_oracle("customer_id")
        expected_number = "NUMBER"
        if result != expected_number:
            msg = f"Expected {expected_number}, got {result}"
            raise AssertionError(msg)

        result = convert_field_pattern_to_oracle("id")
        expected_number = "NUMBER"
        if result != expected_number:
            msg = f"Expected {expected_number}, got {result}"
            raise AssertionError(msg)

        # Test quantity patterns
        result = convert_field_pattern_to_oracle("alloc_qty")
        expected_number = "NUMBER"
        if result != expected_number:
            msg = f"Expected {expected_number}, got {result}"
            raise AssertionError(msg)

        result = convert_field_pattern_to_oracle("order_quantity")
        expected_number = "NUMBER"
        if result != expected_number:
            msg = f"Expected {expected_number}, got {result}"
            raise AssertionError(msg)

        # Test date patterns
        result = convert_field_pattern_to_oracle("created_date")
        expected_timestamp = "TIMESTAMP(6)"
        if result != expected_timestamp:
            msg = f"Expected {expected_timestamp}, got {result}"
            raise AssertionError(msg)

        result = convert_field_pattern_to_oracle("modified_time")
        expected_timestamp = "TIMESTAMP(6)"
        if result != expected_timestamp:
            msg = f"Expected {expected_timestamp}, got {result}"
            raise AssertionError(msg)

        # Test flag patterns
        result = convert_field_pattern_to_oracle("active_flg")
        expected_flag = "NUMBER(1,0)"
        if result != expected_flag:
            msg = f"Expected {expected_flag}, got {result}"
            raise AssertionError(msg)

        result = convert_field_pattern_to_oracle("enabled_flag")
        expected_flag = "NUMBER(1,0)"
        if result != expected_flag:
            msg = f"Expected {expected_flag}, got {result}"
            raise AssertionError(msg)

        # Test set patterns (always 4000 CHAR)
        result = convert_field_pattern_to_oracle("permissions_set")
        expected_varchar = "VARCHAR2(4000 CHAR)"
        if result != expected_varchar:
            msg = f"Expected {expected_varchar}, got {result}"
            raise AssertionError(msg)

        # Test no pattern match
        result = convert_field_pattern_to_oracle("random_field")
        assert result is None

    def test_convert_field_pattern_to_oracle_with_max_length(self) -> None:
        """Test field pattern conversion with max length override."""
        # Test VARCHAR2 with max length
        result = convert_field_pattern_to_oracle("customer_key", max_length=100)
        expected_varchar = "VARCHAR2(100 CHAR)"
        if result != expected_varchar:
            msg = f"Expected {expected_varchar}, got {result}"
            raise AssertionError(msg)

        # Test set patterns ignore max_length
        result = convert_field_pattern_to_oracle("permissions_set", max_length=100)
        expected_varchar = "VARCHAR2(4000 CHAR)"  # Should still be 4000 CHAR
        if result != expected_varchar:
            msg = f"Expected {expected_varchar}, got {result}"
            raise AssertionError(msg)

        # Test max_length capped at 4000
        result = convert_field_pattern_to_oracle("description_desc", max_length=5000)
        expected_varchar = "VARCHAR2(4000 CHAR)"
        if result != expected_varchar:
            msg = f"Expected {expected_varchar}, got {result}"
            raise AssertionError(msg)

    def test_convert_field_to_oracle_new_with_metadata_type(self) -> None:
        """Test field conversion with WMS metadata type."""
        # Test metadata type priority
        result = convert_field_to_oracle_new(metadata_type="pk")
        expected_number = "NUMBER"
        if result != expected_number:
            msg = f"Expected {expected_number}, got {result}"
            raise AssertionError(msg)

        result = convert_field_to_oracle_new(metadata_type="varchar")
        expected_varchar = "VARCHAR2(255 CHAR)"
        if result != expected_varchar:
            msg = f"Expected {expected_varchar}, got {result}"
            raise AssertionError(msg)

        result = convert_field_to_oracle_new(metadata_type="boolean")
        expected_bool = "NUMBER(1,0)"
        if result != expected_bool:
            msg = f"Expected {expected_bool}, got {result}"
            raise AssertionError(msg)

        # Test metadata type with max_length override
        result = convert_field_to_oracle_new(metadata_type="varchar", max_length=500)
        expected_varchar = "VARCHAR2(500 CHAR)"
        if result != expected_varchar:
            msg = f"Expected {expected_varchar}, got {result}"
            raise AssertionError(msg)

    def test_convert_field_to_oracle_new_with_column_name_pattern(self) -> None:
        """Test field conversion using column name patterns."""
        # Test pattern matching when no metadata type
        result = convert_field_to_oracle_new(column_name="customer_id")
        expected_number = "NUMBER"
        if result != expected_number:
            msg = f"Expected {expected_number}, got {result}"
            raise AssertionError(msg)

        result = convert_field_to_oracle_new(column_name="order_qty")
        expected_number = "NUMBER"
        if result != expected_number:
            msg = f"Expected {expected_number}, got {result}"
            raise AssertionError(msg)

        result = convert_field_to_oracle_new(column_name="created_date")
        expected_timestamp = "TIMESTAMP(6)"
        if result != expected_timestamp:
            msg = f"Expected {expected_timestamp}, got {result}"
            raise AssertionError(msg)

    def test_convert_field_to_oracle_new_with_sample_value(self) -> None:
        """Test field conversion using sample value inference."""
        # Test string sample
        result = convert_field_to_oracle_new(sample_value="test string")
        expected_varchar = "VARCHAR2"
        if expected_varchar not in result:
            msg = f"Expected {expected_varchar} in {result}"
            raise AssertionError(msg)

        # Test number samples
        result = convert_field_to_oracle_new(sample_value=123)
        expected_number = "NUMBER"
        if result != expected_number:
            msg = f"Expected {expected_number}, got {result}"
            raise AssertionError(msg)

        result = convert_field_to_oracle_new(sample_value=123.45)
        expected_number = "NUMBER"
        if result != expected_number:
            msg = f"Expected {expected_number}, got {result}"
            raise AssertionError(msg)

        # Test boolean sample
        result = convert_field_to_oracle_new(sample_value=True)
        expected_bool = "NUMBER(1,0)"
        if result != expected_bool:
            msg = f"Expected {expected_bool}, got {result}"
            raise AssertionError(msg)

    def test_convert_field_to_oracle_new_priority_order(self) -> None:
        """Test that conversion follows correct priority order."""
        # Metadata type should override pattern
        result = convert_field_to_oracle_new(
            metadata_type="clob",
            column_name="customer_id",  # This would normally be NUMBER
            sample_value="short string",
        )
        expected_clob = "CLOB"
        if result != expected_clob:
            msg = f"Expected {expected_clob}, got {result}"
            raise AssertionError(msg)

        # Pattern should override sample value
        result = convert_field_to_oracle_new(
            column_name="customer_id",  # This should be NUMBER
            sample_value="not a number",  # This would normally be VARCHAR2
        )
        expected_number = "NUMBER"
        if result != expected_number:
            msg = f"Expected {expected_number}, got {result}"
            raise AssertionError(msg)

    def test_convert_singer_schema_to_oracle(self) -> None:
        """Test Singer schema to Oracle type conversion."""
        # Test string type
        result = convert_singer_schema_to_oracle("name", {"type": "string"})
        expected_varchar = "VARCHAR2"
        if expected_varchar not in result:
            msg = f"Expected {expected_varchar} in {result}"
            raise AssertionError(msg)

        # Test string with maxLength
        result = convert_singer_schema_to_oracle(
            "description",
            {"type": "string", "maxLength": 500},
        )
        expected_varchar = "VARCHAR2(500 CHAR)"
        if result != expected_varchar:
            msg = f"Expected {expected_varchar}, got {result}"
            raise AssertionError(msg)

        # Test integer type
        result = convert_singer_schema_to_oracle("count", {"type": "integer"})
        expected_number = "NUMBER"
        if result != expected_number:
            msg = f"Expected {expected_number}, got {result}"
            raise AssertionError(msg)

        # Test number type
        result = convert_singer_schema_to_oracle("price", {"type": "number"})
        expected_number = "NUMBER"
        if result != expected_number:
            msg = f"Expected {expected_number}, got {result}"
            raise AssertionError(msg)

        # Test boolean type
        result = convert_singer_schema_to_oracle("active", {"type": "boolean"})
        expected_bool = "NUMBER(1,0)"
        if result != expected_bool:
            msg = f"Expected {expected_bool}, got {result}"
            raise AssertionError(msg)

        # Test date-time format
        result = convert_singer_schema_to_oracle(
            "created_at",
            {"type": "string", "format": "date-time"},
        )
        expected_timestamp = "TIMESTAMP(6)"
        if result != expected_timestamp:
            msg = f"Expected {expected_timestamp}, got {result}"
            raise AssertionError(msg)

        # Test nullable type array
        result = convert_singer_schema_to_oracle(
            "optional_field",
            {"type": ["string", "null"]},
        )
        expected_varchar = "VARCHAR2"
        if expected_varchar not in result:
            msg = f"Expected {expected_varchar} in {result}"
            raise AssertionError(msg)

    def test_convert_singer_schema_to_oracle_with_patterns(self) -> None:
        """Test Singer schema conversion with field pattern recognition."""
        # Pattern should override Singer type inference
        result = convert_singer_schema_to_oracle("customer_id", {"type": "string"})
        expected_number = "NUMBER"  # ID pattern overrides string type
        if result != expected_number:
            msg = f"Expected {expected_number}, got {result}"
            raise AssertionError(msg)

        result = convert_singer_schema_to_oracle("allocation_qty", {"type": "string"})
        expected_number = "NUMBER"  # Quantity pattern overrides string type
        if result != expected_number:
            msg = f"Expected {expected_number}, got {result}"
            raise AssertionError(msg)

    def test_oracle_ddl_from_singer_schema(self) -> None:
        """Test Oracle DDL generation from Singer schema."""
        # Test basic schema
        schema = {"type": "string", "maxLength": 100}
        result = oracle_ddl_from_singer_schema(schema, "customer_name")
        expected_varchar = "VARCHAR2"
        if expected_varchar not in result:
            msg = f"Expected {expected_varchar} in {result}"
            raise AssertionError(msg)

        # Test schema with WMS metadata
        schema = {"type": "string", "x-wms-metadata": {"original_metadata_type": "pk"}}
        result = oracle_ddl_from_singer_schema(schema, "id")
        expected_number = "NUMBER"
        if result != expected_number:
            msg = f"Expected {expected_number}, got {result}"
            raise AssertionError(msg)

        # Test schema with max length override
        schema = {
            "type": "string",
            "maxLength": 200,
            "x-wms-metadata": {"original_metadata_type": "varchar"},
        }
        result = oracle_ddl_from_singer_schema(schema, "description")
        expected_varchar = "VARCHAR2(200 CHAR)"
        if result != expected_varchar:
            msg = f"Expected {expected_varchar}, got {result}"
            raise AssertionError(msg)

    def test_edge_cases_and_defaults(self) -> None:
        """Test edge cases and default behavior."""
        # Test empty/None inputs
        result = convert_field_to_oracle_new()
        expected_default = "VARCHAR2(255 CHAR)"  # Default fallback
        if result != expected_default:
            msg = f"Expected {expected_default}, got {result}"
            raise AssertionError(msg)

        result = convert_field_to_oracle_new(
            metadata_type="",
            column_name="",
            sample_value=None,
        )
        expected_default = "VARCHAR2(255 CHAR)"  # Default fallback
        if result != expected_default:
            msg = f"Expected {expected_default}, got {result}"
            raise AssertionError(msg)

        # Test unknown metadata type
        result = convert_field_to_oracle_new(metadata_type="unknown_type")
        expected_default = "VARCHAR2(255 CHAR)"  # Should fall back to default
        if result != expected_default:
            msg = f"Expected {expected_default}, got {result}"
            raise AssertionError(msg)

    def test_case_insensitive_pattern_matching(self) -> None:
        """Test that pattern matching is case insensitive."""
        # Test uppercase
        result = convert_field_pattern_to_oracle("CUSTOMER_ID")
        expected_number = "NUMBER"
        if result != expected_number:
            msg = f"Expected {expected_number}, got {result}"
            raise AssertionError(msg)

        # Test mixed case
        result = convert_field_pattern_to_oracle("Customer_Id")
        expected_number = "NUMBER"
        if result != expected_number:
            msg = f"Expected {expected_number}, got {result}"
            raise AssertionError(msg)

        # Test with metadata type (should be case insensitive)
        result = convert_field_to_oracle_new(metadata_type="VARCHAR")
        expected_varchar = "VARCHAR2(255 CHAR)"
        if result != expected_varchar:
            msg = f"Expected {expected_varchar}, got {result}"
            raise AssertionError(msg)

        result = convert_field_to_oracle_new(metadata_type="Varchar")
        expected_varchar = "VARCHAR2(255 CHAR)"
        if result != expected_varchar:
            msg = f"Expected {expected_varchar}, got {result}"
            raise AssertionError(msg)

    def test_complex_field_patterns(self) -> None:
        """Test complex field pattern matching."""
        # Test multiple underscores
        result = convert_field_pattern_to_oracle("cust_order_id")
        expected_number = "NUMBER"
        if result != expected_number:
            msg = f"Expected {expected_number}, got {result}"
            raise AssertionError(msg)

        # Test compound patterns
        result = convert_field_pattern_to_oracle("total_orig_ord_qty")
        expected_number = "NUMBER"  # Should match qty pattern
        if result != expected_number:
            msg = f"Expected {expected_number}, got {result}"
            raise AssertionError(msg)

        # Test date patterns with prefixes
        result = convert_field_pattern_to_oracle("cust_date_1")
        expected_timestamp = "TIMESTAMP(6)"
        if result != expected_timestamp:
            msg = f"Expected {expected_timestamp}, got {result}"
            raise AssertionError(msg)

    def test_max_length_constraints(self) -> None:
        """Test max length constraint handling."""
        # Test length capping at 4000
        result = convert_field_to_oracle_new(metadata_type="varchar", max_length=5000)
        expected_varchar = "VARCHAR2(4000 CHAR)"
        if result != expected_varchar:
            msg = f"Expected {expected_varchar}, got {result}"
            raise AssertionError(msg)

        # Test reasonable length
        result = convert_field_to_oracle_new(metadata_type="varchar", max_length=500)
        expected_varchar = "VARCHAR2(500 CHAR)"
        if result != expected_varchar:
            msg = f"Expected {expected_varchar}, got {result}"
            raise AssertionError(msg)

        # Test zero or negative length (should use default)
        result = convert_field_to_oracle_new(metadata_type="varchar", max_length=0)
        expected_varchar = "VARCHAR2(255 CHAR)"
        if result != expected_varchar:
            msg = f"Expected {expected_varchar}, got {result}"
            raise AssertionError(msg)

    def test_sample_value_type_inference(self) -> None:
        """Test type inference from sample values."""
        # Test different string patterns
        result = convert_field_to_oracle_new(sample_value="2024-01-15")
        expected_timestamp = "TIMESTAMP(6)"  # Date-like string
        if result != expected_timestamp:
            msg = f"Expected {expected_timestamp}, got {result}"
            raise AssertionError(msg)

        result = convert_field_to_oracle_new(sample_value="2024-01-15T10:30:00")
        expected_timestamp = "TIMESTAMP(6)"  # Datetime-like string
        if result != expected_timestamp:
            msg = f"Expected {expected_timestamp}, got {result}"
            raise AssertionError(msg)

        result = convert_field_to_oracle_new(sample_value="01/15/2024")
        expected_timestamp = "TIMESTAMP(6)"  # US date format
        if result != expected_timestamp:
            msg = f"Expected {expected_timestamp}, got {result}"
            raise AssertionError(msg)

        # Test numeric strings
        result = convert_field_to_oracle_new(sample_value="123")
        expected_varchar = "VARCHAR2"  # String representation, not numeric
        if expected_varchar not in result:
            msg = f"Expected {expected_varchar} in {result}"
            raise AssertionError(msg)

        # Test different sample types
        result = convert_field_to_oracle_new(sample_value=42.5)
        expected_number = "NUMBER"
        if result != expected_number:
            msg = f"Expected {expected_number}, got {result}"
            raise AssertionError(msg)

        result = convert_field_to_oracle_new(sample_value=False)
        expected_bool = "NUMBER(1,0)"
        if result != expected_bool:
            msg = f"Expected {expected_bool}, got {result}"
            raise AssertionError(msg)
