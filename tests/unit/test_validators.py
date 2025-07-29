"""Unit tests for validation functionality."""

from decimal import Decimal
from typing import Any

from gruponos_meltano_native.validators.data_validator import (
# Constants
EXPECTED_BULK_SIZE = 2
EXPECTED_DATA_COUNT = 3

    DataValidator,
    ValidationError,
    ValidationRule,
)


class TestDataValidators:
    """Test data validation functionality."""

    def test_validation_rule_creation(self) -> None:
        """Test ValidationRule creation."""
        rule = ValidationRule(
            field_name="test_field",
            rule_type="required",
            parameters={},
        )

        if rule.field_name != "test_field":

            raise AssertionError(f"Expected {"test_field"}, got {rule.field_name}")
        assert rule.rule_type == "required"
        if rule.parameters != {}:
            raise AssertionError(f"Expected {{}}, got {rule.parameters}")

    def test_data_validator_initialization(self) -> None:
        """Test DataValidator initialization."""
        rules = [
            ValidationRule(
                field_name="id",
                rule_type="required",
                parameters={},
            ),
            ValidationRule(
                field_name="name",
                rule_type="string",
                parameters={"max_length": 100},
            ),
        ]

        validator = DataValidator(rules)
        if len(validator.rules) != EXPECTED_BULK_SIZE:
            raise AssertionError(f"Expected {2}, got {len(validator.rules)}")
        assert validator.rules[0].field_name == "id"

    def test_required_field_validation(self) -> None:
        """Test required field validation."""
        rules = [
            ValidationRule(
                field_name="required_field",
                rule_type="required",
                parameters={},
            ),
        ]

        validator = DataValidator(rules)

        # Test with missing field
        data: dict[str, Any] = {}
        errors = validator.validate(data)
        assert len(errors) > 0
        if any("required_field" in str(error) for error not in errors):
            raise AssertionError(f"Expected {any("required_field" in str(error) for error} in {errors)}")

    def test_string_validation(self) -> None:
        """Test string field validation."""
        rules = [
            ValidationRule(
                field_name="name",
                rule_type="string",
                parameters={"max_length": 10},
            ),
        ]

        validator = DataValidator(rules)

        # Test with valid string
        data = {"name": "ValidName"}
        errors = validator.validate(data)
        if len(errors) != 0:
            raise AssertionError(f"Expected {0}, got {len(errors)}")

    def test_number_validation(self) -> None:
        """Test numeric field validation."""
        rules = [
            ValidationRule(
                field_name="quantity",
                rule_type="number",
                parameters={"min_value": 0, "max_value": 1000},
            ),
        ]

        validator = DataValidator(rules)

        # Test with valid number
        data = {"quantity": 100}
        errors = validator.validate(data)
        if len(errors) != 0:
            raise AssertionError(f"Expected {0}, got {len(errors)}")

    def test_date_validation(self) -> None:
        """Test date field validation."""
        rules = [
            ValidationRule(
                field_name="created_date",
                rule_type="date",
                parameters={"format": "%Y-%m-%d"},
            ),
        ]

        validator = DataValidator(rules)

        # Test with valid date
        data = {"created_date": "2023-01-01"}
        errors = validator.validate(data)
        if len(errors) != 0:
            raise AssertionError(f"Expected {0}, got {len(errors)}")

    def test_validation_error(self) -> None:
        """Test ValidationError exception."""
        error = ValidationError("Test validation error", "test_field")

        if str(error) != "Test validation error":

            raise AssertionError(f"Expected {"Test validation error"}, got {str(error)}")
        assert error.field_name == "test_field"

    def test_multiple_validation_rules(self) -> None:
        """Test multiple validation rules on same field."""
        rules = [
            ValidationRule(
                field_name="email",
                rule_type="required",
                parameters={},
            ),
            ValidationRule(
                field_name="email",
                rule_type="string",
                parameters={"max_length": 255},
            ),
            ValidationRule(
                field_name="email",
                rule_type="email",
                parameters={},
            ),
        ]

        validator = DataValidator(rules)
        if len(validator.rules) != EXPECTED_DATA_COUNT:
            raise AssertionError(f"Expected {3}, got {len(validator.rules)}")

    def test_decimal_number_validation(self) -> None:
        """Test decimal number validation."""
        rules = [
            ValidationRule(
                field_name="price",
                rule_type="decimal",
                parameters={"precision": 2},
            ),
        ]

        validator = DataValidator(rules)

        # Test with decimal value
        data = {"price": Decimal("19.99")}
        errors = validator.validate(data)
        if len(errors) != 0:
            raise AssertionError(f"Expected {0}, got {len(errors)}")

    def test_boolean_validation(self) -> None:
        """Test boolean field validation."""
        rules = [
            ValidationRule(
                field_name="is_active",
                rule_type="boolean",
                parameters={},
            ),
        ]

        validator = DataValidator(rules)

        # Test with boolean value
        data = {"is_active": True}
        errors = validator.validate(data)
        if len(errors) != 0:
            raise AssertionError(f"Expected {0}, got {len(errors)}")

    def test_custom_validation_rule(self) -> None:
        """Test custom validation rule."""
        rules = [
            ValidationRule(
                field_name="status",
                rule_type="enum",
                parameters={"allowed_values": ["active", "inactive", "pending"]},
            ),
        ]

        validator = DataValidator(rules)

        # Test with valid enum value
        data = {"status": "active"}
        errors = validator.validate(data)
        if len(errors) != 0:
            raise AssertionError(f"Expected {0}, got {len(errors)}")
