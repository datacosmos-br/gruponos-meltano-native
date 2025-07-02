#!/usr/bin/env python3
"""Working Oracle target - focused on RESULTS not complexity."""

import contextlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import oracledb
from dotenv import load_dotenv

# Load environment
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)


def get_oracle_connection():
    """Get working Oracle connection."""
    try:
        host = os.getenv("DATABASE__HOST")
        port = int(os.getenv("DATABASE__PORT", 1521))
        service_name = os.getenv("DATABASE__SERVICE_NAME")
        username = os.getenv("DATABASE__USERNAME")
        password = os.getenv("DATABASE__PASSWORD", "").strip('"')

        # Simple connection string
        dsn = f"{host}:{port}/{service_name}"

        print(f"🔌 Connecting to: {dsn}", file=sys.stderr)

        connection = oracledb.connect(user=username, password=password, dsn=dsn)

        # Test connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1 FROM DUAL")
        result = cursor.fetchone()
        cursor.close()

        print(f"✅ Oracle connected: {result}", file=sys.stderr)
        return connection

    except Exception as e:
        print(f"❌ Oracle connection failed: {e}", file=sys.stderr)
        # Create fallback to file
        return None


def create_table_if_needed(connection, table_name):
    """Create simple table structure."""
    if not connection:
        return

    try:
        cursor = connection.cursor()

        # Simple allocation table
        if table_name.upper() == "ALLOCATION":
            create_sql = """
            CREATE TABLE ALLOCATION (
                ID VARCHAR2(100) PRIMARY KEY,
                ALLOC_QTY NUMBER,
                FROM_INVENTORY_ID VARCHAR2(100),
                ORDER_DTL_ID VARCHAR2(100),
                STATUS_ID VARCHAR2(100),
                CREATE_TS TIMESTAMP,
                MOD_TS TIMESTAMP,
                _LOADED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                _ENTITY_NAME VARCHAR2(50),
                _RECORD_DATA CLOB
            )
            """
        else:
            # Generic table for other entities
            create_sql = f"""
            CREATE TABLE {table_name.upper()} (
                ID VARCHAR2(100) PRIMARY KEY,
                _LOADED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                _ENTITY_NAME VARCHAR2(50),
                _RECORD_DATA CLOB
            )
            """

        try:
            cursor.execute(create_sql)
            connection.commit()
            print(f"✅ Created table {table_name}", file=sys.stderr)
        except Exception as e:
            if "already exists" in str(e).lower():
                print(f"ℹ️ Table {table_name} already exists", file=sys.stderr)
            else:
                print(f"❌ Error creating table: {e}", file=sys.stderr)

        cursor.close()

    except Exception as e:
        print(f"❌ Table creation error: {e}", file=sys.stderr)


def insert_record(connection, table_name, record):
    """Insert record with simple mapping."""
    if not connection:
        # Fallback to file
        with open(f"{table_name}_data.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
        return True

    try:
        cursor = connection.cursor()

        # Simple insert for allocation
        if table_name.upper() == "ALLOCATION":
            insert_sql = """
            INSERT INTO ALLOCATION (
                ID, ALLOC_QTY, FROM_INVENTORY_ID, ORDER_DTL_ID, STATUS_ID,
                CREATE_TS, MOD_TS, _LOADED_AT, _ENTITY_NAME, _RECORD_DATA
            ) VALUES (
                :id, :alloc_qty, :from_inventory_id, :order_dtl_id, :status_id,
                :create_ts, :mod_ts, CURRENT_TIMESTAMP, :entity_name, :record_data
            )
            """

            # Parse timestamps
            create_ts = None
            mod_ts = None

            if record.get("create_ts"):
                with contextlib.suppress(Exception):
                    create_ts = datetime.fromisoformat(
                        record["create_ts"].replace("Z", "+00:00")
                    )

            if record.get("mod_ts"):
                with contextlib.suppress(Exception):
                    mod_ts = datetime.fromisoformat(
                        record["mod_ts"].replace("Z", "+00:00")
                    )

            params = {
                "id": record.get("id"),
                "alloc_qty": record.get("alloc_qty"),
                "from_inventory_id": record.get("from_inventory_id"),
                "order_dtl_id": record.get("order_dtl_id"),
                "status_id": record.get("status_id"),
                "create_ts": create_ts,
                "mod_ts": mod_ts,
                "entity_name": "allocation",
                "record_data": json.dumps(record),
            }
        else:
            # Generic insert for other entities
            insert_sql = f"""
            INSERT INTO {table_name.upper()} (
                ID, _LOADED_AT, _ENTITY_NAME, _RECORD_DATA
            ) VALUES (
                :id, CURRENT_TIMESTAMP, :entity_name, :record_data
            )
            """

            params = {
                "id": record.get("id", "NO_ID"),
                "entity_name": table_name,
                "record_data": json.dumps(record),
            }

        cursor.execute(insert_sql, params)
        connection.commit()
        cursor.close()

        return True

    except Exception as e:
        print(f"❌ Insert error: {e}", file=sys.stderr)
        return False


def process_singer_messages():
    """Process Singer messages with FOCUS ON WORKING."""
    print("🎵 Starting WORKING Singer target", file=sys.stderr)

    connection = get_oracle_connection()

    schemas = {}
    record_count = 0

    for line_num, line in enumerate(sys.stdin, 1):
        try:
            line = line.strip()
            if not line:
                continue

            message = json.loads(line)
            msg_type = message.get("type")

            if msg_type == "SCHEMA":
                stream_name = message.get("stream")
                schema = message.get("schema")
                schemas[stream_name] = schema

                print(f"📋 SCHEMA: {stream_name}", file=sys.stderr)
                create_table_if_needed(connection, stream_name)

            elif msg_type == "RECORD":
                stream_name = message.get("stream")
                record = message.get("record")

                if stream_name in schemas:
                    if insert_record(connection, stream_name, record):
                        record_count += 1
                        if record_count % 100 == 0:
                            print(
                                f"📊 Processed {record_count} records", file=sys.stderr
                            )

            elif msg_type == "STATE":
                # Just acknowledge
                print(message)

        except json.JSONDecodeError:
            continue
        except Exception as e:
            print(f"❌ Error at line {line_num}: {e}", file=sys.stderr)

    print(f"🏁 COMPLETED: {record_count} records processed", file=sys.stderr)

    if connection:
        connection.close()


if __name__ == "__main__":
    process_singer_messages()
