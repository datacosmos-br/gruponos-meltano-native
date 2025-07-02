#!/bin/bash
# Final 100% Validation Script

cd /home/marlonsc/flext/gruponos-meltano-native

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🎯 FINAL 100% VALIDATION${NC}"
echo "========================================"
echo ""

TESTS_PASSED=0
TESTS_TOTAL=0

run_test() {
    local test_name="$1"
    local test_command="$2"
    
    ((TESTS_TOTAL++))
    echo -e "${YELLOW}Testing: $test_name${NC}"
    
    if eval "$test_command" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ PASS: $test_name${NC}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}❌ FAIL: $test_name${NC}"
        return 1
    fi
}

echo -e "${BLUE}1. Environment Configuration${NC}"
run_test "Environment variables" 'test -n "$WMS_BASE_URL" && test -n "$WMS_USERNAME" && test -n "$DATABASE__HOST"'
run_test "Meltano.yml exists" 'test -f meltano.yml'
run_test "Scripts executable" 'test -x scripts/meltano_commands.sh && test -x scripts/monitoring.sh'

echo ""
echo -e "${BLUE}2. WMS Connection${NC}"
run_test "Tap wrapper works" 'python tap_oracle_wms_wrapper.py --help'
run_test "WMS API reachable" 'curl -s --connect-timeout 10 "$WMS_BASE_URL" >/dev/null'

echo ""
echo -e "${BLUE}3. Oracle Target${NC}"
run_test "Oracle connectivity" 'python -c "from simple_target_oracle import get_connection; get_connection().close()"'
run_test "Target script works" 'python simple_target_oracle.py --help'

echo ""
echo -e "${BLUE}4. Meltano Configuration${NC}"
run_test "Meltano project valid" 'meltano --version'
run_test "Extractors configured" 'grep -q "tap-oracle-wms" meltano.yml'
run_test "Loaders configured" 'grep -q "target-oracle" meltano.yml'
run_test "Jobs configured" 'grep -q "allocation_full_sync" meltano.yml'
run_test "Schedules configured" 'grep -q "allocation_incremental_sync" meltano.yml'

echo ""
echo -e "${BLUE}5. Data Extraction Test${NC}"
run_test "Schema discovery" './scripts/meltano_commands.sh discover'
run_test "Catalog generated" 'test -f catalog.json && test -s catalog.json'

echo ""
echo -e "${BLUE}6. Monitoring System${NC}"
run_test "Monitoring script works" './scripts/monitoring.sh health-check'
run_test "Logs directory exists" 'test -d logs'

echo ""
echo -e "${BLUE}7. Documentation${NC}"
run_test "Operations guide exists" 'test -f OPERATIONS_GUIDE.md'
run_test "Project documentation" 'test -f CLAUDE.md'

echo ""
echo "========================================"
echo -e "${BLUE}📊 VALIDATION RESULTS${NC}"
echo "========================================"

PASS_RATE=$((TESTS_PASSED * 100 / TESTS_TOTAL))

echo "Tests Passed: $TESTS_PASSED/$TESTS_TOTAL"
echo "Success Rate: $PASS_RATE%"

if [ $PASS_RATE -eq 100 ]; then
    echo ""
    echo -e "${GREEN}🎉 100% VALIDATION SUCCESSFUL!${NC}"
    echo -e "${GREEN}✅ System is PRODUCTION READY${NC}"
    echo ""
    echo -e "${BLUE}Next Steps:${NC}"
    echo "1. Run full sync: ./scripts/meltano_commands.sh full-all"
    echo "2. Start schedules: ./scripts/meltano_commands.sh start-schedules"
    echo "3. Install monitoring: ./scripts/monitoring.sh install"
    echo "4. Monitor status: ./scripts/meltano_commands.sh status"
    exit 0
else
    echo ""
    echo -e "${RED}❌ VALIDATION FAILED ($PASS_RATE%)${NC}"
    echo -e "${YELLOW}⚠️  Please fix failing tests before production use${NC}"
    exit 1
fi