#!/usr/bin/env python3
"""Test tap directly without meltano."""

import subprocess
import os
import json
from pathlib import Path

# Load .env
from dotenv import load_dotenv
load_dotenv()

print("🧪 TESTING TAP-ORACLE-WMS DIRECTLY")
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

# Test discovery
print("\n🔍 Testing Discovery...")
cmd = ["tap-oracle-wms", "--discover"]
env = os.environ.copy()

print(f"Running: {' '.join(cmd)}")
result = subprocess.run(cmd, env=env, capture_output=True, text=True)

if result.returncode != 0:
    print(f"❌ Discovery failed: {result.returncode}")
    print(f"STDERR:\n{result.stderr}")
    exit(1)

# Parse catalog
try:
    catalog = json.loads(result.stdout)
    print(f"✅ Discovery successful! Found {len(catalog.get('streams', []))} streams")
    
    # Show streams
    print("\n📊 Available Streams:")
    for stream in catalog.get('streams', []):
        tap_stream_id = stream.get('tap_stream_id', 'unknown')
        schema = stream.get('schema', {})
        properties = schema.get('properties', {})
        print(f"  - {tap_stream_id} ({len(properties)} properties)")
        
    # Save catalog
    catalog_path = Path("catalog.json")
    with open(catalog_path, "w") as f:
        json.dump(catalog, f, indent=2)
    print(f"\n💾 Catalog saved to {catalog_path}")
    
except json.JSONDecodeError as e:
    print(f"❌ Failed to parse catalog: {e}")
    print(f"Output:\n{result.stdout[:1000]}")
    exit(1)

print("\n✨ Test completed successfully!")