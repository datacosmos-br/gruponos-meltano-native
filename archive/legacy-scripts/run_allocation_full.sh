#!/bin/bash
# ALLOCATION FULL SYNC - Sincronização completa de alocações

set -e

echo "🚀 Starting ALLOCATION FULL SYNC..."

# Activate virtual environment
source /home/marlonsc/flext/.venv/bin/activate

# Set environment variables for full sync
export TAP_ORACLE_WMS_ENTITIES='["allocation"]'
export TAP_ORACLE_WMS_ENABLE_INCREMENTAL="false"
export TAP_ORACLE_WMS_LIMIT=""

# Run Meltano pipeline
echo "📊 Running full allocation extraction..."
meltano run tap-oracle-wms target-oracle

echo "✅ ALLOCATION FULL SYNC completed successfully!"