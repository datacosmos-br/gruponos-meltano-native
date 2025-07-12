#!/usr/bin/env python3
"""Clean up existing tables and run a fresh test."""

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
    """Clean up and prepare for fresh test."""
    try:
        # Build connection params
        if config["protocol"] == "tcps":
            logger.info("Connecting with TCPS protocol...")
            # Use the actual service hostname in DSN to match certificate
            host_name = config["service_name"].split('.')[0] + ".adb.oraclecloud.com"
            dsn = f'(DESCRIPTION=(ADDRESS=(PROTOCOL=TCPS)(HOST={config["host"]})(PORT={config["port"]}))(CONNECT_DATA=(SERVICE_NAME={config["service_name"]})))'
            connection = oracledb.connect(
                user=config["username"],
                password=config["password"],
                dsn=dsn,
                config_dir=config["wallet_location"],
                wallet_location=config["wallet_location"],
                wallet_password=config["wallet_password"],
                ssl_server_dn_match=False,  # Skip hostname verification
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
        
        # Drop existing TEST_ tables
        with connection.cursor() as cursor:
            logger.info("Checking for existing TEST_ tables...")
            cursor.execute("""
                SELECT table_name 
                FROM user_tables 
                WHERE table_name LIKE 'TEST_%'
                ORDER BY table_name
            """)
            
            tables = [row[0] for row in cursor]
            
            if tables:
                logger.info(f"Found {len(tables)} TEST_ tables to drop: {tables}")
                for table in tables:
                    try:
                        cursor.execute(f"DROP TABLE {table} CASCADE CONSTRAINTS")
                        logger.info(f"Dropped table: {table}")
                    except Exception as e:
                        logger.warning(f"Could not drop {table}: {e}")
                connection.commit()
            else:
                logger.info("No existing TEST_ tables found")
            
            # Verify cleanup
            cursor.execute("""
                SELECT COUNT(*) 
                FROM user_tables 
                WHERE table_name LIKE 'TEST_%'
            """)
            count = cursor.fetchone()[0]
            logger.info(f"Remaining TEST_ tables: {count}")
            
        connection.close()
        logger.info("Cleanup completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        raise

if __name__ == "__main__":
    main()