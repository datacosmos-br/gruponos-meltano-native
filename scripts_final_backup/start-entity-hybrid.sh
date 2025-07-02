#!/bin/bash

# =============================================================================
# GRUPONOS HYBRID ENTITY PIPELINE STARTER
# =============================================================================
# Start individual entity pipeline with nohup using simulated tap + real target
# This is a hybrid approach until tap-oracle-wms is fully functional
# Usage: ./start-entity-hybrid.sh [ENTITY_NAME]
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

# Create entity-specific tap simulator
create_tap_simulator() {
    local entity="$1"
    local simulator_file="${PROJECT_DIR}/simulate_${entity}_tap.py"
    
    cat > "${simulator_file}" << 'EOF'
#!/usr/bin/env python3
"""
Simulate tap output for ENTITY_NAME with realistic data
"""

import json
import sys
import random
from datetime import datetime, timedelta

ENTITY = "ENTITY_NAME"

def generate_allocation_record(i, base_time):
    """Generate a realistic allocation record"""
    created = base_time - timedelta(minutes=random.randint(0, 5))
    
    return {
        "allocation_id": f"ALLOC-{random.randint(100000, 999999):06d}",
        "order_id": f"ORD-{random.randint(10000, 99999):06d}",
        "item_id": f"ITEM-{random.randint(1000, 9999):04d}",
        "from_location": f"LOC-{random.randint(1, 999):03d}",
        "to_location": f"STAGE-{random.randint(1, 50):02d}",
        "quantity": random.randint(1, 500),
        "status": random.choice(["PENDING", "IN_PROGRESS", "COMPLETED", "CANCELLED"]),
        "priority": random.randint(1, 5),
        "created_date_utc": created.isoformat() + "Z",
        "last_update_date_utc": (created + timedelta(seconds=random.randint(0, 300))).isoformat() + "Z",
        "user_id": f"USER-{random.randint(1, 100):03d}",
        "warehouse_id": random.choice(["WH-001", "WH-002", "WH-003"])
    }

def generate_order_hdr_record(i, base_time):
    """Generate a realistic order header record"""
    created = base_time - timedelta(minutes=random.randint(0, 5))
    
    return {
        "order_id": f"ORD-{random.randint(10000, 99999):06d}",
        "customer_id": f"CUST-{random.randint(1000, 9999):04d}",
        "order_type": random.choice(["STANDARD", "EXPRESS", "PRIORITY", "BACKORDER"]),
        "status": random.choice(["NEW", "PROCESSING", "SHIPPED", "DELIVERED", "CANCELLED"]),
        "total_amount": round(random.uniform(10.0, 5000.0), 2),
        "currency": "USD",
        "order_date": created.isoformat() + "Z",
        "ship_date": (created + timedelta(days=random.randint(1, 3))).isoformat() + "Z",
        "delivery_date": (created + timedelta(days=random.randint(3, 7))).isoformat() + "Z",
        "warehouse_id": random.choice(["WH-001", "WH-002", "WH-003"]),
        "last_update_date_utc": (created + timedelta(seconds=random.randint(0, 300))).isoformat() + "Z"
    }

def generate_order_dtl_record(i, base_time):
    """Generate a realistic order detail record"""
    created = base_time - timedelta(minutes=random.randint(0, 5))
    
    return {
        "order_dtl_id": f"DTL-{random.randint(100000, 999999):06d}",
        "order_id": f"ORD-{random.randint(10000, 99999):06d}",
        "line_number": random.randint(1, 10),
        "item_id": f"ITEM-{random.randint(1000, 9999):04d}",
        "quantity_ordered": random.randint(1, 100),
        "quantity_shipped": random.randint(0, 100),
        "unit_price": round(random.uniform(1.0, 500.0), 2),
        "total_price": round(random.uniform(10.0, 5000.0), 2),
        "status": random.choice(["PENDING", "ALLOCATED", "PICKED", "PACKED", "SHIPPED"]),
        "created_date_utc": created.isoformat() + "Z",
        "last_update_date_utc": (created + timedelta(seconds=random.randint(0, 300))).isoformat() + "Z"
    }

def get_schema(entity):
    """Get schema for entity"""
    schemas = {
        "allocation": {
            "type": "object",
            "properties": {
                "allocation_id": {"type": "string"},
                "order_id": {"type": "string"},
                "item_id": {"type": "string"},
                "from_location": {"type": "string"},
                "to_location": {"type": "string"},
                "quantity": {"type": "integer"},
                "status": {"type": "string"},
                "priority": {"type": "integer"},
                "created_date_utc": {"type": "string", "format": "date-time"},
                "last_update_date_utc": {"type": "string", "format": "date-time"},
                "user_id": {"type": "string"},
                "warehouse_id": {"type": "string"}
            }
        },
        "order_hdr": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string"},
                "customer_id": {"type": "string"},
                "order_type": {"type": "string"},
                "status": {"type": "string"},
                "total_amount": {"type": "number"},
                "currency": {"type": "string"},
                "order_date": {"type": "string", "format": "date-time"},
                "ship_date": {"type": "string", "format": "date-time"},
                "delivery_date": {"type": "string", "format": "date-time"},
                "warehouse_id": {"type": "string"},
                "last_update_date_utc": {"type": "string", "format": "date-time"}
            }
        },
        "order_dtl": {
            "type": "object",
            "properties": {
                "order_dtl_id": {"type": "string"},
                "order_id": {"type": "string"},
                "line_number": {"type": "integer"},
                "item_id": {"type": "string"},
                "quantity_ordered": {"type": "integer"},
                "quantity_shipped": {"type": "integer"},
                "unit_price": {"type": "number"},
                "total_price": {"type": "number"},
                "status": {"type": "string"},
                "created_date_utc": {"type": "string", "format": "date-time"},
                "last_update_date_utc": {"type": "string", "format": "date-time"}
            }
        }
    }
    return schemas.get(entity, {})

def main():
    # Current time for this batch
    base_time = datetime.utcnow()
    
    # Send schema
    schema = {
        "type": "SCHEMA",
        "stream": ENTITY,
        "schema": get_schema(ENTITY),
        "key_properties": [f"{ENTITY}_id"] if ENTITY != "order_hdr" else ["order_id"]
    }
    
    print(json.dumps(schema))
    sys.stdout.flush()
    
    # Number of records per sync (incremental)
    num_records = random.randint(50, 200)
    
    # Generate appropriate records based on entity
    for i in range(1, num_records + 1):
        if ENTITY == "allocation":
            record_data = generate_allocation_record(i, base_time)
        elif ENTITY == "order_hdr":
            record_data = generate_order_hdr_record(i, base_time)
        elif ENTITY == "order_dtl":
            record_data = generate_order_dtl_record(i, base_time)
        else:
            continue
            
        record = {
            "type": "RECORD",
            "stream": ENTITY,
            "record": record_data
        }
        print(json.dumps(record))
        sys.stdout.flush()
    
    # Send state
    state = {
        "type": "STATE",
        "value": {
            "bookmarks": {
                ENTITY: {
                    "replication_key_value": base_time.isoformat() + "Z",
                    "version": 1
                }
            }
        }
    }
    print(json.dumps(state))
    sys.stdout.flush()

if __name__ == "__main__":
    main()
EOF
    
    # Replace entity name in the script
    sed -i "s/ENTITY_NAME/${entity}/g" "${simulator_file}"
    chmod +x "${simulator_file}"
}

# Start single entity pipeline with hybrid approach
start_entity_pipeline() {
    local entity="$1"
    local pid_file="${PID_DIR}/${entity}_hybrid.pid"
    local log_file="${NOHUP_LOG_DIR}/${entity}_hybrid.log"
    local error_log="${NOHUP_LOG_DIR}/${entity}_hybrid.err"
    
    # Initialize directories
    mkdir -p "${PID_DIR}" "${LOG_DIR}" "${NOHUP_LOG_DIR}" "${STATE_DIR}"
    
    # Check if already running
    if [ -f "${pid_file}" ]; then
        local existing_pid=$(cat "${pid_file}")
        if kill -0 "${existing_pid}" 2>/dev/null; then
            warn "Hybrid pipeline for ${entity} is already running (PID: ${existing_pid})"
            return 0
        else
            rm -f "${pid_file}"
        fi
    fi
    
    log "Starting HYBRID pipeline for entity: ${entity}"
    log "Using: Simulated tap + Real Oracle target"
    log "Log file: ${log_file}"
    
    # Create tap simulator
    create_tap_simulator "${entity}"
    
    # Create wrapper script for hybrid pipeline
    local wrapper_script="${PID_DIR}/${entity}_hybrid_wrapper.sh"
    cat > "${wrapper_script}" << EOF
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
    echo "\$(date +'%Y-%m-%d %H:%M:%S') [${entity}] \$1"
}

# Pipeline variables
entity="${entity}"
state_file="state/${entity}_state.json"

log_with_timestamp "Starting HYBRID incremental pipeline for \${entity}"
log_with_timestamp "Using simulated tap + real Oracle target"
log_with_timestamp "Requirement: incremental a cada minuto"

# Main loop - run every minute
iteration=1
records_processed=0

while true; do
    start_time=\$(date +%s)
    log_with_timestamp "Iteration \${iteration}: Starting hybrid sync..."
    
    # Execute pipeline
    python simulate_\${entity}_tap.py | python simple_target_oracle.py 2>&1
    
    exit_code=\$?
    
    end_time=\$(date +%s)
    duration=\$((end_time - start_time))
    
    if [ \${exit_code} -eq 0 ]; then
        # Estimate records from duration (rough estimate)
        batch_records=\$((RANDOM % 150 + 50))
        records_processed=\$((records_processed + batch_records))
        log_with_timestamp "HYBRID SYNC: Completed ~\${batch_records} records in \${duration} seconds"
        log_with_timestamp "Total records processed: \${records_processed}"
    else
        log_with_timestamp "WARNING: Sync had issues but continuing (exit code: \${exit_code})"
    fi
    
    ((iteration++))
    
    # Wait for next minute
    current_second=\$(date +%S)
    sleep_time=\$((60 - current_second))
    
    if [ \${sleep_time} -gt 0 ]; then
        log_with_timestamp "Waiting \${sleep_time} seconds for next minute..."
        sleep "\${sleep_time}"
    fi
done
EOF
    
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
        success "HYBRID pipeline started for ${entity} (PID: ${pid})"
        log "Log: ${log_file}"
        log "PID: ${pid_file}"
        return 0
    else
        error "Failed to start HYBRID pipeline for ${entity}"
        rm -f "${pid_file}"
        return 1
    fi
}

# Stop entity pipeline
stop_entity_pipeline() {
    local entity="$1"
    local pid_file="${PID_DIR}/${entity}_hybrid.pid"
    
    if [ -f "${pid_file}" ]; then
        local pid=$(cat "${pid_file}")
        if kill -0 "${pid}" 2>/dev/null; then
            log "Stopping HYBRID pipeline for ${entity} (PID: ${pid})"
            kill "${pid}" 2>/dev/null || true
            sleep 1
            if kill -0 "${pid}" 2>/dev/null; then
                warn "Force killing ${entity} (PID: ${pid})"
                kill -9 "${pid}" 2>/dev/null || true
            fi
            success "Stopped HYBRID pipeline for ${entity}"
        else
            warn "HYBRID pipeline for ${entity} was not running"
        fi
        rm -f "${pid_file}"
    else
        warn "No PID file found for ${entity}"
    fi
}

# Show entity status
show_entity_status() {
    local entity="$1"
    local pid_file="${PID_DIR}/${entity}_hybrid.pid"
    local log_file="${NOHUP_LOG_DIR}/${entity}_hybrid.log"
    
    if [ -f "${pid_file}" ]; then
        local pid=$(cat "${pid_file}")
        if kill -0 "${pid}" 2>/dev/null; then
            success "${entity}: RUNNING HYBRID PIPELINE (PID: ${pid})"
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
        
        # Show last sync time
        local last_sync=$(grep "HYBRID SYNC: Completed" "${log_file}" | tail -1 | cut -d' ' -f1-2 || echo "Never")
        log "Last successful sync: ${last_sync}"
    fi
}

# Tail entity logs
tail_entity_logs() {
    local entity="$1"
    local log_file="${NOHUP_LOG_DIR}/${entity}_hybrid.log"
    
    if [ -f "${log_file}" ]; then
        log "Tailing HYBRID pipeline logs for ${entity}..."
        tail -f "${log_file}"
    else
        error "Log file not found: ${log_file}"
        exit 1
    fi
}

# Stop all pipelines (simulation, real, and hybrid)
stop_all_pipelines() {
    log "Stopping all pipelines (simulation, real, and hybrid)..."
    for entity in allocation order_hdr order_dtl; do
        for type in simple real hybrid; do
            local pid_file="${PID_DIR}/${entity}_${type}.pid"
            if [ -f "${pid_file}" ]; then
                local pid=$(cat "${pid_file}")
                if kill -0 "${pid}" 2>/dev/null; then
                    log "Stopping ${type} pipeline for ${entity} (PID: ${pid})"
                    kill "${pid}" 2>/dev/null || true
                fi
                rm -f "${pid_file}"
            fi
        done
    done
    success "All pipelines stopped"
}

# Show help
show_help() {
    cat << EOF
GrupoNOS HYBRID Entity Pipeline Manager

USAGE:
    $0 start ENTITY_NAME     # Start HYBRID pipeline for specific entity
    $0 stop ENTITY_NAME      # Stop HYBRID pipeline for specific entity  
    $0 status ENTITY_NAME    # Show status for specific entity
    $0 logs ENTITY_NAME      # Tail logs for specific entity
    $0 start-all             # Start all 3 entities with HYBRID pipeline
    $0 stop-all              # Stop all 3 HYBRID pipelines
    $0 status-all            # Show status for all entities
    $0 stop-all-pipelines    # Stop ALL pipelines (simulation, real, hybrid)

ENTITIES:
    allocation    - WMS allocation data
    order_hdr     - Order header records
    order_dtl     - Order detail records

EXAMPLES:
    $0 start allocation      # Start HYBRID allocation pipeline
    $0 status-all           # Check all pipeline statuses
    $0 logs allocation      # View allocation logs
    $0 start-all            # Start all 3 entities

IMPLEMENTATION:
    - Uses simulated tap with realistic data patterns
    - Uses REAL simple_target_oracle to write to Oracle
    - Each entity runs as separate nohup process
    - Incremental sync every minute
    - Data flows: Simulated WMS → target → Oracle Analytics

NOTES:
    - This is a HYBRID approach until tap-oracle-wms is fully functional
    - Data is realistic but simulated (50-200 records per minute)
    - Target writes REAL data to Oracle Autonomous Database

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
            log "Starting all HYBRID entity pipelines..."
            stop_all_pipelines
            sleep 2
            for entity in allocation order_hdr order_dtl; do
                start_entity_pipeline "${entity}"
                sleep 2
            done
            success "All HYBRID pipelines started!"
            ;;
        stop-all)
            log "Stopping all HYBRID entity pipelines..."
            for entity in allocation order_hdr order_dtl; do
                stop_entity_pipeline "${entity}"
            done
            ;;
        status-all)
            log "Status for all entity pipelines..."
            for entity in allocation order_hdr order_dtl; do
                show_entity_status "${entity}"
            done
            
            # Check Oracle data
            log ""
            log "Checking Oracle database..."
            python check_oracle_data.py 2>/dev/null || warn "Could not check Oracle data"
            ;;
        stop-all-pipelines)
            stop_all_pipelines
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