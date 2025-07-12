#!/usr/bin/env python3
"""Test flext-target-oracle directly."""

import json
import os
from pathlib import Path

# Load environment
from dotenv import load_dotenv

load_dotenv()

print("🧪 TESTING FLEXT-TARGET-ORACLE")
print("=" * 60)

# Check environment
env_vars = {
    "FLEXT_TARGET_ORACLE_HOST": os.getenv("FLEXT_TARGET_ORACLE_HOST"),
    "FLEXT_TARGET_ORACLE_USERNAME": os.getenv("FLEXT_TARGET_ORACLE_USERNAME"),
    "FLEXT_TARGET_ORACLE_PASSWORD": os.getenv("FLEXT_TARGET_ORACLE_PASSWORD"),
    "FLEXT_TARGET_ORACLE_SERVICE_NAME": os.getenv("FLEXT_TARGET_ORACLE_SERVICE_NAME"),
    "FLEXT_TARGET_ORACLE_PROTOCOL": os.getenv("FLEXT_TARGET_ORACLE_PROTOCOL"),
}

print("\n📋 Environment Variables:")
for key, value in env_vars.items():
    if value:
        if "PASSWORD" in key:
            print(f"✅ {key} = ***")
        else:
            print(f"✅ {key} = {value}")
    else:
        print(f"❌ {key} = NOT SET")

# Create test config
config = {
    "host": env_vars["FLEXT_TARGET_ORACLE_HOST"],
    "port": 1522,
    "service_name": env_vars["FLEXT_TARGET_ORACLE_SERVICE_NAME"],
    "username": env_vars["FLEXT_TARGET_ORACLE_USERNAME"],
    "password": env_vars["FLEXT_TARGET_ORACLE_PASSWORD"],
    "protocol": env_vars["FLEXT_TARGET_ORACLE_PROTOCOL"],
    "default_target_schema": os.getenv("FLEXT_TARGET_ORACLE_SCHEMA", "oic"),
    "table_prefix": os.getenv("FLEXT_TARGET_ORACLE_TABLE_PREFIX", "WMS_"),
    "load_method": "append-only",
    "add_record_metadata": True,
}

print("\n📊 Target Configuration:")
for key, value in config.items():
    if "password" in key:
        print(f"  {key}: ***")
    else:
        print(f"  {key}: {value}")

# Create test messages
messages = [
    {
        "type": "SCHEMA",
        "stream": "test_table",
        "schema": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "created_at": {"type": "string", "format": "date-time"},
            },
        },
        "key_properties": ["id"],
    },
    {
        "type": "RECORD",
        "stream": "test_table",
        "record": {
            "id": 1,
            "name": "Test Record",
            "created_at": "2025-07-11T00:00:00Z",
        },
        "time_extracted": "2025-07-11T16:00:00Z",
    },
    {
        "type": "STATE",
        "value": {"bookmarks": {"test_table": {"replication_key_value": "2025-07-11T00:00:00Z"}}},
    },
]

# Save messages to file
messages_file = Path("test_messages.jsonl")
with open(messages_file, "w", encoding="utf-8") as f:
    f.writelines(json.dumps(msg) + "\n" for msg in messages)

print(f"\n💾 Test messages saved to {messages_file}")
print("\n✨ Run this command to test the target:")
print(f"cat {messages_file} | flext-target-oracle -c config.json")

# Create config file for manual testing
config_file = Path("config.json")
with open(config_file, "w", encoding="utf-8") as f:
    json.dump(config, f, indent=2)
print(f"\n💾 Config saved to {config_file}")
