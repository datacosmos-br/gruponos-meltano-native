# 🔧 Troubleshooting Guide

## Common Issues and Solutions

### 1. Data Validation Errors

#### Problem: `'540' is not of type 'number'`
**Cause**: Oracle WMS API returns numeric fields as strings  
**Solution**: 
```bash
# Option 1: Disable strict validation (recommended for development)
# In meltano.yml, set: validate_records: false

# Option 2: Use professional data validator
python3 src/validators/data_validator.py
```

#### Problem: Schema validation failures
**Cause**: Data types don't match schema expectations  
**Solution**:
```bash
# Check conversion stats
make validate-data

# Reset and retry with lenient validation
make reset-state
make incremental-sync
```

### 2. Oracle Connection Issues

#### Problem: SSL Certificate verification failed
**Error**: `certificate verify failed: IP address mismatch`  
**Solution**:
```bash
# Test connection with diagnostic info
python3 src/oracle/connection_manager.py

# Check current SSL settings
grep -r ssl .env meltano.yml

# For development, use fallback connection
export FLEXT_TARGET_ORACLE_SSL_DN_MATCH=false
```

#### Problem: Connection timeouts
**Cause**: Network latency or Oracle load  
**Solution**:
```bash
# Increase timeout values
export FLEXT_TARGET_ORACLE_TIMEOUT=120
export FLEXT_TARGET_ORACLE_RETRIES=5

# Test with fallback protocol
export FLEXT_TARGET_ORACLE_PROTOCOL=tcp
```

### 3. Sync Process Issues

#### Problem: Sync process hangs
**Symptoms**: Process shows as running but no progress  
**Solution**:
```bash
# Check process status
make status

# Stop hung processes
make stop-sync

# Clean state and restart
make reset-state
make incremental-sync
```

#### Problem: Background sync fails silently
**Cause**: Process exits without proper logging  
**Solution**:
```bash
# Check error logs
make logs

# Analyze failures
make analyze-failures

# Run in foreground for debugging
source /home/marlonsc/flext/.venv/bin/activate
set -a && source .env && set +a
meltano run tap-oracle-wms target-oracle
```

### 4. Performance Issues

#### Problem: Slow data extraction
**Cause**: Large result sets or network latency  
**Solution**:
```bash
# Reduce batch size for testing
# In meltano.yml:
# tap-oracle-wms:
#   config:
#     page_size: 5  # Smaller batches

# Enable compression
# target-oracle:
#   config:
#     use_compression: true
```

#### Problem: Oracle table locks
**Cause**: Long-running transactions  
**Solution**:
```sql
-- Check for locks (as DBA)
SELECT * FROM v$locked_object;

-- Kill blocking sessions if needed
ALTER SYSTEM KILL SESSION 'sid,serial#';
```

### 5. Environment Issues

#### Problem: Virtual environment not found
**Error**: `venv: MISSING` in status  
**Solution**:
```bash
# Check path
ls -la /home/marlonsc/flext/.venv/bin/activate

# If missing, recreate
cd /home/marlonsc/flext
python3 -m venv .venv
source .venv/bin/activate
pip install -r gruponos-meltano-native/requirements.txt
```

#### Problem: Environment variables not loaded
**Cause**: .env file not sourced correctly  
**Solution**:
```bash
# Test environment
make env

# Manual verification
cd /home/marlonsc/flext/gruponos-meltano-native
source /home/marlonsc/flext/.venv/bin/activate
set -a && source .env && set +a
env | grep FLEXT_TARGET_ORACLE
```

## Emergency Procedures

### Complete System Reset
```bash
# Stop all processes
make stop-sync

# Clean all state
make reset-state

# Clean old logs
make clean-logs

# Test environment
make env

# Validate Oracle connection
make validate-oracle

# Start fresh sync
make incremental-sync
```

### Health Check
```bash
# Comprehensive system check
make health-check

# Monitor in real-time
make monitor
```

## Log Analysis

### Understanding Log Patterns
- **INFO**: Normal operation messages
- **WARNING**: Non-fatal issues (connection retries, type conversions)
- **ERROR**: Failed operations that stop processing

### Key Log Locations
- Sync logs: `logs/sync/`
- Error logs: `logs/error/`
- Validation logs: `logs/validation/`

### Emergency Contacts
- **Database Issues**: Contact Oracle DBA team
- **Network Issues**: Contact infrastructure team
- **Application Issues**: Check this troubleshooting guide first