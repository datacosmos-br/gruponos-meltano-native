#!/usr/bin/env python3
"""Run full pipeline with all entities."""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add tap to path
tap_path = Path("/home/marlonsc/flext/flext-tap-oracle-wms/src")
if str(tap_path) not in sys.path:
    sys.path.insert(0, str(tap_path))

# Load environment
from dotenv import load_dotenv
load_dotenv()

# Import tap
from flext_tap_oracle_wms.tap import TapOracleWMS

# Create config for 3 entities
config = {
    "base_url": os.getenv("TAP_ORACLE_WMS_BASE_URL"),
    "username": os.getenv("TAP_ORACLE_WMS_USERNAME"),
    "password": os.getenv("TAP_ORACLE_WMS_PASSWORD"),
    "auth_method": "basic",
    "request_timeout": 300,
    "page_size": 100,
    "entities": ["allocation", "order_hdr", "order_dtl"]
}

# Create tap
tap = TapOracleWMS(config=config)

# Define the entities to sync
selected_streams = ["allocation", "order_hdr", "order_dtl"]

# Output schema for each stream
for stream_id in selected_streams:
    stream = tap.streams.get(stream_id)
    if stream:
        # Output SCHEMA message
        schema_message = {
            "type": "SCHEMA",
            "stream": stream_id,
            "schema": stream.schema,
            "key_properties": stream.primary_keys or ["id"],
            "bookmark_properties": [stream.replication_key] if stream.replication_key else []
        }
        print(json.dumps(schema_message))
        
        # Get records (limited to 10 per entity for testing)
        records = []
        for record in stream.get_records(None):
            records.append(record)
            if len(records) >= 10:
                break
        
        # Output RECORD messages
        for record in records:
            record_message = {
                "type": "RECORD",
                "stream": stream_id,
                "record": record,
                "time_extracted": record.get("_sdc_extracted_at", datetime.utcnow().isoformat() + "Z")
            }
            print(json.dumps(record_message))
        
        # Output STATE message
        state_message = {
            "type": "STATE",
            "value": {
                "bookmarks": {
                    stream_id: {
                        "replication_key_value": records[-1].get(stream.replication_key) if records and stream.replication_key else None
                    }
                }
            }
        }
        print(json.dumps(state_message))