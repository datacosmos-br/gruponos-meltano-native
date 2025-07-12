#!/usr/bin/env python3
"""Test tap discovery with proper configuration."""

import os
import sys
import json
from pathlib import Path

# Add tap to path
tap_path = Path("/home/marlonsc/flext/flext-tap-oracle-wms/src")
if str(tap_path) not in sys.path:
    sys.path.insert(0, str(tap_path))

# Load environment
from dotenv import load_dotenv
load_dotenv()

# Import tap
from flext_tap_oracle_wms.tap import TapOracleWMS

print("🧪 TESTING TAP-ORACLE-WMS DISCOVERY")
print("="*60)

# Check environment
env_vars = {
    "TAP_ORACLE_WMS_BASE_URL": os.getenv("TAP_ORACLE_WMS_BASE_URL"),
    "TAP_ORACLE_WMS_USERNAME": os.getenv("TAP_ORACLE_WMS_USERNAME"),
    "TAP_ORACLE_WMS_PASSWORD": os.getenv("TAP_ORACLE_WMS_PASSWORD")
}

print("\n📋 Environment Variables:")
for key, value in env_vars.items():
    if value:
        print(f"✅ {key} = {value[:20]}...")
    else:
        print(f"❌ {key} = NOT SET")

# Create tap instance
print("\n🔍 Testing Discovery...")
config = {
    "base_url": env_vars["TAP_ORACLE_WMS_BASE_URL"],
    "username": env_vars["TAP_ORACLE_WMS_USERNAME"],
    "password": env_vars["TAP_ORACLE_WMS_PASSWORD"],
    "auth_method": "basic",
    "request_timeout": 300,
    "use_metadata_only": True,
    "discovery_sample_size": 0
}

# Create tap and enable discovery mode
tap = TapOracleWMS(config=config)
tap.set_discovery_mode(enabled=True)

# Run discovery
try:
    streams = tap.discover_streams()
    print(f"\n✅ Discovery successful! Found {len(streams)} streams")
    
    # Show streams
    print("\n📊 Available Streams:")
    for stream in streams:
        print(f"  - {stream.name} ({len(stream.schema.get('properties', {}))} properties)")
        
    # Create catalog
    catalog = {
        "streams": [
            {
                "tap_stream_id": stream.name,
                "stream": stream.name,
                "schema": stream.schema,
                "metadata": [
                    {
                        "breadcrumb": [],
                        "metadata": {
                            "inclusion": "available",
                            "table-key-properties": ["id"],
                            "forced-replication-method": "INCREMENTAL",
                            "valid-replication-keys": ["mod_ts"]
                        }
                    }
                ]
            }
            for stream in streams
        ]
    }
    
    # Save catalog
    catalog_path = Path("catalog.json")
    with open(catalog_path, "w") as f:
        json.dump(catalog, f, indent=2)
    print(f"\n💾 Catalog saved to {catalog_path}")
    
except Exception as e:
    print(f"\n❌ Discovery failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n✨ Test completed successfully!")