#!/usr/bin/env python3
"""Wrapper for tap-oracle-wms that applies jsonschema compatibility patch."""

# Apply the patch first
import os
import sys

# Suppress the patch output when in discovery mode
if "--discover" in sys.argv:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")
    sys.stdout = sys.__stdout__
else:
    pass

# Now import and run the tap
sys.path.insert(0, "/home/marlonsc/flext/flext-tap-oracle-wms/src")

from tap_oracle_wms.tap import TapOracleWMS

if __name__ == "__main__":
    TapOracleWMS.cli()
