#!/bin/bash
# Native Meltano Monitoring and Alerting

cd /home/marlonsc/flext/gruponos-meltano-native

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

ALERT_EMAIL="admin@gruponos.com"
SLACK_WEBHOOK="https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"

check_schedules() {
    echo -e "${BLUE}📅 Checking schedule status...${NC}"
    
    # Check if schedules are running
    RUNNING_SCHEDULES=$(meltano schedule list | grep -c "RUNNING" || echo "0")
    TOTAL_SCHEDULES=3
    
    if [ "$RUNNING_SCHEDULES" -eq "$TOTAL_SCHEDULES" ]; then
        echo -e "${GREEN}✅ All $TOTAL_SCHEDULES schedules running${NC}"
        return 0
    else
        echo -e "${RED}❌ Only $RUNNING_SCHEDULES/$TOTAL_SCHEDULES schedules running${NC}"
        return 1
    fi
}

check_recent_runs() {
    echo -e "${BLUE}🔄 Checking recent runs...${NC}"
    
    # Check last run status for each entity
    for entity in allocation order_hdr order_dtl; do
        echo -e "${YELLOW}Checking ${entity}...${NC}"
        
        # Check state file for last successful run
        STATE_FILE=".meltano/run/${entity}_incremental_sync/state.json"
        if [ -f "$STATE_FILE" ]; then
            LAST_RUN=$(jq -r '.bookmarks.allocation.replication_key_value // "Never"' "$STATE_FILE" 2>/dev/null)
            echo -e "  Last sync: $LAST_RUN"
        else
            echo -e "${RED}  No state file found${NC}"
        fi
    done
}

check_data_freshness() {
    echo -e "${BLUE}📊 Checking data freshness...${NC}"
    
    python3 << 'EOF'
import os
import sys
sys.path.append('.')
from simple_target_oracle import get_connection

try:
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check last update time for each table
    tables = ['ALLOCATION', 'ORDER_HDR', 'ORDER_DTL']
    
    for table in tables:
        try:
            cursor.execute(f"""
                SELECT COUNT(*) as total_records,
                       MAX(_LOADED_AT) as last_update
                FROM {table}
            """)
            result = cursor.fetchone()
            total, last_update = result if result else (0, None)
            
            print(f"  {table}: {total} records, last update: {last_update}")
            
        except Exception as e:
            print(f"  {table}: Error - {e}")
    
    conn.close()
    
except Exception as e:
    print(f"Database connection error: {e}")
    sys.exit(1)
EOF
}

check_disk_space() {
    echo -e "${BLUE}💾 Checking disk space...${NC}"
    
    DISK_USAGE=$(df -h . | awk 'NR==2 {print $5}' | sed 's/%//')
    
    if [ "$DISK_USAGE" -gt 80 ]; then
        echo -e "${RED}❌ Disk usage high: ${DISK_USAGE}%${NC}"
        return 1
    else
        echo -e "${GREEN}✅ Disk usage OK: ${DISK_USAGE}%${NC}"
        return 0
    fi
}

send_alert() {
    local message="$1"
    local severity="$2"
    
    echo -e "${RED}🚨 ALERT: $message${NC}"
    
    # Log alert
    echo "$(date): [$severity] $message" >> logs/alerts.log
    
    # Send email (if configured)
    if command -v mail >/dev/null 2>&1; then
        echo "$message" | mail -s "WMS Sync Alert [$severity]" "$ALERT_EMAIL"
    fi
    
    # Send Slack notification (if configured)
    if [ -n "$SLACK_WEBHOOK" ] && [ "$SLACK_WEBHOOK" != "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK" ]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"🚨 WMS Sync Alert: $message\"}" \
            "$SLACK_WEBHOOK" >/dev/null 2>&1
    fi
}

run_health_check() {
    echo -e "${BLUE}🏥 Running health check...${NC}"
    echo "Started at: $(date)"
    echo ""
    
    ERRORS=0
    
    # Check schedules
    if ! check_schedules; then
        send_alert "Schedules not running properly" "HIGH"
        ((ERRORS++))
    fi
    
    echo ""
    
    # Check recent runs
    check_recent_runs
    
    echo ""
    
    # Check data freshness
    if ! check_data_freshness; then
        send_alert "Data freshness check failed" "MEDIUM"
        ((ERRORS++))
    fi
    
    echo ""
    
    # Check disk space
    if ! check_disk_space; then
        send_alert "Disk space running low" "MEDIUM"
        ((ERRORS++))
    fi
    
    echo ""
    
    if [ $ERRORS -eq 0 ]; then
        echo -e "${GREEN}✅ All health checks passed${NC}"
    else
        echo -e "${RED}❌ Health check failed with $ERRORS errors${NC}"
    fi
    
    echo "Completed at: $(date)"
}

# Create monitoring cron job
install_monitoring() {
    echo -e "${BLUE}📅 Installing monitoring cron job...${NC}"
    
    # Create cron job that runs every 5 minutes
    CRON_JOB="*/5 * * * * cd $(pwd) && ./scripts/monitoring.sh health-check >> logs/monitoring.log 2>&1"
    
    # Add to crontab
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    
    echo -e "${GREEN}✅ Monitoring installed (runs every 5 minutes)${NC}"
    echo "Check logs at: logs/monitoring.log"
}

case "$1" in
    health-check) run_health_check ;;
    install) install_monitoring ;;
    *) 
        echo "Usage: $0 [health-check|install]"
        echo ""
        echo "Commands:"
        echo "  health-check    Run complete health check"
        echo "  install         Install monitoring cron job"
        ;;
esac