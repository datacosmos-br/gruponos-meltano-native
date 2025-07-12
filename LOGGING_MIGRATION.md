# Logging Migration Report for gruponos-meltano-native

## Summary

Total files with logging imports: 7

## Files to Migrate

- `src/validators/data_validator.py:8` - `import logging`
- `src/oracle/connection_manager.py:9` - `import logging`
- `src/oracle/discover_and_save_schemas.py:9` - `import logging`
- `src/oracle/recreate_tables_and_sync.py:8` - `import logging`
- `src/oracle/table_creator.py:13` - `import logging`
- `src/oracle/validate_sync.py:5` - `import logging`
- `src/monitoring/alert_manager.py:13` - `import logging`

## Migration Steps

1. Replace logging imports:

   ```python
   # Old
   import logging
   logger = logging.getLogger(__name__)

   # New
   from flext_observability.logging import get_logger
   logger = get_logger(__name__)
   ```

2. Add setup_logging to your main entry point:

   ```python
   from flext_observability import setup_logging

   setup_logging(
       service_name="gruponos-meltano-native",
       log_level="INFO",
       json_logs=True
   )
   ```

3. Update logging calls to use structured format:

   ```python
   # Old
   logger.info("Processing %s items", count)

   # New
   logger.info("Processing items", count=count)
   ```

See `examples/logging_migration.py` for a complete example.
