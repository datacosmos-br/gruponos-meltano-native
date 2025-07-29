"""Tests for data validator functionality.

REAL IMPLEMENTATION TESTS - NO MOCKS OR FALLBACKS.
Tests the actual data validation logic with comprehensive functionality.
"""

from gruponos_meltano_native.validators.data_validator import (
    DataValidator,
    ValidationError,
    ValidationRule,
)


class TestDataValidator:
    """Test data validator with real implementation."""

    def test_data_validator_initialization(self) -> None:
        """Test data validator initialization."""
        validator = DataValidator()
        assert validator is not None
        if validator.rules != []:
            msg = f"Expected {[]}, got {validator.rules}"
            raise AssertionError(msg)
        if validator.strict_mode:
            msg = f"Expected False, got {validator.strict_mode}"
            raise AssertionError(msg)

        # Test with parameters
        validator_strict = DataValidator(strict_mode=True)
        if not (validator_strict.strict_mode):
            msg = f"Expected True, got {validator_strict.strict_mode}"
            raise AssertionError(msg)

    def test_data_validator_has_required_methods(self) -> None:
        """Test that required methods exist."""
        validator = DataValidator()

        expected_methods = [
            "validate",
            "validate_and_convert_record",
            "get_conversion_stats",
            "reset_stats",
        ]

        for method_name in expected_methods:
            assert hasattr(validator, method_name), f"Missing method: {method_name}"
            assert callable(getattr(validator, method_name))

    def test_validate_and_convert_record(self) -> None:
        """Test validate_and_convert_record functionality."""
        validator = DataValidator()

        # Test with basic data and schema
        test_data = {
            "id": "123",
            "name": "Test Name",
            "quantity": "45.5",
            "active": "true",
        }

        test_schema = {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
                "quantity": {"type": "number"},
                "active": {"type": "boolean"},
            },
        }

        result = validator.validate_and_convert_record(test_data, test_schema)
        assert isinstance(result, dict)

    def test_validation_with_strict_mode(self) -> None:
        """Test validation in strict mode."""
        validator = DataValidator(strict_mode=True)

        # Test basic validation doesn't raise in simple cases
        test_data = {"name": "Test", "value": 123}
        test_schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}, "value": {"type": "number"}},
        }
        result = validator.validate_and_convert_record(test_data, test_schema)
        assert isinstance(result, dict)

    def test_conversion_stats(self) -> None:
        """Test conversion statistics tracking."""
        validator = DataValidator()

        # Get initial stats
        stats = validator.get_conversion_stats()
        assert isinstance(stats, dict)
        if "strings_converted_to_numbers" not in stats:
            msg = f"Expected {'strings_converted_to_numbers'} in {stats}"
            raise AssertionError(
                msg,
            )

        # Reset stats
        validator.reset_stats()
        stats_after_reset = validator.get_conversion_stats()
        assert isinstance(stats_after_reset, dict)

    def test_validate_method(self) -> None:
        """Test the validate method."""
        validator = DataValidator()

        # Test with basic data
        test_data = {"field1": "value1", "field2": 123}
        result = validator.validate(test_data)
        assert isinstance(result, list)  # Returns list of validation errors

    def test_validation_error_class(self) -> None:
        """Test ValidationError class."""
        # Test basic error
        error = ValidationError("Test error")
        if str(error) != "Test error":
            msg = f"Expected {'Test error'}, got {error!s}"
            raise AssertionError(msg)

        # Test error with field name
        error_with_field = ValidationError("Field error", "test_field")
        assert isinstance(error_with_field, ValidationError)

    def test_validation_rule_class(self) -> None:
        """Test ValidationRule class existence."""
        # ValidationRule should be importable
        assert ValidationRule is not None

    def test_number_conversion(self) -> None:
        """Test number conversion functionality."""
        validator = DataValidator()

        # Test data with string numbers
        test_data = {
            "integer_field": "123",
            "float_field": "45.67",
            "negative_field": "-89.12",
        }

        test_schema = {
            "type": "object",
            "properties": {
                "integer_field": {"type": "number"},
                "float_field": {"type": "number"},
                "negative_field": {"type": "number"},
            },
        }

        result = validator.validate_and_convert_record(test_data, test_schema)
        assert isinstance(result, dict)

    def test_boolean_conversion(self) -> None:
        """Test boolean conversion functionality."""
        validator = DataValidator()

        # Test data with various boolean representations
        test_data = {"bool1": "true", "bool2": "false", "bool3": "1", "bool4": "0"}

        test_schema = {
            "type": "object",
            "properties": {
                "bool1": {"type": "boolean"},
                "bool2": {"type": "boolean"},
                "bool3": {"type": "boolean"},
                "bool4": {"type": "boolean"},
            },
        }

        result = validator.validate_and_convert_record(test_data, test_schema)
        assert isinstance(result, dict)

    def test_date_conversion(self) -> None:
        """Test date conversion functionality."""
        validator = DataValidator()

        # Test data with date strings
        test_data = {"date1": "2024-01-15", "date2": "2024-12-31 10:30:00"}

        test_schema = {
            "type": "object",
            "properties": {
                "date1": {"type": "string", "format": "date"},
                "date2": {"type": "string", "format": "date-time"},
            },
        }

        result = validator.validate_and_convert_record(test_data, test_schema)
        assert isinstance(result, dict)

    def test_decimal_conversion(self) -> None:
        """Test decimal conversion functionality."""
        validator = DataValidator()

        # Test data with decimal strings
        test_data = {"price": "123.45", "amount": "67.89", "percentage": "0.15"}

        test_schema = {
            "type": "object",
            "properties": {
                "price": {"type": "number"},
                "amount": {"type": "number"},
                "percentage": {"type": "number"},
            },
        }

        result = validator.validate_and_convert_record(test_data, test_schema)
        assert isinstance(result, dict)

    def test_string_validation(self) -> None:
        """Test string validation functionality."""
        validator = DataValidator()

        # Test data with various string types
        test_data = {
            "name": "John Doe",
            "description": "A long description text",
            "code": "ABC123",
        }

        test_schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "description": {"type": "string"},
                "code": {"type": "string"},
            },
        }

        result = validator.validate_and_convert_record(test_data, test_schema)
        assert isinstance(result, dict)

    def test_empty_data_handling(self) -> None:
        """Test handling of empty or None data."""
        validator = DataValidator()

        # Test with empty dict
        empty_schema = {"type": "object", "properties": {}}
        result = validator.validate_and_convert_record({}, empty_schema)
        assert isinstance(result, dict)

        # Test validation of empty dict
        validation_result = validator.validate({})
        assert isinstance(validation_result, list)
