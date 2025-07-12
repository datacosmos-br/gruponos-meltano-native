#!/usr/bin/env python3
"""Test pipeline with multiple entities."""

import json
import os
import subprocess
import sys
from pathlib import Path

# Configuration for multiple entities
tap_config = {
    "base_url": "https://a29.wms.ocs.oraclecloud.com/raizen",
    "username": "USER_WMS_INTEGRA",
    "password": "jmCyS7BK94YvhS@",
    "entities": ["allocation", "order_hdr", "order_dtl"],
    "page_size": 3,  # Smaller page size for testing
    "enable_incremental": False,
    "discover_catalog": False,
}

target_config = {
    "username": "oic",
    "password": "aehaz232dfNuupah_#",
    "host": "10.93.10.114",
    "port": 1522,
    "service_name": "gbe8f3f2dbbc562_dwpdb_low.adb.oraclecloud.com",
    "protocol": "tcps",
    "default_target_schema": "oic",
    "table_prefix": "TEST_",
}

# Write configs
with open("tap_config_multi.json", "w", encoding="utf-8") as f:
    json.dump(tap_config, f, indent=2)

with open("target_config_multi.json", "w", encoding="utf-8") as f:
    json.dump(target_config, f, indent=2)

print("🧪 TESTING PIPELINE WITH MULTIPLE ENTITIES")
print("=" * 60)
print(f"Entities: {', '.join(tap_config['entities'])}")

# Run tap and pipe to target
tap_cmd = [
    sys.executable,
    "-m",
    "flext_tap_oracle_wms.tap",
    "--config",
    "tap_config_multi.json",
]

target_cmd = [
    sys.executable,
    "-m",
    "flext_target_oracle",
    "--config",
    "target_config_multi.json",
]

print("\n📊 Running pipeline...")
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

# Parse and display results
print("\n📊 PIPELINE RESULTS:")
print(f"Tap return code: {tap_process.returncode}")
print(f"Target return code: {target_process.returncode}")

if target_process.returncode == 0:
    print("\n✅ TARGET OUTPUT:")
    # Show final statistics
    lines = target_stdout.decode().split("\n")
    for line in lines:
        if any(
            x in line for x in ["Target completed", "Total records", "Success rate"]
        ):
            print(line)

    print("\n🎉 Multi-entity pipeline completed successfully!")
else:
    print("\n❌ TARGET ERRORS:")
    print(target_stderr.decode())
    if tap_stderr:
        print("\n❌ TAP ERRORS:")
        print(tap_stderr.decode())
