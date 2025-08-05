# Infrastructure Module

**Cross-Cutting Infrastructure Concerns for GrupoNOS Meltano Native**

This module provides enterprise infrastructure patterns including dependency injection, service location, and system integration components that support the ETL pipeline operations with FLEXT framework standards.

## Components

### `di_container.py` - Dependency Injection Container

Enterprise dependency injection system built on FLEXT container patterns for loose coupling and testability.

#### Features

- **Service Registration**: Type-safe service registration with lifecycle management
- **Dependency Resolution**: Automatic dependency resolution with circular dependency detection
- **Singleton Support**: Configurable singleton pattern for shared resources
- **FLEXT Integration**: Full compatibility with FLEXT container ecosystem

#### Key Classes

- **`GruponosMeltanoContainer`**: Main DI container extending FLEXT patterns
- **Service Factories**: Factory functions for core ETL components
- **Lifecycle Management**: Service initialization and cleanup coordination

#### Usage Example

```python
from gruponos_meltano_native.infrastructure import GruponosMeltanoContainer

# Create container with ETL services
container = GruponosMeltanoContainer()

# Register services
container.register_singleton("oracle_manager", create_oracle_connection_manager)
container.register_transient("data_validator", create_data_validator)

# Resolve services
oracle_manager = container.resolve("oracle_manager")
validator = container.resolve("data_validator")
```

## Architecture Integration

### Clean Architecture Compliance

The infrastructure module sits at the outermost layer of Clean Architecture, providing:

- **External Concerns**: Database connections, external API integrations
- **Cross-Cutting Services**: Logging, caching, monitoring integration
- **System Resources**: Connection pooling, resource management

### FLEXT Standards

- **Container Patterns**: Extends FLEXT container with ETL-specific services
- **Error Handling**: Uses FlextResult for all infrastructure operations
- **Configuration**: Integrates with FLEXT configuration management
- **Observability**: Full FLEXT observability integration

## Dependency Management

### Service Lifecycle

```python
# Service registration with lifecycle
container.register_singleton("connection_pool",
    factory=create_connection_pool,
    cleanup=lambda pool: pool.close_all()
)

# Automatic cleanup on container disposal
container.dispose()  # Calls cleanup for all registered services
```

### Service Dependencies

```python
# Services with dependencies
def create_etl_orchestrator(container: GruponosMeltanoContainer):
    return GruponosMeltanoOrchestrator(
        oracle_manager=container.resolve("oracle_manager"),
        validator=container.resolve("data_validator"),
        alert_manager=container.resolve("alert_manager")
    )

container.register_transient("orchestrator", create_etl_orchestrator)
```

## Testing Support

### Mock Services

```python
# Test container with mocked services
test_container = GruponosMeltanoContainer()
test_container.register_singleton("oracle_manager", mock_oracle_manager)
test_container.register_singleton("alert_manager", mock_alert_manager)

# Test orchestrator with mocked dependencies
orchestrator = test_container.resolve("orchestrator")
```

### Integration Testing

```python
# Real services for integration testing
integration_container = GruponosMeltanoContainer()
integration_container.configure_for_testing()  # Real but test-safe services
```

## Configuration Integration

### Environment-Aware Services

```python
from gruponos_meltano_native.config import GruponosMeltanoSettings

def configure_container_for_environment(container: GruponosMeltanoContainer):
    settings = GruponosMeltanoSettings()

    if settings.environment == "production":
        container.register_production_services()
    elif settings.environment == "development":
        container.register_development_services()
    else:
        container.register_test_services()
```

## Performance Considerations

### Resource Management

- **Connection Pooling**: Efficient database connection management
- **Memory Management**: Proper cleanup of large data processing resources
- **Caching**: Strategic caching of expensive operations
- **Monitoring**: Performance metrics collection

### Scalability Patterns

- **Service Isolation**: Each service can be scaled independently
- **Resource Limits**: Configurable resource consumption limits
- **Circuit Breakers**: Automatic failure handling and recovery
- **Health Checks**: Continuous service health monitoring

## Error Handling

### Infrastructure Failures

```python
# Robust service resolution with fallbacks
def get_service_with_fallback(container, service_name, fallback_factory):
    result = container.try_resolve(service_name)
    if result.success:
        return result

    # Create fallback service
    fallback_service = fallback_factory()
    container.register_singleton(service_name, lambda: fallback_service)
    return FlextResult.ok(fallback_service)
```

### Circuit Breaker Pattern

```python
# Service with circuit breaker
class ServiceWithCircuitBreaker:
    def __init__(self, actual_service, circuit_breaker):
        self.service = actual_service
        self.circuit_breaker = circuit_breaker

    async def execute_operation(self, *args, **kwargs):
        return await self.circuit_breaker.execute(
            lambda: self.service.execute_operation(*args, **kwargs)
        )
```

## Development Guidelines

### Service Creation Standards

1. **FLEXT Integration**: All services must use FLEXT patterns
2. **Error Handling**: FlextResult for all operations
3. **Type Safety**: Complete type annotations
4. **Testing**: Comprehensive unit and integration tests
5. **Documentation**: Detailed docstrings with examples

### Container Configuration

1. **Environment Awareness**: Different configurations per environment
2. **Resource Management**: Proper cleanup and disposal
3. **Health Monitoring**: Service health checks
4. **Performance Metrics**: Resource usage tracking

---

**Purpose**: Enterprise infrastructure with FLEXT standards  
**Pattern**: Dependency injection with service location  
**Integration**: Full FLEXT ecosystem compatibility  
**Testing**: Comprehensive mock and integration support
