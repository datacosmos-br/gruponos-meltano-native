#!/bin/bash
# Test real WMS data extraction

echo "🔍 Testing real WMS data extraction..."

# Test extraction with real tap
echo "📥 Extracting data from WMS..."
python tap_oracle_wms_wrapper.py --config tap_config.json --catalog catalog_test.json 2>/dev/null | \
    head -100 | \
    grep -E '"type"|"record"|"schema"|"stream"' | \
    jq -r 'if .type == "RECORD" then "\(.stream): \(.record | keys | join(", "))" else .type end'

echo ""
echo "✅ If you see SCHEMA and RECORD messages above, the tap is working!"