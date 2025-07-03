#!/usr/bin/env python3
"""Professional Oracle Connection Manager
Handles SSL/TCPS connections with proper error handling and fallbacks
"""

import logging
import os
from dataclasses import dataclass
from typing import Any

import oracledb

logger = logging.getLogger(__name__)


@dataclass
class OracleConnectionConfig:
    """Configuration for Oracle database connections."""
    host: str
    port: int
    service_name: str
    username: str
    password: str
    protocol: str = "tcps"
    ssl_server_dn_match: bool = False
    connection_timeout: int = 60
    retry_attempts: int = 3
    retry_delay: int = 5


class OracleConnectionManager:
    """Professional Oracle connection manager with SSL handling."""

    def __init__(self, config: OracleConnectionConfig):
        """Initialize connection manager with configuration."""
        self.config = config
        self._connection = None
        self._connection_attempts = 0

    def connect(self) -> oracledb.Connection:
        """Establish Oracle connection with professional error handling.
        
        Returns:
            Active Oracle connection
            
        Raises:
            ConnectionError: If connection cannot be established
        """
        for attempt in range(1, self.config.retry_attempts + 1):
            try:
                logger.info(f"Attempting Oracle connection (attempt {attempt}/{self.config.retry_attempts})")

                if self.config.protocol.lower() == "tcps":
                    return self._connect_tcps()
                return self._connect_tcp()

            except Exception as e:
                logger.warning(f"Connection attempt {attempt} failed: {e}")

                if attempt == self.config.retry_attempts:
                    # Last attempt - try fallback
                    if self.config.protocol.lower() == "tcps":
                        logger.info("Attempting fallback to TCP connection")
                        try:
                            return self._connect_tcp_fallback()
                        except Exception as fallback_error:
                            logger.error(f"Fallback connection also failed: {fallback_error}")
                            raise ConnectionError(
                                f"Could not establish Oracle connection after {self.config.retry_attempts} attempts. "
                                f"Last error: {e}, Fallback error: {fallback_error}",
                            )
                    else:
                        raise ConnectionError(
                            f"Could not establish Oracle connection after {self.config.retry_attempts} attempts. "
                            f"Last error: {e}",
                        )

                # Wait before retry
                import time
                time.sleep(self.config.retry_delay)

        raise ConnectionError("Connection attempts exhausted")

    def _connect_tcps(self) -> oracledb.Connection:
        """Connect using TCPS (SSL) protocol."""
        dsn = (
            f"(DESCRIPTION="
            f"(ADDRESS=(PROTOCOL=TCPS)(HOST={self.config.host})(PORT={self.config.port}))"
            f"(CONNECT_DATA=(SERVICE_NAME={self.config.service_name}))"
            f")"
        )

        logger.debug(f"Connecting with TCPS DSN: {dsn}")

        connection_params = {
            "user": self.config.username,
            "password": self.config.password,
            "dsn": dsn,
            "ssl_server_dn_match": self.config.ssl_server_dn_match,
        }

        # Add timeout if supported
        try:
            connection_params["tcp_connect_timeout"] = float(self.config.connection_timeout)
        except:
            pass  # Older oracledb versions may not support this

        return oracledb.connect(**connection_params)  # type: ignore[no-any-return]

    def _connect_tcp(self) -> oracledb.Connection:
        """Connect using standard TCP protocol."""
        logger.debug("Connecting with standard TCP")

        return oracledb.connect(  # type: ignore[no-any-return]
            user=self.config.username,
            password=self.config.password,
            host=self.config.host,
            port=self.config.port,
            service_name=self.config.service_name,
        )

    def _connect_tcp_fallback(self) -> oracledb.Connection:
        """Fallback TCP connection when TCPS fails."""
        logger.info("Using TCP fallback connection")

        # Try with modified port (common fallback)
        fallback_port = 1521 if self.config.port == 1522 else self.config.port

        dsn = (
            f"(DESCRIPTION="
            f"(ADDRESS=(PROTOCOL=TCP)(HOST={self.config.host})(PORT={fallback_port}))"
            f"(CONNECT_DATA=(SERVICE_NAME={self.config.service_name}))"
            f")"
        )

        return oracledb.connect(  # type: ignore[no-any-return]
            user=self.config.username,
            password=self.config.password,
            dsn=dsn,
        )

    def test_connection(self) -> dict[str, Any]:
        """Test Oracle connection and return diagnostic information.
        
        Returns:
            Dictionary with connection test results
        """
        result: dict[str, Any] = {
            "success": False,
            "protocol_used": None,
            "oracle_version": None,
            "current_user": None,
            "connection_time_ms": None,
            "error": None,
        }

        import time
        start_time = time.time()

        try:
            conn = self.connect()
            connection_time = (time.time() - start_time) * 1000

            with conn.cursor() as cursor:
                # Get Oracle version
                cursor.execute("SELECT banner FROM v$version WHERE ROWNUM = 1")
                oracle_version = cursor.fetchone()[0]

                # Get current user
                cursor.execute("SELECT USER FROM DUAL")
                current_user = cursor.fetchone()[0]

            conn.close()

            result.update({
                "success": True,
                "protocol_used": self.config.protocol,
                "oracle_version": oracle_version,
                "current_user": current_user,
                "connection_time_ms": round(connection_time, 2),
            })

        except Exception as e:
            result["error"] = str(e)

        return result


def create_connection_manager_from_env() -> OracleConnectionManager:
    """Create connection manager from environment variables."""
    # Get required environment variables with validation
    host = os.getenv("FLEXT_TARGET_ORACLE_HOST")
    service_name = os.getenv("FLEXT_TARGET_ORACLE_SERVICE_NAME")
    username = os.getenv("FLEXT_TARGET_ORACLE_USERNAME")
    password = os.getenv("FLEXT_TARGET_ORACLE_PASSWORD")

    if not all([host, service_name, username, password]):
        raise ValueError("Missing required Oracle connection environment variables")

    config = OracleConnectionConfig(
        host=host,  # type: ignore[arg-type]
        port=int(os.getenv("FLEXT_TARGET_ORACLE_PORT", "1522")),
        service_name=service_name,  # type: ignore[arg-type]
        username=username,  # type: ignore[arg-type]
        password=password,  # type: ignore[arg-type]
        protocol=os.getenv("FLEXT_TARGET_ORACLE_PROTOCOL", "tcps"),
        ssl_server_dn_match=os.getenv("FLEXT_TARGET_ORACLE_SSL_DN_MATCH", "false").lower() == "true",
        connection_timeout=int(os.getenv("FLEXT_TARGET_ORACLE_TIMEOUT", "60")),
        retry_attempts=int(os.getenv("FLEXT_TARGET_ORACLE_RETRIES", 3)),
        retry_delay=int(os.getenv("FLEXT_TARGET_ORACLE_RETRY_DELAY", 5)),
    )

    return OracleConnectionManager(config)


if __name__ == "__main__":
    # Test the connection manager
    manager = create_connection_manager_from_env()
    result = manager.test_connection()

    print("Oracle Connection Test Results:")
    print("=" * 40)
    for key, value in result.items():
        print(f"{key}: {value}")
