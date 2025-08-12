"""Validador de Dados Profissional para Integração Oracle WMS.

Lida com conversão de tipos e problemas de validação encontrados em produção.
Fornece validação robusta e conversão de dados para integração ETL.

Classes:
    ValidationError: Erro de validação compatível com testes.
    ValidationRule: Definição de regra de validação.
    DataValidator: Validador principal com manipulação específica Oracle.

Funções:
    create_validator_for_environment: Cria validador configurado para ambiente.
"""

from __future__ import annotations

import re
from datetime import UTC, date, datetime
from decimal import Decimal, InvalidOperation
from typing import TYPE_CHECKING

from flext_core import FlextValidationError, get_logger

if TYPE_CHECKING:
    from collections.abc import Callable

# Use dependency injection instead of direct imports for Clean Architecture compliance

# Get dependencies via DI
logger = get_logger(__name__)


# Use FLEXT foundation pattern with proper error code for tests compatibility
class ValidationError(FlextValidationError):
    """Erro de validação com código de erro compatível com testes.

    Estende FlextValidationError para fornecer erro de validação
    consistente com código de erro específico para compatibilidade
    com suíte de testes existente.
    """

    def __init__(self, message: str, validation_details: dict[str, object] | None = None, **kwargs: object) -> None:
        """Inicializa erro de validação com código de erro consistente.

        Args:
            message: Mensagem de erro descritiva.
            validation_details: Detalhes adicionais de validação.
            **kwargs: Argumentos adicionais mesclados no contexto.

        """
        context = validation_details if validation_details is not None else {}
        # Merge kwargs into context if needed
        if kwargs:
            context.update(kwargs)
        super().__init__(
            message,
            error_code="VALIDATION_ERROR",
            context=context,
        )


class ValidationRule:
    """Definição de regra de validação.

    Representa uma regra de validação que pode ser aplicada
    a campos de dados durante o processo de validação.

    Attributes:
        field_name: Nome do campo a ser validado.
        rule_type: Tipo de validação (required, type, range, etc.).
        parameters: Parâmetros da regra.
        params: Alias para parameters (compatibilidade).

    """

    def __init__(
        self,
        field_name: str,
        rule_type: str,
        parameters: dict[str, object] | None = None,
        **kwargs: object,
    ) -> None:
        """Inicializa regra de validação.

        Args:
            field_name: Campo a ser validado.
            rule_type: Tipo de validação (required, type, range, etc.).
            parameters: Dicionário de parâmetros da regra (opcional).
            **kwargs: Parâmetros adicionais da regra (mesclados com parameters).

        """
        self.field_name = field_name
        self.rule_type = rule_type
        # Merge explicit parameters dict with **kwargs
        self.parameters = {**(parameters or {}), **kwargs}
        self.params = self.parameters  # Keep for backward compatibility


class DataValidator:
    """Validador de dados profissional com manipulação de tipos específica Oracle.

    Fornece validação robusta e conversão de dados otimizada para
    integração Oracle WMS, com manipulação adequada de tipos de dados
    e estatísticas de conversão.

    Attributes:
        rules: Lista de regras de validação.
        strict_mode: Se True, lança exceções em falhas de validação.
        conversion_stats: Estatísticas de conversão de dados.

    """

    def __init__(
        self,
        rules: list[ValidationRule] | None = None,
        *,
        strict_mode: bool = False,
    ) -> None:
        """Inicializa validador de dados.

        Args:
            rules: Lista de regras de validação a aplicar.
            strict_mode: Se True, lança exceções em falhas de validação.

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
            error_msg: str = f"Required field '{rule.field_name}' is missing"
            if self.strict_mode:
                raise ValidationError(
                    error_msg,
                    validation_details={"field": rule.field_name},
                )
            logger.warning("Validation failed: %s (field: %s)", error_msg, rule.field_name)
            errors.append(error_msg)
            return False
        return True

    def _validate_field_value(
        self,
        rule: ValidationRule,
        *,
        value: object,
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
        """Valida dados contra regras configuradas.

        Aplica todas as regras de validação configuradas aos dados fornecidos,
        coletando erros de validação encontrados.

        Args:
            data: Dados a serem validados.

        Returns:
            list[str]: Lista de mensagens de erro de validação
            (vazia se todas as validações passarem).

        Raises:
            ValidationError: Se a validação falhar no modo strict.

        Example:
            >>> validator = DataValidator([ValidationRule("id", "required")])
            >>> erros = validator.validate({"nome": "João"})
            >>> print(erros)  # ['Required field "id" is missing']

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
            error_msg: str = f"Field '{rule.field_name}' must be a valid decimal"
            if self.strict_mode:
                raise ValidationError(
                    error_msg,
                    validation_details={"field": rule.field_name},
                ) from e
            logger.warning("Validation failed: %s (field: %s)", error_msg, rule.field_name)
            errors.append(error_msg)

    def _validate_string(
        self,
        rule: ValidationRule,
        value: object,
        errors: list[str],
    ) -> None:
        """Validate string field."""
        if not isinstance(value, str):
            error_msg: str = f"Field '{rule.field_name}' must be a string"
            if self.strict_mode:
                raise ValidationError(
                    error_msg,
                    validation_details={"field": rule.field_name},
                )
            logger.warning("Validation failed: %s (field: %s)", error_msg, rule.field_name)
            errors.append(error_msg)
        else:
            # Check string length constraints - value is now confirmed to be str
            max_length = rule.parameters.get("max_length")
            if (
                max_length is not None
                and isinstance(max_length, int)
                and len(value) > max_length
            ):
                error_msg = (
                    f"Field '{rule.field_name}' exceeds maximum length {max_length}"
                )
                if self.strict_mode:
                    raise ValidationError(
                        error_msg,
                        validation_details={"field": rule.field_name},
                    )
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
            error_msg: str = f"Field '{rule.field_name}' must be a number"
            if self.strict_mode:
                raise ValidationError(
                    error_msg,
                    validation_details={"field": rule.field_name},
                )
            logger.warning("Validation failed: %s (field: %s)", error_msg, rule.field_name)
            errors.append(error_msg)
        else:
            # Check numeric range constraints - value is now confirmed to be int | float
            min_value = rule.parameters.get("min_value")
            max_value = rule.parameters.get("max_value")
            if (
                min_value is not None
                and isinstance(min_value, (int, float))
                and value < min_value
            ):
                min_error_msg: str = (
                    f"Field '{rule.field_name}' below minimum value {min_value}"
                )
                if self.strict_mode:
                    raise ValidationError(
                        min_error_msg,
                        validation_details={"field": rule.field_name},
                    )
                logger.warning(
                    f"Validation failed: {min_error_msg} (field: {rule.field_name})",
                )
                errors.append(min_error_msg)
            if (
                max_value is not None
                and isinstance(max_value, (int, float))
                and value > max_value
            ):
                max_error_msg = (
                    f"Field '{rule.field_name}' exceeds maximum value {max_value}"
                )
                if self.strict_mode:
                    raise ValidationError(
                        max_error_msg,
                        validation_details={"field": rule.field_name},
                    )
                logger.warning(
                    f"Validation failed: {max_error_msg} (field: {rule.field_name})",
                )
                errors.append(max_error_msg)

    def _validate_date(
        self,
        rule: ValidationRule,
        value: object,
        errors: list[str],
    ) -> None:
        """Validate date field."""
        if isinstance(value, str):
            date_format_raw = rule.parameters.get("format", "%Y-%m-%d")
            date_format = (
                date_format_raw if isinstance(date_format_raw, str) else "%Y-%m-%d"
            )
            try:
                datetime.strptime(value, date_format).replace(tzinfo=UTC)
            except ValueError:
                format_error_msg = (
                    f"Field '{rule.field_name}' is not a valid date format "
                    f"{date_format}"
                )
                if self.strict_mode:
                    raise ValidationError(
                        format_error_msg,
                        validation_details={"field": rule.field_name},
                    ) from None
                logger.warning(
                    f"Validation failed: {format_error_msg} (field: {rule.field_name})",
                )
                errors.append(format_error_msg)
        elif not isinstance(value, datetime):
            type_error_msg: str = f"Field '{rule.field_name}' must be a valid date"
            if self.strict_mode:
                raise ValidationError(
                    type_error_msg,
                    validation_details={"field": rule.field_name},
                )
            logger.warning(
                f"Validation failed: {type_error_msg} (field: {rule.field_name})",
            )
            errors.append(type_error_msg)

    def _validate_boolean(
        self,
        rule: ValidationRule,
        value: object,
        errors: list[str],
    ) -> None:
        """Validate boolean field."""
        if not isinstance(value, bool):
            error_msg: str = f"Field '{rule.field_name}' must be a boolean"
            if self.strict_mode:
                raise ValidationError(
                    error_msg,
                    validation_details={"field": rule.field_name},
                )
            logger.warning("Validation failed: %s (field: %s)", error_msg, rule.field_name)
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
            error_msg: str = f"Field '{rule.field_name}' must be a valid email address"
            if self.strict_mode:
                raise ValidationError(
                    error_msg,
                    validation_details={"field": rule.field_name},
                )
            logger.warning("Validation failed: %s (field: %s)", error_msg, rule.field_name)
            errors.append(error_msg)

    def _validate_enum(
        self,
        rule: ValidationRule,
        value: object,
        errors: list[str],
    ) -> None:
        """Validate enum field."""
        allowed_values_raw = rule.parameters.get("allowed_values", [])
        allowed_values = (
            allowed_values_raw
            if isinstance(allowed_values_raw, (list, tuple, set))
            else []
        )
        if value not in allowed_values:
            error_msg: str = (
                f"Field '{rule.field_name}' must be one of {allowed_values}"
            )
            if self.strict_mode:
                raise ValidationError(
                    error_msg,
                    validation_details={"field": rule.field_name},
                )
            logger.warning("Validation failed: %s (field: %s)", error_msg, rule.field_name)
            errors.append(error_msg)

    def validate_and_convert_record(
        self,
        record: dict[str, object],
        schema: dict[str, object],
    ) -> dict[str, object]:
        """Valida e converte um registro de acordo com schema.

        Processa um registro de dados aplicando conversões de tipo
        baseadas no schema fornecido, com manipulação específica
        para tipos Oracle WMS.

        Args:
            record: Registro de dados a ser processado.
            schema: Schema definindo tipos esperados dos campos.

        Returns:
            dict[str, object]: Registro convertido com tipos apropriados.

        Raises:
            ValueError: Se conversão de tipo falhar.

        Example:
            >>> validator = DataValidator()
            >>> schema = {"properties": {"id": {"type": "integer"}}}
            >>> resultado = validator.validate_and_convert_record(
            ...     {"id": "123"}, schema
            ... )
            >>> print(resultado)  # {"id": 123}

        """
        properties = schema.get("properties")
        if not properties or not isinstance(properties, dict):
            return record
        converted_record: dict[str, object] = {}
        for field_name, field_value in record.items():
            if field_name in properties:
                field_schema = properties[field_name]
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
        value: object,
        field_schema: object,
        field_name: str,
        strict: bool = False,
    ) -> object:
        """Convert a single field according to its schema."""
        if value is None or value == "":
            self.conversion_stats["nulls_handled"] += 1
            return None

        # Type check field_schema
        if not isinstance(field_schema, dict):
            return value  # Pass through if schema is not a dict

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
            msg: str = f"Failed to convert field '{field_name}': {e}"
            raise ValueError(msg) from e

    def _convert_to_number(
        self,
        value: object,
        expected_type: object,
        _field_name: str,
    ) -> object:
        """Convert value to number (int or float)."""
        if isinstance(value, (int, float)):
            return value
        if isinstance(value, str):
            return self._convert_string_to_number(value, expected_type)
        return self._convert_other_to_number(value, expected_type)

    def _convert_string_to_number(
        self,
        value: object,
        expected_type: object,
    ) -> object:
        """Convert string value to number."""
        if not isinstance(value, str):
            return value  # Pass through non-string values
        cleaned_value = self._clean_numeric_string(value)
        if not cleaned_value:
            return None
        try:
            if expected_type == "integer":
                return self._convert_to_integer(cleaned_value)
            self.conversion_stats["strings_converted_to_numbers"] += 1
            return float(cleaned_value)
        except (ValueError, TypeError) as e:
            msg: str = f"Cannot convert '{value}' to {expected_type}"
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
            msg: str = f"Cannot convert decimal {cleaned_value} to integer"
            raise ValueError(msg)
        self.conversion_stats["strings_converted_to_numbers"] += 1
        return int(cleaned_value)

    def _convert_other_to_number(
        self,
        value: object,
        expected_type: object,
    ) -> object:
        """Convert non-string types to number."""
        if value is None:
            return None
        try:
            if expected_type == "integer":
                # Type narrowing: int() can handle various numeric types
                return (
                    int(value)
                    if isinstance(value, (int, float, bool, str))
                    else int(str(value))
                )
            # Type narrowing: float() can handle various numeric types
            return (
                float(value)
                if isinstance(value, (int, float, bool, str))
                else float(str(value))
            )
        except (ValueError, TypeError) as e:
            msg: str = f"Cannot convert {type(value)} '{value}' to {expected_type}"
            raise ValueError(msg) from e

    def _convert_to_boolean(
        self,
        *,
        value: object,
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
            msg: str = f"Cannot convert string '{value}' to boolean"
            raise ValueError(msg)
        return bool(value)

    def _convert_to_date(
        self,
        value: object,
        _date_format: object,
        _field_name: str,
    ) -> object:
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
            msg: str = f"Cannot parse date '{value}'"
            raise ValueError(msg)
        return str(value) if value is not None else None

    def get_conversion_stats(self) -> dict[str, int]:
        """Obtém estatísticas de conversão.

        Returns:
            dict[str, int]: Dicionário com estatísticas de conversão
            incluindo strings convertidas, datas normalizadas, etc.

        """
        return self.conversion_stats.copy()

    def reset_stats(self) -> None:
        """Reseta estatísticas de conversão.

        Zera todos os contadores de estatísticas de conversão
        para reiniciar a coleta de métricas.
        """
        for key in self.conversion_stats:
            self.conversion_stats[key] = 0


def create_validator_for_environment(environment: str = "dev") -> DataValidator:
    """Cria validador configurado para o ambiente especificado.

    Factory function que cria um validador de dados com configuração
    apropriada para o ambiente especificado (desenvolvimento vs produção).

    Args:
        environment: Ambiente de execução ("dev", "prod", etc.).

    Returns:
        DataValidator: Instância configurada do validador.

    Example:
        >>> # Validador para desenvolvimento (modo não-strict)
        >>> validator_dev = create_validator_for_environment("dev")
        >>>
        >>> # Validador para produção (modo strict)
        >>> validator_prod = create_validator_for_environment("prod")

    """
    strict_mode = environment == "prod"
    return DataValidator(strict_mode=strict_mode)


if __name__ == "__main__":
    # Test the validator
    validator = DataValidator(strict_mode=False)
    test_record: dict[str, object] = {
        "id": "123",
        "amount": "540.50",
        "count": "42",
        "active": "true",
        "created_date": "2025-07-02T10:00:00",
    }
    test_schema: dict[str, object] = {
        "properties": {
            "id": {"type": "integer"},
            "amount": {"type": "number"},
            "count": {"type": "integer"},
            "active": {"type": "boolean"},
            "created_date": {"type": "string", "format": "date-time"},
        },
    }
    result = validator.validate_and_convert_record(test_record, test_schema)
    logger.info("Converted record: %s", result)
    logger.info("Stats: %s", validator.get_conversion_stats())
