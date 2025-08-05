# Integration Tests

**Real System Integration Testing for GrupoNOS Meltano Native**

This directory contains comprehensive integration tests that validate end-to-end system integration with real Oracle databases, external APIs, and complete ETL pipeline workflows under realistic conditions.

## Test Organization

### Core Integration Tests

#### `test_end_to_end_oracle_integration.py` - Complete Oracle Integration

- **Scope**: Full ETL pipeline with real Oracle WMS and target databases
- **Coverage**: Data extraction, transformation, validation, and loading
- **Scenarios**: Full sync, incremental sync, error recovery, data consistency
- **Dependencies**: Real Oracle WMS API, Oracle target database, test schemas

#### `test_performance_and_load.py` - Performance and Load Testing

- **Scope**: System performance under realistic and stress conditions
- **Coverage**: Large dataset processing, concurrent operations, resource usage
- **Metrics**: Throughput, latency, memory usage, connection pool efficiency
- **Scenarios**: Normal load, peak load, stress testing, resource limits

## Integration Test Categories

### Database Integration

- **Oracle WMS Connectivity**: Real WMS API integration with authentication
- **Target Database Operations**: Bulk operations, transaction management
- **Data Consistency**: Cross-system data consistency validation
- **Performance**: Query optimization, connection pooling efficiency

### ETL Pipeline Integration

- **Complete Workflows**: End-to-end pipeline execution with real data
- **Error Handling**: System failure and recovery scenarios
- **Monitoring Integration**: Alert delivery, performance metrics collection
- **Configuration**: Environment-specific configuration validation

### External System Integration

- **WMS API Integration**: Real Oracle WMS REST API operations
- **Database Connectivity**: Multi-database connection management
- **Alert Delivery**: Email, Slack, webhook delivery testing
- **Monitoring Systems**: Metrics collection and health check integration

## Test Scenarios

### End-to-End Oracle Integration

#### Full Synchronization Testing

```python
@pytest.mark.integration
@pytest.mark.oracle
async def test_complete_full_sync_workflow():
    """Test complete full synchronization workflow with real systems."""
    # Arrange
    orchestrator = create_integration_orchestrator()
    company_code = "TEST_GNOS"
    facility_code = "TEST_DC01"

    # Act
    result = await orchestrator.execute_full_sync(company_code, facility_code)

    # Assert
    assert result.success
    assert result.data.records_processed > 0
    assert result.data.errors_count == 0
    assert result.data.duration_seconds > 0

    # Verify data consistency
    source_count = await get_wms_record_count(company_code, facility_code)
    target_count = await get_target_db_record_count()
    assert source_count == target_count

@pytest.mark.integration
@pytest.mark.oracle
async def test_incremental_sync_workflow():
    """Test incremental synchronization with real timestamp tracking."""
    # Arrange
    orchestrator = create_integration_orchestrator()
    last_sync_timestamp = await get_last_sync_timestamp()

    # Act
    result = await orchestrator.execute_incremental_sync("TEST_GNOS", "TEST_DC01")

    # Assert
    assert result.success

    # Verify only new/modified records were processed
    processed_records = result.data.records_processed
    expected_new_records = await get_modified_records_count_since(last_sync_timestamp)
    assert processed_records == expected_new_records
```

#### Data Consistency Validation

```python
@pytest.mark.integration
@pytest.mark.oracle
async def test_data_consistency_across_systems():
    """Test data consistency between WMS and target database."""
    # Arrange
    test_allocation_id = "INTEGRATION_TEST_001"

    # Create test data in WMS
    await create_test_allocation_in_wms(test_allocation_id)

    # Act - Execute sync
    orchestrator = create_integration_orchestrator()
    result = await orchestrator.execute_full_sync("TEST_GNOS", "TEST_DC01")

    # Assert - Verify data consistency
    assert result.success

    wms_allocation = await get_allocation_from_wms(test_allocation_id)
    target_allocation = await get_allocation_from_target_db(test_allocation_id)

    assert wms_allocation.allocation_id == target_allocation.allocation_id
    assert wms_allocation.quantity == target_allocation.quantity
    assert wms_allocation.location == target_allocation.location

    # Cleanup
    await cleanup_test_allocation(test_allocation_id)
```

### Performance and Load Testing

#### Large Dataset Processing

```python
@pytest.mark.integration
@pytest.mark.performance
async def test_large_dataset_processing():
    """Test processing of large datasets under realistic conditions."""
    # Arrange
    large_dataset_size = 50000  # 50K records
    await create_large_test_dataset(large_dataset_size)

    orchestrator = create_integration_orchestrator()
    start_time = time.time()

    # Act
    result = await orchestrator.execute_full_sync("TEST_GNOS", "TEST_DC01")
    processing_time = time.time() - start_time

    # Assert
    assert result.success
    assert result.data.records_processed == large_dataset_size

    # Performance requirements
    assert processing_time < 300  # Max 5 minutes for 50K records

    # Throughput requirements
    throughput = large_dataset_size / processing_time
    assert throughput > 100  # Min 100 records/second

    # Memory usage validation
    memory_usage = await get_peak_memory_usage()
    assert memory_usage < 2048  # Max 2GB memory usage

    # Cleanup
    await cleanup_large_test_dataset()

@pytest.mark.integration
@pytest.mark.performance
async def test_concurrent_pipeline_execution():
    """Test concurrent pipeline execution performance."""
    # Arrange
    concurrent_pipelines = 5

    async def run_pipeline(pipeline_id):
        orchestrator = create_integration_orchestrator()
        return await orchestrator.execute_full_sync(f"TEST_{pipeline_id}", "TEST_DC01")

    # Act
    start_time = time.time()
    results = await asyncio.gather(*[
        run_pipeline(i) for i in range(concurrent_pipelines)
    ])
    total_time = time.time() - start_time

    # Assert
    assert all(result.success for result in results)

    # Verify concurrent execution efficiency
    expected_sequential_time = sum(result.data.duration_seconds for result in results)
    efficiency = expected_sequential_time / total_time
    assert efficiency > 2.0  # At least 2x improvement with concurrency
```

#### Resource Usage Monitoring

```python
@pytest.mark.integration
@pytest.mark.performance
async def test_resource_usage_monitoring():
    """Test system resource usage under load."""
    # Arrange
    resource_monitor = ResourceUsageMonitor()
    orchestrator = create_integration_orchestrator()

    # Act
    with resource_monitor.track_usage():
        result = await orchestrator.execute_full_sync("TEST_GNOS", "TEST_DC01")

    usage_report = resource_monitor.generate_report()

    # Assert
    assert result.success

    # Memory usage requirements
    assert usage_report.peak_memory_mb < 1024  # Max 1GB memory
    assert usage_report.memory_leak_detected == False

    # Connection pool efficiency
    assert usage_report.connection_pool_efficiency > 0.8  # 80% efficiency
    assert usage_report.connection_leaks == 0

    # CPU usage requirements
    assert usage_report.peak_cpu_percent < 80  # Max 80% CPU
```

### Error Recovery Testing

#### System Failure Scenarios

```python
@pytest.mark.integration
@pytest.mark.oracle
async def test_wms_connection_failure_recovery():
    """Test recovery from WMS connection failures."""
    # Arrange
    orchestrator = create_integration_orchestrator()

    # Simulate WMS connection failure
    with patch_wms_connection_failure():
        # Act
        result = await orchestrator.execute_full_sync("TEST_GNOS", "TEST_DC01")

        # Assert - Should handle failure gracefully
        assert result.is_failure
        assert "connection" in result.error.lower()

    # Recovery test - connection restored
    result = await orchestrator.execute_full_sync("TEST_GNOS", "TEST_DC01")
    assert result.success

@pytest.mark.integration
@pytest.mark.oracle
async def test_database_transaction_rollback():
    """Test database transaction rollback on errors."""
    # Arrange
    orchestrator = create_integration_orchestrator()
    initial_record_count = await get_target_db_record_count()

    # Simulate database error during load
    with patch_database_error_during_load():
        # Act
        result = await orchestrator.execute_full_sync("TEST_GNOS", "TEST_DC01")

        # Assert - Transaction should be rolled back
        assert result.is_failure

        # Verify no partial data was committed
        final_record_count = await get_target_db_record_count()
        assert final_record_count == initial_record_count
```

### Alert Integration Testing

#### Multi-Channel Alert Delivery

```python
@pytest.mark.integration
async def test_alert_delivery_integration():
    """Test alert delivery to real systems."""
    # Arrange
    alert_manager = create_integration_alert_manager()

    # Act
    result = await alert_manager.send_alert(
        title="Integration Test Alert",
        message="This is an integration test alert",
        severity=GruponosMeltanoAlertSeverity.INFO,
        context={"test_id": "INTEGRATION_001"}
    )

    # Assert
    assert result.success

    # Verify alert was delivered to configured channels
    # (This would check actual email, Slack, webhook delivery)
    assert await verify_email_delivery("Integration Test Alert")
    assert await verify_slack_delivery("Integration Test Alert")
```

## Test Environment Setup

### Database Setup

```python
@pytest.fixture(scope="session")
async def integration_test_database():
    """Setup integration test database schema."""
    # Create test schema
    await create_integration_test_schema()

    # Populate with test data
    await populate_test_data()

    yield

    # Cleanup
    await cleanup_integration_test_schema()

@pytest.fixture(scope="session")
async def wms_test_environment():
    """Setup WMS test environment."""
    # Configure WMS test instance
    wms_config = await setup_wms_test_instance()

    yield wms_config

    # Cleanup WMS test data
    await cleanup_wms_test_data()
```

### Configuration Management

```python
@pytest.fixture
def integration_test_config():
    """Provide integration test configuration."""
    return GruponosMeltanoSettings(
        environment="integration_test",
        oracle_wms=GruponosMeltanoWMSSourceConfig(
            base_url="https://wms-test.company.com/api/v1",
            username="integration_test_user",
            password="integration_test_password",
            company_code="TEST_GNOS",
            facility_code="TEST_DC01"
        ),
        oracle_target=GruponosMeltanoTargetOracleConfig(
            host="oracle-test.company.com",
            service_name="TESTDB",
            username="etl_integration_test",
            password="test_password",
            schema="INTEGRATION_TEST"
        )
    )
```

## Execution Guidelines

### Running Integration Tests

```bash
# Run all integration tests
pytest tests/integration/ -v

# Run specific integration test
pytest tests/integration/test_end_to_end_oracle_integration.py -v

# Run performance tests only
pytest tests/integration/ -m performance -v

# Run with extended timeout for slow tests
pytest tests/integration/ --timeout=300 -v

# Run with environment-specific configuration
TEST_ENVIRONMENT=integration pytest tests/integration/ -v
```

### Environment Requirements

```bash
# Required environment variables for integration tests
export TEST_ORACLE_WMS_HOST="wms-test.company.com"
export TEST_ORACLE_WMS_USERNAME="integration_test_user"
export TEST_ORACLE_WMS_PASSWORD="integration_test_password"
export TEST_ORACLE_TARGET_HOST="oracle-test.company.com"
export TEST_ORACLE_TARGET_USERNAME="etl_integration_test"
export TEST_ORACLE_TARGET_PASSWORD="test_password"

# Optional: Test data configuration
export TEST_COMPANY_CODE="TEST_GNOS"
export TEST_FACILITY_CODE="TEST_DC01"
export TEST_DATASET_SIZE="1000"
```

### Performance Benchmarks

- **Small Dataset (1K records)**: < 30 seconds
- **Medium Dataset (10K records)**: < 2 minutes
- **Large Dataset (50K records)**: < 5 minutes
- **Memory Usage**: < 2GB peak usage
- **Connection Pool**: > 80% efficiency
- **Throughput**: > 100 records/second

## Development Guidelines

### Integration Test Development

1. **Real Systems**: Use real databases and APIs, not mocks
2. **Data Cleanup**: Always clean up test data after execution
3. **Performance Aware**: Monitor resource usage and performance
4. **Environment Isolation**: Use dedicated test environments
5. **Comprehensive Coverage**: Test complete workflows and error scenarios

### Error Handling Testing

1. **Failure Scenarios**: Test all failure modes and recovery
2. **Transaction Integrity**: Verify transaction rollback on errors
3. **Resource Cleanup**: Ensure proper cleanup after failures
4. **Alert Integration**: Verify alert delivery for failures
5. **Monitoring Integration**: Test monitoring and metrics collection

---

**Purpose**: Real system integration validation  
**Coverage**: End-to-end workflows with real dependencies  
**Performance**: Load testing under enterprise conditions  
**Reliability**: System failure and recovery scenario validation
