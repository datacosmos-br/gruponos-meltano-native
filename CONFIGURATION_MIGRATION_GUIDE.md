# Configuration Migration Guide

## Overview

The `gruponos-meltano-native` project has been upgraded to use a flexible, environment-based configuration system. Previously hardcoded values in the `flext-tap-oracle-wms` component are now configurable via environment variables and meltano.yml settings.

## What Changed

### Before (Hardcoded)
```python
# In flext-tap-oracle-wms source code
WMS_MAX_PAGE_SIZE = 1250
WMS_DEFAULT_PAGE_SIZE = 100
oauth_scope = "wms.read"
timeout = 120
```

### After (Configurable)
```bash
# In .env file
WMS_MAX_PAGE_SIZE=1250
WMS_DEFAULT_PAGE_SIZE=100
WMS_OAUTH_SCOPE=wms.read
WMS_REQUEST_TIMEOUT=120
```

```yaml
# In meltano.yml
config:
  wms_api_version: $WMS_API_VERSION
  page_size: $WMS_PAGE_SIZE
  request_timeout: $WMS_REQUEST_TIMEOUT
  oauth_scope: $WMS_OAUTH_SCOPE
```

## Migration Steps

### 1. Copy Environment Template
```bash
cd /home/marlonsc/flext/gruponos-meltano-native
cp .env.example .env
```

### 2. Configure Required Variables
Edit `.env` file and set the required connection settings:

```bash
# REQUIRED - WMS Connection
TAP_ORACLE_WMS_BASE_URL=https://your-wms-instance.com
TAP_ORACLE_WMS_USERNAME=your_username
TAP_ORACLE_WMS_PASSWORD=your_password

# REQUIRED - Oracle Database
FLEXT_TARGET_ORACLE_HOST=your-oracle-host
FLEXT_TARGET_ORACLE_SERVICE_NAME=your_service_name
FLEXT_TARGET_ORACLE_USERNAME=your_oracle_username
FLEXT_TARGET_ORACLE_PASSWORD=your_oracle_password
```

### 3. Customize Performance Settings
Adjust performance settings for your environment:

```bash
# Full sync settings
WMS_PAGE_SIZE=100
WMS_REQUEST_TIMEOUT=3600
WMS_BATCH_SIZE_ROWS=100

# Incremental sync settings  
WMS_INCREMENTAL_PAGE_SIZE=100
WMS_INCREMENTAL_REQUEST_TIMEOUT=2700
WMS_LOOKBACK_MINUTES=30
```

### 4. Environment-Specific Overrides
For different environments (dev, staging, prod), you can override specific settings:

```bash
# Development environment
WMS_PAGE_SIZE=50
WMS_REQUEST_TIMEOUT=600
WMS_LOG_LEVEL=DEBUG

# Production environment
WMS_PAGE_SIZE=500
WMS_REQUEST_TIMEOUT=7200
WMS_LOG_LEVEL=INFO
```

## Configuration Categories

### Core Connection Settings (Required)
- `TAP_ORACLE_WMS_BASE_URL`
- `TAP_ORACLE_WMS_USERNAME` 
- `TAP_ORACLE_WMS_PASSWORD`
- `FLEXT_TARGET_ORACLE_HOST`
- `FLEXT_TARGET_ORACLE_SERVICE_NAME`
- `FLEXT_TARGET_ORACLE_USERNAME`
- `FLEXT_TARGET_ORACLE_PASSWORD`

### WMS API Configuration
- `WMS_API_VERSION` - WMS API version (default: v10)
- `WMS_API_PATH_PATTERN` - API path pattern with {version} placeholder
- `WMS_PAGE_MODE` - Pagination mode (default: sequenced)
- `WMS_ORDERING` - Default field for ordering results
- `WMS_REPLICATION_KEY` - Field for incremental replication

### Performance Settings
- `WMS_PAGE_SIZE` - Records per page for full sync
- `WMS_INCREMENTAL_PAGE_SIZE` - Records per page for incremental sync
- `WMS_REQUEST_TIMEOUT` - Request timeout in seconds
- `WMS_MAX_RETRIES` - Maximum retry attempts
- `WMS_RETRY_WAIT_MULTIPLIER` - Exponential backoff multiplier

### Cache Settings
- `WMS_CATALOG_CACHE_TTL` - Catalog cache TTL in seconds
- `WMS_SCHEMA_CACHE_TTL` - Schema cache TTL in seconds

### Security Settings
- `WMS_OAUTH_SCOPE` - OAuth2 scope for WMS access
- `WMS_TOKEN_BUFFER_SECONDS` - Token expiration buffer
- `WMS_USER_AGENT` - User agent string for requests

## Benefits of New Configuration System

### 1. Environment Portability
- Same codebase works across dev/staging/prod
- No hardcoded values specific to one environment
- Easy deployment configuration management

### 2. Performance Tuning
- Adjust timeouts, page sizes, retry logic per environment
- Fine-tune for different data volumes and network conditions
- Optimize cache settings based on infrastructure

### 3. Security and Compliance
- Externalize all sensitive configuration
- Environment-specific authentication settings
- Configurable security parameters

### 4. Operational Flexibility
- Change settings without code modifications
- Runtime configuration adjustments
- Better troubleshooting with configurable logging

## Testing the Migration

### 1. Validate Configuration
```bash
# Test configuration loading
meltano config tap-oracle-wms-full list

# Test connection
meltano invoke tap-oracle-wms-full --help
```

### 2. Test Full Sync
```bash
# Small test with limited data
export WMS_PAGE_SIZE=10
export WMS_MAX_SYNC_DURATION=300
meltano run tap-oracle-wms-full target-oracle-full
```

### 3. Test Incremental Sync
```bash
# Test incremental with short lookback
export WMS_LOOKBACK_MINUTES=5
export WMS_INCREMENTAL_PAGE_SIZE=10
meltano run tap-oracle-wms-incremental target-oracle-incremental
```

## Troubleshooting

### Configuration Issues
```bash
# Check environment variables are loaded
env | grep WMS_

# Verify meltano sees the configuration
meltano config tap-oracle-wms-full list
```

### Performance Issues
```bash
# Enable debug logging
export WMS_LOG_LEVEL=DEBUG
export WMS_ULTRA_DEBUG=true

# Reduce load for testing
export WMS_PAGE_SIZE=10
export WMS_REQUEST_TIMEOUT=60
```

### Connection Issues
```bash
# Test WMS connectivity
curl -u $TAP_ORACLE_WMS_USERNAME:$TAP_ORACLE_WMS_PASSWORD \
  "$TAP_ORACLE_WMS_BASE_URL/wms/lgfapi/v10/entity"

# Test Oracle connectivity
sqlplus $FLEXT_TARGET_ORACLE_USERNAME/$FLEXT_TARGET_ORACLE_PASSWORD@$FLEXT_TARGET_ORACLE_HOST:1522/$FLEXT_TARGET_ORACLE_SERVICE_NAME
```

## Production Deployment Recommendations

### Performance Settings
```bash
# Production-optimized settings
WMS_PAGE_SIZE=500
WMS_REQUEST_TIMEOUT=7200
WMS_MAX_RETRIES=5
WMS_RETRY_WAIT_MULTIPLIER=2.0
WMS_CATALOG_CACHE_TTL=14400  # 4 hours
WMS_SCHEMA_CACHE_TTL=14400   # 4 hours
```

### Monitoring Settings
```bash
# Production monitoring
WMS_LOG_LEVEL=INFO
WMS_PROGRESS_LOG_FREQUENCY=1000
WMS_ULTRA_DEBUG=false
```

### Security Settings
```bash
# Production security
WMS_MIN_USERNAME_LENGTH=8
WMS_MIN_PASSWORD_LENGTH=12
WMS_TOKEN_BUFFER_SECONDS=60
```

## Rollback Plan

If issues occur, you can temporarily revert to static configuration by:

1. Setting environment variables to match previous hardcoded values
2. Using the `inherit_from` mechanism in meltano.yml to share base configs
3. Gradually migrating individual settings rather than all at once

## Support

For issues with the new configuration system:

1. Check `.env.example` for correct variable names and formats
2. Verify meltano.yml syntax and variable references
3. Test with minimal configuration first
4. Enable debug logging for detailed troubleshooting

The new system provides much more flexibility while maintaining backward compatibility through sensible defaults.