#!/usr/bin/env python3
"""Run tap with proper stderr redirection to avoid JSON parsing errors."""

import json
import os
import subprocess
import sys
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
tap_path = parent_dir / "flext-tap-oracle-wms" / "src"
sys.path.insert(0, str(tap_path))

# Configuration
config = {
    "base_url": "https://a29.wms.ocs.oraclecloud.com/raizen",
    "username": "USER_WMS_INTEGRA",
    "password": "jmCyS7BK94YvhS@",
    "entities": ["allocation"],
    "page_size": 5,
    "enable_incremental": False,
    "discover_catalog": False,
}

# Write config to file
config_file = "tap_config_clean.json"
with open(config_file, "w", encoding="utf-8") as f:
    json.dump(config, f, indent=2)

# Run tap with stderr redirected
cmd = [
    sys.executable,
    "-m",
    "flext_tap_oracle_wms.tap",
    "--config",
    config_file,
]

# Execute tap and capture only stdout (JSON messages)
process = subprocess.Popen(
    cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.DEVNULL,  # Discard stderr to avoid log messages
    text=True,
    env={**os.environ},
)

# Read and output only valid JSON lines
for line in process.stdout:
    line = line.strip()
    if line:
        try:
            # Verify it's valid JSON
            json.loads(line)
            # Output the line as-is
        except json.JSONDecodeError:
            # Skip non-JSON lines
            pass

# Wait for process to complete
process.wait()
