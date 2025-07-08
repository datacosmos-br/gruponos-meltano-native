#!/usr/bin/env python3
"""Test script to simulate sync process and verify pipeline functionality."""

import json
import sys
import os
from datetime import datetime, timezone
from typing import Dict, Any
from pathlib import Path


def load_env_variables() -> Dict[str, str]:
    """Load environment variables from .env file."""
    env_vars = {}
    env_file = Path(__file__).parent / ".env"
    
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    value = value.strip('"\'')
                    env_vars[key] = value
    
    return env_vars


def get_config_value(key: str, env_vars: Dict[str, str], default: str = "") -> str:
    """Get configuration value from environment or .env file."""
    return os.environ.get(key) or env_vars.get(key, default)


def create_mock_schema() -> Dict[str, Any]:
    """Create a mock schema for allocation entity."""
    return {
        "type": "object",
        "properties": {
            "allocation_id": {"type": "string"},
            "company_code": {"type": "string"},
            "facility_code": {"type": "string"},
            "item_id": {"type": "string"},
            "quantity": {"type": "number"},
            "status": {"type": "string"},
            "created_date": {"type": "string", "format": "date-time"},
            "modified_date": {"type": "string", "format": "date-time"},
        },
        "required": ["allocation_id", "company_code", "facility_code"],
    }


def create_mock_catalog(env_vars: Dict[str, str]) -> Dict[str, Any]:
    """Create a mock catalog for discovery."""
    company_code = get_config_value("TAP_ORACLE_WMS_COMPANY_CODE", env_vars, "*")
    facility_code = get_config_value("TAP_ORACLE_WMS_FACILITY_CODE", env_vars, "*")
    
    return {
        "streams": [
            {
                "tap_stream_id": "allocation",
                "schema": create_mock_schema(),
                "metadata": [
                    {
                        "breadcrumb": [],
                        "metadata": {
                            "inclusion": "available",
                            "selected": True,
                            "replication-method": "INCREMENTAL",
                            "replication-key": "modified_date",
                        },
                    },
                ],
            },
        ],
    }


def main() -> None:
    """Main function to simulate tap output."""
    # Load environment variables
    env_vars = load_env_variables()
    
    # Get configuration from environment
    base_url = get_config_value("TAP_ORACLE_WMS_BASE_URL", env_vars)
    username = get_config_value("TAP_ORACLE_WMS_USERNAME", env_vars)
    company_code = get_config_value("TAP_ORACLE_WMS_COMPANY_CODE", env_vars, "*")
    facility_code = get_config_value("TAP_ORACLE_WMS_FACILITY_CODE", env_vars, "*")
    
    # Emit SCHEMA message
    schema_message = {
        "type": "SCHEMA",
        "stream": "allocation",
        "schema": create_mock_schema(),
        "key_properties": ["allocation_id", "company_code", "facility_code"],
    }
    print(json.dumps(schema_message))

    # Emit RECORD messages with environment-based data
    for i in range(5):
        record = {
            "allocation_id": f"ALLOC_{i:04d}",
            "company_code": company_code if company_code != "*" else f"COMP_{i}",
            "facility_code": facility_code if facility_code != "*" else f"FAC_{i}",
            "item_id": f"ITEM_{i:06d}",
            "quantity": 100 + i * 10,
            "status": "ACTIVE",
            "created_date": datetime.now(timezone.utc).isoformat(),
            "modified_date": datetime.now(timezone.utc).isoformat(),
        }

        record_message = {
            "type": "RECORD",
            "stream": "allocation",
            "record": record,
            "time_extracted": datetime.now(timezone.utc).isoformat(),
        }
        print(json.dumps(record_message))

    # Emit STATE message
    state_message = {
        "type": "STATE",
        "value": {
            "bookmarks": {
                "allocation": {
                    "replication_key": "modified_date",
                    "replication_key_value": datetime.now(timezone.utc).isoformat(),
                }
            }
        },
    }
    print(json.dumps(state_message))


if __name__ == "__main__":
    main()
