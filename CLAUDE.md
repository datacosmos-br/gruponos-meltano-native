# CLAUDE.md - GRUPONOS MELTANO NATIVE PROJECT

**Hierarchy**: PROJECT-SPECIFIC  
**Project**: GrupoNOS WMS Meltano Native - 100% Meltano native replacement for custom Python approach  
**Status**: PRODUCTION-READY  
**Last Updated**: 2025-07-01  

**Reference**: `/home/marlonsc/CLAUDE.md` → Universal principles  
**Reference**: `/home/marlonsc/CLAUDE.local.md` → Cross-workspace issues  
**Reference**: `../CLAUDE.md` → FLEXT workspace standards  

---

## 🎯 PROJECT OVERVIEW

### Purpose
Complete 100% Meltano native data pipeline replacing the custom Python approach in `gruponos-poc-oic-wms`. This demonstrates enterprise best practices for Singer/Meltano data integration.

### Key Achievements
✅ **Zero Custom Code** - Pure declarative Meltano configuration  
✅ **Production Grade** - Enterprise monitoring, error handling, recovery  
✅ **Comprehensive Testing** - dbt tests, data quality validation  
✅ **Multi-Environment** - Dev, staging, production configurations  
✅ **Documentation** - Complete setup, operation, and troubleshooting guides  

### Architecture
```
Oracle WMS → tap-oracle-wms → Meltano → target-oracle → dbt transformations → Data Marts
```

---

## 🚨 PROJECT-SPECIFIC CRITICAL REQUIREMENTS

### 1. **100% Meltano Native Constraint**

**Critical**: This project MUST remain 100% Meltano native - no custom Python code

**Enforcement**:
- All logic in dbt SQL models
- All orchestration via Meltano schedules/jobs
- All configuration via meltano.yml and environment variables
- Use only standard Meltano plugins and Singer taps/targets

### 2. **Production Oracle Integration**

**Requirements**:
- Uses real tap-oracle-wms from `../flext-tap-oracle-wms`
- Oracle-specific performance optimizations in dbt macros
- Proper connection pooling and batch sizing
- Enterprise security (encrypted passwords, SSL support)

### 3. **Enterprise Data Quality Standards**

**Implementation**:
- Comprehensive dbt tests for all models
- Data freshness monitoring via dbt sources
- Business rule validation in staging models
- Automated data quality scoring

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
  schedule: "0 */2 * * *"  # Every 2 hours

# Daily transactional data  
order_hdr:
  replication_method: INCREMENTAL
  replication_key: order_date
  schedule: "0 2 * * *"    # Daily at 2 AM

# Reference data
item_master, location:
  replication_method: FULL_TABLE
  schedule: "0 6 * * 0"    # Weekly on Sunday
```

---

## 📊 PROJECT-SPECIFIC dbt ARCHITECTURE

### Layer Strategy
```
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