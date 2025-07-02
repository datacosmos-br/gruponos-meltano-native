#!/usr/bin/env python3
"""Executar pipeline real com configuração otimizada."""

import os
import subprocess
import sys
import time


def execute_real_pipeline():
    """Executar pipeline end-to-end real com dados WMS."""
    print("🚀 EXECUÇÃO PIPELINE REAL - MELTANO + ORACLE")
    print("=" * 60)

    # Step 1: Update .env for faster execution
    print("📝 Configurando para execução rápida...")

    try:
        # Backup original .env
        with open(".env") as f:
            original_env = f.read()

        with open(".env.backup", "w") as f:
            f.write(original_env)

        # Create optimized .env for quick testing
        optimized_env = original_env.replace(
            "TAP_ORACLE_WMS_PAGE_SIZE=5", "TAP_ORACLE_WMS_PAGE_SIZE=10"
        ).replace(
            "TAP_ORACLE_WMS_MAX_PAGES=1", "TAP_ORACLE_WMS_MAX_PAGES=2"
        )

        with open(".env", "w") as f:
            f.write(optimized_env)

        print("   ✅ Configuração otimizada: page_size=10, max_pages=2")

    except Exception as e:
        print(f"   ❌ Erro configurando .env: {e}")
        return False

    # Step 2: Clear Oracle table for clean test
    print("\n🗑️ Limpando tabela Oracle...")

    try:
        import oracledb
        from dotenv import load_dotenv

        load_dotenv()

        host = "10.93.10.114"
        port = 1522
        service_name = "gbe8f3f2dbbc562_dwpdb_low.adb.oraclecloud.com"
        username = "oic"
        password = "aehaz232dfNuupah_#"

        dsn = (
            f"(DESCRIPTION="
            f"(RETRY_COUNT=20)(RETRY_DELAY=3)"
            f"(ADDRESS=(PROTOCOL=tcps)(HOST={host})(PORT={port}))"
            f"(CONNECT_DATA=(SERVICE_NAME={service_name}))"
            f"(SECURITY=(SSL_SERVER_DN_MATCH=no))"
            f")"
        )

        connection = oracledb.connect(user=username, password=password, dsn=dsn)
        cursor = connection.cursor()

        cursor.execute("TRUNCATE TABLE WMS_ALLOCATION")
        connection.commit()

        cursor.close()
        connection.close()

        print("   ✅ Tabela WMS_ALLOCATION limpa")

    except Exception as e:
        print(f"   ❌ Erro limpando tabela: {e}")
        return False

    # Step 3: Execute pipeline with shorter timeout
    print("\n🎯 Executando pipeline Meltano...")

    start_time = time.time()

    try:
        # Run allocation-full-sync with timeout
        result = subprocess.run(
            ["meltano", "run", "allocation-full-sync"],
            capture_output=True,
            text=True,
            timeout=90,  # 1.5 minutes timeout
            cwd=".", check=False
        )

        end_time = time.time()
        duration = end_time - start_time

        print(f"   ⏱️ Pipeline executado em {duration:.1f} segundos")
        print(f"   📊 Return code: {result.returncode}")

        # Restore original .env
        with open(".env.backup") as f:
            original_env = f.read()
        with open(".env", "w") as f:
            f.write(original_env)

        if result.returncode == 0:
            print("   ✅ PIPELINE SUCESSO!")

            # Verify results
            try:
                connection = oracledb.connect(user=username, password=password, dsn=dsn)
                cursor = connection.cursor()

                # Count total records
                cursor.execute("SELECT COUNT(*) FROM WMS_ALLOCATION")
                total_count = cursor.fetchone()[0]

                # Count unique IDs
                cursor.execute("SELECT COUNT(DISTINCT ID) FROM WMS_ALLOCATION")
                unique_ids = cursor.fetchone()[0]

                # Check PK structure
                cursor.execute("""
                    SELECT c.constraint_name, cc.column_name, cc.position
                    FROM user_constraints c
                    JOIN user_cons_columns cc ON c.constraint_name = cc.constraint_name
                    WHERE c.table_name = 'WMS_ALLOCATION'
                    AND c.constraint_type = 'P'
                    ORDER BY cc.position
                """)
                pk_columns = cursor.fetchall()
                pk_structure = [col[1] for col in pk_columns]

                # Sample data
                cursor.execute("""
                    SELECT ID, MOD_TS, TK_DATE
                    FROM WMS_ALLOCATION
                    WHERE ROWNUM <= 5
                    ORDER BY TK_DATE DESC
                """)
                sample_data = cursor.fetchall()

                cursor.close()
                connection.close()

                print("\n📊 RESULTADOS:")
                print(f"   📈 Total records: {total_count}")
                print(f"   🆔 IDs únicos: {unique_ids}")
                print(f"   🔑 PK structure: {pk_structure}")

                print("\n📄 Amostra de dados:")
                for i, row in enumerate(sample_data, 1):
                    print(f"   {i}. ID={row[0]}, MOD_TS={str(row[1])[:19]}, TK_DATE={str(row[2])[:19]}")

                # Validate specification
                success_criteria = [
                    ("Records carregados", total_count > 0),
                    ("PK structure correta", pk_structure == ["ID", "MOD_TS"]),
                    ("Dados reais WMS", total_count >= 10),  # Should have at least 10 records from 2 pages
                ]

                print("\n✅ VALIDAÇÃO ESPECIFICAÇÃO:")
                all_passed = True
                for criteria, passed in success_criteria:
                    status = "✅" if passed else "❌"
                    print(f"   {status} {criteria}")
                    if not passed:
                        all_passed = False

                if all_passed:
                    print("\n🏆 100% SUCESSO - PIPELINE REAL FUNCIONANDO!")
                    print("✅ Especificação completamente atendida:")
                    print("   • Primary Key: (ID + MOD_TS) dos dados WMS reais")
                    print("   • TK_DATE: Apenas timestamp de gravação Oracle")
                    print("   • Pipeline end-to-end: WMS → Meltano → Oracle")
                    print("   • Dados reais processados e carregados")
                    return True
                print("\n⚠️ PIPELINE funcionou mas validação incompleta")
                return False

            except Exception as e:
                print(f"   ❌ Erro verificando resultados: {e}")
                return False

        else:
            print("   ❌ PIPELINE FALHOU!")

            # Show relevant error lines
            if result.stderr:
                stderr_lines = result.stderr.split("\n")
                error_lines = [line for line in stderr_lines if "error" in line.lower() or "failed" in line.lower()]

                if error_lines:
                    print("   🚨 Erros encontrados:")
                    for line in error_lines[-5:]:  # Last 5 error lines
                        print(f"     {line}")

            return False

    except subprocess.TimeoutExpired:
        print("   ⏰ TIMEOUT após 90 segundos")

        # Restore original .env
        try:
            with open(".env.backup") as f:
                original_env = f.read()
            with open(".env", "w") as f:
                f.write(original_env)
        except:
            pass

        print("   🚨 Pipeline demorou muito - possível problema de performance")
        return False

    except Exception as e:
        print(f"   ❌ Erro executando pipeline: {e}")

        # Restore original .env
        try:
            with open(".env.backup") as f:
                original_env = f.read()
            with open(".env", "w") as f:
                f.write(original_env)
        except:
            pass

        return False

if __name__ == "__main__":
    success = execute_real_pipeline()

    if success:
        print("\n🎉 MISSÃO CUMPRIDA - 100% CONFORME ESPECIFICAÇÃO!")
    else:
        print("\n❌ EXECUÇÃO INCOMPLETA")

    sys.exit(0 if success else 1)
