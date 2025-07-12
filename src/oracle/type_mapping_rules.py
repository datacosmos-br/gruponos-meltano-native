"""Oracle Type Mapping Rules - Módulo Compartilhado.

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


def convert_metadata_type_to_oracle(
    metadata_type: str | None = None,
    column_name: str = "",
    max_length: int | None = None,
    sample_value: Any | None = None,
) -> str:
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
        return _infer_oracle_from_sample(sample_value)

    # Default type - explicit failure
    return "VARCHAR2(255 CHAR)"


def convert_field_pattern_to_oracle(
    column_name: str, max_length: int | None = None
) -> str | None:
    column_lower = column_name.lower()

    for pattern_key, patterns in FIELD_PATTERN_RULES.items():
        for pattern in patterns:
            # Lidar com padrões wildcard
            if "*" in pattern:
                pattern_clean = pattern.replace("*", "")
                if (
                    pattern.startswith("*_") and column_lower.endswith(pattern_clean)
                ) or (
                    pattern.endswith("_*") and column_lower.startswith(pattern_clean)
                ):
                    oracle_type = FIELD_PATTERNS_TO_ORACLE[pattern_key]
                    # Forçar 4000 CHAR para campos _set independentemente de max_length
                    if pattern_key == "set_patterns":
                        return "VARCHAR2(4000 CHAR)"
                    if oracle_type.startswith("VARCHAR2") and max_length:
                        return f"VARCHAR2({min(max_length, 4000)} CHAR)"
                    return oracle_type
            # Match exato
            elif pattern == column_lower:
                oracle_type = FIELD_PATTERNS_TO_ORACLE[pattern_key]
                # Forçar 4000 CHAR para campos _set independentemente de max_length
                if pattern_key == "set_patterns":
                    return "VARCHAR2(4000 CHAR)"
                if oracle_type.startswith("VARCHAR2") and max_length:
                    return f"VARCHAR2({min(max_length, 4000)} CHAR)"
                return oracle_type

    return None


def convert_singer_schema_to_oracle(
    column_name: str, column_schema: dict[str, Any]
) -> str:
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


def _infer_oracle_from_sample(sample_value: Any) -> str:
    if isinstance(sample_value, bool):
        return "NUMBER(1,0)"
    if isinstance(sample_value, (int, float)):
        return "NUMBER"
    if isinstance(sample_value, str):
        if _looks_like_date(sample_value):
            return "TIMESTAMP(6)"
        length = min(len(sample_value) * 2, 4000)
        return f"VARCHAR2({length} CHAR)"
    return "VARCHAR2(255 CHAR)"


def _looks_like_date(value: str) -> bool:
    date_patterns = [
        r"\d{4}-\d{2}-\d{2}",  # YYYY-MM-DD
        r"\d{2}/\d{2}/\d{4}",  # MM/DD/YYYY
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}",  # ISO datetime
    ]

    return any(re.match(pattern, value) for pattern in date_patterns)


def oracle_ddl_from_singer_schema(
    singer_schema: dict[str, Any], column_name: str = ""
) -> str:
    # Extrair metadata se disponível
    metadata_type = None
    if "x-wms-metadata" in singer_schema:
        metadata_type = singer_schema["x-wms-metadata"].get("original_metadata_type")

    # Obter max length se especificado
    max_length = singer_schema.get("maxLength")

    return convert_metadata_type_to_oracle(
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
    "convert_metadata_type_to_oracle",
    "convert_singer_schema_to_oracle",
    "oracle_ddl_from_singer_schema",
]
