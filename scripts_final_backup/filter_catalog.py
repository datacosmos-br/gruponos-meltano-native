#!/usr/bin/env python3
"""Filter catalog to only include required entities."""

import json

# Entities we want
REQUIRED_ENTITIES = ["allocation", "order_hdr", "order_dtl"]

# Read the full catalog
with open("catalog_clean.json", encoding="utf-8") as f:
    catalog = json.load(f)

# Filter streams
filtered_streams = []
for stream in catalog.get("streams", []):
    if stream.get("tap_stream_id") in REQUIRED_ENTITIES:
        # Enable selection
        stream["metadata"][0]["metadata"]["selected"] = True
        stream["metadata"][0]["metadata"]["replication-method"] = "INCREMENTAL"
        stream["metadata"][0]["metadata"]["replication-key"] = "mod_ts"
        filtered_streams.append(stream)

# Create filtered catalog
filtered_catalog = {"streams": filtered_streams}

# Save filtered catalog
with open("catalog_filtered.json", "w", encoding="utf-8") as f:
    json.dump(filtered_catalog, f, indent=2)
