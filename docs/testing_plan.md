# Testing Plan - GrupoNOS Meltano Native

**Version**: 0.9.0 | **Updated**: 2025-10-10 | **Status**: ⚠️ BLOCKED - Import failures preventing execution

---

## 📋 Testing Overview

### **Current Testing Status**
- **Coverage Target**: 90% minimum (configured in pyproject.toml)
- **Test Categories**: Unit, integration, WMS, Oracle, performance, smoke, e2e
- **Test Framework**: pytest with comprehensive markers and fixtures
- **Test Structure**: 344 tests across unit and integration suites
- **Critical Issue**: ❌ **BLOCKED** - flext-meltano import failures prevent all test execution

### **Testing Architecture**
```
tests/
├── unit/                          # Unit tests (300+ tests)
│   ├── test_cli.py               # CLI functionality (22K lines)
│   ├── test_config.py            # Configuration management
│   ├── test_orchestrator.py      # Meltano orchestration
│   ├── test_oracle_*.py          # Oracle operations (6 files)
│   ├── test_validators.py        # Data validation
│   └── test_*.py                 # Additional unit tests
├── integration/                   # Integration tests (44 tests)
│   ├── test_end_to_end_oracle.py # Full ETL pipeline
│   └── test_performance_and_load.py # Performance validation
├── conftest.py                   # ❌ MISSING - Centralized fixtures
└── README.md                     # Testing documentation
```

---

## 🚨 CRITICAL TESTING BLOCKERS

### **Blocker 1: Import Failures**

**Status**: ❌ **CRITICAL** - No tests can execute

**Issue**: `flext_meltano.models.py` line 50 uses non-existent `FlextModels.BaseModel`:
```python
# ❌ BROKEN - This import fails
from gruponos_meltano_native import GruponosMeltanoOrchestrator
# Leads to: AttributeError: type object 'FlextModels' has no attribute 'BaseModel'
```

**Root Cause**: flext-meltano dependency uses incorrect FlextModels base class.

**Impact**:
- Cannot run any tests
- Cannot validate ETL pipeline functionality
- Cannot generate coverage reports
- Blocks CI/CD pipeline execution

**Required Fix**:
```python
# ✅ CORRECT - Use available base classes
class TapRunParams(FlextModels.ArbitraryTypesModel):  # Instead of BaseModel
class OtherModel(FlextModels.StrictArbitraryTypesModel):
```

### **Blocker 2: Missing conftest.py**

**Status**: ❌ **HIGH PRIORITY** - No shared test infrastructure

**Issue**: 344 tests lack centralized fixtures, database setup, and mock infrastructure.

**Missing Components**:
- Oracle database connection fixtures
- Meltano configuration fixtures
- WMS API mock fixtures
- Test database setup/teardown
- Environment variable mocking

**Impact**:
- Test duplication across files
- Inconsistent test setup
- No shared database state management
- Difficult to maintain test infrastructure

---

## 📊 Testing Strategy

### **Test Categories & Coverage Targets**

| Category | Target Coverage | Current Status | Description |
|----------|----------------|----------------|-------------|
| **Unit Tests** | 85% | ❌ Blocked | Individual component testing |
| **Integration Tests** | 90% | ❌ Blocked | End-to-end pipeline testing |
| **Oracle Tests** | 95% | ❌ Blocked | Database connectivity and operations |
| **WMS Tests** | 95% | ❌ Blocked | REST API integration testing |
| **Performance Tests** | 80% | ❌ Blocked | Load and performance validation |
| **Security Tests** | 100% | ❌ Blocked | Security vulnerability testing |

### **Test Markers**

```python
# Unit tests (fast, isolated)
@pytest.mark.unit                    # Core functionality tests

# Integration tests (with dependencies)
@pytest.mark.integration             # Full pipeline integration
@pytest.mark.oracle                  # Oracle database operations
@pytest.mark.wms                     # Oracle WMS operations

# Special categories
@pytest.mark.performance             # Performance benchmarks
@pytest.mark.slow                    # Slow-running tests
@pytest.mark.smoke                   # Basic functionality smoke tests
@pytest.mark.e2e                     # End-to-end workflow tests
@pytest.mark.destructive             # Tests that modify data
```

---

## 🔧 Required Testing Infrastructure

### **conftest.py Implementation**

**Status**: ❌ Missing - Must be implemented to enable testing

**Required Fixtures**:

```python
# tests/conftest.py - CENTRALIZED TEST INFRASTRUCTURE

@pytest.fixture(scope="session")
def oracle_connection():
    """Provide Oracle database connection for integration tests."""
    # Setup test database connection
    # Yield connection for tests
    # Cleanup after tests

@pytest.fixture
def meltano_config():
    """Provide Meltano configuration for pipeline tests."""
    # Create temporary meltano.yml
    # Yield config path
    # Cleanup temp files

@pytest.fixture
def wms_api_mock():
    """Mock Oracle WMS REST API for testing."""
    # Setup httpx mock responses
    # Yield mock client
    # Verify calls made

@pytest.fixture
def temp_etl_data():
    """Provide test data for ETL pipeline testing."""
    # Create sample allocation/order data
    # Yield data fixtures
    # Cleanup temp data
```

### **Test Database Setup**

**Status**: ❌ Missing - Required for integration tests

**Requirements**:
- Oracle test database instance (or Docker container)
- Schema setup and teardown scripts
- Test data seeding procedures
- Connection pooling for concurrent tests
- Transaction rollback for test isolation

### **Mock Infrastructure**

**Status**: ⚠️ Partial - Basic mocking exists but not centralized

**Required Enhancements**:
- Centralized mock factories
- Consistent response patterns
- Error scenario simulation
- Performance testing mocks

---

## 📋 Test Execution Procedures

### **Local Development Testing**

```bash
# After fixing import issues:

# Run all tests
make test

# Run specific categories
make test-unit               # Unit tests only
make test-integration        # Integration tests

# Run with coverage
make test-coverage          # Generate coverage report
make coverage-html          # HTML coverage report

# Run specific test files
PYTHONPATH=src pytest tests/unit/test_orchestrator.py -v
PYTHONPATH=src pytest tests/integration/test_end_to_end_oracle.py -v

# Run with markers
PYTHONPATH=src pytest -m "oracle and integration" -v
PYTHONPATH=src pytest -m "not slow" -v
```

### **CI/CD Testing Pipeline**

**Status**: ❌ Blocked - Cannot implement until import issues resolved

**Required Pipeline**:
```yaml
# .github/workflows/test.yml
name: Test Suite
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      - name: Install dependencies
        run: |
          poetry install
      - name: Run tests with coverage
        run: |
          make test-coverage
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## 🔍 Test Coverage Analysis

### **Coverage Requirements by Module**

| Module | Lines | Target | Status | Notes |
|--------|-------|--------|--------|-------|
| `cli.py` | 443 | 90% | ❌ Blocked | Click command handling |
| `orchestrator.py` | 389 | 95% | ❌ Blocked | Meltano pipeline orchestration |
| `config.py` | 267 | 90% | ❌ Blocked | Pydantic configuration |
| `models.py` | 198 | 85% | ❌ Blocked | Domain models |
| `constants.py` | 156 | 80% | ❌ Blocked | System constants |
| **Total** | **1453** | **90%** | ❌ Blocked | Overall project coverage |

### **Critical Path Coverage**

**Must achieve 95%+ coverage on**:
- ETL pipeline orchestration logic
- Oracle connectivity and error handling
- WMS API integration points
- Configuration validation
- Data transformation logic

---

## 🚨 Test Failure Analysis

### **Current Failure Patterns**

1. **Import Failures** (100% of tests):
   ```
   AttributeError: type object 'FlextModels' has no attribute 'BaseModel'
   ```
   **Solution**: Fix flext-meltano to use correct base classes

2. **Missing Fixtures** (Integration tests):
   ```
   fixture 'oracle_connection' not found
   ```
   **Solution**: Implement conftest.py with centralized fixtures

3. **Database Connection Issues** (Oracle tests):
   ```
   Connection refused or credentials invalid
   ```
   **Solution**: Setup test database infrastructure

### **Expected Test Results After Fixes**

**Unit Tests** (300+ tests):
- ✅ CLI command parsing and validation
- ✅ Configuration loading and validation
- ✅ Model serialization and validation
- ✅ Orchestrator pipeline setup
- ✅ Error handling and recovery

**Integration Tests** (44 tests):
- ✅ Full ETL pipeline execution
- ✅ Oracle WMS API connectivity
- ✅ Oracle database loading
- ✅ End-to-end data flow validation
- ✅ Error recovery scenarios

---

## 📈 Performance Testing

### **Performance Test Categories**

| Test Type | Target | Status | Description |
|-----------|--------|--------|-------------|
| **Data Loading** | < 5 min for 10K records | ❌ Blocked | ETL pipeline throughput |
| **Memory Usage** | < 500MB peak | ❌ Blocked | Memory consumption monitoring |
| **Concurrent Pipelines** | 3+ simultaneous | ❌ Blocked | Multi-pipeline execution |
| **Large Dataset** | 1M+ records | ❌ Blocked | Scalability validation |

### **Performance Baselines**

**Target Performance Metrics**:
- Full sync pipeline: < 30 minutes for 100K records
- Incremental sync: < 5 minutes for 10K changes
- Memory usage: < 1GB for 500K record processing
- CPU utilization: < 80% during peak processing

---

## 🔧 Testing Tools & Dependencies

### **Core Testing Stack**

```toml
# pyproject.toml test dependencies
[tool.poetry.group.test.dependencies]
pytest = "^8.4.0"
pytest-cov = "^6.3.0"
pytest-mock = "^3.15.0"
pytest-xdist = "^3.8.0"
factory-boy = "^3.3.1"
faker = "^37.11.0"
hypothesis = "^6.140.0"
```

### **Test Configuration**

```toml
# pyproject.toml pytest configuration
[tool.pytest.ini_options]
addopts = [
    "--cov-fail-under=90",
    "--maxfail=1",
    "--strict-config",
    "--strict-markers",
]
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "oracle: Oracle database tests",
    "wms: WMS integration tests",
    "performance: Performance tests",
    "slow: Slow tests",
    "smoke: Smoke tests",
    "e2e: End-to-end tests",
]
```

---

## 📋 Testing Best Practices

### **Test Organization**

```python
# ✅ CORRECT - Clear test structure
class TestOrchestrator:
    """Test GruponosMeltanoOrchestrator functionality."""

    def test_pipeline_creation(self, meltano_config):
        """Test pipeline creation with valid configuration."""
        orchestrator = GruponosMeltanoOrchestrator()
        result = orchestrator.create_pipeline("test-pipeline")
        assert result.is_success

    def test_pipeline_execution(self, meltano_config, oracle_connection):
        """Test full pipeline execution with mocked dependencies."""
        # Test implementation
```

### **Fixture Usage**

```python
# ✅ CORRECT - Use centralized fixtures
def test_oracle_connection(oracle_connection):
    """Test Oracle connectivity."""
    result = oracle_connection.test_connection()
    assert result.is_success

# ❌ AVOID - Duplicate fixture code
def test_oracle_connection():
    """Test Oracle connectivity."""
    conn = OracleConnection(host="localhost", ...)  # Duplicated setup
    result = conn.test_connection()
    assert result.is_success
```

### **Mock Best Practices**

```python
# ✅ CORRECT - Comprehensive mocking
def test_wms_api_integration(wms_api_mock):
    """Test WMS API integration with proper mocking."""
    mock_response = {"allocations": [...]}
    wms_api_mock.get_allocations.return_value = mock_response

    result = orchestrator.fetch_wms_data()
    assert result.is_success
    wms_api_mock.get_allocations.assert_called_once()
```

---

## 📊 Testing Metrics & Reporting

### **Coverage Reporting**

```bash
# Generate coverage reports
make coverage-html          # HTML report in htmlcov/
make coverage-xml          # XML report for CI/CD integration

# Coverage thresholds by directory
PYTHONPATH=src pytest --cov=src/gruponos_meltano_native \
                     --cov-report=term-missing \
                     --cov-fail-under=90
```

### **Test Result Analysis**

**Key Metrics to Track**:
- Test execution time trends
- Coverage percentage trends
- Failure rates by category
- Performance benchmark results
- Flaky test identification

---

## 🎯 Testing Roadmap

### **Phase 1: Critical Fixes (Immediate)**
- [ ] Fix flext-meltano import issues
- [ ] Implement conftest.py with basic fixtures
- [ ] Validate test execution works
- [ ] Establish 90% coverage baseline

### **Phase 2: Infrastructure Enhancement (Week 2)**
- [ ] Complete conftest.py with all fixtures
- [ ] Setup test database infrastructure
- [ ] Implement comprehensive mocking
- [ ] Add integration test fixtures

### **Phase 3: Test Expansion (Week 3)**
- [ ] Add missing integration tests
- [ ] Implement performance testing
- [ ] Add security testing
- [ ] Complete end-to-end test coverage

### **Phase 4: Automation & Monitoring (Week 4)**
- [ ] Implement CI/CD testing pipeline
- [ ] Add automated coverage reporting
- [ ] Setup test result monitoring
- [ ] Implement flaky test detection

---

## ✅ Testing Completion Checklist

### **Infrastructure Completion**
- [ ] conftest.py implemented with comprehensive fixtures
- [ ] Test database infrastructure operational
- [ ] CI/CD testing pipeline configured
- [ ] Coverage reporting automated

### **Test Coverage Completion**
- [ ] 90%+ overall coverage achieved
- [ ] All critical path code covered
- [ ] Integration tests for all major workflows
- [ ] Performance and load testing implemented

### **Process Completion**
- [ ] Automated testing procedures documented
- [ ] Code review includes test validation
- [ ] Testing standards established and followed
- [ ] Test maintenance procedures in place

---

**Testing Status**: ❌ **BLOCKED** - Critical import failures prevent all test execution. Resolution of flext-meltano dependency issues required before testing infrastructure can be validated or enhanced.