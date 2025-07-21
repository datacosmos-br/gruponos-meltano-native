"""Validate data in Oracle tables after sync."""

from __future__ import annotations

from datetime import UTC, datetime

# Use centralized logger from flext-observability - ELIMINATE DUPLICATION
from flext_observability.logging import get_logger

from gruponos_meltano_native.config import get_config
from gruponos_meltano_native.oracle.connection_manager import OracleConnectionManager

# Setup logger
logger = get_logger(__name__)


def _get_table_list() -> list[tuple[str, str]]:
    """Get list of tables to validate.

    Returns:
        List of (table_name, entity_name) tuples

    """
    return [
        ("WMS_ALLOCATION", "allocation"),
        ("WMS_ORDER_HDR", "order_hdr"),
        ("WMS_ORDER_DTL", "order_dtl"),
        ("ALLOCATION", "allocation"),
        ("ORDER_HDR", "order_hdr"),
        ("ORDER_DTL", "order_dtl"),
    ]


def _validate_table_name(table_name: str) -> bool:
    """Validate table name for safety.

    Args:
        table_name: Table name to validate

    Returns:
        True if valid, False otherwise

    """
    return table_name.replace("_", "").isalnum()


def _check_table_exists(cursor: object, table_name: str) -> bool:
    """Check if table exists in the database.

    Args:
        cursor: Database cursor
        table_name: Name of table to check

    Returns:
        True if table exists, False otherwise

    """
    try:
        cursor.execute(
            "SELECT COUNT(*) FROM user_tables WHERE table_name = :table_name",
            {"table_name": table_name},
        )
        return cursor.fetchone()[0] > 0
    except (OSError, ValueError, RuntimeError):
        logger.exception("Error checking if table %s exists", table_name)
        return False


def _count_table_records(cursor: object, table_name: str) -> int:
    """Count records in a table.

    Args:
        cursor: Database cursor
        table_name: Name of table to count

    Returns:
        Number of records, 0 if error or empty

    """
    try:
        # Validate table name for safety before using in query
        if not _validate_table_name(table_name):
            logger.error("Invalid table name: %s", table_name)
            return 0

        cursor.execute(f'SELECT COUNT(*) FROM "OIC"."{table_name}"')  # noqa: S608
        return cursor.fetchone()[0]
    except (OSError, ValueError, RuntimeError):
        logger.exception("Error counting records in table %s", table_name)
        return 0


def _get_table_details(cursor: object, table_name: str) -> dict[str, str | int | None]:
    """Get detailed information about a table.

    Args:
        cursor: Database cursor
        table_name: Name of table to analyze

    Returns:
        Dictionary with table details

    """
    details = {
        "min_date": None,
        "max_date": None,
        "unique_ids": 0,
        "duplicates": 0,
    }

    try:
        if not _validate_table_name(table_name):
            logger.error("Invalid table name: %s", table_name)
            return details

        # Get date range and unique IDs
        cursor.execute(
            f"SELECT "  # noqa: S608
            f'MIN("MOD_TS") as min_date, '
            f'MAX("MOD_TS") as max_date, '
            f'COUNT(DISTINCT "ID") as unique_ids '
            f'FROM "OIC"."{table_name}"',
        )
        min_date, max_date, unique_ids = cursor.fetchone()
        details.update(
            {
                "min_date": min_date,
                "max_date": max_date,
                "unique_ids": unique_ids or 0,
            },
        )

        # Check for duplicates
        cursor.execute(
            f"SELECT COUNT(*) FROM ("  # noqa: S608
            f'SELECT "ID" FROM "OIC"."{table_name}" '
            f'GROUP BY "ID" HAVING COUNT(*) > 1'
            f")",
        )
        duplicate_count = cursor.fetchone()[0]
        details["duplicates"] = duplicate_count

    except (OSError, ValueError, RuntimeError):
        logger.exception("Error getting details for table %s", table_name)

    return details


def _validate_single_table(cursor: object, table_name: str, entity_name: str) -> int:
    """Validate data in a specific table.

    Args:
        cursor: Database cursor
        table_name: Name of table to validate
        entity_name: Entity name for logging

    Returns:
        Number of records found, 0 if table doesn't exist or error

    """
    logger.info("📊 Tabela: %s (%s)", table_name, entity_name)

    # Check if table exists
    if not _check_table_exists(cursor, table_name):
        logger.info("⚠️  Tabela %s não existe", table_name)
        return 0

    # Count records
    record_count = _count_table_records(cursor, table_name)
    logger.info("   Total de registros: %s", f"{record_count:,}")

    if record_count == 0:
        logger.warning("   ⚠️  Tabela vazia")
        return 0

    # Get detailed information
    details = _get_table_details(cursor, table_name)

    if details["min_date"]:
        logger.info("   Data mais antiga: %s", details["min_date"])
    if details["max_date"]:
        logger.info("   Data mais recente: %s", details["max_date"])
    if details["unique_ids"]:
        logger.info("   IDs únicos: %s", f"{details['unique_ids']:,}")

    if details["duplicates"] > 0:
        logger.warning("   ⚠️  Duplicatas encontradas: %d IDs", details["duplicates"])
    else:
        logger.info("   ✅ Nenhuma duplicata encontrada")

    return record_count


def _log_validation_header() -> None:
    """Log validation process header."""
    logger.info("🔍 VALIDANDO DADOS NO ORACLE...")
    logger.info("📅 %s", datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S"))
    logger.info("-" * 60)


def _setup_database_connection() -> tuple[object, object] | None:
    """Set up database connection and return connection and cursor.

    Returns:
        Tuple of (connection, cursor) or None if setup failed

    """
    config = get_config()
    if config.target_oracle is None:
        logger.error("Target Oracle configuration not found")
        return None

    manager = OracleConnectionManager(config.target_oracle.oracle)
    try:
        conn = manager.connect()
        cursor = conn.cursor()
    except (OSError, ValueError, RuntimeError):
        logger.exception("❌ Erro ao conectar com Oracle")
        return None

    return conn, cursor


def _validate_all_tables(cursor: object) -> int:
    """Validate all tables and return total record count.

    Args:
        cursor: Database cursor

    Returns:
        Total number of records across all tables

    """
    tables = _get_table_list()
    total_records = 0

    for table_name, entity_name in tables:
        try:
            record_count = _validate_single_table(cursor, table_name, entity_name)
            total_records += record_count
        except (OSError, ValueError, RuntimeError):
            logger.exception("Error validating table %s", table_name)
            continue

    return total_records


def _log_validation_summary(total_records: int) -> None:
    """Log validation summary.

    Args:
        total_records: Total number of records found

    """
    logger.info("\n%s", "=" * 60)
    logger.info("📊 RESUMO GERAL:")
    logger.info(
        "   Total de registros em todas as tabelas: %s",
        f"{total_records:,}",
    )
    status = (
        "✅ SUCESSO" if total_records > 0 else "❌ FALHA - Nenhum dado sincronizado"
    )
    logger.info("   Status: %s", status)


def _cleanup_connection(cursor: object, conn: object) -> None:
    """Clean up database connection.

    Args:
        cursor: Database cursor to close
        conn: Database connection to close

    """
    cursor.close()
    conn.close()


def validate_sync() -> bool:
    """Validate data synchronization in Oracle tables.

    Returns:
        True if validation passes, False otherwise

    """
    _log_validation_header()

    # Setup database connection
    connection_result = _setup_database_connection()
    if connection_result is None:
        return False

    conn, cursor = connection_result

    try:
        # Validate all tables
        total_records = _validate_all_tables(cursor)

        # Log summary
        _log_validation_summary(total_records)

        # Clean up
        _cleanup_connection(cursor, conn)

    except (OSError, ValueError, RuntimeError):
        logger.exception("\n❌ Erro ao validar")
        return False

    return total_records > 0


if __name__ == "__main__":
    import sys

    success = validate_sync()
    sys.exit(0 if success else 1)
