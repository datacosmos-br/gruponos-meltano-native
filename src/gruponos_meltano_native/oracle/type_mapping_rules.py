"""Oracle Type Mapping Rules - DEPRECATED - USE FLEXT-TARGET-ORACLE.

WARNING: This module duplicates functionality already present in flext-target-oracle.
Per FLEXT documentation analysis, type mapping should be handled by the Singer target:
- flext-target-oracle uses flext-db-oracle for type mapping
- Automatic conversion from Singer JSON Schema to Oracle types
- Enterprise patterns for Oracle optimization

CORRECT APPROACH:
Use flext-target-oracle - it handles type mapping automatically.

This module is maintained only for backward compatibility with existing tests.
For new development, use flext-target-oracle exclusively.

Regras centralizadas para conversão de tipos WMS → Oracle DDL.

Este módulo é usado por:
    - table_creator.py (criação manual de tabelas)
- flext-target-oracle (criação automática pelo Singer)
  Garante consistência total entre os dois métodos de criação.
"""

from __future__ import annotations

import re
from typing import Any

# Oracle DDL Type Mappings
WMS_METADATA_TO_ORACLE = {
    "pk": "NUMBER",
    "varchar": "VARCHAR2(255 CHAR)",
    "char": "CHAR(10)",
    "number": "NUMBER",
    "decimal": "NUMBER",
    "integer": "NUMBER",
    "boolean": "NUMBER(1,0)",
    "datetime": "TIMESTAMP(6)",
    "date": "TIMESTAMP(6)",
    "time": "TIMESTAMP(6)",
    "text": "VARCHAR2(4000 CHAR)",
    "clob": "CLOB",
    "relation": "VARCHAR2(255 CHAR)",
}

# Field Name Patterns to Oracle Types
FIELD_PATTERNS_TO_ORACLE = {
    "id_patterns": "NUMBER",
    "key_patterns": "VARCHAR2(255 CHAR)",
    "qty_patterns": "NUMBER",
    "price_patterns": "NUMBER",
    "weight_patterns": "NUMBER",
    "date_patterns": "TIMESTAMP(6)",
    "flag_patterns": "NUMBER(1,0)",
    "desc_patterns": "VARCHAR2(500 CHAR)",
    "code_patterns": "VARCHAR2(50 CHAR)",
    "name_patterns": "VARCHAR2(255 CHAR)",
    "addr_patterns": "VARCHAR2(500 CHAR)",
    "decimal_patterns": "NUMBER",
    "set_patterns": "VARCHAR2(4000 CHAR)",  # Campos *_set sempre 4000 CHAR
}

# Pattern matching rules
FIELD_PATTERN_RULES = {
    "id_patterns": ["*_id", "id"],
    "key_patterns": ["*_key"],
    "qty_patterns": [
        "*_qty",
        "*_quantity",
        "*_count",
        "*_amount",
        "alloc_qty",
        "ord_qty",
        "packed_qty",
        "ordered_uom_qty",
        "orig_ord_qty",
    ],
    "price_patterns": [
        "*_price",
        "*_cost",
        "*_rate",
        "*_percent",
        "cost",
        "sale_price",
        "unit_declared_value",
        "orig_sale_price",
    ],
    "weight_patterns": [
        "*_weight",
        "*_volume",
        "*_length",
        "*_width",
        "*_height",
    ],
    "date_patterns": [
        "*_date",
        "*_time",
        "*_ts",
        "*_timestamp",
        "cust_date_*",
    ],
    "flag_patterns": ["*_flg", "*_flag", "*_enabled", "*_active"],
    "desc_patterns": ["*_desc", "*_description", "*_note", "*_comment"],
    "code_patterns": ["*_code", "*_status", "*_type"],
    "name_patterns": ["*_name", "*_title"],
    "addr_patterns": ["*_addr", "*_address"],
    "decimal_patterns": [
        "cust_decimal_*",
        "cust_number_*",
        "voucher_amount",
        "total_orig_ord_qty",
    ],
    "set_patterns": ["*_set"],  # IMPORTANTE: Sempre VARCHAR2(4000 CHAR)
}


def convert_field_to_oracle_new(
    *,
    metadata_type: str | None = None,
    column_name: str = "",
    max_length: int | None = None,
    sample_value: str | float | bool | None = None,
) -> str:
    """Convert WMS metadata type to Oracle type with intelligent mapping.

    Args:
        metadata_type: WMS metadata type from API
        column_name: Column name for pattern matching
        max_length: Maximum length constraint
        sample_value: Sample value for type inference (str, int, float, bool, or None)

    Returns:
        Oracle SQL type definition

    """
    # Prioridade 1: Tipos WMS metadata
    if metadata_type and metadata_type.lower() in WMS_METADATA_TO_ORACLE:
        oracle_type = WMS_METADATA_TO_ORACLE[metadata_type.lower()]

        # Aplicar max_length override para tipos VARCHAR2
        if oracle_type.startswith("VARCHAR2") and max_length:
            return f"VARCHAR2({min(max_length, 4000)} CHAR)"

        return oracle_type

    # Prioridade 2: Padrões de nome de campo
    oracle_type_pattern = convert_field_pattern_to_oracle(column_name, max_length)
    if oracle_type_pattern:
        return oracle_type_pattern

    # Prioridade 3: Inferência de valor de amostra (último recurso)
    if sample_value is not None:
        return _infer_oracle_from_sample(sample_value=sample_value)

    # Default type - explicit failure
    return "VARCHAR2(255 CHAR)"


def convert_field_pattern_to_oracle(
    column_name: str,
    max_length: int | None = None,
) -> str | None:
    """Convert field name patterns to Oracle types.

    Args:
        column_name: Name of the column
        max_length: Maximum length constraint

    Returns:
        Oracle type string or None if no pattern matches

    """
    column_lower = column_name.lower()

    for pattern_key, patterns in FIELD_PATTERN_RULES.items():
        oracle_type = _check_pattern_match(
            patterns,
            column_lower,
            pattern_key,
            max_length,
        )
        if oracle_type:
            return oracle_type

    return None


def _check_pattern_match(
    patterns: list[str],
    column_lower: str,
    pattern_key: str,
    max_length: int | None,
) -> str | None:
    """Check if column matches any pattern and return Oracle type."""
    for pattern in patterns:
        if _is_pattern_match(pattern, column_lower):
            return _get_oracle_type_for_pattern(pattern_key, max_length)
    return None


def _is_pattern_match(pattern: str, column_lower: str) -> bool:
    """Check if column name matches the pattern."""
    # Handle wildcard patterns
    if "*" in pattern:
        pattern_clean = pattern.replace("*", "")
        return (pattern.startswith("*_") and column_lower.endswith(pattern_clean)) or (
            pattern.endswith("_*") and column_lower.startswith(pattern_clean)
        )
    # Exact match
    return pattern == column_lower


def _get_oracle_type_for_pattern(pattern_key: str, max_length: int | None) -> str:
    """Get Oracle type for pattern key with length consideration."""
    oracle_type = FIELD_PATTERNS_TO_ORACLE[pattern_key]

    # Force 4000 CHAR for set fields regardless of max_length
    if pattern_key == "set_patterns":
        return "VARCHAR2(4000 CHAR)"

    # Apply max_length for VARCHAR2 types
    if oracle_type.startswith("VARCHAR2") and max_length:
        return f"VARCHAR2({min(max_length, 4000)} CHAR)"

    return oracle_type


def convert_singer_schema_to_oracle(
    column_name: str,
    column_schema: dict[str, Any],
) -> str:
    """Convert Singer schema to Oracle type definition.

    Args:
        column_name: Name of the column
        column_schema: Singer schema definition

    Returns:
        Oracle type definition string

    """
    # Prioridade 1: Padrões de nome de campo (mesma lógica do table_creator)
    oracle_type = convert_field_pattern_to_oracle(column_name)
    if oracle_type:
        return oracle_type

    # Prioridade 2: Inferência de tipo Singer
    schema_type = column_schema.get("type", "string")
    if isinstance(schema_type, list):
        # Lidar com tipos nullable como ["string", "null"]
        schema_type = next((t for t in schema_type if t != "null"), "string")

    if schema_type in {"integer", "number"}:
        return "NUMBER"
    if schema_type == "boolean":
        return "NUMBER(1,0)"
    if schema_type == "string":
        # Verificar formato date-time
        format_type = column_schema.get("format")
        if format_type in {"date-time", "date", "time"}:
            return "TIMESTAMP(6)"

        # Usar max length se disponível
        max_length = column_schema.get("maxLength", 255)
        return f"VARCHAR2({min(max_length, 4000)} CHAR)"

    # Default type
    return "VARCHAR2(255 CHAR)"


def _infer_oracle_from_sample(*, sample_value: Any) -> str:
    if isinstance(sample_value, bool):
        return "NUMBER(1,0)"
    if isinstance(sample_value, (int, float)):
        return "NUMBER"
    if isinstance(sample_value, str):
        if _looks_like_date(sample_value):
            return "TIMESTAMP(6)"
        length = min(len(sample_value) * 2, 4000)
        return f"VARCHAR2({length} CHAR)"
    # Default case for any other type
    return "VARCHAR2(255 CHAR)"


def _looks_like_date(value: str) -> bool:
    date_patterns = [
        r"\d{4}-\d{2}-\d{2}",  # YYYY-MM-DD
        r"\d{2}/\d{2}/\d{4}",  # MM/DD/YYYY
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}",  # ISO datetime
    ]

    return any(re.match(pattern, value) for pattern in date_patterns)


def oracle_ddl_from_singer_schema(
    singer_schema: dict[str, Any],
    column_name: str = "",
) -> str:
    """Generate Oracle DDL from Singer schema with enhanced type mapping.

    Args:
        singer_schema: Singer schema definition
        column_name: Optional column name for context

    Returns:
        Oracle DDL statement

    """
    # Extrair metadata se disponível
    metadata_type = None
    if "x-wms-metadata" in singer_schema:
        metadata_type = singer_schema["x-wms-metadata"].get("original_metadata_type")

    # Obter max length se especificado
    max_length = singer_schema.get("maxLength")

    return convert_field_to_oracle_new(
        metadata_type=metadata_type,
        column_name=column_name,
        max_length=max_length,
    )


# Constantes para uso externo
__all__ = [
    "FIELD_PATTERNS_TO_ORACLE",
    "FIELD_PATTERN_RULES",
    "WMS_METADATA_TO_ORACLE",
    "convert_field_pattern_to_oracle",
    "convert_singer_schema_to_oracle",
    "oracle_ddl_from_singer_schema",
]
