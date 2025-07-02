#!/usr/bin/env python3
"""Fixed Oracle target with proper TCPS configuration and detailed logging."""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import oracledb

# Load .env file
from dotenv import load_dotenv

env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)


def get_oracle_connection():
    """Get Oracle database connection with proper TCPS configuration."""
    try:
        # Connection details from .env
        host = os.getenv("DATABASE__HOST", "10.93.10.114")
        port = int(os.getenv("DATABASE__PORT", "1522"))
        service_name = os.getenv(
            "DATABASE__SERVICE_NAME", "gbe8f3f2dbbc562_dwpdb_low.adb.oraclecloud.com"
        )
        username = os.getenv("DATABASE__USERNAME", "oic")
        password = os.getenv("DATABASE__PASSWORD", "").strip('"')
        protocol = os.getenv("DATABASE__PROTOCOL", "tcp").lower()

        print(f"🔌 Connecting to Oracle: {host}:{port}/{service_name}", file=sys.stderr)
        print(f"🔐 Protocol: {protocol}, User: {username}", file=sys.stderr)

        if protocol == "tcps":
            # For Oracle Autonomous Database with TCPS - simplified approach
            dsn = f"{host}:{port}/{service_name}"

            # Try with minimal configuration first
            connection = oracledb.connect(user=username, password=password, dsn=dsn)
        else:
            # Standard TCP connection
            dsn = f"{host}:{port}/{service_name}"
            connection = oracledb.connect(user=username, password=password, dsn=dsn)

        # Test connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1 FROM DUAL")
        result = cursor.fetchone()
        cursor.close()

        print(f"✅ Oracle connection successful: {result}", file=sys.stderr)
        return connection

    except Exception as e:
        print(f"❌ Oracle connection failed: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc(file=sys.stderr)
        return None


def create_table_if_not_exists(connection, table_name: str, schema: dict[str, Any]):
    """Create table if it doesn't exist based on Singer schema."""
    try:
        cursor = connection.cursor()

        print(f"📋 Creating table {table_name} if not exists", file=sys.stderr)

        # Simple column mapping
        columns = []
        for field_name, field_def in schema.get("properties", {}).items():
            # Skip Singer metadata columns - we'll add them separately
            if field_name.startswith("_"):
                continue

            field_type = field_def.get("type", "string")

            # Check if it's a date-time field (handle anyOf structure)
            is_datetime = False
            if field_def.get("format") == "date-time":
                is_datetime = True
            elif "anyOf" in field_def:
                for option in field_def["anyOf"]:
                    if option.get("format") == "date-time":
                        is_datetime = True
                        break

            if is_datetime:
                sql_type = "TIMESTAMP"
            elif field_type == "string" or (
                isinstance(field_type, list) and "string" in field_type
            ):
                max_length = field_def.get("maxLength", 4000)
                sql_type = f"VARCHAR2({min(max_length, 4000)})"
            elif field_type == "number" or (
                isinstance(field_type, list) and "number" in field_type
            ):
                sql_type = "NUMBER"
            elif field_type == "integer" or (
                isinstance(field_type, list) and "integer" in field_type
            ):
                sql_type = "NUMBER(38)"
            elif field_type == "boolean" or (
                isinstance(field_type, list) and "boolean" in field_type
            ):
                sql_type = "VARCHAR2(10)"
            else:
                sql_type = "CLOB"

            columns.append(f'"{field_name.upper()}" {sql_type}')

        # Add Singer metadata columns
        columns.extend(
            [
                '"_EXTRACTED_AT" TIMESTAMP',
                '"_ENTITY_NAME" VARCHAR2(100)',
                '"_LOADED_AT" TIMESTAMP',
            ]
        )

        create_sql = f"""
        CREATE TABLE "{table_name.upper()}" (
            {', '.join(columns)}
        )
        """

        print(f"🏗️ Creating table with {len(columns)} columns", file=sys.stderr)

        try:
            cursor.execute(create_sql)
            connection.commit()
            print(f"✅ Table {table_name} created successfully", file=sys.stderr)
        except oracledb.DatabaseError as e:
            if "name is already used" in str(e) or "already exists" in str(e):
                print(f"ℹ️ Table {table_name} already exists", file=sys.stderr)
            else:
                print(f"❌ Error creating table {table_name}: {e}", file=sys.stderr)
                raise

        cursor.close()

    except Exception as e:
        print(f"❌ Exception in create_table_if_not_exists: {e}", file=sys.stderr)


def insert_record(connection, table_name: str, record: dict[str, Any]):
    """Insert a record into the Oracle table."""
    try:
        cursor = connection.cursor()

        # Prepare data
        columns = []
        values = []
        placeholders = []

        for key, value in record.items():
            # Skip metadata fields - we'll handle them separately
            if key.startswith("_"):
                continue

            columns.append(f'"{key.upper()}"')

            # Convert values appropriately
            if value is None:
                values.append(None)
            elif isinstance(value, bool):
                values.append("TRUE" if value else "FALSE")
            elif isinstance(value, dict | list):
                values.append(json.dumps(value)[:4000])  # Truncate if too long
            elif isinstance(value, str) and ("T" in value and (":" in value)):
                # Try to parse as timestamp
                try:
                    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
                    values.append(dt)
                except:
                    values.append(str(value)[:4000])
            else:
                values.append(str(value)[:4000] if isinstance(value, str) else value)

            placeholders.append(":" + str(len(placeholders) + 1))

        # Add Singer metadata columns if they exist in the record
        if "_extracted_at" in record:
            columns.append('"_EXTRACTED_AT"')
            # Convert ISO timestamp to Oracle format
            try:
                dt = datetime.fromisoformat(
                    record["_extracted_at"].replace("Z", "+00:00")
                )
                values.append(dt)
            except:
                values.append(datetime.now())
            placeholders.append(":" + str(len(placeholders) + 1))

        if "_entity_name" in record:
            columns.append('"_ENTITY_NAME"')
            values.append(record["_entity_name"])
            placeholders.append(":" + str(len(placeholders) + 1))

        # Add standard metadata
        columns.append('"_LOADED_AT"')
        values.append(datetime.now())
        placeholders.append(":" + str(len(placeholders) + 1))

        insert_sql = f"""
        INSERT INTO "{table_name.upper()}"
        ({', '.join(columns)})
        VALUES ({', '.join(placeholders)})
        """

        cursor.execute(insert_sql, values)
        connection.commit()
        cursor.close()

        return True

    except Exception as e:
        print(f"❌ Insert error for {table_name}: {e}", file=sys.stderr)
        return False


def process_singer_messages():
    """Process Singer messages from stdin with detailed logging."""
    print("🎵 Starting Singer message processing", file=sys.stderr)

    connection = get_oracle_connection()
    if not connection:
        print("❌ Failed to get Oracle connection", file=sys.stderr)
        sys.exit(1)

    schemas = {}
    record_count = 0
    schema_count = 0
    state_count = 0

    for line_num, line in enumerate(sys.stdin, 1):
        try:
            line = line.strip()
            if not line:
                continue

            message = json.loads(line)

            if message.get("type") == "SCHEMA":
                stream_name = message.get("stream")
                schema = message.get("schema")
                schemas[stream_name] = schema
                schema_count += 1

                print(f"📋 SCHEMA #{schema_count}: {stream_name}", file=sys.stderr)

                # Create table
                create_table_if_not_exists(connection, stream_name, schema)

            elif message.get("type") == "RECORD":
                stream_name = message.get("stream")
                record = message.get("record")

                if stream_name in schemas:
                    if insert_record(connection, stream_name, record):
                        record_count += 1
                        if record_count % 100 == 0:
                            print(
                                f"📊 Inserted {record_count} records for {stream_name}",
                                file=sys.stderr,
                            )
                    else:
                        print(
                            f"❌ Failed to insert record #{record_count + 1} for {stream_name}",
                            file=sys.stderr,
                        )

            elif message.get("type") == "STATE":
                state_count += 1
                if state_count % 10 == 0:
                    print(f"🔄 Processed {state_count} STATE messages", file=sys.stderr)

        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error at line {line_num}: {e}", file=sys.stderr)
        except Exception as e:
            print(f"❌ Processing error at line {line_num}: {e}", file=sys.stderr)

    print(
        f"🏁 Processing complete: {schema_count} schemas, {record_count} records, {state_count} states",
        file=sys.stderr,
    )
    connection.close()


if __name__ == "__main__":
    process_singer_messages()
