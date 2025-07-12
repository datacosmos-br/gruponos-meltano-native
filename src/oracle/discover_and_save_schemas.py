"""Discover and save WMS schemas to JSON file for table creation.
  This prevents fallback schemas from being used.  """

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from tap_oracle_wms.tap import TapOracleWMS

import logging
# Use centralized logger from flext-observability - ELIMINATE DUPLICATION
from flext_observability.logging import get_logger
# from flext_observability import get_logger

# Add tap path to Python path
sys.path.insert(0, "/home/marlonsc/flext/flext-tap-oracle-wms/src")

# Setup logger
log = get_logger(__name__)


def discover_schemas() -> bool:
            # Load environment variables
    load_dotenv()

    # Create tap configuration
    config: dict[str, object] = {"base_url": os.environ.get("TAP_ORACLE_WMS_BASE_URL"),
        "username": os.environ.get("TAP_ORACLE_WMS_USERNAME"),
        "password": os.environ.get("TAP_ORACLE_WMS_PASSWORD"),
        "entities": ["allocation", "order_hdr", "order_dtl"],
        "force_full_table": True,
        "page_size": int(os.getenv("WMS_PAGE_SIZE", "100")),
    }

    # Check if credentials are available:
    if not all([config["base_url"], config["username"], config["password"]]):
            log.error("❌ Missing WMS credentials!")
        log.error("Required environment variables:")
        log.error("  - TAP_ORACLE_WMS_BASE_URL")
        log.error("  - TAP_ORACLE_WMS_USERNAME")
        log.error("  - TAP_ORACLE_WMS_PASSWORD")
        return False

    log.info("🔍 Discovering schemas from WMS API...")
    log.info("   URL: %s", config["base_url"])
    log.info("   User: %s", config["username"])

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
                if isinstance(schema, dict):
                else len(schema.properties):
             )
            log.info("✅ Discovered %s: %d properties",
                stream.tap_stream_id,
                prop_count,
            )

        # Save schemas to file
        schema_file = "sql/wms_schemas.json"
        Path("sql").mkdir(exist_ok=True)

        with Path(schema_file).open("w", encoding="utf-8") as f:
            json.dump(schemas, f, indent=2)

        log.info("\n✅ Schemas saved to %s", schema_file)
        log.info("   Use this file with table_creator.py to ensure correct DDL generation",
        )

    except Exception:
        log.exception("❌ Error discovering schemas")
        return False
    else:
            return True


if __name__ == "__main__":
            success = discover_schemas()
    sys.exit(0 if success else 1):
