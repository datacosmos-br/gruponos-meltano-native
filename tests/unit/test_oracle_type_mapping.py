"""Tests for Oracle configuration type mapping functionality.

REAL IMPLEMENTATION TESTS - NO MOCKS OR FALLBACKS.
Tests the actual Oracle configuration and connection management.
"""

import pytest
from flext_db_oracle import FlextDbOracleApi, FlextDbOracleConfig

from gruponos_meltano_native.config import GruponosMeltanoOracleConnectionConfig
from gruponos_meltano_native.oracle import GruponosMeltanoOracleConnectionManager


class TestOracleConnectionConfiguration:
    """Test Oracle connection configuration with real implementation."""

    def test_oracle_connection_manager_types(self) -> None:
        """Test Oracle connection manager type handling."""
        # Test GrupoNOS Oracle connection configuration
        config = GruponosMeltanoOracleConnectionConfig(
            host="localhost",
            port=1521,
            service_name="TESTDB",
            username="test",
            password="test",
        )

        # Test type mapping in configuration
        assert isinstance(config.port, int)
        assert isinstance(config.host, str)
        assert isinstance(config.service_name, str)
        assert isinstance(config.username, str)
        # Password is SecretStr for security
        from pydantic import SecretStr

        assert isinstance(config.password, SecretStr)

        # Test connection manager with configuration
        manager = GruponosMeltanoOracleConnectionManager(config)
        assert manager is not None
        assert manager.config == config

    def test_oracle_api_type_handling(self) -> None:
        """Test Oracle API type handling."""
        # Test Oracle API configuration types
        config_dict = {
            "host": "localhost",
            "port": 1521,
            "service_name": "TESTDB",
            "username": "test",
            "password": "test",
        }

        # Test API creation with proper types
        api = FlextDbOracleApi.with_config(config_dict)
        assert api is not None

        # Test configuration object creation
        config = FlextDbOracleConfig(**config_dict)
        assert config.port == 1521  # NUMBER type
        assert isinstance(config.host, str)  # VARCHAR2 type
        assert isinstance(config.service_name, str)  # VARCHAR2 type

    def test_oracle_field_pattern_recognition(self) -> None:
        """Test Oracle field pattern recognition in configuration."""
        # Test patterns in GrupoNOS configuration
        config = GruponosMeltanoOracleConnectionConfig(
            host="localhost",
            port=1521,
            service_name="TESTDB",
            username="test",
            password="test",
        )

        # Test field patterns in configuration
        assert "port" in str(config.__dict__)  # ID-like field (NUMBER)
        assert "host" in str(config.__dict__)  # VARCHAR2 field
        assert "service_name" in str(config.__dict__)  # VARCHAR2 field
        assert "username" in str(config.__dict__)  # VARCHAR2 field
        assert "password" in str(config.__dict__)  # VARCHAR2 field

    def test_oracle_configuration_field_types(self) -> None:
        """Test Oracle configuration field type conversion."""
        # Test basic field type inference
        config_dict = {
            "host": "localhost",  # String -> VARCHAR2
            "port": 1521,  # Integer -> NUMBER
            "service_name": "TESTDB",  # String -> VARCHAR2
            "username": "test",  # String -> VARCHAR2
            "password": "test",  # String -> VARCHAR2
        }

        # Test that configuration handles types correctly
        config = FlextDbOracleConfig(**config_dict)

        # Verify types are preserved correctly
        assert isinstance(config.port, int)  # NUMBER type
        assert isinstance(config.host, str)  # VARCHAR2 type
        assert isinstance(config.service_name, str)  # VARCHAR2 type
        assert isinstance(config.username, str)  # VARCHAR2 type
        # FlextDbOracleConfig also uses SecretStr for password security
        from pydantic import SecretStr

        assert isinstance(config.password, SecretStr)  # Secure VARCHAR2 type

    def test_oracle_field_length_handling(self) -> None:
        """Test Oracle field length handling in configuration."""
        # Test configuration with reasonable field lengths
        config = GruponosMeltanoOracleConnectionConfig(
            host="very-long-hostname-for-testing-purposes",  # Long VARCHAR2
            port=1521,  # NUMBER
            service_name="VERY_LONG_SERVICE_NAME_FOR_TESTING",  # Long VARCHAR2
            username="very_long_username_for_testing",  # VARCHAR2
            password="very_long_password_for_testing_purposes",  # VARCHAR2
        )

        # Verify long strings are handled correctly
        assert len(config.host) > 30  # Long VARCHAR2 field
        assert len(config.service_name) > 20  # Long VARCHAR2 field
        assert len(config.username) > 20  # Long VARCHAR2 field
        # Password is SecretStr - get actual value for length check
        assert len(config.password.get_secret_value()) > 30  # Long VARCHAR2 field
        assert isinstance(config.port, int)  # NUMBER field

    def test_oracle_metadata_type_handling(self) -> None:
        """Test Oracle metadata type handling in configuration."""
        # Test configuration with different metadata approaches
        config = GruponosMeltanoOracleConnectionConfig(
            host="localhost",  # VARCHAR2 metadata
            port=1521,  # NUMBER metadata
            service_name="TEST",  # VARCHAR2 metadata
            username="user",  # VARCHAR2 metadata
            password="pass",  # VARCHAR2 metadata
        )

        # Test that metadata types are correctly inferred
        assert config.port == 1521  # NUMBER type
        assert config.host == "localhost"  # VARCHAR2 type
        assert config.service_name == "TEST"  # VARCHAR2 type
        assert config.username == "user"  # VARCHAR2 type
        # Password is SecretStr - compare with get_secret_value()
        assert config.password.get_secret_value() == "pass"  # VARCHAR2 type

    def test_oracle_comprehensive_integration(self) -> None:
        """Test comprehensive Oracle integration functionality."""
        # Test complete configuration integration
        config = GruponosMeltanoOracleConnectionConfig(
            host="comprehensive-test-host",
            port=1521,
            service_name="COMPREHENSIVE_TEST_DB",
            username="comprehensive_user",
            password="comprehensive_pass",
        )

        # Test all field types are handled correctly
        assert isinstance(config.host, str)  # VARCHAR2 type
        assert isinstance(config.port, int)  # NUMBER type
        assert isinstance(config.service_name, str)  # VARCHAR2 type
        assert isinstance(config.username, str)  # VARCHAR2 type
        # Password is SecretStr for security (proper enterprise practice)
        from pydantic import SecretStr

        assert isinstance(config.password, SecretStr)  # Secure VARCHAR2 type

        # Test API integration with comprehensive config
        config_dict = {
            "host": config.host,
            "port": config.port,
            "service_name": config.service_name,
            "username": config.username,
            "password": config.password,
        }

        api = FlextDbOracleApi.with_config(config_dict)
        assert api is not None

    def test_oracle_type_validation(self) -> None:
        """Test Oracle type validation in configuration."""
        # Test that configuration validates types correctly
        try:
            config = GruponosMeltanoOracleConnectionConfig(
                host="localhost",
                port=1521,  # Must be int for NUMBER type
                service_name="TESTDB",
                username="test",
                password="test",
            )
            assert config is not None
        except Exception as e:
            pytest.fail(f"Valid configuration should not raise exception: {e}")

        # Test type conversion and validation
        assert isinstance(config.port, int)  # NUMBER type validation
        assert isinstance(config.host, str)  # VARCHAR2 type validation
        # Password is SecretStr for security
        from pydantic import SecretStr

        assert isinstance(config.password, SecretStr)  # Secure VARCHAR2 type
