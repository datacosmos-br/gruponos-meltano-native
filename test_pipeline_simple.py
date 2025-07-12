#!/usr/bin/env python3
"""Test simple pipeline flow with valid Singer messages."""

import json
import subprocess
import sys
from datetime import UTC, datetime

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
                "order_dtl_id": {"type": ["string", "null"]},
                "from_inventory_id": {"type": ["string", "null"]},
                "to_inventory_id": {"type": ["string", "null"]},
                "status_id": {"type": ["integer", "null"]},
                "alloc_qty": {"type": ["string", "null"]},
                "packed_qty": {"type": ["string", "null"]},
                "create_ts": {"type": ["string", "null"], "format": "date-time"},
                "mod_ts": {"type": ["string", "null"], "format": "date-time"},
                "_sdc_extracted_at": {"type": "string", "format": "date-time"},
                "_sdc_entity": {"type": "string"},
            },
        },
        "key_properties": ["id"],
    },
    # Records for allocation
    {
        "type": "RECORD",
        "stream": "allocation",
        "record": {
            "id": "1001",
            "order_dtl_id": "ORD001",
            "from_inventory_id": "WH001",
            "to_inventory_id": "SHIP001",
            "status_id": 1,
            "alloc_qty": "10.0",
            "packed_qty": "10.0",
            "create_ts": "2025-01-11T10:00:00Z",
            "mod_ts": "2025-01-11T10:30:00Z",
            "_sdc_extracted_at": datetime.now(UTC).isoformat(),
            "_sdc_entity": "allocation",
        },
        "time_extracted": datetime.now(UTC).isoformat(),
    },
    {
        "type": "RECORD",
        "stream": "allocation",
        "record": {
            "id": "1002",
            "order_dtl_id": "ORD002",
            "from_inventory_id": "WH001",
            "to_inventory_id": "SHIP002",
            "status_id": 2,
            "alloc_qty": "20.0",
            "packed_qty": "15.0",
            "create_ts": "2025-01-11T11:00:00Z",
            "mod_ts": "2025-01-11T11:30:00Z",
            "_sdc_extracted_at": datetime.now(UTC).isoformat(),
            "_sdc_entity": "allocation",
        },
        "time_extracted": datetime.now(UTC).isoformat(),
    },
    {
        "type": "RECORD",
        "stream": "allocation",
        "record": {
            "id": "1003",
            "order_dtl_id": "ORD003",
            "from_inventory_id": "WH002",
            "to_inventory_id": "SHIP003",
            "status_id": 3,
            "alloc_qty": "30.0",
            "packed_qty": "30.0",
            "create_ts": "2025-01-11T12:00:00Z",
            "mod_ts": "2025-01-11T12:30:00Z",
            "_sdc_extracted_at": datetime.now(UTC).isoformat(),
            "_sdc_entity": "allocation",
        },
        "time_extracted": datetime.now(UTC).isoformat(),
    },
]

# Write messages to temp file
with open("test_messages.jsonl", "w", encoding="utf-8") as f:
    f.writelines(json.dumps(msg) + "\n" for msg in messages)

print("Created test_messages.jsonl with", len(messages), "messages")

# Run the target with the test data
print("\nRunning target with test data...")
with open("test_messages.jsonl", encoding="utf-8") as input_file:
    # Source environment variables
    env_cmd = "export $(grep -v '^#' .env | xargs) && python -m flext_target_oracle"
    result = subprocess.run(
        env_cmd,
        check=False,
        shell=True,
        stdin=input_file,
        capture_output=True,
        text=True,
    )

    print("\nTarget output:")
    print(result.stdout)
    if result.stderr:
        print("\nTarget errors:")
        print(result.stderr)

    print("\nReturn code:", result.returncode)
