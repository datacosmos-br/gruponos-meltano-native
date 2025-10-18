# C4 Model Architecture Documentation
## Table of Contents

- [C4 Model Architecture Documentation](#c4-model-architecture-documentation)
  - [📋 C4 Model Overview](#-c4-model-overview)
  - [🌐 1. System Context (C4 Level 1)](#-1-system-context-c4-level-1)
    - [System Purpose](#system-purpose)
    - [Context Diagram](#context-diagram)
    - [Key Relationships](#key-relationships)
  - [🏗️ 2. Container Architecture (C4 Level 2)](#-2-container-architecture-c4-level-2)
    - [Container Diagram](#container-diagram)
    - [Container Descriptions](#container-descriptions)
      - [**CLI Application**](#cli-application)
      - [**API Service**](#api-service)
      - [**Pipeline Orchestrator**](#pipeline-orchestrator)
      - [**Configuration Manager**](#configuration-manager)
      - [**Monitoring Service**](#monitoring-service)
  - [🔧 3. Component Architecture (C4 Level 3)](#-3-component-architecture-c4-level-3)
    - [ETL Pipeline Components](#etl-pipeline-components)
    - [Data Flow Components](#data-flow-components)
    - [Component Details](#component-details)
      - [**Pipeline Runner**](#pipeline-runner)
      - [**Plugin Manager**](#plugin-manager)
      - [**Configuration Validator**](#configuration-validator)
  - [💻 4. Code Architecture (C4 Level 4)](#-4-code-architecture-c4-level-4)
    - [Package Structure](#package-structure)
    - [Key Classes and Relationships](#key-classes-and-relationships)
      - [**Main Application Classes**](#main-application-classes)
      - [**Domain Model Classes**](#domain-model-classes)
      - [**Infrastructure Classes**](#infrastructure-classes)
  - [🔄 5. Data Flow Architecture](#-5-data-flow-architecture)
    - [ETL Pipeline Data Flow](#etl-pipeline-data-flow)
    - [Configuration Data Flow](#configuration-data-flow)
  - [🛡️ 6. Security Architecture](#-6-security-architecture)
    - [Security Boundaries](#security-boundaries)
    - [Authentication & Authorization](#authentication--authorization)
  - [📊 7. Performance & Scalability](#-7-performance--scalability)
    - [Performance Characteristics](#performance-characteristics)
    - [Scalability Patterns](#scalability-patterns)
  - [📋 8. Architecture Decision Records (ADRs)](#-8-architecture-decision-records-adrs)
    - [ADR Template](#adr-template)
- [ADR [Number]: [Title]](#adr-number-title)
  - [Status](#status)
  - [Context](#context)
  - [Decision](#decision)
  - [Consequences](#consequences)
    - [Positive](#positive)
    - [Negative](#negative)
    - [Risks](#risks)
  - [Alternatives Considered](#alternatives-considered)
  - [Implementation Notes](#implementation-notes)
  - [References](#references)
    - [Current ADRs](#current-adrs)
      - [**ADR 001: Native Meltano Orchestration**](#adr-001-native-meltano-orchestration)
      - [**ADR 002: Dual Pipeline Architecture**](#adr-002-dual-pipeline-architecture)
      - [**ADR 003: Railway Pattern for Error Handling**](#adr-003-railway-pattern-for-error-handling)
  - [🔧 9. Deployment Architecture](#-9-deployment-architecture)
    - [Production Deployment](#production-deployment)
    - [Infrastructure Requirements](#infrastructure-requirements)
  - [🎯 Summary](#-summary)
    - [Architecture Highlights](#architecture-highlights)
    - [Key Architectural Decisions](#key-architectural-decisions)
    - [Quality Attributes](#quality-attributes)


**Project**: gruponos-meltano-native | **Version**: 0.9.0 | **Framework**: C4 Model + PlantUML
**Last Updated**: 2025-10-10 | **Status**: Production-Ready ETL Pipeline

---

## 📋 C4 Model Overview

This document provides a comprehensive architectural view of the gruponos-meltano-native system using the C4 model approach:

- **Context (Level 1)**: System in its environment
- **Containers (Level 2)**: High-level technology choices
- **Components (Level 3)**: Major building blocks
- **Code (Level 4)**: Implementation details

---

## 🌐 1. System Context (C4 Level 1)

### System Purpose
**gruponos-meltano-native** is an enterprise-grade ETL pipeline that orchestrates data integration between Oracle Warehouse Management System (WMS) and downstream analytics databases using Meltano orchestration platform.

### Context Diagram

```plantuml
@startuml C4_Context
!include <C4/C4_Context>

LAYOUT_WITH_LEGEND()

Person(user, "Data Analyst", "Business analyst requiring WMS data for reporting and analytics")

System(gruponos_meltano_native, "GrupoNOS Meltano Native", "ETL pipeline orchestrating Oracle WMS data integration")

System_Ext(oracle_wms, "Oracle WMS", "Warehouse Management System providing operational data")
System_Ext(oracle_db, "Oracle Analytics DB", "Target database for analytics and reporting")
System_Ext(meltano_hub, "Meltano Hub", "Plugin ecosystem for data integration")
System_Ext(flext_ecosystem, "FLEXT Ecosystem", "Shared libraries and frameworks")

Rel(user, gruponos_meltano_native, "Uses", "REST API, CLI")
Rel(gruponos_meltano_native, oracle_wms, "Extracts data from", "REST API")
Rel(gruponos_meltano_native, oracle_db, "Loads data into", "SQL")
Rel(gruponos_meltano_native, meltano_hub, "Uses plugins from", "HTTP")
Rel(gruponos_meltano_native, flext_ecosystem, "Depends on", "Local libraries")

@enduml
```

### Key Relationships

| Component | Relationship | Purpose | Technology |
|-----------|-------------|---------|------------|
| **Data Analyst** | Uses system | Access WMS data for analytics | REST API, CLI |
| **Oracle WMS** | Data source | Provides warehouse operational data | REST API |
| **Oracle Analytics DB** | Data target | Stores transformed analytics data | SQL |
| **Meltano Hub** | Plugin ecosystem | Provides extraction/loading plugins | HTTP |
| **FLEXT Ecosystem** | Shared libraries | Provides common patterns and utilities | Local dependencies |

---

## 🏗️ 2. Container Architecture (C4 Level 2)

### Container Diagram

```plantuml
@startuml C4_Container
!include <C4/C4_Container>

LAYOUT_WITH_LEGEND()

System_Boundary(gruponos_meltano_native, "GrupoNOS Meltano Native") {
    Container(cli_app, "CLI Application", "Python 3.13, Click", "Command-line interface for pipeline management")
    Container(api_service, "API Service", "Python 3.13, FastAPI", "REST API for pipeline operations")
    Container(orchestrator, "Pipeline Orchestrator", "Python 3.13, Meltano", "ETL pipeline execution engine")
    Container(config_manager, "Configuration Manager", "Python 3.13, Pydantic",
     "Environment and pipeline configuration")
    Container(monitoring, "Monitoring Service", "Python 3.13, FLEXT", "Observability and alerting")
}

System_Boundary(flext_ecosystem, "FLEXT Ecosystem") {
    Container(flext_core, "FLEXT Core", "Python 3.13", "Foundation patterns and utilities")
    Container(flext_db_oracle, "FLEXT Oracle DB", "Python 3.13, cx_Oracle", "Oracle database connectivity")
    Container(flext_tap_wms, "FLEXT WMS Tap", "Python 3.13, Singer", "Oracle WMS data extraction")
    Container(flext_target_oracle, "FLEXT Oracle Target", "Python 3.13, Singer", "Oracle database loading")
}

System_Ext(meltano_runtime, "Meltano Runtime", "Python, Docker", "ELT orchestration platform")
System_Ext(oracle_wms, "Oracle WMS", "Oracle Database, REST API", "Warehouse management data source")
System_Ext(oracle_analytics, "Oracle Analytics DB", "Oracle Database", "Analytics data warehouse")

Rel(cli_app, orchestrator, "Triggers", "CLI commands")
Rel(api_service, orchestrator, "Controls", "REST API")
Rel(orchestrator, meltano_runtime, "Uses", "Process execution")
Rel(orchestrator, config_manager, "Reads", "Configuration")
Rel(monitoring, orchestrator, "Monitors", "Metrics collection")

Rel(orchestrator, flext_tap_wms, "Extracts via", "Singer protocol")
Rel(orchestrator, flext_target_oracle, "Loads via", "Singer protocol")
Rel(flext_tap_wms, oracle_wms, "Reads from", "REST API")
Rel(flext_target_oracle, oracle_analytics, "Writes to", "SQL")

Rel(flext_tap_wms, flext_core, "Uses", "Railway patterns")
Rel(flext_target_oracle, flext_db_oracle, "Uses", "Database connectivity")
Rel(orchestrator, flext_core, "Uses", "Result patterns, DI")

@enduml
```

### Container Descriptions

#### **CLI Application**
- **Technology**: Python 3.13, Click framework
- **Purpose**: Command-line interface for pipeline operations
- **Responsibilities**:
  - Pipeline execution triggers
  - Configuration management
  - Status monitoring
  - Interactive operations

#### **API Service**
- **Technology**: Python 3.13, FastAPI
- **Purpose**: REST API for programmatic access
- **Responsibilities**:
  - Pipeline orchestration via HTTP
  - Status monitoring endpoints
  - Configuration management
  - Integration with external systems

#### **Pipeline Orchestrator**
- **Technology**: Python 3.13, Meltano 3.8.0
- **Purpose**: Core ETL orchestration engine
- **Responsibilities**:
  - Meltano pipeline execution
  - Plugin coordination
  - Error handling and recovery
  - Progress monitoring

#### **Configuration Manager**
- **Technology**: Python 3.13, Pydantic v2
- **Purpose**: Centralized configuration management
- **Responsibilities**:
  - Environment variable handling
  - Pipeline configuration validation
  - Runtime configuration updates
  - Secret management

#### **Monitoring Service**
- **Technology**: Python 3.13, FLEXT Observability
- **Purpose**: System observability and alerting
- **Responsibilities**:
  - Metrics collection
  - Performance monitoring
  - Error alerting
  - Health checks

---

## 🔧 3. Component Architecture (C4 Level 3)

### ETL Pipeline Components

```plantuml
@startuml C4_Component_Pipeline
!include <C4/C4_Component>

LAYOUT_WITH_LEGEND()

Container_Boundary(orchestrator, "Pipeline Orchestrator") {
    Component(pipeline_runner, "Pipeline Runner", "Python, Meltano", "Executes ELT pipelines")
    Component(job_scheduler, "Job Scheduler", "Python, APScheduler", "Manages pipeline schedules")
    Component(plugin_manager, "Plugin Manager", "Python, Meltano", "Coordinates Singer plugins")
    Component(state_manager, "State Manager", "Python, JSON", "Tracks pipeline execution state")
}

Container_Boundary(config_manager, "Configuration Manager") {
    Component(env_loader, "Environment Loader", "Python, python-dotenv", "Loads environment variables")
    Component(config_validator, "Config Validator", "Python, Pydantic", "Validates configuration schemas")
    Component(secret_manager, "Secret Manager", "Python, keyring", "Manages sensitive configuration")
}

Container_Boundary(monitoring, "Monitoring Service") {
    Component(metrics_collector, "Metrics Collector", "Python, FLEXT", "Collects performance metrics")
    Component(alert_manager, "Alert Manager", "Python, FLEXT", "Manages alerts and notifications")
    Component(health_checker, "Health Checker", "Python, requests", "Performs system health checks")
}

Rel(pipeline_runner, job_scheduler, "Uses", "Schedule execution")
Rel(pipeline_runner, plugin_manager, "Coordinates", "Plugin lifecycle")
Rel(pipeline_runner, state_manager, "Persists", "Execution state")

Rel(env_loader, config_validator, "Validates", "Environment config")
Rel(config_validator, secret_manager, "Secures", "Sensitive data")

Rel(metrics_collector, alert_manager, "Triggers", "Alert conditions")
Rel(health_checker, metrics_collector, "Reports", "Health metrics")

@enduml
```

### Data Flow Components

```plantuml
@startuml C4_Component_DataFlow
!include <C4/C4_Component>

LAYOUT_WITH_LEGEND()

Container_Boundary(data_pipeline, "Data Pipeline") {
    Component(wms_extractor, "WMS Extractor", "Singer Tap", "Extracts Oracle WMS data")
    Component(data_transformer, "Data Transformer", "Python, Pandas", "Transforms and cleans data")
    Component(oracle_loader, "Oracle Loader", "Singer Target", "Loads data to Oracle DB")
    Component(validation_engine, "Validation Engine", "Python, Pydantic", "Validates data quality")
}

Container_Boundary(quality_gate, "Quality Assurance") {
    Component(schema_validator, "Schema Validator", "Python, jsonschema", "Validates data schemas")
    Component(completeness_checker, "Completeness Checker", "Python", "Checks data completeness")
    Component(consistency_checker, "Consistency Checker", "Python", "Validates data consistency")
}

Rel(wms_extractor, data_transformer, "Streams", "Raw WMS data")
Rel(data_transformer, validation_engine, "Validates", "Transformed data")
Rel(validation_engine, oracle_loader, "Loads", "Validated data")

Rel(schema_validator, completeness_checker, "Validates", "Data structure")
Rel(completeness_checker, consistency_checker, "Checks", "Data integrity")

@enduml
```

### Component Details

#### **Pipeline Runner**
- **Responsibilities**:
  - Execute Meltano ELT pipelines
  - Handle pipeline failures and retries
  - Coordinate between extractors and loaders
  - Manage pipeline execution state
- **Key Classes**: `GruponosMeltanoOrchestrator`, `PipelineRunner`
- **Dependencies**: Meltano runtime, FLEXT core

#### **Plugin Manager**
- **Responsibilities**:
  - Install and configure Singer plugins
  - Manage plugin lifecycle
  - Handle plugin communication
  - Coordinate data flow between plugins
- **Key Classes**: `PluginManager`, `SingerCoordinator`
- **Dependencies**: Meltano plugin system, Singer protocol

#### **Configuration Validator**
- **Responsibilities**:
  - Validate pipeline configuration schemas
  - Check environment variable completeness
  - Verify plugin configuration compatibility
  - Ensure security requirements are met
- **Key Classes**: `GruponosMeltanoConfig`, `ConfigValidator`
- **Dependencies**: Pydantic v2, custom validation rules

---

## 💻 4. Code Architecture (C4 Level 4)

### Package Structure

```plantuml
@startuml C4_Code_Packages
!include <C4/C4_Code>

LAYOUT_WITH_LEGEND()

Package "gruponos_meltano_native" as pkg_main {
    Package "cli" as cli_pkg {
        Class "GruponosMeltanoNativeCli" as cli_class
        Class "CommandParser" as cmd_parser
        Class "OutputFormatter" as formatter
    }

    Package "orchestrator" as orch_pkg {
        Class "GruponosMeltanoOrchestrator" as orchestrator_class
        Class "PipelineExecutor" as executor
        Class "StateManager" as state_mgr
    }

    Package "config" as config_pkg {
        Class "GruponosMeltanoNativeConfig" as config_class
        Class "EnvironmentLoader" as env_loader
        Class "ConfigValidator" as validator
    }

    Package "models" as models_pkg {
        Class "GruponosMeltanoModels" as models_class
        Class "WmsAllocation" as alloc_model
        Class "OrderHeader" as order_hdr
        Class "OrderDetail" as order_dtl
    }

    Package "infrastructure" as infra_pkg {
        Package "di_container" as di_pkg {
            Class "GruponosMeltanoDiContainer" as di_class
        }
        Package "oracle" as oracle_pkg {
            Class "OracleConnectionManager" as conn_mgr
        }
    }

    Package "validators" as validators_pkg {
        Class "DataValidator" as data_validator
        Class "SchemaValidator" as schema_validator
    }

    Package "monitoring" as monitoring_pkg {
        Class "AlertManager" as alert_mgr
        Class "MetricsCollector" as metrics_coll
    }
}

Package "flext_core" as flext_core {
    Class "FlextResult" as result_class
    Class "FlextContainer" as container_class
    Class "FlextModels" as models_base
}

Package "meltano" as meltano {
    Class "Pipeline" as pipeline_class
    Class "Plugin" as plugin_class
}

' Relationships
cli_class --> orchestrator_class : triggers
orchestrator_class --> config_class : reads
orchestrator_class --> models_class : uses
orchestrator_class --> di_class : depends

config_class --> result_class : extends
models_class --> models_base : extends
di_class --> container_class : uses

orchestrator_class --> pipeline_class : uses
orchestrator_class --> plugin_class : coordinates

@enduml
```

### Key Classes and Relationships

#### **Main Application Classes**

| Class | Purpose | Key Methods | Dependencies |
|-------|---------|-------------|--------------|
| `GruponosMeltanoNativeCli` | CLI interface | `main()`, `run_pipeline()` | Click, orchestrator |
| `GruponosMeltanoOrchestrator` | Pipeline execution | `execute_pipeline()`, `validate_config()` | Meltano, FLEXT core |
| `GruponosMeltanoNativeConfig` | Configuration | `load_env()`, `validate()` | Pydantic, python-dotenv |

#### **Domain Model Classes**

| Class | Purpose | Key Attributes | Validation |
|-------|---------|----------------|------------|
| `WmsAllocation` | Warehouse allocation data | `allocation_id`, `item_code`, `quantity` | Pydantic v2 |
| `OrderHeader` | Order header information | `order_id`, `customer_id`, `order_date` | Business rules |
| `OrderDetail` | Order line items | `line_id`, `item_code`, `quantity` | Referential integrity |

#### **Infrastructure Classes**

| Class | Purpose | Key Methods | Technologies |
|-------|---------|-------------|--------------|
| `GruponosMeltanoDiContainer` | Dependency injection | `register()`, `get()` | FLEXT container |
| `OracleConnectionManager` | Database connectivity | `connect()`, `execute()` | cx_Oracle, FLEXT DB |
| `AlertManager` | Alert handling | `send_alert()`, `check_thresholds()` | FLEXT observability |

---

## 🔄 5. Data Flow Architecture

### ETL Pipeline Data Flow

```plantuml
@startuml Data_Flow_ETL
!include <C4/C4_Dynamic>

title ETL Pipeline Data Flow

participant "Oracle WMS" as wms
participant "WMS Extractor" as extractor
participant "Data Transformer" as transformer
participant "Validation Engine" as validator
participant "Oracle Loader" as loader
participant "Oracle Analytics DB" as target

== Full Sync Pipeline ==
wms -> extractor: REST API Call\n(entities: allocation, order_hdr, order_dtl)
extractor -> transformer: Raw JSON Stream\n(page_size: 500)
transformer -> validator: Transformed Records\n(data cleaning, type conversion)
validator -> loader: Validated Records\n(schema compliance)
loader -> target: SQL INSERT/UPDATE\n(batch_size: 5000, append_only)

== Incremental Sync Pipeline ==
wms -> extractor: REST API Call\n(mod_ts > last_sync)
extractor -> transformer: Changed Records Only
transformer -> validator: Incremental Updates
validator -> loader: Validated Changes
loader -> target: SQL UPSERT\n(replication_key: mod_ts)

== Error Handling ==
validator -> validator: Validation Failure
validator -> extractor: Retry Request\n(max_retries: 3)
loader -> loader: Batch Failure
loader -> target: Rollback Transaction
@enduml
```

### Configuration Data Flow

```plantuml
@startuml Data_Flow_Config
!include <C4/C4_Dynamic>

title Configuration Data Flow

participant "Environment" as env
participant ".env file" as dotenv
participant "CLI Args" as cli
participant "Config Loader" as loader
participant "Config Validator" as validator
participant "Application" as app

== Configuration Loading ==
env -> dotenv: Environment Variables
cli -> loader: Command Line Arguments
loader -> dotenv: Read .env file
dotenv -> loader: Parse Variables
loader -> validator: Raw Configuration
validator -> app: Validated Configuration

== Runtime Updates ==
app -> validator: Configuration Changes
validator -> loader: Update Cache
loader -> dotenv: Persist Changes (optional)

== Validation Flow ==
validator -> validator: Schema Validation
validator -> validator: Business Rules Check
validator -> validator: Security Validation
validator -> app: Validation Results
@enduml
```

---

## 🛡️ 6. Security Architecture

### Security Boundaries

```plantuml
@startuml Security_Architecture
!include <C4/C4_Container>

title Security Architecture & Trust Zones

System_Boundary(trust_zones, "Security Trust Zones") {

    System_Boundary(public_zone, "Public Zone") {
        Container(cli_client, "CLI Client", "Terminal", "User command interface")
        Container(api_client, "API Client", "HTTP Client", "External API calls")
    }

    System_Boundary(dmz, "DMZ") {
        Container(api_gateway, "API Gateway", "FastAPI", "Request routing and authentication")
        Container(reverse_proxy, "Reverse Proxy", "nginx", "SSL termination and load balancing")
    }

    System_Boundary(application_zone, "Application Zone") {
        Container(orchestrator, "Pipeline Orchestrator", "Python", "ETL pipeline execution")
        Container(config_manager, "Config Manager", "Python", "Configuration management")
        Container(monitoring, "Monitoring", "Python", "System monitoring")
    }

    System_Boundary(data_zone, "Data Zone") {
        Container(oracle_db, "Oracle Analytics DB", "Oracle DB", "Analytics data storage")
        Container(secret_store, "Secret Store", "HashiCorp Vault", "Credential management")
    }
}

System_Ext(oracle_wms, "Oracle WMS", "External System")
System_Ext(identity_provider, "Identity Provider", "LDAP/OAuth")

Rel(cli_client, reverse_proxy, "HTTPS", "CLI commands (authenticated)")
Rel(api_client, reverse_proxy, "HTTPS", "API requests (authenticated)")
Rel(reverse_proxy, api_gateway, "HTTP", "Routed requests")
Rel(api_gateway, orchestrator, "Internal", "Pipeline operations")
Rel(orchestrator, oracle_db, "SQL/TLS", "Data loading")
Rel(orchestrator, oracle_wms, "HTTPS/mTLS", "Data extraction")

Rel(api_gateway, identity_provider, "LDAP/OAuth", "User authentication")
Rel(config_manager, secret_store, "TLS", "Secret retrieval")

' Security controls
note right of reverse_proxy : SSL/TLS 1.3\nRate Limiting\nWAF
note right of api_gateway : JWT Validation\nRBAC\nAPI Key Auth
note right of oracle_db : Database Encryption\nRow-level Security\nAudit Logging
@enduml
```

### Authentication & Authorization

```plantuml
@startuml Auth_Flow
!include <C4/C4_Dynamic>

title Authentication & Authorization Flow

participant "User" as user
participant "CLI/API" as client
participant "API Gateway" as gateway
participant "Identity Provider" as idp
participant "Application" as app
participant "Oracle DB" as db

== Authentication Flow ==
user -> client: Login Request
client -> gateway: Authenticate Request
gateway -> idp: Validate Credentials
idp -> gateway: JWT Token
gateway -> client: Authentication Success

== Authorization Flow ==
client -> gateway: API Request + JWT
gateway -> gateway: Validate JWT Signature
gateway -> gateway: Check RBAC Permissions
gateway -> app: Authorized Request
app -> db: Execute Query (with user context)

== Token Refresh ==
gateway -> gateway: Check Token Expiry
gateway -> idp: Refresh Token Request
idp -> gateway: New JWT Token
gateway -> client: Refreshed Token
@enduml
```

---

## 📊 7. Performance & Scalability

### Performance Characteristics

```plantuml
@startuml Performance_Profile
title ETL Pipeline Performance Characteristics

scale 0.8

' Performance metrics over time
clock "Time" as t

rectangle "Data Volume" as volume [
  Full Sync: 100K-1M records
  Incremental: 1K-10K records/hour
  Peak Load: 50K records/minute
]

rectangle "Response Times" as response [
  Full Sync: 30-120 minutes
  Incremental: 5-15 minutes
  API Response: <2 seconds
]

rectangle "Resource Usage" as resources [
  CPU: 20-80% (4 cores)
  Memory: 512MB-2GB
  Network: 10-100 Mbps
  Storage: 1-10 GB temp files
]

' Scaling relationships
volume --> response : Direct correlation
response --> resources : Resource consumption
resources --> volume : Capacity limits

note right : Performance degrades with\nlarge datasets. Consider\npartitioning for >1M records.
@enduml
```

### Scalability Patterns

```plantuml
@startuml Scalability_Patterns
!include <C4/C4_Deployment>

title Deployment Scalability Architecture

Deployment_Node(prod_cluster, "Production Cluster", "Kubernetes/AKS") {
    Deployment_Node(pipeline_workers, "Pipeline Workers", "Docker") {
        Container(orchestrator, "Pipeline Orchestrator", "Python/Meltano")
    }

    Deployment_Node(api_services, "API Services", "Docker") {
        Container(api_server, "API Server", "FastAPI")
    }

    Deployment_Node(monitoring, "Monitoring Stack", "Prometheus/Grafana") {
        Container(metrics_db, "Metrics Database", "InfluxDB")
        Container(alert_manager, "Alert Manager", "AlertManager")
    }

    Deployment_Node(databases, "Database Layer") {
        Container(oracle_primary, "Oracle Primary", "Oracle DB")
        Container(oracle_read_replica, "Oracle Read Replica", "Oracle DB")
    }
}

Deployment_Node(load_balancer, "Load Balancer", "Azure Front Door") {
    Container(traffic_manager, "Traffic Manager", "Azure Front Door")
}

' Scaling relationships
pipeline_workers --> databases : Data processing
api_services --> pipeline_workers : Orchestration
monitoring --> pipeline_workers : Metrics collection
monitoring --> api_services : Health monitoring

' External connections
load_balancer --> api_services : API traffic distribution

note right of pipeline_workers
  Horizontal scaling:
  - Auto-scale 1-10 pods
  - Queue-based processing
  - Stateless design
end note

note right of databases
  Read/write splitting:
  - Primary for writes
  - Replicas for reads
  - Connection pooling
end note
@enduml
```

---

## 📋 8. Architecture Decision Records (ADRs)

### ADR Template

```markdown
# ADR [Number]: [Title]

## Status
[Proposed | Accepted | Rejected | Deprecated | Superseded]

## Context
[Describe the context and problem statement]

## Decision
[Describe the decision made and the solution]

## Consequences
### Positive
- [List positive consequences]

### Negative
- [List negative consequences]

### Risks
- [List risks and mitigation strategies]

## Alternatives Considered
- [List alternatives and why they were not chosen]

## Implementation Notes
[Technical details, code references, testing considerations]

## References
- [Links to related documents, issues, PRs]
```

### Current ADRs

#### **ADR 001: Native Meltano Orchestration**
- **Status**: Accepted
- **Decision**: Use Meltano 3.8.0 native orchestration instead of flext-meltano wrapper
- **Rationale**: Direct control, better integration, reduced abstraction overhead
- **Consequences**: Tighter coupling to Meltano, direct plugin management

#### **ADR 002: Dual Pipeline Architecture**
- **Status**: Accepted
- **Decision**: Implement separate full sync and incremental sync pipelines
- **Rationale**: Performance optimization, different load patterns, data freshness requirements
- **Consequences**: Increased complexity, separate scheduling, configuration duplication

#### **ADR 003: Railway Pattern for Error Handling**
- **Status**: Accepted
- **Decision**: Use FlextResult[T] railway pattern throughout the application
- **Rationale**: Composable error handling, functional programming approach, type safety
- **Consequences**: Learning curve, different from traditional exception handling

---

## 🔧 9. Deployment Architecture

### Production Deployment

```plantuml
@startuml Deployment_Architecture
!include <C4/C4_Deployment>

title Production Deployment Architecture

Deployment_Node(azure_cloud, "Azure Cloud", "East US 2") {
    Deployment_Node(aks_cluster, "AKS Cluster", "Kubernetes 1.28") {

        Deployment_Node(pipeline_namespace, "Pipeline Namespace") {
            Container(orchestrator_deployment, "Orchestrator", "Docker", "Pipeline execution")
            Container(worker_deployment, "Workers", "Docker", "Parallel processing")
            Container(job_queue, "Job Queue", "Redis", "Task queuing")
        }

        Deployment_Node(api_namespace, "API Namespace") {
            Container(api_deployment, "API Server", "Docker", "REST API")
            Container(api_gateway, "API Gateway", "nginx", "Request routing")
        }

        Deployment_Node(monitoring_namespace, "Monitoring") {
            Container(prometheus, "Prometheus", "Docker", "Metrics collection")
            Container(grafana, "Grafana", "Docker", "Visualization")
            Container(alertmanager, "AlertManager", "Docker", "Alert routing")
        }

        Deployment_Node(data_namespace, "Data Layer") {
            Container(oracle_primary, "Oracle Primary", "VM", "Primary database")
            Container(oracle_replica, "Oracle Replica", "VM", "Read replica")
            Container(cache, "Redis Cache", "Docker", "Caching layer")
        }
    }

    Deployment_Node(storage, "Storage Accounts") {
        Container(blob_storage, "Blob Storage", "Azure Storage", "File storage")
        Container(table_storage, "Table Storage", "Azure Storage", "Metadata storage")
    }

    Deployment_Node(networking, "Networking") {
        Container(vnet, "Virtual Network", "Azure VNet", "Network isolation")
        Container(nsg, "Network Security", "Azure NSG", "Traffic filtering")
        Container(load_balancer, "Load Balancer", "Azure Front Door", "Traffic distribution")
    }
}

System_Ext(oracle_wms, "Oracle WMS", "External")
System_Ext(monitoring_systems, "Monitoring Systems", "External")

' Data flow
oracle_wms -> aks_cluster : Data extraction (HTTPS)
aks_cluster -> storage : File storage
aks_cluster -> monitoring_systems : Metrics export

' Internal communication
orchestrator_deployment -> worker_deployment : Job distribution
worker_deployment -> oracle_primary : Data loading
api_deployment -> orchestrator_deployment : Pipeline control

@enduml
```

### Infrastructure Requirements

| Component | Specification | Scaling | HA |
|-----------|---------------|---------|----|
| **Orchestrator** | 2 vCPU, 4GB RAM | 1-3 pods | Rolling updates |
| **Workers** | 1 vCPU, 2GB RAM | 1-10 pods | Horizontal scaling |
| **API Server** | 1 vCPU, 2GB RAM | 2-6 pods | Load balancing |
| **Oracle DB** | 4 vCPU, 16GB RAM | Primary + 1 replica | Failover clustering |
| **Redis Cache** | 1 vCPU, 2GB RAM | 1-3 pods | Redis clustering |
| **Monitoring** | 1 vCPU, 2GB RAM | 1-2 pods | External monitoring |

---

## 🎯 Summary

### Architecture Highlights

- **Native Meltano 3.8.0**: Direct orchestration without abstraction layers
- **Dual Pipeline Design**: Separate full and incremental sync strategies
- **Railway Pattern**: Functional error handling with FlextResult[T]
- **C4 Model Documentation**: Comprehensive architectural views
- **Enterprise Security**: Multi-zone architecture with proper boundaries
- **Scalable Deployment**: Kubernetes-native with horizontal scaling

### Key Architectural Decisions

1. **Native Meltano**: Direct control over orchestration vs abstracted wrappers
2. **Dual Pipelines**: Performance optimization through separate sync strategies
3. **Railway Pattern**: Functional error handling throughout the application
4. **FLEXT Integration**: Shared patterns and infrastructure across ecosystem
5. **Container-First**: Kubernetes-native deployment from design phase

### Quality Attributes

- **Reliability**: Railway pattern for robust error handling
- **Performance**: Optimized for both bulk and incremental data loads
- **Security**: Multi-zone architecture with proper authentication/authorization
- **Maintainability**: Clean architecture with clear separation of concerns
- **Scalability**: Horizontal scaling support with queue-based processing

---

**C4 Model Documentation** - Comprehensive architectural views using industry-standard C4 model approach for clear communication of system design and implementation details.