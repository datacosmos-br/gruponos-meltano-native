#!/usr/bin/env python3
"""Configure Meltano Project
Generates meltano.yml from templates and environment configuration.
This allows complete customization without hardcoded values.
"""

import os
import sys
import yaml
from pathlib import Path


def load_project_config():
    """Load project configuration from config/project.yml"""
    config_path = Path(__file__).parent.parent / "config" / "project.yml"
    if config_path.exists():
        with open(config_path) as f:
            return yaml.safe_load(f)
    return {}


def load_wms_config():
    """Load WMS integration configuration"""
    config_path = Path(__file__).parent.parent / "config" / "wms_integration.yml"
    if config_path.exists():
        with open(config_path) as f:
            return yaml.safe_load(f)
    return {}


def get_env_value(key, default=None):
    """Get environment variable with fallback to default"""
    return os.environ.get(key, default)


def generate_meltano_config():
    """Generate meltano.yml configuration dynamically"""
    project_config = load_project_config()
    wms_config = load_wms_config()
    
    # Base configuration
    config = {
        "version": 1,
        "default_environment": get_env_value("MELTANO_ENVIRONMENT", "dev"),
        "project_id": get_env_value("MELTANO_PROJECT_ID", "dynamic-wms-integration"),
        "environments": [{"name": "dev"}, {"name": "staging"}, {"name": "prod"}],
        "plugins": {
            "extractors": [],
            "loaders": [],
        },
        "jobs": [],
        "schedules": []
    }
    
    # Get project-specific values
    company_name = get_env_value("COMPANY_NAME", "YourCompany")
    table_prefix = get_env_value("TABLE_PREFIX", "WMS_")
    
    # Configure extractors
    entities = get_env_value("WMS_ENTITIES", "allocation,order_hdr,order_dtl").split(",")
    
    # Base tap configuration
    base_tap_config = {
        "base_url": "$TAP_ORACLE_WMS_BASE_URL",
        "username": "$TAP_ORACLE_WMS_USERNAME", 
        "password": "$TAP_ORACLE_WMS_PASSWORD",
        "page_size": int(get_env_value("WMS_PAGE_SIZE", "100")),
        "timeout": int(get_env_value("WMS_REQUEST_TIMEOUT", "3600")),
        "request_timeout": int(get_env_value("WMS_REQUEST_TIMEOUT", "3600")),
    }
    
    # Full sync tap
    full_tap = {
        "name": "tap-oracle-wms-full",
        "namespace": "tap_oracle_wms",
        "executable": get_env_value("TAP_EXECUTABLE", "/home/marlonsc/flext/.venv/bin/tap-oracle-wms"),
        "config": {
            **base_tap_config,
            "entities": entities,
            "force_full_table": True,
            "ordering": "-id",
            "filter_mode": "id_recovery",
            "batch_size_rows": int(get_env_value("WMS_BATCH_SIZE", "100")),
            "max_sync_duration": int(get_env_value("MAX_SYNC_DURATION", "10800")),
        }
    }
    
    # Incremental sync tap
    incremental_tap = {
        "name": "tap-oracle-wms-incremental",
        "namespace": "tap_oracle_wms",
        "executable": get_env_value("TAP_EXECUTABLE", "/home/marlonsc/flext/.venv/bin/tap-oracle-wms"),
        "config": {
            **base_tap_config,
            "entities": entities,
            "force_full_table": False,
            "ordering": "mod_ts",
            "filter_mode": "incremental",
            "lookback_minutes": int(get_env_value("WMS_LOOKBACK_MINUTES", "30")),
            "incremental_overlap_minutes": int(get_env_value("WMS_INCREMENTAL_OVERLAP", "30")),
            "max_sync_duration": int(get_env_value("MAX_SYNC_DURATION", "5400")),
        }
    }
    
    config["plugins"]["extractors"].extend([full_tap, incremental_tap])
    
    # Add individual entity extractors
    for entity in entities:
        # Full sync
        entity_tap_full = {
            "name": f"tap-oracle-wms-{entity}-full",
            "inherit_from": "tap-oracle-wms-full",
            "config": {"entities": [entity]}
        }
        
        # Incremental sync
        entity_tap_inc = {
            "name": f"tap-oracle-wms-{entity}-incremental",
            "inherit_from": "tap-oracle-wms-incremental",
            "config": {"entities": [entity]}
        }
        
        config["plugins"]["extractors"].extend([entity_tap_full, entity_tap_inc])
    
    # Configure loaders
    base_target_config = {
        "host": "$FLEXT_TARGET_ORACLE_HOST",
        "port": int(get_env_value("TARGET_ORACLE_PORT", "1522")),
        "service_name": "$FLEXT_TARGET_ORACLE_SERVICE_NAME",
        "username": "$FLEXT_TARGET_ORACLE_USERNAME",
        "password": "$FLEXT_TARGET_ORACLE_PASSWORD",
        "protocol": "$FLEXT_TARGET_ORACLE_PROTOCOL",
        "ssl_server_dn_match": False,
        "add_record_metadata": False,
        "validate_records": False,
        "default_target_schema": get_env_value("TARGET_ORACLE_SCHEMA", "OIC"),
        "primary_key_required": True,
        "table_prefix": table_prefix,
    }
    
    # Full load target
    full_target = {
        "name": "target-oracle-full",
        "namespace": "target_oracle",
        "executable": get_env_value("TARGET_EXECUTABLE", "/home/marlonsc/flext/.venv/bin/flext-target-oracle"),
        "config": {
            **base_target_config,
            "batch_size_rows": int(get_env_value("TARGET_BATCH_SIZE", "1000")),
            "pool_size": 2,
            "max_overflow": 5,
            "parallel_threads": 1,
            "load_method": "append-only",
            "primary_key_includes_mod_ts": True,
            "debug_type_mapping": False,
            "use_null_pool": True,
        }
    }
    
    # Incremental target
    incremental_target = {
        "name": "target-oracle-incremental",
        "namespace": "target_oracle",
        "executable": get_env_value("TARGET_EXECUTABLE", "/home/marlonsc/flext/.venv/bin/flext-target-oracle"),
        "config": {
            **base_target_config,
            "batch_size_rows": int(get_env_value("TARGET_BATCH_SIZE", "5000")),
            "pool_size": 8,
            "parallel_threads": 2,
            "load_method": "append-only",
            "primary_key_includes_mod_ts": True,
            "enable_historical_versioning": True,
            "historical_versioning_column": "mod_ts",
        }
    }
    
    config["plugins"]["loaders"].extend([full_target, incremental_target])
    
    # Configure jobs
    config["jobs"] = [
        {"name": "full-sync-job", "tasks": ["tap-oracle-wms-full target-oracle-full"]},
        {"name": "incremental-sync-job", "tasks": ["tap-oracle-wms-incremental target-oracle-incremental"]},
    ]
    
    # Add individual entity jobs
    for entity in entities:
        config["jobs"].extend([
            {"name": f"sync-{entity}-full", "tasks": [f"tap-oracle-wms-{entity}-full target-oracle-full"]},
            {"name": f"sync-{entity}-incremental", "tasks": [f"tap-oracle-wms-{entity}-incremental target-oracle-incremental"]},
        ])
    
    # Configure schedules if enabled
    if get_env_value("ENABLE_SCHEDULES", "false").lower() == "true":
        config["schedules"] = [
            {
                "name": "daily-full-sync",
                "interval": get_env_value("FULL_SYNC_SCHEDULE", "@daily"),
                "job": "full-sync-job"
            },
            {
                "name": "hourly-incremental-sync", 
                "interval": get_env_value("INCREMENTAL_SYNC_SCHEDULE", "@hourly"),
                "job": "incremental-sync-job"
            }
        ]
    
    return config


def main():
    """Generate meltano.yml from configuration"""
    config = generate_meltano_config()
    
    # Write to meltano.yml
    output_path = Path(__file__).parent.parent / "meltano.yml"
    
    # Backup existing if present
    if output_path.exists():
        backup_path = output_path.with_suffix(".yml.backup")
        output_path.rename(backup_path)
        print(f"Backed up existing meltano.yml to {backup_path}")
    
    # Write new configuration
    with open(output_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    
    print(f"Generated meltano.yml successfully!")
    print(f"Project: {get_env_value('PROJECT_NAME', 'meltano-wms-integration')}")
    print(f"Company: {get_env_value('COMPANY_NAME', 'YourCompany')}")
    print(f"Entities: {get_env_value('WMS_ENTITIES', 'allocation,order_hdr,order_dtl')}")


if __name__ == "__main__":
    main()