#!/bin/bash

# =============================================================================
# GRUPONOS REAL PIPELINE EXECUTOR
# =============================================================================
# Run real tap-oracle-wms with simple_target_oracle
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

# Change to project directory
cd "${PROJECT_DIR}"

# Load environment
set -a
source .env 2>/dev/null || true
set +a

# Function to run pipeline for specific entity
run_entity_pipeline() {
    local entity="$1"
    local mode="${2:-incremental}"  # incremental or full
    
    log "🚀 Starting ${mode} pipeline for entity: ${entity}"
    
    # Create state file directory
    mkdir -p state
    
    # Set up tap configuration
    local tap_config="tap-config.json"
    local state_file="state/${entity}_state.json"
    
    # Build catalog with specific entity
    local catalog_file="catalog_${entity}.json"
    
    # Create minimal catalog for single entity
    cat > "${catalog_file}" << EOF
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
            "forced-replication-method": "${mode}"
          }
        }
      ]
    }
  ]
}
EOF
    
    # Build pipeline command
    local tap_command="python -m tap_oracle_wms"
    export PYTHONPATH="/home/marlonsc/flext/flext-tap-oracle-wms/src:$PYTHONPATH"
    tap_command+=" --config ${tap_config}"
    tap_command+=" --catalog ${catalog_file}"
    
    if [ -f "${state_file}" ] && [ "${mode}" = "incremental" ]; then
        tap_command+=" --state ${state_file}"
        log "Using state file: ${state_file}"
    fi
    
    local target_command="python simple_target_oracle.py"
    
    log "Executing pipeline:"
    log "TAP: ${tap_command}"
    log "TARGET: ${target_command}"
    
    # Execute pipeline with state management
    if [ "${mode}" = "incremental" ]; then
        # For incremental, capture state
        ${tap_command} | tee >(grep '^{"type": "STATE"' > "${state_file}.tmp") | ${target_command}
        
        # Update state file if new state was captured
        if [ -s "${state_file}.tmp" ]; then
            tail -1 "${state_file}.tmp" > "${state_file}"
            log "State updated: $(cat ${state_file})"
        fi
        rm -f "${state_file}.tmp"
    else
        # For full sync, just run without state
        ${tap_command} | ${target_command}
    fi
    
    local exit_code=$?
    
    # Clean up catalog
    rm -f "${catalog_file}"
    
    if [ ${exit_code} -eq 0 ]; then
        success "Pipeline completed for ${entity}"
    else
        error "Pipeline failed for ${entity}"
        return ${exit_code}
    fi
}

# Show help
show_help() {
    cat << EOF
GrupoNOS Real Pipeline Executor

USAGE:
    $0 ENTITY_NAME [MODE]
    $0 test                  # Test with small sample
    $0 all [MODE]           # Run all entities

ENTITIES:
    allocation    - WMS allocation data
    order_hdr     - Order header records
    order_dtl     - Order detail records

MODES:
    incremental   - Incremental sync (default)
    full         - Full table sync

EXAMPLES:
    $0 allocation           # Run incremental sync for allocation
    $0 allocation full      # Run full sync for allocation
    $0 test                # Test pipeline with sample data
    $0 all                 # Run incremental for all entities
    $0 all full           # Run full sync for all entities

EOF
}

# Main execution
main() {
    local entity="${1:-help}"
    local mode="${2:-incremental}"
    
    case "${entity}" in
        allocation|order_hdr|order_dtl)
            run_entity_pipeline "${entity}" "${mode}"
            ;;
        test)
            log "Running test pipeline with sample data..."
            # Test with a simple record
            echo '{"type": "SCHEMA", "stream": "test", "schema": {"properties": {"id": {"type": "integer"}, "name": {"type": "string"}}}}' | python simple_target_oracle.py
            echo '{"type": "RECORD", "stream": "test", "record": {"id": 1, "name": "Test Record"}}' | python simple_target_oracle.py
            ;;
        all)
            log "Running pipeline for all entities (mode: ${mode})..."
            for e in allocation order_hdr order_dtl; do
                run_entity_pipeline "${e}" "${mode}"
                sleep 2
            done
            ;;
        help|-h|--help)
            show_help
            ;;
        *)
            error "Unknown entity: ${entity}"
            show_help
            exit 1
            ;;
    esac
}

# Execute main function
main "$@"