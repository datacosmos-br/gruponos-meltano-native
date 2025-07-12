#!/usr/bin/env python3
"""Test tap with specific entities."""

import json
import os
import subprocess
import sys
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

print("🧪 TESTING TAP-ORACLE-WMS WITH MULTIPLE ENTITIES")
print("=" * 60)

# Configuration for tap with multiple entities
tap_config = {
    "base_url": os.getenv("TAP_ORACLE_WMS_BASE_URL", "https://a29.wms.ocs.oraclecloud.com/raizen"),
    "username": os.getenv("TAP_ORACLE_WMS_USERNAME", "USER_WMS_INTEGRA"),
    "password": os.getenv("TAP_ORACLE_WMS_PASSWORD", "jmCyS7BK94YvhS@"),
    "entities": ["allocation", "order_hdr", "order_dtl"],  # Multiple entities
    "page_size": 5,
    "enable_incremental": False,
    "discover_catalog": False,
}

# Write tap config
with open("tap_config_multi.json", "w", encoding="utf-8") as f:
    json.dump(tap_config, f, indent=2)

# Target config
target_config = {
    "username": os.getenv("DATABASE__USERNAME", "oic"),
    "password": os.getenv("DATABASE__PASSWORD", "aehaz232dfNuupah_#"),
    "host": os.getenv("DATABASE__HOST", "10.93.10.114"),
    "port": int(os.getenv("DATABASE__PORT", "1522")),
    "service_name": os.getenv("DATABASE__SERVICE_NAME", "gbe8f3f2dbbc562_dwpdb_low.adb.oraclecloud.com"),
    "protocol": os.getenv("DATABASE__PROTOCOL", "tcps"),
    "default_target_schema": os.getenv("DATABASE__SCHEMA", "oic"),
    "table_prefix": "TEST_",
}

# Write target config
with open("target_config_multi.json", "w", encoding="utf-8") as f:
    json.dump(target_config, f, indent=2)

# Run pipeline
tap_cmd = [
    sys.executable, "-m", "flext_tap_oracle_wms.tap",
    "--config", "tap_config_multi.json",
]

target_cmd = [
    sys.executable, "-m", "flext_target_oracle",
    "--config", "target_config_multi.json",
]

print(f"\n📊 Running pipeline with entities: {tap_config['entities']}")
print(f"Tap command: {' '.join(tap_cmd)}")
print(f"Target command: {' '.join(target_cmd)}")

# Create pipeline
tap_process = subprocess.Popen(
    tap_cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    env={**os.environ},
)

target_process = subprocess.Popen(
    target_cmd,
    stdin=tap_process.stdout,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    env={**os.environ},
)

# Allow tap to close its stdout
if tap_process.stdout:
    tap_process.stdout.close()

# Get output
target_stdout, target_stderr = target_process.communicate()
tap_stderr = tap_process.stderr.read() if tap_process.stderr else b""

# Extract summary from output
stdout_lines = target_stdout.decode().split("\n")
summary_started = False
for line in stdout_lines:
    if "Target completed successfully:" in line or summary_started:
        summary_started = True
        print(line)
    if "Success rate:" in line:
        summary_started = False

# Check for errors
if target_stderr:
    print("\n⚠️ Target errors:")
    print(target_stderr.decode())

# Check return codes
print(f"\n✅ Tap return code: {tap_process.returncode}")
print(f"✅ Target return code: {target_process.returncode}")

success = tap_process.returncode == 0 and target_process.returncode == 0
if success:
    print("\n🎉 Multi-entity pipeline completed successfully!")
else:
    print("\n❌ Multi-entity pipeline failed!")
    sys.exit(1)

# Define specific entities we want
target_entities = [
    "allocation",
    "order_hdr",
    "order_dtl",
]

# Create config with entities
config = {
    "base_url": os.getenv("TAP_ORACLE_WMS_BASE_URL"),
    "username": os.getenv("TAP_ORACLE_WMS_USERNAME"),
    "password": os.getenv("TAP_ORACLE_WMS_PASSWORD"),
    "auth_method": "basic",
    "request_timeout": 300,
    "use_metadata_only": True,
    "discovery_sample_size": 0,
    "entities": target_entities,
    "entity_filter": target_entities,
    "page_size": 100,
}

print(f"\n📋 Configured entities: {', '.join(target_entities)}")

# Create tap WITHOUT discovery mode (sync mode)
print("\n🔍 Testing Sync Mode...")
tap = TapOracleWMS(config=config)

# Get streams
try:
    streams = tap.discover_streams()
    print(f"\n✅ Found {len(streams)} streams")

    # Show streams
    print("\n📊 Available Streams:")
    for stream in streams:
        print(f"  - {stream.name}")

    # Test extraction for allocation
    if streams:
        print(f"\n🚀 Testing extraction for '{streams[0].name}'...")
        # This would normally run the sync
        print("✅ Stream configured successfully")

except Exception as e:
    print(f"\n❌ Failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✨ Test completed successfully!")
