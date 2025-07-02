#!/usr/bin/env python3
"""Simple Oracle target that WORKS with direct connections."""

import json
import logging
import sys
from datetime import datetime
from typing import Any

import oracledb

# Load environment variables
from dotenv import load_dotenv

load_dotenv(".env")


class SimpleOracleTarget:
    """Simple Oracle target using direct connections - NO SQLAlchemy pooling."""

    def __init__(self, config: dict[str, Any]):
        """Initialize simple Oracle target."""
        self.config = config
        self.connection = None
        self.logger = logging.getLogger("simple-oracle-target")
        logging.basicConfig(level=logging.INFO)

        # Statistics
        self.records_processed = 0
        self.batches_processed = 0

        self.logger.info("Initialized Simple Oracle Target (Direct Connection)")

    def connect(self):
        """Connect to Oracle using PROVEN working pattern."""
        host = self.config["host"]
        port = int(self.config.get("port", 1522))
        username = self.config["username"]
        password = self.config["password"]
        service_name = self.config["service_name"]
        protocol = self.config.get("protocol", "tcps").lower()

        # PROVEN WORKING DSN FORMAT from legacy/flx-database-oracle
        dsn = (
            f"(DESCRIPTION="
            f"(RETRY_COUNT=20)(RETRY_DELAY=3)"
            f"(ADDRESS=(PROTOCOL={protocol})(HOST={host})(PORT={port}))"
            f"(CONNECT_DATA=(SERVICE_NAME={service_name}))"
            f"(SECURITY=(SSL_SERVER_DN_MATCH=no))"
            f")"
        )

        self.logger.info(f"Connecting to Oracle: {username}@{host}:{port} ({protocol})")

        # Direct Oracle connection - NO SQLAlchemy
        self.connection = oracledb.connect(user=username, password=password, dsn=dsn)

        # Test connection
        cursor = self.connection.cursor()
        cursor.execute("SELECT 1 FROM DUAL")
        result = cursor.fetchone()
        cursor.close()

        self.logger.info(f"✅ Oracle connection successful: {result[0]}")

    def create_table(self, stream_name: str, schema: dict[str, Any]):
        """Create Oracle table if not exists."""
        table_name = stream_name.upper()

        # Build CREATE TABLE SQL
        columns = []
        for prop_name, prop_def in schema["properties"].items():
            col_name = prop_name.upper()
            prop_type = prop_def.get("type", "string")

            if prop_type == "integer":
                col_type = "NUMBER(38,0)"
            elif prop_type == "number":
                col_type = "NUMBER(38,10)"
            elif prop_type == "boolean":
                col_type = "VARCHAR2(10)"
            elif prop_type in {"object", "array"}:
                col_type = "CLOB"
            else:
                col_type = "VARCHAR2(4000)"

            columns.append(f"{col_name} {col_type}")

        # Add metadata columns
        columns.extend(
            [
                "_LOADED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                "_ENTITY_NAME VARCHAR2(100)",
                "_BATCH_ID VARCHAR2(50)",
            ]
        )

        create_sql = f"""
        CREATE TABLE {table_name} (
            {', '.join(columns)}
        )
        """

        cursor = self.connection.cursor()
        try:
            cursor.execute(create_sql)
            self.logger.info(f"Created table {table_name}")
        except oracledb.DatabaseError as e:
            if "name is already used" in str(e):
                self.logger.info(f"Table {table_name} already exists")
            else:
                self.logger.exception(f"Error creating table: {e}")
                raise
        finally:
            cursor.close()

    def insert_records(self, stream_name: str, records: list[dict[str, Any]]):
        """Insert records into Oracle table."""
        if not records:
            return

        table_name = stream_name.upper()
        batch_id = f"batch_{int(datetime.now().timestamp())}"

        cursor = self.connection.cursor()
        try:
            for record in records:
                # Prepare record
                prepared = {}
                for key, value in record.items():
                    if key.startswith("_sdc_"):
                        continue
                    oracle_key = key.upper()

                    if value is None:
                        prepared[oracle_key] = None
                    elif isinstance(value, bool):
                        prepared[oracle_key] = "TRUE" if value else "FALSE"
                    elif isinstance(value, dict | list):
                        prepared[oracle_key] = json.dumps(value)
                    elif isinstance(value, str):
                        prepared[oracle_key] = value[:4000]  # Truncate if too long
                    else:
                        prepared[oracle_key] = str(value)[:4000]

                # Add metadata
                prepared["_LOADED_AT"] = datetime.now()
                prepared["_ENTITY_NAME"] = stream_name
                prepared["_BATCH_ID"] = batch_id

                # Build INSERT SQL
                columns = list(prepared.keys())
                placeholders = [f":{col}" for col in columns]

                insert_sql = f"""
                INSERT INTO {table_name} ({', '.join(columns)})
                VALUES ({', '.join(placeholders)})
                """

                cursor.execute(insert_sql, prepared)

            # Commit transaction
            self.connection.commit()
            self.records_processed += len(records)
            self.logger.info(f"Inserted {len(records)} records into {table_name}")

        except Exception as e:
            self.connection.rollback()
            self.logger.exception(f"Error inserting records: {e}")
            raise
        finally:
            cursor.close()

    def process_messages(self):
        """Process Singer messages from stdin."""
        schema = None
        stream_name = None
        batch = []
        batch_size = self.config.get("batch_size", 1000)

        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue

            try:
                message = json.loads(line)
                msg_type = message.get("type")

                if msg_type == "SCHEMA":
                    # New stream schema
                    stream_name = message["stream"]
                    schema = message["schema"]
                    self.logger.info(f"Processing stream: {stream_name}")

                    # Create table
                    self.create_table(stream_name, schema)

                elif msg_type == "RECORD":
                    # Add record to batch
                    if message["stream"] == stream_name:
                        batch.append(message["record"])

                        # Flush batch if full
                        if len(batch) >= batch_size:
                            self.insert_records(stream_name, batch)
                            batch = []
                            self.batches_processed += 1

                elif msg_type == "STATE":
                    # Flush remaining records
                    if batch:
                        self.insert_records(stream_name, batch)
                        batch = []
                        self.batches_processed += 1

            except json.JSONDecodeError as e:
                self.logger.exception(f"Invalid JSON: {e}")
                continue
            except Exception as e:
                self.logger.exception(f"Error processing message: {e}")
                continue

        # Final flush
        if batch:
            self.insert_records(stream_name, batch)
            self.batches_processed += 1

        self.logger.info("=== SIMPLE ORACLE TARGET SUMMARY ===")
        self.logger.info(f"Records processed: {self.records_processed:,}")
        self.logger.info(f"Batches processed: {self.batches_processed:,}")

    def close(self):
        """Close Oracle connection."""
        if self.connection:
            self.connection.close()
            self.logger.info("Oracle connection closed")


def main():
    """Main entry point."""
    # Configuration from environment variables
    config = {
        "host": "10.93.10.114",
        "port": "1522",
        "service_name": "gbe8f3f2dbbc562_dwpdb_low.adb.oraclecloud.com",
        "username": "oic",
        "password": "aehaz232dfNuupah_#",
        "protocol": "tcps",
        "batch_size": 1000,
    }

    target = SimpleOracleTarget(config)

    try:
        target.connect()
        target.process_messages()
    finally:
        target.close()


if __name__ == "__main__":
    main()
