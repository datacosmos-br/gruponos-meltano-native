#!/bin/bash

# Automated Documentation Maintenance Script
# This script runs scheduled documentation maintenance tasks for gruponos-meltano-native
#
# Usage:
#   ./scripts/automated_docs_maintenance.sh [daily|weekly|monthly|full]
#
# Author: FLEXT Documentation Team
# Version: 1.0.0

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="$PROJECT_ROOT/docs/docs_maintenance_config.json"
LOG_FILE="$PROJECT_ROOT/logs/docs_maintenance.log"
REPORTS_DIR="$PROJECT_ROOT/docs/reports"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
    echo "[$level] $message"
}

info() {
    log "INFO" "$1"
}

warn() {
    log "WARN" "$1"
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    log "ERROR" "$1"
    echo -e "${RED}❌ $1${NC}" >&2
}

success() {
    log "SUCCESS" "$1"
    echo -e "${GREEN}✅ $1${NC}"
}

# Setup function
setup() {
    info "Setting up documentation maintenance environment"

    # Create necessary directories
    mkdir -p "$REPORTS_DIR"
    mkdir -p "$(dirname "$LOG_FILE")"

    # Check if Python script exists
    if [[ ! -f "$SCRIPT_DIR/docs_maintenance.py" ]]; then
        error "Documentation maintenance script not found: $SCRIPT_DIR/docs_maintenance.py"
        exit 1
    fi

    # Check if config exists
    if [[ ! -f "$CONFIG_FILE" ]]; then
        warn "Configuration file not found: $CONFIG_FILE"
        warn "Using default configuration"
    fi

    success "Setup completed"
}

# Run maintenance task
run_maintenance() {
    local task="$1"
    local output_file=""

    info "Starting $task maintenance task"

    case "$task" in
        "audit")
            output_file="$REPORTS_DIR/docs_audit_$(date +%Y%m%d_%H%M%S).json"
            python "$SCRIPT_DIR/docs_maintenance.py" audit --output "$output_file"
            ;;
        "validate")
            output_file="$REPORTS_DIR/docs_validation_$(date +%Y%m%d_%H%M%S).json"
            python "$SCRIPT_DIR/docs_maintenance.py" validate --output "$output_file"
            ;;
        "optimize")
            output_file="$REPORTS_DIR/docs_optimization_$(date +%Y%m%d_%H%M%S).json"
            python "$SCRIPT_DIR/docs_maintenance.py" optimize --output "$output_file"
            ;;
        "sync")
            output_file="$REPORTS_DIR/docs_sync_$(date +%Y%m%d_%H%M%S).json"
            python "$SCRIPT_DIR/docs_maintenance.py" sync --output "$output_file"
            ;;
        "report")
            output_file="$REPORTS_DIR/docs_report_$(date +%Y%m%d_%H%M%S).html"
            python "$SCRIPT_DIR/docs_maintenance.py" report --format html --output "$output_file"
            ;;
        "maintenance")
            output_file="$REPORTS_DIR/docs_maintenance_$(date +%Y%m%d_%H%M%S).json"
            python "$SCRIPT_DIR/docs_maintenance.py" maintenance --output "$output_file"
            ;;
        *)
            error "Unknown maintenance task: $task"
            echo "Available tasks: audit, validate, optimize, sync, report, maintenance"
            exit 1
            ;;
    esac

    if [[ -f "$output_file" ]]; then
        success "$task maintenance completed - Report: $output_file"

        # Check for critical issues
        if command -v jq &> /dev/null && [[ "$output_file" == *.json ]]; then
            critical_issues=$(jq '.summary.critical_issues // 0' "$output_file" 2>/dev/null || echo "0")
            if [[ "$critical_issues" -gt 0 ]]; then
                warn "Found $critical_issues critical issues in documentation"
                # Could send notifications here
            fi
        fi
    else
        error "$task maintenance failed - No output file generated"
        return 1
    fi
}

# Daily maintenance tasks
run_daily() {
    info "Running daily maintenance tasks"

    # Quick audit
    run_maintenance "audit"

    # Link validation (lighter check)
    run_maintenance "validate"

    # Generate summary report
    run_maintenance "report"

    success "Daily maintenance completed"
}

# Weekly maintenance tasks
run_weekly() {
    info "Running weekly maintenance tasks"

    # Full maintenance cycle
    run_maintenance "maintenance"

    # Content optimization
    run_maintenance "optimize"

    # Sync with codebase
    run_maintenance "sync"

    success "Weekly maintenance completed"
}

# Monthly maintenance tasks
run_monthly() {
    info "Running monthly maintenance tasks"

    # Comprehensive audit
    run_maintenance "audit"

    # Full validation
    run_maintenance "validate"

    # Complete maintenance cycle
    run_maintenance "maintenance"

    # Generate detailed HTML report
    run_maintenance "report"

    # Archive old reports (keep last 12 months)
    cleanup_old_reports

    success "Monthly maintenance completed"
}

# Full maintenance (manual or emergency)
run_full() {
    info "Running full maintenance cycle"

    run_maintenance "audit"
    run_maintenance "validate"
    run_maintenance "optimize"
    run_maintenance "sync"
    run_maintenance "maintenance"
    run_maintenance "report"

    success "Full maintenance cycle completed"
}

# Cleanup old reports
cleanup_old_reports() {
    info "Cleaning up old reports (keeping last 12 months)"

    # Find reports older than 12 months
    find "$REPORTS_DIR" -name "*.json" -o -name "*.html" -type f -mtime +365 -exec rm {} \; 2>/dev/null || true

    local deleted_count=$?
    info "Cleaned up $deleted_count old report files"
}

# Health check
health_check() {
    info "Running health check"

    local issues=0

    # Check if script is executable
    if [[ ! -x "$SCRIPT_DIR/docs_maintenance.py" ]]; then
        error "Maintenance script is not executable"
        ((issues++))
    fi

    # Check if config exists
    if [[ ! -f "$CONFIG_FILE" ]]; then
        warn "Configuration file missing: $CONFIG_FILE"
        ((issues++))
    fi

    # Check disk space
    local available_space=$(df "$PROJECT_ROOT" | tail -1 | awk '{print $4}')
    if [[ $available_space -lt 100000 ]]; then  # Less than 100MB
        warn "Low disk space available: ${available_space}KB"
        ((issues++))
    fi

    # Check Python availability
    if ! command -v python &> /dev/null; then
        error "Python not found in PATH"
        ((issues++))
    fi

    # Check git status
    if ! git -C "$PROJECT_ROOT" status &> /dev/null; then
        warn "Git repository status check failed"
        ((issues++))
    fi

    if [[ $issues -eq 0 ]]; then
        success "Health check passed - All systems operational"
        return 0
    else
        warn "Health check found $issues issues"
        return 1
    fi
}

# Notification function (placeholder for actual implementation)
send_notification() {
    local level="$1"
    local message="$2"

    # Placeholder for notification systems
    # Could integrate with Slack, email, GitHub issues, etc.

    case "$level" in
        "CRITICAL")
            # Send immediate notification
            warn "CRITICAL: $message"
            ;;
        "WARNING")
            # Log warning
            warn "WARNING: $message"
            ;;
        "INFO")
            info "INFO: $message"
            ;;
    esac
}

# Main function
main() {
    local command="${1:-help}"

    # Initialize logging
    touch "$LOG_FILE"

    info "Documentation Maintenance Script started with command: $command"

    # Setup environment
    setup

    # Health check
    if ! health_check; then
        error "Health check failed - aborting maintenance"
        exit 1
    fi

    # Execute requested command
    case "$command" in
        "daily")
            run_daily
            ;;
        "weekly")
            run_weekly
            ;;
        "monthly")
            run_monthly
            ;;
        "full")
            run_full
            ;;
        "audit")
            run_maintenance "audit"
            ;;
        "validate")
            run_maintenance "validate"
            ;;
        "optimize")
            run_maintenance "optimize"
            ;;
        "sync")
            run_maintenance "sync"
            ;;
        "report")
            run_maintenance "report"
            ;;
        "maintenance")
            run_maintenance "maintenance"
            ;;
        "health")
            health_check
            ;;
        "cleanup")
            cleanup_old_reports
            ;;
        "help"|*)
            echo "Automated Documentation Maintenance Script"
            echo ""
            echo "Usage: $0 [command]"
            echo ""
            echo "Commands:"
            echo "  daily       - Run daily maintenance tasks"
            echo "  weekly      - Run weekly maintenance tasks"
            echo "  monthly     - Run monthly maintenance tasks"
            echo "  full        - Run complete maintenance cycle"
            echo "  audit       - Content quality audit only"
            echo "  validate    - Link validation only"
            echo "  optimize    - Content optimization only"
            echo "  sync        - Codebase synchronization only"
            echo "  report      - Generate quality report only"
            echo "  maintenance - Full maintenance cycle"
            echo "  health      - System health check"
            echo "  cleanup     - Clean up old reports"
            echo "  help        - Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 daily"
            echo "  $0 weekly"
            echo "  $0 full"
            echo ""
            exit 0
            ;;
    esac

    info "Documentation Maintenance Script completed successfully"
}

# Error handling
trap 'error "Script failed with exit code $?"' ERR

# Run main function
main "$@"