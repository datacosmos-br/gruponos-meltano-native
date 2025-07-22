"""Enhanced Oracle Connection Manager using FLEXT-DB-Oracle.

This module provides a backward-compatible interface while leveraging
the enterprise features of flext-db-oracle with resilient connections.
"""

from __future__ import annotations

import os
from typing import Any

from flext_db_oracle.connection import (
    ConnectionConfig,
    ResilientOracleConnection,
)
from flext_observability.logging import get_logger, setup_logging
from pydantic import SecretStr

# Import the REAL config class from our config module - NO DUPLICATION!
from gruponos_meltano_native.config import OracleConnectionConfig

logger = get_logger(__name__)


class OracleConnectionManager:
    """Professional Oracle connection manager with FLEXT enterprise features.

    This class maintains backward compatibility with the original interface
    while providing enhanced features from flext-db-oracle:
    - Connection pooling
    - Automatic retry with configurable attempts
    - TCPS to TCP fallback
    - Port fallback (1522 -> 1521)
    - Health monitoring
    """

    def __init__(self, config: OracleConnectionConfig) -> None:
        """Initialize Oracle connection manager with configuration.

        Args:
            config: Oracle connection configuration with host, port, credentials.

        """
        self.config = config

        # Convert to FLEXT ConnectionConfig
        self._flext_config = ConnectionConfig(
            host=config.host,
            port=config.port,
            service_name=config.service_name,
            username=config.username,
            password=SecretStr(config.password),
            protocol=config.protocol,
            ssl_server_dn_match=config.ssl_server_dn_match,
            # Note: flext-db-oracle uses 'timeout' not 'connection_timeout'
            timeout=config.connection_timeout,
            # Required fields with reasonable defaults
            sid=None,  # Using service_name instead
            pool_min=1,
            pool_max=getattr(config, "connection_pool_size", 5),
            pool_increment=1,
            encoding="UTF-8",
            ssl_cert_path=None,
            ssl_key_path=None,
        )

        # Create resilient connection with retry and fallback
        self._connection = ResilientOracleConnection(
            config=self._flext_config,
            retry_attempts=config.retry_attempts,
            retry_delay=config.retry_delay,
            enable_fallback=True,  # Always enable fallback for compatibility
        )

        self._connection_attempts = 0

        logger.info(
            "Initialized enhanced Oracle connection manager - "
            "host=%s, port=%s, service_name=%s, "
            "protocol=%s, retry_attempts=%s",
            config.host,
            config.port,
            config.service_name,
            config.protocol,
            config.retry_attempts,
        )

    def connect(self) -> object:
        """Connect to Oracle database with enterprise resilience.

        Returns:
            The underlying connection object for backward compatibility.

        Raises:
            ConnectionError: If connection cannot be established after all retries.

        """
        logger.info("Connecting to Oracle using enhanced FLEXT connection")

        # ResilientOracleConnection handles all retry logic internally
        self._connection.connect()

        # Store connection attempts for backward compatibility
        # Note: Accessing private member for backward compatibility only
        self._connection_attempts = getattr(
            self._connection,
            "connection_attempts",
            0,
        )

        # Return the underlying oracledb connection for compatibility
        # Note: Accessing private member for backward compatibility only
        return getattr(self._connection, "_connection", None)

    def test_connection(self) -> dict[str, Any]:
        """Test the connection and return detailed results.

        Returns:
            Dictionary with connection test results including:
            - success: bool
            - protocol_used: str
            - oracle_version: str
            - current_user: str
            - connection_time_ms: float
            - error: str (if failed)

        """
        # Use the enhanced test_connection_detailed from ResilientOracleConnection
        test_result = self._connection.test_connection_detailed()

        # Log the result
        if test_result["success"]:
            logger.info(
                "Connection test successful - "
                "oracle_version=%s, user=%s, "
                "time_ms=%s, attempts=%s, "
                "fallback=%s",
                test_result.get("oracle_version"),
                test_result.get("current_user"),
                test_result.get("connection_time_ms"),
                test_result.get("attempts"),
                test_result.get("fallback_applied"),
            )
        else:
            logger.error(
                "Connection test failed - error=%s, attempts=%s",
                test_result.get("error"),
                test_result.get("attempts"),
            )

        return test_result

    def close(self) -> None:
        """Close the connection."""
        if self._connection and self._connection.is_connected:
            self._connection.disconnect()
            logger.info("Connection closed")

    def execute(self, sql: str, parameters: dict[str, Any] | None = None) -> object:
        """Execute SQL statement using FLEXT connection.

        Args:
            sql: SQL statement to execute
            parameters: Optional parameters for the SQL statement

        Returns:
            Query results or row count

        """
        if not self._connection.is_connected:
            self.connect()

        return self._connection.execute(sql, parameters)

    def fetch_one(
        self,
        sql: str,
        parameters: dict[str, Any] | None = None,
    ) -> tuple[Any, ...] | None:
        """Fetch one row from SQL query.

        Args:
            sql: SQL query to execute
            parameters: Optional parameters for the query

        Returns:
            Single row result or None

        """
        if not self._connection.is_connected:
            self.connect()

        return self._connection.fetch_one(sql, parameters)

    def fetch_all(
        self,
        sql: str,
        parameters: dict[str, Any] | None = None,
    ) -> list[Any]:
        """Fetch all rows from SQL query.

        Args:
            sql: SQL query to execute
            parameters: Optional parameters for the query

        Returns:
            List of row results

        """
        if not self._connection.is_connected:
            self.connect()

        return self._connection.fetch_all(sql, parameters)

    @property
    def is_connected(self) -> bool:
        """Check if connected to database."""
        return self._connection.is_connected

    def get_connection_info(self) -> dict[str, Any]:
        """Get detailed connection information.

        Returns:
            Dictionary with connection details and statistics

        """
        return self._connection.get_connection_info()


def _validate_required_env_var(var_name: str) -> str:
    """Validate required environment variable exists."""
    env_value = os.getenv(var_name)
    if not env_value:
        msg = f"Missing {var_name} environment variable"
        raise ValueError(msg)
    return env_value


def _get_env_config() -> dict[str, str | int | bool]:
    """Get environment configuration with validation."""
    # Required variables

    config: dict[str, str | int | bool] = {}
    # Map environment variable names to config keys
    var_mapping = {
        "FLEXT_TARGET_ORACLE_HOST": "host",
        "FLEXT_TARGET_ORACLE_SERVICE_NAME": "service_name",
        "FLEXT_TARGET_ORACLE_USERNAME": "username",
        "FLEXT_TARGET_ORACLE_PASSWORD": "password",
        "FLEXT_TARGET_ORACLE_PROTOCOL": "protocol",
    }
    for var, key in var_mapping.items():
        config[key] = _validate_required_env_var(var)

    # Optional variables with defaults
    config["port"] = int(os.getenv("FLEXT_TARGET_ORACLE_PORT", "1522"))
    config["connection_timeout"] = int(os.getenv("FLEXT_TARGET_ORACLE_TIMEOUT", "60"))
    config["retry_attempts"] = int(os.getenv("FLEXT_TARGET_ORACLE_RETRIES", "3"))
    config["retry_delay"] = int(os.getenv("FLEXT_TARGET_ORACLE_RETRY_DELAY", "5"))

    ssl_dn_match_str = os.getenv("FLEXT_TARGET_ORACLE_SSL_DN_MATCH", "false")
    config["ssl_server_dn_match"] = ssl_dn_match_str.lower() == "true"

    return config


def create_connection_manager_from_env() -> OracleConnectionManager:
    """Create connection manager from environment variables.

    This function maintains backward compatibility with existing
    environment variable names while using the enhanced connection.
    """
    env_config = _get_env_config()
    # Convert types for OracleConnectionConfig constructor
    config = OracleConnectionConfig(
        host=str(env_config["host"]),
        port=int(env_config["port"]),
        service_name=str(env_config["service_name"]),
        username=str(env_config["username"]),
        password=str(env_config["password"]),
        protocol=str(env_config["protocol"]),
        connection_timeout=int(env_config["connection_timeout"]),
        retry_attempts=int(env_config["retry_attempts"]),
        retry_delay=int(env_config["retry_delay"]),
        ssl_server_dn_match=bool(env_config["ssl_server_dn_match"]),
    )

    logger.info(
        "Creating enhanced Oracle connection manager from environment - "
        "host=%s, port=%s, service_name=%s, "
        "protocol=%s",
        config.host,
        config.port,
        config.service_name,
        config.protocol,
    )

    return OracleConnectionManager(config)


# Backward compatibility - expose the same interface as original
if __name__ == "__main__":
    # Test the connection manager
    # Setup FLEXT logging
    setup_logging()

    manager = create_connection_manager_from_env()
    result = manager.test_connection()

    logger.info("Oracle Connection Test Results:")
    logger.info("=" * 40)
    for key, result_value in result.items():
        logger.info("%s: %s", key, result_value)
