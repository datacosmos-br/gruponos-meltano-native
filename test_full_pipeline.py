#!/usr/bin/env python3
"""Test full pipeline with tap-oracle-wms and target-oracle."""

import json
import os
import subprocess
import sys
from datetime import UTC, datetime

# Configuration for tap
tap_config = {
    "base_url": os.getenv(
        "TAP_ORACLE_WMS_BASE_URL", "https://a29.wms.ocs.oraclecloud.com/raizen"
    ),
    "username": os.getenv("TAP_ORACLE_WMS_USERNAME", "USER_WMS_INTEGRA"),
    "password": os.getenv("TAP_ORACLE_WMS_PASSWORD", "jmCyS7BK94YvhS@"),
    "entities": ["allocation"],
    "page_size": 5,
    "enable_incremental": False,
    "discover_catalog": False,
}

# Write tap config
with open("tap_config_test.json", "w", encoding="utf-8") as f:
    json.dump(tap_config, f, indent=2)

print("🚀 Testing Full Pipeline: tap-oracle-wms → target-oracle")
print("=" * 60)

# Create target config
target_config = {
    "username": os.getenv("DATABASE__USERNAME", "oic"),
    "password": os.getenv("DATABASE__PASSWORD", "aehaz232dfNuupah_#"),
    "host": os.getenv("DATABASE__HOST", "10.93.10.114"),
    "port": int(os.getenv("DATABASE__PORT", "1522")),
    "service_name": os.getenv(
        "DATABASE__SERVICE_NAME", "gbe8f3f2dbbc562_dwpdb_low.adb.oraclecloud.com"
    ),
    "protocol": os.getenv("DATABASE__PROTOCOL", "tcps"),
    "default_target_schema": os.getenv("DATABASE__SCHEMA", "oic"),
    "table_prefix": "TEST_",
}

# Write target config
with open("target_config_test.json", "w", encoding="utf-8") as f:
    json.dump(target_config, f, indent=2)

# Run tap and pipe to target
tap_cmd = [
    sys.executable,
    "-m",
    "flext_tap_oracle_wms",
    "--config",
    "tap_config_test.json",
]

target_cmd = [
    sys.executable,
    "-m",
    "flext_target_oracle",
    "--config",
    "target_config_test.json",
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

# Print results
print("\n📤 Tap output (stderr):")
print(tap_stderr.decode())

print("\n📥 Target output (stdout):")
print(target_stdout.decode())

print("\n⚠️ Target errors (stderr):")
print(target_stderr.decode())

# Check return codes
print(f"\n✅ Tap return code: {tap_process.returncode}")
print(f"✅ Target return code: {target_process.returncode}")

if tap_process.returncode == 0 and target_process.returncode == 0:
    print("\n🎉 Pipeline completed successfully!")
else:
    print("\n❌ Pipeline failed!")
    sys.exit(1)
