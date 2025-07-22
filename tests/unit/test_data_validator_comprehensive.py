"""Comprehensive data validator tests targeting 100% coverage.

Tests all validation rules, conversion paths, error handling, and edge cases.
"""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Any
from unittest.mock import patch

import pytest

from gruponos_meltano_native.validators.data_validator import (
    DataValidator,
    ValidationError,
    ValidationRule,
    create_validator_for_environment,
)


class TestValidationError:
    """Test ValidationError class."""

    def test_validation_error_with_field_name(self) -> None:
        """Test ValidationError with field name."""
        error = ValidationError("Test message", "test_field")
        assert str(error) == "Test message"
        assert error.field_name == "test_field"

    def test_validation_error_without_field_name(self) -> None:
        """Test ValidationError without field name."""
        error = ValidationError("Test message")
        assert str(error) == "Test message"
        assert error.field_name is None


class TestValidationRule:
    """Test ValidationRule class."""

    def test_validation_rule_basic(self) -> None:
        """Test basic validation rule creation."""
        rule = ValidationRule("test_field", "required")

        assert rule.field_name == "test_field"
        assert rule.rule_type == "required"
        assert rule.parameters == {}
        assert rule.params == {}  # Backward compatibility

    def test_validation_rule_with_parameters_dict(self) -> None:
        """Test validation rule with parameters dictionary."""
        params = {"max_length": 100, "min_value": 0}
        rule = ValidationRule("test_field", "string", parameters=params)

        assert rule.field_name == "test_field"
        assert rule.rule_type == "string"
        assert rule.parameters == params
        assert rule.params == params

    def test_validation_rule_with_kwargs(self) -> None:
        """Test validation rule with kwargs parameters."""
        rule = ValidationRule("test_field", "number", max_value=1000, min_value=1)

        assert rule.field_name == "test_field"
        assert rule.rule_type == "number"
        assert rule.parameters == {"max_value": 1000, "min_value": 1}

    def test_validation_rule_with_parameters_and_kwargs(self) -> None:
        """Test validation rule with both parameters dict and kwargs (merged)."""
        params = {"max_length": 100}
        rule = ValidationRule("test_field", "string", parameters=params, min_length=5)

        assert rule.field_name == "test_field"
        assert rule.rule_type == "string"
        assert rule.parameters == {"max_length": 100, "min_length": 5}


class TestDataValidator:
    """Test DataValidator class."""

    def test_data_validator_initialization_defaults(self) -> None:
        """Test DataValidator initialization with defaults."""
        validator = DataValidator()

        assert validator.rules == []
        assert validator.strict_mode is False
        assert validator.conversion_stats == {
            "strings_converted_to_numbers": 0,
            "dates_normalized": 0,
            "nulls_handled": 0,
            "validation_errors": 0,
        }

    def test_data_validator_initialization_with_rules(self) -> None:
        """Test DataValidator initialization with rules."""
        rules = [ValidationRule("field1", "required")]
        validator = DataValidator(rules, strict_mode=True)

        assert validator.rules == rules
        assert validator.strict_mode is True

    def test_validate_required_field_present(self) -> None:
        """Test validation of present required field."""
        rules = [ValidationRule("name", "required")]
        validator = DataValidator(rules)

        data = {"name": "test value"}
        errors = validator.validate(data)

        assert len(errors) == 0

    def test_validate_required_field_missing_non_strict(self) -> None:
        """Test validation of missing required field in non-strict mode."""
        rules = [ValidationRule("name", "required")]
        validator = DataValidator(rules, strict_mode=False)

        data: dict[str, Any] = {}
        errors = validator.validate(data)

        assert len(errors) == 1
        assert "Required field 'name' is missing" in errors[0]

    def test_validate_required_field_missing_strict_mode(self) -> None:
        """Test validation of missing required field in strict mode."""
        rules = [ValidationRule("name", "required")]
        validator = DataValidator(rules, strict_mode=True)

        data: dict[str, Any] = {}

        with pytest.raises(ValidationError, match="Required field 'name' is missing"):
            validator.validate(data)

    def test_validate_field_not_in_data_skip(self) -> None:
        """Test validation skips fields not in data (non-required)."""
        rules = [ValidationRule("optional_field", "string")]
        validator = DataValidator(rules)

        data = {"other_field": "value"}
        errors = validator.validate(data)

        assert len(errors) == 0

    def test_validate_decimal_valid(self) -> None:
        """Test decimal validation with valid values."""
        rules = [ValidationRule("amount", "decimal")]
        validator = DataValidator(rules)

        # Test with Decimal
        data = {"amount": Decimal("123.45")}
        errors = validator.validate(data)
        assert len(errors) == 0

        # Test with string (convertible)
        data_str: dict[str, Any] = {"amount": "123.45"}
        errors = validator.validate(data_str)
        assert len(errors) == 0

    def test_validate_decimal_invalid_non_strict(self) -> None:
        """Test decimal validation with invalid value in non-strict mode."""
        rules = [ValidationRule("amount", "decimal")]
        validator = DataValidator(rules, strict_mode=False)

        data = {"amount": "invalid_decimal"}
        errors = validator.validate(data)

        assert len(errors) == 1
        assert "Field 'amount' must be a valid decimal" in errors[0]

    def test_validate_decimal_invalid_strict_mode(self) -> None:
        """Test decimal validation with invalid value in strict mode."""
        rules = [ValidationRule("amount", "decimal")]
        validator = DataValidator(rules, strict_mode=True)

        data = {"amount": "invalid_decimal"}

        with pytest.raises(ValidationError, match="Field 'amount' must be a valid decimal"):
            validator.validate(data)

    def test_validate_string_valid(self) -> None:
        """Test string validation with valid values."""
        rules = [ValidationRule("name", "string")]
        validator = DataValidator(rules)

        data = {"name": "test string"}
        errors = validator.validate(data)

        assert len(errors) == 0

    def test_validate_string_invalid_type_non_strict(self) -> None:
        """Test string validation with invalid type in non-strict mode."""
        rules = [ValidationRule("name", "string")]
        validator = DataValidator(rules, strict_mode=False)

        data = {"name": 123}  # Not a string
        errors = validator.validate(data)

        assert len(errors) == 1
        assert "Field 'name' must be a string" in errors[0]

    def test_validate_string_invalid_type_strict_mode(self) -> None:
        """Test string validation with invalid type in strict mode."""
        rules = [ValidationRule("name", "string")]
        validator = DataValidator(rules, strict_mode=True)

        data = {"name": 123}

        with pytest.raises(ValidationError, match="Field 'name' must be a string"):
            validator.validate(data)

    def test_validate_string_max_length_valid(self) -> None:
        """Test string validation with valid max length."""
        rules = [ValidationRule("name", "string", parameters={"max_length": 10})]
        validator = DataValidator(rules)

        data = {"name": "short"}
        errors = validator.validate(data)

        assert len(errors) == 0

    def test_validate_string_max_length_exceeded_non_strict(self) -> None:
        """Test string validation with exceeded max length in non-strict mode."""
        rules = [ValidationRule("name", "string", parameters={"max_length": 5})]
        validator = DataValidator(rules, strict_mode=False)

        data = {"name": "very long string"}
        errors = validator.validate(data)

        assert len(errors) == 1
        assert "Field 'name' exceeds maximum length 5" in errors[0]

    def test_validate_string_max_length_exceeded_strict_mode(self) -> None:
        """Test string validation with exceeded max length in strict mode."""
        rules = [ValidationRule("name", "string", parameters={"max_length": 5})]
        validator = DataValidator(rules, strict_mode=True)

        data = {"name": "very long string"}

        with pytest.raises(ValidationError, match="Field 'name' exceeds maximum length 5"):
            validator.validate(data)

    def test_validate_number_valid(self) -> None:
        """Test number validation with valid values."""
        rules = [ValidationRule("count", "number")]
        validator = DataValidator(rules)

        # Test with int
        data = {"count": 42}
        errors = validator.validate(data)
        assert len(errors) == 0

        # Test with float
        data_float: dict[str, Any] = {"count": 42.5}
        errors = validator.validate(data_float)
        assert len(errors) == 0

    def test_validate_number_invalid_type_non_strict(self) -> None:
        """Test number validation with invalid type in non-strict mode."""
        rules = [ValidationRule("count", "number")]
        validator = DataValidator(rules, strict_mode=False)

        data = {"count": "not a number"}
        errors = validator.validate(data)

        assert len(errors) == 1
        assert "Field 'count' must be a number" in errors[0]

    def test_validate_number_invalid_type_strict_mode(self) -> None:
        """Test number validation with invalid type in strict mode."""
        rules = [ValidationRule("count", "number")]
        validator = DataValidator(rules, strict_mode=True)

        data = {"count": "not a number"}

        with pytest.raises(ValidationError, match="Field 'count' must be a number"):
            validator.validate(data)

    def test_validate_number_min_value_valid(self) -> None:
        """Test number validation with valid min value."""
        rules = [ValidationRule("count", "number", min_value=0)]
        validator = DataValidator(rules)

        data = {"count": 10}
        errors = validator.validate(data)

        assert len(errors) == 0

    def test_validate_number_below_min_value_non_strict(self) -> None:
        """Test number validation below min value in non-strict mode."""
        rules = [ValidationRule("count", "number", min_value=5)]
        validator = DataValidator(rules, strict_mode=False)

        data = {"count": 3}
        errors = validator.validate(data)

        assert len(errors) == 1
        assert "Field 'count' below minimum value 5" in errors[0]

    def test_validate_number_below_min_value_strict_mode(self) -> None:
        """Test number validation below min value in strict mode."""
        rules = [ValidationRule("count", "number", min_value=5)]
        validator = DataValidator(rules, strict_mode=True)

        data = {"count": 3}

        with pytest.raises(ValidationError, match="Field 'count' below minimum value 5"):
            validator.validate(data)

    def test_validate_number_max_value_valid(self) -> None:
        """Test number validation with valid max value."""
        rules = [ValidationRule("count", "number", max_value=100)]
        validator = DataValidator(rules)

        data = {"count": 50}
        errors = validator.validate(data)

        assert len(errors) == 0

    def test_validate_number_above_max_value_non_strict(self) -> None:
        """Test number validation above max value in non-strict mode."""
        rules = [ValidationRule("count", "number", max_value=10)]
        validator = DataValidator(rules, strict_mode=False)

        data = {"count": 15}
        errors = validator.validate(data)

        assert len(errors) == 1
        assert "Field 'count' exceeds maximum value 10" in errors[0]

    def test_validate_number_above_max_value_strict_mode(self) -> None:
        """Test number validation above max value in strict mode."""
        rules = [ValidationRule("count", "number", max_value=10)]
        validator = DataValidator(rules, strict_mode=True)

        data = {"count": 15}

        with pytest.raises(ValidationError, match="Field 'count' exceeds maximum value 10"):
            validator.validate(data)

    def test_validate_date_string_valid(self) -> None:
        """Test date validation with valid string date."""
        rules = [ValidationRule("created_date", "date")]
        validator = DataValidator(rules)

        data = {"created_date": "2025-01-15"}
        errors = validator.validate(data)

        assert len(errors) == 0

    def test_validate_date_string_custom_format(self) -> None:
        """Test date validation with custom format."""
        rules = [ValidationRule("created_date", "date", format="%m/%d/%Y")]
        validator = DataValidator(rules)

        data = {"created_date": "01/15/2025"}
        errors = validator.validate(data)

        assert len(errors) == 0

    def test_validate_date_string_invalid_format_non_strict(self) -> None:
        """Test date validation with invalid format in non-strict mode."""
        rules = [ValidationRule("created_date", "date")]
        validator = DataValidator(rules, strict_mode=False)

        data = {"created_date": "invalid-date"}
        errors = validator.validate(data)

        assert len(errors) == 1
        assert "Field 'created_date' is not a valid date format %Y-%m-%d" in errors[0]

    def test_validate_date_string_invalid_format_strict_mode(self) -> None:
        """Test date validation with invalid format in strict mode."""
        rules = [ValidationRule("created_date", "date")]
        validator = DataValidator(rules, strict_mode=True)

        data = {"created_date": "invalid-date"}

        with pytest.raises(ValidationError, match="Field 'created_date' is not a valid date format"):
            validator.validate(data)

    def test_validate_date_datetime_object_valid(self) -> None:
        """Test date validation with datetime object."""
        rules = [ValidationRule("created_date", "date")]
        validator = DataValidator(rules)

        data = {"created_date": datetime(2025, 1, 15, tzinfo=UTC)}
        errors = validator.validate(data)

        assert len(errors) == 0

    def test_validate_date_invalid_type_non_strict(self) -> None:
        """Test date validation with invalid type in non-strict mode."""
        rules = [ValidationRule("created_date", "date")]
        validator = DataValidator(rules, strict_mode=False)

        data = {"created_date": 123}  # Not a date or string
        errors = validator.validate(data)

        assert len(errors) == 1
        assert "Field 'created_date' must be a valid date" in errors[0]

    def test_validate_date_invalid_type_strict_mode(self) -> None:
        """Test date validation with invalid type in strict mode."""
        rules = [ValidationRule("created_date", "date")]
        validator = DataValidator(rules, strict_mode=True)

        data = {"created_date": 123}

        with pytest.raises(ValidationError, match="Field 'created_date' must be a valid date"):
            validator.validate(data)

    def test_validate_boolean_valid(self) -> None:
        """Test boolean validation with valid values."""
        rules = [ValidationRule("active", "boolean")]
        validator = DataValidator(rules)

        data = {"active": True}
        errors = validator.validate(data)
        assert len(errors) == 0

        data = {"active": False}
        errors = validator.validate(data)
        assert len(errors) == 0

    def test_validate_boolean_invalid_type_non_strict(self) -> None:
        """Test boolean validation with invalid type in non-strict mode."""
        rules = [ValidationRule("active", "boolean")]
        validator = DataValidator(rules, strict_mode=False)

        data = {"active": "not a boolean"}
        errors = validator.validate(data)

        assert len(errors) == 1
        assert "Field 'active' must be a boolean" in errors[0]

    def test_validate_boolean_invalid_type_strict_mode(self) -> None:
        """Test boolean validation with invalid type in strict mode."""
        rules = [ValidationRule("active", "boolean")]
        validator = DataValidator(rules, strict_mode=True)

        data = {"active": "not a boolean"}

        with pytest.raises(ValidationError, match="Field 'active' must be a boolean"):
            validator.validate(data)

    def test_validate_email_valid(self) -> None:
        """Test email validation with valid email addresses."""
        rules = [ValidationRule("email", "email")]
        validator = DataValidator(rules)

        valid_emails = [
            "test@example.com",
            "user.name@domain.org",
            "user+tag@domain.co.uk",
            "123@domain123.com",
        ]

        for email in valid_emails:
            data = {"email": email}
            errors = validator.validate(data)
            assert len(errors) == 0, f"Email {email} should be valid"

    def test_validate_email_invalid_non_strict(self) -> None:
        """Test email validation with invalid emails in non-strict mode."""
        rules = [ValidationRule("email", "email")]
        validator = DataValidator(rules, strict_mode=False)

        invalid_emails = [
            "invalid",
            "invalid@",
            "@invalid.com",
            "invalid@.com",
            "invalid.com",
            123,  # Not a string
        ]

        for email in invalid_emails:
            data = {"email": email}
            errors = validator.validate(data)
            assert len(errors) == 1, f"Email {email} should be invalid"
            assert "Field 'email' must be a valid email address" in errors[0]

    def test_validate_email_invalid_strict_mode(self) -> None:
        """Test email validation with invalid email in strict mode."""
        rules = [ValidationRule("email", "email")]
        validator = DataValidator(rules, strict_mode=True)

        data = {"email": "invalid-email"}

        with pytest.raises(ValidationError, match="Field 'email' must be a valid email address"):
            validator.validate(data)

    def test_validate_enum_valid(self) -> None:
        """Test enum validation with valid values."""
        allowed_values = ["active", "inactive", "pending"]
        rules = [ValidationRule("status", "enum", allowed_values=allowed_values)]
        validator = DataValidator(rules)

        for value in allowed_values:
            data = {"status": value}
            errors = validator.validate(data)
            assert len(errors) == 0, f"Status {value} should be valid"

    def test_validate_enum_invalid_non_strict(self) -> None:
        """Test enum validation with invalid value in non-strict mode."""
        allowed_values = ["active", "inactive", "pending"]
        rules = [ValidationRule("status", "enum", allowed_values=allowed_values)]
        validator = DataValidator(rules, strict_mode=False)

        data = {"status": "invalid_status"}
        errors = validator.validate(data)

        assert len(errors) == 1
        assert "Field 'status' must be one of ['active', 'inactive', 'pending']" in errors[0]

    def test_validate_enum_invalid_strict_mode(self) -> None:
        """Test enum validation with invalid value in strict mode."""
        allowed_values = ["active", "inactive"]
        rules = [ValidationRule("status", "enum", allowed_values=allowed_values)]
        validator = DataValidator(rules, strict_mode=True)

        data = {"status": "invalid_status"}

        with pytest.raises(ValidationError, match="Field 'status' must be one of"):
            validator.validate(data)

    def test_validate_unknown_rule_type_ignored(self) -> None:
        """Test that unknown rule types are ignored."""
        rules = [ValidationRule("field", "unknown_rule_type")]
        validator = DataValidator(rules)

        data = {"field": "any value"}
        errors = validator.validate(data)

        # Unknown rule types should be ignored without error
        assert len(errors) == 0

    def test_validate_null_value_skipped(self) -> None:
        """Test that null values are skipped for validation."""
        rules = [ValidationRule("optional_field", "string")]
        validator = DataValidator(rules)

        data = {"optional_field": None}
        errors = validator.validate(data)

        # None values should be skipped
        assert len(errors) == 0


class TestRecordValidationAndConversion:
    """Test record validation and conversion functionality."""

    def test_validate_and_convert_record_no_schema_properties(self) -> None:
        """Test record conversion with no schema properties."""
        validator = DataValidator()

        record = {"field1": "value1", "field2": "value2"}
        schema: dict[str, Any] = {}  # No properties

        result = validator.validate_and_convert_record(record, schema)

        assert result == record  # Should return unchanged

    def test_validate_and_convert_record_basic(self) -> None:
        """Test basic record conversion."""
        validator = DataValidator()

        record = {"name": "test", "age": "25", "active": True}
        schema = {
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
                "active": {"type": "boolean"},
            },
        }

        result = validator.validate_and_convert_record(record, schema)

        assert result["name"] == "test"
        assert result["age"] == 25
        assert result["active"] is True

    def test_validate_and_convert_record_unknown_fields_preserved(self) -> None:
        """Test that unknown fields are passed through unchanged."""
        validator = DataValidator()

        record = {"known_field": "value", "unknown_field": "preserve_me"}
        schema = {
            "properties": {
                "known_field": {"type": "string"},
            },
        }

        result = validator.validate_and_convert_record(record, schema)

        assert result["known_field"] == "value"
        assert result["unknown_field"] == "preserve_me"

    def test_convert_field_null_and_empty_values(self) -> None:
        """Test field conversion with null and empty values."""
        validator = DataValidator()

        field_schema = {"type": "string"}

        # Test None
        result = validator._convert_field(
            value=None,
            field_schema=field_schema,
            field_name="test_field",
        )
        assert result is None
        assert validator.conversion_stats["nulls_handled"] == 1

        # Test empty string
        result = validator._convert_field(
            value="",
            field_schema=field_schema,
            field_name="test_field",
        )
        assert result is None
        assert validator.conversion_stats["nulls_handled"] == 2

    def test_convert_field_nullable_type_array(self) -> None:
        """Test field conversion with nullable type array."""
        validator = DataValidator()

        field_schema = {"type": ["string", "null"]}

        result = validator._convert_field(
            value="test_value",
            field_schema=field_schema,
            field_name="test_field",
        )

        assert result == "test_value"

    def test_convert_field_only_null_type_defaults_to_string(self) -> None:
        """Test field conversion with only null type defaults to string."""
        validator = DataValidator()

        field_schema = {"type": ["null"]}

        result = validator._convert_field(
            value="test_value",
            field_schema=field_schema,
            field_name="test_field",
        )

        assert result == "test_value"

    def test_convert_field_number_type(self) -> None:
        """Test field conversion for number type."""
        validator = DataValidator()

        field_schema = {"type": "number"}

        # String to number
        result = validator._convert_field(
            value="123.45",
            field_schema=field_schema,
            field_name="test_field",
        )
        assert result == 123.45
        assert validator.conversion_stats["strings_converted_to_numbers"] == 1

    def test_convert_field_integer_type(self) -> None:
        """Test field conversion for integer type."""
        validator = DataValidator()

        field_schema = {"type": "integer"}

        # String to integer
        result = validator._convert_field(
            value="42",
            field_schema=field_schema,
            field_name="test_field",
        )
        assert result == 42
        assert validator.conversion_stats["strings_converted_to_numbers"] == 1

    def test_convert_field_boolean_type(self) -> None:
        """Test field conversion for boolean type."""
        validator = DataValidator()

        field_schema = {"type": "boolean"}

        result = validator._convert_field(
            value="true",
            field_schema=field_schema,
            field_name="test_field",
        )

        assert result is True

    def test_convert_field_date_format(self) -> None:
        """Test field conversion for date format."""
        validator = DataValidator()

        field_schema = {"type": "string", "format": "date"}

        result = validator._convert_field(
            value="2025-01-15",
            field_schema=field_schema,
            field_name="test_field",
        )

        assert result == "2025-01-15"
        assert validator.conversion_stats["dates_normalized"] == 1

    def test_convert_field_date_time_format(self) -> None:
        """Test field conversion for date-time format."""
        validator = DataValidator()

        field_schema = {"type": "string", "format": "date-time"}

        result = validator._convert_field(
            value="2025-01-15T10:00:00",
            field_schema=field_schema,
            field_name="test_field",
        )

        assert result == "2025-01-15T10:00:00"
        assert validator.conversion_stats["dates_normalized"] == 1

    def test_convert_field_string_default(self) -> None:
        """Test field conversion defaults to string."""
        validator = DataValidator()

        field_schema = {"type": "string"}

        result = validator._convert_field(
            value=123,
            field_schema=field_schema,
            field_name="test_field",
        )

        assert result == "123"

    def test_convert_field_conversion_error(self) -> None:
        """Test field conversion error handling."""
        validator = DataValidator()

        field_schema = {"type": "integer"}

        with pytest.raises(ValueError, match="Failed to convert field 'test_field'"):
            validator._convert_field(
                value="not a number",
                field_schema=field_schema,
                field_name="test_field",
            )

        assert validator.conversion_stats["validation_errors"] == 1


class TestNumberConversion:
    """Test number conversion functionality."""

    def test_convert_to_number_already_number(self) -> None:
        """Test converting number that's already a number."""
        validator = DataValidator()

        # Integer
        result = validator._convert_to_number(42, "integer", "test_field")
        assert result == 42

        # Float
        result = validator._convert_to_number(42.5, "number", "test_field")
        assert result == 42.5

    def test_convert_to_number_string_input(self) -> None:
        """Test converting string to number."""
        validator = DataValidator()

        result = validator._convert_to_number("123", "integer", "test_field")
        assert result == 123

    def test_convert_to_number_other_types(self) -> None:
        """Test converting other types to number."""
        validator = DataValidator()

        # None
        result = validator._convert_other_to_number(None, "integer")
        assert result is None

        # Boolean to integer
        result = validator._convert_other_to_number(True, "integer")
        assert result == 1

    def test_convert_string_to_number_cleaned(self) -> None:
        """Test string to number conversion with cleaning."""
        validator = DataValidator()

        # Test cleaning of currency and commas
        result = validator._convert_string_to_number("$1,234.56", "number")
        assert result == 1234.56
        assert validator.conversion_stats["strings_converted_to_numbers"] == 1

    def test_convert_string_to_number_empty_string(self) -> None:
        """Test string to number conversion with empty string."""
        validator = DataValidator()

        result = validator._convert_string_to_number("   ", "number")
        assert result is None

    def test_convert_string_to_number_invalid_string(self) -> None:
        """Test string to number conversion with invalid string."""
        validator = DataValidator()

        with pytest.raises(ValueError, match="Cannot convert 'invalid' to integer"):
            validator._convert_string_to_number("invalid", "integer")

    def test_clean_numeric_string(self) -> None:
        """Test numeric string cleaning."""
        validator = DataValidator()

        # Test cleaning of various formats
        assert validator._clean_numeric_string("  $1,234.56  ") == "1234.56"
        assert validator._clean_numeric_string("$123") == "123"
        assert validator._clean_numeric_string("1,000") == "1000"

    def test_convert_to_integer_decimal_handling(self) -> None:
        """Test integer conversion with decimal handling."""
        validator = DataValidator()

        # Whole number as decimal
        result = validator._convert_to_integer("42.0")
        assert result == 42
        assert validator.conversion_stats["strings_converted_to_numbers"] == 1

        # Non-whole decimal should raise error
        with pytest.raises(ValueError, match="Cannot convert decimal 42.5 to integer"):
            validator._convert_to_integer("42.5")

    def test_convert_to_integer_whole_number(self) -> None:
        """Test integer conversion with whole number string."""
        validator = DataValidator()

        result = validator._convert_to_integer("123")
        assert result == 123
        assert validator.conversion_stats["strings_converted_to_numbers"] == 1

    def test_convert_other_to_number_error(self) -> None:
        """Test error handling in other type conversion."""
        validator = DataValidator()

        with pytest.raises(ValueError, match="Cannot convert <class 'str'> 'invalid' to integer"):
            validator._convert_other_to_number("invalid", "integer")


class TestBooleanConversion:
    """Test boolean conversion functionality."""

    def test_convert_to_boolean_already_boolean(self) -> None:
        """Test converting boolean that's already boolean."""
        validator = DataValidator()

        assert validator._convert_to_boolean(value=True, _field_name="test", _strict=False) is True
        assert validator._convert_to_boolean(value=False, _field_name="test", _strict=False) is False

    def test_convert_to_boolean_string_truthy(self) -> None:
        """Test converting truthy string values to boolean."""
        validator = DataValidator()

        truthy_values = ["true", "t", "yes", "y", "1", "on", "TRUE", "True", " TRUE "]

        for value in truthy_values:
            result = validator._convert_to_boolean(value=value, _field_name="test", _strict=False)
            assert result is True, f"Value '{value}' should convert to True"

    def test_convert_to_boolean_string_falsy(self) -> None:
        """Test converting falsy string values to boolean."""
        validator = DataValidator()

        falsy_values = ["false", "f", "no", "n", "0", "off", "FALSE", "False", " FALSE "]

        for value in falsy_values:
            result = validator._convert_to_boolean(value=value, _field_name="test", _strict=False)
            assert result is False, f"Value '{value}' should convert to False"

    def test_convert_to_boolean_string_invalid(self) -> None:
        """Test converting invalid string to boolean raises error."""
        validator = DataValidator()

        with pytest.raises(ValueError, match="Cannot convert string 'maybe' to boolean"):
            validator._convert_to_boolean(value="maybe", _field_name="test", _strict=False)

    def test_convert_to_boolean_other_types(self) -> None:
        """Test converting other types to boolean."""
        validator = DataValidator()

        # Truthy values
        assert validator._convert_to_boolean(value=1, _field_name="test", _strict=False) is True
        assert validator._convert_to_boolean(value=42, _field_name="test", _strict=False) is True
        # Lists are not supported by _convert_to_boolean - test with numeric values
        assert validator._convert_to_boolean(value=1.5, _field_name="test", _strict=False) is True

        # Falsy values
        assert validator._convert_to_boolean(value=0, _field_name="test", _strict=False) is False
        assert validator._convert_to_boolean(value=0.0, _field_name="test", _strict=False) is False


class TestDateConversion:
    """Test date conversion functionality."""

    def test_convert_to_date_datetime_object(self) -> None:
        """Test converting datetime object to date string."""
        validator = DataValidator()

        dt = datetime(2025, 1, 15, 10, 30, 45)
        result = validator._convert_to_date(dt, "date-time", "test_field")

        assert result == "2025-01-15T10:30:45"
        assert validator.conversion_stats["dates_normalized"] == 1

    def test_convert_to_date_date_object(self) -> None:
        """Test converting date object to date string."""
        validator = DataValidator()

        d = date(2025, 1, 15)
        result = validator._convert_to_date(d, "date", "test_field")

        assert result == "2025-01-15"
        assert validator.conversion_stats["dates_normalized"] == 1

    def test_convert_to_date_string_iso_datetime(self) -> None:
        """Test converting ISO datetime string."""
        validator = DataValidator()

        result = validator._convert_to_date("2025-01-15T10:30:45", "date-time", "test_field")

        assert result == "2025-01-15T10:30:45"
        assert validator.conversion_stats["dates_normalized"] == 1

    def test_convert_to_date_string_iso_date(self) -> None:
        """Test converting ISO date string."""
        validator = DataValidator()

        result = validator._convert_to_date("2025-01-15", "date", "test_field")

        assert result == "2025-01-15"
        assert validator.conversion_stats["dates_normalized"] == 1

    def test_convert_to_date_string_us_format_slash(self) -> None:
        """Test converting US format date with slashes."""
        validator = DataValidator()

        result = validator._convert_to_date("01/15/2025", "date", "test_field")

        assert result == "01/15/2025"
        assert validator.conversion_stats["dates_normalized"] == 1

    def test_convert_to_date_string_us_format_dash(self) -> None:
        """Test converting US format date with dashes."""
        validator = DataValidator()

        result = validator._convert_to_date("01-15-2025", "date", "test_field")

        assert result == "01-15-2025"
        assert validator.conversion_stats["dates_normalized"] == 1

    def test_convert_to_date_string_invalid_format(self) -> None:
        """Test converting invalid date string raises error."""
        validator = DataValidator()

        with pytest.raises(ValueError, match="Cannot parse date 'invalid-date-format'"):
            validator._convert_to_date("invalid-date-format", "date", "test_field")

    def test_convert_to_date_string_whitespace_handling(self) -> None:
        """Test date conversion handles whitespace."""
        validator = DataValidator()

        result = validator._convert_to_date("  2025-01-15  ", "date", "test_field")

        assert result == "2025-01-15"
        assert validator.conversion_stats["dates_normalized"] == 1

    def test_convert_to_date_non_string_non_datetime(self) -> None:
        """Test converting non-string, non-datetime values."""
        validator = DataValidator()

        # Test invalid date string should raise ValueError
        with pytest.raises(ValueError, match="Cannot parse date '123'"):
            validator._convert_to_date("123", "date", "test_field")

        # Test None value should return None
        result = validator._convert_to_date(None, "date", "test_field")
        assert result is None


class TestStatisticsAndUtilities:
    """Test statistics and utility functions."""

    def test_get_conversion_stats(self) -> None:
        """Test getting conversion statistics."""
        validator = DataValidator()

        # Perform some conversions to update stats
        validator._convert_to_number("123", "integer", "test")
        validator._convert_to_date(datetime.now(), "date-time", "test")
        validator._convert_field(value=None, field_schema={"type": "string"}, field_name="test")

        stats = validator.get_conversion_stats()

        assert stats["strings_converted_to_numbers"] == 1
        assert stats["dates_normalized"] == 1
        assert stats["nulls_handled"] == 1
        assert stats["validation_errors"] == 0

        # Verify it's a copy
        stats["strings_converted_to_numbers"] = 999
        assert validator.conversion_stats["strings_converted_to_numbers"] == 1

    def test_reset_stats(self) -> None:
        """Test resetting conversion statistics."""
        validator = DataValidator()

        # Update stats
        validator.conversion_stats["strings_converted_to_numbers"] = 5
        validator.conversion_stats["dates_normalized"] = 3
        validator.conversion_stats["nulls_handled"] = 2
        validator.conversion_stats["validation_errors"] = 1

        # Reset
        validator.reset_stats()

        assert validator.conversion_stats["strings_converted_to_numbers"] == 0
        assert validator.conversion_stats["dates_normalized"] == 0
        assert validator.conversion_stats["nulls_handled"] == 0
        assert validator.conversion_stats["validation_errors"] == 0

    def test_create_validator_for_environment_dev(self) -> None:
        """Test creating validator for development environment."""
        validator = create_validator_for_environment("dev")

        assert isinstance(validator, DataValidator)
        assert validator.strict_mode is False

    def test_create_validator_for_environment_prod(self) -> None:
        """Test creating validator for production environment."""
        validator = create_validator_for_environment("prod")

        assert isinstance(validator, DataValidator)
        assert validator.strict_mode is True

    def test_create_validator_for_environment_default(self) -> None:
        """Test creating validator with default environment."""
        validator = create_validator_for_environment()

        assert isinstance(validator, DataValidator)
        assert validator.strict_mode is False


class TestMainExecution:
    """Test main execution path."""

    def test_main_execution_path(self) -> None:
        """Test the main execution path when module is run directly."""
        import gruponos_meltano_native.validators.data_validator

        # The actual main execution would happen here if __name__ == "__main__"
        # We're testing that the functions exist and can be called
        assert callable(gruponos_meltano_native.validators.data_validator.DataValidator)
        assert callable(gruponos_meltano_native.validators.data_validator.create_validator_for_environment)

        # Test that example code runs without error
        with patch("gruponos_meltano_native.validators.data_validator.logger"):
            validator = gruponos_meltano_native.validators.data_validator.DataValidator(strict_mode=False)

            test_record = {
                "id": "123",
                "amount": "540.50",
                "count": "42",
                "active": "true",
                "created_date": "2025-07-02T10:00:00",
            }

            test_schema = {
                "properties": {
                    "id": {"type": "integer"},
                    "amount": {"type": "number"},
                    "count": {"type": "integer"},
                    "active": {"type": "boolean"},
                    "created_date": {"type": "string", "format": "date-time"},
                },
            }

            result = validator.validate_and_convert_record(test_record, test_schema)
            stats = validator.get_conversion_stats()

            assert result["id"] == 123
            assert result["amount"] == 540.50
            assert result["count"] == 42
            assert result["active"] is True
            assert result["created_date"] == "2025-07-02T10:00:00"

            # Verify stats were updated
            assert stats["strings_converted_to_numbers"] == 3  # id, amount and count
            assert stats["dates_normalized"] == 1  # created_date
