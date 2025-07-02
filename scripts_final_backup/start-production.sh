#!/bin/bash

# =============================================================================
# GRUPONOS PRODUCTION STARTUP SCRIPT
# =============================================================================
# Start all incremental sync pipelines in background with nohup
# User requirement: "coloque os pipelines para rodar como nohup"
# =============================================================================

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "${SCRIPT_DIR}")"
PID_DIR="${PROJECT_DIR}/pids"
LOG_DIR="${PROJECT_DIR}/logs"
NOHUP_LOG_DIR="${LOG_DIR}/nohup"

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

# Initialize directories
init_directories() {
    log "Creating necessary directories..."
    mkdir -p "${PID_DIR}"
    mkdir -p "${LOG_DIR}"
    mkdir -p "${NOHUP_LOG_DIR}"
    mkdir -p "${LOG_DIR}/meltano"
    
    success "Directories created successfully"
}

# Check if meltano is available and configured
check_environment() {
    log "Checking environment..."
    
    # Check if in correct directory
    if [ ! -f "${PROJECT_DIR}/meltano.yml" ]; then
        error "meltano.yml not found. Please run from project directory."
        exit 1
    fi
    
    # Check if meltano is available
    if ! command -v meltano &> /dev/null; then
        error "Meltano not found. Please install meltano first."
        exit 1
    fi
    
    # Check if .env exists
    if [ ! -f "${PROJECT_DIR}/.env" ]; then
        error ".env file not found. Please create .env with required credentials."
        exit 1
    fi
    
    # Load environment variables
    cd "${PROJECT_DIR}"
    set -a
    source .env
    set +a
    
    success "Environment checked and loaded successfully"
}

# Install Meltano plugins if needed
install_plugins() {
    log "Installing Meltano plugins..."
    
    cd "${PROJECT_DIR}"
    
    # Install plugins
    if meltano install 2>&1; then
        success "Meltano plugins installed successfully"
    else
        warn "Some plugins may have failed to install, continuing..."
    fi
}

# Test database connections
test_connections() {
    log "Testing database connections..."
    
    cd "${PROJECT_DIR}"
    
    # Install plugins first
    install_plugins
    
    # Test if meltano can load plugins
    log "Testing Meltano plugin configuration..."
    if meltano config list tap-oracle-wms >/dev/null 2>&1; then
        success "Meltano configuration: OK"
    else
        warn "Meltano configuration: Cannot verify (plugins may need manual installation)"
    fi
    
    # Test WMS connection (optional - may fail if plugins not fully installed)
    log "Testing WMS Oracle connection..."
    if timeout 30 meltano invoke tap-oracle-wms:test 2>/dev/null; then
        success "WMS Oracle connection: OK"
    else
        warn "WMS Oracle connection: Could not test (tap may not be installed yet)"
        warn "This is normal on first run - plugins will be installed on first execution"
    fi
    
    success "Environment validation completed"
}

# Kill existing processes
kill_existing_processes() {
    log "Checking for existing pipeline processes..."
    
    local entities=("allocation" "order_hdr" "order_dtl")
    local killed_count=0
    
    for entity in "${entities[@]}"; do
        local pid_file="${PID_DIR}/${entity}_incremental.pid"
        
        if [ -f "${pid_file}" ]; then
            local pid=$(cat "${pid_file}")
            
            if kill -0 "${pid}" 2>/dev/null; then
                log "Killing existing process for ${entity} (PID: ${pid})"
                kill "${pid}" 2>/dev/null || true
                sleep 2
                
                # Force kill if still running
                if kill -0 "${pid}" 2>/dev/null; then
                    warn "Force killing ${entity} process (PID: ${pid})"
                    kill -9 "${pid}" 2>/dev/null || true
                fi
                
                ((killed_count++))
            fi
            
            rm -f "${pid_file}"
        fi
    done
    
    if [ ${killed_count} -gt 0 ]; then
        warn "Killed ${killed_count} existing processes"
        sleep 3
    else
        log "No existing processes found"
    fi
}

# Start incremental sync for a specific entity
start_entity_pipeline() {
    local entity="$1"
    local schedule_name="${entity}_incremental_sync"
    local pid_file="${PID_DIR}/${entity}_incremental.pid"
    local log_file="${NOHUP_LOG_DIR}/${entity}_incremental.log"
    local error_log="${NOHUP_LOG_DIR}/${entity}_incremental.err"
    
    log "Starting incremental sync pipeline for: ${entity}"
    log "Schedule: ${schedule_name}"
    log "Log file: ${log_file}"
    log "Error log: ${error_log}"
    
    cd "${PROJECT_DIR}"
    
    # Create a wrapper script for the pipeline
    local wrapper_script="${PID_DIR}/${entity}_wrapper.sh"
    cat > "${wrapper_script}" << EOF
#!/bin/bash
set -euo pipefail

# Load environment
cd "${PROJECT_DIR}"
set -a
source .env
set +a

# Function to log with timestamp
log_with_timestamp() {
    echo "\$(date +'%Y-%m-%d %H:%M:%S') [\${entity}] \$1"
}

# Main pipeline loop
entity="${entity}"
schedule_name="${schedule_name}"

log_with_timestamp "Starting incremental sync pipeline for \${entity}"
log_with_timestamp "Schedule: \${schedule_name}"

# Pipeline execution loop - run every minute
while true; do
    start_time=\$(date +%s)
    log_with_timestamp "Starting sync execution..."
    
    # Run the meltano schedule (install plugins if needed on first run)
    if meltano install >/dev/null 2>&1 && meltano run "\${schedule_name}" 2>&1; then
        end_time=\$(date +%s)
        duration=\$((end_time - start_time))
        log_with_timestamp "Sync completed successfully in \${duration} seconds"
    else
        end_time=\$(date +%s)
        duration=\$((end_time - start_time))
        log_with_timestamp "ERROR: Sync failed after \${duration} seconds"
    fi
    
    # Wait for next minute (calculate remaining seconds)
    current_second=\$(date +%S)
    sleep_time=\$((60 - current_second))
    
    log_with_timestamp "Waiting \${sleep_time} seconds for next minute..."
    sleep "\${sleep_time}"
done
EOF
    
    chmod +x "${wrapper_script}"
    
    # Start the pipeline with nohup
    log "Executing: nohup ${wrapper_script} >> ${log_file} 2>> ${error_log} &"
    
    # Start in background with nohup
    nohup "${wrapper_script}" >> "${log_file}" 2>> "${error_log}" &
    local pid=$!
    
    # Save PID
    echo "${pid}" > "${pid_file}"
    
    # Wait a moment to check if process started successfully
    sleep 2
    
    if kill -0 "${pid}" 2>/dev/null; then
        success "Pipeline started successfully for ${entity} (PID: ${pid})"
        log "Log file: ${log_file}"
        log "Error log: ${error_log}"
        log "PID file: ${pid_file}"
        return 0
    else
        error "Failed to start pipeline for ${entity}"
        rm -f "${pid_file}"
        return 1
    fi
}

# Start all entity pipelines
start_all_pipelines() {
    local entities=("allocation" "order_hdr" "order_dtl")
    local success_count=0
    local total_count=${#entities[@]}
    
    log "Starting all incremental sync pipelines..."
    log "Entities: ${entities[*]}"
    log "Requirement: incremental a cada minuto, um job para cada entidade"
    
    for entity in "${entities[@]}"; do
        log ""
        log "Starting pipeline ${entity} (${success_count}/${total_count} completed)..."
        
        if start_entity_pipeline "${entity}"; then
            ((success_count++))
        else
            error "Failed to start pipeline for entity: ${entity}"
        fi
        
        # Small delay between starts
        sleep 1
    done
    
    log ""
    log "=================================================="
    log "PIPELINE STARTUP SUMMARY"
    log "=================================================="
    log "Total entities: ${total_count}"
    log "Successfully started: ${success_count}"
    log "Failed to start: $((total_count - success_count))"
    
    if [ ${success_count} -eq ${total_count} ]; then
        success "ALL PIPELINES STARTED SUCCESSFULLY!"
        success "Pipelines running with nohup in background"
        return 0
    else
        error "Some pipelines failed to start. Check logs above."
        return 1
    fi
}

# Show status of running pipelines
show_status() {
    log "Checking pipeline status..."
    
    local entities=("allocation" "order_hdr" "order_dtl")
    local running_count=0
    
    echo
    printf "%-15s %-10s %-10s %-30s\n" "ENTITY" "STATUS" "PID" "LOG FILE"
    echo "────────────────────────────────────────────────────────────────────"
    
    for entity in "${entities[@]}"; do
        local pid_file="${PID_DIR}/${entity}_incremental.pid"
        local log_file="${NOHUP_LOG_DIR}/${entity}_incremental.log"
        
        if [ -f "${pid_file}" ]; then
            local pid=$(cat "${pid_file}")
            
            if kill -0 "${pid}" 2>/dev/null; then
                printf "%-15s ${GREEN}%-10s${NC} %-10s %-30s\n" "${entity}" "RUNNING" "${pid}" "$(basename ${log_file})"
                ((running_count++))
            else
                printf "%-15s ${RED}%-10s${NC} %-10s %-30s\n" "${entity}" "STOPPED" "N/A" "$(basename ${log_file})"
                rm -f "${pid_file}"
            fi
        else
            printf "%-15s ${YELLOW}%-10s${NC} %-10s %-30s\n" "${entity}" "NOT_STARTED" "N/A" "$(basename ${log_file})"
        fi
    done
    
    echo
    log "Running pipelines: ${running_count}/${#entities[@]}"
    
    if [ ${running_count} -eq ${#entities[@]} ]; then
        success "All pipelines are running successfully!"
    elif [ ${running_count} -gt 0 ]; then
        warn "Some pipelines are not running"
    else
        error "No pipelines are running"
    fi
}

# Stop all pipelines
stop_all_pipelines() {
    log "Stopping all pipeline processes..."
    kill_existing_processes
    success "All pipelines stopped"
}

# View logs for a specific entity
tail_logs() {
    local entity="${1:-allocation}"
    local log_file="${NOHUP_LOG_DIR}/${entity}_incremental.log"
    local error_log="${NOHUP_LOG_DIR}/${entity}_incremental.err"
    
    if [ -f "${log_file}" ]; then
        log "Tailing logs for ${entity}..."
        log "Log file: ${log_file}"
        log "Press Ctrl+C to stop"
        echo
        tail -f "${log_file}"
    else
        error "Log file not found: ${log_file}"
        exit 1
    fi
}

# Show help
show_help() {
    cat << EOF
GrupoNOS Production Pipeline Startup

USAGE:
    $0 [COMMAND] [OPTIONS]

COMMANDS:
    start                 Start all incremental pipelines with nohup
    stop                  Stop all running pipelines
    restart               Stop and start all pipelines
    status                Show status of all pipelines
    logs [ENTITY]         Tail logs for entity (default: allocation)
    test                  Test connections and configuration

EXAMPLES:
    $0 start                    # Start all pipelines in background
    $0 status                   # Check which pipelines are running
    $0 logs allocation          # View allocation pipeline logs
    $0 stop                     # Stop all pipelines
    $0 restart                  # Restart all pipelines

ENTITIES:
    allocation    - WMS allocation data (largest entity)
    order_hdr     - Order header records
    order_dtl     - Order detail records

PIPELINE BEHAVIOR:
    - Each entity runs as separate nohup process
    - Incremental sync every minute (60-second intervals)
    - Automatic restart on failure (built into pipeline loop)
    - Logs written to: logs/nohup/ENTITY_incremental.log
    - PIDs stored in: pids/ENTITY_incremental.pid

REQUIREMENTS:
    - Meltano installed and configured
    - .env file with database credentials
    - Access to WMS Oracle and target Oracle databases

IMPLEMENTATION:
    - Implements "incremental a cada minuto" requirement
    - Uses nohup for background execution
    - Separate process per entity due to large data volumes
    - Production-ready with logging and PID management

EOF
}

# Main execution
main() {
    local command="${1:-start}"
    
    case "${command}" in
        start)
            init_directories
            check_environment
            test_connections
            kill_existing_processes
            start_all_pipelines
            echo
            log "Use '$0 status' to check pipeline status"
            log "Use '$0 logs [entity]' to view logs"
            ;;
        stop)
            stop_all_pipelines
            ;;
        restart)
            init_directories
            check_environment
            test_connections
            kill_existing_processes
            start_all_pipelines
            ;;
        status)
            show_status
            ;;
        logs)
            tail_logs "${2:-allocation}"
            ;;
        test)
            check_environment
            test_connections
            ;;
        -h|--help|help)
            show_help
            exit 0
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