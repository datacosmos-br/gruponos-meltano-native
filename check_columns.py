#!/usr/bin/env python3
"""Check Oracle table columns."""

import os
import sys

import oracledb
from oracle_validator import *

try:
    # Get Oracle connection parameters from environment
    host = os.getenv("FLEXT_TARGET_ORACLE_HOST")
    port = int(os.getenv("FLEXT_TARGET_ORACLE_PORT", 1522))
    service_name = os.getenv("FLEXT_TARGET_ORACLE_SERVICE_NAME")
    username = os.getenv("FLEXT_TARGET_ORACLE_USERNAME")
    password = os.getenv("FLEXT_TARGET_ORACLE_PASSWORD")
    protocol = os.getenv("FLEXT_TARGET_ORACLE_PROTOCOL", "tcps")

    if protocol == "tcps":
        dsn = f"(DESCRIPTION=(ADDRESS=(PROTOCOL=TCPS)(HOST={host})(PORT={port}))(CONNECT_DATA=(SERVICE_NAME={service_name})))"
        conn = oracledb.connect(user=username, password=password, dsn=dsn, ssl_server_dn_match=False)
    else:
        conn = oracledb.connect(user=username, password=password, host=host, port=port, service_name=service_name)

    cursor = conn.cursor()

    # Check table structure
    cursor.execute("""
        SELECT column_name, data_type, data_length, nullable
        FROM user_tab_columns
        WHERE table_name = 'WMS_ALLOCATION'
        ORDER BY column_id
    """)

    print("WMS_ALLOCATION table structure:")
    print("-" * 60)
    columns = cursor.fetchall()
    for row in columns:
        col_name, data_type, data_length, nullable = row
        print(f"{col_name:30} {data_type:15} ({data_length:4}) {nullable}")

    # Count columns
    print("-" * 60)
    print(f"Total columns: {len(columns)}")

    # Check if specific columns exist
    print("\nChecking for key columns:")
    key_cols = ["id", "mod_ts", "create_ts", "alloc_qty", "order_dtl_id", "wave_id", "wave_key", "mhe_system_key"]
    for col in key_cols:
        exists = any(c[0].upper() == col.upper() for c in columns)
        print(f"  {col:20} {'✅' if exists else '❌'}")

    cursor.close()
    conn.close()

except Exception as e:
    print(f"❌ Error: {e!s}")
    sys.exit(1)
