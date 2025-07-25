#!/usr/bin/env python3
"""Configure Meltano Project.

Generates meltano.yml from templates and environment configuration.
This allows complete customization without hardcoded values.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from flext_core import get_logger

# Setup logger
log = get_logger(__name__)


def load_project_config() -> dict[str, Any]:
    """Load project configuration from YAML file."""
    config_path = Path(__file__).parent.parent / "config" / "project.yml"
    if config_path.exists():
        with Path(config_path).open(encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data if isinstance(data, dict) else {}
    return {}


def load_wms_config() -> dict[str, Any]:
    """Load WMS integration configuration from YAML file."""
    config_path = Path(__file__).parent.parent / "config" / "wms_integration.yml"
    if config_path.exists():
        with Path(config_path).open(encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data if isinstance(data, dict) else {}
    return {}


def get_env_value(key: str, default: str | None = None) -> str | None:
    """Get environment variable value with optional default."""
    return os.environ.get(key, default)


def generate_meltano_config() -> dict[str, Any]:
    """Generate complete Meltano configuration from environment variables."""
    _ = load_project_config()  # Keep for future use
    _ = load_wms_config()  # Keep for future use

    # Base configuration
    config: dict[str, Any] = {
        "version": 1,
        "default_environment": get_env_value("MELTANO_ENVIRONMENT", "dev"),
        "project_id": get_env_value("MELTANO_PROJECT_ID", "dynamic-wms-integration"),
        "environments": [{"name": "dev"}, {"name": "staging"}, {"name": "prod"}],
        "plugins": {
            "extractors": [],
            "loaders": [],
        },
        "jobs": [],
        "schedules": [],
    }

    # Get project-specific values
    _ = get_env_value("COMPANY_NAME", "YourCompany")  # Keep for future use
    get_env_value("TABLE_PREFIX", "WMS_")

    # Configure extractors
    entities_str = get_env_value(
        "WMS_ENTITIES",
        "allocation,order_hdr,order_dtl",
    )
    entities = entities_str.split(",") if entities_str else []

    # Base tap configuration - CORRECTED for REST API per FLEXT documentation
    base_tap_config = {
        "base_url": "$TAP_ORACLE_WMS_BASE_URL",
        "username": "$TAP_ORACLE_WMS_USERNAME",
        "password": "$TAP_ORACLE_WMS_PASSWORD",
        "company_code": "$TAP_ORACLE_WMS_COMPANY_CODE",
        "facility_code": "$TAP_ORACLE_WMS_FACILITY_CODE",
        "page_size": int(get_env_value("WMS_PAGE_SIZE", "500") or "500"),
        "timeout": int(get_env_value("WMS_REQUEST_TIMEOUT", "600") or "600"),
        "max_retries": int(get_env_value("WMS_MAX_RETRIES", "3") or "3"),
        "start_date": get_env_value(
            "TAP_ORACLE_WMS_START_DATE",
            "2024-01-01T00:00:00Z",
        ),
    }

    # Full sync tap
    full_tap = {
        "name": "tap-oracle-wms-full",
        "namespace": "tap_oracle_wms",
        "executable": get_env_value(
            "TAP_EXECUTABLE",
            "flext-tap-oracle-wms",
        ),
        "config": {
            **base_tap_config,
            "entities": entities,
            "enable_incremental": False,
        },
    }

    # Incremental sync tap
    incremental_tap = {
        "name": "tap-oracle-wms-incremental",
        "namespace": "tap_oracle_wms",
        "executable": get_env_value(
            "TAP_EXECUTABLE",
            "flext-tap-oracle-wms",
        ),
        "config": {
            **base_tap_config,
            "entities": entities,
            "enable_incremental": True,
            "replication_key": "mod_ts",
        },
    }

    extractors = config["plugins"]["extractors"]
    if isinstance(extractors, list):
        extractors.extend([full_tap, incremental_tap])

    # Add individual entity extractors
    for entity in entities:
        # Full sync
        entity_tap_full = {
            "name": f"tap-oracle-wms-{entity}-full",
            "inherit_from": "tap-oracle-wms-full",
            "config": {"entities": [entity]},
        }

        # Incremental sync
        entity_tap_inc = {
            "name": f"tap-oracle-wms-{entity}-incremental",
            "inherit_from": "tap-oracle-wms-incremental",
            "config": {"entities": [entity]},
        }

        extractors = config["plugins"]["extractors"]
        if isinstance(extractors, list):
            extractors.extend([entity_tap_full, entity_tap_inc])

    # Configure loaders - CORRECTED per FLEXT documentation
    base_target_config = {
        "oracle_config": {
            "host": "$FLEXT_TARGET_ORACLE_HOST",
            "port": int(get_env_value("TARGET_ORACLE_PORT", "1522") or "1522"),
            "service_name": "$FLEXT_TARGET_ORACLE_SERVICE_NAME",
            "username": "$FLEXT_TARGET_ORACLE_USERNAME",
            "password": "$FLEXT_TARGET_ORACLE_PASSWORD",
            "protocol": "$FLEXT_TARGET_ORACLE_PROTOCOL",
        },
        "default_target_schema": get_env_value("TARGET_ORACLE_SCHEMA", "OIC"),
        "add_record_metadata": False,
    }

    # Full load target
    full_target = {
        "name": "target-oracle-full",
        "namespace": "target_oracle",
        "executable": get_env_value(
            "TARGET_EXECUTABLE",
            "flext-target-oracle",
        ),
        "config": {
            **base_target_config,
            "batch_size": int(
                get_env_value("TARGET_BATCH_SIZE", "1000") or "1000",
            ),
            "load_method": "append_only",
        },
    }

    # Incremental target
    incremental_target = {
        "name": "target-oracle-incremental",
        "namespace": "target_oracle",
        "executable": get_env_value(
            "TARGET_EXECUTABLE",
            "flext-target-oracle",
        ),
        "config": {
            **base_target_config,
            "batch_size": int(
                get_env_value("TARGET_BATCH_SIZE", "5000") or "5000",
            ),
            "load_method": "upsert",
        },
    }

    loaders = config["plugins"]["loaders"]
    if isinstance(loaders, list):
        loaders.extend([full_target, incremental_target])

    # Configure jobs
    config["jobs"] = [
        {"name": "full-sync-job", "tasks": ["tap-oracle-wms-full target-oracle-full"]},
        {
            "name": "incremental-sync-job",
            "tasks": ["tap-oracle-wms-incremental target-oracle-incremental"],
        },
    ]

    # Add individual entity jobs
    for entity in entities:
        jobs = config["jobs"]
        if isinstance(jobs, list):
            jobs.extend(
                [
                    {
                        "name": f"sync-{entity}-full",
                        "tasks": [f"tap-oracle-wms-{entity}-full target-oracle-full"],
                    },
                    {
                        "name": f"sync-{entity}-incremental",
                        "tasks": [
                            f"tap-oracle-wms-{entity}-incremental "
                            "target-oracle-incremental",
                        ],
                    },
                ],
            )

    # Configure schedules if enabled:
    enable_schedules = get_env_value("ENABLE_SCHEDULES", "false")
    if enable_schedules and enable_schedules.lower() == "true":
        config["schedules"] = [
            {
                "name": "daily-full-sync",
                "interval": get_env_value("FULL_SYNC_SCHEDULE", "@daily") or "@daily",
                "job": "full-sync-job",
            },
            {
                "name": "hourly-incremental-sync",
                "interval": (
                    get_env_value("INCREMENTAL_SYNC_SCHEDULE", "@hourly") or "@hourly"
                ),
                "job": "incremental-sync-job",
            },
        ]

    return config


def main() -> None:
    """Generate and output Meltano configuration."""
    config = generate_meltano_config()

    # Write to meltano.yml
    output_path = Path(__file__).parent.parent / "meltano.yml"

    # Backup existing if present:
    if output_path.exists():
        backup_path = output_path.with_suffix(".yml.backup")
        output_path.rename(backup_path)
        log.info("Backed up existing meltano.yml to %s", backup_path)

    # Write new configuration
    with Path(output_path).open("w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    log.info("Generated meltano.yml successfully!")
    log.info(
        "Project: %s",
        get_env_value("PROJECT_NAME", "meltano-wms-integration"),
    )
    log.info("Company: %s", get_env_value("COMPANY_NAME", "YourCompany"))
    log.info("Environment: %s", get_env_value("MELTANO_ENVIRONMENT", "dev"))


if __name__ == "__main__":
    main()
