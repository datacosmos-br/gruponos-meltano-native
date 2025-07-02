#!/bin/bash
set -euo pipefail

# Change to project directory
cd "/home/marlonsc/flext/gruponos-meltano-native"

# Load environment
set -a
source .env 2>/dev/null || true
set +a

# Function to log with timestamp
log_with_timestamp() {
    echo "$(date +'%Y-%m-%d %H:%M:%S') [allocation] $1"
}

# Pipeline variables
entity="allocation"
tap_config="tap-config.json"
state_file="state/allocation_state.json"
catalog_file="catalog_allocation_incremental.json"

log_with_timestamp "Starting REAL incremental pipeline for allocation"
log_with_timestamp "Using tap-oracle-wms + simple_target_oracle"
log_with_timestamp "Requirement: incremental a cada minuto"

# Create catalog for incremental sync
create_incremental_catalog() {
    cat > "${catalog_file}" << CATALOG_EOF
{
  "streams": [
    {
      "tap_stream_id": "allocation",
      "stream": "allocation",
      "schema": {
        "type": "object",
        "properties": {}
      },
      "metadata": [
        {
          "breadcrumb": [],
          "metadata": {
            "inclusion": "selected",
            "selected": true,
            "table-key-properties": [],
            "forced-replication-method": "incremental"
          }
        }
      ]
    }
  ]
}
CATALOG_EOF
}

# Main loop - run every minute
iteration=1
while true; do
    start_time=$(date +%s)
    log_with_timestamp "Iteration ${iteration}: Starting REAL sync..."
    
    # Create catalog
    create_incremental_catalog
    
    # Build pipeline command
    tap_command="python /home/marlonsc/flext/flext-tap-oracle-wms/tap_oracle_wms/main.py"
    tap_command+=" --config ${tap_config}"
    tap_command+=" --catalog ${catalog_file}"
    
    if [ -f "${state_file}" ]; then
        tap_command+=" --state ${state_file}"
        log_with_timestamp "Using existing state file"
    fi
    
    target_command="python simple_target_oracle.py"
    
    # Execute pipeline with state management
    log_with_timestamp "Executing: ${tap_command} | ${target_command}"
    
    # Run pipeline and capture state
    ${tap_command} 2>&1 | tee >(grep '^{"type": "STATE"' > "${state_file}.tmp") | ${target_command} 2>&1
    
    exit_code=$?
    
    # Update state file if new state was captured
    if [ -s "${state_file}.tmp" ]; then
        tail -1 "${state_file}.tmp" > "${state_file}"
        log_with_timestamp "State updated"
    fi
    rm -f "${state_file}.tmp"
    
    # Clean up catalog
    rm -f "${catalog_file}"
    
    end_time=$(date +%s)
    duration=$((end_time - start_time))
    
    if [ ${exit_code} -eq 0 ]; then
        log_with_timestamp "REAL SYNC: Completed successfully in ${duration} seconds"
    else
        log_with_timestamp "WARNING: Sync had issues but continuing (exit code: ${exit_code})"
    fi
    
    ((iteration++))
    
    # Wait for next minute
    current_second=$(date +%S)
    sleep_time=$((60 - current_second))
    
    if [ ${sleep_time} -gt 0 ]; then
        log_with_timestamp "Waiting ${sleep_time} seconds for next minute..."
        sleep "${sleep_time}"
    fi
done
