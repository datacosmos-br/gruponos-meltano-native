"""FLEXT Integration Migration Guide.

This module documents the migration from duplicated code to pure FLEXT libraries.

ORIGINAL APPROACH (PROBLEMATIC):
- Manual DDL generation (table_creator.py)
- Custom type mapping (type_mapping_rules.py)
- Manual table recreation (recreate_tables_and_sync.py)

CORRECTED FLEXT APPROACH:
- flext-tap-oracle-wms: Handles ALL WMS REST API extraction
- flext-target-oracle: Handles ALL database operations automatically
- No manual DDL: Target creates schemas automatically from Singer streams
- No manual types: Target maps types automatically using flext-db-oracle
- No manual sync: Meltano orchestrates Singer protocol end-to-end

MIGRATION STEPS COMPLETED:
1. ✅ Updated meltano.yml to use flext-tap-oracle-wms and flext-target-oracle executables
2. ✅ Fixed configuration structure to use oracle_config nested format
3. ✅ Updated connection_manager_enhanced.py to use ResilientOracleConnection from flext-db-oracle
4. 🔄 IN PROGRESS: Removing duplicated DDL and type mapping code
5. ⏭️ TODO: Update integration tests to use pure Singer protocol

ZERO TOLERANCE PRINCIPLE:
"SEMPRE USE A DE ORIGEM" - Always use original FLEXT libraries
No exceptions, no fallbacks, no double implementations.

The Oracle WMS synchronization should work 100% through:
meltano run tap-oracle-wms-full target-oracle-full

All schema creation, type mapping, and data loading handled automatically.
"""
