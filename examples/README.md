# Examples Directory

**Practical Usage Examples for GrupoNOS Meltano Native**

This directory contains comprehensive, working examples demonstrating how to use the GrupoNOS Meltano Native ETL pipeline framework effectively. All examples follow FLEXT standards and enterprise best practices.

## Available Examples

### `config_usage.py` - Configuration Management Examples
Comprehensive demonstration of configuration management patterns, environment-specific settings, and validation techniques.

#### Key Features Demonstrated
- **Environment-Aware Configuration**: Loading settings for different environments
- **Validation Patterns**: Configuration validation with detailed error reporting
- **Security Best Practices**: Secure credential handling and field exclusion
- **Hierarchical Configuration**: Nested configuration models with inheritance

#### Example Scenarios
```python
# Basic configuration loading
from gruponos_meltano_native.config import GruponosMeltanoSettings

# Load configuration from environment
settings = GruponosMeltanoSettings()
print(f"Environment: {settings.environment}")
print(f"Application: {settings.app_name} v{settings.version}")

# Oracle WMS configuration
wms_config = settings.oracle_wms
print(f"WMS URL: {wms_config.base_url}")
print(f"Company: {wms_config.company_code}")

# Configuration validation
validation_result = settings.validate_all_connections()
if validation_result.is_success:
    print("All configurations validated successfully")
else:
    print(f"Configuration validation failed: {validation_result.error}")
```

## Usage Patterns

### Basic ETL Pipeline Execution
```python
"""
Basic ETL Pipeline Execution Example

Demonstrates how to execute a complete ETL pipeline with proper
error handling and monitoring integration.
"""

import asyncio
from gruponos_meltano_native import create_gruponos_meltano_platform

async def main():
    # Create ETL platform instance
    platform = create_gruponos_meltano_platform()
    
    # Execute full synchronization
    print("Starting full synchronization...")
    result = await platform.execute_full_sync("GNOS", "DC01")
    
    if result.is_success:
        print(f"ETL completed successfully!")
        print(f"Records processed: {result.data.records_processed}")
        print(f"Duration: {result.data.duration_seconds} seconds")
        print(f"Throughput: {result.data.records_per_second:.2f} records/sec")
    else:
        print(f"ETL failed: {result.error}")
        # Handle error appropriately
        await handle_etl_failure(result)

async def handle_etl_failure(result):
    """Handle ETL failure with appropriate actions."""
    # Log error details
    logger.error(f"ETL pipeline failed: {result.error}")
    
    # Send alert if configured
    alert_manager = create_gruponos_meltano_alert_manager()
    await alert_manager.send_alert(
        title="ETL Pipeline Failure",
        message=f"Pipeline execution failed: {result.error}",
        severity=GruponosMeltanoAlertSeverity.ERROR
    )

if __name__ == "__main__":
    asyncio.run(main())
```

### Advanced Configuration Examples
```python
"""
Advanced Configuration Management Example

Demonstrates advanced configuration patterns including environment-specific
settings, custom validation rules, and secure credential management.
"""

from gruponos_meltano_native.config import (
    GruponosMeltanoSettings,
    GruponosMeltanoOracleConnectionConfig,
    GruponosMeltanoWMSSourceConfig
)

def demonstrate_environment_specific_config():
    """Demonstrate environment-specific configuration loading."""
    
    # Development environment
    dev_settings = GruponosMeltanoSettings(environment="development")
    print(f"Dev WMS URL: {dev_settings.oracle_wms.base_url}")
    print(f"Dev Debug Mode: {dev_settings.debug}")
    
    # Production environment
    prod_settings = GruponosMeltanoSettings(environment="production")
    print(f"Prod WMS URL: {prod_settings.oracle_wms.base_url}")
    print(f"Prod Debug Mode: {prod_settings.debug}")

def demonstrate_custom_configuration():
    """Demonstrate custom configuration creation and validation."""
    
    # Create custom Oracle WMS configuration
    custom_wms_config = GruponosMeltanoWMSSourceConfig(
        base_url="https://custom-wms.company.com/api/v1",
        username="custom_user",
        password="secure_password",
        company_code="CUSTOM",
        facility_code="DC99",
        timeout_seconds=300,
        batch_size=2000,
        max_retries=5
    )
    
    # Validate configuration
    validation_result = custom_wms_config.validate_connection_settings()
    if validation_result.is_success:
        print("Custom WMS configuration is valid")
    else:
        print(f"Configuration validation failed: {validation_result.error}")
    
    # Create complete settings with custom config
    settings = GruponosMeltanoSettings(oracle_wms=custom_wms_config)
    return settings

def demonstrate_configuration_security():
    """Demonstrate secure configuration handling."""
    
    settings = GruponosMeltanoSettings()
    
    # Demonstrate credential exclusion in string representation
    print("Settings representation (passwords excluded):")
    print(settings)
    
    # Access credentials securely
    wms_password = settings.oracle_wms.password.get_secret_value()
    target_password = settings.oracle_target.password.get_secret_value()
    
    # Use credentials for connections (not printed)
    print("Credentials loaded securely for connection use")
```

### Data Validation Examples
```python
"""
Data Validation Examples

Demonstrates comprehensive data validation patterns including
schema validation, business rules, and data quality checks.
"""

from gruponos_meltano_native.validators import (
    create_gruponos_meltano_validator_for_environment,
    GruponosMeltanoDataValidator
)

async def demonstrate_basic_validation():
    """Demonstrate basic data validation workflow."""
    
    # Create validator for current environment
    validator = create_gruponos_meltano_validator_for_environment()
    
    # Sample allocation data
    allocation_data = [
        {
            "allocation_id": "A001",
            "item_code": "ITEM001",
            "quantity": 100,
            "facility_code": "DC01",
            "location": "A1-B2-C3"
        },
        {
            "allocation_id": "A002",
            "item_code": "ITEM002",
            "quantity": 250,
            "facility_code": "DC01",
            "location": "B1-C2-D3"
        }
    ]
    
    # Execute validation chain
    result = await validator.validate_allocation_data(allocation_data)
    
    if result.is_success:
        print(f"Validation passed: {len(result.data)} records validated")
        for record in result.data:
            print(f"  - {record['allocation_id']}: {record['quantity']} units")
    else:
        print(f"Validation failed: {result.error}")
        
        # Handle validation errors
        if hasattr(result, 'validation_errors'):
            for error in result.validation_errors:
                print(f"  - Error: {error.field} - {error.message}")

async def demonstrate_custom_validation_rules():
    """Demonstrate custom validation rule implementation."""
    
    # Custom validation configuration
    validation_config = {
        "business_rules": [
            {
                "name": "minimum_quantity",
                "description": "Allocation quantity must be at least 10",
                "condition": lambda record: record.get("quantity", 0) >= 10,
                "error_message": "Allocation quantity must be at least 10 units"
            },
            {
                "name": "valid_location_format",
                "description": "Location must follow pattern A#-B#-C#",
                "condition": lambda record: validate_location_format(record.get("location", "")),
                "error_message": "Location must follow format A#-B#-C# (e.g., A1-B2-C3)"
            }
        ]
    }
    
    # Create validator with custom rules
    validator = GruponosMeltanoDataValidator(validation_config)
    
    # Test data with validation violations
    test_data = [
        {
            "allocation_id": "A001",
            "item_code": "ITEM001",
            "quantity": 5,  # Violates minimum quantity rule
            "facility_code": "DC01",
            "location": "INVALID_LOCATION"  # Violates location format rule
        }
    ]
    
    result = await validator.validate_business_rules(test_data)
    
    if result.is_failure:
        print("Expected validation failures:")
        for error in result.validation_errors:
            print(f"  - {error.rule_name}: {error.message}")

def validate_location_format(location: str) -> bool:
    """Custom location format validation."""
    import re
    pattern = r'^[A-Z]\d+-[A-Z]\d+-[A-Z]\d+$'
    return bool(re.match(pattern, location))
```

### Oracle Integration Examples
```python
"""
Oracle Database Integration Examples

Demonstrates Oracle database connectivity, connection management,
and optimized ETL operations.
"""

from gruponos_meltano_native.oracle import (
    create_gruponos_meltano_oracle_connection_manager,
    GruponosMeltanoOracleConnectionConfig
)

async def demonstrate_oracle_connection():
    """Demonstrate Oracle database connection management."""
    
    # Create connection configuration
    config = GruponosMeltanoOracleConnectionConfig(
        host="oracle-dev.company.com",
        port=1521,
        service_name="DEVDB",
        username="etl_user",
        password="secure_password",
        schema="WMS_DATA"
    )
    
    # Create connection manager
    manager = create_gruponos_meltano_oracle_connection_manager(config)
    
    # Get database connection
    connection_result = await manager.get_connection()
    
    if connection_result.is_success:
        conn = connection_result.data
        print("Connected to Oracle database successfully")
        
        # Execute sample query
        result = await conn.execute("SELECT COUNT(*) FROM allocations")
        count = await result.fetchone()
        print(f"Total allocations in database: {count[0]}")
        
        # Return connection to pool
        await manager.return_connection(conn)
    else:
        print(f"Failed to connect to Oracle: {connection_result.error}")

async def demonstrate_bulk_operations():
    """Demonstrate bulk database operations for ETL."""
    
    manager = create_gruponos_meltano_oracle_connection_manager()
    
    # Sample data for bulk insert
    allocation_batch = [
        ("A001", "ITEM001", 100, "DC01", "A1-B2-C3"),
        ("A002", "ITEM002", 250, "DC01", "B1-C2-D3"),
        ("A003", "ITEM003", 150, "DC01", "C1-D2-E3")
    ]
    
    # Execute bulk insert with transaction management
    async with manager.get_connection() as conn:
        async with conn.begin():  # Transaction context
            # Bulk insert statement
            insert_sql = """
                INSERT INTO wms_allocations 
                (allocation_id, item_code, quantity, facility_code, location)
                VALUES (?, ?, ?, ?, ?)
            """
            
            # Execute bulk insert
            await conn.executemany(insert_sql, allocation_batch)
            print(f"Inserted {len(allocation_batch)} allocations successfully")
```

### Monitoring and Alerting Examples
```python
"""
Monitoring and Alerting Examples

Demonstrates alert management, monitoring integration,
and observability patterns.
"""

from gruponos_meltano_native.monitoring import (
    create_gruponos_meltano_alert_manager,
    GruponosMeltanoAlertSeverity,
    GruponosMeltanoAlertType
)

async def demonstrate_alert_management():
    """Demonstrate alert management and delivery."""
    
    # Create alert manager
    alert_manager = create_gruponos_meltano_alert_manager()
    
    # Send informational alert
    info_result = await alert_manager.send_alert(
        title="ETL Pipeline Started",
        message="Full synchronization pipeline has started for GNOS/DC01",
        severity=GruponosMeltanoAlertSeverity.INFO,
        alert_type=GruponosMeltanoAlertType.PIPELINE_START,
        context={
            "company_code": "GNOS",
            "facility_code": "DC01",
            "started_at": datetime.utcnow().isoformat()
        }
    )
    
    if info_result.is_success:
        print("Informational alert sent successfully")
    
    # Send error alert with rich context
    error_result = await alert_manager.send_alert(
        title="Data Validation Error Detected",
        message="Data validation failed during ETL processing",
        severity=GruponosMeltanoAlertSeverity.ERROR,
        alert_type=GruponosMeltanoAlertType.DATA_QUALITY,
        context={
            "company_code": "GNOS",
            "facility_code": "DC01",
            "error_count": 15,
            "total_records": 1000,
            "error_rate": 0.015,
            "validation_rules_failed": ["minimum_quantity", "location_format"],
            "recommended_action": "Review data source quality"
        }
    )
    
    if error_result.is_success:
        print("Error alert sent successfully")
```

## Running Examples

### Prerequisites
```bash
# Set up environment variables
export GRUPONOS_ORACLE_WMS_BASE_URL="https://wms-dev.company.com/api/v1"
export GRUPONOS_ORACLE_WMS_USERNAME="your_username"
export GRUPONOS_ORACLE_WMS_PASSWORD="your_password"
export GRUPONOS_ORACLE_TARGET_HOST="oracle-dev.company.com"
export GRUPONOS_ORACLE_TARGET_USERNAME="etl_user"
export GRUPONOS_ORACLE_TARGET_PASSWORD="your_db_password"
```

### Execution Commands
```bash
# Run configuration example
python examples/config_usage.py

# Run with development environment
GRUPONOS_ENVIRONMENT=development python examples/config_usage.py

# Run with debug logging
GRUPONOS_LOG_LEVEL=DEBUG python examples/config_usage.py
```

## Development Guidelines

### Creating New Examples
1. **Real Scenarios**: Use realistic business scenarios and data
2. **Error Handling**: Demonstrate proper error handling patterns
3. **Documentation**: Include comprehensive docstrings and comments
4. **FLEXT Patterns**: Follow FLEXT standards throughout examples
5. **Testing**: Ensure examples are tested and functional

### Example Structure
```python
"""
Example Title - Brief Description

Detailed description of what this example demonstrates,
including key concepts and patterns shown.
"""

# Imports with clear organization
from gruponos_meltano_native import create_gruponos_meltano_platform
from gruponos_meltano_native.config import GruponosMeltanoSettings

async def main():
    """Main example function with clear structure."""
    # Setup
    print("Setting up example...")
    
    # Demonstration
    print("Executing example logic...")
    
    # Results
    print("Example completed successfully")

if __name__ == "__main__":
    # Execute example
    import asyncio
    asyncio.run(main())
```

---

**Purpose**: Practical usage demonstrations  
**Standards**: FLEXT patterns with enterprise best practices  
**Coverage**: Complete workflow examples with error handling  
**Documentation**: Comprehensive comments and explanations