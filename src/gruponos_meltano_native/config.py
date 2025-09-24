"""GrupoNOS Meltano Native Configuration - Settings using flext-core patterns.

Provides GrupoNOS-specific configuration management extending FlextConfig
with Pydantic Settings for environment variable support and validation.

Copyright (c) 2025 Grupo Nós. Todos os direitos reservados.
SPDX-License-Identifier: Proprietary
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from pydantic_settings import SettingsConfigDict

from flext_core import FlextConfig


class GruponosMeltanoNativeConfig(FlextConfig):
    """GrupoNOS Meltano Native Configuration extending FlextConfig.

    Provides comprehensive configuration for GrupoNOS Oracle WMS integration
    and Meltano pipeline operations using Pydantic BaseSettings for validation
    and environment variable support with enhanced Pydantic 2.11 features.
    """

    model_config = SettingsConfigDict(
        env_prefix="GRUPONOS_MELTANO_NATIVE_",
        case_sensitive=False,
        extra="ignore",
        use_enum_values=True,
        validate_assignment=True,
        validate_default=True,
        frozen=False,
        # Enhanced Pydantic 2.11 features
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
