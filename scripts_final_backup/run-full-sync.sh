#!/bin/bash

# =============================================================================
# GRUPONOS FULL SYNC SCRIPT
# =============================================================================
# User requirement: "o full só quero uma vez"
# Execute full sync for all 3 entities individually
# 
# Usage: ./scripts/run-full-sync.sh [entity_name]
#   - Without parameters: Run full sync for all entities
#   - With entity parameter: Run full sync for specific entity
# =============================================================================

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] SUCCESS:${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

# Check if meltano is available
check_meltano() {
    if ! command -v meltano &> /dev/null; then
        error "Meltano not found. Please install meltano first."
        exit 1
    fi
}

# Check if .env file exists
check_env() {
    if [ ! -f ".env" ]; then
        error ".env file not found. Please create .env with required credentials."
        exit 1
    fi
}

# Execute full sync for a specific entity
run_entity_full_sync() {
    local entity="$1"
    local job_name="${entity}_full_sync"
    
    log "Starting full sync for entity: ${entity}"
    log "Job name: ${job_name}"
    
    # Check if job exists in meltano.yml
    if ! meltano job list | grep -q "${job_name}"; then
        error "Job '${job_name}' not found in meltano.yml"
        return 1
    fi
    
    # Execute the full sync job
    log "Executing: meltano run ${job_name}"
    
    if meltano run "${job_name}"; then
        success "Full sync completed successfully for entity: ${entity}"
        
        # Log sync statistics (if available)
        log "Sync completed at: $(date)"
        
        return 0
    else
        error "Full sync failed for entity: ${entity}"
        return 1
    fi
}

# Main execution function
main() {
    local entity_param="${1:-}"
    
    log "GrupoNOS Full Sync Script"
    log "Requirement: Full sync só uma vez (manual execution only)"
    log "=================================================="
    
    # Validations
    check_meltano
    check_env
    
    # Load environment variables
    set -a
    source .env
    set +a
    
    log "Environment loaded successfully"
    
    # Define entities to sync
    local entities=()
    
    if [ -n "${entity_param}" ]; then
        # Single entity specified
        case "${entity_param}" in
            allocation|order_hdr|order_dtl)
                entities=("${entity_param}")
                log "Single entity sync requested: ${entity_param}"
                ;;
            *)
                error "Invalid entity: ${entity_param}"
                error "Valid entities: allocation, order_hdr, order_dtl"
                exit 1
                ;;
        esac
    else
        # All entities
        entities=("allocation" "order_hdr" "order_dtl")
        log "Full sync for all 3 entities requested"
    fi
    
    # Execute sync for each entity
    local success_count=0
    local total_count=${#entities[@]}
    
    for entity in "${entities[@]}"; do
        log ""
        log "Processing entity ${entity} (${success_count}/${total_count} completed)..."
        
        if run_entity_full_sync "${entity}"; then
            ((success_count++))
        else
            error "Failed to sync entity: ${entity}"
        fi
    done
    
    # Final summary
    log ""
    log "=================================================="
    log "FULL SYNC SUMMARY"
    log "=================================================="
    log "Total entities: ${total_count}"
    log "Successful syncs: ${success_count}"
    log "Failed syncs: $((total_count - success_count))"
    
    if [ ${success_count} -eq ${total_count} ]; then
        success "ALL ENTITIES SYNCED SUCCESSFULLY!"
        success "Full sync requirement completed: 'full só quero uma vez'"
        return 0
    else
        error "Some entities failed to sync. Check logs above."
        return 1
    fi
}

# Help function
show_help() {
    cat << EOF
GrupoNOS Full Sync Script

USAGE:
    $0 [ENTITY_NAME]

PARAMETERS:
    ENTITY_NAME    Optional. Specific entity to sync (allocation, order_hdr, order_dtl)
                   If not provided, all entities will be synced.

EXAMPLES:
    $0                    # Sync all entities
    $0 allocation         # Sync only allocation entity
    $0 order_hdr         # Sync only order headers
    $0 order_dtl         # Sync only order details

ENTITIES:
    allocation    - WMS allocation data (largest entity)
    order_hdr     - Order header records
    order_dtl     - Order detail records

REQUIREMENTS:
    - Meltano installed and configured
    - .env file with database credentials
    - Access to WMS Oracle and target Oracle databases

NOTES:
    - This script implements "full só quero uma vez" requirement
    - Full sync is for initial data load only
    - For ongoing sync, use incremental sync (automated every minute)
    - Each entity has separate job due to large data volumes

EOF
}

# Handle script parameters
case "${1:-}" in
    -h|--help|help)
        show_help
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac