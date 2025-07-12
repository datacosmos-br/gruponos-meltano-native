#!/usr/bin/env python3
"""Test the parameter binding fix."""

import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_parameter_mapping() -> None:
    """Test parameter name mapping for Oracle bind variables."""
    # Test the old vs new approach
    test_columns = [
        "_sdc_extracted_at",
        "_sdc_batched_at",
        "_sdc_entity",
        "_sdc_sequence",
        "id",
        "status_id",
        "alloc_qty",
    ]

    logger.info("Testing parameter name mapping:")

    for col in test_columns:
        col_lower = col.lower()

        # OLD (wrong) approach using lstrip
        old_param = col_lower.lstrip("_") if col_lower.startswith("_") else col_lower

        # NEW (correct) approach removing only first underscore
        new_param = col_lower.removeprefix("_")

        logger.info(f"  {col} -> old: '{old_param}', new: '{new_param}'")

        # Check if they differ (which would indicate a problem with lstrip)
        if old_param != new_param:
            logger.warning(
                "    MISMATCH! Old lstrip approach differs from new approach"
            )

    # Test SQL placeholder generation
    logger.info("\nTesting SQL placeholder generation:")

    for col in test_columns:
        col_lower = col.lower()
        param_name = col_lower.removeprefix("_")

        # Timestamp columns get special treatment
        timestamp_columns = [
            "_sdc_extracted_at",
            "_sdc_batched_at",
            "create_ts",
            "mod_ts",
            "picked_ts",
        ]

        if col_lower in timestamp_columns:
            placeholder = f"TO_TIMESTAMP(:{param_name}, 'YYYY-MM-DD\"T\"HH24:MI:SS.FF')"
        else:
            placeholder = f":{param_name}"

        logger.info(f"  {col} -> {placeholder}")

    logger.info("\nTest completed!")


if __name__ == "__main__":
    test_parameter_mapping()
