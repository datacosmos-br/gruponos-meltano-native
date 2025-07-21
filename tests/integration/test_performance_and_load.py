"""Performance and load testing for GrupoNOS Oracle WMS integration.

These tests focus on performance characteristics and load handling:
- Connection pool performance and stress testing
- Large dataset processing and validation
- Memory usage and resource monitoring
- Concurrent operation handling
- Performance regression testing

Requirements:
- Real Oracle database connections
- Sufficient data volume for meaningful performance tests
- Resource monitoring capabilities
- Time and patience for load testing
"""

from __future__ import annotations

import concurrent.futures
import contextlib
import gc
import os
import time
from statistics import mean, median
from typing import Any

import pytest

from gruponos_meltano_native.config import OracleConnectionConfig
from gruponos_meltano_native.oracle.connection_manager_enhanced import (
    OracleConnectionManager,
)
from gruponos_meltano_native.oracle.table_creator import OracleTableCreator
from gruponos_meltano_native.validators.data_validator import (
    DataValidator,
    ValidationRule,
)


class TestConnectionPerformance:
    """Test Oracle connection performance and resource usage."""

    @pytest.fixture
    def performance_config(self) -> OracleConnectionConfig:
        """High-performance Oracle configuration for testing."""
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
            connection_timeout=10,  # Shorter timeout for performance testing
            retry_attempts=2,
            retry_delay=2,
            connection_pool_size=10,  # Larger pool for performance testing
        )

    @pytest.mark.integration
    @pytest.mark.performance
    @pytest.mark.slow
    def test_connection_establishment_performance(
        self,
        performance_config: OracleConnectionConfig,
    ) -> None:
        """Test Oracle connection establishment performance."""
        connection_times = []

        # Test multiple connection attempts
        for attempt in range(10):
            manager = OracleConnectionManager(performance_config)

            start_time = time.perf_counter()
            connection = manager.connect()
            connection_time = time.perf_counter() - start_time

            if connection is not None:
                connection_times.append(connection_time)
                manager.close()
            else:
                pytest.fail(f"Connection failed on attempt {attempt + 1}")

        # Analyze performance
        avg_time = mean(connection_times)
        median(connection_times)
        max_time = max(connection_times)
        min_time = min(connection_times)


        # Performance assertions
        assert avg_time < 5.0, f"Average connection time too slow: {avg_time:.3f}s"
        assert max_time < 10.0, f"Maximum connection time too slow: {max_time:.3f}s"
        assert min_time > 0.0, "Connection time should be measurable"

        # Consistency check
        time_variance = max_time - min_time
        assert time_variance < 15.0, f"Connection time variance too high: {time_variance:.3f}s"

    @pytest.mark.integration
    @pytest.mark.performance
    @pytest.mark.slow
    def test_concurrent_connection_handling(
        self,
        performance_config: OracleConnectionConfig,
    ) -> None:
        """Test handling multiple concurrent Oracle connections."""
        num_concurrent = 8  # Test with 8 concurrent connections
        connection_results = []

        def test_single_connection(connection_id: int) -> dict[str, Any]:
            """Test a single connection in a thread."""
            try:
                manager = OracleConnectionManager(performance_config)

                start_time = time.perf_counter()
                connection = manager.connect()
                connect_time = time.perf_counter() - start_time

                if connection is None:
                    return {"id": connection_id, "success": False, "error": "Connection failed"}

                # Test query execution
                query_start = time.perf_counter()
                result = manager.fetch_one("SELECT 1 FROM DUAL")
                query_time = time.perf_counter() - query_start

                manager.close()

                return {
                    "id": connection_id,
                    "success": True,
                    "connect_time": connect_time,
                    "query_time": query_time,
                    "total_time": connect_time + query_time,
                    "result": result[0] if result else None,
                }

            except Exception as e:
                return {"id": connection_id, "success": False, "error": str(e)}

        # Run concurrent connections
        start_time = time.perf_counter()
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_concurrent) as executor:
            futures = [
                executor.submit(test_single_connection, i)
                for i in range(num_concurrent)
            ]

            for future in concurrent.futures.as_completed(futures):
                connection_results.extend([future.result()])

        time.perf_counter() - start_time

        # Analyze results
        successful_connections = [r for r in connection_results if r["success"]]
        failed_connections = [r for r in connection_results if not r["success"]]


        # Performance requirements
        success_rate = len(successful_connections) / num_concurrent
        assert success_rate >= 0.8, f"Success rate too low: {success_rate:.2%}"

        if successful_connections:
            avg_connect_time = mean([r["connect_time"] for r in successful_connections])
            avg_query_time = mean([r["query_time"] for r in successful_connections])


            assert avg_connect_time < 10.0, f"Concurrent connection time too slow: {avg_connect_time:.3f}s"
            assert avg_query_time < 2.0, f"Concurrent query time too slow: {avg_query_time:.3f}s"

        # Log failed connections for debugging
        if failed_connections:
            for _failed in failed_connections:
                pass

    @pytest.mark.integration
    @pytest.mark.performance
    @pytest.mark.slow
    def test_connection_pool_stress_test(
        self,
        performance_config: OracleConnectionConfig,
    ) -> None:
        """Stress test connection pooling and resource management."""
        # Configure for stress testing
        stress_config = OracleConnectionConfig(
            **performance_config.model_dump(),
            connection_pool_size=5,
            connection_timeout=5,
        )

        managers = []
        active_connections = 0
        max_connections = 15  # More than pool size to test limits

        try:
            # Create multiple connection managers
            for _ in range(max_connections):
                manager = OracleConnectionManager(stress_config)
                connection = manager.connect()

                if connection is not None:
                    managers.append(manager)
                    active_connections += 1

                # Small delay to simulate real usage
                time.sleep(0.1)


            # Test query execution with all connections
            successful_queries = 0
            for i, manager in enumerate(managers):
                with contextlib.suppress(Exception):
                    result = manager.fetch_one(f"SELECT {i + 1} FROM DUAL")  # noqa: S608
                    if result and result[0] == i + 1:
                        successful_queries += 1


            # Performance requirements for stress test
            assert active_connections >= stress_config.connection_pool_size, "Should establish at least pool_size connections"
            assert successful_queries >= active_connections * 0.8, "Most queries should succeed under stress"

        finally:
            # Clean up all connections
            for manager in managers:
                with contextlib.suppress(Exception):
                    manager.close()  # Best effort cleanup


class TestDataProcessingPerformance:
    """Test performance of data processing and validation operations."""

    @pytest.mark.integration
    @pytest.mark.performance
    def test_large_dataset_validation_performance(self) -> None:
        """Test data validator performance with large datasets."""
        # Create comprehensive validation rules
        validation_rules = [
            ValidationRule("id", "required"),
            ValidationRule("id", "number", {"min_value": 1}),
            ValidationRule("name", "required"),
            ValidationRule("name", "string", {"max_length": 100}),
            ValidationRule("email", "email"),
            ValidationRule("amount", "decimal"),
            ValidationRule("status", "enum", {"allowed_values": ["ACTIVE", "INACTIVE", "PENDING"]}),
            ValidationRule("created_date", "date"),
            ValidationRule("priority", "number", {"min_value": 1, "max_value": 10}),
        ]

        validator = DataValidator(rules=validation_rules, strict_mode=False)

        # Generate large dataset (simulating WMS data volume)
        dataset_size = 10000
        large_dataset = []

        start_generation = time.perf_counter()
        for i in range(dataset_size):
            record = {
                "id": str(i + 1),
                "name": f"Record_{i:06d}",
                "email": f"user{i}@gruponos.com",
                "amount": f"{(i * 123.45) % 10000:.2f}",
                "status": ["ACTIVE", "INACTIVE", "PENDING"][i % 3],
                "created_date": "2024-07-21T10:00:00",
                "priority": str((i % 10) + 1),
                "optional_field": f"data_{i}" if i % 3 == 0 else None,
            }
            large_dataset.append(record)

        time.perf_counter() - start_generation

        # Test validation performance
        start_validation = time.perf_counter()
        total_errors = 0

        for record in large_dataset:
            errors = validator.validate(record)
            total_errors += len(errors)

        validation_time = time.perf_counter() - start_validation

        # Test conversion performance
        schema = {
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "email": {"type": "string"},
                "amount": {"type": "number"},
                "status": {"type": "string"},
                "created_date": {"type": "string", "format": "date-time"},
                "priority": {"type": "integer"},
                "optional_field": {"type": ["string", "null"]},
            },
        }

        start_conversion = time.perf_counter()
        converted_records = []

        for record in large_dataset[:1000]:  # Convert subset for performance
            converted = validator.validate_and_convert_record(record, schema)
            converted_records.append(converted)

        conversion_time = time.perf_counter() - start_conversion

        # Performance analysis
        records_per_second_validation = dataset_size / validation_time
        records_per_second_conversion = 1000 / conversion_time


        # Performance requirements
        assert records_per_second_validation >= 1000, f"Validation too slow: {records_per_second_validation:.0f} rec/sec"
        assert records_per_second_conversion >= 100, f"Conversion too slow: {records_per_second_conversion:.0f} rec/sec"
        assert validation_time < 30.0, f"Total validation time too long: {validation_time:.3f}s"

        # Data quality requirements
        error_rate = (total_errors / dataset_size) * 100
        assert error_rate < 20.0, f"Error rate too high: {error_rate:.2f}%"

        # Verify conversion correctness
        sample_converted = converted_records[0]
        assert isinstance(sample_converted["id"], int), "ID should convert to integer"
        assert isinstance(sample_converted["amount"], (int, float)), "Amount should convert to number"
        assert isinstance(sample_converted["priority"], int), "Priority should convert to integer"

    @pytest.mark.integration
    @pytest.mark.performance
    @pytest.mark.memory
    def test_memory_usage_during_processing(self) -> None:
        """Test memory usage patterns during data processing."""
        try:
            import psutil
        except ImportError:
            pytest.skip("psutil required for memory testing")

        process = psutil.Process(os.getpid())

        # Baseline memory usage
        gc.collect()  # Force garbage collection
        process.memory_info().rss / 1024 / 1024  # MB

        validator = DataValidator(strict_mode=False)

        # Test memory usage with increasingly large datasets
        dataset_sizes = [1000, 5000, 10000, 20000]
        memory_measurements = []

        for size in dataset_sizes:
            # Generate dataset
            dataset = []
            for i in range(size):
                record = {
                    "id": i,
                    "data": f"test_data_{i:06d}",
                    "amount": i * 1.23,
                    "active": i % 2 == 0,
                }
                dataset.append(record)

            # Measure memory before processing
            gc.collect()
            memory_before = process.memory_info().rss / 1024 / 1024  # MB

            # Process dataset
            start_time = time.perf_counter()
            for record in dataset:
                validator.validate_and_convert_record(record, {
                    "properties": {
                        "id": {"type": "integer"},
                        "data": {"type": "string"},
                        "amount": {"type": "number"},
                        "active": {"type": "boolean"},
                    },
                })
            processing_time = time.perf_counter() - start_time

            # Measure memory after processing
            memory_after = process.memory_info().rss / 1024 / 1024  # MB
            memory_used = memory_after - memory_before

            memory_measurements.append({
                "size": size,
                "memory_before": memory_before,
                "memory_after": memory_after,
                "memory_used": memory_used,
                "processing_time": processing_time,
                "records_per_mb": size / max(memory_used, 0.1),  # Avoid division by zero
            })

            # Clean up
            del dataset
            gc.collect()

        # Analyze memory usage patterns

        for _measurement in memory_measurements:
            pass

        # Memory efficiency requirements
        largest_dataset = memory_measurements[-1]
        assert largest_dataset["memory_used"] < 500, f"Memory usage too high: {largest_dataset['memory_used']:.1f} MB"

        # Check for memory leaks (memory should not grow linearly with dataset size)
        memory_per_record = largest_dataset["memory_used"] / largest_dataset["size"] * 1024 * 1024  # bytes per record
        assert memory_per_record < 1000, f"Memory per record too high: {memory_per_record:.1f} bytes/record"

        # Processing time should scale reasonably
        time_per_record = largest_dataset["processing_time"] / largest_dataset["size"] * 1000  # ms per record
        assert time_per_record < 1.0, f"Processing time per record too high: {time_per_record:.3f} ms/record"


class TestDDLGenerationPerformance:
    """Test Oracle DDL generation performance."""

    @pytest.fixture
    def table_creator_config(self) -> dict[str, Any]:
        """Configuration for table creator performance testing."""
        if not all(os.getenv(var) for var in [
            "FLEXT_TARGET_ORACLE_HOST",
            "FLEXT_TARGET_ORACLE_USERNAME",
            "FLEXT_TARGET_ORACLE_PASSWORD",
        ]):
            pytest.skip("Missing Oracle configuration for DDL testing")

        return {
            "host": os.environ["FLEXT_TARGET_ORACLE_HOST"],
            "port": int(os.getenv("FLEXT_TARGET_ORACLE_PORT", "1522")),
            "service_name": os.getenv("FLEXT_TARGET_ORACLE_SERVICE_NAME", "XEPDB1"),
            "username": os.environ["FLEXT_TARGET_ORACLE_USERNAME"],
            "password": os.environ["FLEXT_TARGET_ORACLE_PASSWORD"],
        }

    @pytest.mark.integration
    @pytest.mark.performance
    def test_complex_ddl_generation_performance(
        self,
        table_creator_config: dict[str, Any],
    ) -> None:
        """Test DDL generation performance for complex schemas."""
        creator = OracleTableCreator(table_creator_config)

        # Create increasingly complex schemas
        schema_complexities = [10, 50, 100, 200]  # Number of columns
        ddl_performance = []

        for num_columns in schema_complexities:
            # Generate complex schema
            properties = {}
            for i in range(num_columns):
                col_type = ["string", "integer", "number", "boolean", "date-time"][i % 5]
                properties[f"column_{i:03d}"] = {"type": col_type}

                if col_type == "string":
                    properties[f"column_{i:03d}"]["maxLength"] = str(50 + (i % 200))
                elif col_type in ["integer", "number"]:
                    properties[f"column_{i:03d}"]["minimum"] = str(0)
                    properties[f"column_{i:03d}"]["maximum"] = str(10000)

            # Add primary key and indexes
            key_properties = [f"column_{i:03d}" for i in range(min(3, num_columns))]

            complex_schema = {
                "properties": properties,
                "key_properties": key_properties,
            }

            # Measure DDL generation time
            start_time = time.perf_counter()
            ddl = creator.create_table_from_schema(f"PERF_TEST_{num_columns}_COLS", complex_schema)
            ddl_time = time.perf_counter() - start_time

            # Measure index generation time
            start_index = time.perf_counter()
            indexes = creator.create_indexes_for_table(f"PERF_TEST_{num_columns}_COLS", complex_schema)
            index_time = time.perf_counter() - start_index

            ddl_performance.append({
                "columns": num_columns,
                "ddl_time": ddl_time,
                "index_time": index_time,
                "total_time": ddl_time + index_time,
                "ddl_size": len(ddl),
                "num_indexes": len(indexes),
                "columns_per_second": num_columns / (ddl_time + index_time),
            })

        # Analyze DDL generation performance

        for _perf in ddl_performance:
            pass

        # Performance requirements
        largest_schema = ddl_performance[-1]
        assert largest_schema["total_time"] < 5.0, f"DDL generation too slow: {largest_schema['total_time']:.3f}s"
        assert largest_schema["columns_per_second"] >= 50, f"Column processing too slow: {largest_schema['columns_per_second']:.0f} col/s"

        # DDL quality checks
        assert largest_schema["ddl_size"] > 10000, "DDL should be substantial for complex schema"
        assert largest_schema["num_indexes"] >= 5, "Should generate reasonable number of indexes"

        # Scalability check - time should scale sub-linearly
        if len(ddl_performance) >= 2:
            time_ratio = ddl_performance[-1]["total_time"] / ddl_performance[0]["total_time"]
            column_ratio = ddl_performance[-1]["columns"] / ddl_performance[0]["columns"]
            scalability_factor = time_ratio / column_ratio

            assert scalability_factor < 2.0, f"DDL generation scaling poorly: {scalability_factor:.2f}"


# Performance Test Configuration
@pytest.fixture(scope="session")
def performance_test_environment() -> None:
    """Set up performance testing environment."""
    # Check for performance testing dependencies
    missing_packages = []
    try:
        import psutil
    except ImportError:
        missing_packages.append("psutil")

    try:
        import concurrent.futures
    except ImportError:
        missing_packages.append("concurrent.futures")

    if missing_packages:
        pytest.skip(f"Performance tests require packages: {', '.join(missing_packages)}")

    # Log performance test configuration

    try:
        import psutil
        psutil.virtual_memory()
    except ImportError:
        pass



if __name__ == "__main__":
    # Allow running performance tests directly
    pytest.main([__file__, "-v", "-m", "performance", "--tb=short"])
