#!/usr/bin/env python3
"""Test target directly with sample data."""

import asyncio
import json
import logging
from datetime import UTC, datetime

from flext_target_oracle.application.services import SingerTargetService
from flext_target_oracle.domain.models import TargetConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_target_direct() -> None:
    """Test target service directly."""
    # Load config from environment like the target does
    import os

    from dotenv import load_dotenv

    load_dotenv()

    config = {
        "host": os.getenv("FLEXT_TARGET_ORACLE_HOST"),
        "port": int(os.getenv("FLEXT_TARGET_ORACLE_PORT", "1522")),
        "service_name": os.getenv("FLEXT_TARGET_ORACLE_SERVICE_NAME"),
        "username": os.getenv("FLEXT_TARGET_ORACLE_USERNAME"),
        "password": os.getenv("FLEXT_TARGET_ORACLE_PASSWORD"),
        "protocol": os.getenv("FLEXT_TARGET_ORACLE_PROTOCOL", "tcp"),
        "default_target_schema": "OIC",
        "batch_size": 1,  # Use small batch for testing
    }

    # Handle TCPS protocol
    if config["protocol"] == "tcps":
        config["wallet_location"] = os.getenv("ORACLE_WALLET_LOCATION")
        config["wallet_password"] = os.getenv("ORACLE_WALLET_PASSWORD")

    logger.info("Testing target with config: %s", {k: v for k, v in config.items() if k != "password"})

    try:
        target_config = TargetConfig(**config)
        service = SingerTargetService(target_config)

        # Test schema message first
        schema_msg = {
            "type": "SCHEMA",
            "stream": "test_allocation",
            "schema": {
                "properties": {
                    "id": {"type": "string"},
                    "status_id": {"type": "integer"},
                    "alloc_qty": {"type": "string"},
                },
                "key_properties": ["id"],
            },
        }

        logger.info("Processing SCHEMA message...")
        schema_result = await service.process_singer_message(schema_msg)
        if not schema_result.is_success:
            logger.error("Schema processing failed: %s", schema_result.error)
            return

        logger.info("Schema processed successfully!")

        # Test record message
        record_msg = {
            "type": "RECORD",
            "stream": "test_allocation",
            "record": {
                "id": "TEST001",
                "status_id": 1,
                "alloc_qty": "10.5",
            },
        }

        logger.info("Processing RECORD message...")
        record_result = await service.process_singer_message(record_msg)
        if not record_result.is_success:
            logger.error("Record processing failed: %s", record_result.error)
            return

        logger.info("Record processed successfully!")

        # Finalize to flush any remaining records
        logger.info("Finalizing streams...")
        final_result = await service.finalize_all_streams()
        if final_result.is_success:
            logger.info("Finalization successful! Stats: %s", final_result.value)
        else:
            logger.error("Finalization failed: %s", final_result.error)

    except Exception as e:
        logger.exception("Test failed: %s", e)


if __name__ == "__main__":
    asyncio.run(test_target_direct())
