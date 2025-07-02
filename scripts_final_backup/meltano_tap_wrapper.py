#!/usr/bin/env python3
"""Meltano-compatible wrapper for tap-oracle-wms."""

import sys

# Add tap path
sys.path.insert(0, "/home/marlonsc/flext/flext-tap-oracle-wms/src")

# Apply jsonschema patch silently
import jsonschema

if not hasattr(jsonschema, "Draft7Validator"):
    jsonschema.Draft7Validator = jsonschema.Draft4Validator

# Import and run the tap
from tap_oracle_wms.tap import TapOracleWMS

if __name__ == "__main__":
    TapOracleWMS.cli()
