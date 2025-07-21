# Integration Tests for GrupoNOS Meltano Native

This directory contains comprehensive integration tests that test real Oracle database connections and end-to-end WMS functionality.

## Overview

The integration tests are designed to validate:

- **Real Oracle Database Connections** - Test actual Oracle connectivity, authentication, and query execution
- **WMS Schema Discovery** - Test discovery and mapping of real WMS table schemas
- **Table Creation and Synchronization** - Test DDL generation and execution against Oracle databases
- **Data Validation Workflows** - Test data validation and conversion with real WMS data patterns
- **Alert and Monitoring Systems** - Test webhook alerts and system resource monitoring
- **Performance and Load Testing** - Test connection pooling, concurrent operations, and large dataset processing
- **Complete Pipeline Workflows** - Test end-to-end sync simulation with real components

## Test Files

### `test_end_to_end_oracle_integration.py`
Main integration tests covering:
- Oracle connection management and resilience
- WMS schema discovery and data sampling
- Table creation and sync operations  
- Data validation with realistic WMS patterns
- Alerting and monitoring integration
- Full pipeline workflow simulation

### `test_performance_and_load.py`
Performance-focused tests covering:
- Connection establishment performance
- Concurrent connection handling
- Connection pool stress testing
- Large dataset validation performance
- Memory usage monitoring
- DDL generation performance for complex schemas

## Prerequisites

### Required Environment Variables

#### Oracle Target Database (Required)
```bash
export FLEXT_TARGET_ORACLE_HOST="your-target-oracle-host"
export FLEXT_TARGET_ORACLE_PORT="1522"  # Optional, defaults to 1522
export FLEXT_TARGET_ORACLE_SERVICE_NAME="your-service-name"
export FLEXT_TARGET_ORACLE_USERNAME="your-username"
export FLEXT_TARGET_ORACLE_PASSWORD="your-password"
export FLEXT_TARGET_ORACLE_PROTOCOL="tcps"  # Optional, defaults to tcps
```

#### WMS Source Database (Optional - for WMS-specific tests)
```bash
export TAP_ORACLE_WMS_HOST="your-wms-oracle-host"
export TAP_ORACLE_WMS_PORT="1521"  # Optional, defaults to 1521
export TAP_ORACLE_WMS_SERVICE_NAME="your-wms-service"
export TAP_ORACLE_WMS_USERNAME="your-wms-username"
export TAP_ORACLE_WMS_PASSWORD="your-wms-password"
```

#### Test Control Variables
```bash
# Enable destructive tests (table drops/recreates)
export ALLOW_DESTRUCTIVE_TESTS="true"

# Enable full end-to-end workflow tests
export FULL_E2E_TESTS="true"
```

### Required Python Packages
```bash
pip install requests psutil
```

### Database Permissions
The test user needs the following Oracle permissions:
- `CREATE TABLE`, `DROP TABLE` - For table creation tests
- `SELECT` on `V$VERSION`, `USER_TABLES`, `USER_TAB_COLUMNS`, `USER_TABLESPACES` - For discovery tests
- `INSERT`, `UPDATE`, `DELETE` - For data manipulation tests (if enabled)

## Running Tests

### Run All Integration Tests
```bash
# From project root
pytest tests/integration/ -v -m integration

# With specific markers
pytest tests/integration/ -v -m "integration and not destructive"
```

### Run Specific Test Categories

#### Basic Oracle Connection Tests
```bash
pytest tests/integration/test_end_to_end_oracle_integration.py::TestOracleConnectionIntegration -v
```

#### WMS-Specific Tests (requires WMS environment)
```bash
pytest tests/integration/ -v -m wms
```

#### Performance Tests
```bash
pytest tests/integration/test_performance_and_load.py -v -m performance
```

#### Full End-to-End Tests
```bash
FULL_E2E_TESTS=true pytest tests/integration/ -v -m e2e
```

#### Destructive Tests (use with caution)
```bash
ALLOW_DESTRUCTIVE_TESTS=true pytest tests/integration/ -v -m destructive
```

### Run Tests with Coverage
```bash
pytest tests/integration/ -v --cov=gruponos_meltano_native --cov-report=html
```

## Test Markers

The integration tests use pytest markers for organization:

- `@pytest.mark.integration` - All integration tests
- `@pytest.mark.slow` - Tests that take longer to execute
- `@pytest.mark.wms` - Tests requiring WMS database connection
- `@pytest.mark.performance` - Performance and load tests
- `@pytest.mark.memory` - Memory usage tests
- `@pytest.mark.destructive` - Tests that modify/drop database objects
- `@pytest.mark.e2e` - Full end-to-end workflow tests

## Test Environment Setup

### Local Development
```bash
# Set up test environment
export FLEXT_TARGET_ORACLE_HOST="localhost"
export FLEXT_TARGET_ORACLE_SERVICE_NAME="XEPDB1"
export FLEXT_TARGET_ORACLE_USERNAME="testuser"
export FLEXT_TARGET_ORACLE_PASSWORD="testpass"

# Run integration tests
pytest tests/integration/ -v -m integration
```

### CI/CD Environment
```yaml
# Example GitHub Actions configuration
env:
  FLEXT_TARGET_ORACLE_HOST: ${{ secrets.ORACLE_HOST }}
  FLEXT_TARGET_ORACLE_USERNAME: ${{ secrets.ORACLE_USER }}
  FLEXT_TARGET_ORACLE_PASSWORD: ${{ secrets.ORACLE_PASS }}
  FLEXT_TARGET_ORACLE_SERVICE_NAME: "TESTDB"
  
steps:
  - name: Install dependencies
    run: pip install requests psutil
    
  - name: Run integration tests
    run: pytest tests/integration/ -v -m "integration and not destructive"
```

## Expected Test Results

### Successful Test Run
- Oracle connections establish within performance thresholds
- Schema discovery finds expected table structures
- DDL generation produces valid Oracle syntax
- Data validation handles realistic WMS data patterns
- Alert systems successfully deliver notifications
- Performance metrics meet established benchmarks

### Common Test Failures and Solutions

#### Connection Failures
- **Issue**: `pytest.skip("Missing required environment variables")`
- **Solution**: Set required environment variables listed above

#### Permission Errors
- **Issue**: `ORA-00942: table or view does not exist`
- **Solution**: Grant necessary SELECT permissions to test user

#### Performance Test Failures
- **Issue**: Performance metrics below thresholds
- **Solution**: Review database configuration, network latency, and system resources

#### WMS Test Skips
- **Issue**: `pytest.skip("WMS connection not configured")`
- **Solution**: This is expected if WMS environment variables are not set

## Writing Custom Integration Tests

### Test Structure
```python
import pytest
from gruponos_meltano_native.config import OracleConnectionConfig
from gruponos_meltano_native.oracle.connection_manager_enhanced import OracleConnectionManager

class TestCustomIntegration:
    @pytest.fixture
    def oracle_config(self) -> OracleConnectionConfig:
        # Skip if environment not configured
        required_vars = ["FLEXT_TARGET_ORACLE_HOST", ...]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            pytest.skip(f"Missing variables: {missing_vars}")
        
        return OracleConnectionConfig(...)
    
    @pytest.mark.integration
    def test_custom_functionality(self, oracle_config: OracleConnectionConfig) -> None:
        # Test implementation
        pass
```

### Best Practices
1. **Always clean up resources** - Use try/finally blocks for connections
2. **Skip gracefully** - Use pytest.skip() when environment is not configured
3. **Use appropriate markers** - Mark tests with relevant pytest markers
4. **Handle permissions** - Test may fail if database permissions are insufficient
5. **Verify real behavior** - Integration tests should test actual system behavior, not mocks

## Troubleshooting

### Oracle Connection Issues
- Verify Oracle client is installed and configured
- Check network connectivity to Oracle host
- Verify credentials and service name
- Check Oracle listener status

### Test Performance Issues
- Reduce dataset sizes for local testing
- Skip performance tests in constrained environments
- Check system resources (memory, CPU)

### Environment Setup Issues
- Verify all required environment variables are set
- Check Python package dependencies
- Ensure Oracle permissions are correctly configured

## Contributing

When adding new integration tests:

1. Follow the existing test structure and patterns
2. Use appropriate pytest markers
3. Include proper environment variable checking
4. Add documentation for any new requirements
5. Test both success and failure scenarios
6. Clean up any resources created during testing

## Security Considerations

- Never commit database credentials to version control
- Use environment variables or secure credential management
- Limit database permissions to minimum required for testing
- Be cautious with destructive tests in shared environments
- Consider using test-specific database schemas/users