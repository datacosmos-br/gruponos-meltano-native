"""Enhanced Oracle Connection Manager using FLEXT-DB-Oracle.

This module provides a backward-compatible interface while leveraging
the enterprise features of flext-db-oracle with resilient connections.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from flext_observability.logging import get_logger
from flext_db_oracle.connection import (
    ConnectionConfig,
    ResilientOracleConnection,
)

logger = get_logger(__name__)


@dataclass
class OracleConnectionConfig:
    """Configuration for Oracle database connections - backward compatible."""

    host: str
    port: int = 1522
    service_name: str = ""
    username: str = ""
    password: str = ""
    protocol: str = "tcps"
    ssl_server_dn_match: bool = False
    connection_timeout: int = 60
    retry_attempts: int = 3
    retry_delay: int = 5


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
        self.config = config
        
        # Convert to FLEXT ConnectionConfig
        self._flext_config = ConnectionConfig(
            host=config.host,
            port=config.port,
            service_name=config.service_name,
            username=config.username,
            password=config.password,
            protocol=config.protocol,
            ssl_server_dn_match=config.ssl_server_dn_match,
            # Note: flext-db-oracle uses 'timeout' not 'connection_timeout'
            timeout=config.connection_timeout,
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
            "Initialized enhanced Oracle connection manager",
            host=config.host,
            port=config.port,
            service_name=config.service_name,
            protocol=config.protocol,
            retry_attempts=config.retry_attempts,
        )

    def connect(self) -> Any:
        """Connect to Oracle database with enterprise resilience.
        
        Returns:
            The underlying connection object for backward compatibility.
            
        Raises:
            ConnectionError: If connection cannot be established after all retries.
        """
        logger.info("Connecting to Oracle using enhanced FLEXT connection")
        
        # ResilientOracleConnection handles all retry logic internally
        self._connection.connect()
        
        # Get the actual connection attempts from the resilient connection
        self._connection_attempts = self._connection._connection_attempts
        
        # Return the underlying oracledb connection for compatibility
        return self._connection._connection

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
        # Use the enhanced test_connection from ResilientOracleConnection
        result = self._connection.test_connection()
        
        # Log the result
        if result["success"]:
            logger.info(
                "Connection test successful",
                oracle_version=result.get("oracle_version"),
                user=result.get("current_user"),
                time_ms=result.get("connection_time_ms"),
                attempts=result.get("attempts"),
                fallback=result.get("fallback_applied"),
            )
        else:
            logger.error(
                "Connection test failed",
                error=result.get("error"),
                attempts=result.get("attempts"),
            )
        
        return result

    def close(self) -> None:
        """Close the connection."""
        if self._connection and self._connection.is_connected:
            self._connection.disconnect()
            logger.info("Connection closed")

    def execute(self, sql: str, parameters: dict[str, Any] | None = None) -> Any:
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

    def fetch_one(self, sql: str, parameters: dict[str, Any] | None = None) -> Any:
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

    def fetch_all(self, sql: str, parameters: dict[str, Any] | None = None) -> list[Any]:
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


def create_connection_manager_from_env() -> OracleConnectionManager:
    """Create connection manager from environment variables.
    
    This function maintains backward compatibility with existing
    environment variable names while using the enhanced connection.
    """
    # Get required environment variables with validation
    host = os.getenv("FLEXT_TARGET_ORACLE_HOST")
    service_name = os.getenv("FLEXT_TARGET_ORACLE_SERVICE_NAME")
    username = os.getenv("FLEXT_TARGET_ORACLE_USERNAME")
    password = os.getenv("FLEXT_TARGET_ORACLE_PASSWORD")

    if not host:
        msg = "Missing FLEXT_TARGET_ORACLE_HOST environment variable"
        raise ValueError(msg)
    if not service_name:
        msg = "Missing FLEXT_TARGET_ORACLE_SERVICE_NAME environment variable"
        raise ValueError(msg)
    if not username:
        msg = "Missing FLEXT_TARGET_ORACLE_USERNAME environment variable"
        raise ValueError(msg)
    if not password:
        msg = "Missing FLEXT_TARGET_ORACLE_PASSWORD environment variable"
        raise ValueError(msg)

    protocol = os.getenv("FLEXT_TARGET_ORACLE_PROTOCOL")
    if not protocol:
        msg = "Missing FLEXT_TARGET_ORACLE_PROTOCOL environment variable"
        raise ValueError(msg)

    ssl_dn_match_str = os.getenv("FLEXT_TARGET_ORACLE_SSL_DN_MATCH")
    if not ssl_dn_match_str:
        msg = "Missing FLEXT_TARGET_ORACLE_SSL_DN_MATCH environment variable"
        raise ValueError(msg)
    ssl_server_dn_match = ssl_dn_match_str.lower() == "true"

    port_str = os.getenv("FLEXT_TARGET_ORACLE_PORT")
    if not port_str:
        msg = "Missing FLEXT_TARGET_ORACLE_PORT environment variable"
        raise ValueError(msg)

    timeout_str = os.getenv("FLEXT_TARGET_ORACLE_TIMEOUT")
    if not timeout_str:
        msg = "Missing FLEXT_TARGET_ORACLE_TIMEOUT environment variable"
        raise ValueError(msg)

    retries_str = os.getenv("FLEXT_TARGET_ORACLE_RETRIES")
    if not retries_str:
        msg = "Missing FLEXT_TARGET_ORACLE_RETRIES environment variable"
        raise ValueError(msg)

    retry_delay_str = os.getenv("FLEXT_TARGET_ORACLE_RETRY_DELAY")
    if not retry_delay_str:
        msg = "Missing FLEXT_TARGET_ORACLE_RETRY_DELAY environment variable"
        raise ValueError(msg)

    config = OracleConnectionConfig(
        host=host,
        port=int(port_str),
        service_name=service_name,
        username=username,
        password=password,
        protocol=protocol,
        ssl_server_dn_match=ssl_server_dn_match,
        connection_timeout=int(timeout_str),
        retry_attempts=int(retries_str),
        retry_delay=int(retry_delay_str),
    )

    logger.info(
        "Creating enhanced Oracle connection manager from environment",
        host=host,
        port=config.port,
        service_name=service_name,
        protocol=protocol,
    )

    return OracleConnectionManager(config)


# Backward compatibility - expose the same interface as original
if __name__ == "__main__":
    # Test the connection manager
    from flext_observability.logging import setup_logging
    
    # Setup FLEXT logging
    setup_logging(level="INFO")
    
    manager = create_connection_manager_from_env()
    result = manager.test_connection()

    logger.info("Oracle Connection Test Results:")
    logger.info("=" * 40)
    for key, value in result.items():
        logger.info(f"{key}: {value}")