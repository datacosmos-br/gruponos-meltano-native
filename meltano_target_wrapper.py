#!/usr/bin/env python3
"""Meltano-compatible wrapper for target-oracle."""

import sys

# Add current path
sys.path.insert(0, ".")

# Import and run simple_target_oracle_fixed
if __name__ == "__main__":
    import simple_target_oracle_fixed

    simple_target_oracle_fixed.process_singer_messages()
