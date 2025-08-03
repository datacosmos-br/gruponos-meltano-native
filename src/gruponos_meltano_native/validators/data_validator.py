"""Professional Data Validator for Oracle WMS Integration.

Handles type conversion and validation issues found in production.
"""

from __future__ import annotations

import re
from datetime import UTC, date, datetime
from decimal import Decimal, InvalidOperation
from typing import TYPE_CHECKING

from flext_core import get_logger

if TYPE_CHECKING:
    from collections.abc import Callable

# Use dependency injection instead of direct imports for Clean Architecture compliance

# Get dependencies via DI
logger = get_logger(__name__)


class ValidationError(Exception):
    """Custom validation error with field information."""

    def __init__(self, message: str, field_name: str | None = None) -> None:
        """Initialize validation error.

        Args:
            message: Error message
            field_name: Field that failed validation.

        """
        super().__init__(message)
        self.field_name = field_name


class ValidationRule:
    """Validation rule definition."""

    def __init__(
        self,
        field_name: str,
        rule_type: str,
        parameters: dict[str, object] | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize validation rule.

        Args:
            field_name: Field to validate
            rule_type: Type of validation (required, type, range, etc.)
            parameters: Rule parameters dictionary (optional)
            **kwargs: Additional rule parameters (merged with parameters).

        """
        self.field_name = field_name
        self.rule_type = rule_type
        # Merge explicit parameters dict with **kwargs
        self.parameters = {**(parameters or {}), **kwargs}
        self.params = self.parameters  # Keep for backward compatibility


class DataValidator:
    """Professional data validator with Oracle-specific type handling."""

    def __init__(
        self,
        rules: list[ValidationRule] | None = None,
        *,
        strict_mode: bool = False,
    ) -> None:
        """Initialize data validator.

        Args:
            rules: List of validation rules to apply
            strict_mode: Whether to raise exceptions on validation failures.

        """
        self.rules = rules or []
        self.strict_mode = strict_mode
        self.conversion_stats = {
            "strings_converted_to_numbers": 0,
            "dates_normalized": 0,
            "nulls_handled": 0,
            "validation_errors": 0,
        }

    def _validate_required_field(
        self,
        rule: ValidationRule,
        data: dict[str, object],
        errors: list[str],
    ) -> bool:
        """Validate required field presence."""
        if rule.field_name not in data and rule.rule_type == "required":
            error_msg = f"Required field '{rule.field_name}' is missing"
            if self.strict_mode:
                raise ValidationError(error_msg, rule.field_name)
            logger.warning(f"Validation failed: {error_msg} (field: {rule.field_name})")
            errors.append(error_msg)
            return False
        return True

    def _validate_field_value(
        self,
        rule: ValidationRule,
        *,
        value: str | float | bool | datetime | None,
        errors: list[str],
    ) -> None:
        """Validate field value based on rule type."""
        validation_methods: dict[
            str,
            Callable[[ValidationRule, object, list[str]], None],
        ] = {
            "decimal": self._validate_decimal,
            "string": self._validate_string,
            "number": self._validate_number,
            "date": self._validate_date,
            "boolean": self._validate_boolean,
            "email": self._validate_email,
            "enum": self._validate_enum,
        }
        validation_method = validation_methods.get(rule.rule_type)
        if validation_method is not None and value is not None:
            validation_method(rule, value, errors)

    def validate(self, data: dict[str, object]) -> list[str]:
        """Validate data against configured rules.

        Args:
            data: Data to validate
        Returns:
            List of validation error messages (empty if all validations pass)

        Raises:
            ValidationError: If validation fails in strict mode.

        """
        errors: list[str] = []
        for rule in self.rules:
            # Check required fields first
            if not self._validate_required_field(rule, data, errors):
                continue
            # Skip if field not in data
            if rule.field_name not in data:
                continue
            value = data[rule.field_name]
            self._validate_field_value(rule, value=value, errors=errors)
        return errors

    def _validate_decimal(
        self,
        rule: ValidationRule,
        value: object,
        errors: list[str],
    ) -> None:
        """Validate decimal field."""
        try:
            if not isinstance(value, Decimal):
                Decimal(str(value))
        except (ValueError, TypeError, InvalidOperation) as e:
            error_msg = f"Field '{rule.field_name}' must be a valid decimal"
            if self.strict_mode:
                raise ValidationError(error_msg, rule.field_name) from e
            logger.warning(f"Validation failed: {error_msg} (field: {rule.field_name})")
            errors.append(error_msg)

    def _validate_string(
        self,
        rule: ValidationRule,
        value: object,
        errors: list[str],
    ) -> None:
        """Validate string field."""
        if not isinstance(value, str):
            error_msg = f"Field '{rule.field_name}' must be a string"
            if self.strict_mode:
                raise ValidationError(error_msg, rule.field_name)
            logger.warning(f"Validation failed: {error_msg} (field: {rule.field_name})")
            errors.append(error_msg)
        else:
            # Check string length constraints
            max_length = rule.parameters.get("max_length")
            if max_length and len(value) > max_length:
                error_msg = (
                    f"Field '{rule.field_name}' exceeds maximum length {max_length}"
                )
                if self.strict_mode:
                    raise ValidationError(error_msg, rule.field_name)
                logger.warning(
                    f"Validation failed: {error_msg} (field: {rule.field_name})",
                )
                errors.append(error_msg)

    def _validate_number(
        self,
        rule: ValidationRule,
        value: object,
        errors: list[str],
    ) -> None:
        """Validate number field."""
        if not isinstance(value, (int, float)):
            error_msg = f"Field '{rule.field_name}' must be a number"
            if self.strict_mode:
                raise ValidationError(error_msg, rule.field_name)
            logger.warning(f"Validation failed: {error_msg} (field: {rule.field_name})")
            errors.append(error_msg)
        else:
            # Check numeric range constraints
            min_value = rule.parameters.get("min_value")
            max_value = rule.parameters.get("max_value")
            if min_value is not None and value < min_value:
                error_msg = f"Field '{rule.field_name}' below minimum value {min_value}"
                if self.strict_mode:
                    raise ValidationError(error_msg, rule.field_name)
                logger.warning(
                    f"Validation failed: {error_msg} (field: {rule.field_name})",
                )
                errors.append(error_msg)
            if max_value is not None and value > max_value:
                error_msg = (
                    f"Field '{rule.field_name}' exceeds maximum value {max_value}"
                )
                if self.strict_mode:
                    raise ValidationError(error_msg, rule.field_name)
                logger.warning(
                    f"Validation failed: {error_msg} (field: {rule.field_name})",
                )
                errors.append(error_msg)

    def _validate_date(
        self,
        rule: ValidationRule,
        value: object,
        errors: list[str],
    ) -> None:
        """Validate date field."""
        if isinstance(value, str):
            date_format = rule.parameters.get("format", "%Y-%m-%d")
            try:
                datetime.strptime(value, date_format).replace(tzinfo=UTC)
            except ValueError:
                error_msg = (
                    f"Field '{rule.field_name}' is not a valid date format "
                    f"{date_format}"
                )
                if self.strict_mode:
                    raise ValidationError(error_msg, rule.field_name) from None
                logger.warning(
                    f"Validation failed: {error_msg} (field: {rule.field_name})",
                )
                errors.append(error_msg)
        elif not isinstance(value, datetime):
            error_msg = f"Field '{rule.field_name}' must be a valid date"
            if self.strict_mode:
                raise ValidationError(error_msg, rule.field_name)
            logger.warning(f"Validation failed: {error_msg} (field: {rule.field_name})")
            errors.append(error_msg)

    def _validate_boolean(
        self,
        rule: ValidationRule,
        value: object,
        errors: list[str],
    ) -> None:
        """Validate boolean field."""
        if not isinstance(value, bool):
            error_msg = f"Field '{rule.field_name}' must be a boolean"
            if self.strict_mode:
                raise ValidationError(error_msg, rule.field_name)
            logger.warning(f"Validation failed: {error_msg} (field: {rule.field_name})")
            errors.append(error_msg)

    def _validate_email(
        self,
        rule: ValidationRule,
        value: object,
        errors: list[str],
    ) -> None:
        """Validate email field."""
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not isinstance(value, str) or not re.match(email_pattern, value):
            error_msg = f"Field '{rule.field_name}' must be a valid email address"
            if self.strict_mode:
                raise ValidationError(error_msg, rule.field_name)
            logger.warning(f"Validation failed: {error_msg} (field: {rule.field_name})")
            errors.append(error_msg)

    def _validate_enum(
        self,
        rule: ValidationRule,
        value: object,
        errors: list[str],
    ) -> None:
        """Validate enum field."""
        allowed_values = rule.parameters.get("allowed_values", [])
        if value not in allowed_values:
            error_msg = f"Field '{rule.field_name}' must be one of {allowed_values}"
            if self.strict_mode:
                raise ValidationError(error_msg, rule.field_name)
            logger.warning(f"Validation failed: {error_msg} (field: {rule.field_name})")
            errors.append(error_msg)

    def validate_and_convert_record(
        self,
        record: dict[str, object],
        schema: dict[str, object],
    ) -> dict[str, object]:
        """Validate and convert a record according to schema."""
        if not schema.get("properties"):
            return record
        converted_record = {}
        for field_name, field_value in record.items():
            if field_name in schema["properties"]:
                field_schema = schema["properties"][field_name]
                converted_record[field_name] = self._convert_field(
                    value=field_value,
                    field_schema=field_schema,
                    field_name=field_name,
                    strict=self.strict_mode,
                )
            else:
                # Pass through unknown fields
                converted_record[field_name] = field_value
        return converted_record

    def _convert_field(
        self,
        *,
        value: str | float | bool | None,
        field_schema: dict[str, object],
        field_name: str,
        strict: bool = False,
    ) -> str | int | float | bool | None:
        """Convert a single field according to its schema."""
        if value is None or value == "":
            self.conversion_stats["nulls_handled"] += 1
            return None
        expected_type = field_schema.get("type", "string")
        # Handle type arrays (nullable types)
        if isinstance(expected_type, list):
            # Filter out null type and get the first non-null type
            non_null_types = [t for t in expected_type if t != "null"]
            expected_type = "string" if not non_null_types else non_null_types[0]
        try:
            if expected_type in {"number", "integer"}:
                return self._convert_to_number(value, expected_type, field_name)
            if expected_type == "boolean":
                return self._convert_to_boolean(
                    value=value,
                    _field_name=field_name,
                    _strict=strict,
                )
            if expected_type == "string" and field_schema.get("format") in {
                "date",
                "date-time",
            }:
                date_format = field_schema.get("format") or "date-time"
                str_value = str(value) if value is not None else None
                return self._convert_to_date(str_value, date_format, field_name)
            # This line is reachable for string type conversions
            return str(value) if value is not None else None
        except (ValueError, TypeError, AttributeError) as e:
            self.conversion_stats["validation_errors"] += 1
            # Always fail explicitly - no fallbacks allowed
            msg = f"Failed to convert field '{field_name}': {e}"
            raise ValueError(msg) from e

    def _convert_to_number(
        self,
        value: str | float | None,
        expected_type: str,
        _field_name: str,
    ) -> int | float | None:
        """Convert value to number (int or float)."""
        if isinstance(value, (int, float)):
            return value
        if isinstance(value, str):
            return self._convert_string_to_number(value, expected_type)
        return self._convert_other_to_number(value, expected_type)

    def _convert_string_to_number(
        self,
        value: str,
        expected_type: str,
    ) -> int | float | None:
        """Convert string value to number."""
        cleaned_value = self._clean_numeric_string(value)
        if not cleaned_value:
            return None
        try:
            if expected_type == "integer":
                return self._convert_to_integer(cleaned_value)
            self.conversion_stats["strings_converted_to_numbers"] += 1
            return float(cleaned_value)
        except (ValueError, TypeError) as e:
            msg = f"Cannot convert '{value}' to {expected_type}"
            raise ValueError(msg) from e

    def _clean_numeric_string(self, value: str) -> str:
        """Clean string for numeric conversion."""
        return value.strip().replace(",", "").replace("$", "")

    def _convert_to_integer(self, cleaned_value: str) -> int:
        """Convert cleaned string to integer with decimal handling."""
        if "." in cleaned_value:
            float_val = float(cleaned_value)
            if float_val.is_integer():
                self.conversion_stats["strings_converted_to_numbers"] += 1
                return int(float_val)
            msg = f"Cannot convert decimal {cleaned_value} to integer"
            raise ValueError(msg)
        self.conversion_stats["strings_converted_to_numbers"] += 1
        return int(cleaned_value)

    def _convert_other_to_number(
        self,
        value: str | float | None,
        expected_type: str,
    ) -> int | float | None:
        """Convert non-string types to number."""
        if value is None:
            return None
        try:
            if expected_type == "integer":
                return int(value)
            return float(value)
        except (ValueError, TypeError) as e:
            msg = f"Cannot convert {type(value)} '{value}' to {expected_type}"
            raise ValueError(msg) from e

    def _convert_to_boolean(
        self,
        *,
        value: str | float | bool,
        _field_name: str,
        _strict: bool = False,
    ) -> bool:
        """Convert value to boolean."""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            lower_val = value.lower().strip()
            if lower_val in {"true", "t", "yes", "y", "1", "on"}:
                return True
            if lower_val in {"false", "f", "no", "n", "0", "off"}:
                return False
            # Always fail explicitly - no fallbacks allowed
            msg = f"Cannot convert string '{value}' to boolean"
            raise ValueError(msg)
        return bool(value)

    def _convert_to_date(
        self,
        value: str | datetime | date | None,
        _date_format: str,
        _field_name: str,
    ) -> str | None:
        """Convert value to date string."""
        if isinstance(value, (datetime, date)):
            self.conversion_stats["dates_normalized"] += 1
            return value.isoformat()
        if isinstance(value, str):
            # Try parsing common date formats
            date_patterns = [
                r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}",  # ISO datetime
                r"\d{4}-\d{2}-\d{2}",  # ISO date
                r"\d{2}/\d{2}/\d{4}",  # US format
                r"\d{2}-\d{2}-\d{4}",  # US format with dashes
            ]
            for pattern in date_patterns:
                if re.match(pattern, value.strip()):
                    self.conversion_stats["dates_normalized"] += 1
                    return value.strip()
            # Always fail explicitly - no fallbacks allowed
            msg = f"Cannot parse date '{value}'"
            raise ValueError(msg)
        return str(value) if value is not None else None

    def get_conversion_stats(self) -> dict[str, int]:
        """Get conversion statistics."""
        return self.conversion_stats.copy()

    def reset_stats(self) -> None:
        """Reset conversion statistics."""
        for key in self.conversion_stats:
            self.conversion_stats[key] = 0


def create_validator_for_environment(environment: str = "dev") -> DataValidator:
    """Create a validator configured for the given environment."""
    strict_mode = environment == "prod"
    return DataValidator(strict_mode=strict_mode)


if __name__ == "__main__":
    # Test the validator
    validator = DataValidator(strict_mode=False)
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
    logger.info(f"Converted record: {result}")
    logger.info(f"Stats: {validator.get_conversion_stats()}")
