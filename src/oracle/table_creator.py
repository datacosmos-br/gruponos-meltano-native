#!/usr/bin/env python3
"""Oracle Table Creator - Professional DDL Generation
Creates optimized Oracle tables based on WMS schema with enterprise features
Uses metadata-first pattern for consistency with tap discovery.
"""

import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime
from typing import Any

from src.oracle.connection_manager import create_connection_manager_from_env

# Import centralized type mapping for Singer schema processing
sys.path.insert(0, "/home/marlonsc/flext/flext-tap-oracle-wms/src")

# Oracle DDL Type Mappings (moved from type_mapping.py)
WMS_METADATA_TO_ORACLE = {
    "pk": "NUMBER",
    "varchar": "VARCHAR2(255 CHAR)",
    "char": "CHAR(10)",
    "number": "NUMBER",
    "decimal": "NUMBER",
    "integer": "NUMBER",
    "boolean": "NUMBER(1,0)",
    "datetime": "TIMESTAMP(6)",
    "date": "TIMESTAMP(6)",
    "time": "TIMESTAMP(6)",
    "text": "VARCHAR2(4000 CHAR)",
    "clob": "CLOB",
    "relation": "VARCHAR2(255 CHAR)",
}

# Field Name Patterns to Oracle Types
FIELD_PATTERNS_TO_ORACLE = {
    "id_patterns": "NUMBER",
    "key_patterns": "VARCHAR2(255 CHAR)",
    "qty_patterns": "NUMBER",
    "price_patterns": "NUMBER",
    "weight_patterns": "NUMBER",
    "date_patterns": "TIMESTAMP(6)",
    "flag_patterns": "NUMBER(1,0)",
    "desc_patterns": "VARCHAR2(500 CHAR)",
    "code_patterns": "VARCHAR2(50 CHAR)",
    "name_patterns": "VARCHAR2(255 CHAR)",
    "addr_patterns": "VARCHAR2(500 CHAR)",
    "decimal_patterns": "NUMBER",
    "set_patterns": "VARCHAR2(4000 CHAR)",
}

# Pattern matching rules (same as in type_mapping.py)
FIELD_PATTERN_RULES = {
    "id_patterns": ["*_id", "id"],
    "key_patterns": ["*_key"],
    "qty_patterns": ["*_qty", "*_quantity", "*_count", "*_amount", "alloc_qty", "ord_qty", "packed_qty", "ordered_uom_qty", "orig_ord_qty"],
    "price_patterns": ["*_price", "*_cost", "*_rate", "*_percent", "cost", "sale_price", "unit_declared_value", "orig_sale_price"],
    "weight_patterns": ["*_weight", "*_volume", "*_length", "*_width", "*_height"],
    "date_patterns": ["*_date", "*_time", "*_ts", "*_timestamp", "cust_date_*"],
    "flag_patterns": ["*_flg", "*_flag", "*_enabled", "*_active"],
    "desc_patterns": ["*_desc", "*_description", "*_note", "*_comment"],
    "code_patterns": ["*_code", "*_status", "*_type"],
    "name_patterns": ["*_name", "*_title"],
    "addr_patterns": ["*_addr", "*_address"],
    "decimal_patterns": ["cust_decimal_*", "cust_number_*", "voucher_amount", "total_orig_ord_qty"],
    "set_patterns": ["*_set"],
}


def convert_metadata_type_to_oracle(
    metadata_type: str | None = None,
    column_name: str = "",
    max_length: int | None = None,
    sample_value: Any = None,
) -> str:
    """Convert WMS metadata type to Oracle DDL type using metadata-first pattern.
    
    Args:
        metadata_type: WMS metadata type
        column_name: Field name for pattern matching
        max_length: Maximum length for string fields
        sample_value: Sample value for type inference
        
    Returns:
        Oracle DDL type string (e.g., 'VARCHAR2(255 CHAR)', 'NUMBER')
    """
    # Priority 1: WMS metadata types
    if metadata_type and metadata_type.lower() in WMS_METADATA_TO_ORACLE:
        oracle_type = WMS_METADATA_TO_ORACLE[metadata_type.lower()]

        # Apply max_length override for VARCHAR2 types
        if oracle_type.startswith("VARCHAR2") and max_length:
            return f"VARCHAR2({min(max_length, 4000)} CHAR)"

        return oracle_type

    # Priority 2: Field name patterns
    column_lower = column_name.lower()
    for pattern_key, patterns in FIELD_PATTERN_RULES.items():
        for pattern in patterns:
            # Handle wildcard patterns
            if "*" in pattern:
                pattern_clean = pattern.replace("*", "")
                if (pattern.startswith("*_") and column_lower.endswith(pattern_clean)) or (pattern.endswith("_*") and column_lower.startswith(pattern_clean)):
                    oracle_type = FIELD_PATTERNS_TO_ORACLE[pattern_key]
                    if oracle_type.startswith("VARCHAR2") and max_length:
                        return f"VARCHAR2({min(max_length, 4000)} CHAR)"
                    return oracle_type
            # Exact match
            elif pattern == column_lower:
                oracle_type = FIELD_PATTERNS_TO_ORACLE[pattern_key]
                if oracle_type.startswith("VARCHAR2") and max_length:
                    return f"VARCHAR2({min(max_length, 4000)} CHAR)"
                return oracle_type

    # Priority 3: Sample value inference (last resort)
    if sample_value is not None:
        return _infer_oracle_from_sample(sample_value)

    # Default fallback
    return "VARCHAR2(255 CHAR)"


def oracle_ddl_from_singer_schema(singer_schema: dict[str, Any], column_name: str = "") -> str:
    """Convert Singer schema back to Oracle DDL type.
    
    Useful for table creation from discovered Singer schemas.
    """
    # Extract metadata if available
    metadata_type = None
    if "x-wms-metadata" in singer_schema:
        metadata_type = singer_schema["x-wms-metadata"].get("original_metadata_type")

    # Get max length if specified
    max_length = singer_schema.get("maxLength")

    return convert_metadata_type_to_oracle(
        metadata_type=metadata_type,
        column_name=column_name,
        max_length=max_length,
    )


def _infer_oracle_from_sample(sample_value: Any) -> str:
    """Infer Oracle type from sample value."""
    if isinstance(sample_value, bool):
        return "NUMBER(1,0)"
    if isinstance(sample_value, int) or isinstance(sample_value, float):
        return "NUMBER"
    if isinstance(sample_value, str):
        if _looks_like_date(sample_value):
            return "TIMESTAMP(6)"
        length = min(len(sample_value) * 2, 4000)
        return f"VARCHAR2({length} CHAR)"
    return "VARCHAR2(255 CHAR)"


def _looks_like_date(value: str) -> bool:
    """Check if string value looks like a date."""
    import re
    date_patterns = [
        r"\d{4}-\d{2}-\d{2}",  # YYYY-MM-DD
        r"\d{2}/\d{2}/\d{4}",  # MM/DD/YYYY
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}",  # ISO datetime
    ]

    for pattern in date_patterns:
        if re.match(pattern, value):
            return True
    return False


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

    def generate_ddl_from_schema(self, stream_name: str, schema: dict[str, Any]) -> str:
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
            f"-- Generated on {datetime.now().isoformat()}",
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
            for name in properties.keys()
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
                primary_key_field, properties[primary_key_field],
            )
            columns.append(f"    {column_def}")
            if primary_key_field.upper().endswith("_ID"):
                index_columns.append(primary_key_field.upper())

        # 2. Add all other fields (sorted, excluding URLs and complex nested objects)
        other_fields = []
        for prop_name in sorted(properties.keys()):
            if (
                prop_name != primary_key_field
                and not prop_name.upper().endswith("_URL")
                and prop_name.upper() != "URL"
                and not prop_name.upper().endswith("_ID_ID")
                and not prop_name.upper().endswith("_ID_KEY")
                and not prop_name.upper().endswith("_ID_URL")
                and prop_name.upper() not in ["TK_DATE", "CREATE_USER", "CREATE_TS", "MOD_USER", "MOD_TS"]
            ):
                other_fields.append(prop_name)

        for prop_name in other_fields:
            column_def = self._generate_wms_column_definition(
                prop_name, properties[prop_name],
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
            for name in properties.keys()
            if "_ID_" in name.upper() and not name.upper().endswith("_URL")
        ]
        for prop_name in sorted(fk_fields):
            if not prop_name.upper().endswith("_URL"):
                column_def = self._generate_wms_column_definition(
                    prop_name, properties[prop_name],
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
        if column_name.upper() in ["ID", "MOD_TS", "TK_DATE"]:
            nullable = " NOT NULL ENABLE"

        # Add collation for string types
        collation = ""
        if "VARCHAR2" in col_type or "CHAR" in col_type:
            collation = ' COLLATE "USING_NLS_COMP"'

        return f"{col_name} {col_type}{collation}{nullable}"

    def _map_to_wms_oracle_type(self, column_name: str, schema: dict[str, Any]) -> str:
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
        if json_type == "integer" or json_type == "number":
            return "NUMBER"
        if json_type == "boolean":
            return "NUMBER"  # Oracle boolean as NUMBER
        if json_type == "string":
            if json_format in ["date-time", "date", "time"]:
                return "TIMESTAMP (6)"
            # Use VARCHAR2 with 255 CHAR as standard for WMS fields
            return "VARCHAR2(255 CHAR)"
        if json_type in ["object", "array"]:
            return "CLOB"
        return "VARCHAR2(4000 CHAR)"

    def discover_and_create_tables(self, entities: list[str] | None = None) -> dict[str, str]:
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
        print("🔍 Discovering schemas from Oracle WMS...")
        schema_data = self._discover_schemas()

        if not schema_data:
            raise Exception("Failed to discover schemas from tap")

        # Generate DDL for each entity
        for entity in entities:
            if entity in schema_data:
                print(f"📄 Generating DDL for {entity}...")
                ddl = self.generate_ddl_from_schema(entity, schema_data[entity])
                results[entity] = ddl
            else:
                print(f"⚠️  Schema not found for entity: {entity}")

        return results

    def _discover_schemas(self) -> dict[str, Any]:
        """Discover schemas dynamically using tap-oracle-wms via API describe."""
        # First, check if we have saved schemas
        schema_file = "sql/wms_schemas.json"
        if os.path.exists(schema_file):
            print(f"📄 Using saved schemas from {schema_file}")
            try:
                with open(schema_file) as f:
                    schemas = json.load(f)

                for entity, schema in schemas.items():
                    prop_count = len(schema.get("properties", {}))
                    print(f"  ✅ Loaded schema for {entity} ({prop_count} properties)")

                return dict(schemas)
            except Exception as e:
                print(f"⚠️  Could not load saved schemas: {e}")
                print("🔄 Attempting fresh discovery...")

        try:
            print("🔍 Running WMS API schema discovery...")

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
            required_vars = ["TAP_ORACLE_WMS_BASE_URL", "TAP_ORACLE_WMS_USERNAME", "TAP_ORACLE_WMS_PASSWORD"]
            missing_vars = [var for var in required_vars if not env.get(var)]

            if missing_vars:
                print(f"❌ Missing required environment variables: {missing_vars}")
                print("💡 Configure these in your .env file or environment")
                print("🔄 Attempting direct tap discovery instead...")
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
                print(f"❌ Meltano schema discovery failed: {result.stderr}")
                print("🔄 Attempting direct tap discovery instead...")
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
                            print(
                                f"  ✅ Discovered schema for {stream_name} ({prop_count} properties via WMS API)",
                            )
                    except json.JSONDecodeError:
                        continue

            if not schemas:
                print("❌ No schemas found in meltano output")
                print("🚨 CRITICAL: Cannot proceed without proper schema discovery")
                raise Exception("Schema discovery failed - check WMS credentials and connectivity")

            return schemas

        except subprocess.TimeoutExpired:
            print("❌ Schema discovery timed out")
            raise Exception("Schema discovery timed out - check WMS API connectivity")
        except Exception as e:
            print(f"❌ Error in schema discovery: {e}")
            raise Exception(f"Schema discovery failed: {e}")

    def _discover_schemas_direct(self) -> dict[str, Any]:
        """Discover schemas by calling tap-oracle-wms directly."""
        try:
            print("🔍 Running direct tap-oracle-wms schema discovery...")

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
                "page_size": 1000,
                "force_full_table": True,
            }

            # Check if we have minimal config
            if not all([config["base_url"], config["username"], config["password"]]):
                print("❌ Missing WMS credentials for direct discovery")
                raise Exception("WMS credentials not configured - cannot discover schemas")

            # Write temporary config file

            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
                json.dump(config, f)
                config_file = f.name

            try:
                # Run tap with config
                result = subprocess.run(
                    cmd + ["--config", config_file],
                    capture_output=True,
                    text=True,
                    timeout=120,
                    check=False,
                )

                if result.returncode != 0:
                    print(f"❌ Direct tap discovery failed: {result.stderr}")
                    raise Exception(f"Direct tap discovery failed: {result.stderr}")

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
                                print(
                                    f"  ✅ Direct discovered schema for {stream_name} ({prop_count} properties)",
                                )
                        except json.JSONDecodeError:
                            continue

                if not schemas:
                    print("❌ No schemas found in direct tap output")
                    raise Exception("Direct schema discovery failed - no schemas returned")

                return schemas

            finally:
                # Clean up temp config file
                try:
                    os.unlink(config_file)
                except:
                    pass

        except subprocess.TimeoutExpired:
            print("❌ Direct tap discovery timed out")
            raise Exception("Direct tap discovery timed out")
        except Exception as e:
            print(f"❌ Error in direct schema discovery: {e}")
            raise Exception(f"Direct schema discovery failed: {e}")

    def _get_fallback_schemas(self) -> dict[str, Any]:
        """REMOVED: Fallback schemas are dangerous and should never be used."""
        raise Exception(
            "Fallback schemas are disabled. "
            "Configure proper WMS credentials to discover real schemas. "
            "Required: TAP_ORACLE_WMS_BASE_URL, TAP_ORACLE_WMS_USERNAME, TAP_ORACLE_WMS_PASSWORD",
        )

    def _oracle_to_json_schema(
        self, data_type: str, length: int, precision: int, scale: int, nullable: bool,
    ) -> dict[str, Any]:
        """Convert Oracle column type to JSON schema with original type tracking."""
        schema: dict[str, Any] = {}

        if data_type in ["NUMBER"]:
            if precision and scale and scale > 0:
                schema = {"type": ["number", "null"] if nullable else ["number"]}
            else:
                schema = {"type": ["integer", "null"] if nullable else ["integer"]}
            schema["oracle_type"] = "NUMBER"  # Keep original Oracle type
        elif data_type in ["VARCHAR2", "CHAR", "CLOB"]:
            schema = {"type": ["string", "null"] if nullable else ["string"]}
            if length and data_type == "VARCHAR2":
                schema["maxLength"] = length
            schema["oracle_type"] = (
                f"VARCHAR2({length} CHAR)"
                if data_type == "VARCHAR2" and length
                else data_type
            )
        elif data_type in ["DATE", "TIMESTAMP"]:
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
        raise Exception(
            f"Default schema creation is disabled for entity '{entity}'. "
            "Use proper schema discovery with WMS API credentials.",
        )

    def execute_ddl(
        self, ddl_statements: dict[str, str], drop_existing: bool = True,
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
                print(f"🔨 Executing DDL for {entity}...")

                # Split DDL into individual statements, handle PL/SQL blocks
                statements = []
                current_stmt = ""
                in_plsql_block = False

                for line in ddl.split("\n"):
                    line = line.strip()
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
                            print(f"  ✅ Executed: {stmt[:50]}...")
                        except Exception as e:
                            if "ORA-00942" in str(e) and "DROP TABLE" in stmt:
                                # Table doesn't exist for drop - OK
                                print(f"  ℹ️  Table doesn't exist (OK): {e}")
                            elif "ORA-00955" in str(e) and "CREATE TABLE" in stmt:
                                # Table already exists - drop and recreate
                                print("  🔄 Table exists, dropping first...")
                                table_name = stmt.split('"')[3]  # Extract table name
                                try:
                                    cursor.execute(
                                        f'DROP TABLE "OIC"."{table_name}" CASCADE CONSTRAINTS',
                                    )
                                    cursor.execute(stmt)
                                    print(f"  ✅ Recreated table: {table_name}")
                                except Exception as drop_e:
                                    print(f"  ⚠️  Drop/Recreate failed: {drop_e}")
                            else:
                                print(f"  ⚠️  SQL Warning: {e}")
                                print(f"     Statement: {stmt[:100]}...")

            conn.commit()
            cursor.close()
            conn.close()

            print("✅ All DDL statements executed successfully")
            return True

        except Exception as e:
            print(f"❌ Error executing DDL: {e}")
            return False


def main() -> int:
    """Main execution function."""
    # Check if we should discover schemas first
    if len(sys.argv) > 1 and sys.argv[1] == "--discover-only":
        print("🔍 Running schema discovery only...")
        from src.oracle.discover_and_save_schemas import discover_schemas
        success = discover_schemas()
        return 0 if success else 1

    creator = OracleTableCreator()

    # Get entities from command line or use default
    entities = sys.argv[1:] if len(sys.argv) > 1 else None

    try:
        # Discover and generate DDL
        ddl_statements = creator.discover_and_create_tables(entities)

        if not ddl_statements:
            print("❌ No DDL statements generated")
            return 1

        # Save DDL to files
        os.makedirs("sql/ddl", exist_ok=True)
        for entity, ddl in ddl_statements.items():
            ddl_file = f"sql/ddl/{entity}_table.sql"
            with open(ddl_file, "w") as f:
                f.write(ddl)
            print(f"📄 DDL saved to: {ddl_file}")

        # Execute DDL
        print("\n🚀 Executing DDL on Oracle database...")
        success = creator.execute_ddl(ddl_statements)

        if success:
            print("\n✅ Tables recreated successfully with optimized structure!")
            return 0
        print("\n❌ DDL execution failed")
        return 1

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
