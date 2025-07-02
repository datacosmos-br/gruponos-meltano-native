#!/usr/bin/env python3
"""Native Meltano tap wrapper for tap-oracle-wms without custom scripts."""

import os
import sys

# Add tap source directory to Python path
tap_source_dir = "/home/marlonsc/flext/flext-tap-oracle-wms/src"
if tap_source_dir not in sys.path:
    sys.path.insert(0, tap_source_dir)

# Import and run the tap
try:
    from tap_oracle_wms.cli import cli
    if __name__ == "__main__":
        cli()
except ImportError as e:
    print(f"❌ Failed to import tap-oracle-wms: {e}", file=sys.stderr)
    print("Please ensure tap-oracle-wms is properly installed", file=sys.stderr)
    sys.exit(1)
