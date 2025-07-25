"""GrupoNOS Meltano Native Oracle Connection Manager - FLEXT standardized.

Professional Oracle connection management following FLEXT patterns
and Clean Architecture principles with proper type safety.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

# FLEXT Core Standards
from flext_core import FlextResult

# Oracle database imports - TYPE_CHECKING to avoid runtime dependency issues
if TYPE_CHECKING:
    from flext_db_oracle.connection.config import ConnectionConfig

from gruponos_meltano_native.exceptions import (
    GruponosMeltanoOracleConnectionError,
    GruponosMeltanoOracleError,
)

if TYPE_CHECKING:
    from gruponos_meltano_native.config import GruponosMeltanoOracleConnectionConfig

# Use standard logging for Oracle connection management
from flext_core import FlextLoggerFactory
from flext_core.patterns.typedefs import FlextLoggerName

logger_factory = FlextLoggerFactory()
logger = logger_factory.create_logger(FlextLoggerName(__name__))


class GruponosMeltanoOracleConnectionManager:
    """GrupoNOS Meltano Oracle connection manager following FLEXT patterns.

    Professional Oracle connection management with enterprise features:
    - Connection validation and health monitoring
    - Proper error handling with FlextResult
    - Configuration validation
    - Clean logging without external dependencies
    """

    def __init__(self, config: GruponosMeltanoOracleConnectionConfig) -> None:
        """Initialize Oracle connection manager with configuration.

        Args:
            config: Oracle connection configuration

        """
        self.config = config
        self._connection_attempts = 0
        self._is_connected = False
        self._oracle_config: ConnectionConfig | None = None

        # Validate configuration on initialization
        config.validate_domain_rules()

        logger.info(
            f"GrupoNOS Meltano Oracle Connection Manager initialized - "
            f"host: {config.host}, port: {config.port}, service_name: {config.service_name}, protocol: {config.protocol}",
        )

    def _get_oracle_config(self) -> ConnectionConfig:
        """Get or create Oracle configuration for flext-db-oracle."""
        if self._oracle_config is None:
            # Import at runtime to avoid dependency issues
            from flext_db_oracle.connection.config import ConnectionConfig
            from pydantic import SecretStr

            self._oracle_config = ConnectionConfig(
                host=self.config.host,
                port=self.config.port,
                service_name=self.config.service_name,
                username=self.config.username,
                password=SecretStr(self.config.password),
                protocol=self.config.protocol,
            )
        return self._oracle_config

    def test_connection(self) -> FlextResult[dict[str, Any]]:
        """Test Oracle database connection.

        Returns:
            FlextResult with connection test results

        """
        try:
            self._connection_attempts += 1

            logger.info(
                f"Testing Oracle connection (attempt {self._connection_attempts}): "
                f"{self.config.host}:{self.config.port}/{self.config.service_name}",
            )

            # Get Oracle configuration using DRY principle
            oracle_config = self._get_oracle_config()

            # Import at runtime to avoid dependency issues
            from flext_db_oracle.connection.resilient_connection import (
                FlextDbOracleResilientConnection,
            )

            # Test actual connection
            conn = FlextDbOracleResilientConnection(oracle_config)
            try:
                conn.connect()
                result = conn.fetch_one("SELECT 1 FROM DUAL")

                if result and result[0] == 1:
                    test_result = {
                        "success": True,
                        "host": self.config.host,
                        "port": self.config.port,
                        "service_name": self.config.service_name,
                        "protocol": self.config.protocol,
                        "connection_attempts": self._connection_attempts,
                        "message": "Oracle connection test successful",
                        "oracle_version": conn.get_version(),
                    }
                    self._is_connected = True
                    logger.info("Oracle connection test successful")
                else:
                    msg = "Oracle connection test failed: invalid response"
                    raise ConnectionError(msg)
            finally:
                conn.disconnect()

            return FlextResult.ok(test_result)

        except Exception as e:
            logger.exception(f"Oracle connection test failed: {e}")
            self._is_connected = False
            msg = f"Oracle connection test failed: {e}"
            raise GruponosMeltanoOracleConnectionError(
                msg,
                context={"host": self.config.host, "port": self.config.port},
            ) from e

    def connect(self) -> FlextResult[bool]:
        """Establish connection to Oracle database.

        Returns:
            FlextResult indicating connection success

        """
        try:
            # Test connection first
            test_result = self.test_connection()
            if not test_result.is_success:
                return FlextResult.fail(test_result.error or "Connection test failed")

            logger.info("Oracle connection established successfully")
            return FlextResult.ok(True)

        except GruponosMeltanoOracleConnectionError:
            raise
        except Exception as e:
            logger.exception(f"Failed to connect to Oracle database: {e}")
            msg = f"Connection failed: {e}"
            raise GruponosMeltanoOracleConnectionError(
                msg,
                context={"host": self.config.host, "port": self.config.port},
            ) from e

    def disconnect(self) -> FlextResult[bool]:
        """Disconnect from Oracle database.

        Returns:
            FlextResult indicating disconnection success

        """
        try:
            if self._is_connected:
                # Reset connection state
                self._is_connected = False
                self._oracle_config = None
                logger.info("Oracle connection closed successfully")

            return FlextResult.ok(True)

        except Exception as e:
            logger.exception(f"Failed to disconnect from Oracle database: {e}")
            return FlextResult.fail(f"Disconnection failed: {e}")

    def execute_query(
        self,
        sql: str,
        parameters: dict[str, Any] | None = None,
    ) -> FlextResult[list[dict[str, Any]]]:
        """Execute SQL query and return results.

        Args:
            sql: SQL query to execute
            parameters: Query parameters

        Returns:
            FlextResult with query results

        """
        try:
            if not self._is_connected:
                connect_result = self.connect()
                if not connect_result.is_success:
                    return FlextResult.fail(connect_result.error or "Connection failed")

            logger.debug(f"Executing SQL query: {sql[:100]}")

            # Get Oracle configuration using DRY principle
            oracle_config = self._get_oracle_config()

            # Import at runtime to avoid dependency issues
            from flext_db_oracle.connection.resilient_connection import (
                FlextDbOracleResilientConnection,
            )

            # Execute actual SQL query with proper column metadata
            conn = FlextDbOracleResilientConnection(oracle_config)
            try:
                conn.connect()

                # Use the new public method to get metadata
                query_result = conn.execute_with_metadata(sql, parameters)

                # Extract columns and rows from the result
                columns = query_result["columns"]
                rows = query_result["rows"]

                # Convert to list of dictionaries with real column names
                results = [dict(zip(columns, row, strict=True)) for row in rows]
            finally:
                conn.disconnect()

            logger.debug(f"Query executed successfully, {len(results)} rows returned")
            return FlextResult.ok(results)

        except Exception as e:
            logger.exception(f"SQL query execution failed: {e}")
            return FlextResult.fail(f"Query execution failed: {e}")

    def execute_command(
        self,
        sql: str,
        parameters: dict[str, Any] | None = None,
    ) -> FlextResult[int]:
        """Execute SQL command and return affected rows.

        Args:
            sql: SQL command to execute
            parameters: Command parameters

        Returns:
            FlextResult with number of affected rows

        """
        try:
            if not self._is_connected:
                connect_result = self.connect()
                if not connect_result.is_success:
                    return FlextResult.fail(connect_result.error or "Connection failed")

            logger.debug(f"Executing SQL command: {sql[:100]}")

            # Get Oracle configuration using DRY principle
            oracle_config = self._get_oracle_config()

            # Import at runtime to avoid dependency issues
            from flext_db_oracle.connection.resilient_connection import (
                FlextDbOracleResilientConnection,
            )

            # Execute actual SQL command
            conn = FlextDbOracleResilientConnection(oracle_config)
            try:
                conn.connect()

                # Use the new public method to get metadata including affected rows
                command_result = conn.execute_with_metadata(sql, parameters)

                # Extract affected rows count
                affected_rows = command_result["affected_rows"]

                # Commit the transaction for commands
                conn.commit()
            finally:
                conn.disconnect()

            logger.debug(
                f"Command executed successfully, {affected_rows} rows affected",
            )
            return FlextResult.ok(affected_rows)

        except Exception as e:
            logger.exception(f"SQL command execution failed: {e}")
            return FlextResult.fail(f"Command execution failed: {e}")

    def is_connected(self) -> bool:
        """Check if connection is active.

        Returns:
            True if connected, False otherwise

        """
        return self._is_connected

    def get_connection_info(self) -> dict[str, Any]:
        """Get connection information.

        Returns:
            Dictionary with connection details

        """
        return {
            "host": self.config.host,
            "port": self.config.port,
            "service_name": self.config.service_name,
            "protocol": self.config.protocol,
            "username": self.config.username,
            "is_connected": self._is_connected,
            "connection_attempts": self._connection_attempts,
        }

    def validate_configuration(self) -> FlextResult[bool]:
        """Validate Oracle connection configuration.

        Returns:
            FlextResult indicating validation success

        """
        try:
            self.config.validate_domain_rules()
            logger.debug("Oracle connection configuration validated successfully")
            return FlextResult.ok(True)

        except ValueError as e:
            logger.exception(f"Oracle connection configuration validation failed: {e}")
            msg = f"Configuration validation failed: {e}"
            raise GruponosMeltanoOracleError(
                msg,
                context={"config": str(self.config)},
            ) from e


# Factory function
def create_gruponos_meltano_oracle_connection_manager(
    config: GruponosMeltanoOracleConnectionConfig | None = None,
) -> GruponosMeltanoOracleConnectionManager:
    """Create GrupoNOS Meltano Oracle connection manager instance.

    Args:
        config: Optional Oracle connection configuration

    Returns:
        Configured GruponosMeltanoOracleConnectionManager instance

    """
    if config is None:
        import os

        from gruponos_meltano_native.config import GruponosMeltanoOracleConnectionConfig

        config = GruponosMeltanoOracleConnectionConfig(
            host=os.getenv("ORACLE_HOST", "localhost"),
            port=int(os.getenv("ORACLE_PORT", "1522")),
            service_name=os.getenv("ORACLE_SERVICE_NAME", "ORCL"),
            username=os.getenv("ORACLE_USERNAME", "system"),
            password=os.getenv("ORACLE_PASSWORD", "oracle"),
        )

    return GruponosMeltanoOracleConnectionManager(config)


# Public API exports
__all__ = [
    # FLEXT Standard Classes
    "GruponosMeltanoOracleConnectionManager",
    # Factory Functions
    "create_gruponos_meltano_oracle_connection_manager",
]
