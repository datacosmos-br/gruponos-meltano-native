#!/usr/bin/env python3
"""Test with detailed error capture."""

import json
import os
import subprocess
import sys
from datetime import UTC, datetime

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
            "_sdc_extracted_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        },
        "time_extracted": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
    },
]

# Write messages to temp file
with open("test_detailed.jsonl", "w", encoding="utf-8") as f:
    f.writelines(json.dumps(msg) + "\n" for msg in messages)

print("Created test_detailed.jsonl")

# Run the target with debug
with open("test_detailed.jsonl", encoding="utf-8") as input_file:
    env_cmd = "export $(grep -v '^#' .env | xargs) && FLEXT_LOG_LEVEL=DEBUG python -m flext_target_oracle.target 2>&1"
    result = subprocess.run(
        env_cmd,
        check=False,
        shell=True,
        stdin=input_file,
        capture_output=True,
        text=True,
    )

    print("\n=== FULL OUTPUT ===")
    print(result.stdout)
    print("\nReturn code:", result.returncode)

    # Extract error details
    for line in result.stdout.split("\n"):
        if "Traceback" in line:
            # Print traceback and following lines
            idx = result.stdout.split("\n").index(line)
            for tb_line in result.stdout.split("\n")[idx : idx + 20]:
                print(tb_line)
