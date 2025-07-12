#!/usr/bin/env python3
"""Test meltano pipeline with tap only."""

import os
import subprocess
import sys
from pathlib import Path

# Load environment
from dotenv import load_dotenv

load_dotenv()

print("🚀 TESTING MELTANO PIPELINE")
print("=" * 60)

# Create output directory
output_dir = Path("output")
output_dir.mkdir(exist_ok=True)

# First, test tap only
print("\n1️⃣ Testing tap-oracle-wms-full...")
cmd = [
    "meltano",
    "invoke",
    "tap-oracle-wms-full",
    "--config",
    "config.json",
    "--state",
    "state.json",
]

print(f"Running: {' '.join(cmd)}")
result = subprocess.run(cmd, check=False, capture_output=True, text=True)

if result.returncode != 0:
    print(f"❌ Tap failed: {result.returncode}")
    print(f"STDOUT:\n{result.stdout}")
    print(f"STDERR:\n{result.stderr}")
    sys.exit(1)

# Save output
with open(output_dir / "tap_output.jsonl", "w", encoding="utf-8") as f:
    f.write(result.stdout)

print(f"✅ Tap output saved to {output_dir}/tap_output.jsonl")

# Count records
record_count = sum(
    1
    for line in result.stdout.splitlines()
    if line.strip().startswith('{"type":"RECORD"')
)
schema_count = sum(
    1
    for line in result.stdout.splitlines()
    if line.strip().startswith('{"type":"SCHEMA"')
)

print("\n📊 Results:")
print(f"  - Schemas: {schema_count}")
print(f"  - Records: {record_count}")

print("\n✨ Test completed successfully!")
