"""Core module for Gruponos Meltano Native.

Provides core functionality and utilities for Gruponos Meltano Native integration.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from gruponos_meltano_native.core.external_command import (
    ExternalCommandResult,
    run_external_command,
)

__all__ = ["ExternalCommandResult", "run_external_command"]
