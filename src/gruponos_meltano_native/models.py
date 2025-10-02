"""Models for Grupo Nos Meltano Native operations.

This module provides data models for Grupo Nos Meltano Native operations.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from pydantic import (
    ConfigDict,
    Field,
    field_validator,
)

from flext_core import FlextModels
from gruponos_meltano_native.constants import GruponosMeltanoNativeConstants

"""GrupoNOS Meltano Native Models - Domain models with Pydantic v2.

Provides GrupoNOS-specific models extending FlextModels for
Oracle WMS integration and Meltano pipeline operations.

Copyright (c) 2025 Grupo Nós. Todos os direitos reservados.
SPDX-License-Identifier: Proprietary
"""


class GruponosMeltanoNativeModels(FlextModels):
    """GrupoNOS Meltano Native models extending FlextModels.

    Contains all Pydantic models for GrupoNOS Oracle WMS integration
    and Meltano pipeline operations following FLEXT standards with
    enhanced Pydantic 2.11 features and comprehensive validation.
    """

    # Enhanced base models with Pydantic 2.11 features
    class _BaseEntity(FlextModels.Entity):
        """Enhanced base entity with GrupoNOS-specific fields and validation."""

        model_config = ConfigDict(
            # Enhanced Pydantic 2.11 features
            validate_assignment=True,
            use_enum_values=True,
            arbitrary_types_allowed=True,
            validate_return=True,
            serialize_by_alias=True,
            populate_by_name=True,
            ser_json_timedelta="iso8601",
            ser_json_bytes="base64",
            str_strip_whitespace=True,
            defer_build=False,
            coerce_numbers_to_str=False,
            enable_decoding=True,
            # Custom encoders for complex types
            json_encoders={
                Path: str,
                datetime: lambda dt: dt.isoformat(),
            },
        )

        status: str = Field(
            default=GruponosMeltanoNativeConstants.Status.PENDING.value,
            description="Entity status",
        )
        metadata: dict[str, object] = Field(
            default_factory=dict, description="Additional metadata"
        )

        @field_validator("status")
        @classmethod
        def validate_status(cls, v: str) -> str:
            """Validate status against allowed values."""
            valid_statuses = [e.value for e in GruponosMeltanoNativeConstants.Status]
            if v not in valid_statuses:
                msg = f"Invalid status: {v}. Valid statuses: {valid_statuses}"
                raise ValueError(msg)
            return v
