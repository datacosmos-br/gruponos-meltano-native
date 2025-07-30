#!/usr/bin/env python3
"""Test script to verify SSL certificate validation fix."""

import builtins
import contextlib
import os
import traceback

from gruponos_meltano_native.config import OracleConnectionConfig
from gruponos_meltano_native.oracle.connection_manager_enhanced import (
    OracleConnectionManager,
    create_connection_manager_from_env,
)


def test_ssl_connection() -> None:
    """Test the SSL connection with ssl_server_dn_match=False."""
    # Create config directly to test
    config: OracleConnectionConfig = OracleConnectionConfig(
        host="10.93.10.114",
        port=1522,
        service_name=os.getenv("FLEXT_TARGET_ORACLE_SERVICE_NAME", "ORCL"),
        username=os.getenv("FLEXT_TARGET_ORACLE_USERNAME", "test"),
        password=os.getenv("FLEXT_TARGET_ORACLE_PASSWORD", "test"),
        protocol="tcps",
        ssl_server_dn_match=False,  # This should disable certificate name validation
        connection_timeout=60,
        retry_attempts=3,
        retry_delay=5,
    )

    # Create connection manager
    manager = OracleConnectionManager(config)

    try:
        # Test the connection
        result = manager.test_connection()

        for _key, _value in result.items():
            pass

        if result["success"]:
            pass

    except (RuntimeError, ValueError, TypeError):

        traceback.print_exc()
    finally:
        # Clean up
        with contextlib.suppress(builtins.BaseException):
            manager.close()


def test_env_connection() -> None:
    """Test connection using environment variables."""
    try:
        manager = create_connection_manager_from_env()
        result = manager.test_connection()

        for _key, _value in result.items():
            pass

        if result["success"]:
            pass

    except (RuntimeError, ValueError, TypeError):

        traceback.print_exc()


if __name__ == "__main__":

    # Test direct configuration
    test_ssl_connection()

    # Test environment-based configuration if env vars are set
    if os.getenv("FLEXT_TARGET_ORACLE_HOST"):
        test_env_connection()
