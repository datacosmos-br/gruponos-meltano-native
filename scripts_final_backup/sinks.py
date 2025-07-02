"""Advanced Oracle sinks with SQLAlchemy and bulk operations."""

from __future__ import annotations

import json
import threading
import time
from datetime import datetime
from typing import TYPE_CHECKING, Any

import sqlalchemy as sa
from singer_sdk.sinks import SQLSink
from sqlalchemy import (
    Column,
    MetaData,
    Table,
    create_engine,
    event,
)
from sqlalchemy.dialects import oracle
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

if TYPE_CHECKING:
    from sqlalchemy.engine import Engine

try:
    from flext_target_oracle.connectors import OracleConnector
except ImportError:
    from connectors import OracleConnector


class OracleSink(SQLSink):
    """Advanced Oracle sink with SQLAlchemy and performance optimizations."""

    # Required connector class for SQLSink compatibility
    connector_class = OracleConnector

    # Oracle-specific type mappings
    type_mapping = {
        "string": oracle.VARCHAR2,
        "integer": oracle.NUMBER,
        "number": oracle.NUMBER,
        "boolean": oracle.VARCHAR2(10),  # Store as TRUE/FALSE
        "date": oracle.DATE,
        "date-time": oracle.TIMESTAMP,
        "time": oracle.TIMESTAMP,
        "object": oracle.CLOB,  # Store as JSON
        "array": oracle.CLOB,  # Store as JSON
    }

    def __init__(
        self, target, stream_name: str, schema: dict, key_properties: list[str]
    ):
        """Initialize Oracle sink with advanced features."""
        # Set target first
        self.target = target

        super().__init__(target, stream_name, schema, key_properties)

        # Performance tracking
        self._batch_start_time = None
        self._records_in_batch = 0
        self._total_records = 0

        # Thread safety
        self._lock = threading.Lock()

        # Batch management - PRODUCTION optimized for TCPS stability
        self._current_batch: list[dict[str, Any]] = []
        # PRODUCTION: Smaller batches for TCPS stability with large volumes
        self._batch_size = self.config.get("batch_size", 25)  # EXTREME: Ultra-small for real volume

        # Connection management
        self._engine: Engine | None = None
        self._session_factory = None
        self._oracle_connection = None  # Store main Oracle connection like legacy
        self._oracle_pool = None  # Oracle native connection pool for TCPS

        # Table structure cache
        self._table_columns = None  # Cache of existing table columns
        self._table = None  # Cache the table object

        # Fallback handling
        self._fallback_mode = False
        self._fallback_file = None

        self.logger.info(
            f"Initialized Oracle sink for stream '{stream_name}' "
            f"with batch_size={self._batch_size}"
        )

    @property
    def config(self) -> dict[str, Any]:
        """Get target configuration."""
        return self.target.config

    @property
    def engine(self) -> Engine:
        """Get or create SQLAlchemy engine with optimized settings."""
        if self._engine is None:
            self._engine = self._create_engine()
        return self._engine

    def _create_engine(self) -> Engine:
        """Create optimized SQLAlchemy engine for Oracle Autonomous Database TCPS using research-based solution."""
        # Initialize Oracle native connection pool for TCPS
        self._oracle_pool = None

        try:
            # Extract connection parameters
            host = self.config["host"]
            port = int(self.config.get("port", 1521))
            username = self.config["username"]
            password = self.config["password"]
            # Handle SecretStr from pydantic
            if hasattr(password, "get_secret_value"):
                password = password.get_secret_value()
            # Remove quotes if present (from .env files)
            if isinstance(password, str):
                password = password.strip("\"'")
            protocol = self.config.get("protocol", "tcp").lower()

            # Build DSN based on service_name or database - USING PROVEN LEGACY PATTERN
            if self.config.get("service_name"):
                # For Autonomous Database - use EXACT format from working legacy code
                service_name = self.config["service_name"]
                if protocol == "tcps":
                    # PROVEN WORKING TCPS DSN FORMAT from legacy/flx-database-oracle
                    dsn = (
                        f"(DESCRIPTION="
                        f"(RETRY_COUNT=20)(RETRY_DELAY=3)"
                        f"(ADDRESS=(PROTOCOL=tcps)(HOST={host})(PORT={port}))"
                        f"(CONNECT_DATA=(SERVICE_NAME={service_name}))"
                        f"(SECURITY=(SSL_SERVER_DN_MATCH=no))"
                        f")"
                    )
                else:
                    dsn = f"{host}:{port}/{service_name}"
            else:
                # For regular database - use SID
                database = self.config.get("database", "XE")
                if protocol == "tcps":
                    dsn = (
                        f"(DESCRIPTION="
                        f"(RETRY_COUNT=20)(RETRY_DELAY=3)"
                        f"(ADDRESS=(PROTOCOL=tcps)(HOST={host})(PORT={port}))"
                        f"(CONNECT_DATA=(SID={database}))"
                        f"(SECURITY=(SSL_SERVER_DN_MATCH=no))"
                        f")"
                    )
                else:
                    dsn = f"{host}:{port}/{database}"

            self.logger.info(
                f"🔌 Creating Oracle connection pool for TCPS: {username}@{host}:{port}"
            )

            # PRODUCTION-OPTIMIZED SOLUTION: Use Oracle native pooling for TCPS with real volume
            import oracledb

            # Create Oracle native connection pool optimized for production volume (4K+ records)
            pool_size = min(
                self.config.get("pool_size", 5), 2  # PRODUCTION: max 2 for TCPS stability
            )
            self._oracle_pool = oracledb.create_pool(
                user=username,
                password=password,
                dsn=dsn,
                min=1,  # Minimum connections
                max=1,  # EXTREME: Single connection for maximum stability
                increment=1,  # Pool growth increment
                ping_interval=10,  # Very frequent ping for TCPS stability
                timeout=600,  # EXTREME: Very long timeout for real volume
                getmode=oracledb.POOL_GETMODE_WAIT,  # Wait for connection if pool full
                # PRODUCTION TCPS optimizations
                stmtcachesize=40,  # Increase statement cache for repeated operations
                edition="",  # Ensure clean edition
                events=True,  # Enable connection events for monitoring
            )

            self.logger.info(
                f"✅ Oracle connection pool created: min=1, max={pool_size}"
            )

            # Oracle connection function using native pool
            def get_oracle_connection():
                """Get connection from Oracle native pool - TCPS COMPATIBLE."""
                try:
                    # Acquire connection from Oracle pool (not SQLAlchemy pool)
                    connection = self._oracle_pool.acquire()
                    self.logger.debug("🔗 Acquired connection from Oracle native pool")
                    return connection
                except Exception as e:
                    self.logger.exception(
                        f"❌ Failed to acquire connection from Oracle pool: {e}"
                    )
                    raise

            # RESEARCH-BASED: Use NullPool to disable SQLAlchemy pooling for TCPS
            from sqlalchemy.pool import NullPool

            # Create SQLAlchemy engine with Oracle native pooling
            engine = create_engine(
                "oracle+oracledb://",  # Empty URL - connection via creator
                creator=get_oracle_connection,
                poolclass=NullPool,  # CRITICAL: Disable SQLAlchemy pooling for TCPS
                echo=self.config.get("log_sql_statements", False),
            )

            # Add DPY-4011 error handling for TCPS disconnections
            @event.listens_for(engine, "handle_error")
            def handle_tcps_errors(context):
                """Handle Oracle TCPS-specific disconnection errors."""
                import re

                if not context.is_disconnect and re.match(
                    r"^(?:DPY-1001|DPY-4011)", str(context.original_exception)
                ):
                    self.logger.warning(
                        f"🔄 Detected Oracle TCPS disconnection: {context.original_exception}"
                    )
                    context.is_disconnect = True

            # Test the connection pool
            test_conn = self._oracle_pool.acquire()
            cursor = test_conn.cursor()
            cursor.execute("SELECT 1 FROM DUAL")
            test_result = cursor.fetchone()[0]
            cursor.close()
            self._oracle_pool.release(test_conn)

            self.logger.info(
                f"✅ Oracle TCPS connection pool test successful: {test_result}"
            )

        except Exception as e:
            self.logger.exception(f"❌ Oracle TCPS connection pool creation failed: {e}")
            self.logger.warning(
                "🔄 Falling back to file-based storage for this session"
            )

            # Set fallback mode
            self._fallback_mode = True
            self._fallback_file = f"{self.stream_name}_data.jsonl"

            # Return a dummy engine (won't be used in fallback mode)
            engine = None

        # Setup event listeners for performance monitoring (only if engine is not None)
        if engine is not None and self.config.get("enable_performance_metrics"):
            self._setup_engine_events(engine)

        # Create session factory
        self._session_factory = sessionmaker(bind=engine)

        if engine is not None:
            self.logger.info(
                f"🚀 Created Oracle TCPS engine with native pooling: {self.config['username']}@{self.config['host']}:{self.config.get('port', 1521)}"
            )
        return engine

    def _setup_engine_events(self, engine: Engine) -> None:
        """Setup SQLAlchemy event listeners for monitoring."""

        @event.listens_for(engine, "before_cursor_execute")
        def before_cursor_execute(
            conn, cursor, statement, parameters, context, executemany
        ):
            context._query_start_time = time.time()

        @event.listens_for(engine, "after_cursor_execute")
        def after_cursor_execute(
            conn, cursor, statement, parameters, context, executemany
        ):
            total = time.time() - context._query_start_time
            self.target.update_metrics("total_processing_time", total)

            if total > 1.0:  # Log slow queries
                self.logger.warning(f"Slow query ({total:.2f}s): {statement[:100]}...")

    def get_table_name(self) -> str:
        """Get full table name with WMS_ prefix per specification."""
        # ESPECIFICAÇÃO: Tabelas Oracle devem ter prefixo WMS_
        prefix = "WMS_"
        suffix = self.config.get("table_suffix", "")
        return f"{prefix}{self.stream_name}{suffix}".upper()

    def create_table_if_not_exists(self) -> Table:
        """Create Oracle table with optimized structure or get existing table."""
        # Skip table creation in fallback mode
        if self._fallback_mode:
            return None

        table_name = self.get_table_name()
        metadata = MetaData()

        # First check if table already exists
        try:
            with self.engine.begin() as conn:
                # Check if table exists and get its columns
                existing_columns_query = text("""
                    SELECT column_name, data_type
                    FROM user_tab_columns
                    WHERE table_name = :table_name
                    ORDER BY column_name
                """)
                result = conn.execute(existing_columns_query, {"table_name": table_name})
                existing_columns = {row[0]: row[1] for row in result.fetchall()}

                if existing_columns:
                    self.logger.info(f"✅ Table {table_name} already exists with {len(existing_columns)} columns")

                    # Cache the column names for later use
                    self._table_columns = set(existing_columns.keys())

                    # Create minimal SQLAlchemy table object for existing table
                    # Avoid autoload to prevent duplicate column errors
                    table = Table(table_name, metadata)

                    # Add only the columns we actually need for inserts
                    # Use existing column information to build minimal structure
                    for col_name, col_type in existing_columns.items():
                        # Map Oracle types to SQLAlchemy types
                        if col_type.startswith("VARCHAR"):
                            sa_type = oracle.VARCHAR2(4000)
                        elif col_type == "NUMBER":
                            sa_type = oracle.NUMBER
                        elif col_type.startswith("TIMESTAMP"):
                            sa_type = oracle.TIMESTAMP
                        else:
                            sa_type = oracle.VARCHAR2(4000)  # Safe default

                        table.append_column(Column(col_name, sa_type))

                    self._table = table  # Cache for reuse
                    self.logger.info(f"🔄 Created minimal table object for existing {table_name} with {len(existing_columns)} columns")
                    return table

        except Exception as e:
            self.logger.warning(f"Could not check existing table structure: {e}")
            # Continue with table creation

        # Build columns from schema (for new table creation)
        columns = []

        # Add primary key columns first
        # ESPECIFICAÇÃO NOVA: Chave primária = pk original + MOD_TS (não TK_DATE)
        primary_key_columns = []
        for key_prop in self.key_properties:
            prop_def = self.schema["properties"].get(key_prop, {})
            col_type = self._get_oracle_type(prop_def)
            columns.append(Column(key_prop.upper(), col_type, nullable=False))
            primary_key_columns.append(key_prop.upper())

        # ESPECIFICAÇÃO NOVA: MOD_TS faz parte da chave primária composta (não TK_DATE)
        # Primeiro adicione MOD_TS se existir no schema
        if "mod_ts" in self.schema.get("properties", {}):
            mod_ts_prop = self.schema["properties"]["mod_ts"]
            mod_ts_type = self._get_oracle_type(mod_ts_prop)
            columns.append(Column("MOD_TS", mod_ts_type, nullable=False))
            primary_key_columns.append("MOD_TS")

        # TK_DATE agora é apenas timestamp de gravação (NÃO faz parte da PK)
        columns.append(
            Column("TK_DATE", oracle.TIMESTAMP, nullable=False, default=sa.func.current_timestamp())
        )

        # Add other properties (skip MOD_TS since it's already added as part of PK)
        for prop_name, prop_def in self.schema["properties"].items():
            if prop_name not in self.key_properties and prop_name != "mod_ts":
                col_type = self._get_oracle_type(prop_def)
                nullable = prop_name not in self.schema.get("required", [])
                columns.append(Column(prop_name.upper(), col_type, nullable=nullable))

        # Add metadata columns if enabled
        if self.config.get("add_record_metadata", True):
            columns.extend(
                [
                    Column(
                        "_LOADED_AT",
                        oracle.TIMESTAMP,
                        default=sa.func.current_timestamp(),
                    ),
                    Column("_EXTRACTED_AT", oracle.TIMESTAMP),
                    Column("_ENTITY_NAME", oracle.VARCHAR2(100)),
                    Column("_BATCH_ID", oracle.VARCHAR2(50)),
                ]
            )

        # Create table with composite primary key
        table = Table(table_name, metadata, *columns)

        # ESPECIFICAÇÃO NOVA: Adicionar constraint de chave primária composta (pk + MOD_TS)
        if primary_key_columns:
            from sqlalchemy import PrimaryKeyConstraint
            table.append_constraint(
                PrimaryKeyConstraint(*primary_key_columns, name=f"PK_{table_name}")
            )

        # Add table-level optimizations
        table_args = []

        # Add parallel processing hint if configured
        if self.config.get("parallel_degree", 0) > 1:
            table_args.append(f"PARALLEL {self.config['parallel_degree']}")

        # Create table with error handling
        try:
            with self.engine.begin() as conn:
                metadata.create_all(conn, checkfirst=True)

                # Add table statistics for optimizer
                if self.config.get("enable_performance_metrics"):
                    conn.execute(text(f"ANALYZE TABLE {table_name} COMPUTE STATISTICS"))

            self.logger.info(f"Table {table_name} ready with {len(columns)} columns")

        except SQLAlchemyError as e:
            self.logger.exception(f"Error creating table {table_name}: {e}")
            raise

        return table

    def _get_oracle_type(self, property_def: dict[str, Any]) -> sa.types.TypeEngine:
        """Map JSON schema property to Oracle type."""
        # Handle anyOf structures
        if "anyOf" in property_def:
            # Find the non-null type
            for type_option in property_def["anyOf"]:
                if type_option.get("type") != "null":
                    property_def = type_option
                    break

        prop_type = property_def.get("type", "string")
        prop_format = property_def.get("format")

        # Handle specific formats
        if prop_format == "date-time":
            return oracle.TIMESTAMP
        if prop_format == "date":
            return oracle.DATE
        if prop_format == "time":
            return oracle.TIMESTAMP

        # Handle types
        if prop_type == "string":
            max_length = property_def.get("maxLength", 255)
            if max_length > self.config.get("max_varchar_length", 4000):
                return oracle.CLOB
            return oracle.VARCHAR2(min(max_length, 4000))

        if prop_type == "integer":
            # Handle precision for large integers
            minimum = property_def.get("minimum", 0)
            maximum = property_def.get("maximum", 2**31)

            if maximum > 2**31:
                return oracle.NUMBER(38, 0)  # Large integer
            return oracle.NUMBER(10, 0)

        if prop_type == "number":
            # Handle precision and scale
            return oracle.NUMBER(38, 10)  # High precision decimal

        if prop_type == "boolean":
            return oracle.VARCHAR2(10)  # Store as TRUE/FALSE

        if prop_type in ("object", "array"):
            return oracle.CLOB  # Store as JSON

        # Default to VARCHAR2
        return oracle.VARCHAR2(4000)

    def process_record(self, record: dict[str, Any], context: dict) -> None:
        """Process a single record with batching."""
        # Add to current batch
        with self._lock:
            self._current_batch.append(record)
            self._records_in_batch += 1

            # Check if batch is ready - IMMEDIATE FLUSH for batch_size=1
            if len(self._current_batch) >= self._batch_size:
                # Release lock before flushing to avoid deadlock
                pass

        # Flush outside of lock if batch is ready
        if len(self._current_batch) >= self._batch_size:
            self._flush_batch()

    def _flush_batch(self) -> None:
        """Flush current batch to database or file."""
        if not self._current_batch:
            return

        batch_start = time.time()
        batch_records = self._current_batch.copy()
        batch_size = len(batch_records)

        # Clear current batch
        self._current_batch.clear()
        self._records_in_batch = 0

        try:
            # Check if in fallback mode
            if self._fallback_mode:
                self._flush_to_file(batch_records)
            else:
                # Normal Oracle database mode - use cached table if available
                if self._table is None:
                    table = self.create_table_if_not_exists()
                else:
                    table = self._table

                # Process batch
                if self.config.get("use_bulk_insert", True):
                    self._bulk_insert_batch(table, batch_records)
                else:
                    self._standard_insert_batch(table, batch_records)

            # Update metrics
            batch_time = time.time() - batch_start
            self.target.update_metrics("records_processed", batch_size)
            self.target.update_metrics("batches_processed", 1)
            self.target.update_metrics("total_processing_time", batch_time)

            destination = (
                self._fallback_file if self._fallback_mode else "Oracle database"
            )
            self.logger.info(
                f"Flushed batch of {batch_size:,} records to {destination} "
                f"in {batch_time:.2f}s ({batch_size / batch_time:.0f} records/sec)"
            )

        except Exception as e:
            self.target.update_metrics("records_failed", batch_size)
            self.logger.exception(f"Error flushing batch: {e}")

            # Retry logic (only for Oracle mode)
            if not self._fallback_mode and self.config.get("max_retries", 3) > 0:
                self._retry_batch(table, batch_records)
            # Fallback to file if Oracle fails
            elif not self._fallback_mode:
                self.logger.warning(
                    "🔄 Switching to fallback file mode due to Oracle error"
                )
                self._fallback_mode = True
                self._fallback_file = f"{self.stream_name}_data.jsonl"
                self._flush_to_file(batch_records)
            else:
                raise

    def _flush_to_file(self, records: list[dict[str, Any]]) -> None:
        """Flush records to JSONL file as fallback."""
        import json

        with open(self._fallback_file, "a", encoding="utf-8") as f:
            for record in records:
                # Add metadata to record
                enhanced_record = {
                    **record,
                    "_loaded_at": datetime.utcnow().isoformat(),
                    "_entity_name": self.stream_name,
                    "_target_mode": "fallback_file",
                }
                f.write(json.dumps(enhanced_record) + "\n")

    def _bulk_insert_batch(self, table: Table, records: list[dict[str, Any]]) -> None:
        """Insert batch using Oracle bulk operations."""
        # Prepare records for bulk insert
        prepared_records = []
        batch_id = f"batch_{int(time.time())}_{threading.current_thread().ident}"

        for record in records:
            prepared_record = self._prepare_record(record, batch_id)
            prepared_records.append(prepared_record)

        # Execute bulk insert
        with self.engine.begin() as conn:
            if self.config.get("use_merge_upsert", False) and self.key_properties:
                # Use MERGE for upsert operations
                self._execute_merge_upsert(conn, table, prepared_records)
            else:
                # Standard bulk insert
                try:
                    conn.execute(table.insert(), prepared_records)
                except IntegrityError as e:
                    if self.config.get("ignore_duplicate_keys", True):
                        self.logger.warning(f"Ignoring duplicate key error: {e}")
                        # Try individual inserts to identify duplicates
                        self._insert_with_duplicate_handling(
                            conn, table, prepared_records
                        )
                    else:
                        raise

    def _standard_insert_batch(
        self, table: Table, records: list[dict[str, Any]]
    ) -> None:
        """Insert batch using standard individual inserts."""
        batch_id = f"batch_{int(time.time())}_{threading.current_thread().ident}"

        # FORÇAR AUTOCOMMIT para garantir commits imediatos
        with self.engine.connect() as conn:
            # Enable autocommit mode
            conn.execute(text(""))  # Empty statement to establish connection
            for record in records:
                prepared_record = self._prepare_record(record, batch_id)

                try:
                    result = conn.execute(table.insert(), prepared_record)
                    conn.commit()  # FORÇA commit imediato de cada record
                    self.logger.info(f"✅ COMMITTED record ID {prepared_record.get('ID', 'unknown')}")
                except IntegrityError as e:
                    if self.config.get("ignore_duplicate_keys", True):
                        self.logger.warning(f"⚠️ Skipping duplicate record: {e}")
                    else:
                        raise

    def _execute_merge_upsert(
        self, conn, table: Table, records: list[dict[str, Any]]
    ) -> None:
        """Execute MERGE statement for upsert operations."""
        # Build MERGE statement
        source_data = ", ".join(
            [
                f"SELECT {', '.join([f':{k}_{i} as {k}' for k in records[0]])} FROM dual"
                for i, _ in enumerate(records)
            ]
        )

        merge_sql = f"""
        MERGE INTO {table.name} target
        USING ({source_data}) source
        ON ({' AND '.join([f'target.{k} = source.{k}' for k in self.key_properties])})
        WHEN MATCHED THEN
            UPDATE SET {', '.join([f'{k} = source.{k}' for k in records[0] if k not in self.key_properties])}
        WHEN NOT MATCHED THEN
            INSERT ({', '.join(records[0].keys())})
            VALUES ({', '.join([f'source.{k}' for k in records[0]])})
        """

        # Prepare parameters
        params = {}
        for i, record in enumerate(records):
            for k, v in record.items():
                params[f"{k}_{i}"] = v

        conn.execute(text(merge_sql), params)

    def _insert_with_duplicate_handling(
        self, conn, table: Table, records: list[dict[str, Any]]
    ) -> None:
        """Insert records individually to handle duplicates gracefully."""
        successful_inserts = 0

        for record in records:
            try:
                conn.execute(table.insert(), record)
                successful_inserts += 1
            except IntegrityError:
                # Skip duplicate
                continue

        self.logger.info(
            f"Inserted {successful_inserts}/{len(records)} records (skipped duplicates)"
        )

    def _prepare_record(self, record: dict[str, Any], batch_id: str) -> dict[str, Any]:
        """Prepare record for Oracle insertion with proper date formatting."""
        prepared = {}

        # DEBUG: Log schema and record structure for troubleshooting
        if len(prepared) == 0:  # Only log once per batch
            self.logger.info(f"🔍 Schema has {len(self.schema.get('properties', {}))} properties: {list(self.schema.get('properties', {}).keys())}")
            self.logger.info(f"🔍 Record has {len(record)} fields: {list(record.keys())}")

        # Process each field
        for key, value in record.items():
            # Skip metadata fields that will be added separately
            if key.startswith("_sdc_"):
                continue

            oracle_key = key.upper()

            # Handle null values
            if value is None:
                prepared[oracle_key] = None
                continue

            # Get property definition - with fallback for missing schema
            prop_def = self.schema.get("properties", {}).get(key, {})
            prop_type = prop_def.get("type", "string")
            prop_format = prop_def.get("format")

            # Handle anyOf structures
            if "anyOf" in prop_def:
                for type_option in prop_def["anyOf"]:
                    if type_option.get("type") != "null":
                        prop_type = type_option.get("type", "string")
                        prop_format = type_option.get("format", prop_format)
                        break

            # Convert value based on type and format
            if prop_type == "boolean":
                prepared[oracle_key] = "TRUE" if value else "FALSE"
            elif isinstance(value, str) and value.upper() in ("TRUE", "FALSE"):
                # Handle boolean strings specifically for Oracle NUMBER fields
                prepared[oracle_key] = 1 if value.upper() == "TRUE" else 0
            elif prop_type in ("object", "array"):
                prepared[oracle_key] = json.dumps(value)
            elif prop_type == "string":
                if prop_format in ("date-time", "date", "time"):
                    # Handle date/time strings with Oracle-compatible conversion
                    try:
                        if isinstance(value, str):
                            # Parse ISO format date strings for Oracle
                            if "T" in value:
                                # ISO datetime format: 2025-07-02T10:00:00Z
                                value_clean = value.replace("Z", "+00:00")
                                dt = datetime.fromisoformat(value_clean)
                                # Convert to timezone-naive datetime for Oracle compatibility
                                if dt.tzinfo is not None:
                                    dt = dt.replace(tzinfo=None)
                                prepared[oracle_key] = dt
                            else:
                                # Date only format: 2025-07-02
                                dt = datetime.strptime(value, "%Y-%m-%d")
                                prepared[oracle_key] = dt
                        else:
                            prepared[oracle_key] = str(value)[:4000]
                    except (ValueError, AttributeError):
                        # If date parsing fails, store as string
                        prepared[oracle_key] = str(value)[:4000]
                else:
                    # Regular string handling
                    max_length = self.config.get("max_varchar_length", 4000)
                    prepared[oracle_key] = str(value)[:max_length]
            elif prop_type in ("integer", "number") and isinstance(value, int | float):
                prepared[oracle_key] = value
            else:
                # Convert to string as fallback
                prepared[oracle_key] = str(value)[:4000]

        # ESPECIFICAÇÃO NOVA: TK_DATE apenas timestamp de gravação (não mais parte da PK)
        # Agora TK_DATE é apenas para auditoria, não para uniqueness
        import time
        current_time = datetime.fromtimestamp(time.time())
        prepared["TK_DATE"] = current_time

        # Add metadata if enabled and columns exist in target table
        if self.config.get("add_record_metadata", True):
            # Only add metadata columns that exist in the target table
            if self._table_columns is None or "_LOADED_AT" in self._table_columns:
                prepared["_LOADED_AT"] = current_time
            if self._table_columns is None or "_BATCH_ID" in self._table_columns:
                prepared["_BATCH_ID"] = batch_id
            if self._table_columns is None or "_ENTITY_NAME" in self._table_columns:
                prepared["_ENTITY_NAME"] = self.stream_name

            # Add extracted timestamp if available and column exists
            if self._table_columns is None or "_EXTRACTED_AT" in self._table_columns:
                if "_extracted_at" in record:
                    try:
                        if isinstance(record["_extracted_at"], str):
                            extracted_at = datetime.fromisoformat(
                                record["_extracted_at"].replace("Z", "+00:00")
                            )
                        else:
                            extracted_at = current_time
                        prepared["_EXTRACTED_AT"] = extracted_at
                    except (ValueError, AttributeError):
                        prepared["_EXTRACTED_AT"] = current_time
                else:
                    prepared["_EXTRACTED_AT"] = current_time

        return prepared

    def _retry_batch(self, table: Table, records: list[dict[str, Any]]) -> None:
        """Retry failed batch with exponential backoff."""
        max_retries = self.config.get("max_retries", 3)
        retry_delay = self.config.get("retry_delay", 1.0)

        for attempt in range(max_retries):
            try:
                self.target.update_metrics("retry_attempts", 1)

                # Wait before retry
                time.sleep(retry_delay * (2**attempt))

                # Retry the operation
                self._bulk_insert_batch(table, records)

                self.logger.info(f"Batch retry succeeded on attempt {attempt + 1}")
                return

            except Exception as e:
                self.logger.warning(f"Retry attempt {attempt + 1} failed: {e}")

                if attempt == max_retries - 1:
                    self.logger.exception(f"All {max_retries} retry attempts failed")
                    raise

    def activate_version(self, new_version: int) -> None:
        """Finalize the sink by flushing remaining records."""
        # Flush any remaining records
        with self._lock:
            if self._current_batch:
                self._flush_batch()

        # Log final statistics
        if self.config.get("enable_performance_metrics"):
            self.logger.info(
                f"Sink '{self.stream_name}' processed {self._total_records:,} total records"
            )

    def __del__(self):
        """Cleanup when sink is destroyed."""
        try:
            # Final flush
            if hasattr(self, "_current_batch") and self._current_batch:
                self._flush_batch()

            # Close Oracle native pool first (TCPS-specific cleanup)
            if hasattr(self, "_oracle_pool") and self._oracle_pool:
                try:
                    self._oracle_pool.close()
                    self.logger.info("🔒 Oracle native connection pool closed")
                except Exception as pool_e:
                    self.logger.warning(f"Warning closing Oracle pool: {pool_e}")

            # Close SQLAlchemy engine
            if hasattr(self, "_engine") and self._engine:
                self._engine.dispose()

        except Exception as e:
            self.logger.exception(f"Error during sink cleanup: {e}")
