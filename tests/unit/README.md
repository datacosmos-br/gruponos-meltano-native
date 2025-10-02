# Unit Tests

**Fast, Isolated Component Testing for GrupoNOS Meltano Native**

This directory contains comprehensive unit tests for all application components, designed for fast execution with isolated testing of business logic, error handling, and edge cases using mocked dependencies.

## Test Organization

### Core Application Components

#### `test_cli.py` - Command-Line Interface Testing

- **Coverage**: All CLI commands, options, and interactive features
- **Scenarios**: Success paths, error handling, user input validation
- **Mocking**: External system calls, user interactions, file operations
- **Performance**: CLI responsiveness and output formatting

#### `test_config.py` - Configuration Management Testing

- **Coverage**: Pydantic model validation, environment variable loading
- **Scenarios**: Valid/invalid configurations, environment-specific settings
- **Validation**: Business rule validation, type checking, constraint enforcement
- **Security**: Credential handling, sensitive field exclusion

#### `test_orchestrator.py` - ETL Orchestration Testing

- **Coverage**: Pipeline orchestration, workflow coordination, error propagation
- **Scenarios**: Full sync, incremental sync, error recovery, monitoring integration
- **Patterns**: Railway-oriented programming validation, FlextResult chains
- **Business Logic**: ETL workflow rules, data processing coordination

#### `test_exceptions.py` - Exception Hierarchy Testing

- **Coverage**: Complete exception inheritance tree, context handling
- **Scenarios**: Exception creation, inheritance validation, context enrichment
- **Integration**: Error propagation through pipeline layers
- **Standards**: FLEXT exception pattern compliance

### Specialized Component Testing

#### `test_alert_manager_comprehensive.py` - Alert Management Testing

- **Coverage**: Multi-channel delivery, severity routing, rate limiting
- **Channels**: Email, Slack, webhook delivery testing
- **Features**: Template rendering, retry logic, failure handling
- **Performance**: Alert delivery performance, batch processing

#### `test_data_validator.py` - Data Validation Testing

- **Coverage**: Multi-layer validation, business rule enforcement
- **Layers**: Schema, business rules, data quality, referential integrity
- **Performance**: Large dataset validation, batch processing optimization
- **Quality**: Data quality metrics, threshold validation

#### `test_oracle_connections.py` - Oracle Integration Testing

- **Coverage**: Connection management, pooling, health monitoring
- **Features**: Connection lifecycle, transaction handling, query optimization
- **Error Handling**: Connection failures, retry mechanisms, failover
- **Performance**: Connection pool efficiency, query performance

### Integration-Focused Unit Tests

#### `test_flext_integration.py` - FLEXT Framework Integration

- **Coverage**: FLEXT core pattern usage, container integration
- **Patterns**: FlextResult usage, dependency injection, error handling
- **Standards**: FLEXT naming conventions, configuration patterns
- **Integration**: Cross-component FLEXT pattern consistency

## Testing Patterns

### Railway-Oriented Testing

```python
def test_successful_pipeline_execution():
    """Test successful ETL pipeline with railway-oriented pattern."""
    # Arrange
    mock_data = TestDataFactory.create_batch_allocations(10)
    orchestrator = create_test_orchestrator()

    # Act
    result = orchestrator.execute_full_sync("GNOS", "DC01")

    # Assert
    assert result.success
    assert result.data.records_processed == 10
    assert result.data.duration_seconds > 0

def test_pipeline_error_propagation():
    """Test error propagation through pipeline chain."""
    # Arrange
    orchestrator = create_test_orchestrator()
    mock_validator_failure()  # Mock validation failure

    # Act
    result = orchestrator.execute_full_sync("GNOS", "DC01")

    # Assert
    assert result.is_failure
    assert "validation" in result.error.lower()
```

### Mock-Based Testing

```python
@patch('gruponos_meltano_native.oracle.connection_manager_enhanced.FlextDbOracleApi')
def test_oracle_connection_with_mock(mock_oracle_api):
    """Test Oracle connection management with controlled mocks."""
    # Arrange
    mock_connection = Mock()
    mock_oracle_api.return_value.get_connection.return_value = FlextResult[None].ok(mock_connection)

    config = create_test_oracle_config()
    manager = create_gruponos_meltano_oracle_connection_manager(config)

    # Act
    result = manager.get_connection()

    # Assert
    assert result.success
    assert result.data == mock_connection
    mock_oracle_api.assert_called_once()
```

### Configuration Testing

```python
def test_valid_configuration_loading():
    """Test loading of valid configuration from environment."""
    # Arrange
    test_env = {
        "GRUPONOS_ORACLE_WMS_BASE_URL": "https://test-wms.company.com",
        "GRUPONOS_ORACLE_WMS_USERNAME": "test_user",
        "GRUPONOS_ORACLE_WMS_PASSWORD": "test_password",
        "GRUPONOS_ORACLE_TARGET_HOST": "test-db.company.com"
    }

    with patch.dict(os.environ, test_env):
        # Act
        settings = GruponosMeltanoSettings()

        # Assert
        assert settings.oracle_wms.base_url == "https://test-wms.company.com"
        assert settings.oracle_wms.username == "test_user"
        assert settings.oracle_target.host == "test-db.company.com"

def test_invalid_configuration_validation():
    """Test validation of invalid configuration values."""
    # Arrange & Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        GruponosMeltanoOracleConnectionConfig(
            host="",  # Invalid: empty host
            service_name="TEST",
            username="test",
            password="test"
        )

    assert "host" in str(exc_info.value)
```

### Exception Testing

```python
def test_exception_hierarchy():
    """Test complete exception inheritance hierarchy."""
    # Test base exception
    base_error = GruponosMeltanoError("Base error")
    assert isinstance(base_error, Exception)
    assert str(base_error) == "Base error"

    # Test derived exceptions
    oracle_error = GruponosMeltanoOracleConnectionError("Connection failed")
    assert isinstance(oracle_error, GruponosMeltanoError)
    assert isinstance(oracle_error, GruponosMeltanoOracleError)

    # Test context handling
    pipeline_error = GruponosMeltanoPipelineError(
        "Pipeline failed",
        context={"company_code": "GNOS", "facility_code": "DC01"}
    )
    assert pipeline_error.context["company_code"] == "GNOS"
    assert "GNOS" in str(pipeline_error)
```

### Data Validation Testing

```python
def test_schema_validation_success():
    """Test successful schema validation."""
    # Arrange
    validator = create_test_validator()
    valid_data = [
        {
            "allocation_id": "A001",
            "item_code": "ITEM001",
            "quantity": 100,
            "facility_code": "DC01",
            "location": "A1-B2-C3"
        }
    ]

    # Act
    result = validator.validate_schema(valid_data)

    # Assert
    assert result.success
    assert len(result.data) == 1
    assert result.data[0]["allocation_id"] == "A001"

def test_business_rule_validation_failure():
    """Test business rule validation failure scenarios."""
    # Arrange
    validator = create_test_validator()
    invalid_data = [
        {
            "allocation_id": "A001",
            "item_code": "ITEM001",
            "quantity": -10,  # Invalid: negative quantity
            "facility_code": "DC01",
            "location": "A1-B2-C3"
        }
    ]

    # Act
    result = validator.validate_business_rules(invalid_data)

    # Assert
    assert result.is_failure
    assert "quantity" in result.error.lower()
    assert "negative" in result.error.lower()
```

### Alert Testing

```python
def test_alert_delivery_success():
    """Test successful alert delivery to multiple channels."""
    # Arrange
    mock_email_sender = Mock()
    mock_slack_sender = Mock()
    alert_manager = create_test_alert_manager(
        email_sender=mock_email_sender,
        slack_sender=mock_slack_sender
    )

    # Act
    result = alert_manager.send_alert(
        title="Test Alert",
        message="This is a test alert",
        severity=GruponosMeltanoAlertSeverity.INFO
    )

    # Assert
    assert result.success
    mock_email_sender.send.assert_called_once()
    mock_slack_sender.send.assert_called_once()

def test_alert_rate_limiting():
    """Test alert rate limiting functionality."""
    # Arrange
    alert_manager = create_test_alert_manager(
        rate_limit_window_minutes=1,
        max_alerts_per_window=2
    )

    # Act - Send 3 alerts within rate limit window
    result1 = alert_manager.send_alert("Alert 1", "Message 1")
    result2 = alert_manager.send_alert("Alert 2", "Message 2")
    result3 = alert_manager.send_alert("Alert 3", "Message 3")

    # Assert
    assert result1.success
    assert result2.success
    assert result3.is_failure  # Should be rate limited
    assert "rate limit" in result3.error.lower()
```

## Test Utilities

### Mock Factories

```python
class MockFactory:
    @staticmethod
    def create_mock_oracle_connection():
        """Create mock Oracle connection for testing."""
        mock_conn = Mock()
        mock_conn.execute.return_value = Mock()
        mock_conn.fetchall.return_value = []
        return mock_conn

    @staticmethod
    def create_mock_alert_manager():
        """Create mock alert manager for testing."""
        mock_manager = Mock()
        mock_manager.send_alert.return_value = FlextResult[None].ok("Alert sent")
        return mock_manager

    @staticmethod
    def create_mock_validator():
        """Create mock data validator for testing."""
        mock_validator = Mock()
        mock_validator.validate_allocation_data.return_value = FlextResult[None].ok([])
        return mock_validator
```

### Test Data Generators

```python
class TestDataGenerator:
    @staticmethod
    def generate_allocation_batch(count=10, **overrides):
        """Generate batch of allocation test data."""
        return [
            {
                "allocation_id": f"TEST{i:04d}",
                "item_code": f"ITEM{i:03d}",
                "quantity": random.randint(1, 1000),
                "facility_code": "DC01",
                "location": f"A{i % 10}-B{i % 10}-C{i % 10}",
                **overrides
            }
            for i in range(count)
        ]

    @staticmethod
    def generate_invalid_allocation(**invalid_fields):
        """Generate invalid allocation for error testing."""
        base_allocation = {
            "allocation_id": "TEST001",
            "item_code": "ITEM001",
            "quantity": 100,
            "facility_code": "DC01",
            "location": "A1-B2-C3"
        }
        base_allocation.update(invalid_fields)
        return base_allocation
```

## Execution Guidelines

### Running Unit Tests

```bash
# Run all unit tests
pytest tests/unit/ -v

# Run specific test file
pytest tests/unit/test_orchestrator.py -v

# Run with coverage
pytest tests/unit/ --cov=src/gruponos_meltano_native --cov-report=html

# Run fast tests only
pytest tests/unit/ -m "not slow" -v

# Run specific test pattern
pytest tests/unit/ -k "test_config" -v
```

### Performance Requirements

- **Individual Test Speed**: < 1 second per test
- **Total Suite Speed**: < 2 minutes for all unit tests
- **Coverage Requirement**: > 90% line coverage
- **Success Rate**: 100% pass rate required for CI/CD

### Development Guidelines

#### Test Writing Standards

1. **Fast Execution**: Keep tests under 1 second each
2. **Isolated**: No dependencies between tests
3. **Descriptive**: Clear test names describing the scenario
4. **Comprehensive**: Cover success, failure, and edge cases
5. **Maintainable**: Easy to understand and modify

#### Mock Usage Best Practices

1. **External Only**: Mock external dependencies, not business logic
2. **Realistic**: Use realistic mock data and behavior
3. **Verification**: Verify interactions with mocks
4. **Cleanup**: Proper mock cleanup between tests
5. **Consistency**: Consistent mocking patterns across tests

---

**Purpose**: Fast, isolated component testing  
**Coverage**: > 90% with comprehensive business logic validation  
**Speed**: < 2 minutes total execution for rapid feedback  
**Standards**: Enterprise testing with FLEXT pattern compliance
