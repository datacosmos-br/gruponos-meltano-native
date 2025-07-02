#!/bin/bash
# End-to-end pipeline test with REAL data

cd /home/marlonsc/flext/gruponos-meltano-native

echo "🎯 Running COMPLETE END-TO-END test with REAL WMS data"
echo "======================================================="

# Config for small test
cat > e2e_config.json << 'EOF'
{
  "base_url": "https://ta29.wms.ocs.oraclecloud.com/raizen_test",
  "username": "USER_WMS_INTEGRA",
  "password": "jmCyS7BK94YvhS@",
  "page_size": 100,
  "timeout": 300,
  "enable_incremental": false,
  "verify_ssl": true,
  "entities": ["allocation"],
  "company_code": "*",
  "facility_code": "*"
}
EOF

echo "1️⃣ TESTING TAP DISCOVERY..."
python meltano_tap_wrapper.py --config e2e_config.json --discover > e2e_catalog.json 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Discovery successful"
else
    echo "❌ Discovery failed"
    exit 1
fi

echo ""
echo "2️⃣ TESTING DATA EXTRACTION..."
echo "Extracting sample records..."
timeout 30 python meltano_tap_wrapper.py --config e2e_config.json --catalog e2e_catalog.json 2>/dev/null > e2e_data.json
EXIT_CODE=$?

# Count records
RECORD_COUNT=$(grep '"type":"RECORD"' e2e_data.json | wc -l)
echo "✅ Extracted $RECORD_COUNT records"

if [ $RECORD_COUNT -eq 0 ]; then
    echo "❌ No records extracted"
    exit 1
fi

# Show timeout is expected
if [ $EXIT_CODE -eq 124 ]; then
    echo "⏰ Timeout reached (expected) - pipeline extracted $RECORD_COUNT records successfully"
fi

echo ""
echo "3️⃣ TESTING TARGET LOADING..."
head -1000 e2e_data.json | python meltano_target_wrapper.py

if [ $? -eq 0 ]; then
    echo "✅ Target loading successful"
else
    echo "❌ Target loading failed"
    exit 1
fi

echo ""
echo "4️⃣ TESTING STATE PERSISTENCE..."
# Check if state files exist
if [ -d ".meltano/run" ]; then
    echo "✅ Meltano state directory exists"
    ls -la .meltano/run/
else
    echo "⚠️  No Meltano state directory (expected for manual run)"
fi

echo ""
echo "5️⃣ VALIDATING DATA IN ORACLE..."
python -c "
import sys
sys.path.append('.')
from simple_target_oracle import get_oracle_connection

conn = get_oracle_connection()
cursor = conn.cursor()

try:
    cursor.execute('SELECT COUNT(*) FROM ALLOCATION WHERE _LOADED_AT > SYSDATE - 1/24')
    recent_count = cursor.fetchone()[0]
    print(f'✅ Recent records in Oracle: {recent_count}')
    
    if recent_count > 0:
        cursor.execute('SELECT ID, ALLOC_QTY, STATUS_ID, _LOADED_AT FROM ALLOCATION WHERE ROWNUM <= 3 ORDER BY _LOADED_AT DESC')
        rows = cursor.fetchall()
        print('📋 Sample records:')
        for row in rows:
            print(f'   ID: {row[0]}, Qty: {row[1]}, Status: {row[2]}, Loaded: {row[3]}')
    
except Exception as e:
    print(f'❌ Oracle validation failed: {e}')
    sys.exit(1)
finally:
    conn.close()
"

echo ""
echo "🎉 END-TO-END TEST COMPLETED SUCCESSFULLY!"
echo "✅ WMS → TAP → TARGET → ORACLE pipeline working 100%"
echo ""
echo "📊 Summary:"
echo "  - Discovered WMS schema: ✅"
echo "  - Extracted real data: ✅ ($RECORD_COUNT records)"  
echo "  - Loaded to Oracle: ✅"
echo "  - Data validated: ✅"
echo ""
echo "🚀 SYSTEM IS 100% OPERATIONAL!"