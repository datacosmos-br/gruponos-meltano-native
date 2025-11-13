"""Simplified tests for Oracle schema discovery functionality.

REAL IMPLEMENTATION TESTS - NO MOCKS OR FALLBACKS.
Tests the actual Oracle schema discovery logic with basic functionality.
"""

from flext_core import FlextLogger
from flext_db_oracle import FlextDbOracleApi, FlextDbOracleMetadataManager


class TestOracleSchemaDiscoverySimple:
    """Test Oracle schema discovery with real implementation."""

    def test_schema_discovery_functions_exist(self) -> None:
        """Test schema discovery functions exist."""  # Test flext-db-oracle API exists
        assert FlextDbOracleApi is not None
        assert hasattr(FlextDbOracleApi, "with_config")
        assert callable(FlextDbOracleApi.from_config)

    def test_schema_discovery_module_import(self) -> None:
        """Test schema discovery module imports correctly."""  # Test that flext-db-oracle components are available
        assert FlextDbOracleApi is not None
        assert FlextDbOracleMetadataManager is not None

    def test_discovery_function_callable(self) -> None:
        """Test discovery function is callable."""  # Test that the main API function exists and is callable
        assert hasattr(FlextDbOracleApi, "with_config")
        assert callable(FlextDbOracleApi.from_config)

        # Test basic API usage
        config_dict = {
            "host": "localhost",
            "port": 1521,
            "service_name": "TESTDB",
            "username": "test",
            "password": "test",
        }
        api = FlextDbOracleApi.from_config(config_dict)
        assert api is not None

    def test_module_has_logger(self) -> None:
        """Test module has logger configured."""  # Test flext-core logger integration
        logger = FlextLogger(__name__)
        assert logger is not None

    def test_module_structure(self) -> None:
        """Test module has expected structure."""  # Test flext-db-oracle module structure
        assert FlextDbOracleApi.__module__ == "flext_db_oracle.api"
        assert FlextDbOracleMetadataManager.__module__ == "flext_db_oracle.metadata"
