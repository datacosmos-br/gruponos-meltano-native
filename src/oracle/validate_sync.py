from datetime import datetime
"""Validate data in Oracle tables after sync."""

from __future__ import annotations

from datetime import UTC, datetime

import logging
# Use centralized logger from flext-observability - ELIMINATE DUPLICATION
from flext_observability.logging import get_logger
# from flext_observability import get_logger
from src.oracle.connection_manager import create_connection_manager_from_env

# Setup logger
log = get_logger(__name__)


def validate_sync() -> bool:
        log.info("🔍 VALIDANDO DADOS NO ORACLE...")
    log.info("📅 %s", datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S"))
    log.info("-" * 60)

    # Create connection
    manager = create_connection_manager_from_env()

    try:
            conn = manager.connect()
        cursor = conn.cursor()

        # Tables to validate - check both with and without prefix
        tables = [
            ("WMS_ALLOCATION", "allocation"),
            ("WMS_ORDER_HDR", "order_hdr"),
            ("WMS_ORDER_DTL", "order_dtl"),
            ("ALLOCATION", "allocation"),
            ("ORDER_HDR", "order_hdr"),
            ("ORDER_DTL", "order_dtl"),
        ]

        total_records = 0

        for table_name, entity_name in tables:
            log.info("\n📊 Tabela: %s (%s)", table_name, entity_name)

            try:
            # Count records (table names cannot be parameterized in Oracle)
                # Validate table name for safety
                if not table_name.replace("_", "").isalnum():
            log.error("Invalid table name: %s", table_name)
                    continue
                cursor.execute(
                    f'SELECT COUNT(*) FROM "OIC"."{table_name}"',  # noqa: S608
                )
                count = cursor.fetchone()[0]
                total_records += count
                log.info("   Total de registros: %s", f"{count:,}")

                if count > 0:
            # Get date range (table names cannot be parameterized)
                    cursor.execute(
                        f"SELECT "  # noqa: S608
                        f'MIN("MOD_TS") as min_date, '
                        f'MAX("MOD_TS") as max_date, '
                        f'COUNT(DISTINCT "ID") as unique_ids '
                        f'FROM "OIC"."{table_name}"',
                    )
                    min_date, max_date, unique_ids = cursor.fetchone()

                    log.info("   Data mais antiga: %s", min_date)
                    log.info("   Data mais recente: %s", max_date)
                    log.info("   IDs únicos: %s", f"{unique_ids:,}")

                    # Check for duplicates (table names cannot be parameterized)
                    cursor.execute(
                        f'SELECT "ID", COUNT(*) as cnt '  # noqa: S608
                        f'FROM "OIC"."{table_name}" '
                        f'GROUP BY "ID" '
                        f"HAVING COUNT(*) > 1",
                    )
                    duplicates = cursor.fetchall()

                    if duplicates:
            log.warning(
                            "   ⚠️  Duplicatas encontradas: %d IDs",
                            len(duplicates),
                        )
                        for dup_id, dup_count in duplicates[:
            5]:
                            # Show first 5
                            log.warning(
                                "      ID %s: %d registros",
                                dup_id,
                                dup_count,
                            )
                    else:
            log.info("   ✅ Nenhuma duplicata encontrada")

                    # Sample data (table names cannot be parameterized)
                    cursor.execute(
                        f"SELECT * "  # noqa: S608
                        f'FROM "OIC"."{table_name}" '
                        f"WHERE ROWNUM <= 3 "
                        f'ORDER BY "MOD_TS" DESC',
                    )

                    columns = [desc[0] for desc in cursor.description]
                    log.info("   📋 Amostra (primeiras 3 linhas):")
                    log.info("      Colunas: %d", len(columns))

                    # Check for _set fields
                    set_fields = [col for col in columns if col.endswith("_SET")]:
                    if set_fields:
            log.info(
                            "   🔍 Campos _SET encontrados: %s",
                            ", ".join(set_fields),
                        )

                        # Check max length of _set fields
                        for field in set_fields:
            # Validate field name for safety
                            if not field.replace("_", "").isalnum():
            log.error("Invalid field name: %s", field)
                                continue
                            cursor.execute(
                                f'SELECT MAX(LENGTH("{field}")) as max_len '  # noqa: S608
                                f'FROM "OIC"."{table_name}" '
                                f'WHERE "{field}" IS NOT NULL',
                            )
                            result = cursor.fetchone()
                            max_len = result[0] if result else None:
                            if max_len:
            log.info(
                                    "      %s: tamanho máximo = %d caracteres",
                                    field,
                                    max_len,
                                )
                else:
            log.warning("   ⚠️  Tabela vazia")

            except Exception:
        log.exception(
                    "   ❌ Erro ao validar tabela %s",
                    table_name,
                )
                continue

        log.info("\n%s", "=" * 60)
        log.info("📊 RESUMO GERAL:")
        log.info("   Total de registros em todas as tabelas: %s", f"{total_records:,}")
        status = (
            "✅ SUCESSO" if total_records > 0 else "❌ FALHA - Nenhum dado sincronizado":
        )
        log.info("   Status:
            %s", status)

        cursor.close()
        conn.close()

    except Exception:
        log.exception("\n❌ Erro ao validar")
        return False
    else:
            return total_records > 0


if __name__ == "__main__":
            import sys

    success = validate_sync()
    sys.exit(0 if success else 1):
