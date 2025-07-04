#!/usr/bin/env python3
"""Professional Data Validator for Oracle WMS Integration
Handles type conversion and validation issues found in production.
"""

import re
from datetime import date, datetime
from typing import Any


class DataValidator:
    """Professional data validator with Oracle-specific type handling."""

    def __init__(self, strict_mode: bool = False):
        """Initialize validator with configurable strictness."""
        self.strict_mode = strict_mode
        self.conversion_stats = {
            "strings_converted_to_numbers": 0,
            "dates_normalized": 0,
            "nulls_handled": 0,
            "validation_errors": 0,
        }

    def validate_and_convert_record(self, record: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any]:
        """Validate and convert a record according to schema.

        Args:
            record: Input record to validate
            schema: JSON schema for validation

        Returns:
            Converted and validated record
        """
        if not schema.get("properties"):
            return record

        converted_record = {}

        for field_name, field_value in record.items():
            if field_name in schema["properties"]:
                field_schema = schema["properties"][field_name]
                converted_record[field_name] = self._convert_field(
                    field_value, field_schema, field_name,
                )
            else:
                # Pass through unknown fields
                converted_record[field_name] = field_value

        return converted_record

    def _convert_field(self, value: Any, field_schema: dict[str, Any], field_name: str) -> Any:
        """Convert field value according to schema definition."""
        if value is None or value == "":
            self.conversion_stats["nulls_handled"] += 1
            return None

        expected_type = field_schema.get("type", "string")

        # Handle type arrays (nullable types)
        if isinstance(expected_type, list):
            if "null" in expected_type and value is None:
                return None
            expected_type = next((t for t in expected_type if t != "null"), "string")

        try:
            if expected_type in {"number", "integer"}:
                return self._convert_to_number(value, expected_type, field_name)
            if expected_type == "boolean":
                return self._convert_to_boolean(value, field_name)
            if expected_type == "string" and field_schema.get("format") in {"date", "date-time"}:
                date_format = field_schema.get("format") or "date-time"
                return self._convert_to_date(value, date_format, field_name)
            return str(value) if value is not None else None

        except Exception as e:
            self.conversion_stats["validation_errors"] += 1
            if self.strict_mode:
                msg = f"Failed to convert field '{field_name}': {e}"
                raise ValueError(msg)
            # Log warning and return original value
            print(f"⚠️  Warning: Could not convert {field_name}={value} to {expected_type}: {e}")
            return value

    def _convert_to_number(self, value: Any, expected_type: str, field_name: str) -> int | float | None:
        """Convert value to number, handling string numbers."""
        if isinstance(value, int | float):
            return value

        if isinstance(value, str):
            # Remove common formatting
            cleaned_value = value.strip().replace(",", "").replace("$", "")

            # Handle empty strings
            if not cleaned_value:
                return None

            try:
                if expected_type == "integer":
                    # Handle decimal strings for integers
                    if "." in cleaned_value:
                        float_val = float(cleaned_value)
                        if float_val.is_integer():
                            self.conversion_stats["strings_converted_to_numbers"] += 1
                            return int(float_val)
                        if self.strict_mode:
                            msg = f"Cannot convert decimal {cleaned_value} to integer"
                            raise ValueError(msg)
                        return int(float_val)  # Truncate in non-strict mode
                    self.conversion_stats["strings_converted_to_numbers"] += 1
                    return int(cleaned_value)
                # number (float)
                self.conversion_stats["strings_converted_to_numbers"] += 1
                return float(cleaned_value)

            except ValueError:
                if self.strict_mode:
                    msg = f"Cannot convert '{value}' to {expected_type}"
                    raise ValueError(msg)
                # Return 0 as fallback in non-strict mode
                return 0

        # Handle other types
        try:
            if expected_type == "integer":
                return int(value)
            return float(value)
        except (ValueError, TypeError):
            if self.strict_mode:
                msg = f"Cannot convert {type(value)} '{value}' to {expected_type}"
                raise ValueError(msg)
            return 0

    def _convert_to_boolean(self, value: Any, field_name: str) -> bool:
        """Convert value to boolean."""
        if isinstance(value, bool):
            return value

        if isinstance(value, str):
            lower_val = value.lower().strip()
            if lower_val in {"true", "t", "yes", "y", "1", "on"}:
                return True
            if lower_val in {"false", "f", "no", "n", "0", "off"}:
                return False
            if self.strict_mode:
                msg = f"Cannot convert string '{value}' to boolean"
                raise ValueError(msg)
            return bool(value)  # Fallback to truthiness

        if isinstance(value, int | float):
            return bool(value)

        if self.strict_mode:
            msg = f"Cannot convert {type(value)} '{value}' to boolean"
            raise ValueError(msg)
        return bool(value)

    def _convert_to_date(self, value: Any, date_format: str, field_name: str) -> str | None:
        """Convert value to standardized date format."""
        if isinstance(value, datetime | date):
            self.conversion_stats["dates_normalized"] += 1
            return value.isoformat()

        if isinstance(value, str):
            # Try parsing common date formats
            date_patterns = [
                r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}",  # ISO datetime
                r"\d{4}-\d{2}-\d{2}",                     # ISO date
                r"\d{2}/\d{2}/\d{4}",                     # US format
                r"\d{2}-\d{2}-\d{4}",                     # US format with dashes
            ]

            for pattern in date_patterns:
                if re.match(pattern, value.strip()):
                    self.conversion_stats["dates_normalized"] += 1
                    return value.strip()

            if self.strict_mode:
                msg = f"Cannot parse date '{value}'"
                raise ValueError(msg)
            return value  # Return as-is if can't parse

        return str(value) if value is not None else None

    def get_conversion_stats(self) -> dict[str, int]:
        """Get statistics about conversions performed."""
        return self.conversion_stats.copy()

    def reset_stats(self) -> None:
        """Reset conversion statistics."""
        for key in self.conversion_stats:
            self.conversion_stats[key] = 0


def create_validator_for_environment(environment: str = "dev") -> DataValidator:
    """Create validator configured for specific environment."""
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
    print(f"Converted record: {result}")
    print(f"Stats: {validator.get_conversion_stats()}")
