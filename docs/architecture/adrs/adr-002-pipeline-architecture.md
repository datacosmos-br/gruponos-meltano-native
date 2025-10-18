# ADR 002: Pipeline Architecture Pattern
## Table of Contents

- [ADR 002: Pipeline Architecture Pattern](#adr-002-pipeline-architecture-pattern)
  - [Status](#status)
  - [Context](#context)
  - [Decision](#decision)
    - [Full Sync Pipeline](#full-sync-pipeline)
    - [Incremental Sync Pipeline](#incremental-sync-pipeline)
  - [Rationale](#rationale)
    - [Business Requirements Alignment](#business-requirements-alignment)
    - [Technical Benefits](#technical-benefits)
    - [Architecture Patterns](#architecture-patterns)
  - [Consequences](#consequences)
    - [Positive](#positive)
    - [Negative](#negative)
    - [Risks](#risks)
    - [Mitigation Strategies](#mitigation-strategies)
  - [Alternatives Considered](#alternatives-considered)
    - [Alternative 1: Single Pipeline with Modes](#alternative-1-single-pipeline-with-modes)
    - [Alternative 2: Event-Driven Incremental Only](#alternative-2-event-driven-incremental-only)
    - [Alternative 3: Micro-batch Incremental Processing](#alternative-3-micro-batch-incremental-processing)
    - [Alternative 4: Database-Level Change Tracking](#alternative-4-database-level-change-tracking)
    - [Alternative 5: Time-Based Windowing](#alternative-5-time-based-windowing)
  - [Implementation](#implementation)
    - [Pipeline Configuration Structure](#pipeline-configuration-structure)
- [Full sync pipeline configuration](#full-sync-pipeline-configuration)
- [Incremental sync pipeline configuration](#incremental-sync-pipeline-configuration)
    - [Shared Infrastructure Components](#shared-infrastructure-components)
    - [Monitoring and Alerting](#monitoring-and-alerting)
  - [References](#references)
  - [Notes](#notes)


## Status
Accepted

## Context

The gruponos-meltano-native system needs to handle Oracle WMS data integration with requirements for both data consistency/completeness and data freshness. The system must support:

- **Initial Data Loading**: Complete historical data synchronization
- **Ongoing Data Synchronization**: Real-time data updates for operational reporting
- **Data Quality Assurance**: Schema validation and business rule enforcement
- **Error Recovery**: Robust handling of network issues, API failures, and data inconsistencies
- **Performance Optimization**: Efficient processing for different data volumes and frequencies

Key challenges include:
- Oracle WMS API rate limiting and pagination requirements
- Large initial data sets (potentially millions of records)
- Frequent incremental updates (every 2 hours)
- Data transformation complexity and validation requirements
- Network reliability and error recovery needs

## Decision

Implement a **dual pipeline architecture** with separate full sync and incremental sync pipelines:

### Full Sync Pipeline
- **Purpose**: Complete data extraction and loading for data reconciliation
- **Schedule**: Weekly execution
- **Method**: Append-only loading (no duplicates)
- **Scope**: All entities (allocation, order_hdr, order_dtl)
- **Use Case**: Schema changes, data reconciliation, initial loads

### Incremental Sync Pipeline
- **Purpose**: Continuous data synchronization with change detection
- **Schedule**: Every 2 hours
- **Method**: Upsert loading using modification timestamps
- **Scope**: Changed records since last sync
- **Use Case**: Real-time data freshness, operational reporting

Both pipelines use the same underlying infrastructure but with different configurations and execution patterns.

## Rationale

### Business Requirements Alignment

**Data Freshness vs. Consistency Trade-off**:
- Full sync ensures complete, consistent datasets for analytics
- Incremental sync provides operational data freshness
- Dual approach satisfies both analytical and operational needs

**Scalability Considerations**:
- Separate pipelines allow independent scaling
- Different performance characteristics can be optimized separately
- Resource allocation can be tuned per pipeline type

### Technical Benefits

**Performance Optimization**:
- Incremental processing reduces API calls and data transfer
- Full sync can be scheduled during low-usage periods
- Different batch sizes and timeouts per pipeline type

**Error Isolation**:
- Issues in one pipeline don't affect the other
- Independent retry logic and error handling
- Separate monitoring and alerting per pipeline

**Operational Flexibility**:
- Full sync can be triggered manually for data reconciliation
- Incremental sync can be paused during maintenance windows
- Different alerting thresholds per pipeline criticality

### Architecture Patterns

**Pipeline Separation**:
- Clear separation of concerns between bulk and incremental processing
- Independent configuration and deployment
- Separate monitoring and observability

**Shared Infrastructure**:
- Common Meltano orchestration layer
- Shared Singer plugins and connectors
- Common error handling and logging infrastructure

## Consequences

### Positive
- **Performance**: Optimized processing for different data volumes and frequencies
- **Reliability**: Independent error handling and recovery per pipeline
- **Flexibility**: Separate scheduling and configuration capabilities
- **Scalability**: Independent scaling of full vs. incremental workloads
- **Monitoring**: Granular observability and alerting per pipeline type

### Negative
- **Complexity**: Dual pipeline management and coordination
- **Configuration**: Separate configuration management for each pipeline
- **Maintenance**: Additional operational complexity
- **Resource Usage**: Potential resource duplication
- **Testing**: More comprehensive testing requirements

### Risks
- **Configuration Drift**: Inconsistent configurations between pipelines
- **Scheduling Conflicts**: Potential overlaps or gaps in data coverage
- **Monitoring Complexity**: Separate alerting and monitoring per pipeline
- **Operational Overhead**: Managing two separate pipeline lifecycles

### Mitigation Strategies
- **Shared Configuration**: Common base configuration with pipeline-specific overrides
- **Centralized Scheduling**: Single scheduling system managing both pipelines
- **Unified Monitoring**: Common monitoring dashboard with pipeline-specific views
- **Automated Testing**: Comprehensive integration tests covering both pipelines
- **Documentation**: Clear operational procedures for managing dual pipelines

## Alternatives Considered

### Alternative 1: Single Pipeline with Modes
- **Description**: One pipeline that switches between full and incremental modes
- **Pros**: Simpler architecture, single point of management
- **Cons**: Complex mode switching logic, performance compromises, inflexible scheduling
- **Rejected**: Mode switching complexity outweighs benefits, inflexible for different requirements

### Alternative 2: Event-Driven Incremental Only
- **Description**: Real-time event streaming from Oracle WMS
- **Pros**: Most up-to-date data, efficient change detection
- **Cons**: Requires Oracle WMS webhook support, complex event processing, potential data loss
- **Rejected**: Oracle WMS doesn't provide real-time events, would require significant custom development

### Alternative 3: Micro-batch Incremental Processing
- **Description**: Frequent small batches instead of hourly incremental sync
- **Pros**: More frequent updates, smaller failure domains
- **Cons**: Increased API load, more complex coordination, higher operational overhead
- **Rejected**: Oracle WMS API rate limits would be exceeded, unnecessary complexity for current requirements

### Alternative 4: Database-Level Change Tracking
- **Description**: Direct database CDC instead of API-based incremental sync
- **Pros**: Most efficient change detection, real-time capabilities
- **Cons**: No direct database access to Oracle WMS, security restrictions, architectural violations
- **Rejected**: Security and architectural constraints prevent direct database access

### Alternative 5: Time-Based Windowing
- **Description**: Fixed time windows for incremental processing
- **Pros**: Predictable processing windows, simpler scheduling
- **Cons**: Potential data gaps, less efficient for sparse changes, fixed batch sizes
- **Rejected**: Less efficient than timestamp-based incremental sync, potential data consistency issues

## Implementation

### Pipeline Configuration Structure

```yaml
# Full sync pipeline configuration
full_sync_pipeline:
  name: "tap-oracle-wms-full"
  schedule: "@weekly"
  config:
    enable_incremental: false
    entities: ["allocation", "order_hdr", "order_dtl"]
    page_size: 500
    timeout: 1800  # 30 minutes
    batch_size: 5000
  target:
    name: "target-oracle-full"
    load_method: "append_only"

# Incremental sync pipeline configuration
incremental_pipeline:
  name: "tap-oracle-wms-incremental"
  schedule: "0 */2 * * *"  # Every 2 hours
  config:
    enable_incremental: true
    replication_key: "mod_ts"
    entities: ["allocation", "order_hdr", "order_dtl"]
    page_size: 500
    timeout: 600   # 10 minutes
    batch_size: 1000
  target:
    name: "target-oracle-incremental"
    load_method: "upsert"
```

### Shared Infrastructure Components

```python
class PipelineInfrastructure:
    """Shared infrastructure for both pipeline types."""

    def __init__(self):
        self.meltano_client = MeltanoClient()
        self.error_handler = RailwayErrorHandler()
        self.monitoring = FLEXTMonitoring()

    def execute_pipeline(self, pipeline_config: dict) -> FlextResult[PipelineResult]:
        """Execute pipeline with shared error handling and monitoring."""
        return (
            self._validate_config(pipeline_config)
            .flat_map(lambda _: self.meltano_client.run_pipeline(pipeline_config))
            .map(lambda result: self._process_result(result, pipeline_config))
            .map_error(lambda error: self._handle_pipeline_error(error, pipeline_config))
        )
```

### Monitoring and Alerting

```python
class PipelineMonitoring:
    """Monitoring infrastructure for pipeline operations."""

    def monitor_full_sync(self, result: PipelineResult) -> None:
        """Monitor full sync pipeline with weekly expectations."""
        if result.duration > timedelta(hours=2):
            self.alert_manager.send_alert(
                "Full sync exceeded 2-hour threshold",
                severity="WARNING"
            )

    def monitor_incremental_sync(self, result: PipelineResult) -> None:
        """Monitor incremental sync with 2-hour expectations."""
        if result.duration > timedelta(minutes=30):
            self.alert_manager.send_alert(
                "Incremental sync exceeded 30-minute threshold",
                severity="WARNING"
            )
```

## References

- [Meltano Pipeline Patterns](https://docs.meltano.com/concepts/pipelines)
- [Singer Incremental Replication](https://github.com/singer-io/getting-started/blob/master/docs/SPEC.md#replication)
- [Oracle WMS API Documentation](https://docs.oracle.com/en/cloud/saas/supply-chain-management/wms-api/)
- [ETL Pipeline Architecture Patterns](https://www.oreilly.com/library/view/data-pipeline-design/9781492085708/)
- [ADR 001: Technology Stack Selection](adr-001-technology-stack.md)

## Notes

The dual pipeline architecture provides the best balance of data freshness, consistency,
     and operational flexibility. The separation allows each pipeline to be optimized for its specific use case while sharing common infrastructure components.

Future evolution may include:
- Event-driven incremental processing if Oracle WMS adds webhook support
- Adaptive batch sizing based on data volume patterns
- Machine learning-based scheduling optimization