#!/usr/bin/env python3
"""Discover and save WMS schemas to JSON file for table creation.
This prevents fallback schemas from being used.
"""

import json
import os
import sys

# Add tap path to Python path
sys.path.insert(0, "/home/marlonsc/flext/flext-tap-oracle-wms/src")

from tap_oracle_wms.tap import TapOracleWMS


def discover_schemas() -> bool:
    """Discover schemas from WMS API and save to file."""
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    # Create tap configuration
    config = {
        "base_url": os.environ.get("TAP_ORACLE_WMS_BASE_URL"),
        "username": os.environ.get("TAP_ORACLE_WMS_USERNAME"),
        "password": os.environ.get("TAP_ORACLE_WMS_PASSWORD"),
        "entities": ["allocation", "order_hdr", "order_dtl"],
        "force_full_table": True,
        "page_size": 1000,
    }

    # Check if credentials are available
    if not all([config["base_url"], config["username"], config["password"]]):
        print("❌ Missing WMS credentials!")
        print("Required environment variables:")
        print("  - TAP_ORACLE_WMS_BASE_URL")
        print("  - TAP_ORACLE_WMS_USERNAME")
        print("  - TAP_ORACLE_WMS_PASSWORD")
        return False

    print("🔍 Discovering schemas from WMS API...")
    print(f"   URL: {config['base_url']}")
    print(f"   User: {config['username']}")

    try:
        # Create tap instance
        tap = TapOracleWMS(config=config)

        # Discover schemas
        catalog = tap.discover_streams()
        schemas = {}

        for stream in catalog:
            schema = stream.schema if hasattr(stream.schema, "to_dict") else stream.schema
            schemas[stream.tap_stream_id] = schema
            prop_count = len(schema.get("properties", {})) if isinstance(schema, dict) else len(schema.properties)
            print(f"✅ Discovered {stream.tap_stream_id}: {prop_count} properties")

        # Save schemas to file
        schema_file = "sql/wms_schemas.json"
        os.makedirs("sql", exist_ok=True)

        with open(schema_file, "w") as f:
            json.dump(schemas, f, indent=2)

        print(f"\n✅ Schemas saved to {schema_file}")
        print("   Use this file with table_creator.py to ensure correct DDL generation")

        return True

    except Exception as e:
        print(f"❌ Error discovering schemas: {e}")
        return False

if __name__ == "__main__":
    success = discover_schemas()
    sys.exit(0 if success else 1)
