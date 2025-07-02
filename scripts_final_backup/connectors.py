"""Oracle connector for SQLAlchemy integration."""

import sqlalchemy as sa
from singer_sdk.connectors import SQLConnector
from sqlalchemy.dialects import oracle


class OracleConnector(SQLConnector):
    """Oracle database connector with TCPS support."""

    allow_column_add: bool = True
    allow_column_rename: bool = True
    allow_column_alter: bool = True
    allow_merge_upsert: bool = True
    allow_temp_tables: bool = True

    def get_sqlalchemy_url(self, config: dict) -> str:
        """Construct Oracle connection URL with TCPS support for Autonomous Database."""
        protocol = config.get("protocol", "tcp").lower()
        host = config["host"]
        port = int(config.get("port", 1521))
        username = config["username"]
        password = config["password"]

        # Handle service name vs SID
        if config.get("service_name"):
            database = config["service_name"]
            if protocol == "tcps":
                # For Oracle Autonomous Database with TCPS
                # Add connection parameters for autonomous database stability
                # For Oracle Autonomous Database with TCPS - simplified parameters
                # Note: retry_count, retry_delay, ssl_server_dn_match are not valid SQLAlchemy URL params
                connection_params = [
                    "protocol=tcps"
                ]
                params_str = "&".join(connection_params)
                url = f"oracle+oracledb://{username}:{password}@{host}:{port}/{database}?{params_str}"
            else:
                # Standard connection
                url = (
                    f"oracle+oracledb://{username}:{password}@{host}:{port}/{database}"
                )
        else:
            database = config.get("database", "XE")
            if protocol == "tcps":
                # For Oracle Autonomous Database with TCPS - simplified parameters
                connection_params = [
                    "protocol=tcps"
                ]
                params_str = "&".join(connection_params)
                url = f"oracle+oracledb://{username}:{password}@{host}:{port}/{database}?{params_str}"
            else:
                url = (
                    f"oracle+oracledb://{username}:{password}@{host}:{port}/{database}"
                )

        return url

    @property
    def to_sql_type(self):
        """Return Oracle type mapping."""
        return {
            "string": oracle.VARCHAR2(4000),
            "date": oracle.DATE,
            "datetime": oracle.TIMESTAMP,
            "time": oracle.TIMESTAMP,
            "integer": oracle.NUMBER(38, 0),
            "number": oracle.NUMBER(38, 10),
            "boolean": oracle.VARCHAR2(10),
        }

    def create_schema(self, schema_name: str) -> None:
        """Create schema if not exists."""
        # Oracle uses users as schemas, so this is typically not needed

    def create_table(
        self,
        full_table_name: str,
        schema: dict,
        primary_keys: list[str] | None = None,
        partition_keys: list[str] | None = None,
        as_temp_table: bool = False,
    ) -> None:
        """Create table with Oracle optimizations."""
        super().create_table(
            full_table_name=full_table_name,
            schema=schema,
            primary_keys=primary_keys,
            partition_keys=partition_keys,
            as_temp_table=as_temp_table,
        )

        # Add Oracle-specific optimizations
        if not as_temp_table:
            try:
                with self._engine.begin() as conn:
                    # Analyze table for optimizer statistics
                    conn.execute(
                        sa.text(f"ANALYZE TABLE {full_table_name} COMPUTE STATISTICS")
                    )
            except Exception:
                # Ignore if analyze fails
                pass
