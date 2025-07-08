"""Oracle Table Creator - Professional DDL Generation.

Creates optimized Oracle tables based on WMS schema with enterprise features
Uses metadata-first pattern for consistency with tap discovery.

REFATORADO: Agora usa type_mapping_rules.py como módulo compartilhado
"""

from __future__ import annotations

import contextlib
import json
import logging
import os
import subprocess
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from src.oracle.connection_manager import create_connection_manager_from_env
from src.oracle.discover_and_save_schemas import discover_schemas
from src.oracle.type_mapping_rules import convert_metadata_type_to_oracle

# Import centralized type mapping for Singer schema processing
sys.path.insert(0, "/home/marlonsc/flext/flext-tap-oracle-wms/src")

# Setup logger
log = logging.getLogger(__name__)


class OracleTableCreator:
    """Professional Oracle table creator with optimized DDL."""

    def __init__(self) -> None:
        """Initialize table creator."""
        self.connection_manager = create_connection_manager_from_env()
        self.schema_mapping = {
            "allocation": "ALLOCATION",
            "order_hdr": "ORDER_HDR",
            "order_dtl": "ORDER_DTL",
        }

    def generate_ddl_from_schema(
        self, stream_name: str, schema: dict[str, Any],
    ) -> str:
        """Generate optimized Oracle DDL following WMS enterprise rules.

        Args:
            stream_name: Name of the stream/entity
            schema: JSON schema from tap discovery

        Returns:
            Oracle DDL statement with proper column ordering and types
        """
        # Use optimized WMS table names for the new tables
        table_name = f"WMS_{stream_name.upper()}"
        properties = schema.get("properties", {})

        # Start DDL
        ddl_lines = [
            f"-- Optimized Oracle table for {stream_name}",
            f"-- Generated on {datetime.now(UTC).isoformat()}",
            f'DROP TABLE "OIC"."{table_name}" CASCADE CONSTRAINTS;',
            "",
            f'CREATE TABLE "OIC"."{table_name}"',
            "  (",
        ]

        # Organize columns according to WMS rules
        columns = []
        index_columns = []  # Track columns that need indexes
        primary_key_field = None

        # 1. First add ID field (primary key) - prioritize simple 'ID' field
        id_fields = [
            name
            for name in properties
            if name.upper() == "ID"
            or (name.upper().endswith("_ID") and not name.upper().endswith("_ID_ID"))
        ]
        if id_fields:
            # Prioritize simple 'ID' field over complex ones
            if "id" in [f.lower() for f in id_fields]:
                primary_key_field = next(f for f in id_fields if f.lower() == "id")
            else:
                primary_key_field = id_fields[0]  # Use first ID field as PK

            column_def = self._generate_wms_column_definition(
                primary_key_field,
                properties[primary_key_field],
            )
            columns.append(f"    {column_def}")
            if primary_key_field.upper().endswith("_ID"):
                index_columns.append(primary_key_field.upper())

        # 2. Add all other fields (sorted, excluding URLs and complex nested objects)
        other_fields = [
            prop_name
            for prop_name in sorted(properties.keys())
            if (
                prop_name != primary_key_field
                and not prop_name.upper().endswith("_URL")
                and prop_name.upper() != "URL"
                and not prop_name.upper().endswith("_ID_ID")
                and not prop_name.upper().endswith("_ID_KEY")
                and not prop_name.upper().endswith("_ID_URL")
                and prop_name.upper()
                not in {"TK_DATE", "CREATE_USER", "CREATE_TS", "MOD_USER", "MOD_TS"}
            )
        ]

        for prop_name in other_fields:
            column_def = self._generate_wms_column_definition(
                prop_name,
                properties[prop_name],
            )
            columns.append(f"    {column_def}")

            # Track fields that need indexes
            if (
                prop_name.upper().endswith("_ID")
                or prop_name.upper().endswith("_KEY")
                or prop_name.upper().endswith("_TS")
            ):
                index_columns.append(prop_name.upper())

        # 3. Add complex foreign key fields (_ID_KEY, _ID_URL, etc.)
        fk_fields = [
            name
            for name in properties
            if "_ID_" in name.upper() and not name.upper().endswith("_URL")
        ]
        for prop_name in sorted(fk_fields):
            if not prop_name.upper().endswith("_URL"):
                column_def = self._generate_wms_column_definition(
                    prop_name,
                    properties[prop_name],
                )
                columns.append(f"    {column_def}")

                # Track _KEY fields for indexes
                if prop_name.upper().endswith("_KEY"):
                    index_columns.append(prop_name.upper())

        # 4. Add mandatory audit fields
        audit_fields = [
            ("CREATE_USER", "VARCHAR2(255 CHAR)", ""),
            ("CREATE_TS", "TIMESTAMP (6)", ""),
            ("MOD_USER", "VARCHAR2(255 CHAR)", ""),
            ("MOD_TS", "TIMESTAMP (6)", " NOT NULL ENABLE"),
        ]

        for field_name, field_type, constraints in audit_fields:
            collation = ' COLLATE "USING_NLS_COMP"' if "VARCHAR2" in field_type else ""
            columns.append(f'    "{field_name}" {field_type}{collation}{constraints}')
            if field_name.endswith("_TS"):
                index_columns.append(field_name)

        # 5. Add TK_DATE field
        columns.append(
            '    "TK_DATE" TIMESTAMP (6) DEFAULT CURRENT_TIMESTAMP NOT NULL ENABLE',
        )
        index_columns.append("TK_DATE")

        # Join columns with commas
        ddl_lines.extend(
            [
                col + ("," if i < len(columns) - 1 else "")
                for i, col in enumerate(columns)
            ],
        )

        # Add primary key constraint (PK field + MOD_TS)
        if primary_key_field:
            pk_name = f"PK_{table_name}"
            pk_columns = f'"{primary_key_field.upper()}", "MOD_TS"'
            ddl_lines.append(
                f'     , CONSTRAINT "{pk_name}" PRIMARY KEY ({pk_columns})',
            )

        # Close table definition
        ddl_lines.append(" ) ;")
        ddl_lines.append("")

        # Add indexes for performance
        ddl_lines.append("-- Performance indexes")
        for col_name in sorted(set(index_columns)):
            index_name = f"IDX_{table_name}_{col_name}"
            ddl_lines.append(
                f'CREATE INDEX "{index_name}" ON "OIC"."{table_name}" ("{col_name}");',
            )

        ddl_lines.append("")

        return "\n".join(ddl_lines)

    def _generate_wms_column_definition(
        self, column_name: str, column_schema: dict[str, Any],
    ) -> str:
        """Generate Oracle column definition following WMS enterprise rules."""
        col_name = f'"{column_name.upper()}"'
        col_type = self._map_to_wms_oracle_type(column_name, column_schema)

        # Determine nullability - only ID, MOD_TS and TK_DATE are NOT NULL
        nullable = ""
        if column_name.upper() in {"ID", "MOD_TS", "TK_DATE"}:
            nullable = " NOT NULL ENABLE"

        # Add collation for string types
        collation = ""
        if "VARCHAR2" in col_type or "CHAR" in col_type:
            collation = ' COLLATE "USING_NLS_COMP"'

        return f"{col_name} {col_type}{collation}{nullable}"

    def _map_to_wms_oracle_type(
        self, column_name: str, schema: dict[str, Any],
    ) -> str:
        """Map Singer schema to Oracle type using metadata-first pattern."""
        # Extract metadata if available from Singer schema
        metadata_type = None
        if "x-wms-metadata" in schema:
            metadata_type = schema["x-wms-metadata"].get("original_metadata_type")

        # Get max length if specified
        max_length = schema.get("maxLength")

        # Use the centralized Oracle conversion function
        return convert_metadata_type_to_oracle(
            metadata_type=metadata_type,
            column_name=column_name,
            max_length=max_length,
            sample_value=None,  # Not available during table creation
        )

    def _generate_column_definition(
        self, column_name: str, column_schema: dict[str, Any],
    ) -> str:
        """Generate Oracle column definition from JSON schema."""
        col_name = f'"{column_name.upper()}"'
        col_type = self._map_to_oracle_type(column_schema)

        # Determine nullability - only ID, MOD_TS and TK_DATE are NOT NULL
        nullable = ""
        required_columns = ["id", "mod_ts", "tk_date"]
        if column_name.lower() in required_columns:
            nullable = " NOT NULL ENABLE"

        # Add collation for string types
        collation = ""
        if "VARCHAR2" in col_type:
            collation = ' COLLATE "USING_NLS_COMP"'

        return f"{col_name} {col_type}{collation}{nullable}"

    def _map_to_oracle_type(self, schema: dict[str, Any]) -> str:
        """Map JSON schema to optimized Oracle types following the WMS pattern."""
        # Check if we have the original Oracle type preserved
        if "oracle_type" in schema:
            return str(schema["oracle_type"])

        json_type = schema.get("type", "string")
        json_format = schema.get("format", "")

        # Handle nullable types
        if isinstance(json_type, list):
            json_type = next((t for t in json_type if t != "null"), "string")

        # Map to Oracle types following WMS pattern
        if json_type in {"integer", "number"}:
            return "NUMBER"
        if json_type == "boolean":
            return "NUMBER"  # Oracle boolean as NUMBER
        if json_type == "string":
            if json_format in {"date-time", "date", "time"}:
                return "TIMESTAMP (6)"
            # Use VARCHAR2 with 255 CHAR as standard for WMS fields
            return "VARCHAR2(255 CHAR)"
        if json_type in {"object", "array"}:
            return "CLOB"
        return "VARCHAR2(4000 CHAR)"

    def discover_and_create_tables(
        self, entities: list[str] | None = None,
    ) -> dict[str, str]:
        """Discover schemas and create optimized tables.

        Args:
            entities: List of entities to process (default: all configured)

        Returns:
            Dictionary of entity -> DDL statements
        """
        if entities is None:
            entities = ["allocation", "order_hdr", "order_dtl"]

        results = {}

        # First, discover schemas using tap
        log.info("🔍 Discovering schemas from Oracle WMS...")
        schema_data = self._discover_schemas()

        if not schema_data:
            msg = "Failed to discover schemas from tap"
            raise RuntimeError(msg)

        # Generate DDL for each entity
        for entity in entities:
            if entity in schema_data:
                log.info("📄 Generating DDL for %s...", entity)
                ddl = self.generate_ddl_from_schema(entity, schema_data[entity])
                results[entity] = ddl
            else:
                log.warning("⚠️  Schema not found for entity: %s", entity)

        return results

    def _discover_schemas(self) -> dict[str, Any]:
        """Discover schemas dynamically using tap-oracle-wms via API describe."""
        # First, check if we have saved schemas
        schema_file = "sql/wms_schemas.json"
        if Path(schema_file).exists():
            log.info("📄 Using saved schemas from %s", schema_file)
            try:
                with Path(schema_file).open(encoding="utf-8") as f:
                    schemas = json.load(f)

                for entity, schema in schemas.items():
                    prop_count = len(schema.get("properties", {}))
                    log.info(
                        "  ✅ Loaded schema for %s (%d properties)",
                        entity,
                        prop_count,
                    )

                return dict(schemas)
            except Exception as e:
                log.warning("⚠️  Could not load saved schemas: %s", e)
                log.info("🔄 Attempting fresh discovery...")

        try:
            log.info("🔍 Running WMS API schema discovery...")

            # Use meltano's built-in discover command instead of custom --test parameter
            cmd = [
                "/home/marlonsc/flext/.venv/bin/meltano",
                "invoke",
                "tap-oracle-wms-full",
                "--discover",
            ]

            # First, ensure environment variables are loaded
            env = os.environ.copy()

            # Check if essential WMS config is available
            required_vars = [
                "TAP_ORACLE_WMS_BASE_URL",
                "TAP_ORACLE_WMS_USERNAME",
                "TAP_ORACLE_WMS_PASSWORD",
            ]
            missing_vars = [var for var in required_vars if not env.get(var)]

            if missing_vars:
                log.error(
                    "❌ Missing required environment variables: %s", missing_vars,
                )
                log.info("💡 Configure these in your .env file or environment")
                log.info("🔄 Attempting direct tap discovery instead...")
                return self._discover_schemas_direct()

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd="/home/marlonsc/flext/gruponos-meltano-native",
                env=env,
                timeout=120,  # 2 minute timeout
                check=False,
            )

            if result.returncode != 0:
                log.error("❌ Meltano schema discovery failed: %s", result.stderr)
                log.info("🔄 Attempting direct tap discovery instead...")
                return self._discover_schemas_direct()

            # Parse SCHEMA messages from output
            schemas = {}
            lines = result.stdout.strip().split("\n")

            for line in lines:
                if line.startswith('{"type":"SCHEMA"'):
                    try:
                        schema_msg = json.loads(line)
                        stream_name = schema_msg.get("stream")
                        schema = schema_msg.get("schema")

                        if stream_name and schema:
                            schemas[stream_name] = schema
                            prop_count = len(schema.get("properties", {}))
                            log.info(
                                "  ✅ Discovered schema for %s (%d properties via API)",
                                stream_name,
                                prop_count,
                            )
                    except Exception as parse_err:
                        log.debug("Failed to parse schema line: %s", parse_err)
                        continue

            if not schemas:
                log.error("❌ No schemas found in meltano output")
                log.error(
                    "🚨 CRITICAL: Cannot proceed without proper schema discovery",
                )
                msg = "Schema discovery failed - check WMS credentials and connectivity"
                raise RuntimeError(msg)

        except subprocess.TimeoutExpired as timeout_err:
            log.exception("❌ Schema discovery timed out")
            msg = "Schema discovery timed out - check WMS API connectivity"
            raise RuntimeError(msg) from timeout_err
        except Exception as e:
            log.exception("❌ Error in schema discovery")
            msg = f"Schema discovery failed: {e}"
            raise RuntimeError(msg) from e
        else:
            return schemas

    def _discover_schemas_direct(self) -> dict[str, Any]:
        """Discover schemas by calling tap-oracle-wms directly."""
        try:
            log.info("🔍 Running direct tap-oracle-wms schema discovery...")

            # Call the tap directly with --discover
            cmd = [
                "/home/marlonsc/flext/.venv/bin/tap-oracle-wms",
                "--discover",
            ]

            # Build config from environment variables
            config = {
                "base_url": os.environ.get("TAP_ORACLE_WMS_BASE_URL", ""),
                "username": os.environ.get("TAP_ORACLE_WMS_USERNAME", ""),
                "password": os.environ.get("TAP_ORACLE_WMS_PASSWORD", ""),
                "entities": ["allocation", "order_hdr", "order_dtl"],
                "page_size": int(os.getenv("WMS_PAGE_SIZE", "100")),
                "force_full_table": True,
            }

            # Check if we have minimal config
            if not all([config["base_url"], config["username"], config["password"]]):
                log.error("❌ Missing WMS credentials for direct discovery")
                msg = "WMS credentials not configured - cannot discover schemas"
                raise RuntimeError(msg)

            # Write temporary config file
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".json", delete=False, encoding="utf-8",
            ) as f:
                json.dump(config, f)
                config_file = f.name

            try:
                # Run tap with config
                result = subprocess.run(
                    [*cmd, "--config", config_file],
                    capture_output=True,
                    text=True,
                    timeout=120,
                    check=False,
                )

                if result.returncode != 0:
                    log.error("❌ Direct tap discovery failed: %s", result.stderr)
                    msg = f"Direct tap discovery failed: {result.stderr}"
                    raise RuntimeError(msg)

                # Parse SCHEMA messages from output
                schemas = {}
                lines = result.stdout.strip().split("\n")

                for line in lines:
                    if line.startswith('{"type":"SCHEMA"'):
                        try:
                            schema_msg = json.loads(line)
                            stream_name = schema_msg.get("stream")
                            schema = schema_msg.get("schema")

                            if stream_name and schema:
                                schemas[stream_name] = schema
                                prop_count = len(schema.get("properties", {}))
                                log.info(
                                    "  ✅ Direct schema for %s (%d properties)",
                                    stream_name,
                                    prop_count,
                                )
                        except Exception as parse_err:
                            log.debug("Failed to parse schema line: %s", parse_err)
                            continue

                if not schemas:
                    log.error("❌ No schemas found in direct tap output")
                    msg = "Direct schema discovery failed - no schemas returned"
                    raise RuntimeError(msg)

                return schemas

            finally:
                # Clean up temp config file
                with contextlib.suppress(Exception):
                    Path(config_file).unlink()

        except subprocess.TimeoutExpired as timeout_err:
            log.exception("❌ Direct tap discovery timed out")
            msg = "Direct tap discovery timed out"
            raise RuntimeError(msg) from timeout_err
        except Exception as e:
            log.exception("❌ Error in direct schema discovery")
            msg = f"Direct schema discovery failed: {e}"
            raise RuntimeError(msg) from e

    def _get_fallback_schemas(self) -> dict[str, Any]:
        """REMOVED: Fallback schemas are dangerous and should never be used."""
        msg = (
            "Fallback schemas are disabled. "
            "Configure proper WMS credentials to discover real schemas. "
            "Required: TAP_ORACLE_WMS_BASE_URL, "
            "TAP_ORACLE_WMS_USERNAME, "
            "TAP_ORACLE_WMS_PASSWORD"
        )
        raise RuntimeError(msg)

    def _oracle_to_json_schema(
        self,
        data_type: str,
        length: int,
        precision: int,
        scale: int,
        *,
        nullable: bool,
    ) -> dict[str, Any]:
        """Convert Oracle column type to JSON schema with original type tracking."""
        schema: dict[str, Any] = {}

        if data_type == "NUMBER":
            if precision and scale and scale > 0:
                schema = {"type": ["number", "null"] if nullable else ["number"]}
            else:
                schema = {"type": ["integer", "null"] if nullable else ["integer"]}
            schema["oracle_type"] = "NUMBER"  # Keep original Oracle type
        elif data_type in {"VARCHAR2", "CHAR", "CLOB"}:
            schema = {"type": ["string", "null"] if nullable else ["string"]}
            if length and data_type == "VARCHAR2":
                schema["maxLength"] = length
            schema["oracle_type"] = (
                f"VARCHAR2({length} CHAR)"
                if data_type == "VARCHAR2" and length
                else data_type
            )
        elif data_type in {"DATE", "TIMESTAMP"}:
            schema = {
                "type": ["string", "null"] if nullable else ["string"],
                "format": "date-time",
                "oracle_type": "TIMESTAMP(6)",
            }
        else:
            schema = {"type": ["string", "null"] if nullable else ["string"]}
            schema["oracle_type"] = "VARCHAR2(255 CHAR)"

        return schema

    def _create_default_schema(self, entity: str) -> dict[str, Any]:
        """REMOVED: Default schemas are dangerous and should never be used."""
        msg = (
            f"Default schema creation is disabled for entity '{entity}'. "
            "Use proper schema discovery with WMS API credentials."
        )
        raise RuntimeError(msg)

    def execute_ddl(
        self,
        ddl_statements: dict[str, str],
        *,
        drop_existing: bool | None = None,
    ) -> bool:
        """Execute DDL statements on Oracle database.

        Args:
            ddl_statements: Dictionary of entity -> DDL
            drop_existing: Whether to drop existing tables

        Returns:
            True if successful
        """
        try:
            conn = self.connection_manager.connect()
            cursor = conn.cursor()

            for entity, ddl in ddl_statements.items():
                log.info("🔨 Executing DDL for %s...", entity)

                # Split DDL into individual statements, handle PL/SQL blocks
                statements = []
                current_stmt = ""
                in_plsql_block = False

                for raw_line in ddl.split("\n"):
                    line = raw_line.strip()
                    if not line or line.startswith("--"):
                        continue

                    current_stmt += line + "\n"

                    # Check for PL/SQL block
                    if line.upper().startswith("BEGIN"):
                        in_plsql_block = True
                    elif line == "/" and in_plsql_block:
                        statements.append(current_stmt.replace("/", "").strip())
                        current_stmt = ""
                        in_plsql_block = False
                    elif line.endswith(";") and not in_plsql_block:
                        statements.append(current_stmt.rstrip(";\n"))
                        current_stmt = ""

                if current_stmt.strip():
                    statements.append(current_stmt.strip())

                for stmt in statements:
                    if stmt.strip():
                        try:
                            cursor.execute(stmt)
                            log.info("  ✅ Executed: %s...", stmt[:50])
                        except Exception as e:
                            if "ORA-00942" in str(e) and "DROP TABLE" in stmt:
                                # Table doesn't exist for drop - OK
                                log.info("  i  Table doesn't exist (OK): %s", e)
                            elif "ORA-00955" in str(e) and "CREATE TABLE" in stmt:
                                # Table already exists - drop and recreate
                                log.info("  🔄 Table exists, dropping first...")
                                table_name = stmt.split('"')[3]  # Extract table name
                                try:
                                    drop_sql = (
                                        f'DROP TABLE "OIC"."{table_name}" '
                                        "CASCADE CONSTRAINTS"
                                    )
                                    cursor.execute(drop_sql)
                                    cursor.execute(stmt)
                                    log.info("  ✅ Recreated table: %s", table_name)
                                except Exception as drop_e:
                                    log.warning("  ⚠️  Drop/Recreate failed: %s", drop_e)
                            else:
                                log.warning("  ⚠️  SQL Warning: %s", e)
                                log.warning("     Statement: %s...", stmt[:100])

            conn.commit()
            cursor.close()
            conn.close()

            log.info("✅ All DDL statements executed successfully")

        except Exception:
            log.exception("❌ Error executing DDL")
            return False
        else:
            return True


def main() -> int:
    """Main execution function."""
    # Check if we should discover schemas first
    if len(sys.argv) > 1 and sys.argv[1] == "--discover-only":
        log.info("🔍 Running schema discovery only...")

        success = discover_schemas()
        return 0 if success else 1

    creator = OracleTableCreator()

    # Get entities from command line or use default
    entities = sys.argv[1:] if len(sys.argv) > 1 else None

    try:
        # Discover and generate DDL
        ddl_statements = creator.discover_and_create_tables(entities)

        if not ddl_statements:
            log.error("❌ No DDL statements generated")
            return 1

        # Save DDL to files
        Path("sql/ddl").mkdir(parents=True, exist_ok=True)
        for entity, ddl in ddl_statements.items():
            ddl_file = f"sql/ddl/{entity}_table.sql"
            with Path(ddl_file).open("w", encoding="utf-8") as f:
                f.write(ddl)
            log.info("📄 DDL saved to: %s", ddl_file)

        # Execute DDL
        log.info("\n🚀 Executing DDL on Oracle database...")
        success = creator.execute_ddl(ddl_statements)

        if success:
            log.info("\n✅ Tables recreated successfully with optimized structure!")
            return 0

        log.error("\n❌ DDL execution failed")

    except Exception:
        log.exception("❌ Error")
        return 1
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
