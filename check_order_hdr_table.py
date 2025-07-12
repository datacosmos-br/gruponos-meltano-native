#!/usr/bin/env python3
"""Check Oracle ORDER_HDR table structure."""

import logging

import oracledb
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Oracle connection details
config = {
    "host": "10.93.10.114",
    "port": 1522,
    "service_name": "gbe8f3f2dbbc562_dwpdb_low.adb.oraclecloud.com",
    "username": "oic",
    "password": "aehaz232dfNuupah_#",
    "protocol": "tcps",
}


def main() -> None:
    """Check table structure."""
    try:
        # Build connection with TCPS
        logger.info("Connecting with TCPS protocol...")
        dsn = f'(DESCRIPTION=(ADDRESS=(PROTOCOL=TCPS)(HOST={config["host"]})(PORT={config["port"]}))(CONNECT_DATA=(SERVICE_NAME={config["service_name"]})))'
        connection = oracledb.connect(
            user=config["username"],
            password=config["password"],
            dsn=dsn,
            ssl_server_dn_match=False,
        )

        logger.info("Connected to Oracle database!")

        # Check table structure
        with connection.cursor() as cursor:
            logger.info("\nChecking TEST_ORDER_HDR table structure...")
            try:
                cursor.execute("""
                    SELECT column_name, data_type, data_length, nullable
                    FROM user_tab_columns
                    WHERE table_name = 'TEST_ORDER_HDR'
                    ORDER BY column_id
                """)
                columns = cursor.fetchall()

                if columns:
                    logger.info("Table TEST_ORDER_HDR structure:")
                    for col in columns:
                        logger.info(f"  {col[0]}: {col[1]}({col[2]}) {'NULL' if col[3] == 'Y' else 'NOT NULL'}")

                    # Check for potentially problematic columns
                    number_columns = [col[0] for col in columns if col[1] == "NUMBER"]
                    logger.info(f"\nNUMBER columns: {number_columns}")

                else:
                    logger.info("Table TEST_ORDER_HDR does not exist")

            except Exception as e:
                logger.exception(f"Error checking table: {e}")

        connection.close()
        logger.info("Check completed!")

    except Exception as e:
        logger.exception(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()
