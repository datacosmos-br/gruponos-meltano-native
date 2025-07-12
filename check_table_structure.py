#!/usr/bin/env python3
"""Check the structure of TEST_ALLOCATION table."""

import os
import oracledb
from dotenv import load_dotenv
import logging

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

def main():
    """Check table structure."""
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
        
        # Check table structure
        with connection.cursor() as cursor:
            logger.info("\nChecking TEST_ALLOCATION table structure...")
            cursor.execute("""
                SELECT column_name, data_type, data_length, nullable
                FROM user_tab_columns
                WHERE table_name = 'TEST_ALLOCATION'
                ORDER BY column_id
            """)
            
            columns = cursor.fetchall()
            if columns:
                logger.info(f"\nFound {len(columns)} columns in TEST_ALLOCATION:")
                logger.info("-" * 80)
                logger.info(f"{'Column Name':<30} {'Data Type':<20} {'Length':<10} {'Nullable':<10}")
                logger.info("-" * 80)
                for col_name, data_type, data_length, nullable in columns:
                    logger.info(f"{col_name:<30} {data_type:<20} {data_length:<10} {nullable:<10}")
            else:
                logger.info("TEST_ALLOCATION table not found!")
                
                # Check if any TEST_ tables exist
                cursor.execute("""
                    SELECT table_name 
                    FROM user_tables 
                    WHERE table_name LIKE 'TEST_%'
                    ORDER BY table_name
                """)
                
                tables = [row[0] for row in cursor]
                if tables:
                    logger.info(f"\nFound TEST_ tables: {tables}")
                else:
                    logger.info("\nNo TEST_ tables found in the schema")
            
        connection.close()
        logger.info("\nCheck completed successfully!")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        raise

if __name__ == "__main__":
    main()