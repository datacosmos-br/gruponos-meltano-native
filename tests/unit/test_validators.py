"""Unit tests for validation functionality."""

from decimal import Decimal
from typing import Any

from gruponos_meltano_native.validators.data_validator import (
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

        assert rule.field_name == "test_field"
        assert rule.rule_type == "required"
        assert rule.parameters == {}

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
        assert len(validator.rules) == 2
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
        assert any("required_field" in str(error) for error in errors)

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
        assert len(errors) == 0

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
        assert len(errors) == 0

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
        assert len(errors) == 0

    def test_validation_error(self) -> None:
        """Test ValidationError exception."""
        error = ValidationError("Test validation error", "test_field")

        assert str(error) == "Test validation error"
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
        assert len(validator.rules) == 3

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
        assert len(errors) == 0

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
        assert len(errors) == 0

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
        assert len(errors) == 0
