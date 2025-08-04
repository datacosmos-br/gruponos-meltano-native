# Oracle Integration Module

**Enterprise Oracle Database Integration for GrupoNOS Meltano Native**

This module provides high-performance Oracle database connectivity optimized for ETL operations, with connection pooling, health monitoring, and comprehensive error handling built on FLEXT database integration standards.

## Components

### `connection_manager_enhanced.py` - Enhanced Connection Management
Enterprise-grade Oracle connection management system optimized for large-scale ETL operations.

#### Key Classes

##### `GruponosMeltanoOracleConnectionManager`
Primary connection management system with enterprise features:
- **Connection Pooling**: High-performance connection pool with configurable limits
- **Health Monitoring**: Continuous health checks with automatic failover
- **Query Optimization**: Query performance monitoring and optimization
- **Transaction Management**: Robust transaction handling with rollback capabilities
- **Retry Logic**: Intelligent retry mechanisms with exponential backoff

#### Features

##### Connection Pooling
- **Pool Management**: Configurable min/max connections with automatic scaling
- **Connection Validation**: Pre-use connection validation to ensure reliability
- **Leak Detection**: Connection leak detection with automatic recovery
- **Performance Monitoring**: Connection usage metrics and performance tracking

##### Health Monitoring
- **Continuous Checks**: Regular health check execution with configurable intervals
- **Automatic Recovery**: Automatic connection recovery and pool refresh
- **Failover Support**: Multi-host failover configuration for high availability
- **Status Reporting**: Detailed health status reporting with metrics

##### Query Optimization
- **Performance Tracking**: Query execution time monitoring
- **Slow Query Detection**: Automatic detection of slow-running queries
- **Query Hints**: Oracle-specific query hints for ETL optimization
- **Batch Processing**: Optimized batch operations for large data volumes

## Usage Examples

### Basic Connection Management
```python
from gruponos_meltano_native.oracle import (
    create_gruponos_meltano_oracle_connection_manager,
    GruponosMeltanoOracleConnectionConfig
)

# Create connection configuration
config = GruponosMeltanoOracleConnectionConfig(
    host="oracle-prod.company.com",
    port=1521,
    service_name="PRODDB",
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
    # Use connection for ETL operations
    await conn.execute("SELECT COUNT(*) FROM allocations")
else:
    print(f"Connection failed: {connection_result.error}")
```

### ETL Pipeline Integration
```python
from contextlib import asynccontextmanager

class ETLDataProcessor:
    def __init__(self, connection_manager: GruponosMeltanoOracleConnectionManager):
        self.connection_manager = connection_manager
    
    @asynccontextmanager
    async def database_transaction(self):
        """Managed database transaction with automatic rollback."""
        connection_result = await self.connection_manager.get_connection()
        if connection_result.is_failure:
            raise Exception(f"Failed to get connection: {connection_result.error}")
        
        conn = connection_result.data
        transaction = await conn.begin()
        
        try:
            yield conn
            await transaction.commit()
        except Exception:
            await transaction.rollback()
            raise
        finally:
            await self.connection_manager.return_connection(conn)
    
    async def bulk_insert_allocations(self, allocations_data):
        """Bulk insert allocation data with transaction management."""
        async with self.database_transaction() as conn:
            # Prepare bulk insert statement
            insert_sql = """
                INSERT INTO wms_allocations 
                (allocation_id, item_code, quantity, facility_code, location, load_timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            
            # Execute bulk insert
            await conn.executemany(insert_sql, allocations_data)
            
            return len(allocations_data)
```

### Advanced Configuration
```python
from gruponos_meltano_native.config import GruponosMeltanoOracleConnectionConfig

# Advanced connection configuration
config = GruponosMeltanoOracleConnectionConfig(
    # Basic connection
    host="oracle-cluster.company.com",
    port=1521,
    service_name="ETLDB",
    username="etl_service",
    password="secure_password",
    
    # Connection pooling
    min_connections=5,
    max_connections=20,
    connection_timeout=30,
    
    # Health monitoring
    health_check_interval=60,
    max_retry_attempts=3,
    retry_delay_seconds=5,
    
    # Performance optimization
    enable_query_hints=True,
    batch_size=1000,
    fetch_size=10000,
    
    # Security
    enable_ssl=True,
    ssl_verify_certificate=True,
    wallet_location="/opt/oracle/wallet"
)

# Create connection manager with advanced configuration
manager = create_gruponos_meltano_oracle_connection_manager(config)
```

## Performance Optimization

### Query Optimization Features
```python
# ETL-optimized queries with hints
class OptimizedETLQueries:
    def __init__(self, connection_manager):
        self.connection_manager = connection_manager
    
    async def extract_incremental_data(self, last_sync_timestamp):
        """Extract incremental data with Oracle-specific optimizations."""
        query = """
            SELECT /*+ FIRST_ROWS(1000) INDEX(a, idx_mod_ts) */
                   allocation_id, item_code, quantity, facility_code, 
                   location, mod_ts
            FROM wms_allocations a
            WHERE mod_ts > :last_sync
            ORDER BY mod_ts
        """
        
        async with self.connection_manager.get_connection() as conn:
            cursor = await conn.execute(query, {"last_sync": last_sync_timestamp})
            
            # Fetch in batches for memory efficiency
            batch_size = 1000
            while True:
                batch = await cursor.fetchmany(batch_size)
                if not batch:
                    break
                yield batch
    
    async def bulk_upsert_with_merge(self, data_batch):
        """High-performance bulk upsert using Oracle MERGE statement."""
        merge_sql = """
            MERGE INTO target_allocations t
            USING (
                SELECT * FROM TABLE(?)
            ) s ON (t.allocation_id = s.allocation_id)
            WHEN MATCHED THEN
                UPDATE SET 
                    quantity = s.quantity,
                    location = s.location,
                    mod_ts = s.mod_ts
            WHEN NOT MATCHED THEN
                INSERT (allocation_id, item_code, quantity, facility_code, location, mod_ts)
                VALUES (s.allocation_id, s.item_code, s.quantity, s.facility_code, s.location, s.mod_ts)
        """
        
        async with self.connection_manager.get_connection() as conn:
            await conn.execute(merge_sql, [data_batch])
```

### Connection Pool Monitoring
```python
class ConnectionPoolMonitor:
    def __init__(self, connection_manager):
        self.connection_manager = connection_manager
    
    async def get_pool_metrics(self):
        """Get detailed connection pool metrics."""
        pool_stats = await self.connection_manager.get_pool_statistics()
        
        return {
            "active_connections": pool_stats.active_count,
            "idle_connections": pool_stats.idle_count,
            "total_connections": pool_stats.total_count,
            "peak_connections": pool_stats.peak_count,
            "connection_requests": pool_stats.request_count,
            "average_wait_time": pool_stats.average_wait_time_ms,
            "pool_utilization_percent": (pool_stats.active_count / pool_stats.total_count) * 100
        }
    
    async def check_pool_health(self):
        """Comprehensive pool health check."""
        health_result = await self.connection_manager.check_pool_health()
        
        if health_result.is_success:
            return {
                "status": "healthy",
                "metrics": await self.get_pool_metrics(),
                "last_health_check": health_result.data.timestamp
            }
        else:
            return {
                "status": "unhealthy",
                "error": health_result.error,
                "recommended_action": "Pool restart recommended"
            }
```

## Error Handling and Recovery

### Connection Failure Recovery
```python
class ResilientConnectionManager:
    def __init__(self, primary_config, failover_configs):
        self.primary_manager = create_gruponos_meltano_oracle_connection_manager(primary_config)
        self.failover_managers = [
            create_gruponos_meltano_oracle_connection_manager(config)
            for config in failover_configs
        ]
        self.current_manager = self.primary_manager
    
    async def get_connection_with_failover(self):
        """Get connection with automatic failover to backup instances."""
        # Try primary connection
        result = await self.current_manager.get_connection()
        if result.is_success:
            return result
        
        # Try failover connections
        for failover_manager in self.failover_managers:
            result = await failover_manager.get_connection()
            if result.is_success:
                self.current_manager = failover_manager
                await self._notify_failover_activated()
                return result
        
        # All connections failed
        return FlextResult.fail("All database connections failed")
    
    async def _notify_failover_activated(self):
        """Notify operations team of failover activation."""
        # Send alert about failover
        pass
```

### Transaction Recovery
```python
class TransactionManager:
    def __init__(self, connection_manager):
        self.connection_manager = connection_manager
    
    async def execute_with_retry(self, operation, max_retries=3):
        """Execute database operation with retry logic."""
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                async with self.connection_manager.get_connection() as conn:
                    return await operation(conn)
            
            except DatabaseConnectionError as e:
                last_error = e
                if attempt < max_retries:
                    wait_time = 2 ** attempt  # Exponential backoff
                    await asyncio.sleep(wait_time)
                    continue
                break
            
            except Exception as e:
                # Non-recoverable error
                return FlextResult.fail(f"Operation failed: {str(e)}")
        
        return FlextResult.fail(f"Operation failed after {max_retries} retries: {str(last_error)}")
```

## Configuration

### Environment Variables
```bash
# Basic Oracle connection
GRUPONOS_ORACLE_HOST=oracle-prod.company.com
GRUPONOS_ORACLE_PORT=1521
GRUPONOS_ORACLE_SERVICE_NAME=PRODDB
GRUPONOS_ORACLE_USERNAME=etl_user
GRUPONOS_ORACLE_PASSWORD=secure_password
GRUPONOS_ORACLE_SCHEMA=WMS_DATA

# Connection pooling
GRUPONOS_ORACLE_MIN_CONNECTIONS=5
GRUPONOS_ORACLE_MAX_CONNECTIONS=20
GRUPONOS_ORACLE_CONNECTION_TIMEOUT=30

# Performance tuning
GRUPONOS_ORACLE_BATCH_SIZE=1000
GRUPONOS_ORACLE_FETCH_SIZE=10000
GRUPONOS_ORACLE_ENABLE_QUERY_HINTS=true

# Security
GRUPONOS_ORACLE_ENABLE_SSL=true
GRUPONOS_ORACLE_WALLET_LOCATION=/opt/oracle/wallet
```

## Testing Support

### Mock Connection Manager
```python
class MockOracleConnectionManager:
    def __init__(self):
        self.mock_data = {}
        self.connection_calls = []
    
    async def get_connection(self):
        self.connection_calls.append(datetime.utcnow())
        return FlextResult.ok(MockConnection(self.mock_data))
    
    def set_mock_data(self, table_name, data):
        self.mock_data[table_name] = data
    
    def get_connection_count(self):
        return len(self.connection_calls)
```

### Integration Testing
```python
@pytest.mark.integration
async def test_oracle_connection_pool():
    """Test connection pool under load."""
    config = get_test_oracle_config()
    manager = create_gruponos_meltano_oracle_connection_manager(config)
    
    # Simulate concurrent connections
    async def get_connection_task():
        result = await manager.get_connection()
        assert result.is_success
        await asyncio.sleep(0.1)  # Simulate work
        await manager.return_connection(result.data)
    
    # Execute 50 concurrent connection requests
    tasks = [get_connection_task() for _ in range(50)]
    await asyncio.gather(*tasks)
    
    # Verify pool health
    pool_health = await manager.check_pool_health()
    assert pool_health.is_success
```

## Development Guidelines

### Connection Management Best Practices
1. **Always Use Context Managers**: Ensure proper connection cleanup
2. **Monitor Pool Health**: Regular health checks and monitoring
3. **Handle Failures Gracefully**: Comprehensive error handling and recovery
4. **Optimize for ETL**: Use batch operations and appropriate fetch sizes
5. **Security First**: Secure credential management and SSL connections

### Performance Optimization
1. **Connection Pooling**: Proper pool sizing for workload
2. **Query Optimization**: Use Oracle-specific hints and optimizations
3. **Batch Operations**: Minimize round trips with bulk operations
4. **Memory Management**: Appropriate fetch sizes for large result sets
5. **Monitoring**: Continuous performance monitoring and alerting

---

**Purpose**: Enterprise Oracle database integration  
**Performance**: Optimized for large-scale ETL operations  
**Reliability**: Connection pooling with health monitoring  
**Integration**: Full FLEXT database abstraction compatibility