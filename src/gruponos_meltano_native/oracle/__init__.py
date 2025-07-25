"""Oracle Integration Module - FLEXT standardized.

This module provides Oracle database integration capabilities following FLEXT standards,
Clean Architecture principles, and proper type safety.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

# Direct imports - NO wrappers or legacy aliases
from gruponos_meltano_native.oracle.connection_manager_enhanced import (
    GruponosMeltanoOracleConnectionManager,
    create_gruponos_meltano_oracle_connection_manager,
)

# Public API exports - FLEXT standard only
__all__ = [
    # FLEXT Standard Classes
    "GruponosMeltanoOracleConnectionManager",
    # Factory Functions
    "create_gruponos_meltano_oracle_connection_manager",
]
