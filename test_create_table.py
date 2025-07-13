import json
import os

import oracledb

# Load target config
with open("target_config_test.json", encoding="utf-8") as f:
    config = json.load(f)

print(
    f"Connecting to Oracle at {config['host']}:{config['port']}/{config['service_name']}",
)

# Build DSN with SSL support
protocol = config.get("protocol", "tcp")
if protocol == "tcps":
    # Build SSL DSN
    dsn = (
        f"tcps://{config['host']}:{config['port']}/{config['service_name']}?"
        "ssl_server_dn_match=false&ssl_server_cert_dn=cn=*"
    )
else:
    dsn = f"{config['host']}:{config['port']}/{config['service_name']}"

print(f"Using DSN: {dsn}")

# Connect with params
params = {
    "user": config["username"],
    "password": config["password"],
    "dsn": dsn,
}

if protocol == "tcps":
    params["ssl_server_dn_match"] = False

connection = oracledb.connect(**params)

# Test simple query
with connection.cursor() as cursor:
    # Get current user
    cursor.execute("SELECT user FROM dual")
    current_user = cursor.fetchone()[0]
    print(f"Connected as user: {current_user}")

    # Check if table exists
    schema_name = config.get("default_target_schema", current_user)
    table_name = "TEST_ALLOCATION"

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM all_tables
        WHERE owner = UPPER(:owner)
        AND table_name = UPPER(:table_name)
    """,
        {"owner": schema_name, "table_name": table_name},
    )

    count = cursor.fetchone()[0]
    print(f"\nTable {schema_name}.{table_name} exists: {count > 0}")

    if count > 0:
        # Get column info
        cursor.execute(
            """
            SELECT column_name, data_type, data_length
            FROM all_tab_columns
            WHERE owner = UPPER(:owner)
            AND table_name = UPPER(:table_name)
            ORDER BY column_id
        """,
            {"owner": schema_name, "table_name": table_name},
        )

        print(f"\nColumns in {schema_name}.{table_name}:")
        for col_name, data_type, data_length in cursor:
            print(f"  {col_name}: {data_type}({data_length})")

connection.close()
print("\nConnection closed successfully")
