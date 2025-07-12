"""Professional Oracle Connection Manager.

Handles SSL/TCPS connections with proper error handling and fallbacks.
"""

from __future__ import annotations

import contextlib
import os
import time
from dataclasses import dataclass
from typing import Any

import oracledb
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class OracleConnectionConfig:
    """Configuration for Oracle database connections."""

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
    """Professional Oracle connection manager with SSL handling."""
    def __init__(self, config: OracleConnectionConfig) -> None:
        self.config = config
        self._connection = None
        self._connection_attempts = 0
    def connect(self) -> oracledb.Connection:
        for attempt in range(1, self.config.retry_attempts + 1):
            try:
                logger.info(
                    "Attempting Oracle connection",
                    attempt=attempt,
                    max_attempts=self.config.retry_attempts,
                )

                if self.config.protocol.lower() == "tcps":
                    return self._connect_tcps()
                return self._connect_tcp()

            except Exception as e:
                logger.warning(
                    "Connection attempt failed",
                    attempt=attempt,
                    error=str(e),
                )

                if attempt == self.config.retry_attempts:
                    # Last attempt - try fallback
                    if self.config.protocol.lower() == "tcps":
                        logger.info("Attempting fallback to TCP connection")
                        try:
                            return self._connect_tcp_fallback()
                        except Exception as fallback_error:
                            logger.exception("Fallback connection also failed")
                            msg = (
                                f"Could not establish Oracle connection after "
                                f"{self.config.retry_attempts} attempts. "
                                f"Last error {e}, Fallback error: {fallback_error}"
                            )
                            raise ConnectionError(msg) from e
                    else:
                        msg = (
                            f"Could not establish Oracle connection after "
                            f"{self.config.retry_attempts} attempts. "
                            f"Last error: {e}"
                        )
                        raise ConnectionError(msg) from e

                # Wait before retry
                time.sleep(self.config.retry_delay)

        msg = "Connection attempts exhausted"
        raise ConnectionError(msg) from None

    def _connect_tcps(self) -> oracledb.Connection:
        dsn = (
            f"(DESCRIPTION="
            f"(ADDRESS=(PROTOCOL=TCPS)(HOST={self.config.host})"
            f"(PORT={self.config.port}))"
            f"(CONNECT_DATA=(SERVICE_NAME={self.config.service_name}))"
            f")"
        )

        logger.debug("Connecting with TCPS DSN", dsn=dsn)

        connection_params = {
            "user": self.config.username,
            "password": self.config.password,
            "dsn": dsn,
            "ssl_server_dn_match": self.config.ssl_server_dn_match,
        }

        # Add timeout if supported:
        with contextlib.suppress(Exception):
            connection_params["tcp_connect_timeout"] = self.config.connection_timeout

        return oracledb.connect(**connection_params)  # type: ignore[no-any-return]

    def _connect_tcp(self) -> oracledb.Connection:
        logger.debug("Connecting with standard TCP")

        return oracledb.connect(  # type: ignore[no-any-return]
            user=self.config.username,
            password=self.config.password,
            host=self.config.host,
            port=self.config.port,
            service_name=self.config.service_name,
        )

    def _connect_tcp_fallback(self) -> oracledb.Connection:
        logger.info("Using TCP fallback connection")

        # Try with modified port (common fallback)
        default_oracle_port = 1522
        fallback_oracle_port = 1521
        fallback_port = (
            fallback_oracle_port
            if self.config.port == default_oracle_port
            else self.config.port
        )

        dsn = (
            f"(DESCRIPTION="
            f"(ADDRESS=(PROTOCOL=TCP)(HOST={self.config.host})"
            f"(PORT={fallback_port}))"
            f"(CONNECT_DATA=(SERVICE_NAME={self.config.service_name}))"
            f")"
        )

        return oracledb.connect(  # type: ignore[no-any-return]
            user=self.config.username,
            password=self.config.password,
            dsn=dsn,
        )

    def test_connection(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "success": False,
            "protocol_used": None,
            "oracle_version": None,
            "current_user": None,
            "connection_time_ms": None,
            "error": None,
        }

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

    protocol = os.getenv("FLEXT_TARGET_ORACLE_PROTOCOL", "tcps")
    ssl_dn_match_str = os.getenv("FLEXT_TARGET_ORACLE_SSL_DN_MATCH", "false")
    ssl_server_dn_match = ssl_dn_match_str.lower() == "true"

    config = OracleConnectionConfig(
        host=host,
        port=int(os.getenv("FLEXT_TARGET_ORACLE_PORT", "1522")),
        service_name=service_name,
        username=username,
        password=password,
        protocol=protocol,
        ssl_server_dn_match=ssl_server_dn_match,
        connection_timeout=int(os.getenv("FLEXT_TARGET_ORACLE_TIMEOUT", "60")),
        retry_attempts=int(os.getenv("FLEXT_TARGET_ORACLE_RETRIES", "3")),
        retry_delay=int(os.getenv("FLEXT_TARGET_ORACLE_RETRY_DELAY", "5")),
    )

    return OracleConnectionManager(config)


if __name__ == "__main__":
    # Test the connection manager
    manager = create_connection_manager_from_env()
    result = manager.test_connection()

    logger.info("Oracle Connection Test Results:")
    logger.info("=" * 40)
    for key, value in result.items():
        logger.info(f"{key}: {value}")
