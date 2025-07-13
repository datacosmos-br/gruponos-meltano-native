#!/usr/bin/env python3
"""Test and compare original vs enhanced connection managers."""

import os
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from flext_observability.logging import get_logger, setup_logging

# Import both implementations
from oracle.connection_manager import OracleConnectionManager as OriginalManager
from oracle.connection_manager import (
    create_connection_manager_from_env as create_original,
)
from oracle.connection_manager_enhanced import (
    OracleConnectionManager as EnhancedManager,
)
from oracle.connection_manager_enhanced import (
    create_connection_manager_from_env as create_enhanced,
)

logger = get_logger(__name__)


def test_connection_manager(manager_class, manager_name: str):
    """Test a connection manager implementation."""
    logger.info(f"\n{'=' * 60}")
    logger.info(f"Testing {manager_name}")
    logger.info(f"{'=' * 60}")

    try:
        # Create manager
        start_time = time.time()

        if "original" in manager_name.lower():
            manager = create_original()
        else:
            manager = create_enhanced()

        create_time = time.time() - start_time
        logger.info(f"Manager created in {create_time:.3f}s")

        # Test connection
        test_start = time.time()
        result = manager.test_connection()
        test_time = time.time() - test_start

        # Log results
        logger.info("\nConnection Test Results:")
        logger.info(f"  Success: {result.get('success', False)}")
        logger.info(f"  Protocol: {result.get('protocol_used', 'N/A')}")
        logger.info(f"  Oracle Version: {result.get('oracle_version', 'N/A')}")
        logger.info(f"  User: {result.get('current_user', 'N/A')}")
        logger.info(f"  Connection Time: {result.get('connection_time_ms', 'N/A')}ms")
        logger.info(f"  Total Test Time: {test_time:.3f}s")

        if "enhanced" in manager_name.lower():
            # Additional info for enhanced version
            logger.info(f"  Attempts: {result.get('attempts', 'N/A')}")
            logger.info(f"  Fallback Applied: {result.get('fallback_applied', 'N/A')}")

            # Get connection info
            conn_info = manager.get_connection_info()
            logger.info("\nConnection Info:")
            logger.info(f"  {conn_info}")

        # Test SQL execution (if connected)
        if result.get("success"):
            logger.info("\nTesting SQL execution...")

            # Simple query
            query_start = time.time()
            row = manager.fetch_one("SELECT SYSDATE FROM DUAL")
            query_time = time.time() - query_start

            if row:
                logger.info(f"  Current database time: {row[0]}")
                logger.info(f"  Query execution time: {query_time:.3f}s")

            # Test with parameters
            param_query = "SELECT :1 + :2 FROM DUAL"
            result = manager.fetch_one(param_query, [10, 20])
            if result:
                logger.info(f"  Parameter query result: {result[0]}")

        return result.get("success", False)

    except Exception as e:
        logger.exception(f"Error testing {manager_name}: {e}")
        return False


def simulate_connection_failure() -> None:
    """Simulate connection failure by using wrong credentials."""
    logger.info(f"\n{'=' * 60}")
    logger.info("Testing Connection Failure Handling")
    logger.info(f"{'=' * 60}")

    # Save original env vars
    original_env = {
        "host": os.getenv("FLEXT_TARGET_ORACLE_HOST"),
        "port": os.getenv("FLEXT_TARGET_ORACLE_PORT"),
    }

    try:
        # Set invalid host to trigger failure
        os.environ["FLEXT_TARGET_ORACLE_HOST"] = "invalid.host.local"
        os.environ["FLEXT_TARGET_ORACLE_PORT"] = "9999"

        # Test original
        logger.info("\nOriginal Manager - Failure Handling:")
        try:
            manager = create_original()
            result = manager.test_connection()
            logger.info(f"Result: {result}")
        except Exception as e:
            logger.exception(f"Failed as expected: {e}")

        # Test enhanced
        logger.info("\nEnhanced Manager - Failure Handling:")
        try:
            manager = create_enhanced()
            result = manager.test_connection()
            logger.info(f"Result: {result}")
        except Exception as e:
            logger.exception(f"Failed as expected: {e}")

    finally:
        # Restore env vars
        if original_env["host"]:
            os.environ["FLEXT_TARGET_ORACLE_HOST"] = original_env["host"]
        if original_env["port"]:
            os.environ["FLEXT_TARGET_ORACLE_PORT"] = original_env["port"]


def main() -> int:
    """Run comparison tests."""
    setup_logging(level="INFO")

    logger.info("Oracle Connection Manager Comparison Test")
    logger.info("========================================\n")

    # Check if we have required env vars
    required_vars = [
        "FLEXT_TARGET_ORACLE_HOST",
        "FLEXT_TARGET_ORACLE_SERVICE_NAME",
        "FLEXT_TARGET_ORACLE_USERNAME",
        "FLEXT_TARGET_ORACLE_PASSWORD",
    ]

    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        logger.error(f"Missing required environment variables: {missing}")
        logger.info("\nPlease set the following environment variables:")
        for var in required_vars:
            logger.info(f"  export {var}=<value>")
        return 1

    # Test both implementations
    original_success = test_connection_manager(
        OriginalManager, "Original Connection Manager",
    )
    enhanced_success = test_connection_manager(
        EnhancedManager, "Enhanced Connection Manager (FLEXT)",
    )

    # Test failure handling
    simulate_connection_failure()

    # Summary
    logger.info(f"\n{'=' * 60}")
    logger.info("SUMMARY")
    logger.info(f"{'=' * 60}")
    logger.info(
        f"Original Manager: {'✅ SUCCESS' if original_success else '❌ FAILED'}",
    )
    logger.info(
        f"Enhanced Manager: {'✅ SUCCESS' if enhanced_success else '❌ FAILED'}",
    )

    if enhanced_success:
        logger.info("\n✅ Enhanced manager with FLEXT-DB-Oracle is working correctly!")
        logger.info("   It provides the same interface with additional features:")
        logger.info("   - Connection pooling support")
        logger.info("   - Built-in retry logic")
        logger.info("   - Automatic TCPS->TCP fallback")
        logger.info("   - Enhanced monitoring and logging")

    return 0 if (original_success or enhanced_success) else 1


if __name__ == "__main__":
    sys.exit(main())
