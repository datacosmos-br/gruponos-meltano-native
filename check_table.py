#!/usr/bin/env python3
import os
import oracledb

# Get Oracle connection parameters from environment
host = os.getenv('FLEXT_TARGET_ORACLE_HOST')
port = int(os.getenv('FLEXT_TARGET_ORACLE_PORT', 1522))
service_name = os.getenv('FLEXT_TARGET_ORACLE_SERVICE_NAME')
username = os.getenv('FLEXT_TARGET_ORACLE_USERNAME')
password = os.getenv('FLEXT_TARGET_ORACLE_PASSWORD')
protocol = os.getenv('FLEXT_TARGET_ORACLE_PROTOCOL', 'tcps')

# Connect to Oracle
if protocol == 'tcps':
    dsn = f'(DESCRIPTION=(ADDRESS=(PROTOCOL=TCPS)(HOST={host})(PORT={port}))(CONNECT_DATA=(SERVICE_NAME={service_name})))'
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
for row in cursor.fetchall():
    col_name, data_type, data_length, nullable = row
    print(f"{col_name:30} {data_type:15} ({data_length:4}) {nullable}")

# Count columns
cursor.execute("SELECT COUNT(*) FROM user_tab_columns WHERE table_name = 'WMS_ALLOCATION'")
col_count = cursor.fetchone()[0]
print("-" * 60)
print(f"Total columns: {col_count}")

cursor.close()
conn.close()