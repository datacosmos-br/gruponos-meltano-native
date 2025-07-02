#!/bin/bash
# ORDER_DTL INCREMENTAL SYNC - Sincronização incremental de detalhes de pedido

set -e

echo "🔄 Starting ORDER_DTL INCREMENTAL SYNC..."

# Activate virtual environment
source /home/marlonsc/flext/.venv/bin/activate

# Set environment variables for incremental sync
export TAP_ORACLE_WMS_ENTITIES='["order_dtl"]'
export TAP_ORACLE_WMS_ENABLE_INCREMENTAL="true"
export TAP_ORACLE_WMS_REPLICATION_KEY="last_updated"

# Run Meltano pipeline
echo "📊 Running incremental order_dtl extraction..."
meltano run tap-oracle-wms target-oracle

echo "✅ ORDER_DTL INCREMENTAL SYNC completed successfully!"