"""Performance and load testing for GrupoNOS Oracle integration.

These tests focus on performance characteristics and load handling.
"""

from __future__ import annotations

import os
import time

import pytest
from dotenv import load_dotenv

from gruponos_meltano_native.config import GruponosMeltanoOracleConnectionConfig
from gruponos_meltano_native.oracle.connection_manager_enhanced import (
    GruponosMeltanoOracleConnectionManager,
)

# Load environment variables from .env file for integration tests
load_dotenv()


class TestPerformanceBasics:
    """Test basic performance characteristics."""

    @pytest.fixture
    def performance_config(self) -> GruponosMeltanoOracleConnectionConfig:
        """Create Oracle configuration optimized for performance testing."""
        required_vars = [
            "FLEXT_TARGET_ORACLE_HOST",
            "FLEXT_TARGET_ORACLE_SERVICE_NAME",
            "FLEXT_TARGET_ORACLE_USERNAME",
            "FLEXT_TARGET_ORACLE_PASSWORD",
        ]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            pytest.skip(f"Missing required environment variables: {missing_vars}")

        return GruponosMeltanoOracleConnectionConfig(
            host=os.environ["FLEXT_TARGET_ORACLE_HOST"],
            service_name=os.environ["FLEXT_TARGET_ORACLE_SERVICE_NAME"],
            username=os.environ["FLEXT_TARGET_ORACLE_USERNAME"],
            password=os.environ["FLEXT_TARGET_ORACLE_PASSWORD"],
            port=int(os.getenv("FLEXT_TARGET_ORACLE_PORT", "1522")),
            protocol=os.getenv("FLEXT_TARGET_ORACLE_PROTOCOL", "tcps"),
        )

    @pytest.mark.integration
    @pytest.mark.performance
    @pytest.mark.slow
    def test_connection_establishment_performance(
        self,
        performance_config: GruponosMeltanoOracleConnectionConfig,
    ) -> None:
        """Test Oracle connection establishment performance."""
        connection_times = []

        # Perform multiple connection tests to get meaningful performance data
        for i in range(5):
            connection_manager = GruponosMeltanoOracleConnectionManager(
                performance_config,
            )

            start_time = time.time()
            result = connection_manager.test_connection()
            end_time = time.time()

            assert result.is_success, f"Connection {i + 1} failed: {result.error}"

            connection_time = end_time - start_time
            connection_times.append(connection_time)

        # Verify performance characteristics
        avg_time = sum(connection_times) / len(connection_times)
        max_time = max(connection_times)

        # Basic performance assertions
        assert avg_time < 10.0, f"Average connection time too slow: {avg_time:.2f}s"
        assert max_time < 15.0, f"Maximum connection time too slow: {max_time:.2f}s"

    @pytest.mark.integration
    @pytest.mark.performance
    @pytest.mark.slow
    def test_query_performance(
        self,
        performance_config: GruponosMeltanoOracleConnectionConfig,
    ) -> None:
        """Test Oracle query execution performance."""
        connection_manager = GruponosMeltanoOracleConnectionManager(performance_config)

        # Test simple query performance
        start_time = time.time()
        result = connection_manager.execute_query(
            "SELECT COUNT(*) as row_count FROM DUAL",
        )
        end_time = time.time()

        assert result.is_success, f"Query failed: {result.error}"

        query_time = end_time - start_time
        assert query_time < 5.0, f"Query time too slow: {query_time:.2f}s"

    @pytest.mark.integration
    @pytest.mark.performance
    @pytest.mark.slow
    def test_multiple_operations_performance(
        self,
        performance_config: GruponosMeltanoOracleConnectionConfig,
    ) -> None:
        """Test performance of multiple operations."""
        connection_manager = GruponosMeltanoOracleConnectionManager(performance_config)

        operations = [
            "SELECT 1 FROM DUAL",
            "SELECT SYSDATE FROM DUAL",
            "SELECT USER FROM DUAL",
            "SELECT SYS_CONTEXT('USERENV', 'SESSION_USER') FROM DUAL",
            "SELECT COUNT(*) FROM DUAL",
        ]

        start_time = time.time()

        for query in operations:
            result = connection_manager.execute_query(query)
            assert result.is_success, f"Query failed: {query} - {result.error}"

        end_time = time.time()

        total_time = end_time - start_time
        avg_per_operation = total_time / len(operations)

        # Performance assertions
        assert total_time < 10.0, f"Total time too slow: {total_time:.2f}s"
        assert avg_per_operation < 2.0, (
            f"Average per operation too slow: {avg_per_operation:.2f}s"
        )
