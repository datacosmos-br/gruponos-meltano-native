#!/usr/bin/env python3
"""Validate Oracle data after pipeline execution - CORRECTED VERSION."""

from __future__ import annotations

import os
import sys
from datetime import UTC, datetime

import oracledb
from flext_observability.logging import get_logger

# Setup logger
log = get_logger(__name__)


def create_oracle_connection() -> oracledb.Connection:
    """Create Oracle connection using environment variables or defaults."""
    # Use same config as test_full_pipeline.py
    config = {
        "username": os.getenv("DATABASE__USERNAME", "oic"),
        "password": os.getenv("DATABASE__PASSWORD", "aehaz232dfNuupah_#"),
        "host": os.getenv("DATABASE__HOST", "10.93.10.114"),
        "port": int(os.getenv("DATABASE__PORT", "1522")),
        "service_name": os.getenv(
            "DATABASE__SERVICE_NAME",
            "gbe8f3f2dbbc562_dwpdb_low.adb.oraclecloud.com",
        ),
        "protocol": os.getenv("DATABASE__PROTOCOL", "tcps"),
    }

    # Build DSN for Oracle connection
    dsn = oracledb.makedsn(
        host=config["host"],
        port=config["port"],
        service_name=config["service_name"],
    )

    # Create connection with SSL settings for Oracle Autonomous Database
    return oracledb.connect(
        user=config["username"],
        password=config["password"],
        dsn=dsn,
        ssl_server_dn_match=False,  # Skip hostname verification
    )


def validate_oracle_data() -> bool:
    """Validate data in Oracle tables after sync."""
    log.info("🔍 VALIDANDO DADOS NO ORACLE...")
    log.info("📅 %s", datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S"))
    log.info("-" * 60)

    try:
        conn = create_oracle_connection()
        cursor = conn.cursor()

        # Tables to validate - check TEST_ prefixed tables
        tables = [
            ("TEST_ALLOCATION", "allocation"),
            ("TEST_WMS_ALLOCATION", "allocation"),
            ("TEST_ORDER_HDR", "order_hdr"),
            ("TEST_ORDER_DTL", "order_dtl"),
        ]

        total_records = 0
        schema_name = "OIC"

        for table_name, entity_name in tables:
            log.info("\\n📊 Tabela: %s (%s)", table_name, entity_name)

            try:
                # Count records - validate table name for safety
                if not table_name.replace("_", "").replace("TEST", "").isalnum():
                    log.error("Invalid table name: %s", table_name)
                    continue

                cursor.execute(
                    f'SELECT COUNT(*) FROM "{schema_name}"."{table_name}"',  # noqa: S608
                )
                count = cursor.fetchone()[0]
                total_records += count
                log.info("   Total de registros: %s", f"{count:,}")

                if count > 0:
                    # Get sample data
                    cursor.execute(
                        f"SELECT * "  # noqa: S608
                        f'FROM "{schema_name}"."{table_name}" '
                        f"WHERE ROWNUM <= 3 "
                        f'ORDER BY "_SDC_EXTRACTED_AT" DESC',
                    )

                    columns = [desc[0] for desc in cursor.description]
                    log.info("   📋 Colunas encontradas: %d", len(columns))
                    log.info("   📋 Primeiras colunas: %s", columns[:5])

                    # Check for Singer metadata columns
                    singer_cols = [col for col in columns if col.startswith("_SDC_")]
                    if singer_cols:
                        log.info("   ✅ Singer metadata presente: %s", singer_cols)

                    # Check for ID column
                    if "ID" in columns:
                        cursor.execute(
                            f'SELECT MIN("ID"), MAX("ID") '  # noqa: S608
                            f'FROM "{schema_name}"."{table_name}"',
                        )
                        min_id, max_id = cursor.fetchone()
                        log.info("   📊 Range de IDs: %s - %s", min_id, max_id)

                else:
                    log.warning("   ⚠️  Tabela vazia")

            except Exception as e:
                log.exception("   ❌ Erro ao validar tabela %s: %s", table_name, e)
                continue

        log.info("\\n%s", "=" * 60)
        log.info("📊 RESUMO GERAL:")
        log.info("   Total de registros em todas as tabelas: %s", f"{total_records:,}")
        status = (
            "✅ SUCESSO" if total_records > 0 else "❌ FALHA - Nenhum dado sincronizado"
        )
        log.info("   Status: %s", status)

        cursor.close()
        conn.close()
        return total_records > 0

    except Exception as e:
        log.exception("\\n❌ Erro ao validar: %s", e)
        return False


if __name__ == "__main__":
    success = validate_oracle_data()
    sys.exit(0 if success else 1)
