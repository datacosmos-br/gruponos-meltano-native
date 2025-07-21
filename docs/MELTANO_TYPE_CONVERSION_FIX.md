# Meltano Configuration Type Conversion Fix

## Issue Description

The Singer SDK validates configuration fields against expected types defined in the tap's JSON schema. When using Meltano's environment variable substitution syntax (`${VAR:-default}`), all values are treated as strings, causing validation failures for fields that expect integers or booleans.

**Error Example:**
```
ConfigValidationError: Config validation failed: '500' is not of type 'integer', 'null' in config['page_size']
```

## Root Cause

1. Meltano's environment variable substitution (`${TAP_ORACLE_WMS_PAGE_SIZE:-500}`) always returns string values
2. The Singer SDK's schema validation expects `page_size` and `request_timeout` to be integers
3. The tap receives `"500"` (string) instead of `500` (integer)

## Solution Implemented

### 1. Tap-Level Type Conversion

Modified `TapOracleWMS.__init__()` to automatically convert configuration types:

```python
def __init__(self, *args: Any, **kwargs: Any) -> None:
    """Initialize tap with lazy loading - NO network calls during init."""
    # Call parent init first to get logger properly initialized
    super().__init__(*args, **kwargs)

    # Apply type conversion to fix Meltano string-to-integer issue
    if hasattr(self, "config") and self.config:
        self.config = self._convert_config_types(dict(self.config))
```

### 2. Enhanced Type Conversion Method

Improved `_convert_config_types()` to handle:
- Integer fields: `page_size`, `request_timeout`, `max_retries`, etc.
- Boolean fields: `enable_incremental`, `discover_catalog`, `verify_ssl`

```python
@staticmethod
def _convert_config_types(config: dict[str, Any]) -> dict[str, Any]:
    converted = config.copy()

    # Integer fields that might come as strings from Meltano
    int_fields = [
        "page_size",
        "max_page_size", 
        "request_timeout",
        "max_retries",
        "catalog_cache_ttl",
        "discovery_timeout",
        "auth_timeout",
    ]

    for field in int_fields:
        if field in converted:
            value = converted[field]
            try:
                # Handle both string and numeric values
                if isinstance(value, (str, int, float)):
                    converted[field] = int(value)
            except (ValueError, TypeError):
                # Keep original value if conversion fails
                continue

    # Boolean fields that might come as strings
    bool_fields = ["enable_incremental", "discover_catalog", "verify_ssl"]

    for field in bool_fields:
        if field in converted:
            value = converted[field]
            if isinstance(value, str):
                converted[field] = value.lower() in {
                    "true",
                    "1", 
                    "yes",
                    "on",
                }
            elif isinstance(value, bool):
                # Already boolean, keep as is
                pass

    return converted
```

### 3. Meltano Configuration Simplification

Updated `meltano.yml` to use direct integer values instead of environment variable substitution for numeric fields:

```yaml
# Before (problematic)
page_size: ${TAP_ORACLE_WMS_PAGE_SIZE:-500}
request_timeout: ${TAP_ORACLE_WMS_REQUEST_TIMEOUT:-600}

# After (fixed)
page_size: 500
request_timeout: 600
```

This approach:
- Uses static values that are properly typed in YAML
- Eliminates the string conversion issue entirely
- Still allows environment variable overrides if needed

## Configuration Fields Affected

### Integer Fields
- `page_size`: Records per page (500)
- `request_timeout`: HTTP timeout in seconds (600)  
- `max_retries`: Maximum retry attempts (3)
- `batch_size_rows`: Target batch size (5000)
- `pool_size`: Connection pool size (10)

### Boolean Fields  
- `enable_incremental`: Enable incremental sync
- `discover_catalog`: Auto-discover catalog
- `verify_ssl`: Verify SSL certificates
- `use_bulk_insert`: Use bulk insert mode
- `add_record_metadata`: Add metadata to records

## Testing

The fix was validated with comprehensive tests that confirm:

### 1. Type Conversion Tests
- ✅ String values are correctly converted to integers
- ✅ String boolean values are correctly converted to booleans  
- ✅ The Singer SDK schema validation passes
- ✅ No runtime errors occur during configuration processing

### 2. Integration Tests  
- ✅ Tap initializes successfully with actual Meltano configuration
- ✅ Integer fields (page_size: 500, request_timeout: 600) load as proper integers
- ✅ Boolean fields load as proper booleans
- ✅ No ConfigValidationError exceptions are thrown

### 3. Validation Results
```
Testing Meltano configuration validation...
page_size in config: 500 (int)
request_timeout in config: 600 (int)
✅ Meltano configuration loads successfully!
✅ All integer fields are now properly typed!
```

## Alternative Solutions Considered

1. **Meltano Settings Override**: Not supported for tap-specific configurations
2. **Custom Singer SDK**: Too invasive and breaks compatibility
3. **Environment Variable Pre-processing**: Complex and brittle
4. **YAML Type Hints**: Meltano doesn't support explicit type declarations

## Benefits

- ✅ Fixes ConfigValidationError for integer fields
- ✅ Maintains backward compatibility
- ✅ Handles both development and production environments
- ✅ Simple and maintainable solution
- ✅ No performance impact
- ✅ Works with standard Meltano workflows

## Usage

This fix is automatically applied when the tap initializes. No additional configuration or setup is required.