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

# Use centralized logger from flext-observability - ELIMINATE DUPLICATION
from flext_observability.logging import get_logger

from gruponos_meltano_native.config import get_config
from gruponos_meltano_native.oracle.connection_manager import OracleConnectionManager

# Always fail explicitly - no fallbacks allowed
from gruponos_meltano_native.oracle.validate_sync import validate_sync

# Setup logger
logger = get_logger(__name__)


def drop_all_wms_tables() -> bool:
    """Drop all WMS tables from the Oracle database.

    Returns:
        True if all tables were dropped successfully, False otherwise.

    """
    logger.info("🗑️ REMOVENDO TODAS AS TABELAS WMS...")
    logger.info("=" * 60)

    # Create connection using config from environment
    config = get_config()
    if config.target_oracle is None:
        logger.error("Target Oracle configuration not found")
        return False  # Return in error path

    manager = OracleConnectionManager(config.target_oracle.oracle)

    try:
        conn = manager.connect()
        cursor = conn.cursor()

        # Listar todas as tabelas que podem ser do WMS
        cursor.execute(
            """
            SELECT table_name
            FROM user_tables
            WHERE table_name IN (
                'WMS_ALLOCATION', 'WMS_ORDER_HDR', 'WMS_ORDER_DTL',
                'ALLOCATION', 'ORDER_HDR', 'ORDER_DTL'
            )
            """,
        )

        tables = cursor.fetchall()

        if not tables:
            logger.info("   ✅ Nenhuma tabela WMS encontrada")
        else:
            for (table_name,) in tables:
                try:
                    cursor.execute(f'DROP TABLE "{table_name}" CASCADE CONSTRAINTS')
                    logger.info("   ✅ Tabela %s removida", table_name)
                except (OSError, RuntimeError) as e:
                    logger.warning("   ⚠️ Erro ao remover %s: %s", table_name, e)

        conn.commit()
        cursor.close()
        conn.close()

        logger.info("\n✅ Limpeza concluída")
    except (OSError, RuntimeError):
        logger.exception("❌ Erro durante limpeza")
        return False  # Return in error path

    return True


def list_current_tables() -> None:
    """List all current WMS-related tables in the Oracle schema."""
    logger.info("\n📋 TABELAS ATUAIS NO SCHEMA:")
    logger.info("-" * 40)

    # Create connection using config from environment
    config = get_config()
    if config.target_oracle is None:
        logger.error("Target Oracle configuration not found")
        return

    manager = OracleConnectionManager(config.target_oracle.oracle)

    try:
        conn = manager.connect()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT table_name, num_rows
            FROM user_tables
            WHERE table_name LIKE '%ALLOCATION%'
               OR table_name LIKE '%ORDER%'
            ORDER BY table_name
            """,
        )

        tables = cursor.fetchall()

        if not tables:
            logger.info("   Nenhuma tabela relevante encontrada")
        else:
            for table_name, num_rows in tables:
                logger.info("   %s: %d registros", table_name, num_rows or 0)

        cursor.close()
        conn.close()

    except (OSError, RuntimeError):
        logger.exception("   ❌ Erro ao listar tabelas")


def check_table_structure(table_name: str) -> None:
    """Check the structure of a specific table.

    Args:
        table_name: Name of the table to check structure for.

    """
    # Create connection using config from environment
    config = get_config()
    if config.target_oracle is None:
        logger.error("Target Oracle configuration not found")
        return

    manager = OracleConnectionManager(config.target_oracle.oracle)

    try:
        conn = manager.connect()
        cursor = conn.cursor()

        # Verificar colunas
        # Use parameterized query to avoid SQL injection
        cursor.execute(
            """
            SELECT column_name, data_type, data_length
            FROM user_tab_columns
            WHERE table_name = :table_name
            ORDER BY column_id
            """,
            {"table_name": table_name},
        )

        columns = cursor.fetchall()

        if columns:
            logger.info("📊 Estrutura da tabela %s:", table_name)
            max_columns_to_show = 10
            for col_name, data_type, data_length in columns[:max_columns_to_show]:
                logger.info("   %s: %s(%s)", col_name, data_type, data_length or "")
            if len(columns) > max_columns_to_show:
                logger.info(
                    "   ... e mais %d colunas",
                    len(columns) - max_columns_to_show,
                )
        else:
            logger.warning("❌ Tabela %s não encontrada", table_name)

        cursor.close()
        conn.close()

    except (OSError, RuntimeError):
        logger.exception("❌ Erro ao verificar estrutura")


def create_tables_with_ddl() -> bool:
    """Create WMS tables using optimized DDL from table creator.

    Returns:
        True if tables were created successfully, False otherwise.

    """
    logger.info("\n🔨 CRIANDO TABELAS COM DDL OTIMIZADO...")
    logger.info("-" * 50)

    try:
        # Executar table_creator
        result = subprocess.run(  # Trusted internal module execution
            [sys.executable, "-m", "src.oracle.table_creator"],
            cwd=Path(__file__).parent.parent.parent,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutes
            check=False,
        )

        if result.returncode == 0:
            logger.info("✅ Tabelas criadas com sucesso")
            if result.stdout:
                logger.info("Output: %s", result.stdout)
            return True
        logger.error("❌ Erro ao criar tabelas")
        if result.stderr:
            logger.error("Error: %s", result.stderr)
        return False  # Return in error path
    except subprocess.TimeoutExpired:
        logger.exception("❌ Timeout ao criar tabelas")
        return False  # Return in error path
    except (OSError, RuntimeError):
        logger.exception("❌ Erro ao executar table_creator")
        return False  # Return in error path


def run_full_sync() -> bool:
    """Execute full sync using Meltano with tap-oracle-wms.

    Returns:
        True if sync completed successfully, False otherwise.

    """
    logger.info("\n🚀 EXECUTANDO SYNC COMPLETO...")
    logger.info("-" * 40)

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

        logger.info("Comando: %s", " ".join(cmd))

        start_time = time.time()

        result = subprocess.run(  # Trusted meltano command execution
            cmd,
            cwd="/home/marlonsc/flext/gruponos-meltano-native",
            env=env,
            capture_output=True,
            text=True,
            timeout=1800,  # 30 minutes
            check=False,
        )

        duration = time.time() - start_time
        logger.info("Duração: %.1f segundos", duration)

        if result.returncode == 0:
            logger.info("✅ Sync executado com sucesso")

            # Procurar por estatísticas no output
            lines = result.stdout.split("\n")
            for line in lines:
                if "records" in line.lower() or "extracted" in line.lower():
                    logger.info("📊 %s", line.strip())
            return True
        logger.error("❌ Sync falhou (código: %d)", result.returncode)
        if result.stderr:
            # Limit stderr output to 1000 characters
            stderr_limit = 1000
            logger.error("Error: %s", result.stderr[:stderr_limit])
        return False  # Return in error path
    except subprocess.TimeoutExpired:
        logger.exception("❌ Timeout durante sync (30 minutos)")
        return False  # Return in error path
    except (OSError, RuntimeError):
        logger.exception("❌ Erro ao executar sync")
        return False  # Return in error path


def validate_sync_results() -> bool:
    """Validate the results of the sync operation.

    Returns:
        True if validation passed, False otherwise.

    """
    logger.info("\n🔍 VALIDANDO RESULTADOS...")
    logger.info("-" * 30)

    try:
        return validate_sync()
    except (OSError, RuntimeError):
        logger.exception("❌ Erro na validação")
        return False  # Return in error path


def main() -> int:
    """Execute the complete recreation and sync process.

    Returns:
        Exit code: 0 for success, 1 for failure.

    """
    logger.info("🏁 INICIANDO PROCESSO COMPLETO DE RECRIAÇÃO E SYNC")
    logger.info("=" * 70)
    logger.info("⏰ %s", datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC"))
    logger.info("=" * 70)

    # 1. Listar tabelas atuais
    list_current_tables()

    # 2. Remover tabelas existentes
    if not drop_all_wms_tables():
        logger.error("❌ Falha na limpeza de tabelas")
        return 1

    # 3. Criar novas tabelas
    if not create_tables_with_ddl():
        logger.error("❌ Falha na criação de tabelas")
        return 1

    # 4. Verificar estrutura das tabelas criadas
    for table in ["WMS_ALLOCATION", "WMS_ORDER_HDR", "WMS_ORDER_DTL"]:
        check_table_structure(table)

    # 5. Executar sync completo
    if not run_full_sync():
        logger.error("❌ Falha no sync")
        return 1

    # 6. Validar resultados
    if not validate_sync_results():
        logger.error("❌ Falha na validação")
        return 1

    # 7. Relatório final
    separator = "=" * 70
    logger.info("\n%s", separator)
    logger.info("🎉 PROCESSO CONCLUÍDO COM SUCESSO!")
    logger.info("✅ Tabelas recriadas")
    logger.info("✅ Sync executado")
    logger.info("✅ Dados validados")
    logger.info(
        "⏰ Finalizado em: %s",
        datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC"),
    )
    logger.info("=" * 70)

    return 0


if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    try:
        EXIT_CODE = main()
        sys.exit(EXIT_CODE)
    except KeyboardInterrupt:
        logger.exception("\n❌ Processo interrompido pelo usuário")
        sys.exit(1)
    except (OSError, RuntimeError):
        logger.exception("❌ Erro fatal")
        sys.exit(1)
