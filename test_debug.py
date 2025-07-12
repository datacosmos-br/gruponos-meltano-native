#!/usr/bin/env python3
"""Test with debug logging enabled."""

import json
import os
import subprocess
import sys
from datetime import datetime

# Enable debug logging
os.environ["FLEXT_LOG_LEVEL"] = "DEBUG"
# Set smaller batch size
os.environ["FLEXT_TARGET_ORACLE_BATCH_SIZE"] = "1"

# Create simple test data
messages = [
    # Schema for allocation
    {
        "type": "SCHEMA",
        "stream": "allocation",
        "schema": {
            "type": "object",
            "properties": {
                "id": {"type": ["integer", "string"]},
                "status_id": {"type": ["integer", "null"]},
                "alloc_qty": {"type": ["string", "null"]},
                "_sdc_extracted_at": {"type": "string", "format": "date-time"},
            },
        },
        "key_properties": ["id"],
    },
    # One record
    {
        "type": "RECORD",
        "stream": "allocation",
        "record": {
            "id": "1001",
            "status_id": 1,
            "alloc_qty": "10.0",
            "_sdc_extracted_at": datetime.utcnow().isoformat() + "Z",
        },
        "time_extracted": datetime.utcnow().isoformat() + "Z",
    },
]

# Write messages to temp file
with open("test_debug.jsonl", "w", encoding="utf-8") as f:
    f.writelines(json.dumps(msg) + "\n" for msg in messages)

print("Created test_debug.jsonl")

# Run the target with debug
with open("test_debug.jsonl", encoding="utf-8") as input_file:
    env_cmd = "export $(grep -v '^#' .env | xargs) && FLEXT_LOG_LEVEL=DEBUG python -m flext_target_oracle.target 2>&1"
    result = subprocess.run(
        env_cmd,
        check=False,
        shell=True,
        stdin=input_file,
        capture_output=True,
        text=True,
    )

    print("\nOutput:")
    # Show only relevant debug lines
    for line in result.stdout.split("\n"):
        if (
            "SQL:" in line
            or "Existing columns:" in line
            or "First record keys:" in line
            or "ERROR" in line
        ):
            print(line)

    print("\nReturn code:", result.returncode)
