"""Test configuration and shared fixtures for gruponos-meltano-native.

This conftest.py provides centralized test infrastructure including:
- Database fixtures and connections
- Meltano configuration fixtures
- Mock objects for external services
- Test data factories
- Environment variable management
- Cleanup and teardown procedures

Author: FLEXT Test Infrastructure Team
Version: 1.0.0
"""

import os
import tempfile
import uuid
from collections.abc import Generator
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
import pytest_asyncio
from flext_core import FlextContainer

from gruponos_meltano_native import (
    GruponosMeltanoNativeCli,
    GruponosMeltanoNativeConfig,
    GruponosMeltanoOrchestrator,
)

# Test configuration constants
TEST_DB_URL = "sqlite:///test_gruponos.db"
TEST_CONFIG_PATH = Path("test_config")
TEST_OUTPUT_DIR = Path("test_output")


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up global test environment before all tests."""
    # Create test directories
    TEST_CONFIG_PATH.mkdir(exist_ok=True)
    TEST_OUTPUT_DIR.mkdir(exist_ok=True)

    # Set test environment variables
    os.environ.setdefault("GRUPONOS_TESTING", "true")
    os.environ.setdefault("GRUPONOS_LOG_LEVEL", "DEBUG")

    yield

    # Cleanup after all tests
    import shutil

    if TEST_CONFIG_PATH.exists():
        shutil.rmtree(TEST_CONFIG_PATH)
    if TEST_OUTPUT_DIR.exists():
        shutil.rmtree(TEST_OUTPUT_DIR)


@pytest.fixture
def temp_dir() -> Generator[Path]:
    """Provide a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def test_config_file(temp_dir: Path) -> Path:
    """Create a test configuration file."""
    config_file = temp_dir / "test_config.yml"
    config_content = """
environment: test
debug: true
log_level: DEBUG

pipeline:
  batch_size: 100
  timeout: 300
  retries: 1

database:
  host: localhost
  port: 5432
  database: test_db
  ssl_mode: disable

oracle_wms:
  base_url: "https://test-wms.example.com"
  timeout: 30
  max_retries: 3

monitoring:
  enabled: false
"""
    config_file.write_text(config_content)
    return config_file


@pytest.fixture
def sample_wms_allocation() -> dict[str, Any]:
    """Provide a sample WMS allocation record."""
    return {
        "allocation_id": "ALLOC001",
        "item_code": "ITEM123",
        "location_code": "LOC001",
        "allocated_quantity": 100.0,
        "allocated_date": "2024-01-15T10:00:00Z",
        "warehouse_code": "WH001",
        "status": "ACTIVE",
        "mod_ts": "2024-01-15T10:00:00Z",
    }


@pytest.fixture
def sample_order_header() -> dict[str, Any]:
    """Provide a sample order header record."""
    return {
        "order_id": "ORD001",
        "order_number": "ORD-2024-001",
        "customer_id": "CUST001",
        "order_date": "2024-01-15",
        "status": "PROCESSING",
        "total_amount": 1500.50,
        "warehouse_code": "WH001",
        "mod_ts": "2024-01-15T10:00:00Z",
    }


@pytest.fixture
def sample_order_detail() -> dict[str, Any]:
    """Provide a sample order detail record."""
    return {
        "order_detail_id": "ORDDTL001",
        "order_id": "ORD001",
        "line_number": 1,
        "item_code": "ITEM123",
        "quantity_ordered": 10.0,
        "quantity_shipped": 10.0,
        "unit_price": 150.05,
        "discount_percent": 0.0,
        "warehouse_code": "WH001",
        "location_code": "LOC001",
        "mod_ts": "2024-01-15T10:00:00Z",
    }


@pytest.fixture
def mock_oracle_connection():
    """Mock Oracle database connection."""
    mock_conn = MagicMock()
    mock_conn.execute.return_value = []
    mock_conn.fetchone.return_value = None
    mock_conn.fetchall.return_value = []
    mock_conn.commit.return_value = None
    mock_conn.rollback.return_value = None
    mock_conn.close.return_value = None
    return mock_conn


@pytest.fixture
def mock_wms_api_response():
    """Mock WMS API response."""
    return {
        "data": [
            {
                "allocation_id": "ALLOC001",
                "item_code": "ITEM123",
                "location_code": "LOC001",
                "allocated_quantity": 100.0,
                "allocated_date": "2024-01-15T10:00:00Z",
                "warehouse_code": "WH001",
                "status": "ACTIVE",
                "mod_ts": "2024-01-15T10:00:00Z",
            }
        ],
        "pagination": {
            "page": 1,
            "page_size": 500,
            "total_pages": 1,
            "total_records": 1,
        },
    }


@pytest.fixture
def mock_httpx_client(mock_wms_api_response):
    """Mock HTTPX client for WMS API calls."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.json.return_value = mock_wms_api_response
    mock_response.status_code = 200
    mock_client.get.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    return mock_client


@pytest.fixture
def mock_flext_container():
    """Mock FLEXT dependency injection container."""
    mock_container = MagicMock()
    mock_service = MagicMock()
    mock_container.get.return_value = mock_service
    return mock_container


@pytest.fixture
def sample_pipeline_config() -> dict[str, Any]:
    """Provide a sample pipeline configuration."""
    return {
        "name": "test-pipeline",
        "environment": "test",
        "extractor": {
            "name": "tap-oracle-wms-full",
            "config": {
                "base_url": "https://test-wms.example.com",
                "username": "test_user",
                "password": "test_pass",
                "company_code": "TEST",
                "facility_code": "TEST01",
                "entities": ["allocation", "order_hdr", "order_dtl"],
                "page_size": 500,
                "timeout": 600,
                "max_retries": 3,
                "enable_incremental": False,
                "start_date": "2024-01-01T00:00:00Z",
            },
        },
        "loader": {
            "name": "target-oracle-full",
            "config": {
                "oracle_config": {
                    "host": "localhost",
                    "port": 1521,
                    "service_name": "TESTDB",
                    "username": "test_user",
                    "password": "test_pass",
                    "protocol": "tcp",
                },
                "default_target_schema": "TEST_SCHEMA",
                "batch_size": 5000,
                "load_method": "append_only",
                "add_record_metadata": False,
            },
        },
    }


@pytest.fixture
def sample_incremental_config() -> dict[str, Any]:
    """Provide a sample incremental pipeline configuration."""
    config = sample_pipeline_config()
    config["extractor"]["config"]["enable_incremental"] = True
    config["extractor"]["config"]["replication_key"] = "mod_ts"
    config["loader"]["config"]["load_method"] = "upsert"
    return config


@pytest.fixture
def valid_gruponos_config(sample_pipeline_config) -> GruponosMeltanoNativeConfig:
    """Provide a valid GruponosMeltanoNativeConfig instance."""
    return GruponosMeltanoNativeConfig(
        environment="test",
        debug=True,
        log_level="DEBUG",
        pipeline=sample_pipeline_config,
    )


@pytest.fixture
def mock_orchestrator(valid_gruponos_config, mock_flext_container):
    """Provide a mock orchestrator instance."""
    with patch(
        "gruponos_meltano_native.orchestrator.FlextContainer.get_global",
        return_value=mock_flext_container,
    ):
        return GruponosMeltanoOrchestrator()


@pytest.fixture
def mock_cli(valid_gruponos_config):
    """Provide a mock CLI instance."""
    return GruponosMeltanoNativeCli()


@pytest.fixture
def clean_flext_container():
    """Provide a clean FLEXT container state for tests."""
    # This fixture ensures each test starts with a clean container state

    # Clear any existing global container
    if hasattr(FlextContainer, "_global_instance"):
        FlextContainer._global_instance = None

    container = FlextContainer.get_global()

    yield container

    # Cleanup after test
    if hasattr(FlextContainer, "_global_instance"):
        FlextContainer._global_instance = None


@pytest.fixture
def sample_file_data() -> dict[str, Any]:
    """Provide sample file processing data."""
    return {
        "file_path": "/tmp/test_data.json",
        "content": {
            "allocations": [
                {"allocation_id": "ALLOC001", "item_code": "ITEM123", "quantity": 100.0}
            ]
        },
        "metadata": {
            "source": "test_file",
            "timestamp": "2024-01-15T10:00:00Z",
            "record_count": 1,
        },
    }


@pytest.fixture
def mock_environment_variables():
    """Mock environment variables for testing."""
    env_vars = {
        "TAP_ORACLE_WMS_BASE_URL": "https://test-wms.example.com",
        "TAP_ORACLE_WMS_USERNAME": "test_user",
        "TAP_ORACLE_WMS_PASSWORD": "test_pass",
        "TAP_ORACLE_WMS_COMPANY_CODE": "TEST",
        "TAP_ORACLE_WMS_FACILITY_CODE": "TEST01",
        "FLEXT_TARGET_ORACLE_HOST": "localhost",
        "FLEXT_TARGET_ORACLE_PORT": "1521",
        "FLEXT_TARGET_ORACLE_SERVICE_NAME": "TESTDB",
        "FLEXT_TARGET_ORACLE_USERNAME": "test_user",
        "FLEXT_TARGET_ORACLE_PASSWORD": "test_pass",
        "FLEXT_TARGET_ORACLE_PROTOCOL": "tcp",
        "FLEXT_TARGET_ORACLE_SCHEMA": "TEST_SCHEMA",
    }

    with patch.dict(os.environ, env_vars):
        yield env_vars


@pytest.fixture
def sample_monitoring_data() -> dict[str, Any]:
    """Provide sample monitoring data."""
    return {
        "pipeline_id": "test-pipeline-001",
        "start_time": "2024-01-15T10:00:00Z",
        "end_time": "2024-01-15T10:30:00Z",
        "status": "SUCCESS",
        "records_processed": 1000,
        "records_failed": 5,
        "performance_metrics": {
            "throughput": 33.3,  # records/second
            "memory_peak": 256,  # MB
            "cpu_average": 65.5,  # percentage
        },
        "errors": [
            {
                "timestamp": "2024-01-15T10:05:00Z",
                "error_type": "VALIDATION_ERROR",
                "message": "Invalid quantity value",
                "record_id": "ALLOC001",
            }
        ],
    }


@pytest.fixture
def mock_alert_manager():
    """Mock alert manager for testing."""
    alert_manager = MagicMock()
    alert_manager.send_alert.return_value = True
    alert_manager.check_thresholds.return_value = []
    return alert_manager


@pytest.fixture
def mock_metrics_collector():
    """Mock metrics collector for testing."""
    collector = MagicMock()
    collector.collect_metrics.return_value = {
        "pipeline_runtime": 1800.5,
        "records_processed": 10000,
        "error_rate": 0.05,
    }
    return collector


@pytest.fixture
def sample_validation_errors() -> list[dict[str, Any]]:
    """Provide sample validation errors."""
    return [
        {
            "field": "quantity",
            "value": -10.5,
            "error_type": "NEGATIVE_VALUE",
            "message": "Quantity cannot be negative",
            "severity": "ERROR",
        },
        {
            "field": "allocation_date",
            "value": "invalid-date",
            "error_type": "INVALID_FORMAT",
            "message": "Invalid date format",
            "severity": "WARNING",
        },
        {
            "field": "item_code",
            "value": "",
            "error_type": "MISSING_REQUIRED",
            "message": "Item code is required",
            "severity": "ERROR",
        },
    ]


@pytest.fixture
def sample_quality_metrics() -> dict[str, Any]:
    """Provide sample data quality metrics."""
    return {
        "total_records": 10000,
        "valid_records": 9500,
        "invalid_records": 500,
        "quality_score": 95.0,
        "completeness_score": 98.5,
        "accuracy_score": 99.2,
        "consistency_score": 96.8,
        "timeliness_score": 100.0,
        "validation_errors": {
            "schema_errors": 150,
            "business_rule_errors": 250,
            "data_type_errors": 100,
        },
        "performance_metrics": {
            "processing_time": 45.2,  # seconds
            "throughput": 221.2,  # records/second
            "memory_usage": 512.5,  # MB
        },
    }


# Async fixtures for async tests
@pytest_asyncio.fixture
async def async_mock_wms_client(mock_wms_api_response):
    """Async mock WMS API client."""
    mock_client = MagicMock()

    # Mock async context manager
    mock_client.__aenter__ = MagicMock(return_value=mock_client)
    mock_client.__aexit__ = MagicMock(return_value=None)

    # Mock async get method
    async def mock_get(url, **kwargs):
        response = MagicMock()
        response.status_code = 200
        response.json = MagicMock(return_value=mock_wms_api_response)
        return response

    mock_client.get = mock_get
    return mock_client


@pytest.fixture
def sample_etl_result() -> dict[str, Any]:
    """Provide a sample ETL pipeline result."""
    return {
        "pipeline_id": str(uuid.uuid4()),
        "pipeline_name": "test-full-sync",
        "status": "SUCCESS",
        "start_time": "2024-01-15T10:00:00Z",
        "end_time": "2024-01-15T10:30:00Z",
        "duration_seconds": 1800.0,
        "records_extracted": 10000,
        "records_transformed": 9500,
        "records_loaded": 9500,
        "records_failed": 500,
        "performance_metrics": {
            "extraction_rate": 250.0,  # records/second
            "transformation_rate": 235.0,
            "loading_rate": 220.0,
            "overall_throughput": 5.28,  # records/second average
        },
        "quality_metrics": {
            "data_quality_score": 95.0,
            "completeness_score": 98.5,
            "accuracy_score": 99.2,
        },
        "errors": [
            {
                "phase": "transformation",
                "error_type": "VALIDATION_ERROR",
                "message": "Invalid quantity value: -10.5",
                "record_count": 50,
            }
        ],
    }


# Factory fixtures for generating test data
@pytest.fixture
def allocation_factory():
    """Factory for creating test allocation records."""

    def _create_allocation(**kwargs):
        defaults = {
            "allocation_id": f"ALLOC{uuid.uuid4().hex[:6].upper()}",
            "item_code": f"ITEM{uuid.uuid4().hex[:6].upper()}",
            "location_code": f"LOC{uuid.uuid4().hex[:6].upper()}",
            "allocated_quantity": 100.0,
            "allocated_date": "2024-01-15T10:00:00Z",
            "warehouse_code": "WH001",
            "status": "ACTIVE",
            "mod_ts": "2024-01-15T10:00:00Z",
        }
        defaults.update(kwargs)
        return defaults

    return _create_allocation


@pytest.fixture
def order_factory():
    """Factory for creating test order records."""

    def _create_order(**kwargs):
        defaults = {
            "order_id": str(uuid.uuid4()),
            "order_number": f"ORD-2024-{uuid.uuid4().hex[:6].upper()}",
            "customer_id": f"CUST{uuid.uuid4().hex[:6].upper()}",
            "order_date": "2024-01-15",
            "status": "PROCESSING",
            "total_amount": 1500.50,
            "warehouse_code": "WH001",
            "mod_ts": "2024-01-15T10:00:00Z",
        }
        defaults.update(kwargs)
        return defaults

    return _create_order


# Configuration fixtures for different test scenarios
@pytest.fixture(params=["full_sync", "incremental_sync"])
def pipeline_scenario(request, sample_pipeline_config, sample_incremental_config):
    """Parameterized fixture for different pipeline scenarios."""
    if request.param == "full_sync":
        return {
            "name": "full_sync",
            "config": sample_pipeline_config,
            "expected_load_method": "append_only",
        }
    return {
        "name": "incremental_sync",
        "config": sample_incremental_config,
        "expected_load_method": "upsert",
    }


# Cleanup fixture to ensure clean state between tests
@pytest.fixture(autouse=True)
def cleanup_test_artifacts() -> None:
    """Clean up test artifacts after each test."""
    return

    # Add any cleanup logic here if needed
    # For example, cleaning up temporary files, resetting global state, etc.
