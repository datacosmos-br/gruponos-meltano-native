"""Oracle Connection Manager - NO DUPLICATION VERSION.

This module imports from connection_manager_enhanced to eliminate code duplication.
The enhanced version uses FLEXT-DB-Oracle enterprise features as per requirement:
"SEMPRE USE A DE ORIGEM" - always use original FLEXT libraries.
"""

# Re-export the main class for backward compatibility
# Import everything from the enhanced version to eliminate duplication
from gruponos_meltano_native.oracle.connection_manager_enhanced import (
    OracleConnectionManager,
    create_connection_manager_from_env,
)

# Explicitly make imports available for re-export
__all__ = ["OracleConnectionManager", "create_connection_manager_from_env"]
