"""Discover and save WMS schemas to JSON file for table creation.

This prevents fallback schemas from being used.
"""

from __future__ import annotations

import logging
import os
import sys

from dotenv import load_dotenv

# 🚨 ARCHITECTURAL VIOLATION FIXED: Direct import REMOVED
# Level 6 projects cannot directly import other Level 6 projects
# Use Meltano plugin discovery instead of direct tap imports

# Setup logger
logger = logging.getLogger(__name__)


def discover_schemas() -> bool:
    """Discover WMS schemas from API and save to JSON file.

    Returns:
        True if schemas were discovered and saved successfully, False otherwise.

    """
    # Load environment variables
    load_dotenv()

    # Create tap configuration
    config: dict[str, object] = {
        "base_url": os.environ.get("TAP_ORACLE_WMS_BASE_URL"),
        "username": os.environ.get("TAP_ORACLE_WMS_USERNAME"),
        "password": os.environ.get("TAP_ORACLE_WMS_PASSWORD"),
        "entities": ["allocation", "order_hdr", "order_dtl"],
        "force_full_table": True,
        "page_size": int(os.getenv("WMS_PAGE_SIZE", "100")),
    }

    # Check if credentials are available:
    if not all([config["base_url"], config["username"], config["password"]]):
        logger.error("❌ Missing WMS credentials!")
        logger.error("Required environment variables:")
        logger.error("  - TAP_ORACLE_WMS_BASE_URL")
        logger.error("  - TAP_ORACLE_WMS_USERNAME")
        logger.error("  - TAP_ORACLE_WMS_PASSWORD")
        return False

    logger.info("🔍 Discovering schemas from WMS API...")
    logger.info("   URL: %s", config["base_url"])
    logger.info("   User: %s", config["username"])

    try:
        # 🚨 ARCHITECTURAL COMPLIANCE: Use Meltano for plugin discovery
        # Cannot directly instantiate TapOracleWMS (architectural violation)
        logger.error("❌ Schema discovery requires Meltano plugin system")
        logger.error("Use 'meltano discover tap-oracle-wms' instead")
        return False
    except Exception:
        logger.exception("❌ Error discovering schemas")
        return False

    return True


if __name__ == "__main__":
    SUCCESS = discover_schemas()
    sys.exit(0 if SUCCESS else 1)
