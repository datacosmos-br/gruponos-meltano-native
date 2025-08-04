"""GrupoNOS Meltano Native Validators - FLEXT standardized validation.

This module provides data validation capabilities following FLEXT standards
and Clean Architecture principles.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import contextlib

# FLEXT Standard Validation Components
with contextlib.suppress(ImportError):
    from gruponos_meltano_native.validators.data_validator import (
        DataValidator as _DataValidator,
        create_validator_for_environment as _create_validator_for_environment,
    )

    # FLEXT Standard Validation Classes
    class GruponosMeltanoDataValidator(_DataValidator):
        """GrupoNOS Meltano data validator following FLEXT standards."""

    # FLEXT Standard Factory Function
    def create_gruponos_meltano_validator_for_environment(
        environment: str = "dev",
        **kwargs: object,
    ) -> GruponosMeltanoDataValidator:
        """Create GrupoNOS Meltano data validator for environment.

        Args:
            environment: Target environment (dev, prod, etc.)
            **kwargs: Additional configuration parameters

        Returns:
            Configured GruponosMeltanoDataValidator instance

        """
        base_validator = _create_validator_for_environment(environment)
        # DataValidator doesn't have config - pass the constructor args
        return GruponosMeltanoDataValidator(
            rules=getattr(base_validator, "rules", None),
            strict_mode=getattr(base_validator, "strict_mode", False),
        )

    # Backward compatibility aliases
    DataValidator = GruponosMeltanoDataValidator  # Legacy alias
    create_validator_for_environment = (
        create_gruponos_meltano_validator_for_environment  # Legacy alias
    )

# FLEXT Standard Validation Exports
__all__: list[str] = [
    # Legacy Compatibility (deprecated)
    "DataValidator",
    # FLEXT Standard Classes
    "GruponosMeltanoDataValidator",
    # FLEXT Standard Factory Functions
    "create_gruponos_meltano_validator_for_environment",
    "create_validator_for_environment",
]
