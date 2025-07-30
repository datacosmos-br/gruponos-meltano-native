"""Infrastructure layer for GrupoNOS Meltano Native - FLEXT standardized.

This module provides FLEXT-standard infrastructure components following
Clean Architecture and Domain-Driven Design principles.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

# FLEXT Core Infrastructure - Direct imports ONLY
from flext_core import (
    FlextBaseSettings,
    FlextContainer,
    get_flext_container,
)

# GrupoNOS Meltano specific DI
from gruponos_meltano_native.infrastructure.di_container import (
    get_gruponos_meltano_container,
)

# FLEXT Standard Infrastructure Exports - NO legacy functions
__all__ = [
    # FLEXT Core Infrastructure
    "FlextBaseSettings",
    "FlextContainer",
    "get_flext_container",
    # GrupoNOS Meltano Infrastructure
    "get_gruponos_meltano_container",
]
