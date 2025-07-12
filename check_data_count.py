#!/usr/bin/env python3
"""Check data count in Oracle tables."""

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


def main() -> None:
    """Check data count in all TEST_ tables."""
    try:
        # Build connection params
        if config["protocol"] == "tcps":
            logger.info("Connecting with TCPS protocol...")
            dsn = f'(DESCRIPTION=(ADDRESS=(PROTOCOL=TCPS)(HOST={config["host"]})(PORT={config["port"]}))(CONNECT_DATA=(SERVICE_NAME={config["service_name"]})))'
            connection = oracledb.connect(
                user=config["username"],
                password=config["password"],
                dsn=dsn,
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

        # Get all TEST_ tables
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name
                FROM user_tables
                WHERE table_name LIKE 'TEST_%'
                ORDER BY table_name
            """)

            tables = [row[0] for row in cursor]
            if not tables:
                logger.info("No TEST_ tables found!")
                return

            logger.info(f"Found {len(tables)} TEST_ tables:")
            logger.info("-" * 60)
            logger.info(f"{'Table Name':<30} {'Record Count':<15} {'Latest Record':<15}")
            logger.info("-" * 60)

            for table_name in tables:
                # Get count
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]

                    # Get latest record timestamp if exists
                    latest = "N/A"
                    try:
                        cursor.execute(f"SELECT MAX(_SDC_EXTRACTED_AT) FROM {table_name}")
                        latest_ts = cursor.fetchone()[0]
                        if latest_ts:
                            latest = latest_ts.strftime("%H:%M:%S")
                    except:
                        pass

                    logger.info(f"{table_name:<30} {count:<15} {latest:<15}")

                except Exception as e:
                    logger.info(f"{table_name:<30} ERROR: {e}")

        connection.close()
        logger.info("\nData count check completed!")

    except Exception as e:
        logger.exception(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()
