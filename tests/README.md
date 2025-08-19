# Test Suite Documentation

**Comprehensive Testing Framework for GrupoNOS Meltano Native**

This directory contains the complete test suite for the GrupoNOS Meltano Native ETL pipeline, implementing enterprise testing standards with 90% minimum coverage requirements and comprehensive validation across unit, integration, and end-to-end testing scenarios.

## Test Structure

```
tests/
├── __init__.py                                    # Test package initialization
├── conftest.py                                    # Shared test configuration and fixtures
├── unit/                                         # Unit tests (fast, isolated)
│   ├── __init__.py                              # Unit test package
│   ├── test_cli.py                              # CLI functionality tests
│   ├── test_config.py                           # Configuration management tests
│   ├── test_exceptions.py                       # Exception hierarchy tests
│   ├── test_orchestrator.py                    # Orchestrator business logic tests
│   ├── test_data_validator.py                  # Data validation tests
│   ├── test_alert_manager_comprehensive.py      # Alert management tests
│   ├── test_oracle_connections.py              # Oracle connection tests
│   └── [additional unit test files]            # Component-specific unit tests
├── integration/                                  # Integration tests (real systems)
│   ├── __init__.py                              # Integration test package
│   ├── test_end_to_end_oracle_integration.py   # Complete Oracle integration
│   └── test_performance_and_load.py            # Performance and load testing
└── [additional test files]                      # Feature-specific tests
```

## Testing Standards

### Coverage Requirements

- **Minimum Coverage**: 90% across all modules
- **Branch Coverage**: Comprehensive branch coverage for business logic
- **Integration Coverage**: Real system integration validation
- **Performance Coverage**: Load testing under enterprise conditions

### Test Categories

#### Unit Tests (`unit/`)

- **Scope**: Individual components in isolation
- **Speed**: Fast execution (< 1 second per test)
- **Dependencies**: Mocked external dependencies
- **Coverage**: Business logic, error handling, edge cases

#### Integration Tests (`integration/`)

- **Scope**: Real system integration with databases and external APIs
- **Speed**: Moderate execution (< 30 seconds per test)
- **Dependencies**: Real Oracle databases, test environments
- **Coverage**: End-to-end workflows, system integration

#### End-to-End Tests

- **Scope**: Complete pipeline execution from source to target
- **Speed**: Slower execution (< 5 minutes per test)
- **Dependencies**: Full system stack with real data
- **Coverage**: Complete business workflows, user scenarios

## Test Execution

### Standard Test Commands

```bash
# Run all tests with coverage
make test

# Run unit tests only (fast feedback)
make test-unit
pytest tests/unit/ -v

# Run integration tests only
make test-integration
pytest tests/integration/ -v

# Run specific test markers
pytest -m "not slow" -v              # Exclude slow tests
pytest -m "unit" -v                  # Unit tests only
pytest -m "integration" -v           # Integration tests only
pytest -m "oracle" -v                # Oracle-specific tests
pytest -m "wms" -v                   # WMS-specific tests

# Coverage reporting
pytest --cov=src/gruponos_meltano_native --cov-report=html --cov-report=term
```

### Test Markers

```python
# Available test markers
@pytest.mark.unit          # Fast unit tests
@pytest.mark.integration   # Integration tests with real systems
@pytest.mark.slow          # Tests that take > 10 seconds
@pytest.mark.oracle        # Oracle database specific tests
@pytest.mark.wms           # WMS integration specific tests
@pytest.mark.e2e           # End-to-end pipeline tests
@pytest.mark.performance   # Performance and load tests
@pytest.mark.smoke         # Smoke tests for basic functionality
```

## Key Test Components

### `conftest.py` - Shared Test Configuration

Centralized test configuration with reusable fixtures for consistent testing.

#### Key Fixtures

- **`mock_settings`**: Mock application settings for controlled testing
- **`mock_oracle_connection`**: Mock Oracle database connections
- **`test_data_fixtures`**: Standardized test data for validation
- **`mock_alert_manager`**: Mock alert system for notification testing

### Unit Test Categories

#### Configuration Testing (`test_config.py`)

- **Settings Validation**: Environment-specific configuration validation
- **Business Rule Validation**: Configuration business rule enforcement
- **Error Handling**: Configuration error scenarios and recovery
- **Environment Loading**: Multi-environment configuration testing

#### CLI Testing (`test_cli.py`)

- **Command Execution**: All CLI commands with various parameters
- **Error Handling**: CLI error scenarios and user feedback
- **Interactive Mode**: User interaction and input validation
- **Output Formatting**: CLI output formatting and presentation

#### Orchestrator Testing (`test_orchestrator.py`)

- **Pipeline Execution**: Full and incremental sync workflows
- **Error Propagation**: Railway-oriented error handling validation
- **Business Logic**: ETL orchestration business rules
- **Performance**: Pipeline performance and optimization

#### Exception Testing (`test_exceptions.py`)

- **Exception Hierarchy**: Complete exception inheritance validation
- **Context Handling**: Rich exception context and error information
- **Error Propagation**: Exception propagation through pipeline layers
- **Recovery Scenarios**: Error recovery and retry mechanisms

#### Data Validation Testing (`test_data_validator.py`)

- **Schema Validation**: Data structure and type validation
- **Business Rules**: WMS-specific business rule enforcement
- **Data Quality**: Quality metrics and threshold validation
- **Performance**: Large dataset validation performance

#### Alert Management Testing (`test_alert_manager_comprehensive.py`)

- **Multi-Channel Delivery**: Email, Slack, webhook delivery testing
- **Severity Routing**: Alert routing based on severity levels
- **Rate Limiting**: Alert rate limiting and flood prevention
- **Template Rendering**: Alert template customization and rendering

#### Oracle Integration Testing (`test_oracle_connections.py`)

- **Connection Management**: Connection pooling and lifecycle management
- **Query Optimization**: Oracle-specific query optimization validation
- **Transaction Handling**: Transaction management and rollback scenarios
- **Health Monitoring**: Connection health monitoring and recovery

### Integration Test Categories

#### End-to-End Oracle Integration (`test_end_to_end_oracle_integration.py`)

- **Complete Pipeline**: Full ETL pipeline with real Oracle systems
- **Data Validation**: End-to-end data integrity validation
- **Performance**: Real-world performance under load
- **Error Recovery**: System failure and recovery scenarios

#### Performance and Load Testing (`test_performance_and_load.py`)

- **Scalability**: System behavior under increasing load
- **Resource Usage**: Memory and connection usage monitoring
- **Throughput**: Data processing throughput validation
- **Stress Testing**: System limits and failure points

## Test Data Management

### Test Data Fixtures

```python
# Standard test data patterns
@pytest.fixture
def valid_allocation_data():
    return [
        {
            "allocation_id": "TEST001",
            "item_code": "ITEM001",
            "quantity": 100,
            "facility_code": "DC01",
            "location": "A1-B2-C3",
            "mod_ts": datetime.utcnow()
        }
        # ... additional test records
    ]

@pytest.fixture
def invalid_allocation_data():
    return [
        {
            "allocation_id": "",  # Invalid: empty ID
            "quantity": -10,      # Invalid: negative quantity
            "facility_code": "INVALID"  # Invalid: bad facility
        }
    ]
```

### Mock Data Factories

```python
class TestDataFactory:
    @staticmethod
    def create_wms_allocation(**overrides):
        """Create valid WMS allocation test data."""
        default_data = {
            "allocation_id": f"TEST{random.randint(1000, 9999)}",
            "item_code": f"ITEM{random.randint(100, 999)}",
            "quantity": random.randint(1, 1000),
            "facility_code": "DC01",
            "location": "A1-B2-C3"
        }
        default_data.update(overrides)
        return default_data

    @staticmethod
    def create_batch_allocations(count=10, **overrides):
        """Create batch of allocation test data."""
        return [
            TestDataFactory.create_wms_allocation(**overrides)
            for _ in range(count)
        ]
```

## Testing Patterns

### Railway-Oriented Testing

```python
def test_etl_pipeline_success_path():
    """Test successful ETL pipeline execution."""
    # Given: Valid input data
    test_data = TestDataFactory.create_batch_allocations(100)

    # When: Execute pipeline
    result = await orchestrator.execute_full_sync("GNOS", "DC01")

    # Then: Verify success:
    assert result.success
    assert result.data.records_processed == 100
    assert result.data.errors_count == 0

def test_etl_pipeline_failure_propagation():
    """Test error propagation through pipeline."""
    # Given: Invalid input data
    test_data = [{"invalid": "data"}]

    # When: Execute pipeline
    result = await orchestrator.execute_full_sync("GNOS", "DC01")

    # Then: Verify failure
    assert result.is_failure
    assert "validation" in result.error.lower()
```

### Mock Integration Testing

```python
@patch('gruponos_meltano_native.oracle.connection_manager_enhanced.FlextDbOracleApi')
def test_oracle_integration_with_mocks(mock_oracle_api):
    """Test Oracle integration with controlled mocks."""
    # Setup mock behavior
    mock_connection = Mock()
    mock_oracle_api.return_value.get_connection.return_value = FlextResult[None].ok(mock_connection)

    # Execute test
    manager = create_gruponos_meltano_oracle_connection_manager(test_config)
    result = await manager.get_connection()

    # Verify behavior
    assert result.success
    mock_oracle_api.assert_called_once()
```

### Performance Testing Patterns

```python
@pytest.mark.performance
async def test_large_dataset_processing():
    """Test processing of large datasets."""
    # Given: Large test dataset
    large_dataset = TestDataFactory.create_batch_allocations(10000)

    # When: Process with time measurement
    start_time = time.time()
    result = await validator.validate_allocation_data(large_dataset)
    processing_time = time.time() - start_time

    # Then: Verify performance requirements
    assert result.success
    assert processing_time < 30  # Max 30 seconds for 10k records
    assert len(result.data) == 10000
```

## Continuous Integration

### Test Automation

```yaml
# GitHub Actions test workflow
name: Test Suite
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.13

      - name: Install dependencies
        run: |
          pip install poetry
          poetry install

      - name: Run unit tests
        run: poetry run pytest tests/unit/ --cov=src --cov-fail-under=90

      - name: Run integration tests
        run: poetry run pytest tests/integration/ -v
        env:
          TEST_ORACLE_HOST: ${{ secrets.TEST_ORACLE_HOST }}
          TEST_ORACLE_PASSWORD: ${{ secrets.TEST_ORACLE_PASSWORD }}
```

### Quality Gates

```bash
# Quality gate validation
poetry run pytest --cov=src/gruponos_meltano_native --cov-fail-under=90 --maxfail=1
poetry run mypy src/gruponos_meltano_native --strict
poetry run ruff check src/ tests/
poetry run bandit -r src/
```

## Development Guidelines

### Test Development Standards

1. **Arrange-Act-Assert**: Clear test structure with AAA pattern
2. **Single Responsibility**: Each test validates one specific behavior
3. **Descriptive Names**: Test names clearly describe the scenario
4. **FLEXT Patterns**: Use FLEXT testing utilities and patterns
5. **Coverage**: Aim for 95%+ coverage with meaningful tests

### Mock Usage Guidelines

1. **External Dependencies**: Mock all external system dependencies
2. **Consistent Behavior**: Predictable mock behavior across tests
3. **Verification**: Verify interactions with mocked dependencies
4. **Realistic Data**: Use realistic test data and scenarios
5. **Error Scenarios**: Test both success and failure paths

---

**Coverage**: 90% minimum with comprehensive validation  
**Standards**: Enterprise testing with FLEXT patterns  
**Performance**: Load testing under realistic conditions  
**Integration**: Real system validation with mocked dependencies
