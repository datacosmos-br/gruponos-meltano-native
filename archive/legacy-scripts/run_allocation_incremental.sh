#!/bin/bash
# ALLOCATION INCREMENTAL SYNC - Sincronização incremental de alocações

set -e

echo "🔄 Starting ALLOCATION INCREMENTAL SYNC with installed plugins..."

# Activate virtual environment
source /home/marlonsc/flext/.venv/bin/activate

# Set environment variables for incremental sync
export TAP_ORACLE_WMS_ENTITIES='["allocation"]'
export TAP_ORACLE_WMS_ENABLE_INCREMENTAL="true"
export TAP_ORACLE_WMS_REPLICATION_KEY="last_updated"

# Show plugin versions
echo "📦 Using installed plugins:"
echo "  - tap-oracle-wms: $(tap-oracle-wms --version 2>/dev/null || echo 'version check failed')"
echo "  - flext-target-oracle: $(flext-target-oracle --about | head -2 | tail -1 | cut -d' ' -f2 2>/dev/null || echo 'version check failed')"

# Run Meltano pipeline with installed plugins
echo "📊 Running incremental allocation extraction..."
meltano run tap-oracle-wms target-oracle

echo "✅ ALLOCATION INCREMENTAL SYNC completed successfully!"