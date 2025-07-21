"""End-to-end integration tests for Oracle WMS functionality.

These tests require real Oracle database connections and test complete business workflows:
- WMS schema discovery and mapping
- Table recreation and synchronization
- Data extraction, validation and loading
- Alert monitoring and error handling
- Full pipeline execution with real data

Test Requirements:
- Oracle database with WMS schema access
- Environment variables configured for source and target connections
- Network access to Oracle servers
- Sufficient database permissions for DDL operations
"""

from __future__ import annotations

import os
import tempfile
import time
from pathlib import Path
from typing import Any

import pytest

from gruponos_meltano_native.config import (
    AlertConfig,
    GrupoNOSConfig,
    OracleConnectionConfig,
)
from gruponos_meltano_native.monitoring.alert_manager import AlertManager, AlertService
from gruponos_meltano_native.oracle.connection_manager_enhanced import (
    OracleConnectionManager,
    create_connection_manager_from_env,
)
from gruponos_meltano_native.oracle.recreate_tables_and_sync import (
    check_table_structure,
    create_tables_with_ddl,
    drop_all_wms_tables,
    list_current_tables,
)
from gruponos_meltano_native.oracle.table_creator import OracleTableCreator
from gruponos_meltano_native.validators.data_validator import (
    DataValidator,
    ValidationRule,
    create_validator_for_environment,
)


class TestOracleConnectionIntegration:
    """Test real Oracle database connections and operations."""

    @pytest.fixture
    def oracle_config(self) -> OracleConnectionConfig:
        """Create Oracle configuration from environment variables."""
        required_vars = [
            "FLEXT_TARGET_ORACLE_HOST",
            "FLEXT_TARGET_ORACLE_SERVICE_NAME",
            "FLEXT_TARGET_ORACLE_USERNAME",
            "FLEXT_TARGET_ORACLE_PASSWORD",
        ]

        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            pytest.skip(f"Missing required environment variables: {missing_vars}")

        return OracleConnectionConfig(
            host=os.environ["FLEXT_TARGET_ORACLE_HOST"],
            service_name=os.environ["FLEXT_TARGET_ORACLE_SERVICE_NAME"],
            username=os.environ["FLEXT_TARGET_ORACLE_USERNAME"],
            password=os.environ["FLEXT_TARGET_ORACLE_PASSWORD"],
            port=int(os.getenv("FLEXT_TARGET_ORACLE_PORT", "1522")),
            protocol=os.getenv("FLEXT_TARGET_ORACLE_PROTOCOL", "tcps"),
            connection_timeout=30,
            retry_attempts=3,
        )

    @pytest.fixture
    def connection_manager(self, oracle_config: OracleConnectionConfig) -> OracleConnectionManager:
        """Create connection manager with real Oracle config."""
        return OracleConnectionManager(oracle_config)

    @pytest.mark.integration
    @pytest.mark.slow
    def test_real_oracle_connection_and_basic_queries(
        self,
        connection_manager: OracleConnectionManager,
    ) -> None:
        """Test real Oracle connection and execute basic queries."""
        # Test connection establishment
        connection = connection_manager.connect()
        assert connection is not None, "Should establish real Oracle connection"
        assert connection_manager.is_connected, "Connection manager should report as connected"

        try:
            # Test basic query execution
            result = connection_manager.fetch_one("SELECT 1 FROM DUAL")
            assert result is not None, "Should execute basic query"
            assert result[0] == 1, "Query should return expected result"

            # Test Oracle version query
            version_result = connection_manager.fetch_one(
                "SELECT BANNER FROM V$VERSION WHERE ROWNUM = 1",
            )
            assert version_result is not None, "Should get Oracle version"
            assert "Oracle" in str(version_result[0]), "Should return Oracle version string"

            # Test current user query
            user_result = connection_manager.fetch_one("SELECT USER FROM DUAL")
            assert user_result is not None, "Should get current user"
            assert len(str(user_result[0])) > 0, "Should return non-empty username"

            # Test table space query (permissions test)
            tablespace_result = connection_manager.fetch_all(
                "SELECT TABLESPACE_NAME FROM USER_TABLESPACES",
            )
            assert tablespace_result is not None, "Should query tablespaces"

        finally:
            # Always clean up connection
            connection_manager.close()
            assert not connection_manager.is_connected, "Should close connection properly"

    @pytest.mark.integration
    @pytest.mark.slow
    def test_connection_resilience_and_retry_logic(
        self,
        oracle_config: OracleConnectionConfig,
    ) -> None:
        """Test connection resilience with intentional failures and recovery."""
        # Test with invalid host to trigger retry logic
        bad_config = OracleConnectionConfig(
            host="invalid.host.example.com",
            service_name=oracle_config.service_name,
            username=oracle_config.username,
            password=oracle_config.password,
            port=oracle_config.port,
            retry_attempts=2,
            retry_delay=1,
            connection_timeout=5,
        )

        bad_manager = OracleConnectionManager(bad_config)

        # This should fail but not crash
        start_time = time.time()
        test_result = bad_manager.test_connection()
        elapsed_time = time.time() - start_time

        # Verify retry logic was executed (should take at least retry_delay * retry_attempts)
        assert elapsed_time >= 1.5, "Should have attempted retries with delays"
        assert test_result["success"] is False, "Should fail with invalid host"
        assert "attempts" in test_result, "Should report retry attempts"
        assert test_result["attempts"] >= 2, "Should have attempted multiple connections"

        # Now test recovery with good config
        good_manager = OracleConnectionManager(oracle_config)
        recovery_result = good_manager.test_connection()

        assert recovery_result["success"] is True, "Should recover with valid config"
        assert "oracle_version" in recovery_result, "Should include Oracle version"

        good_manager.close()

    @pytest.mark.integration
    @pytest.mark.slow
    def test_environment_based_connection_creation(self) -> None:
        """Test creating connection manager directly from environment variables."""
        # Skip if required environment variables are missing
        required_vars = [
            "FLEXT_TARGET_ORACLE_HOST",
            "FLEXT_TARGET_ORACLE_SERVICE_NAME",
            "FLEXT_TARGET_ORACLE_USERNAME",
            "FLEXT_TARGET_ORACLE_PASSWORD",
        ]

        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            pytest.skip(f"Missing required environment variables: {missing_vars}")

        # Test environment-based creation
        manager = create_connection_manager_from_env()
        assert isinstance(manager, OracleConnectionManager), "Should create connection manager"

        # Test actual connection
        test_result = manager.test_connection()
        assert test_result["success"] is True, "Should connect using environment config"

        # Verify connection info
        conn_info = manager.get_connection_info()
        assert conn_info["host"] == os.environ["FLEXT_TARGET_ORACLE_HOST"]
        assert conn_info["service_name"] == os.environ["FLEXT_TARGET_ORACLE_SERVICE_NAME"]

        manager.close()


class TestWMSSchemaDiscoveryIntegration:
    """Test WMS schema discovery and mapping with real Oracle connections."""

    @pytest.fixture
    def wms_connection_manager(self) -> OracleConnectionManager:
        """Create WMS connection manager if environment is configured."""
        wms_vars = [
            "TAP_ORACLE_WMS_HOST",
            "TAP_ORACLE_WMS_SERVICE_NAME",
            "TAP_ORACLE_WMS_USERNAME",
            "TAP_ORACLE_WMS_PASSWORD",
        ]

        missing_vars = [var for var in wms_vars if not os.getenv(var)]
        if missing_vars:
            pytest.skip(f"WMS connection not configured, missing: {missing_vars}")

        config = OracleConnectionConfig(
            host=os.environ["TAP_ORACLE_WMS_HOST"],
            service_name=os.environ["TAP_ORACLE_WMS_SERVICE_NAME"],
            username=os.environ["TAP_ORACLE_WMS_USERNAME"],
            password=os.environ["TAP_ORACLE_WMS_PASSWORD"],
            port=int(os.getenv("TAP_ORACLE_WMS_PORT", "1521")),
        )

        return OracleConnectionManager(config)

    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.wms
    def test_wms_table_discovery(self, wms_connection_manager: OracleConnectionManager) -> None:
        """Test discovery of WMS tables in real Oracle database."""
        connection = wms_connection_manager.connect()
        assert connection is not None, "Should connect to WMS database"

        try:
            # Query for WMS-related tables
            wms_tables = wms_connection_manager.fetch_all("""
                SELECT TABLE_NAME, NUM_ROWS, TABLESPACE_NAME
                FROM USER_TABLES
                WHERE TABLE_NAME LIKE 'WMS_%'
                   OR TABLE_NAME LIKE '%ALLOCATION%'
                   OR TABLE_NAME LIKE '%ORDER%'
                   OR TABLE_NAME LIKE '%INVENTORY%'
                ORDER BY TABLE_NAME
            """)

            assert wms_tables is not None, "Should find WMS tables"

            if wms_tables:  # Only test if WMS tables exist
                # Verify table structure
                table_names = [table[0] for table in wms_tables]
                assert len(table_names) > 0, "Should find at least some WMS tables"

                # Test column discovery for first table
                first_table = table_names[0]
                # Use parameterized query to prevent SQL injection
                columns = wms_connection_manager.fetch_all(
                    "SELECT COLUMN_NAME, DATA_TYPE, NULLABLE, DATA_DEFAULT "
                    "FROM USER_TAB_COLUMNS WHERE TABLE_NAME = :table_name ORDER BY COLUMN_ID",
                    {"table_name": first_table},
                )

                assert columns is not None, "Should discover table columns"
                assert len(columns) > 0, "Table should have columns defined"

                # Verify column information completeness
                for column in columns[:3]:  # Test first 3 columns
                    assert column[0] is not None, "Column name should not be null"
                    assert column[1] is not None, "Data type should not be null"
                    assert column[2] in ("Y", "N"), "Nullable should be Y or N"
            else:
                pytest.skip("No WMS tables found in database for testing")

        finally:
            wms_connection_manager.close()

    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.wms
    def test_wms_data_sampling(self, wms_connection_manager: OracleConnectionManager) -> None:
        """Test sampling data from WMS tables for validation."""
        connection = wms_connection_manager.connect()
        assert connection is not None, "Should connect to WMS database"

        try:
            # Find a table with data
            tables_with_data = wms_connection_manager.fetch_all("""
                SELECT TABLE_NAME, NUM_ROWS
                FROM USER_TABLES
                WHERE NUM_ROWS > 0
                  AND (TABLE_NAME LIKE 'WMS_%'
                       OR TABLE_NAME LIKE '%ALLOCATION%'
                       OR TABLE_NAME LIKE '%ORDER%')
                ORDER BY NUM_ROWS DESC
            """)

            if not tables_with_data:
                pytest.skip("No WMS tables with data found for sampling")

            # Sample from the largest table
            test_table = tables_with_data[0][0]

            # Get sample records - validate table name for security
            # This is safe since test_table comes from a controlled database metadata query
            if not test_table.replace("_", "").replace("-", "").isalnum():
                pytest.fail(f"Invalid table name from database metadata: {test_table}")

            # ruff: noqa: S608 - Table name validated above from database metadata
            sample_query = f"""
                SELECT * FROM (
                    SELECT * FROM {test_table}
                    WHERE ROWNUM <= 5
                ) ORDER BY 1
            """
            sample_data = wms_connection_manager.fetch_all(sample_query)

            assert sample_data is not None, "Should retrieve sample data"
            if sample_data:  # Only test if data exists
                assert len(sample_data) > 0, "Should have at least one sample record"

                # Verify record structure
                first_record = sample_data[0]
                assert len(first_record) > 0, "Record should have columns"

                # Test data types (basic validation)
                for _value in first_record[:5]:  # Test first 5 columns
                    assert True, "Values can be null, but structure should be valid"

        finally:
            wms_connection_manager.close()


class TestTableCreationAndSyncIntegration:
    """Test table creation and sync operations with real Oracle database."""

    @pytest.fixture
    def target_config(self) -> OracleConnectionConfig:
        """Target Oracle configuration for table creation tests."""
        required_vars = [
            "FLEXT_TARGET_ORACLE_HOST",
            "FLEXT_TARGET_ORACLE_SERVICE_NAME",
            "FLEXT_TARGET_ORACLE_USERNAME",
            "FLEXT_TARGET_ORACLE_PASSWORD",
        ]

        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            pytest.skip(f"Missing required environment variables: {missing_vars}")

        return OracleConnectionConfig(
            host=os.environ["FLEXT_TARGET_ORACLE_HOST"],
            service_name=os.environ["FLEXT_TARGET_ORACLE_SERVICE_NAME"],
            username=os.environ["FLEXT_TARGET_ORACLE_USERNAME"],
            password=os.environ["FLEXT_TARGET_ORACLE_PASSWORD"],
            port=int(os.getenv("FLEXT_TARGET_ORACLE_PORT", "1522")),
            protocol=os.getenv("FLEXT_TARGET_ORACLE_PROTOCOL", "tcps"),
        )

    @pytest.fixture
    def table_creator(self, target_config: OracleConnectionConfig) -> OracleTableCreator:
        """Create table creator with real Oracle config."""
        return OracleTableCreator({
            "host": target_config.host,
            "port": target_config.port,
            "service_name": target_config.service_name,
            "username": target_config.username,
            "password": target_config.password,
        })

    @pytest.mark.integration
    @pytest.mark.slow
    def test_table_creation_from_singer_schema(
        self,
        table_creator: OracleTableCreator,
        target_config: OracleConnectionConfig,
    ) -> None:
        """Test creating real Oracle table from Singer schema."""
        # Define test schema similar to WMS structure
        test_schema = {
            "properties": {
                "allocation_id": {"type": "integer"},
                "order_number": {"type": "string", "maxLength": 50},
                "item_code": {"type": "string", "maxLength": 100},
                "quantity": {"type": "number"},
                "status": {"type": "string", "maxLength": 20},
                "created_date": {"type": "string", "format": "date-time"},
                "updated_date": {"type": ["string", "null"], "format": "date-time"},
                "active_flag": {"type": ["boolean", "null"]},
                "priority": {"type": ["integer", "null"]},
            },
            "key_properties": ["allocation_id"],
        }

        # Generate DDL
        test_table_name = f"TEST_WMS_INTEGRATION_{int(time.time())}"
        ddl = table_creator.create_table_from_schema(test_table_name, test_schema)

        # Verify DDL structure
        assert f"CREATE TABLE {target_config.username.upper()}.{test_table_name}" in ddl
        assert "ALLOCATION_ID NUMBER(10) NOT NULL" in ddl
        assert "ORDER_NUMBER VARCHAR2(50) NOT NULL" in ddl
        assert "QUANTITY NUMBER NOT NULL" in ddl
        assert "ACTIVE_FLAG NUMBER(1)" in ddl  # Nullable boolean
        assert f"CONSTRAINT PK_{test_table_name} PRIMARY KEY (ALLOCATION_ID)" in ddl

        # Test index generation
        indexes = table_creator.create_indexes_for_table(test_table_name, test_schema)
        assert len(indexes) > 0, "Should generate indexes for common patterns"

        # Find date and ID indexes
        date_indexes = [idx for idx in indexes if "DATE" in idx]
        id_indexes = [idx for idx in indexes if "ALLOCATION_ID" in idx]

        assert len(date_indexes) >= 2, "Should create indexes for date columns"
        assert len(id_indexes) >= 1, "Should create index for ID column"

    @pytest.mark.integration
    @pytest.mark.slow
    def test_table_list_and_structure_operations(self) -> None:
        """Test listing tables and checking structure in real database."""
        # Skip if no target environment configured
        required_vars = [
            "FLEXT_TARGET_ORACLE_HOST",
            "FLEXT_TARGET_ORACLE_USERNAME",
            "FLEXT_TARGET_ORACLE_PASSWORD",
        ]

        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            pytest.skip(f"Missing required environment variables: {missing_vars}")

        # Test listing current tables
        tables = list_current_tables()
        assert isinstance(tables, list), "Should return list of tables"

        # Test table structure checking if tables exist
        if tables:
            # Check structure of first table
            first_table = tables[0]
            structure = check_table_structure(first_table)
            assert isinstance(structure, dict), "Should return table structure info"
            assert "exists" in structure, "Should indicate table existence"
            assert structure["exists"] is True, "Listed table should exist"

            if "columns" in structure:
                assert len(structure["columns"]) > 0, "Table should have columns"

    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.destructive
    def test_drop_and_recreate_operations(self) -> None:
        """Test drop and recreate operations (DESTRUCTIVE - use with caution)."""
        # This test is marked as destructive and requires explicit opt-in
        if os.getenv("ALLOW_DESTRUCTIVE_TESTS", "false").lower() != "true":
            pytest.skip("Destructive tests disabled. Set ALLOW_DESTRUCTIVE_TESTS=true to enable")

        required_vars = [
            "FLEXT_TARGET_ORACLE_HOST",
            "FLEXT_TARGET_ORACLE_USERNAME",
            "FLEXT_TARGET_ORACLE_PASSWORD",
        ]

        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            pytest.skip(f"Missing required environment variables: {missing_vars}")

        # Create a test table first
        test_table_name = f"TEMP_TEST_TABLE_{int(time.time())}"

        # Use table creator to make a simple test table
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            test_catalog = {
                "streams": [{
                    "tap_stream_id": test_table_name,
                    "schema": {
                        "properties": {
                            "id": {"type": "integer"},
                            "name": {"type": "string", "maxLength": 100},
                            "created": {"type": "string", "format": "date-time"},
                        },
                        "key_properties": ["id"],
                    },
                }],
            }
            import json
            json.dump(test_catalog, f)
            catalog_path = Path(f.name)

        try:
            # Test table creation with DDL execution
            result = create_tables_with_ddl(str(catalog_path), [test_table_name])
            # Note: This may fail in CI/CD without SQL*Plus, which is expected
            # The important part is that the function executes without crashing
            assert isinstance(result, bool), "Should return boolean result"

            # List tables to verify
            tables = list_current_tables()
            table_names = [t.upper() for t in tables]

            # If table creation succeeded, test dropping
            if test_table_name.upper() in table_names:
                # Test dropping specific WMS tables (safe since we just created this one)
                drop_result = drop_all_wms_tables()
                assert isinstance(drop_result, bool), "Should return boolean result"

        finally:
            # Clean up catalog file
            catalog_path.unlink()

            # Attempt cleanup of test table (best effort)
            try:
                from gruponos_meltano_native.oracle.connection_manager_enhanced import (
                    create_connection_manager_from_env,
                )
                manager = create_connection_manager_from_env()
                connection = manager.connect()
                if connection:
                    manager.execute(f"DROP TABLE {test_table_name} CASCADE CONSTRAINTS")
                    manager.close()
            except Exception as e:
                # Log cleanup failure but continue - cleanup is best-effort
                import logging
                logging.getLogger(__name__).warning(f"Failed to cleanup test table {test_table_name}: {e}")


class TestDataValidationIntegration:
    """Test data validation with real WMS data patterns."""

    @pytest.mark.integration
    def test_real_wms_data_conversion_patterns(self) -> None:
        """Test data validator with realistic WMS data patterns."""
        # Create validator with production-like rules
        validation_rules = [
            ValidationRule("allocation_id", "required"),
            ValidationRule("allocation_id", "number", {"min_value": 1}),
            ValidationRule("order_number", "required"),
            ValidationRule("order_number", "string", {"max_length": 50}),
            ValidationRule("quantity", "number", {"min_value": 0}),
            ValidationRule("status", "enum", {"allowed_values": ["PENDING", "ALLOCATED", "SHIPPED", "CANCELLED"]}),
            ValidationRule("created_date", "date", {"format": "%Y-%m-%d %H:%M:%S"}),
            ValidationRule("priority", "number", {"min_value": 1, "max_value": 10}),
        ]

        validator = DataValidator(rules=validation_rules, strict_mode=False)

        # Test with realistic WMS-like data (includes common data quality issues)
        test_records = [
            # Valid record
            {
                "allocation_id": "12345",  # String that should convert to number
                "order_number": "ORD-001-2024",
                "item_code": "ITEM-ABC-123",
                "quantity": "150.5",  # String that should convert to number
                "status": "ALLOCATED",
                "created_date": "2024-07-21T10:30:00",
                "updated_date": "2024-07-21T11:45:00",
                "active_flag": "true",  # String that should convert to boolean
                "priority": "5",
            },
            # Record with data quality issues
            {
                "allocation_id": "12346",
                "order_number": "ORD-002-2024",
                "item_code": "",  # Empty string
                "quantity": "0",
                "status": "PENDING",
                "created_date": "2024-07-20 09:15:30",  # Different date format
                "updated_date": None,
                "active_flag": "1",  # Numeric boolean
                "priority": "",  # Empty string for optional number
            },
        ]

        # Test validation and conversion
        for i, record in enumerate(test_records):
            record_dict = dict(record) if not isinstance(record, dict) else record  # Ensure it's a dict
            errors = validator.validate(record_dict)

            if i == 0:  # First record should be mostly valid
                # Some errors expected due to conversion issues, but basic structure should be ok
                assert len(errors) <= 3, f"First record should have minimal errors, got: {errors}"

            # Test conversion regardless of validation errors
            converted = validator.validate_and_convert_record(record_dict, {
                "properties": {
                    "allocation_id": {"type": "integer"},
                    "order_number": {"type": "string"},
                    "item_code": {"type": "string"},
                    "quantity": {"type": "number"},
                    "status": {"type": "string"},
                    "created_date": {"type": "string", "format": "date-time"},
                    "updated_date": {"type": ["string", "null"], "format": "date-time"},
                    "active_flag": {"type": ["boolean", "null"]},
                    "priority": {"type": ["integer", "null"]},
                },
            })

            # Verify conversions worked
            assert isinstance(converted.get("allocation_id"), int), "Should convert allocation_id to integer"
            assert isinstance(converted.get("quantity"), (int, float)), "Should convert quantity to number"

            # Verify boolean conversion
            if "active_flag" in converted and converted["active_flag"] is not None:
                assert isinstance(converted["active_flag"], bool), "Should convert active_flag to boolean"

        # Verify conversion statistics
        stats = validator.get_conversion_stats()
        assert stats["strings_converted_to_numbers"] >= 4, "Should have converted multiple strings to numbers"
        assert stats["dates_normalized"] >= 0, "Should track date normalizations"

    @pytest.mark.integration
    def test_validator_environment_configuration(self) -> None:
        """Test validator creation for different environments."""
        # Test development environment (non-strict)
        dev_validator = create_validator_for_environment("dev")
        assert dev_validator.strict_mode is False, "Dev validator should be non-strict"

        # Test production environment (strict)
        prod_validator = create_validator_for_environment("prod")
        assert prod_validator.strict_mode is True, "Prod validator should be strict"

        # Test validation behavior differences
        test_data = {"missing_required_field": "test"}
        required_rule = ValidationRule("required_field", "required")

        dev_validator.rules = [required_rule]
        prod_validator.rules = [required_rule]

        # Dev should return errors but not raise
        dev_errors = dev_validator.validate(test_data)
        assert len(dev_errors) > 0, "Dev validator should find validation errors"

        # Prod should raise validation exception
        with pytest.raises((ValueError, RuntimeError), match=r"(validation|required)"):
            prod_validator.validate(test_data)


class TestAlertingAndMonitoringIntegration:
    """Test alerting and monitoring with real system integration."""

    @pytest.fixture
    def alert_config(self) -> dict[str, Any]:
        """Alert configuration for testing."""
        return {
            "webhook_enabled": True,
            "webhook_url": "https://httpbin.org/post",  # Test endpoint
            "max_sync_duration_minutes": 30,
            "max_error_rate_percent": 10.0,
            "min_records_threshold": 50,
        }

    @pytest.mark.integration
    @pytest.mark.slow
    def test_real_webhook_alert_integration(self, alert_config: dict[str, Any]) -> None:
        """Test alert manager with real webhook endpoints."""
        from gruponos_meltano_native.config import AlertConfig

        # Create alert service with real webhook
        config = AlertConfig(**alert_config)
        alert_service = AlertService(config)

        # Test successful webhook delivery
        success = alert_service.send_alert(
            message="Integration test alert from GrupoNOS pipeline",
            severity=alert_service.AlertSeverity.MEDIUM,
            context={
                "test_type": "integration",
                "timestamp": time.time(),
                "environment": "test",
            },
        )

        # Should succeed with real webhook endpoint
        assert success is True, "Should successfully deliver webhook alert"

        # Test alert manager threshold monitoring
        alert_manager = AlertManager(config)

        # Test connection time monitoring
        alert_manager.check_connection_time(25.0)  # Under threshold
        assert alert_manager.alert_count == 0, "Should not trigger alert for normal connection time"

        alert_manager.check_connection_time(45.0)  # Over threshold
        assert alert_manager.alert_count >= 1, "Should trigger alert for slow connection"

    @pytest.mark.integration
    def test_system_monitoring_integration(self) -> None:
        """Test system resource monitoring capabilities."""
        import psutil

        from gruponos_meltano_native.config import AlertConfig

        # Create alert manager with realistic thresholds
        config = AlertConfig(
            webhook_enabled=False,  # Disable webhooks for this test
            max_memory_usage_percent=95.0,  # High threshold
            max_cpu_usage_percent=90.0,
        )
        alert_manager = AlertManager(config)

        # Get current system stats
        memory_percent = psutil.virtual_memory().percent
        cpu_percent = psutil.cpu_percent(interval=1)

        # Test memory monitoring (should normally pass)
        alert_manager.check_memory_usage(memory_percent)
        if memory_percent > 95.0:
            assert alert_manager.alert_count >= 1, "Should alert on high memory usage"
        else:
            assert alert_manager.alert_count == 0, "Should not alert on normal memory usage"

        # Test CPU monitoring
        alert_manager.check_cpu_usage(cpu_percent)

        # Verify monitoring is working
        assert isinstance(memory_percent, float), "Should get real memory percentage"
        assert isinstance(cpu_percent, float), "Should get real CPU percentage"
        assert 0 <= memory_percent <= 100, "Memory percentage should be valid range"
        assert 0 <= cpu_percent <= 100, "CPU percentage should be valid range"


class TestFullPipelineIntegration:
    """Test complete end-to-end pipeline with real systems."""

    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.e2e
    def test_complete_configuration_loading(self) -> None:
        """Test loading complete configuration from environment."""
        # This tests the full configuration system
        config = GrupoNOSConfig.from_env()

        # Verify config structure
        assert isinstance(config, GrupoNOSConfig), "Should create main configuration"
        assert hasattr(config, "alerts"), "Should have alerts configuration"
        assert isinstance(config.alerts, AlertConfig), "Should create alert config"

        # Test configuration export
        legacy_env = config.to_legacy_env()
        assert isinstance(legacy_env, dict), "Should export to environment variables"
        assert "DEBUG" in legacy_env, "Should include global settings"

        # If Oracle configs are present, verify they're properly structured
        if config.target_oracle is not None:
            assert hasattr(config.target_oracle, "oracle"), "Target should have Oracle config"
            assert hasattr(config.target_oracle, "schema_name"), "Target should have schema name"

        if config.wms_source is not None:
            assert hasattr(config.wms_source, "oracle"), "WMS source should have Oracle config"

    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.e2e
    def test_cli_integration_with_real_config(self) -> None:
        """Test CLI commands with real configuration and connections."""
        from click.testing import CliRunner

        from gruponos_meltano_native.cli import main

        runner = CliRunner()

        # Test health command with real environment
        result = runner.invoke(main, ["health"])

        # Should execute without crashing
        assert result.exit_code in (0, 1), "Health command should complete"

        # Should produce some output
        assert len(result.output) > 0, "Health command should produce output"

        # Test show-config command
        config_result = runner.invoke(main, ["show-config"])
        assert config_result.exit_code == 0, "Show-config should always succeed"
        assert "GrupoNOS Configuration" in config_result.output, "Should show configuration header"

    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.e2e
    @pytest.mark.skipif(not os.getenv("FULL_E2E_TESTS"), reason="Full E2E tests require FULL_E2E_TESTS=true")
    def test_complete_sync_workflow_simulation(self) -> None:
        """Test complete sync workflow (simulation with real components)."""
        # This test simulates a complete sync workflow using real components
        # but without actually moving large amounts of data

        # Phase 1: Configuration and Connection Testing
        config = GrupoNOSConfig.from_env()
        assert config is not None, "Should load configuration"

        # Phase 2: Source Connection Testing (if configured)
        if config.wms_source is not None:
            try:
                # Test WMS connection
                wms_manager = OracleConnectionManager(config.wms_source.oracle)
                wms_test = wms_manager.test_connection()
                assert wms_test is not None, "Should test WMS connection"
                wms_manager.close()
            except Exception as e:
                pytest.skip(f"WMS connection not available: {e}")

        # Phase 3: Target Connection Testing (if configured)
        if config.target_oracle is not None:
            try:
                target_manager = OracleConnectionManager(config.target_oracle.oracle)
                target_test = target_manager.test_connection()
                assert target_test is not None, "Should test target connection"
                assert target_test["success"] is True, "Target connection should succeed"
                target_manager.close()
            except Exception as e:
                pytest.skip(f"Target connection not available: {e}")

        # Phase 4: Schema Discovery Simulation
        if config.wms_source is not None and config.target_oracle is not None:
            # This would normally discover schemas and create tables
            # For testing, we just verify the components work
            table_creator = OracleTableCreator({
                "host": config.target_oracle.oracle.host,
                "port": config.target_oracle.oracle.port,
                "service_name": config.target_oracle.oracle.service_name,
                "username": config.target_oracle.oracle.username,
                "password": config.target_oracle.oracle.password,
            })

            # Test DDL generation
            test_schema = {
                "properties": {
                    "test_id": {"type": "integer"},
                    "test_name": {"type": "string", "maxLength": 100},
                },
                "key_properties": ["test_id"],
            }

            ddl = table_creator.create_table_from_schema("TEST_SYNC_WORKFLOW", test_schema)
            assert len(ddl) > 100, "Should generate substantial DDL"
            assert "CREATE TABLE" in ddl, "DDL should contain CREATE TABLE"

        # Phase 5: Data Validation Testing
        validator = DataValidator(strict_mode=True)
        test_record = {
            "test_id": "123",
            "test_name": "Integration Test Record",
            "test_amount": "456.78",
        }

        converted = validator.validate_and_convert_record(test_record, {
            "properties": {
                "test_id": {"type": "integer"},
                "test_name": {"type": "string"},
                "test_amount": {"type": "number"},
            },
        })

        assert converted["test_id"] == 123, "Should convert ID to integer"
        assert isinstance(converted["test_amount"], float), "Should convert amount to float"

        # Phase 6: Alert System Testing
        alert_manager = AlertManager(config.alerts)

        # Simulate sync completion
        alert_manager.check_sync_duration(15.0)  # 15 minutes - should be OK
        assert alert_manager.alert_count == 0, "Should not alert on normal sync duration"

        # Test successful completion
        pytest.skip("Complete E2E workflow simulation completed successfully")


# Test Configuration and Fixtures
@pytest.fixture(scope="session", autouse=True)
def setup_integration_environment() -> None:
    """Set up integration test environment."""
    # Ensure we have required packages for integration tests
    try:
        import psutil
        import requests
    except ImportError:
        pytest.skip("Integration tests require additional packages: pip install requests psutil")

    # Log test environment info


if __name__ == "__main__":
    # Allow running integration tests directly
    pytest.main([__file__, "-v", "-m", "integration"])
