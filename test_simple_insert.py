#!/usr/bin/env python3
"""Direct test of Oracle insert with simple data."""

import logging
import os
from datetime import datetime

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
    """Test insert directly."""
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
            # First, create a simple test table
            logger.info("Creating TEST_SIMPLE table...")
            try:
                cursor.execute("DROP TABLE TEST_SIMPLE")
                connection.commit()
            except:
                pass  # Table doesn't exist

            cursor.execute("""
                CREATE TABLE TEST_SIMPLE (
                    ID VARCHAR2(100),
                    STATUS_ID NUMBER,
                    ALLOC_QTY VARCHAR2(100),
                    SDC_EXTRACTED_AT TIMESTAMP
                )
            """)
            connection.commit()
            logger.info("Table created!")

            # Test insert with bind parameters
            sql = """INSERT INTO TEST_SIMPLE (ID, STATUS_ID, ALLOC_QTY, SDC_EXTRACTED_AT)
                     VALUES (:id, :status_id, :alloc_qty, TO_TIMESTAMP(:sdc_extracted_at, 'YYYY-MM-DD"T"HH24:MI:SS.FF'))"""

            params = {
                "id": "1001",
                "status_id": 1,
                "alloc_qty": "10.0",
                "sdc_extracted_at": datetime.utcnow().isoformat(),
            }

            logger.info(f"SQL: {sql}")
            logger.info(f"Params: {params}")

            cursor.execute(sql, params)
            connection.commit()
            logger.info("Insert successful!")

            # Verify
            cursor.execute("SELECT * FROM TEST_SIMPLE")
            rows = cursor.fetchall()
            logger.info(f"Rows in table: {len(rows)}")
            for row in rows:
                logger.info(f"Row: {row}")

        connection.close()
        logger.info("Test completed successfully!")

    except Exception as e:
        logger.exception(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()
