#!/bin/bash
# Full sync for allocation entity (run once)

cd /home/marlonsc/flext/gruponos-meltano-native

echo "🚀 Starting FULL SYNC for allocation entity..."
echo "📅 Date: $(date)"

# Create full sync config with historical data
cat > tap_config_full_allocation.json << EOF
{
  "base_url": "https://a29.wms.ocs.oraclecloud.com/raizen",
  "username": "USER_WMS_INTEGRA",
  "password": "jmCyS7BK94YvhS@",
  "page_size": 1000,
  "timeout": 7200,
  "enable_incremental": false,
  "verify_ssl": true,
  "max_retries": 3,
  "retry_delay": 1.0,
  "entities": ["allocation"],
  "company_code": "*",
  "facility_code": "*",
  "start_date": "2020-01-01T00:00:00Z"
}
EOF

# Run full extraction
echo "📥 Extracting ALL allocation data from WMS..."
python tap_oracle_wms_wrapper.py --config tap_config_full_allocation.json --catalog catalog_test.json | \
    python simple_target_oracle.py --config target_config.json

echo "✅ Full sync completed for allocation"
echo "📊 Check Oracle database for results"
