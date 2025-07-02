#!/bin/bash
# ORDER_HDR FULL SYNC - Sincronização completa de cabeçalhos de pedido

set -e

echo "🚀 Starting ORDER_HDR FULL SYNC..."

# Activate virtual environment
source /home/marlonsc/flext/.venv/bin/activate

# Set environment variables for full sync
export TAP_ORACLE_WMS_ENTITIES='["order_hdr"]'
export TAP_ORACLE_WMS_ENABLE_INCREMENTAL="false"
export TAP_ORACLE_WMS_LIMIT=""

# Run Meltano pipeline
echo "📊 Running full order_hdr extraction..."
meltano run tap-oracle-wms target-oracle

echo "✅ ORDER_HDR FULL SYNC completed successfully!"