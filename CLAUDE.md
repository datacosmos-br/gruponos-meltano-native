# CLAUDE.md - GRUPONOS MELTANO NATIVE PROJECT

**Hierarchy**: PROJECT-SPECIFIC (FLEXT Workspace)
**Project**: GrupoNOS WMS Meltano Native - Enterprise FLEXT Singer/Meltano Integration
**Status**: OPERATIONAL  
**Last Updated**: 2025-07-12

**Reference**: `/home/marlonsc/CLAUDE.md` → Universal principles  
**Reference**: `/home/marlonsc/CLAUDE.local.md` → Cross-workspace issues  
**Reference**: `../CLAUDE.md` → FLEXT workspace standards

---

## 🎯 FLEXT PROJECT OVERVIEW

### Purpose

Enterprise data integration project using FLEXT Singer/Meltano components to synchronize Oracle WMS data with Oracle Analytics. Demonstrates FLEXT ecosystem patterns for enterprise ETL operations.

### FLEXT Components Used

✅ **flext-tap-oracle-wms** - WMS data extraction with Singer protocol  
✅ **flext-target-oracle** - Oracle data loading with connection pooling  
✅ **flext-observability** - Structured logging and monitoring  
✅ **flext-meltano** - ETL orchestration patterns and state management

### FLEXT Architecture

```ascii
Oracle WMS → flext-tap-oracle-wms → Meltano → flext-target-oracle → Oracle Analytics
           FLEXT Singer TAP      Framework   FLEXT Singer TARGET
```

---

## 🚨 FLEXT PROJECT REQUIREMENTS

### 1. **FLEXT Singer Protocol Compliance**

**Critical**: Project MUST use FLEXT Singer components exclusively

**Enforcement**:
- flext-tap-oracle-wms for data extraction
- flext-target-oracle for data loading  
- flext-observability for all logging
- FLEXT naming conventions and patterns

### 2. **FLEXT Workspace Integration**

**Requirements**:
- Shared FLEXT venv: `/home/marlonsc/flext/.venv`
- Environment variable namespacing (TAP_*, FLEXT_TARGET_*)
- Coordinated development via `.token` file
- FLEXT workspace standards compliance

### 3. **Enterprise Oracle Integration (FLEXT Patterns)**

**Implementation**:
- FLEXT Oracle connection pooling
- TCPS/SSL with certificate validation
- FLEXT retry patterns with exponential backoff
- Singer metadata with FLEXT standards

---

## 🔧 PROJECT-SPECIFIC TECHNICAL CONFIGURATION

### Environment Structure

```bash
# Three-tier environment strategy
MELTANO_ENVIRONMENT=dev      # Development with smaller batches
MELTANO_ENVIRONMENT=staging  # Pre-production validation
MELTANO_ENVIRONMENT=prod     # Production with full performance tuning
```

### Critical Environment Variables

```bash
# WMS Source (per environment)
WMS_ORACLE_HOST=wms-{env}-oracle.gruponos.local
WMS_ORACLE_SID=WMS{ENV}
WMS_ORACLE_USERNAME=wms_reader_{env}

# Target Analytics Database
TARGET_ORACLE_HOST=analytics-{env}-oracle.gruponos.local
TARGET_ORACLE_SERVICE_NAME=ANA{ENV}
TARGET_ORACLE_SCHEMA=WMS_SYNC_{ENV}

# Performance Tuning
WMS_BATCH_SIZE=1000          # Dev: 1K, Staging: 2K, Prod: 5K
TARGET_BATCH_SIZE=5000       # Dev: 5K, Staging: 7K, Prod: 10K
DBT_THREADS=4                # Dev: 4, Staging: 6, Prod: 8
```

### Stream Configuration Strategy

```yaml
# High-frequency operational data
allocation:
  replication_method: INCREMENTAL
  replication_key: last_updated
  schedule: "0 */2 * * *" # Every 2 hours

# Daily transactional data
order_hdr:
  replication_method: INCREMENTAL
  replication_key: order_date
  schedule: "0 2 * * *" # Daily at 2 AM

# Reference data
item_master, location:
  replication_method: FULL_TABLE
  schedule: "0 6 * * 0" # Weekly on Sunday
```

---

## 📊 PROJECT-SPECIFIC dbt ARCHITECTURE

### Layer Strategy

```ascii
sources (Raw WMS tables)
    ↓
staging (Data cleaning + validation)
    ↓
intermediate (Business logic calculations)
    ↓
marts (Analytics-ready facts and dimensions)
```

### Business Logic Implementation

**Staging Models**:

- `stg_wms_allocation` - Allocation data with quality scoring
- `stg_wms_orders` - Order data with calculated totals validation
- `stg_wms_items` - Item master with business classifications
- `stg_wms_locations` - Location data with utilization metrics

**Intermediate Models**:

- `int_allocation_performance` - Performance benchmarking vs location/user averages

**Mart Models**:

- `dim_items` - Item dimension with velocity and value categorization
- `fact_allocation_performance` - Daily allocation performance metrics
- `fact_inventory_movement` - Comprehensive movement tracking and analysis

### Oracle-Specific Optimizations

```sql
-- Custom macros for Oracle performance
{{ oracle_analyze_table() }}              -- Update table statistics
{{ oracle_running_totals() }}             -- Efficient windowing
{{ oracle_percentile_analysis() }}        -- Performance benchmarking
{{ oracle_partition_by_date() }}          -- Partition management
```

---

## 🔄 PROJECT-SPECIFIC OPERATIONAL PROCEDURES

### Daily Operations

```bash
# Health check (automated)
make health-check

# Run allocation sync (every 2 hours)
make run-allocation

# Monitor performance
make status
tail -f logs/meltano/meltano.log
```

### Weekly Operations

```bash
# Master data refresh (Sundays)
make run-master-data

# Performance review
cd transform && dbt docs generate --profiles-dir profiles

# Data quality review
make test-data-quality
```

### Emergency Procedures

```bash
# If pipeline fails
1. Check health: make health-check
2. Test connections: make test-connections
3. Check recent logs: make logs
4. Run individual components:
   - make run-extract    # Test extraction only
   - make run-transform  # Test transformations only

# If data quality issues
1. Run dbt tests with details: cd transform && dbt test --store-failures --profiles-dir profiles
2. Check source freshness: cd transform && dbt source freshness --profiles-dir profiles
3. Validate business rules in staging models
```

---

## 🚀 PROJECT-SPECIFIC DEPLOYMENT STRATEGY

### Environment Promotion

```bash
# Development → Staging
make deploy-staging

# Staging → Production
make deploy-prod
```

### Production Deployment Checklist

1. ✅ All dbt tests pass in staging
2. ✅ Data volume validation completed
3. ✅ Performance benchmarks met
4. ✅ Oracle connection pool properly configured
5. ✅ Monitoring and alerting functional
6. ✅ Backup and recovery procedures tested

### Rollback Strategy

```bash
# If production deployment fails
1. Revert to previous Meltano state
2. Restore dbt models from git
3. Validate data integrity
4. Restart monitoring
```

---

## 📈 PROJECT-SPECIFIC SUCCESS METRICS

### Technical Metrics

- **Extraction Performance**: >1000 records/second from WMS
- **Load Performance**: >5000 records/second to target
- **dbt Runtime**: <30 minutes for full refresh
- **Data Freshness**: <2 hours for operational data
- **Test Coverage**: 100% of critical business rules tested

### Business Metrics

- **Allocation Processing**: <1 hour average processing time
- **Order Fulfillment**: >85% fulfillment rate
- **Data Quality**: >95% excellent quality score
- **System Availability**: >99.5% uptime

### Monitoring Dashboard

```sql
-- Key Performance Indicators (KPIs) available in marts
SELECT
  allocation_date,
  avg_processing_time_seconds,
  fulfillment_rate_pct,
  excellent_quality_rate_pct,
  overall_efficiency_score
FROM fact_allocation_performance
WHERE allocation_date >= current_date - 7;
```

---

## 🔧 PROJECT-SPECIFIC TROUBLESHOOTING

### Common Issues

**Oracle Connection Timeouts**:

```bash
# Check connection pool settings
grep -r "connection_pool\|timeout" .env meltano.yml

# Test individual connection
meltano invoke tap-oracle-wms --test-connection --timeout 60
```

**dbt Model Failures**:

```bash
# Run with debug logging
cd transform && dbt run --profiles-dir profiles --debug --select failing_model

# Check Oracle-specific syntax
# Ensure date functions use Oracle syntax (SYSDATE, TO_DATE, etc.)
```

**Performance Issues**:

```bash
# Check batch sizes
grep -r "batch_size" .env meltano.yml

# Monitor Oracle sessions
# Check v$session during pipeline runs

# Review dbt compilation
cd transform && dbt compile --profiles-dir profiles
```

---

## 🏆 PROJECT BEST PRACTICES DEMONSTRATED

### Meltano Native Patterns

- Environment-specific configuration inheritance
- Plugin-based architecture with zero custom code
- State management via Singer protocol
- Schedule management via Meltano jobs

### Enterprise dbt Patterns

- Source-staging-intermediate-mart layering
- Comprehensive testing strategy
- Oracle-specific performance optimizations
- Business logic documentation

### Oracle Integration Patterns

- Connection pooling optimization
- Batch size tuning per environment
- Table statistics management
- Partitioning strategies

---

**Authority**: This project demonstrates production-ready Meltano native architecture
**Integration**: Replaces custom Python approach with maintainable declarative configuration
**Maintenance**: Self-documenting via dbt, monitored via built-in health checks

**Critical Note**: Maintain 100% Meltano native approach - resist temptation to add custom Python code
