#!/bin/bash
# Drop Oracle table script

# Load environment variables
source .env

# Use sqlplus to drop the table
sqlplus -s ${FLEXT_TARGET_ORACLE_USERNAME}/${FLEXT_TARGET_ORACLE_PASSWORD}@${FLEXT_TARGET_ORACLE_HOST}:${FLEXT_TARGET_ORACLE_PORT}/${FLEXT_TARGET_ORACLE_SERVICE_NAME} <<EOF
DROP TABLE WMS_ALLOCATION CASCADE CONSTRAINTS;
EXIT;
EOF

echo "Table WMS_ALLOCATION dropped (if it existed)"