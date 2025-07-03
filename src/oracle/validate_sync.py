#!/usr/bin/env python3
"""Validate data in Oracle tables after sync."""

import os
from datetime import datetime

from connection_manager import create_connection_manager_from_env


def validate_sync():
    """Validate sync results in Oracle tables."""
    print("🔍 VALIDANDO DADOS NO ORACLE...")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)

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
            ("ORDER_DTL", "order_dtl")
        ]

        total_records = 0

        for table_name, entity_name in tables:
            print(f"\n📊 Tabela: {table_name} ({entity_name})")

            # Count records
            cursor.execute(f'SELECT COUNT(*) FROM "OIC"."{table_name}"')
            count = cursor.fetchone()[0]
            total_records += count
            print(f"   Total de registros: {count:,}")

            if count > 0:
                # Get date range
                cursor.execute(f"""
                    SELECT 
                        MIN("MOD_TS") as min_date,
                        MAX("MOD_TS") as max_date,
                        COUNT(DISTINCT "ID") as unique_ids
                    FROM "OIC"."{table_name}"
                """)
                min_date, max_date, unique_ids = cursor.fetchone()

                print(f"   Data mais antiga: {min_date}")
                print(f"   Data mais recente: {max_date}")
                print(f"   IDs únicos: {unique_ids:,}")

                # Check for duplicates
                cursor.execute(f"""
                    SELECT "ID", COUNT(*) as cnt
                    FROM "OIC"."{table_name}"
                    GROUP BY "ID"
                    HAVING COUNT(*) > 1
                """)
                duplicates = cursor.fetchall()

                if duplicates:
                    print(f"   ⚠️  Duplicatas encontradas: {len(duplicates)} IDs")
                    for dup_id, dup_count in duplicates[:5]:  # Show first 5
                        print(f"      ID {dup_id}: {dup_count} registros")
                else:
                    print("   ✅ Nenhuma duplicata encontrada")

                # Sample data
                cursor.execute(f"""
                    SELECT *
                    FROM "OIC"."{table_name}"
                    WHERE ROWNUM <= 3
                    ORDER BY "MOD_TS" DESC
                """)

                columns = [desc[0] for desc in cursor.description]
                print("   📋 Amostra (primeiras 3 linhas):")
                print(f"      Colunas: {len(columns)}")

                # Check for _set fields
                set_fields = [col for col in columns if col.endswith("_SET")]
                if set_fields:
                    print(f"   🔍 Campos _SET encontrados: {', '.join(set_fields)}")

                    # Check max length of _set fields
                    for field in set_fields:
                        cursor.execute(f"""
                            SELECT MAX(LENGTH("{field}")) as max_len
                            FROM "OIC"."{table_name}"
                            WHERE "{field}" IS NOT NULL
                        """)
                        max_len = cursor.fetchone()[0]
                        if max_len:
                            print(f"      {field}: tamanho máximo = {max_len} caracteres")
            else:
                print("   ⚠️  Tabela vazia")

        print("\n" + "=" * 60)
        print("📊 RESUMO GERAL:")
        print(f"   Total de registros em todas as tabelas: {total_records:,}")
        print(f"   Status: {'✅ SUCESSO' if total_records > 0 else '❌ FALHA - Nenhum dado sincronizado'}")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"\n❌ Erro ao validar: {e}")
        return False

    return total_records > 0


if __name__ == "__main__":
    validate_sync()
