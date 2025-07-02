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
    echo "$(date +'%Y-%m-%d %H:%M:%S') [${entity}] $1"
}

# Main pipeline simulation loop
entity="allocation"
schedule_name="allocation_incremental_sync"

log_with_timestamp "Starting simple pipeline simulation for ${entity}"
log_with_timestamp "Schedule: ${schedule_name}"
log_with_timestamp "Requirement: incremental a cada minuto"

# Simulation loop - run every minute
iteration=1
while true; do
    start_time=$(date +%s)
    log_with_timestamp "Iteration ${iteration}: Starting sync simulation..."
    
    # Simulate meltano run (since tap-oracle-wms may not be ready yet)
    log_with_timestamp "Simulating: meltano run ${schedule_name}"
    
    # Try actual meltano run first, fallback to simulation
    if command -v meltano >/dev/null 2>&1; then
        if meltano install >/dev/null 2>&1 && meltano run "${schedule_name}" 2>&1; then
            end_time=$(date +%s)
            duration=$((end_time - start_time))
            log_with_timestamp "Real sync completed successfully in ${duration} seconds"
        else
            # Fallback to simulation
            sleep 2  # Simulate processing time
            end_time=$(date +%s)
            duration=$((end_time - start_time))
            simulated_records=$((RANDOM % 100 + 10))
            log_with_timestamp "SIMULATION: Processed ${simulated_records} records in ${duration} seconds"
            log_with_timestamp "NOTE: This is a simulation - real tap-oracle-wms will replace this"
        fi
    else
        sleep 2  # Simulate processing
        end_time=$(date +%s)
        duration=$((end_time - start_time))
        log_with_timestamp "SIMULATION: Meltano not available, simulated processing in ${duration} seconds"
    fi
    
    ((iteration++))
    
    # Wait for next minute (calculate remaining seconds)
    current_second=$(date +%S)
    sleep_time=$((60 - current_second))
    
    if [ ${sleep_time} -gt 0 ]; then
        log_with_timestamp "Waiting ${sleep_time} seconds for next minute..."
        sleep "${sleep_time}"
    fi
done
