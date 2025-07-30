"""GrupoNOS Meltano Native Oracle Connection Manager - GRUPONOS specific implementation.

Professional Oracle connection management following FLEXT patterns
and Clean Architecture principles with proper type safety.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core import FlextResult

from gruponos_meltano_native.config import GruponosMeltanoOracleConnectionConfig

if TYPE_CHECKING:
    from flext_db_oracle import FlextDbOracleApi

# =============================================
# GRUPONOS ORACLE CONNECTION MANAGER
# =============================================


class GruponosMeltanoOracleConnectionManager:
    """GrupoNOS-specific Oracle connection manager."""

    def __init__(
        self,
        config: GruponosMeltanoOracleConnectionConfig | None = None,
    ) -> None:
        """Initialize Oracle connection manager for GrupoNOS."""
        self.config = config or GruponosMeltanoOracleConnectionConfig()
        self._connection: FlextDbOracleApi | None = None

    def get_connection(self) -> FlextResult[FlextDbOracleApi]:
        """Get Oracle database connection for GrupoNOS."""
        try:
            # Import here to avoid circular dependencies
            from flext_db_oracle import FlextDbOracleApi, FlextDbOracleConfig

            # Build connection config
            db_config = FlextDbOracleConfig(
                host=self.config.host,
                port=self.config.port,
                username=self.config.username,
                password=self.config.password,
                service_name=self.config.service_name,
                sid=self.config.sid,
                protocol=self.config.protocol,
            )

            # Create connection
            self._connection = FlextDbOracleApi(db_config)

            return FlextResult.ok(self._connection)

        except Exception as e:
            return FlextResult.fail(f"Failed to create Oracle connection: {e}")

    def test_connection(self) -> FlextResult[bool]:
        """Test Oracle database connection for GrupoNOS."""
        connection_result = self.get_connection()
        if not connection_result.is_success:
            return FlextResult.fail(f"Connection failed: {connection_result.error}")

        connection = connection_result.data
        if connection is None:
            return FlextResult.fail("Connection is None")

        test_result = connection.test_connection()

        if test_result.is_success:
            return FlextResult.ok(True)
        return FlextResult.fail(f"Connection test failed: {test_result.error}")

    def close_connection(self) -> FlextResult[bool]:
        """Close Oracle connection."""
        try:
            if self._connection:
                # disconnect() returns the API instance, not a FlextResult
                self._connection.disconnect()
                self._connection = None
                return FlextResult.ok(True)
            return FlextResult.ok(True)

        except Exception as e:
            return FlextResult.fail(f"Error closing connection: {e}")


# =============================================
# FACTORY FUNCTIONS
# =============================================


def create_gruponos_meltano_oracle_connection_manager(
    config: GruponosMeltanoOracleConnectionConfig | None = None,
) -> GruponosMeltanoOracleConnectionManager:
    """Create GrupoNOS Oracle connection manager instance."""
    return GruponosMeltanoOracleConnectionManager(config)


# =============================================
# EXPORTS
# =============================================


__all__ = [
    "GruponosMeltanoOracleConnectionManager",
    "create_gruponos_meltano_oracle_connection_manager",
]
