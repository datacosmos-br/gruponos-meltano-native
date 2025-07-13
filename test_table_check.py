import json
import os

import oracledb

# Load target config
with open("target_config_test.json", encoding="utf-8") as f:
    config = json.load(f)

# Build DSN
dsn = f"{config['host']}:{config['port']}/{config['service_name']}"

# Connect
connection = oracledb.connect(
    user=config["username"],
    password=config["password"],
    dsn=dsn,
    ssl_server_dn_match=False if config.get("protocol") == "tcps" else None,
)

# Check what tables exist
with connection.cursor() as cursor:
    # Check in specified schema
    cursor.execute(
        """
        SELECT owner, table_name
        FROM all_tables
        WHERE owner = UPPER(:schema)
        AND table_name LIKE 'TEST_%'
        ORDER BY owner, table_name
    """,
        {"schema": config["default_target_schema"]},
    )

    tables = cursor.fetchall()
    print(f"Tables in schema {config['default_target_schema']}:")
    for owner, table in tables:
        print(f"  {owner}.{table}")

    # Also check current user's tables
    cursor.execute(
        """
        SELECT user FROM dual
    """,
    )
    current_user = cursor.fetchone()[0]
    print(f"\nCurrent user: {current_user}")

    cursor.execute(
        """
        SELECT table_name
        FROM user_tables
        WHERE table_name LIKE 'TEST_%'
        ORDER BY table_name
    """,
    )

    user_tables = cursor.fetchall()
    print(f"\nTables owned by {current_user}:")
    for (table,) in user_tables:
        print(f"  {table}")

connection.close()
