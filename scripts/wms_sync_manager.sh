#!/bin/bash
# WMS Sync Manager - Controls full and incremental syncs

cd /home/marlonsc/flext/gruponos-meltano-native

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

show_help() {
    echo "WMS Sync Manager"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  full-sync         Run one-time full sync for all entities"
    echo "  start-incremental Start incremental sync (every minute)"
    echo "  stop-incremental  Stop incremental sync"
    echo "  status           Show sync status"
    echo "  test             Test connection and extract sample data"
    echo ""
}

run_full_sync() {
    echo -e "${BLUE}🚀 Starting FULL SYNC for all entities...${NC}"
    echo -e "${YELLOW}⚠️  This will load ALL historical data from 2020-01-01${NC}"
    read -p "Continue? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}Running full sync for allocation...${NC}"
        ./scripts/full_sync_allocation.sh
        
        echo -e "${GREEN}Running full sync for order_hdr...${NC}"
        ./scripts/full_sync_order_hdr.sh
        
        echo -e "${GREEN}Running full sync for order_dtl...${NC}"
        ./scripts/full_sync_order_dtl.sh
        
        echo -e "${GREEN}✅ Full sync completed!${NC}"
    else
        echo -e "${RED}❌ Full sync cancelled${NC}"
    fi
}

start_incremental() {
    echo -e "${BLUE}🔄 Starting incremental sync...${NC}"
    
    # Create a script that runs all incrementals
    cat > run_all_incrementals.sh << 'EOF'
#!/bin/bash
cd /home/marlonsc/flext/gruponos-meltano-native

while true; do
    echo "[$(date)] Running incremental sync..."
    
    ./scripts/incremental_sync_allocation.sh
    ./scripts/incremental_sync_order_hdr.sh
    ./scripts/incremental_sync_order_dtl.sh
    
    echo "[$(date)] Incremental sync completed. Waiting 60 seconds..."
    sleep 60
done
EOF
    
    chmod +x run_all_incrementals.sh
    nohup ./run_all_incrementals.sh > logs/incremental_sync.log 2>&1 &
    echo $! > incremental_sync.pid
    
    echo -e "${GREEN}✅ Incremental sync started (PID: $(cat incremental_sync.pid))${NC}"
    echo -e "${YELLOW}📋 Check logs at: logs/incremental_sync.log${NC}"
}

stop_incremental() {
    if [ -f incremental_sync.pid ]; then
        PID=$(cat incremental_sync.pid)
        kill $PID 2>/dev/null
        rm incremental_sync.pid
        echo -e "${GREEN}✅ Incremental sync stopped${NC}"
    else
        echo -e "${YELLOW}⚠️  No incremental sync running${NC}"
    fi
}

show_status() {
    echo -e "${BLUE}📊 WMS Sync Status${NC}"
    echo ""
    
    # Check if incremental is running
    if [ -f incremental_sync.pid ]; then
        PID=$(cat incremental_sync.pid)
        if ps -p $PID > /dev/null; then
            echo -e "${GREEN}✅ Incremental sync: RUNNING (PID: $PID)${NC}"
            echo -e "   Last logs:"
            tail -5 logs/incremental_sync.log 2>/dev/null | sed 's/^/   /'
        else
            echo -e "${RED}❌ Incremental sync: STOPPED (stale PID)${NC}"
            rm incremental_sync.pid
        fi
    else
        echo -e "${YELLOW}⚠️  Incremental sync: NOT RUNNING${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}📈 Database Status:${NC}"
    python -c "
import os
import sys
sys.path.append('.')
from simple_target_oracle import get_connection, check_tables
conn = get_connection()
check_tables(conn)
conn.close()
"
}

test_connection() {
    echo -e "${BLUE}🧪 Testing WMS connection...${NC}"
    
    # Test with limited data
    cat > tap_config_test.json << EOF
{
  "base_url": "https://ta29.wms.ocs.oraclecloud.com/raizen_test",
  "username": "USER_WMS_INTEGRA",
  "password": "jmCyS7BK94YvhS@",
  "page_size": 10,
  "timeout": 60,
  "enable_incremental": true,
  "verify_ssl": true,
  "entities": ["allocation"],
  "record_limit": 5
}
EOF

    echo "Testing tap-oracle-wms..."
    python tap_oracle_wms_wrapper.py --config tap_config_test.json --catalog catalog_test.json 2>&1 | \
        head -20
    
    echo -e "${GREEN}✅ Test completed${NC}"
}

# Main script logic
case "$1" in
    full-sync)
        run_full_sync
        ;;
    start-incremental)
        start_incremental
        ;;
    stop-incremental)
        stop_incremental
        ;;
    status)
        show_status
        ;;
    test)
        test_connection
        ;;
    *)
        show_help
        ;;
esac