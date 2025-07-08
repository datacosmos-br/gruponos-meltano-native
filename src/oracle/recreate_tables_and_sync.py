"""Script para recriar tabelas e executar sync full.

Objetivo: Verificar comportamento completo do ambiente.
"""

from __future__ import annotations

import logging
import os
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

from src.oracle.connection_manager import create_connection_manager_from_env

try:
    from src.oracle.validate_sync import validate_sync
except ImportError:
    validate_sync = None  # type: ignore[assignment]

# Setup logger
log = logging.getLogger(__name__)


def drop_all_wms_tables() -> bool:
    """Drop todas as tabelas WMS_ e sem prefixo.

    Returns:
        True if successful, False otherwise
    """
    log.info("🗑️ REMOVENDO TODAS AS TABELAS WMS...")
    log.info("=" * 60)

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
            log.info("   ✅ Nenhuma tabela WMS encontrada")
        else:
            for (table_name,) in tables:
                try:
                    cursor.execute(f'DROP TABLE "{table_name}" CASCADE CONSTRAINTS')
                    log.info("   ✅ Tabela %s removida", table_name)
                except Exception as e:
                    log.warning("   ⚠️ Erro ao remover %s: %s", table_name, e)

        conn.commit()
        cursor.close()
        conn.close()

        log.info("\n✅ Limpeza concluída")
    except Exception:
        log.exception("❌ Erro durante limpeza")
        return False
    else:
        return True


def list_current_tables() -> None:
    """Lista tabelas atuais do schema."""
    log.info("\n📋 TABELAS ATUAIS NO SCHEMA:")
    log.info("-" * 40)

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
            log.info("   Nenhuma tabela relevante encontrada")
        else:
            for table_name, num_rows in tables:
                log.info("   %s: %d registros", table_name, num_rows or 0)

        cursor.close()
        conn.close()

    except Exception:
        log.exception("   ❌ Erro ao listar tabelas")


def check_table_structure(table_name: str) -> None:
    """Verifica estrutura de uma tabela.

    Args:
        table_name: Nome da tabela a verificar
    """
    manager = create_connection_manager_from_env()

    try:
        conn = manager.connect()
        cursor = conn.cursor()

        # Verificar colunas
        # Use parameterized query to avoid SQL injection
        cursor.execute("""
            SELECT column_name, data_type, data_length
            FROM user_tab_columns
            WHERE table_name = :table_name
            ORDER BY column_id
        """, {"table_name": table_name})

        columns = cursor.fetchall()

        if columns:
            log.info("📊 Estrutura da tabela %s:", table_name)
            max_columns_to_show = 10
            for col_name, data_type, data_length in columns[:max_columns_to_show]:
                log.info("   %s: %s(%s)", col_name, data_type, data_length or "")
            if len(columns) > max_columns_to_show:
                log.info("   ... e mais %d colunas", len(columns) - max_columns_to_show)
        else:
            log.warning("❌ Tabela %s não encontrada", table_name)

        cursor.close()
        conn.close()

    except Exception:
        log.exception("❌ Erro ao verificar estrutura")


def create_tables_with_ddl() -> bool:
    """Cria tabelas usando table_creator.py.

    Returns:
        True if successful, False otherwise
    """
    log.info("\n🔨 CRIANDO TABELAS COM DDL OTIMIZADO...")
    log.info("-" * 50)

    try:
        # Executar table_creator
        result = subprocess.run(
            [sys.executable, "-m", "src.oracle.table_creator"],
            cwd=Path(__file__).parent.parent.parent,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutes
            check=False,
        )

        if result.returncode == 0:
            log.info("✅ Tabelas criadas com sucesso")
            if result.stdout:
                log.info("Output: %s", result.stdout)
        log.error("❌ Erro ao criar tabelas")
        if result.stderr:
            log.error("Error: %s", result.stderr)
    except subprocess.TimeoutExpired:
        log.exception("❌ Timeout ao criar tabelas")
        return False
    except Exception:
        log.exception("❌ Erro ao executar table_creator")
        return False
    else:
        return True

    return False


def run_full_sync() -> bool:
    """Executa sync completo via meltano.

    Returns:
        True if successful, False otherwise
    """
    log.info("\n🚀 EXECUTANDO SYNC COMPLETO...")
    log.info("-" * 40)

    try:
        # Configurar ambiente
        env = os.environ.copy()

        # Executar meltano run
        cmd = [
            "/home/marlonsc/flext/.venv/bin/meltano",
            "run",
            "tap-oracle-wms-full",
            "target-oracle-full",
        ]

        log.info("Comando: %s", " ".join(cmd))

        start_time = time.time()

        result = subprocess.run(
            cmd,
            cwd="/home/marlonsc/flext/gruponos-meltano-native",
            env=env,
            capture_output=True,
            text=True,
            timeout=1800,  # 30 minutes
            check=False,
        )

        duration = time.time() - start_time
        log.info("Duração: %.1f segundos", duration)

        if result.returncode == 0:
            log.info("✅ Sync executado com sucesso")

            # Procurar por estatísticas no output
            lines = result.stdout.split("\n")
            for line in lines:
                if "records" in line.lower() or "extracted" in line.lower():
                    log.info("📊 %s", line.strip())

        log.error("❌ Sync falhou (código: %d)", result.returncode)
        if result.stderr:
            # Limit stderr output to 1000 characters
            stderr_limit = 1000
            log.error("Error: %s", result.stderr[:stderr_limit])
    except subprocess.TimeoutExpired:
        log.exception("❌ Timeout durante sync (30 minutos)")
        return False
    except Exception:
        log.exception("❌ Erro ao executar sync")
        return False
    else:
        return True

    return False


def validate_sync_results() -> bool:
    """Valida resultados do sync.

    Returns:
        True if validation successful, False otherwise
    """
    log.info("\n🔍 VALIDANDO RESULTADOS...")
    log.info("-" * 30)

    if validate_sync is None:
        log.error("❌ Módulo validate_sync não disponível")
        return False

    try:
        return validate_sync()
    except Exception:
        log.exception("❌ Erro na validação")
        return False


def main() -> int:
    """Função principal - executa todo o processo.

    Returns:
        0 if successful, 1 if failed
    """
    log.info("🏁 INICIANDO PROCESSO COMPLETO DE RECRIAÇÃO E SYNC")
    log.info("=" * 70)
    log.info("⏰ %s", datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC"))
    log.info("=" * 70)

    # 1. Listar tabelas atuais
    list_current_tables()

    # 2. Remover tabelas existentes
    if not drop_all_wms_tables():
        log.error("❌ Falha na limpeza de tabelas")
        return 1

    # 3. Criar novas tabelas
    if not create_tables_with_ddl():
        log.error("❌ Falha na criação de tabelas")
        return 1

    # 4. Verificar estrutura das tabelas criadas
    for table in ["WMS_ALLOCATION", "WMS_ORDER_HDR", "WMS_ORDER_DTL"]:
        check_table_structure(table)

    # 5. Executar sync completo
    if not run_full_sync():
        log.error("❌ Falha no sync")
        return 1

    # 6. Validar resultados
    if not validate_sync_results():
        log.error("❌ Falha na validação")
        return 1

    # 7. Relatório final
    separator = "=" * 70
    log.info("\n%s", separator)
    log.info("🎉 PROCESSO CONCLUÍDO COM SUCESSO!")
    log.info("✅ Tabelas recriadas")
    log.info("✅ Sync executado")
    log.info("✅ Dados validados")
    log.info(
        "⏰ Finalizado em: %s",
        datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC"),
    )
    log.info("=" * 70)

    return 0


if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        log.exception("\n❌ Processo interrompido pelo usuário")
        sys.exit(1)
    except Exception:
        log.exception("❌ Erro fatal")
        sys.exit(1)
