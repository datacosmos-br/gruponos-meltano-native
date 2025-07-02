#!/bin/bash

# =============================================================================
# GRUPONOS MELTANO NATIVE - HEALTH CHECK SCRIPT
# =============================================================================

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Project configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENVIRONMENT=${MELTANO_ENVIRONMENT:-dev}

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  GrupoNOS WMS Pipeline - Health Check${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""
echo "Environment: $ENVIRONMENT"
echo "Project: $PROJECT_DIR"
echo ""

# Health check results
HEALTH_STATUS="HEALTHY"
ISSUES_FOUND=0

print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
    HEALTH_STATUS="UNHEALTHY"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
}

# Activate virtual environment
if [ -f "$PROJECT_DIR/.venv/bin/activate" ]; then
    source "$PROJECT_DIR/.venv/bin/activate"
    print_status "Virtual environment activated"
else
    print_error "Virtual environment not found at $PROJECT_DIR/.venv"
    exit 1
fi

# Load environment variables
if [ -f "$PROJECT_DIR/.env" ]; then
    export $(grep -v '^#' "$PROJECT_DIR/.env" | xargs)
    print_status "Environment variables loaded"
else
    print_error ".env file not found"
    exit 1
fi

export MELTANO_ENVIRONMENT=$ENVIRONMENT

echo ""
echo -e "${BLUE}1. System Prerequisites${NC}"
echo "======================="

# Check Python version
PYTHON_VERSION=$(python --version 2>&1 | cut -d' ' -f2)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 9 ]; then
    print_status "Python $PYTHON_VERSION (compatible)"
else
    print_error "Python 3.9+ required, found $PYTHON_VERSION"
fi

# Check Meltano installation
if command -v meltano &> /dev/null; then
    MELTANO_VERSION=$(meltano --version 2>&1)
    print_status "Meltano installed: $MELTANO_VERSION"
else
    print_error "Meltano not found"
fi

# Check dbt installation
if command -v dbt &> /dev/null; then
    DBT_VERSION=$(dbt --version 2>&1 | head -1)
    print_status "dbt installed: $DBT_VERSION"
else
    print_error "dbt not found"
fi

# Check Oracle client
if [ -n "$ORACLE_HOME" ] || [ -n "$LD_LIBRARY_PATH" ]; then
    print_status "Oracle environment variables detected"
else
    print_warning "Oracle Instant Client environment not detected"
fi

echo ""
echo -e "${BLUE}2. Configuration Validation${NC}"
echo "==========================="

# Check required environment variables
REQUIRED_VARS=(
    "WMS_ORACLE_HOST"
    "WMS_ORACLE_USERNAME" 
    "WMS_ORACLE_PASSWORD"
    "TARGET_ORACLE_HOST"
    "TARGET_ORACLE_USERNAME"
    "TARGET_ORACLE_PASSWORD"
)

for var in "${REQUIRED_VARS[@]}"; do
    if [ -n "${!var}" ]; then
        print_status "$var is set"
    else
        print_error "$var is not set"
    fi
done

# Check Meltano configuration
if meltano config list >/dev/null 2>&1; then
    print_status "Meltano configuration valid"
else
    print_error "Meltano configuration invalid"
fi

echo ""
echo -e "${BLUE}3. Database Connectivity${NC}"
echo "========================"

# Test WMS Oracle connection
echo "Testing WMS Oracle connection..."
if timeout 30 meltano invoke tap-oracle-wms --test-connection >/dev/null 2>&1; then
    print_status "WMS Oracle connection successful"
else
    print_error "WMS Oracle connection failed"
fi

# Test target Oracle connection  
echo "Testing target Oracle connection..."
if timeout 30 meltano invoke target-oracle --test-connection >/dev/null 2>&1; then
    print_status "Target Oracle connection successful"
else
    print_error "Target Oracle connection failed"
fi

# Test dbt connection
echo "Testing dbt connection..."
cd "$PROJECT_DIR/transform"
if timeout 30 dbt debug --profiles-dir profiles >/dev/null 2>&1; then
    print_status "dbt connection successful"
else
    print_error "dbt connection failed"
fi
cd "$PROJECT_DIR"

echo ""
echo -e "${BLUE}4. Data Freshness${NC}"
echo "================="

# Check data freshness (if data exists)
cd "$PROJECT_DIR/transform"
if dbt source freshness --profiles-dir profiles >/dev/null 2>&1; then
    print_status "Data freshness check passed"
else
    print_warning "Data freshness check failed or no data"
fi
cd "$PROJECT_DIR"

echo ""
echo -e "${BLUE}5. Pipeline Components${NC}"
echo "======================"

# Check tap-oracle-wms
if meltano invoke tap-oracle-wms --version >/dev/null 2>&1; then
    print_status "tap-oracle-wms functional"
else
    print_error "tap-oracle-wms not functional"
fi

# Check target-oracle
if meltano invoke target-oracle --version >/dev/null 2>&1; then
    print_status "target-oracle functional"
else
    print_error "target-oracle not functional"
fi

# Check dbt models
cd "$PROJECT_DIR/transform"
if dbt list --profiles-dir profiles >/dev/null 2>&1; then
    MODEL_COUNT=$(dbt list --profiles-dir profiles 2>/dev/null | wc -l)
    print_status "dbt models available: $MODEL_COUNT"
else
    print_error "dbt models not accessible"
fi
cd "$PROJECT_DIR"

echo ""
echo -e "${BLUE}6. Storage and Logs${NC}"
echo "=================="

# Check disk space
DISK_USAGE=$(df "$PROJECT_DIR" | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 90 ]; then
    print_status "Disk space OK ($DISK_USAGE% used)"
else
    print_warning "Disk space high ($DISK_USAGE% used)"
fi

# Check log directories
for log_dir in "logs" "logs/meltano" "logs/dbt" "transform/logs"; do
    if [ -d "$PROJECT_DIR/$log_dir" ]; then
        print_status "Log directory exists: $log_dir"
    else
        print_warning "Log directory missing: $log_dir"
    fi
done

echo ""
echo -e "${BLUE}7. Performance Metrics${NC}"
echo "======================"

# Check recent pipeline runs (if logs exist)
if [ -f "$PROJECT_DIR/logs/meltano/meltano.log" ]; then
    RECENT_ERRORS=$(tail -100 "$PROJECT_DIR/logs/meltano/meltano.log" | grep -i error | wc -l)
    if [ "$RECENT_ERRORS" -eq 0 ]; then
        print_status "No recent errors in Meltano logs"
    else
        print_warning "$RECENT_ERRORS recent errors found in Meltano logs"
    fi
else
    print_warning "No Meltano logs found"
fi

# Check state files
if [ -d "$PROJECT_DIR/.meltano/state" ]; then
    STATE_FILES=$(find "$PROJECT_DIR/.meltano/state" -name "*.json" | wc -l)
    print_status "State files found: $STATE_FILES"
else
    print_warning "No state directory found"
fi

echo ""
echo -e "${BLUE}8. Security Check${NC}"
echo "================="

# Check file permissions
if [ -f "$PROJECT_DIR/.env" ]; then
    ENV_PERMS=$(stat -f "%A" "$PROJECT_DIR/.env" 2>/dev/null || stat -c "%a" "$PROJECT_DIR/.env" 2>/dev/null)
    if [ "$ENV_PERMS" = "600" ] || [ "$ENV_PERMS" = "644" ]; then
        print_status ".env file permissions OK ($ENV_PERMS)"
    else
        print_warning ".env file permissions: $ENV_PERMS (consider 600)"
    fi
fi

# Check for sensitive data in logs
if [ -d "$PROJECT_DIR/logs" ]; then
    SENSITIVE_LOGS=$(grep -r -i "password\|secret\|token" "$PROJECT_DIR/logs" 2>/dev/null | wc -l)
    if [ "$SENSITIVE_LOGS" -eq 0 ]; then
        print_status "No sensitive data found in logs"
    else
        print_warning "Potential sensitive data found in logs"
    fi
fi

echo ""
echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  Health Check Summary${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

if [ "$HEALTH_STATUS" = "HEALTHY" ]; then
    if [ "$ISSUES_FOUND" -eq 0 ]; then
        echo -e "${GREEN}✓ System Status: HEALTHY${NC}"
        echo -e "${GREEN}✓ No issues found${NC}"
        EXIT_CODE=0
    else
        echo -e "${YELLOW}⚠ System Status: HEALTHY (with warnings)${NC}"
        echo -e "${YELLOW}⚠ $ISSUES_FOUND warnings found${NC}"
        EXIT_CODE=1
    fi
else
    echo -e "${RED}✗ System Status: UNHEALTHY${NC}"
    echo -e "${RED}✗ $ISSUES_FOUND issues found${NC}"
    EXIT_CODE=2
fi

echo ""
echo "Next steps:"
if [ "$HEALTH_STATUS" = "UNHEALTHY" ]; then
    echo "1. Address the critical errors listed above"
    echo "2. Re-run health check: ./scripts/health-check.sh"
    echo "3. Check logs for more details: tail -f logs/meltano/meltano.log"
elif [ "$ISSUES_FOUND" -gt 0 ]; then
    echo "1. Consider addressing the warnings listed above"
    echo "2. Run pipeline test: make test"
    echo "3. Monitor logs during next run"
else
    echo "1. System is ready for operation"
    echo "2. Run pipeline: make run"
    echo "3. Monitor performance: make status"
fi

echo ""
echo "For support, check the README.md or contact the Data Engineering team."

exit $EXIT_CODE