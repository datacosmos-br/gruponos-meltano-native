#!/usr/bin/env python3
"""Oracle Database Validation Script
Validates data integrity and connection for GrupoNOS Meltano Native project
"""

import os
import sys
from datetime import datetime

import oracledb


def validate_oracle():
    """Validate Oracle database connection and data."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"logs/validation/oracle_validation_{timestamp}.log"

    # Ensure log directory exists
    os.makedirs("logs/validation", exist_ok=True)

    try:
        # Get Oracle connection parameters from environment
        host = os.getenv("FLEXT_TARGET_ORACLE_HOST")
        port = int(os.getenv("FLEXT_TARGET_ORACLE_PORT", 1522))
        service_name = os.getenv("FLEXT_TARGET_ORACLE_SERVICE_NAME")
        username = os.getenv("FLEXT_TARGET_ORACLE_USERNAME")
        password = os.getenv("FLEXT_TARGET_ORACLE_PASSWORD")
        protocol = os.getenv("FLEXT_TARGET_ORACLE_PROTOCOL", "tcps")

        print(f"🔗 Conectando ao Oracle: {host}:{port}")

        # Connect to Oracle
        if protocol == "tcps":
            dsn = f"(DESCRIPTION=(ADDRESS=(PROTOCOL=TCPS)(HOST={host})(PORT={port}))(CONNECT_DATA=(SERVICE_NAME={service_name})))"
            # For validation, disable SSL verification to avoid certificate issues
            try:
                conn = oracledb.connect(user=username, password=password, dsn=dsn, ssl_server_dn_match=False)
            except Exception as ssl_error:
                print(f"⚠️  Erro SSL: {ssl_error}")
                print("🔄 Tentando conexão sem SSL...")
                # Fallback to non-SSL connection for validation
                dsn_fallback = f"(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST={host})(PORT={port}))(CONNECT_DATA=(SERVICE_NAME={service_name})))"
                conn = oracledb.connect(user=username, password=password, dsn=dsn_fallback)
        else:
            conn = oracledb.connect(user=username, password=password, host=host, port=port, service_name=service_name)

        cursor = conn.cursor()

        with open(log_file, "w") as f:
            f.write(f"{datetime.now()} - INÍCIO: Validação Oracle\n")

            print("📊 Verificando tabelas...")
            # Check for existing tables
            cursor.execute("""
                SELECT table_name FROM user_tables 
                WHERE table_name LIKE '%ALLOCATION%' 
                OR table_name LIKE '%ORDER%'
                OR table_name LIKE 'TAP_%'
                ORDER BY table_name
            """)
            tables = cursor.fetchall()
            f.write(f"{datetime.now()} - TABELAS ENCONTRADAS: {len(tables)}\n")

            if not tables:
                print("⚠️  Nenhuma tabela encontrada - pipeline ainda não executou")
                f.write(f"{datetime.now()} - AVISO: Nenhuma tabela encontrada\n")
            else:
                print(f"✅ Encontradas {len(tables)} tabelas")

                # Count records in each table
                for table in tables:
                    table_name = table[0]
                    try:
                        cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
                        count = cursor.fetchone()[0]
                        f.write(f"{datetime.now()} - TABELA {table_name}: {count} registros\n")
                        print(f"  📄 {table_name}: {count:,} registros")

                        # Get sample data
                        if count > 0:
                            cursor.execute(f'SELECT * FROM "{table_name}" WHERE ROWNUM <= 3')
                            sample = cursor.fetchall()
                            f.write(f"{datetime.now()} - AMOSTRA {table_name}: {len(sample)} registros\n")

                    except Exception as e:
                        f.write(f"{datetime.now()} - ERRO TABELA {table_name}: {e!s}\n")
                        print(f"  ❌ Erro ao acessar {table_name}: {e!s}")

            # Check Oracle version and capabilities
            cursor.execute("SELECT banner FROM v$version WHERE ROWNUM = 1")
            version = cursor.fetchone()[0]
            f.write(f"{datetime.now()} - VERSÃO ORACLE: {version}\n")
            print(f"🏷️  Oracle Version: {version}")

            # Check current user and schema
            cursor.execute("SELECT USER FROM DUAL")
            current_user = cursor.fetchone()[0]
            f.write(f"{datetime.now()} - USUÁRIO ATUAL: {current_user}\n")
            print(f"👤 Usuário atual: {current_user}")

            f.write(f"{datetime.now()} - SUCESSO: Validação Oracle concluída\n")

        cursor.close()
        conn.close()

        print("✅ Validação Oracle concluída com sucesso")
        print(f"📄 Log salvo em: {log_file}")
        return True

    except Exception as e:
        error_msg = f"{datetime.now()} - ERRO: {e!s}"
        try:
            with open(log_file, "a") as f:
                f.write(error_msg + "\n")
        except:
            pass
        print(f"❌ Erro na validação Oracle: {e!s}")
        return False

if __name__ == "__main__":
    success = validate_oracle()
    sys.exit(0 if success else 1)
