#!/usr/bin/env python3
"""Script para analisar comportamento de dados Oracle entre syncs"""

import os
from datetime import datetime

import oracledb


def check_overwrite_behavior():
    """Analisa se dados são substituídos ou acumulados"""
    print("🔍 ANALISANDO COMPORTAMENTO OVERWRITE vs RECOVERY...")
    print("📋 Verificando se dados são substituídos ou acumulados...")
    print()

    # Connection string from environment
    conn_str = f"{os.getenv('TARGET_ORACLE_USERNAME')}/{os.getenv('TARGET_ORACLE_PASSWORD')}@{os.getenv('TARGET_ORACLE_HOST')}:{os.getenv('TARGET_ORACLE_PORT')}/{os.getenv('TARGET_ORACLE_SERVICE_NAME')}"

    conn = oracledb.connect(conn_str)
    cursor = conn.cursor()

    print("📊 ANÁLISE DE OVERWRITE BEHAVIOR:")
    print()

    for table in ["WMS_ALLOCATION", "WMS_ORDER_HDR", "WMS_ORDER_DTL"]:
        try:
            # Check mod_ts range (source data timestamps)
            cursor.execute(f"""
                SELECT COUNT(*) as total, 
                       MIN(mod_ts) as oldest, 
                       MAX(mod_ts) as newest 
                FROM {table}
            """)
            result = cursor.fetchone()

            print(f"🔸 {table}:")
            print(f"   Total registros: {result[0]}")
            print(f"   Data range (mod_ts): {result[1]} → {result[2]}")

            # Check TK_DATE range (actual insert timestamps)
            cursor.execute(f"""
                SELECT MIN(TK_DATE) as first_insert, 
                       MAX(TK_DATE) as last_insert 
                FROM {table}
            """)
            tk_result = cursor.fetchone()
            print(f"   Insert range (TK_DATE): {tk_result[0]} → {tk_result[1]}")

            # Check if there are duplicates (would indicate accumulation vs overwrite)
            cursor.execute(f"""
                SELECT COUNT(*) as total_rows,
                       COUNT(DISTINCT id) as unique_ids,
                       CASE WHEN COUNT(*) > COUNT(DISTINCT id) 
                            THEN 'DUPLICATES FOUND' 
                            ELSE 'NO DUPLICATES' 
                       END as duplicate_status
                FROM {table}
            """)
            dup_result = cursor.fetchone()
            print(f"   Duplicates: {dup_result[2]} (Total: {dup_result[0]}, Unique IDs: {dup_result[1]})")
            print()

        except Exception as e:
            print(f"❌ Erro em {table}: {e}")
            print()

    cursor.close()
    conn.close()


def check_incremental_order():
    """Verifica se incremental está ordenado por mod_ts"""
    print("🔍 VERIFICANDO ORDEM INCREMENTAL POR MOD_TS...")
    print()

    conn_str = f"{os.getenv('TARGET_ORACLE_USERNAME')}/{os.getenv('TARGET_ORACLE_PASSWORD')}@{os.getenv('TARGET_ORACLE_HOST')}:{os.getenv('TARGET_ORACLE_PORT')}/{os.getenv('TARGET_ORACLE_SERVICE_NAME')}"

    conn = oracledb.connect(conn_str)
    cursor = conn.cursor()

    print("📊 ALLOCATION - Ordem incremental (mod_ts):")
    cursor.execute("""
        SELECT id, mod_ts, 
               ROW_NUMBER() OVER (ORDER BY mod_ts ASC) as row_order 
        FROM WMS_ALLOCATION 
        ORDER BY mod_ts ASC 
        FETCH FIRST 10 ROWS ONLY
    """)

    for row in cursor.fetchall():
        print(f"  ID: {row[0]} | mod_ts: {row[1]} | order: {row[2]}")

    print()
    print("📊 Estatísticas temporais:")
    cursor.execute("""
        SELECT COUNT(*) as total, 
               MIN(mod_ts) as oldest, 
               MAX(mod_ts) as newest, 
               COUNT(DISTINCT mod_ts) as unique_ts 
        FROM WMS_ALLOCATION
    """)
    result = cursor.fetchone()
    print(f"  Total: {result[0]} | Oldest: {result[1]} | Newest: {result[2]} | Unique timestamps: {result[3]}")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "overwrite":
            check_overwrite_behavior()
        elif sys.argv[1] == "order":
            check_incremental_order()
        else:
            print("Usage: python check_data_behavior.py [overwrite|order]")
    else:
        check_overwrite_behavior()
        print()
        check_incremental_order()
