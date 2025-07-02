#!/bin/bash

# =============================================================================
# GRUPONOS PIPELINE MONITORING DASHBOARD
# =============================================================================
# Real-time monitoring dashboard for all 3 NOHUP pipelines
# User requirement: Monitor "incremental a cada minuto, um job para cada entidade"
# =============================================================================

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "${SCRIPT_DIR}")"
PID_DIR="${PROJECT_DIR}/pids"
LOG_DIR="${PROJECT_DIR}/logs"
NOHUP_LOG_DIR="${LOG_DIR}/nohup"
REFRESH_INTERVAL=5

# Get pipeline status
get_pipeline_status() {
    local entity="$1"
    local pid_file="${PID_DIR}/${entity}_simple.pid"
    
    if [ -f "${pid_file}" ]; then
        local pid=$(cat "${pid_file}")
        if kill -0 "${pid}" 2>/dev/null; then
            echo "RUNNING:${pid}"
        else
            echo "STOPPED:0"
        fi
    else
        echo "NOT_STARTED:0"
    fi
}

# Get last log entry
get_last_log_entry() {
    local entity="$1"
    local log_file="${NOHUP_LOG_DIR}/${entity}_simple.log"
    
    if [ -f "${log_file}" ]; then
        tail -1 "${log_file}" 2>/dev/null || echo "No logs yet"
    else
        echo "Log file not found"
    fi
}

# Get log line count
get_log_lines() {
    local entity="$1"
    local log_file="${NOHUP_LOG_DIR}/${entity}_simple.log"
    
    if [ -f "${log_file}" ]; then
        wc -l < "${log_file}" 2>/dev/null || echo "0"
    else
        echo "0"
    fi
}

# Get pipeline uptime
get_pipeline_uptime() {
    local entity="$1"
    local pid_file="${PID_DIR}/${entity}_simple.pid"
    
    if [ -f "${pid_file}" ]; then
        local pid=$(cat "${pid_file}")
        if kill -0 "${pid}" 2>/dev/null; then
            # Get process start time
            local start_time=$(ps -o lstart= -p "${pid}" 2>/dev/null | xargs -I {} date -d "{}" +%s 2>/dev/null || echo "0")
            local current_time=$(date +%s)
            local uptime_seconds=$((current_time - start_time))
            
            if [ ${uptime_seconds} -gt 0 ]; then
                local hours=$((uptime_seconds / 3600))
                local minutes=$(((uptime_seconds % 3600) / 60))
                local seconds=$((uptime_seconds % 60))
                printf "%02d:%02d:%02d" ${hours} ${minutes} ${seconds}
            else
                echo "00:00:00"
            fi
        else
            echo "00:00:00"
        fi
    else
        echo "00:00:00"
    fi
}

# Count iterations from log
get_iteration_count() {
    local entity="$1"
    local log_file="${NOHUP_LOG_DIR}/${entity}_simple.log"
    
    if [ -f "${log_file}" ]; then
        grep -c "Iteration" "${log_file}" 2>/dev/null || echo "0"
    else
        echo "0"
    fi
}

# Display dashboard
display_dashboard() {
    clear
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}                         GRUPONOS PIPELINE MONITORING DASHBOARD${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}Requirement: incremental a cada minuto, um job para cada entidade (NOHUP)${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════════════${NC}"
    
    # Current time
    echo -e "${BLUE}Current Time:${NC} $(date +'%Y-%m-%d %H:%M:%S')"
    echo -e "${BLUE}Next Minute:${NC}  $(date -d '+1 minute' +'%Y-%m-%d %H:%M:00')"
    echo -e "${BLUE}Refresh:${NC}      Every ${REFRESH_INTERVAL} seconds"
    echo
    
    # Pipeline status table
    printf "%-12s %-12s %-8s %-10s %-12s %-8s %-8s\n" "ENTITY" "STATUS" "PID" "UPTIME" "ITERATIONS" "LOGS" "MODE"
    echo "─────────────────────────────────────────────────────────────────────────────────────────"
    
    local entities=("allocation" "order_hdr" "order_dtl")
    local running_count=0
    
    for entity in "${entities[@]}"; do
        local status_info=$(get_pipeline_status "${entity}")
        local status=$(echo "${status_info}" | cut -d: -f1)
        local pid=$(echo "${status_info}" | cut -d: -f2)
        local uptime=$(get_pipeline_uptime "${entity}")
        local iterations=$(get_iteration_count "${entity}")
        local log_lines=$(get_log_lines "${entity}")
        
        # Color coding for status
        case "${status}" in
            "RUNNING")
                local status_color="${GREEN}"
                ((running_count++))
                ;;
            "STOPPED")
                local status_color="${RED}"
                ;;
            *)
                local status_color="${YELLOW}"
                ;;
        esac
        
        printf "%-12s ${status_color}%-12s${NC} %-8s %-10s %-12s %-8s %-8s\n" \
            "${entity}" "${status}" "${pid}" "${uptime}" "${iterations}" "${log_lines}" "NOHUP"
    done
    
    echo
    echo "─────────────────────────────────────────────────────────────────────────────────────────"
    
    # Summary
    echo -e "${BLUE}Running Pipelines:${NC} ${running_count}/${#entities[@]}"
    
    if [ ${running_count} -eq ${#entities[@]} ]; then
        echo -e "${GREEN}✅ ALL PIPELINES RUNNING SUCCESSFULLY${NC}"
    elif [ ${running_count} -gt 0 ]; then
        echo -e "${YELLOW}⚠️  SOME PIPELINES NOT RUNNING${NC}"
    else
        echo -e "${RED}❌ NO PIPELINES RUNNING${NC}"
    fi
    
    echo
    echo "─────────────────────────────────────────────────────────────────────────────────────────"
    
    # Recent activity
    echo -e "${BLUE}Recent Activity (Last Log Entry):${NC}"
    echo
    
    for entity in "${entities[@]}"; do
        local last_log=$(get_last_log_entry "${entity}")
        local status_info=$(get_pipeline_status "${entity}")
        local status=$(echo "${status_info}" | cut -d: -f1)
        
        if [ "${status}" = "RUNNING" ]; then
            echo -e "${GREEN}${entity}:${NC} ${last_log}"
        else
            echo -e "${RED}${entity}:${NC} ${last_log}"
        fi
    done
    
    echo
    echo "─────────────────────────────────────────────────────────────────────────────────────────"
    
    # Implementation details
    echo -e "${MAGENTA}Implementation Details:${NC}"
    echo -e "• Each entity runs as separate nohup process"
    echo -e "• Incremental sync every minute (60-second intervals)"
    echo -e "• Separate logs: logs/nohup/ENTITY_simple.log"
    echo -e "• PID files: pids/ENTITY_simple.pid"
    echo -e "• Mode: SIMULATION (will be replaced with real tap-oracle-wms)"
    
    echo
    echo -e "${YELLOW}Controls: Ctrl+C to exit | ./start-entity.sh [start|stop|status]-all${NC}"
}

# Main monitoring loop
monitor_loop() {
    # Trap Ctrl+C to exit gracefully
    trap 'echo -e "\n${YELLOW}Monitoring stopped by user${NC}"; exit 0' INT
    
    while true; do
        display_dashboard
        sleep "${REFRESH_INTERVAL}"
    done
}

# Show single status
show_single_status() {
    display_dashboard
}

# Show help
show_help() {
    cat << EOF
GrupoNOS Pipeline Monitoring Dashboard

USAGE:
    $0 [COMMAND] [OPTIONS]

COMMANDS:
    monitor               Start real-time monitoring dashboard (default)
    status                Show current status (one-time)
    
OPTIONS:
    --refresh N          Set refresh interval in seconds (default: ${REFRESH_INTERVAL})
    -h, --help           Show this help

EXAMPLES:
    $0                          # Start real-time monitoring
    $0 monitor --refresh 3      # Monitor with 3-second refresh
    $0 status                   # Show status once and exit

MONITORED PIPELINES:
    allocation_simple    - PID: pids/allocation_simple.pid
    order_hdr_simple     - PID: pids/order_hdr_simple.pid
    order_dtl_simple     - PID: pids/order_dtl_simple.pid

FEATURES:
    - Real-time status updates
    - Uptime tracking per pipeline
    - Iteration count monitoring
    - Recent activity display
    - Color-coded status indicators

MANAGEMENT:
    Start:    ./start-entity.sh start-all
    Stop:     ./start-entity.sh stop-all
    Status:   ./start-entity.sh status-all

REQUIREMENTS:
    - Pipelines started with start-entity.sh
    - NOHUP processes running in background
    - Log files in logs/nohup/ directory

NOTE:
    Implements "incremental a cada minuto, um job para cada entidade"
    requirement with real-time monitoring dashboard.

EOF
}

# Parse command line arguments
COMMAND="monitor"
while [[ $# -gt 0 ]]; do
    case $1 in
        monitor)
            COMMAND="monitor"
            shift
            ;;
        status)
            COMMAND="status"
            shift
            ;;
        --refresh)
            REFRESH_INTERVAL="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Execute command
case "${COMMAND}" in
    monitor)
        monitor_loop
        ;;
    status)
        show_single_status
        ;;
    *)
        echo "Unknown command: ${COMMAND}"
        show_help
        exit 1
        ;;
esac