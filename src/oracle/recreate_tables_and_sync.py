#!/usr/bin/env python3
"""Script para recriar tabelas e executar sync full.
Objetivo: Verificar comportamento completo do ambiente.
"""

import os
import subprocess
import sys
import time
from datetime import datetime

from connection_manager import create_connection_manager_from_env


def drop_all_wms_tables():
    """Drop todas as tabelas WMS_ e sem prefixo."""
    print("🗑️ REMOVENDO TODAS AS TABELAS WMS...")
    print("=" * 60)

    manager = create_connection_manager_from_env()

    try:
        conn = manager.connect()
        cursor = conn.cursor()

        # Listar todas as tabelas que podem ser do WMS
        cursor.execute("""
            SELECT table_name
            FROM user_tables
            WHERE table_name IN (
                'WMS_ALLOCATION', 'WMS_ORDER_HDR', 'WMS_ORDER_DTL',
                'ALLOCATION', 'ORDER_HDR', 'ORDER_DTL'
            )
        """)

        tables = cursor.fetchall()

        if not tables:
            print("   ✅ Nenhuma tabela WMS encontrada")
        else:
            for (table_name,) in tables:
                try:
                    cursor.execute(f'DROP TABLE "{table_name}" CASCADE CONSTRAINTS')
                    print(f"   ✅ Tabela {table_name} removida")
                except Exception as e:
                    print(f"   ⚠️ Erro ao remover {table_name}: {e}")

        conn.commit()
        cursor.close()
        conn.close()

        print("\n✅ Limpeza concluída")

    except Exception as e:
        print(f"❌ Erro durante limpeza: {e}")
        return False

    return True


def list_current_tables():
    """Lista tabelas atuais do schema."""
    print("\n📋 TABELAS ATUAIS NO SCHEMA:")
    print("-" * 40)

    manager = create_connection_manager_from_env()

    try:
        conn = manager.connect()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT table_name, num_rows
            FROM user_tables
            WHERE table_name LIKE '%ALLOCATION%'
               OR table_name LIKE '%ORDER%'
            ORDER BY table_name
        """)

        tables = cursor.fetchall()

        if not tables:
            print("   Nenhuma tabela relevante encontrada")
        else:
            for table_name, num_rows in tables:
                print(f"   {table_name}: {num_rows or 0} registros")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"   ❌ Erro ao listar tabelas: {e}")


def check_table_structure(table_name):
    """Verifica estrutura de uma tabela."""
    manager = create_connection_manager_from_env()

    try:
        conn = manager.connect()
        cursor = conn.cursor()

        # Verificar colunas
        cursor.execute(f"""
            SELECT column_name, data_type, data_length
            FROM user_tab_columns
            WHERE table_name = '{table_name}'
            ORDER BY column_id
        """)

        columns = cursor.fetchall()

        if columns:
            print(f"\n   📊 Estrutura da tabela {table_name}:")
            print(f"   Total de colunas: {len(columns)}")

            # Mostrar algumas colunas importantes
            set_fields = []
            for col_name, data_type, data_length in columns:
                if col_name.endswith("_SET"):
                    set_fields.append(f"{col_name} ({data_type} {data_length})")

            if set_fields:
                print(f"   Campos _SET encontrados: {', '.join(set_fields)}")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"   ⚠️ Erro ao verificar estrutura: {e}")


def run_full_sync():
    """Executa sync full via make."""
    print("\n🚀 EXECUTANDO SYNC FULL...")
    print("=" * 60)

    os.chdir("/home/marlonsc/flext/gruponos-meltano-native")

    # Criar diretório de logs se não existir
    os.makedirs("logs/sync", exist_ok=True)

    # Nome do arquivo de log
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"logs/sync/recreate_test_{timestamp}.log"

    print(f"   📝 Log sendo gravado em: {log_file}")
    print("   ⏳ Aguarde o sync completar...")

    # Executar o sync
    with open(log_file, "w", encoding="utf-8") as log:
        process = subprocess.Popen(
            ["make", "full-sync-debug"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        # Monitorar o progresso
        start_time = time.time()
        while True:
            line = process.stdout.readline()
            if not line:
                break

            log.write(line)

            # Mostrar algumas linhas importantes
            if any(keyword in line for keyword in ["BATCH", "COMPLETED", "ERROR", "TRUNCATE", "table_name"]):
                print(f"   {line.strip()}")

        process.wait()
        duration = time.time() - start_time

    print(f"\n   ⏱️ Sync completado em {duration:.1f} segundos")

    # Verificar se houve erros
    with open(log_file, encoding="utf-8") as log:
        content = log.read()
        if "ERROR" in content or "FAILED" in content:
            print("   ⚠️ ATENÇÃO: Erros encontrados no log!")

            # Mostrar erros principais
            for line in content.split("\n"):
                if "ERROR" in line or "ORA-" in line:
                    print(f"      {line.strip()}")
        else:
            print("   ✅ Sync aparentemente completado sem erros")

    return log_file


def analyze_results():
    """Analisa resultados finais."""
    print("\n📊 ANÁLISE DOS RESULTADOS:")
    print("=" * 60)

    manager = create_connection_manager_from_env()

    try:
        conn = manager.connect()
        cursor = conn.cursor()

        # Verificar todas as possíveis tabelas
        tables_to_check = [
            ("WMS_ALLOCATION", "allocation"),
            ("WMS_ORDER_HDR", "order_hdr"),
            ("WMS_ORDER_DTL", "order_dtl"),
            ("ALLOCATION", "allocation"),
            ("ORDER_HDR", "order_hdr"),
            ("ORDER_DTL", "order_dtl")
        ]

        found_tables = {}

        for table_name, _entity in tables_to_check:
            cursor.execute(f"""
                SELECT COUNT(*) as cnt
                FROM user_tables
                WHERE table_name = '{table_name}'
            """)

            exists = cursor.fetchone()[0] > 0

            if exists:
                cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
                count = cursor.fetchone()[0]
                found_tables[table_name] = count

        print("\n   📋 TABELAS ENCONTRADAS:")
        if not found_tables:
            print("   ❌ NENHUMA TABELA ENCONTRADA!")
        else:
            for table_name, count in found_tables.items():
                print(f"   - {table_name}: {count} registros")

                # Verificar estrutura se for WMS_
                if table_name.startswith("WMS_"):
                    check_table_structure(table_name)

        # Resumo
        print("\n   🎯 RESUMO:")
        wms_tables = [t for t in found_tables if t.startswith("WMS_")]
        non_wms_tables = [t for t in found_tables if not t.startswith("WMS_")]

        print(f"   - Tabelas com prefixo WMS_: {len(wms_tables)}")
        print(f"   - Tabelas sem prefixo: {len(non_wms_tables)}")
        print(f"   - Total de registros: {sum(found_tables.values())}")

        if len(wms_tables) == 3 and len(non_wms_tables) == 0:
            print("\n   ✅ SUCESSO: Todas as tabelas criadas com prefixo WMS_ corretamente!")
        elif len(non_wms_tables) == 3 and len(wms_tables) == 0:
            print("\n   ⚠️ PROBLEMA: Tabelas criadas SEM o prefixo WMS_!")
        else:
            print("\n   ❌ PROBLEMA: Mistura de tabelas com e sem prefixo!")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"   ❌ Erro na análise: {e}")


def main():
    """Executa o ciclo completo."""
    print("🔄 CICLO COMPLETO: RECRIAR TABELAS E SYNC")
    print("=" * 70)
    print(f"Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 1. Listar estado atual
    list_current_tables()

    # 2. Limpar tabelas
    if not drop_all_wms_tables():
        print("❌ Falha na limpeza, abortando...")
        return 1

    # 3. Confirmar limpeza
    print("\n📋 CONFIRMANDO LIMPEZA:")
    list_current_tables()

    # 4. Executar sync
    log_file = run_full_sync()

    # 5. Analisar resultados
    analyze_results()

    print("\n✅ Ciclo completo finalizado!")
    print(f"📝 Log completo em: {log_file}")
    print(f"Fim: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
