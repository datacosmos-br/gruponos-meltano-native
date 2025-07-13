#!/usr/bin/env python3
"""Check Oracle database for loaded data."""

import logging
import os

import oracledb
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Oracle connection details
config = {
    "host": os.getenv("FLEXT_TARGET_ORACLE_HOST"),
    "port": int(os.getenv("FLEXT_TARGET_ORACLE_PORT", "1522")),
    "service_name": os.getenv("FLEXT_TARGET_ORACLE_SERVICE_NAME"),
    "username": os.getenv("FLEXT_TARGET_ORACLE_USERNAME"),
    "password": os.getenv("FLEXT_TARGET_ORACLE_PASSWORD"),
    "protocol": os.getenv("FLEXT_TARGET_ORACLE_PROTOCOL", "tcp"),
}

# Handle TCPS protocol
if config["protocol"] == "tcps":
    config["wallet_location"] = os.getenv("ORACLE_WALLET_LOCATION")
    config["wallet_password"] = os.getenv("ORACLE_WALLET_PASSWORD")


def main() -> None:
    """Check Oracle database for data."""
    try:
        # Build connection params
        if config["protocol"] == "tcps":
            logger.info("Connecting with TCPS protocol...")
            dsn = f'(DESCRIPTION=(ADDRESS=(PROTOCOL=TCPS)(HOST={config["host"]})(PORT={config["port"]}))(CONNECT_DATA=(SERVICE_NAME={config["service_name"]})))'
            connection = oracledb.connect(
                user=config["username"],
                password=config["password"],
                dsn=dsn,
                config_dir=config["wallet_location"],
                wallet_location=config["wallet_location"],
                wallet_password=config["wallet_password"],
                ssl_server_dn_match=False,
            )
        else:
            logger.info("Connecting with TCP protocol...")
            connection = oracledb.connect(
                user=config["username"],
                password=config["password"],
                host=config["host"],
                port=config["port"],
                service_name=config["service_name"],
            )

        logger.info("Connected to Oracle database!")

        with connection.cursor() as cursor:
            # Check for tables with data
            logger.info("Checking OIC schema for tables with data...")

            # Get all tables in OIC schema
            cursor.execute(
                """
                SELECT table_name
                FROM user_tables
                WHERE table_name LIKE '%ALLOCATION%'
                   OR table_name LIKE '%ORDER%'
                   OR table_name LIKE 'TEST_%'
                ORDER BY table_name
            """,
            )

            tables = cursor.fetchall()
            logger.info(f"Found {len(tables)} relevant tables")

            for (table_name,) in tables:
                logger.info(f"\nChecking table: {table_name}")

                # Count records
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    logger.info(f"  Records: {count}")

                    if count > 0:
                        # Show sample data
                        cursor.execute(f"SELECT * FROM {table_name} WHERE ROWNUM <= 3")
                        rows = cursor.fetchall()
                        logger.info("  Sample data (first 3 rows):")
                        for i, row in enumerate(rows, 1):
                            logger.info(f"    Row {i}: {row}")

                        # Check for Singer metadata
                        cursor.execute(
                            f"""
                            SELECT column_name
                            FROM user_tab_columns
                            WHERE table_name = '{table_name}'
                              AND column_name LIKE '_SDC_%'
                            ORDER BY column_name
                        """,
                        )
                        sdc_columns = cursor.fetchall()
                        if sdc_columns:
                            logger.info(
                                f"  Singer columns: {[col[0] for col in sdc_columns]}",
                            )

                except Exception as e:
                    logger.warning(f"  Error checking table {table_name}: {e}")

        connection.close()
        logger.info("Database check completed!")

    except Exception as e:
        logger.exception(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()
