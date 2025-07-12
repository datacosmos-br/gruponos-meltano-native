"""Oracle Table Creator - Professional DDL Generation.

REFACTORED: Complete rewrite due to 267+ syntax errors.
Creates optimized Oracle tables based on WMS schema with enterprise features.
Uses metadata-first pattern for consistency with tap discovery.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any

# Use centralized logger from flext-observability
from flext_observability.logging import get_logger

logger = get_logger(__name__)


class OracleTableCreator:
    """Professional Oracle DDL generation for WMS schema synchronization."""

    def __init__(self, connection_config: dict[str, Any]) -> None:
        """Initialize table creator with Oracle connection configuration."""
        self.host = connection_config["host"]
        self.port = connection_config.get("port", 1521)
        self.service_name = connection_config["service_name"]
        self.username = connection_config["username"]
        self.password = connection_config["password"]
        self.schema = connection_config.get("schema", self.username.upper())

        self.type_mappings = self._get_oracle_type_mappings()

    def _get_oracle_type_mappings(self) -> dict[str, str]:
        """Get Singer to Oracle type mappings for DDL generation."""
        return {
            # Numeric types
            "integer": "NUMBER(10)",
            "number": "NUMBER",
            "float": "BINARY_DOUBLE",
            "decimal": "NUMBER(18,4)",

            # String types
            "string": "VARCHAR2(4000)",
            "text": "CLOB",

            # Date/time types
            "date-time": "TIMESTAMP WITH TIME ZONE",
            "date": "DATE",
            "time": "TIMESTAMP",

            # Boolean
            "boolean": "NUMBER(1) CHECK (VALUE IN (0,1))",

            # JSON/Object
            "object": "CLOB CHECK (VALUE IS JSON)",
            "array": "CLOB CHECK (VALUE IS JSON ARRAY)",
        }

    def create_table_from_schema(self, table_name: str, singer_schema: dict[str, Any]) -> str:
        """Create Oracle table DDL from Singer schema."""
        if "properties" not in singer_schema:
            raise ValueError(f"Invalid Singer schema for table {table_name}")

        columns = []
        primary_keys = []

        # Extract key properties if specified
        if "key_properties" in singer_schema:
            primary_keys = singer_schema["key_properties"]

        # Process each column
        for column_name, column_schema in singer_schema["properties"].items():
            column_ddl = self._create_column_ddl(column_name, column_schema, column_name in primary_keys)
            columns.append(column_ddl)

        # Build complete DDL
        ddl = self._build_create_table_ddl(table_name, columns, primary_keys)

        logger.info(f"Generated DDL for table {table_name}")
        return ddl

    def _create_column_ddl(self, column_name: str, column_schema: dict[str, Any], is_primary_key: bool) -> str:
        """Create column DDL from Singer schema property."""
        # Handle multiple types (e.g., ["string", "null"])
        column_types = column_schema.get("type", ["string"])
        if isinstance(column_types, str):
            column_types = [column_types]

        # Find the main type (excluding null)
        main_type = next((t for t in column_types if t != "null"), "string")

        # Map to Oracle type
        oracle_type = self.type_mappings.get(main_type, "VARCHAR2(4000)")

        # Handle special cases
        if main_type == "string" and "maxLength" in column_schema:
            max_length = min(column_schema["maxLength"], 4000)
            oracle_type = f"VARCHAR2({max_length})"
        elif main_type == "number" and "multipleOf" in column_schema:
            # Decimal precision handling
            precision = self._calculate_precision(column_schema["multipleOf"])
            oracle_type = f"NUMBER({precision},4)"

        # Build column definition
        column_ddl = f"{column_name.upper()} {oracle_type}"

        # Add constraints
        if "null" not in column_types or is_primary_key:
            column_ddl += " NOT NULL"

        # Add default value if specified
        if "default" in column_schema:
            default_value = self._format_default_value(column_schema["default"], main_type)
            column_ddl += f" DEFAULT {default_value}"

        return column_ddl

    def _calculate_precision(self, multiple_of: float) -> int:
        """Calculate Oracle NUMBER precision from multipleOf."""
        if multiple_of >= 1:
            return 18  # Large integers
        # Count decimal places
        decimal_str = str(multiple_of).split(".")[1] if "." in str(multiple_of) else ""
        return 18  # Conservative precision

    def _format_default_value(self, default_value: Any, data_type: str) -> str:
        """Format default value for Oracle DDL."""
        if default_value is None:
            return "NULL"
        if data_type in ("string", "text"):
            return f"'{default_value}'"
        if data_type == "boolean":
            return "1" if default_value else "0"
        if data_type in ("date-time", "date", "time"):
            if default_value == "CURRENT_TIMESTAMP":
                return "SYSTIMESTAMP"
            return f"TIMESTAMP '{default_value}'"
        return str(default_value)

    def _build_create_table_ddl(self, table_name: str, columns: list[str], primary_keys: list[str]) -> str:
        """Build complete CREATE TABLE DDL statement."""
        ddl_lines = [
            f"CREATE TABLE {self.schema}.{table_name.upper()} (",
            "  -- Auto-generated from Singer schema",
        ]

        # Add columns
        for i, column in enumerate(columns):
            comma = "," if i < len(columns) - 1 or primary_keys else ""
            ddl_lines.append(f"  {column}{comma}")

        # Add primary key constraint if specified
        if primary_keys:
            pk_columns = ", ".join(pk.upper() for pk in primary_keys)
            ddl_lines.append(f"  ,CONSTRAINT PK_{table_name.upper()} PRIMARY KEY ({pk_columns})")

        ddl_lines.extend([
            ")",
            "TABLESPACE USERS",
            "PCTFREE 10",
            "PCTUSED 40",
            "INITRANS 1",
            "MAXTRANS 255",
            "STORAGE (",
            "  INITIAL 64K",
            "  NEXT 1M",
            "  MINEXTENTS 1",
            "  MAXEXTENTS UNLIMITED",
            "  PCTINCREASE 0",
            ")",
            "LOGGING",
            "NOCOMPRESS",
            "NOCACHE",
            "NOPARALLEL",
            "MONITORING;",
            "",
            f"COMMENT ON TABLE {self.schema}.{table_name.upper()} IS 'WMS data synchronized via Singer tap';",
            "",
            "-- Add table statistics collection",
            "BEGIN",
            "  DBMS_STATS.GATHER_TABLE_STATS(",
            f"    ownname => '{self.schema}',",
            f"    tabname => '{table_name.upper()}',",
            "    estimate_percent => DBMS_STATS.AUTO_SAMPLE_SIZE,",
            "    method_opt => 'FOR ALL COLUMNS SIZE AUTO'",
            "  );",
            "END;",
            "/",
        ])

        return "\n".join(ddl_lines)

    def create_indexes_for_table(self, table_name: str, singer_schema: dict[str, Any]) -> list[str]:
        """Generate recommended indexes for WMS table based on schema."""
        indexes = []

        # Get properties that likely need indexing
        properties = singer_schema.get("properties", {})

        # Common WMS index patterns
        index_candidates = []

        for column_name, column_schema in properties.items():
            # Date columns (for range queries)
            if "date" in column_name.lower() or "time" in column_name.lower():
                index_candidates.append((column_name, "DATE_RANGE"))

            # ID columns (for joins)
            elif column_name.lower().endswith("_id") or column_name.lower() == "id":
                index_candidates.append((column_name, "JOIN"))

            # Status columns (for filtering)
            elif "status" in column_name.lower() or "state" in column_name.lower():
                index_candidates.append((column_name, "FILTER"))

            # Code columns (for lookups)
            elif "code" in column_name.lower() or "number" in column_name.lower():
                index_candidates.append((column_name, "LOOKUP"))

        # Generate index DDL
        for i, (column_name, index_type) in enumerate(index_candidates):
            index_name = f"IDX_{table_name.upper()}_{column_name.upper()}"

            if index_type == "DATE_RANGE":
                # B-tree index for date ranges
                index_ddl = (
                    f"CREATE INDEX {index_name} ON {self.schema}.{table_name.upper()} ({column_name.upper()}) "
                    f"TABLESPACE INDX PCTFREE 10 LOGGING ONLINE COMPUTE STATISTICS;"
                )
            elif index_type in ("JOIN", "LOOKUP"):
                # Unique or non-unique based on naming
                uniqueness = "UNIQUE " if column_name.lower().endswith("_id") else ""
                index_ddl = (
                    f"CREATE {uniqueness}INDEX {index_name} ON {self.schema}.{table_name.upper()} ({column_name.upper()}) "
                    f"TABLESPACE INDX PCTFREE 10 LOGGING ONLINE COMPUTE STATISTICS;"
                )
            else:
                # Standard index
                index_ddl = (
                    f"CREATE INDEX {index_name} ON {self.schema}.{table_name.upper()} ({column_name.upper()}) "
                    f"TABLESPACE INDX PCTFREE 10 LOGGING ONLINE;"
                )

            indexes.append(index_ddl)

        return indexes

    def execute_ddl(self, ddl_statements: list[str]) -> bool:
        """Execute DDL statements against Oracle database."""
        try:
            # Create SQL*Plus script
            script_content = "\n".join([
                "SET ECHO ON",
                "SET FEEDBACK ON",
                "SET TIMING ON",
                "WHENEVER SQLERROR EXIT FAILURE",
                "",
                *ddl_statements,
                "",
                "EXIT SUCCESS;",
            ])

            # Write to temporary file
            script_path = Path("/tmp/oracle_ddl.sql")
            script_path.write_text(script_content, encoding="utf-8")

            # Execute via SQL*Plus
            connection_string = f"{self.username}/{self.password}@{self.host}:{self.port}/{self.service_name}"

            result = subprocess.run(
                ["sqlplus", "-S", connection_string, "@/tmp/oracle_ddl.sql"],
                capture_output=True,
                text=True,
                timeout=300, check=False,  # 5 minute timeout
            )

            if result.returncode == 0:
                logger.info("DDL execution completed successfully")
                logger.debug(f"SQL*Plus output: {result.stdout}")
                return True
            logger.error(f"DDL execution failed: {result.stderr}")
            return False

        except subprocess.TimeoutExpired:
            logger.error("DDL execution timed out after 5 minutes")
            return False
        except Exception as e:
            logger.exception(f"Error executing DDL: {e}")
            return False
        finally:
            # Clean up temporary file
            if script_path.exists():
                script_path.unlink()

    def generate_table_from_singer_catalog(self, catalog_path: Path, table_name: str) -> str:
        """Generate Oracle table DDL from Singer catalog file."""
        try:
            catalog_data = json.loads(catalog_path.read_text(encoding="utf-8"))

            # Find stream in catalog
            stream = None
            for stream_data in catalog_data.get("streams", []):
                if stream_data.get("tap_stream_id") == table_name:
                    stream = stream_data
                    break

            if not stream:
                raise ValueError(f"Stream {table_name} not found in catalog")

            schema = stream.get("schema", {})
            return self.create_table_from_schema(table_name, schema)

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in catalog file: {e}") from e
        except Exception as e:
            logger.exception(f"Error processing Singer catalog: {e}")
            raise


def main() -> None:
    """Main function for CLI usage."""
    import argparse

    parser = argparse.ArgumentParser(description="Oracle Table Creator for WMS")
    parser.add_argument("--catalog", required=True, help="Singer catalog file path")
    parser.add_argument("--table", required=True, help="Table name to create")
    parser.add_argument("--host", required=True, help="Oracle host")
    parser.add_argument("--service", required=True, help="Oracle service name")
    parser.add_argument("--username", required=True, help="Oracle username")
    parser.add_argument("--password", help="Oracle password (or use env var)")
    parser.add_argument("--schema", help="Oracle schema (defaults to username)")
    parser.add_argument("--execute", action="store_true", help="Execute DDL immediately")
    parser.add_argument("--indexes", action="store_true", help="Generate indexes")

    args = parser.parse_args()

    # Get password from environment if not provided
    password = args.password or os.getenv("ORACLE_PASSWORD")
    if not password:
        raise ValueError("Password must be provided via --password or ORACLE_PASSWORD env var")

    # Create connection config
    connection_config = {
        "host": args.host,
        "service_name": args.service,
        "username": args.username,
        "password": password,
        "schema": args.schema or args.username.upper(),
    }

    # Initialize creator
    creator = OracleTableCreator(connection_config)

    # Generate DDL
    catalog_path = Path(args.catalog)
    table_ddl = creator.generate_table_from_singer_catalog(catalog_path, args.table)

    print("-- Table DDL:")
    print(table_ddl)

    # Generate indexes if requested
    if args.indexes:
        catalog_data = json.loads(catalog_path.read_text(encoding="utf-8"))
        stream = next(s for s in catalog_data["streams"] if s["tap_stream_id"] == args.table)
        indexes = creator.create_indexes_for_table(args.table, stream["schema"])

        print("\n-- Recommended Indexes:")
        for index_ddl in indexes:
            print(index_ddl)

    # Execute if requested
    if args.execute:
        ddl_statements = [table_ddl]
        if args.indexes:
            ddl_statements.extend(indexes)

        success = creator.execute_ddl(ddl_statements)
        if success:
            print(f"\n✅ Successfully created table {args.table}")
        else:
            print(f"\n❌ Failed to create table {args.table}")
            return 1

    return 0


if __name__ == "__main__":
    exit(main())
