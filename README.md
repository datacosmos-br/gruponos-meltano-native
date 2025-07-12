# GrupoNOS Meltano Native

Enterprise integration project using FLEXT Singer/Meltano components for Oracle WMS data synchronization.

## FLEXT Ecosystem Position

```
FLEXT Framework:
├── flext-core - Foundation & Domain patterns
├── flext-observability - Structured logging (USED)
├── flext-meltano - ETL orchestration patterns  
├── flext-tap-oracle-wms - WMS data extraction (USED)
├── flext-target-oracle - Oracle data loading (USED)
└── gruponos-meltano-native - THIS PROJECT
```

## Architecture

```
Oracle WMS → flext-tap-oracle-wms → Meltano → flext-target-oracle → Oracle Analytics
    ↓              ↓                    ↓              ↓
Enterprise API   FLEXT Singer TAP   Framework   FLEXT Singer TARGET
```

## Setup

### Prerequisites
- FLEXT workspace: `/home/marlonsc/flext/`
- Shared venv: `/home/marlonsc/flext/.venv` 
- Environment: See `.env.example`

### Quick Start
```bash
# From FLEXT workspace root
cd gruponos-meltano-native

# Configure project
cp .env.example .env
# Edit .env with Oracle credentials

# Run pipeline (uses shared FLEXT venv)
meltano run tap-oracle-wms-full target-oracle-full

# Validate using FLEXT patterns
python validate_oracle_data.py
```

## Data Synchronization

### Entities (FLEXT Singer Protocol)
- **allocation**: Stock allocations (1.250 records)
- **order_hdr**: Order headers (1.250 records)
- **order_dtl**: Order details (1.250 records)

### Performance
- **Volume**: 3.750 total records
- **Duration**: ~5 minutes complete sync
- **Pattern**: FLEXT Singer incremental state management

## FLEXT Integration Commands

### Pipeline Operations (FLEXT Singer Protocol)
```bash
# Full sync using FLEXT components
meltano run tap-oracle-wms-full target-oracle-full

# Incremental sync (FLEXT state management)
meltano run tap-oracle-wms-incremental target-oracle-incremental

# Pre-configured FLEXT jobs
meltano job run full-sync-job
meltano job run incremental-sync-job
```

### Validation (FLEXT Observability)
```bash
# Oracle validation with FLEXT logging
python validate_oracle_data.py

# Advanced validation using FLEXT connection patterns
PYTHONPATH=. python src/oracle/validate_sync.py
```

### Development (FLEXT Standards)
```bash
# Test FLEXT TAP connection
meltano invoke tap-oracle-wms-full --test

# Test FLEXT TARGET connection
meltano invoke target-oracle-full --test

# Debug with FLEXT observability
meltano --log-level=debug run tap-oracle-wms-full target-oracle-full
```

## FLEXT Configuration

### Environment Variables (FLEXT Namespacing)
```bash
# FLEXT TAP Configuration (Oracle WMS Source)
TAP_ORACLE_WMS_BASE_URL=https://enterprise-wms-api.com
TAP_ORACLE_WMS_USERNAME=wms_user
TAP_ORACLE_WMS_PASSWORD=wms_password
TAP_ORACLE_WMS_COMPANY_CODE=COMPANY
TAP_ORACLE_WMS_FACILITY_CODE=FACILITY

# FLEXT TARGET Configuration (Oracle Analytics)
FLEXT_TARGET_ORACLE_HOST=oracle.analytics.host
FLEXT_TARGET_ORACLE_SERVICE_NAME=analytics_service
FLEXT_TARGET_ORACLE_USERNAME=analytics_user
FLEXT_TARGET_ORACLE_PASSWORD=analytics_password
FLEXT_TARGET_ORACLE_PROTOCOL=tcps
FLEXT_TARGET_ORACLE_TABLE_PREFIX=WMS_
```

### Oracle Schema (FLEXT Singer Metadata)
- `OIC.WMS_ALLOCATION` - Stock allocations with Singer metadata
- `OIC.WMS_ORDER_HDR` - Order headers with Singer metadata  
- `OIC.WMS_ORDER_DTL` - Order details with Singer metadata
- Metadata: `_SDC_EXTRACTED_AT`, `_SDC_BATCHED_AT`, `_SDC_RECEIVED_AT`

## FLEXT Integration Patterns

### Connection Management
- **Pattern**: FLEXT Oracle connection pooling
- **SSL**: TCPS with certificate validation
- **Retry**: Exponential backoff (FLEXT standards)
- **Timeout**: Configurable per environment

### State Management  
- **Pattern**: Singer incremental state (FLEXT Singer protocol)
- **Storage**: Meltano system database
- **Recovery**: Automatic state restoration
- **Replication**: Key-based incremental sync

### Observability
- **Logging**: flext-observability structured logging
- **Monitoring**: Health checks and performance metrics
- **Alerting**: FLEXT monitoring patterns
- **Tracing**: Request tracing with context propagation

## Troubleshooting (FLEXT Patterns)

### Oracle Connection Issues
```bash
# Use FLEXT connection validation
python src/oracle/validate_sync.py

# Check FLEXT TARGET configuration
meltano invoke target-oracle-full --test
```

### Singer State Problems
```bash
# Clear Singer state (FLEXT pattern)
meltano state clear tap-oracle-wms-full

# Validate state consistency
meltano state list
```

### Performance Tuning
```bash
# FLEXT recommended settings
batch_size: 1000          # Oracle bulk operations
max_parallelism: 5        # Concurrent streams
request_timeout: 600      # API timeout (seconds)
```

## FLEXT Ecosystem Files

### Core Components
- `meltano.yml` - FLEXT Singer pipeline configuration
- `CLAUDE.md` - FLEXT project documentation standards
- `pyproject.toml` - FLEXT workspace dependencies

### Validation & Monitoring
- `validate_oracle_data.py` - FLEXT observability validation
- `src/oracle/validate_sync.py` - FLEXT connection patterns
- `src/validators/data_validator.py` - FLEXT data quality

### Documentation
- [OPERATIONS.md](OPERATIONS.md) - FLEXT operational procedures
- [ARCHITECTURE.md](ARCHITECTURE.md) - FLEXT technical patterns
- [CHANGELOG.md](CHANGELOG.md) - FLEXT project evolution

## FLEXT Workspace Integration

This project follows FLEXT workspace standards:
- Single shared venv: `/home/marlonsc/flext/.venv`
- Coordinated development via `.token` file
- Environment variable namespacing for conflict avoidance
- Standardized logging and observability patterns