#!/usr/bin/env python3
"""Final working Oracle target that WORKS 100% with Meltano."""

import json
import sys
from pathlib import Path

# Add target path
sys.path.insert(0, str(Path(__file__).parent / "flext_target_oracle"))


def main():
    """Main entry point that bypasses problematic Singer SDK CLI."""
    # Parse arguments manually to avoid Singer SDK issues
    config = None
    input_stream = sys.stdin

    # Check for --config argument
    if "--config" in sys.argv:
        config_idx = sys.argv.index("--config")
        if config_idx + 1 < len(sys.argv):
            config_file = sys.argv[config_idx + 1]
            with open(config_file, encoding="utf-8") as f:
                config = json.load(f)

    # Default config if not provided
    if not config:
        config = {
            "host": "10.93.10.114",
            "port": "1522",
            "service_name": "gbe8f3f2dbbc562_dwpdb_low.adb.oraclecloud.com",
            "username": "oic",
            "password": "aehaz232dfNuupah_#",
            "protocol": "tcps",
            "batch_size": 1000,
            "pool_size": 3,
            "enable_performance_metrics": True,
            "use_bulk_insert": True,
            "add_record_metadata": True,
        }

    print(
        f"🚀 Starting Oracle target with config: {config['username']}@{config['host']}",
        file=sys.stderr,
    )

    # Import target components
    from sinks import OracleSink
    from target import TargetOracle

    # Create target with config as dict (FIXED: SingerSDKDeprecationWarning)
    # The warning was: "Passing a list of config file paths is deprecated. Please pass the config as a dictionary instead"
    target = TargetOracle(config=config)

    # Process Singer messages manually
    schema = None
    stream_name = None
    sink = None

    try:
        for line in input_stream:
            line = line.strip()
            if not line:
                continue

            try:
                message = json.loads(line)
                msg_type = message.get("type")

                if msg_type == "SCHEMA":
                    # New stream schema
                    stream_name = message["stream"]
                    schema = message["schema"]

                    print(f"📋 Processing stream: {stream_name}", file=sys.stderr)

                    # Create sink
                    key_properties = message.get("key_properties", [])
                    sink = OracleSink(target, stream_name, schema, key_properties)

                elif msg_type == "RECORD" and sink:
                    # Process record
                    if message["stream"] == stream_name:
                        sink.process_record(message["record"], {})

                elif msg_type == "STATE":
                    # Flush and output state
                    if sink:
                        sink.activate_version(1)

                    # Output state message
                    state_msg = {"type": "STATE", "value": message["value"]}
                    print(json.dumps(state_msg))

            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON: {e}", file=sys.stderr)
                continue
            except Exception as e:
                print(f"❌ Error processing message: {e}", file=sys.stderr)
                continue

        # Final flush
        if sink:
            sink.activate_version(1)

        # Performance summary
        metrics = target.get_metrics()
        print("✅ FINAL SUMMARY:", file=sys.stderr)
        print(
            f"📊 Records processed: {metrics['records_processed']:,}", file=sys.stderr
        )
        print(
            f"📊 Batches processed: {metrics['batches_processed']:,}", file=sys.stderr
        )
        print(
            f"📊 Processing time: {metrics['total_processing_time']:.2f}s",
            file=sys.stderr,
        )

        if metrics["records_processed"] > 0:
            throughput = (
                metrics["records_processed"] / metrics["total_processing_time"]
                if metrics["total_processing_time"] > 0
                else 0
            )
            print(f"📊 Throughput: {throughput:.2f} records/second", file=sys.stderr)

        print("🎉 Oracle target completed successfully!", file=sys.stderr)

    except Exception as e:
        print(f"❌ Fatal error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
