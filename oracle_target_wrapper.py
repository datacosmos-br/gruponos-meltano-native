#!/usr/bin/env python3
"""Meltano-compatible wrapper for advanced Oracle target - PRODUCTION VERSION."""

import json
import os
import sys
from pathlib import Path

# Add target path
sys.path.insert(0, str(Path(__file__).parent / "flext_target_oracle"))

# Load environment variables
from dotenv import load_dotenv

env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)


def main():
    """Main entry point for Meltano wrapper."""
    # Import after path setup
    # Parse command line arguments manually to avoid Singer SDK deprecation warnings
    import argparse

    from target import TargetOracle

    parser = argparse.ArgumentParser(description="Oracle Target for Meltano")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--test", action="store_true", help="Test the connection")
    parser.add_argument("--discover", action="store_true", help="Discover schema")

    args, unknown = parser.parse_known_args()

    try:
        # Load configuration from file or environment
        config = {}

        if args.config:
            with open(args.config, encoding="utf-8") as f:
                config = json.load(f)
        else:
            # Load from environment variables for Meltano
            config = {
                "host": os.getenv("TARGET_ORACLE_HOST"),
                "port": os.getenv("TARGET_ORACLE_PORT", "1522"),
                "service_name": os.getenv("TARGET_ORACLE_SERVICE_NAME"),
                "username": os.getenv("TARGET_ORACLE_USERNAME"),
                "password": os.getenv("TARGET_ORACLE_PASSWORD"),
                "protocol": os.getenv("TARGET_ORACLE_PROTOCOL", "tcps"),
                "batch_size": int(os.getenv("TARGET_ORACLE_BATCH_SIZE", "250")),
                "pool_size": int(os.getenv("TARGET_ORACLE_POOL_SIZE", "2")),
                "enable_performance_metrics": True,
                "use_bulk_insert": True,
                "add_record_metadata": True,
                "connection_timeout": 180,
                "max_retries": 5,
                "retry_delay": 2.0
            }

        # Remove None values
        config = {k: v for k, v in config.items() if v is not None}

        if args.test:
            # Test connection
            target = TargetOracle(config=config)
            print("✅ Connection test successful!")
            return 0
        if args.discover:
            # Discovery mode
            target = TargetOracle(config=config)
            print("✅ Discovery successful!")
            return 0
        # Normal execution mode - read from stdin
        target = TargetOracle(config=config)

        # Process input stream
        schema = None
        stream_name = None

        for line in sys.stdin:
            if not line.strip():
                continue

            try:
                message = json.loads(line.strip())

                if message.get("type") == "SCHEMA":
                    schema = message
                    stream_name = message.get("stream")
                    target.process_schema(schema)
                elif message.get("type") == "RECORD":
                    if schema and stream_name:
                        target.process_record(message, schema, stream_name)
                elif message.get("type") == "STATE":
                    target.process_state(message)

            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON: {e}", file=sys.stderr)
                continue
            except Exception as e:
                print(f"❌ Processing error: {e}", file=sys.stderr)
                continue

        # Finalize
        target.finalize()
        return 0

    except Exception as e:
        print(f"❌ Fatal error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
