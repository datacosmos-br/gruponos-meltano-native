# Monitoring Module

**Enterprise Monitoring and Alerting for GrupoNOS Meltano Native**

This module provides comprehensive monitoring, alerting, and observability capabilities for ETL pipeline operations, built on FLEXT observability standards with enterprise-grade reliability and multi-channel delivery.

## Components

### `alert_manager.py` - Alert Management System

Enterprise alert management with multi-channel delivery, severity-based routing, and comprehensive monitoring integration.

#### Key Classes

##### `GruponosMeltanoAlertManager`

Primary alert management system with enterprise features:

- **Multi-Channel Delivery**: Email, Slack, webhooks, and custom integrations
- **Severity-Based Routing**: Automatic routing based on alert severity levels
- **Rate Limiting**: Intelligent rate limiting to prevent alert flooding
- **Retry Mechanisms**: Robust retry logic with exponential backoff
- **Template Support**: Customizable alert templates with rich formatting

##### `GruponosMeltanoAlert`

Rich alert entity with comprehensive context:

- **Structured Data**: Type-safe alert structure with validation
- **Context Enrichment**: Automatic context addition from ETL operations
- **Correlation IDs**: Distributed tracing support for complex workflows
- **Severity Classification**: Standard severity levels (INFO, WARNING, ERROR, CRITICAL)

##### `GruponosMeltanoAlertService`

Service layer for alert operations:

- **Business Logic**: Alert processing and routing logic
- **Integration**: ETL pipeline integration points
- **Configuration**: Dynamic configuration management
- **Monitoring**: Self-monitoring and health checks

## Alert Severity Levels

### `GruponosMeltanoAlertSeverity`

```python
class GruponosMeltanoAlertSeverity(str, Enum):
    INFO = "info"           # Informational messages
    WARNING = "warning"     # Potential issues requiring attention
    ERROR = "error"         # Operation failures requiring intervention
    CRITICAL = "critical"   # System failures requiring immediate action
```

### Alert Type Classifications

### `GruponosMeltanoAlertType`

```python
class GruponosMeltanoAlertType(str, Enum):
    PIPELINE_START = "pipeline_start"       # ETL pipeline initiation
    PIPELINE_SUCCESS = "pipeline_success"   # Successful completion
    PIPELINE_FAILURE = "pipeline_failure"   # Pipeline execution failure
    DATA_QUALITY = "data_quality"           # Data quality issues
    CONNECTION_ERROR = "connection_error"   # Database/API connection issues
    PERFORMANCE = "performance"             # Performance threshold violations
    SYSTEM_HEALTH = "system_health"         # System health monitoring
```

## Usage Examples

### Basic Alert Sending

```python
from gruponos_meltano_native.monitoring import (
    create_gruponos_meltano_alert_manager,
    GruponosMeltanoAlertSeverity,
    GruponosMeltanoAlertType
)

# Create alert manager
alert_manager = create_gruponos_meltano_alert_manager()

# Send pipeline completion alert
alert_manager.send_alert(
    title="ETL Pipeline Completed Successfully",
    message="Full sync pipeline completed processing 10,000 records",
    severity=GruponosMeltanoAlertSeverity.INFO,
    alert_type=GruponosMeltanoAlertType.PIPELINE_SUCCESS,
    context={
        "company_code": "GNOS",
        "facility_code": "DC01",
        "records_processed": 10000,
        "duration_seconds": 120
    }
)
```

### ETL Pipeline Integration

```python
class GruponosMeltanoOrchestrator:
    def __init__(self, alert_manager: GruponosMeltanoAlertManager):
        self.alert_manager = alert_manager

    def execute_full_sync(self, company_code: str, facility_code: str):
        # Send start notification
        self.alert_manager.send_alert(
            title="ETL Pipeline Started",
            message=f"Starting full sync for {company_code}/{facility_code}",
            severity=GruponosMeltanoAlertSeverity.INFO,
            alert_type=GruponosMeltanoAlertType.PIPELINE_START
        )

        try:
            # Execute ETL operations
            result = self._execute_pipeline(company_code, facility_code)

            # Send success notification
            self.alert_manager.send_alert(
                title="ETL Pipeline Completed",
                message=f"Pipeline completed successfully: {result.summary}",
                severity=GruponosMeltanoAlertSeverity.INFO,
                alert_type=GruponosMeltanoAlertType.PIPELINE_SUCCESS,
                context=result.to_dict()
            )

            return FlextResult[None].ok(result)

        except Exception as e:
            # Send failure notification
            self.alert_manager.send_alert(
                title="ETL Pipeline Failed",
                message=f"Pipeline execution failed: {str(e)}",
                severity=GruponosMeltanoAlertSeverity.ERROR,
                alert_type=GruponosMeltanoAlertType.PIPELINE_FAILURE,
                context={
                    "company_code": company_code,
                    "facility_code": facility_code,
                    "error": str(e),
                    "stack_trace": traceback.format_exc()
                }
            )

            return FlextResult[None].fail(f"Pipeline execution failed: {str(e)}")
```

### Custom Alert Configuration

```python
from gruponos_meltano_native.config import GruponosMeltanoAlertConfig

# Configure alert channels
alert_config = GruponosMeltanoAlertConfig(
    # Email configuration
    email_enabled=True,
    smtp_host="smtp.company.com",
    smtp_port=587,
    email_from="etl-alerts@company.com",
    email_recipients=["ops-team@company.com", "data-team@company.com"],

    # Slack configuration
    slack_enabled=True,
    slack_webhook_url="https://hooks.slack.com/services/...",
    slack_channel="#data-ops",

    # Webhook configuration
    webhook_enabled=True,
    webhook_url="https://monitoring.company.com/alerts",
    webhook_auth_token="bearer_token_here",

    # Alert filtering
    min_severity_level=GruponosMeltanoAlertSeverity.WARNING,
    rate_limit_window_minutes=5,
    max_alerts_per_window=10
)

# Create alert manager with custom configuration
alert_manager = create_gruponos_meltano_alert_manager(alert_config)
```

## Advanced Features

### Alert Templating

```python
# Custom alert templates
alert_templates = {
    GruponosMeltanoAlertType.PIPELINE_FAILURE: {
        "email_subject": "🚨 ETL Pipeline Failure - {company_code}/{facility_code}",
        "email_body": """
        ETL Pipeline Failure Alert

        Company: {company_code}
        Facility: {facility_code}
        Time: {timestamp}
        Error: {error_message}

        Please investigate immediately.
        """,
        "slack_message": "🚨 ETL Pipeline failed for {company_code}/{facility_code}: {error_message}"
    }
}

alert_manager.configure_templates(alert_templates)
```

### Performance Monitoring

```python
# Performance threshold monitoring
class PerformanceMonitor:
    def __init__(self, alert_manager: GruponosMeltanoAlertManager):
        self.alert_manager = alert_manager
        self.thresholds = {
            "pipeline_duration_minutes": 30,
            "records_per_second": 100,
            "error_rate_percent": 5
        }

    def check_performance_metrics(self, pipeline_result):
        # Check duration threshold
        if pipeline_result.duration_minutes > self.thresholds["pipeline_duration_minutes"]:
            self.alert_manager.send_alert(
                title="Performance Threshold Exceeded",
                message=f"Pipeline duration {pipeline_result.duration_minutes}m exceeds threshold",
                severity=GruponosMeltanoAlertSeverity.WARNING,
                alert_type=GruponosMeltanoAlertType.PERFORMANCE
            )

        # Check processing rate
        processing_rate = pipeline_result.records_processed / pipeline_result.duration_seconds
        if processing_rate < self.thresholds["records_per_second"]:
            self.alert_manager.send_alert(
                title="Low Processing Rate Detected",
                message=f"Processing rate {processing_rate:.2f} records/sec below threshold",
                severity=GruponosMeltanoAlertSeverity.WARNING,
                alert_type=GruponosMeltanoAlertType.PERFORMANCE
            )
```

### Health Check Integration

```python
# System health monitoring
class HealthCheckMonitor:
    def __init__(self, alert_manager: GruponosMeltanoAlertManager):
        self.alert_manager = alert_manager

    def check_system_health(self):
        # Check Oracle WMS connectivity
        wms_health = self.check_wms_connectivity()
        if not wms_health.is_healthy:
            self.alert_manager.send_alert(
                title="Oracle WMS Connectivity Issue",
                message=f"WMS health check failed: {wms_health.error}",
                severity=GruponosMeltanoAlertSeverity.ERROR,
                alert_type=GruponosMeltanoAlertType.CONNECTION_ERROR
            )

        # Check target database connectivity
        db_health = self.check_database_connectivity()
        if not db_health.is_healthy:
            self.alert_manager.send_alert(
                title="Target Database Connectivity Issue",
                message=f"Database health check failed: {db_health.error}",
                severity=GruponosMeltanoAlertSeverity.CRITICAL,
                alert_type=GruponosMeltanoAlertType.CONNECTION_ERROR
            )
```

## Configuration

### Environment Variables

```bash
# Alert configuration
GRUPONOS_ALERT_EMAIL_ENABLED=true
GRUPONOS_ALERT_SMTP_HOST=smtp.company.com
GRUPONOS_ALERT_SMTP_PORT=587
GRUPONOS_ALERT_EMAIL_FROM=etl-alerts@company.com
GRUPONOS_ALERT_EMAIL_RECIPIENTS=ops-team@company.com,data-team@company.com

# Slack configuration
GRUPONOS_ALERT_SLACK_ENABLED=true
GRUPONOS_ALERT_SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
GRUPONOS_ALERT_SLACK_CHANNEL=#data-ops

# Alert filtering
GRUPONOS_ALERT_MIN_SEVERITY=WARNING
GRUPONOS_ALERT_RATE_LIMIT_WINDOW=5
GRUPONOS_ALERT_MAX_PER_WINDOW=10
```

## Testing Support

### Mock Alert Manager

```python
# Mock for testing
class MockAlertManager:
    def __init__(self):
        self.sent_alerts = []

    def send_alert(self, **kwargs):
        self.sent_alerts.append(kwargs)
        return FlextResult[None].ok("Alert sent successfully")

    def get_alerts_by_type(self, alert_type):
        return [alert for alert in self.sent_alerts if alert.get("alert_type") == alert_type]
```

### Integration Testing

```python
# Test alert delivery
@pytest.mark.integration
def test_alert_delivery():
    alert_manager = create_gruponos_meltano_alert_manager()

    result = alert_manager.send_alert(
        title="Test Alert",
        message="This is a test alert",
        severity=GruponosMeltanoAlertSeverity.INFO
    )

    assert result.success
    # Verify alert was delivered to configured channels
```

## Development Guidelines

### Alert Design Principles

1. **Context-Rich**: Include comprehensive context for debugging
2. **Actionable**: Provide clear guidance on required actions
3. **Severity-Appropriate**: Use appropriate severity levels
4. **Rate-Limited**: Prevent alert flooding
5. **Monitored**: Monitor alert system health

### Integration Standards

1. **FLEXT Compliance**: Use FLEXT patterns throughout
2. **Error Handling**: FlextResult for all operations
3. **Configuration**: Environment-aware configuration
4. **Testing**: Comprehensive unit and integration tests
5. **Documentation**: Clear examples and usage patterns

---

**Purpose**: Enterprise monitoring and alerting  
**Integration**: FLEXT observability standards  
**Delivery**: Multi-channel with rate limiting  
**Monitoring**: Self-monitoring alert system health
