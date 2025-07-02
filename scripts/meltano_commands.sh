#!/bin/bash
# Meltano Native Commands - 100% Meltano compliance

cd /home/marlonsc/flext/gruponos-meltano-native

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

show_help() {
    echo -e "${BLUE}🎵 Meltano Native WMS Sync Commands${NC}"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo -e "${GREEN}FULL SYNC (One-time only):${NC}"
    echo "  full-allocation    Run full sync for allocation"
    echo "  full-order-hdr     Run full sync for order_hdr"
    echo "  full-order-dtl     Run full sync for order_dtl"
    echo "  full-all           Run full sync for all entities"
    echo ""
    echo -e "${GREEN}INCREMENTAL SYNC:${NC}"
    echo "  start-schedules    Start all incremental schedules"
    echo "  stop-schedules     Stop all schedules"
    echo "  run-allocation     Run allocation incremental once"
    echo "  run-order-hdr      Run order_hdr incremental once"
    echo "  run-order-dtl      Run order_dtl incremental once"
    echo ""
    echo -e "${GREEN}MONITORING:${NC}"
    echo "  status             Show sync status and state"
    echo "  test               Test WMS connection"
    echo "  discover           Discover WMS schema"
    echo "  logs               Show recent logs"
    echo ""
}

# FULL SYNC COMMANDS (run once)
full_allocation() {
    echo -e "${BLUE}🚀 Running FULL SYNC for allocation...${NC}"
    meltano run allocation_full_sync
}

full_order_hdr() {
    echo -e "${BLUE}🚀 Running FULL SYNC for order_hdr...${NC}"
    meltano run order_hdr_full_sync
}

full_order_dtl() {
    echo -e "${BLUE}🚀 Running FULL SYNC for order_dtl...${NC}"
    meltano run order_dtl_full_sync
}

full_all() {
    echo -e "${BLUE}🚀 Running FULL SYNC for ALL entities...${NC}"
    echo -e "${YELLOW}⚠️  This will load ALL historical data. Continue? (y/n)${NC}"
    read -p "" -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        meltano run all_entities_full_sync
    else
        echo -e "${RED}❌ Full sync cancelled${NC}"
    fi
}

# INCREMENTAL SYNC COMMANDS
start_schedules() {
    echo -e "${BLUE}🔄 Starting all incremental schedules...${NC}"
    meltano schedule start allocation_incremental_sync
    meltano schedule start order_hdr_incremental_sync
    meltano schedule start order_dtl_incremental_sync
    echo -e "${GREEN}✅ All schedules started${NC}"
}

stop_schedules() {
    echo -e "${BLUE}⏹️  Stopping all schedules...${NC}"
    meltano schedule stop allocation_incremental_sync
    meltano schedule stop order_hdr_incremental_sync
    meltano schedule stop order_dtl_incremental_sync
    echo -e "${GREEN}✅ All schedules stopped${NC}"
}

run_allocation() {
    echo -e "${BLUE}🔄 Running allocation incremental...${NC}"
    meltano run tap-oracle-wms target-oracle --environment=dev \
        --extractor-setting='entities=["allocation"]' \
        --extractor-setting='simple_date_expressions={"allocation":{"mod_ts__gte":"today-1h"}}'
}

run_order_hdr() {
    echo -e "${BLUE}🔄 Running order_hdr incremental...${NC}"
    meltano run tap-oracle-wms target-oracle --environment=dev \
        --extractor-setting='entities=["order_hdr"]' \
        --extractor-setting='simple_date_expressions={"order_hdr":{"mod_ts__gte":"today-1h"}}'
}

run_order_dtl() {
    echo -e "${BLUE}🔄 Running order_dtl incremental...${NC}"
    meltano run tap-oracle-wms target-oracle --environment=dev \
        --extractor-setting='entities=["order_dtl"]' \
        --extractor-setting='simple_date_expressions={"order_dtl":{"mod_ts__gte":"today-1h"}}'
}

# MONITORING COMMANDS
show_status() {
    echo -e "${BLUE}📊 Meltano Status${NC}"
    echo ""
    
    echo -e "${GREEN}🎵 Schedules:${NC}"
    meltano schedule list
    
    echo ""
    echo -e "${GREEN}💾 State Files:${NC}"
    ls -la .meltano/run/*/state.json 2>/dev/null || echo "No state files found"
    
    echo ""
    echo -e "${GREEN}📈 Last Run Results:${NC}"
    meltano state list
}

test_connection() {
    echo -e "${BLUE}🧪 Testing WMS connection...${NC}"
    meltano invoke tap-oracle-wms --test
}

discover_schema() {
    echo -e "${BLUE}🔍 Discovering WMS schema...${NC}"
    meltano invoke tap-oracle-wms --discover > catalog.json
    echo -e "${GREEN}✅ Schema saved to catalog.json${NC}"
}

show_logs() {
    echo -e "${BLUE}📋 Recent logs:${NC}"
    if [ -d ".meltano/logs" ]; then
        find .meltano/logs -name "*.log" -exec tail -10 {} \;
    else
        echo "No logs directory found"
    fi
}

# Main command dispatcher
case "$1" in
    # Full sync
    full-allocation) full_allocation ;;
    full-order-hdr) full_order_hdr ;;
    full-order-dtl) full_order_dtl ;;
    full-all) full_all ;;
    
    # Incremental sync
    start-schedules) start_schedules ;;
    stop-schedules) stop_schedules ;;
    run-allocation) run_allocation ;;
    run-order-hdr) run_order_hdr ;;
    run-order-dtl) run_order_dtl ;;
    
    # Monitoring
    status) show_status ;;
    test) test_connection ;;
    discover) discover_schema ;;
    logs) show_logs ;;
    
    *) show_help ;;
esac