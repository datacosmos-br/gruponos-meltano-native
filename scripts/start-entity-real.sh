#!/bin/bash

# =============================================================================
# GRUPONOS REAL ENTITY PIPELINE STARTER
# =============================================================================
# Start individual entity pipeline with nohup using REAL tap + target
# Usage: ./start-entity-real.sh [ENTITY_NAME]
# =============================================================================

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "${SCRIPT_DIR}")"
PID_DIR="${PROJECT_DIR}/pids"
LOG_DIR="${PROJECT_DIR}/logs"
NOHUP_LOG_DIR="${LOG_DIR}/nohup"
STATE_DIR="${PROJECT_DIR}/state"

# Logging function
log() {
    local timestamp=$(date +'%Y-%m-%d %H:%M:%S')
    echo -e "${BLUE}[${timestamp}]${NC} $1"
}

error() {
    local timestamp=$(date +'%Y-%m-%d %H:%M:%S')
    echo -e "${RED}[${timestamp}] ERROR:${NC} $1" >&2
}

success() {
    local timestamp=$(date +'%Y-%m-%d %H:%M:%S')
    echo -e "${GREEN}[${timestamp}] SUCCESS:${NC} $1"
}

warn() {
    local timestamp=$(date +'%Y-%m-%d %H:%M:%S')
    echo -e "${YELLOW}[${timestamp}] WARNING:${NC} $1"
}

# Start single entity pipeline with REAL tap + target
start_entity_pipeline() {
    local entity="$1"
    local pid_file="${PID_DIR}/${entity}_real.pid"
    local log_file="${NOHUP_LOG_DIR}/${entity}_real.log"
    local error_log="${NOHUP_LOG_DIR}/${entity}_real.err"
    
    # Initialize directories
    mkdir -p "${PID_DIR}" "${LOG_DIR}" "${NOHUP_LOG_DIR}" "${STATE_DIR}"
    
    # Check if already running
    if [ -f "${pid_file}" ]; then
        local existing_pid=$(cat "${pid_file}")
        if kill -0 "${existing_pid}" 2>/dev/null; then
            warn "Real pipeline for ${entity} is already running (PID: ${existing_pid})"
            return 0
        else
            rm -f "${pid_file}"
        fi
    fi
    
    log "Starting REAL pipeline for entity: ${entity}"
    log "Log file: ${log_file}"
    
    # Create wrapper script for real pipeline
    local wrapper_script="${PID_DIR}/${entity}_real_wrapper.sh"
    cat > "${wrapper_script}" << 'EOF'
#!/bin/bash
set -euo pipefail

# Change to project directory
cd "${PROJECT_DIR}"

# Load environment
set -a
source .env 2>/dev/null || true
set +a

# Function to log with timestamp
log_with_timestamp() {
    echo "$(date +'%Y-%m-%d %H:%M:%S') [${entity}] $1"
}

# Pipeline variables
entity="${entity}"
tap_config="tap-config.json"
state_file="state/${entity}_state.json"
catalog_file="catalog_${entity}_incremental.json"

log_with_timestamp "Starting REAL incremental pipeline for ${entity}"
log_with_timestamp "Using tap-oracle-wms + simple_target_oracle"
log_with_timestamp "Requirement: incremental a cada minuto"

# Create catalog for incremental sync
create_incremental_catalog() {
    cat > "${catalog_file}" << CATALOG_EOF
{
  "streams": [
    {
      "tap_stream_id": "${entity}",
      "stream": "${entity}",
      "schema": {
        "type": "object",
        "properties": {}
      },
      "metadata": [
        {
          "breadcrumb": [],
          "metadata": {
            "inclusion": "selected",
            "selected": true,
            "table-key-properties": [],
            "forced-replication-method": "incremental"
          }
        }
      ]
    }
  ]
}
CATALOG_EOF
}

# Main loop - run every minute
iteration=1
while true; do
    start_time=$(date +%s)
    log_with_timestamp "Iteration ${iteration}: Starting REAL sync..."
    
    # Create catalog
    create_incremental_catalog
    
    # Build pipeline command
    tap_command="python /home/marlonsc/flext/flext-tap-oracle-wms/tap_oracle_wms/main.py"
    tap_command+=" --config ${tap_config}"
    tap_command+=" --catalog ${catalog_file}"
    
    if [ -f "${state_file}" ]; then
        tap_command+=" --state ${state_file}"
        log_with_timestamp "Using existing state file"
    fi
    
    target_command="python simple_target_oracle.py"
    
    # Execute pipeline with state management
    log_with_timestamp "Executing: ${tap_command} | ${target_command}"
    
    # Run pipeline and capture state
    ${tap_command} 2>&1 | tee >(grep '^{"type": "STATE"' > "${state_file}.tmp") | ${target_command} 2>&1
    
    exit_code=$?
    
    # Update state file if new state was captured
    if [ -s "${state_file}.tmp" ]; then
        tail -1 "${state_file}.tmp" > "${state_file}"
        log_with_timestamp "State updated"
    fi
    rm -f "${state_file}.tmp"
    
    # Clean up catalog
    rm -f "${catalog_file}"
    
    end_time=$(date +%s)
    duration=$((end_time - start_time))
    
    if [ ${exit_code} -eq 0 ]; then
        log_with_timestamp "REAL SYNC: Completed successfully in ${duration} seconds"
    else
        log_with_timestamp "WARNING: Sync had issues but continuing (exit code: ${exit_code})"
    fi
    
    ((iteration++))
    
    # Wait for next minute
    current_second=$(date +%S)
    sleep_time=$((60 - current_second))
    
    if [ ${sleep_time} -gt 0 ]; then
        log_with_timestamp "Waiting ${sleep_time} seconds for next minute..."
        sleep "${sleep_time}"
    fi
done
EOF
    
    # Substitute variables in wrapper script
    sed -i "s/\${PROJECT_DIR}/${PROJECT_DIR//\//\\/}/g" "${wrapper_script}"
    sed -i "s/\${entity}/${entity}/g" "${wrapper_script}"
    
    chmod +x "${wrapper_script}"
    
    # Start with nohup
    log "Executing: nohup ${wrapper_script} >> ${log_file} 2>> ${error_log} &"
    nohup "${wrapper_script}" >> "${log_file}" 2>> "${error_log}" &
    local pid=$!
    
    # Save PID
    echo "${pid}" > "${pid_file}"
    
    # Check if started successfully
    sleep 2
    if kill -0 "${pid}" 2>/dev/null; then
        success "REAL pipeline started for ${entity} (PID: ${pid})"
        log "Log: ${log_file}"
        log "PID: ${pid_file}"
        return 0
    else
        error "Failed to start REAL pipeline for ${entity}"
        rm -f "${pid_file}"
        return 1
    fi
}

# Stop entity pipeline
stop_entity_pipeline() {
    local entity="$1"
    local pid_file="${PID_DIR}/${entity}_real.pid"
    
    if [ -f "${pid_file}" ]; then
        local pid=$(cat "${pid_file}")
        if kill -0 "${pid}" 2>/dev/null; then
            log "Stopping REAL pipeline for ${entity} (PID: ${pid})"
            kill "${pid}" 2>/dev/null || true
            sleep 1
            if kill -0 "${pid}" 2>/dev/null; then
                warn "Force killing ${entity} (PID: ${pid})"
                kill -9 "${pid}" 2>/dev/null || true
            fi
            success "Stopped REAL pipeline for ${entity}"
        else
            warn "REAL pipeline for ${entity} was not running"
        fi
        rm -f "${pid_file}"
    else
        warn "No PID file found for ${entity}"
    fi
}

# Show entity status
show_entity_status() {
    local entity="$1"
    local pid_file="${PID_DIR}/${entity}_real.pid"
    local log_file="${NOHUP_LOG_DIR}/${entity}_real.log"
    
    if [ -f "${pid_file}" ]; then
        local pid=$(cat "${pid_file}")
        if kill -0 "${pid}" 2>/dev/null; then
            success "${entity}: RUNNING REAL PIPELINE (PID: ${pid})"
        else
            error "${entity}: STOPPED (stale PID file)"
            rm -f "${pid_file}"
        fi
    else
        warn "${entity}: NOT STARTED"
    fi
    
    if [ -f "${log_file}" ]; then
        local log_lines=$(wc -l < "${log_file}")
        log "Log file: ${log_file} (${log_lines} lines)"
    fi
}

# Tail entity logs
tail_entity_logs() {
    local entity="$1"
    local log_file="${NOHUP_LOG_DIR}/${entity}_real.log"
    
    if [ -f "${log_file}" ]; then
        log "Tailing REAL pipeline logs for ${entity}..."
        tail -f "${log_file}"
    else
        error "Log file not found: ${log_file}"
        exit 1
    fi
}

# Stop all simulation pipelines
stop_all_simulations() {
    log "Stopping all simulation pipelines..."
    for entity in allocation order_hdr order_dtl; do
        local sim_pid_file="${PID_DIR}/${entity}_simple.pid"
        if [ -f "${sim_pid_file}" ]; then
            local pid=$(cat "${sim_pid_file}")
            if kill -0 "${pid}" 2>/dev/null; then
                log "Stopping simulation for ${entity} (PID: ${pid})"
                kill "${pid}" 2>/dev/null || true
                sleep 1
                if kill -0 "${pid}" 2>/dev/null; then
                    kill -9 "${pid}" 2>/dev/null || true
                fi
            fi
            rm -f "${sim_pid_file}"
        fi
    done
    success "All simulations stopped"
}

# Show help
show_help() {
    cat << EOF
GrupoNOS REAL Entity Pipeline Manager

USAGE:
    $0 start ENTITY_NAME     # Start REAL pipeline for specific entity
    $0 stop ENTITY_NAME      # Stop REAL pipeline for specific entity  
    $0 status ENTITY_NAME    # Show status for specific entity
    $0 logs ENTITY_NAME      # Tail logs for specific entity
    $0 start-all             # Start all 3 entities with REAL pipeline
    $0 stop-all              # Stop all 3 REAL pipelines
    $0 status-all            # Show status for all entities
    $0 stop-simulations      # Stop all simulation pipelines
    $0 migrate-all           # Stop simulations and start REAL pipelines

ENTITIES:
    allocation    - WMS allocation data
    order_hdr     - Order header records
    order_dtl     - Order detail records

EXAMPLES:
    $0 start allocation      # Start REAL allocation pipeline
    $0 status allocation     # Check allocation status
    $0 logs allocation       # View allocation logs
    $0 migrate-all          # Migrate from simulation to REAL

IMPLEMENTATION:
    - Uses REAL tap-oracle-wms + simple_target_oracle
    - Each entity runs as separate nohup process
    - Incremental sync every minute with state management
    - Data flows: Oracle WMS → tap → target → Oracle Analytics

EOF
}

# Main execution
main() {
    local command="${1:-help}"
    local entity="${2:-}"
    
    case "${command}" in
        start)
            if [ -z "${entity}" ]; then
                error "Entity name required for start command"
                show_help
                exit 1
            fi
            case "${entity}" in
                allocation|order_hdr|order_dtl)
                    start_entity_pipeline "${entity}"
                    ;;
                *)
                    error "Invalid entity: ${entity}"
                    error "Valid entities: allocation, order_hdr, order_dtl"
                    exit 1
                    ;;
            esac
            ;;
        stop)
            if [ -z "${entity}" ]; then
                error "Entity name required for stop command"
                show_help
                exit 1
            fi
            case "${entity}" in
                allocation|order_hdr|order_dtl)
                    stop_entity_pipeline "${entity}"
                    ;;
                *)
                    error "Invalid entity: ${entity}"
                    exit 1
                    ;;
            esac
            ;;
        status)
            if [ -z "${entity}" ]; then
                error "Entity name required for status command"
                show_help
                exit 1
            fi
            case "${entity}" in
                allocation|order_hdr|order_dtl)
                    show_entity_status "${entity}"
                    ;;
                *)
                    error "Invalid entity: ${entity}"
                    exit 1
                    ;;
            esac
            ;;
        logs)
            if [ -z "${entity}" ]; then
                error "Entity name required for logs command"
                show_help
                exit 1
            fi
            case "${entity}" in
                allocation|order_hdr|order_dtl)
                    tail_entity_logs "${entity}"
                    ;;
                *)
                    error "Invalid entity: ${entity}"
                    exit 1
                    ;;
            esac
            ;;
        start-all)
            log "Starting all REAL entity pipelines..."
            for entity in allocation order_hdr order_dtl; do
                start_entity_pipeline "${entity}"
                sleep 2
            done
            ;;
        stop-all)
            log "Stopping all REAL entity pipelines..."
            for entity in allocation order_hdr order_dtl; do
                stop_entity_pipeline "${entity}"
            done
            ;;
        status-all)
            log "Status for all entity pipelines..."
            for entity in allocation order_hdr order_dtl; do
                show_entity_status "${entity}"
            done
            ;;
        stop-simulations)
            stop_all_simulations
            ;;
        migrate-all)
            log "Migrating from simulation to REAL pipelines..."
            stop_all_simulations
            sleep 2
            log "Starting all REAL pipelines..."
            for entity in allocation order_hdr order_dtl; do
                start_entity_pipeline "${entity}"
                sleep 2
            done
            success "Migration complete! All entities now using REAL pipeline"
            ;;
        help|-h|--help)
            show_help
            ;;
        *)
            error "Unknown command: ${command}"
            show_help
            exit 1
            ;;
    esac
}

# Execute main function
main "$@"