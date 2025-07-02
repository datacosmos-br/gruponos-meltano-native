#!/bin/bash
# ORDER_HDR INCREMENTAL SYNC - Sincronização incremental de cabeçalhos de pedido

set -e

echo "🔄 Starting ORDER_HDR INCREMENTAL SYNC..."

# Activate virtual environment
source /home/marlonsc/flext/.venv/bin/activate

# Set environment variables for incremental sync
export TAP_ORACLE_WMS_ENTITIES='["order_hdr"]'
export TAP_ORACLE_WMS_ENABLE_INCREMENTAL="true"
export TAP_ORACLE_WMS_REPLICATION_KEY="order_date"

# Run Meltano pipeline
echo "📊 Running incremental order_hdr extraction..."
meltano run tap-oracle-wms target-oracle

echo "✅ ORDER_HDR INCREMENTAL SYNC completed successfully!"