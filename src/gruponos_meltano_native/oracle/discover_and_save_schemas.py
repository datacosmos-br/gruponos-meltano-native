"""Discover and save WMS schemas to JSON file for table creation.

This prevents fallback schemas from being used.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Use centralized logger from flext-observability - ELIMINATE DUPLICATION
from flext_observability.logging import get_logger

# Add tap path to Python path
sys.path.insert(0, "/home/marlonsc/flext/flext-tap-oracle-wms/src")

from flext_tap_oracle_wms.tap import TapOracleWMS

# Setup logger
logger = get_logger(__name__)


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
        # Create tap instance
        tap = TapOracleWMS(config=config)

        # Discover schemas
        catalog = tap.discover_streams()
        schemas = {}

        for stream in catalog:
            schema = stream.schema
            schemas[stream.tap_stream_id] = schema
            prop_count = (
                len(schema.get("properties", {}))
                if isinstance(schema, dict)
                else len(schema.properties)
            )
            logger.info(
                "✅ Discovered %s: %d properties",
                stream.tap_stream_id,
                prop_count,
            )

        # Save schemas to file
        schema_file = "sql/wms_schemas.json"
        Path("sql").mkdir(exist_ok=True)

        with Path(schema_file).open("w", encoding="utf-8") as f:
            json.dump(schemas, f, indent=2)

        logger.info("\n✅ Schemas saved to %s", schema_file)
        logger.info(
            "   Use this file with table_creator.py to ensure correct DDL generation",
        )
    except Exception:
        logger.exception("❌ Error discovering schemas")
        return False

    return True


if __name__ == "__main__":
    SUCCESS = discover_schemas()
    sys.exit(0 if SUCCESS else 1)
