#!/bin/bash
# Incremental sync for allocation entity (run every minute)

cd /home/marlonsc/flext/gruponos-meltano-native

# Create incremental config with last 7 days
cat > tap_config_incremental_allocation.json << EOF
{
  "base_url": "https://ta29.wms.ocs.oraclecloud.com/raizen_test",
  "username": "USER_WMS_INTEGRA",
  "password": "jmCyS7BK94YvhS@",
  "page_size": 1000,
  "timeout": 300,
  "enable_incremental": true,
  "verify_ssl": true,
  "max_retries": 3,
  "retry_delay": 1.0,
  "entities": ["allocation"],
  "company_code": "*",
  "facility_code": "*",
  "simple_date_expressions": {
    "allocation": {
      "mod_ts__gte": "today-7d"
    }
  }
}
EOF

# Run incremental extraction
python tap_oracle_wms_wrapper.py --config tap_config_incremental_allocation.json --catalog catalog_test.json | \
    python simple_target_oracle.py --config target_config.json