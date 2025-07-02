#!/bin/bash
# ORDER_DTL FULL SYNC - Sincronização completa de detalhes de pedido

set -e

echo "🚀 Starting ORDER_DTL FULL SYNC..."

# Activate virtual environment
source /home/marlonsc/flext/.venv/bin/activate

# Set environment variables for full sync
export TAP_ORACLE_WMS_ENTITIES='["order_dtl"]'
export TAP_ORACLE_WMS_ENABLE_INCREMENTAL="false"
export TAP_ORACLE_WMS_LIMIT=""

# Run Meltano pipeline
echo "📊 Running full order_dtl extraction..."
meltano run tap-oracle-wms target-oracle

echo "✅ ORDER_DTL FULL SYNC completed successfully!"