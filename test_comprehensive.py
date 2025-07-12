#!/usr/bin/env python3
"""Comprehensive test with multiple records."""

import json
import os
import subprocess
import sys
from datetime import UTC, datetime

# Enable info logging
os.environ["FLEXT_LOG_LEVEL"] = "INFO"
# Set batch size
os.environ["FLEXT_TARGET_ORACLE_BATCH_SIZE"] = "5"

# Create test data with multiple records
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
                "create_ts": {"type": ["string", "null"], "format": "date-time"},
                "mod_ts": {"type": ["string", "null"], "format": "date-time"},
                "order_dtl_id": {"type": ["object", "null"]},
                "from_inventory_id": {"type": ["object", "null"]},
                "alloc_uom_id": {"type": ["object", "null"]},
                "_sdc_extracted_at": {"type": "string", "format": "date-time"},
            },
        },
        "key_properties": ["id"],
    },
]

# Add 10 allocation records
messages.extend(
    {
        "type": "RECORD",
        "stream": "allocation",
        "record": {
            "id": str(i),
            "status_id": i % 3 + 1,  # Status 1, 2, or 3
            "alloc_qty": f"{i * 10.5}",
            "create_ts": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "mod_ts": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "order_dtl_id": {"id": f"ODT{i}", "url": f"/order_dtl/{i}"},
            "from_inventory_id": {"id": f"INV{i}", "url": f"/inventory/{i}"},
            "alloc_uom_id": {"id": "EA", "url": "/uom/EA"},
            "_sdc_extracted_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        },
        "time_extracted": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
    }
    for i in range(1001, 1011)
)

# Write messages to temp file
with open("test_comprehensive.jsonl", "w", encoding="utf-8") as f:
    f.writelines(json.dumps(msg) + "\n" for msg in messages)

print("Created test_comprehensive.jsonl with", len(messages), "messages")

# Run the target
with open("test_comprehensive.jsonl", encoding="utf-8") as input_file:
    env_cmd = "export $(grep -v '^#' .env | xargs) && python -m flext_target_oracle.target 2>&1"
    result = subprocess.run(
        env_cmd,
        check=False,
        shell=True,
        stdin=input_file,
        capture_output=True,
        text=True,
    )

    print("\n=== SUMMARY ===")
    for line in result.stdout.split("\n"):
        if any(
            x in line
            for x in [
                "Total records:",
                "Successful:",
                "Failed:",
                "Success rate:",
                "Batch loaded",
            ]
        ):
            print(line)

    print("\nReturn code:", result.returncode)

    # Check for errors
    if "ERROR" in result.stdout:
        print("\n=== ERRORS ===")
        for line in result.stdout.split("\n"):
            if "ERROR" in line:
                print(line)
