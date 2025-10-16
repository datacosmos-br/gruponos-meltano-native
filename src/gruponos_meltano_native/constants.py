"""GrupoNOS Meltano Native Constants - Domain-specific constants.

Provides GrupoNOS-specific constants extending FlextConstants for
Oracle WMS integration and Meltano pipeline operations.

Copyright (c) 2025 Grupo Nós. Todos os direitos reservados.
SPDX-License-Identifier: Proprietary
"""

from __future__ import annotations

from enum import StrEnum
from typing import ClassVar, Final


class GruponosMeltanoNativeConstants(FlextConstants):
    """GrupoNOS Meltano Native constants extending FlextConstants.

    Contains all constants for GrupoNOS Oracle WMS integration and
    Meltano pipeline operations following FLEXT standards with
    comprehensive validation and enhanced organization.
    """

    # Project identification
    PROJECT_PREFIX: Final[str] = "GRUPONOS_MELTANO_NATIVE"
    PROJECT_NAME: Final[str] = "GrupoNOS Meltano Native"
    PROJECT_VERSION: Final[str] = "1.0.0"
    PROJECT_DESCRIPTION: Final[str] = (
        "Native Meltano integration for GrupoNOS Oracle WMS"
    )

    # Oracle WMS Configuration with enhanced defaults
    class OracleWMS:
        """Oracle WMS specific constants with comprehensive configuration."""

        DEFAULT_HOST: Final[str] = "localhost"
        DEFAULT_PORT: Final[int] = 1521
        DEFAULT_SERVICE_NAME: Final[str] = "WMS"
        DEFAULT_SCHEMA: Final[str] = "WMS_USER"
        DEFAULT_TIMEOUT: Final[int] = 30
        DEFAULT_POOL_SIZE: Final[int] = 10
        DEFAULT_POOL_MAX: Final[int] = 20

        # Connection limits
        MIN_TIMEOUT: Final[int] = 1
        MAX_TIMEOUT: Final[int] = 3600
        MIN_POOL_SIZE: Final[int] = 1
        MAX_POOL_SIZE: Final[int] = 100
        MIN_POOL_MAX: Final[int] = 1
        MAX_POOL_MAX: Final[int] = 100

        # String length limits
        MAX_HOST_LENGTH: Final[int] = 255
        MAX_SERVICE_NAME_LENGTH: Final[int] = 128
        MAX_SCHEMA_LENGTH: Final[int] = 128
        MAX_USERNAME_LENGTH: Final[int] = 128
        MAX_PASSWORD_LENGTH: Final[int] = 128

    # Enhanced Meltano Pipeline Configuration
    class MeltanoPipeline:
        """Meltano pipeline specific constants with comprehensive settings."""

        DEFAULT_BATCH_SIZE: Final[int] = 1000
        DEFAULT_MAX_WORKERS: Final[int] = 4
        DEFAULT_TIMEOUT: Final[int] = 3600
        DEFAULT_RETRY_ATTEMPTS: Final[int] = 3
        DEFAULT_RETRY_DELAY: Final[float] = 5.0

        # Performance limits
        MIN_BATCH_SIZE: Final[int] = 1
        MAX_BATCH_SIZE: Final[int] = 100000
        MIN_MAX_WORKERS: Final[int] = 1
        MAX_MAX_WORKERS: Final[int] = 32
        MIN_TIMEOUT: Final[int] = 1
        MAX_TIMEOUT: Final[int] = 86400  # 24 hours
        MIN_RETRY_ATTEMPTS: Final[int] = 0
        MAX_RETRY_ATTEMPTS: Final[int] = 10
        MIN_RETRY_DELAY: Final[float] = 0.1
        MAX_RETRY_DELAY: Final[float] = 300.0

    # Enhanced Data Processing Configuration
    class DataProcessing:
        """Data processing specific constants with comprehensive limits."""

        DEFAULT_CHUNK_SIZE: Final[int] = 10000
        DEFAULT_MEMORY_LIMIT: Final[int] = 1024 * 1024 * 1024  # 1GB
        DEFAULT_COMPRESSION_LEVEL: Final[int] = 6
        DEFAULT_ENCODING: Final[str] = "utf-8"

        # Processing limits
        MIN_CHUNK_SIZE: Final[int] = 1
        MAX_CHUNK_SIZE: Final[int] = 1000000
        MIN_MEMORY_LIMIT: Final[int] = 1024 * 1024  # 1MB
        MAX_MEMORY_LIMIT: Final[int] = 1024 * 1024 * 1024 * 10  # 10GB
        MIN_COMPRESSION_LEVEL: Final[int] = 0
        MAX_COMPRESSION_LEVEL: Final[int] = 9

        # Supported encodings
        SUPPORTED_ENCODINGS: Final[FlextTypes.StringList] = [
            "utf-8",
            "utf-16",
            "ascii",
            "latin-1",
            "cp1252",
        ]

    # Enhanced File and Directory Configuration
    class Paths:
        """Path configuration constants with validation."""

        DEFAULT_DATA_DIR: Final[str] = "./data"
        DEFAULT_LOG_DIR: Final[str] = "./logs"
        DEFAULT_CONFIG_DIR: Final[str] = "./config"
        DEFAULT_OUTPUT_DIR: Final[str] = "./output"
        DEFAULT_TEMP_DIR: Final[str] = "./temp"

        # Path validation
        MAX_PATH_LENGTH: Final[int] = 4096
        MIN_PATH_LENGTH: Final[int] = 1

    # Enhanced Logging Configuration
    class Logging:
        """Logging configuration constants with comprehensive options."""

        DEFAULT_LEVEL: Final[str] = "INFO"
        DEFAULT_FORMAT: Final[str] = (
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        DEFAULT_MAX_FILE_SIZE: Final[int] = 10 * 1024 * 1024  # 10MB
        DEFAULT_BACKUP_COUNT: Final[int] = 5

        # Logging limits
        MIN_MAX_FILE_SIZE: Final[int] = 1024  # 1KB
        MAX_MAX_FILE_SIZE: Final[int] = 1024 * 1024 * 100  # 100MB
        MIN_BACKUP_COUNT: Final[int] = 1
        MAX_BACKUP_COUNT: Final[int] = 50

        # Valid log levels
        VALID_LEVELS: Final[FlextTypes.StringList] = [
            "DEBUG",
            "INFO",
            "WARNING",
            "ERROR",
            "CRITICAL",
        ]

    # Enhanced Performance Configuration
    class Performance:
        """Performance configuration constants with comprehensive timeouts."""

        DEFAULT_BATCH_SIZE: Final[int] = 1000
        MAX_BATCH_ITEMS: Final[int] = 10000
        DEFAULT_QUERY_TIMEOUT: Final[int] = 300
        DEFAULT_CONNECTION_TIMEOUT: Final[int] = 30
        DEFAULT_READ_TIMEOUT: Final[int] = 60
        DEFAULT_WRITE_TIMEOUT: Final[int] = 60

        # Performance limits
        MIN_BATCH_SIZE: Final[int] = 1
        MAX_BATCH_SIZE: Final[int] = 100000
        MIN_QUERY_TIMEOUT: Final[int] = 1
        MAX_QUERY_TIMEOUT: Final[int] = 3600
        MIN_CONNECTION_TIMEOUT: Final[int] = 1
        MAX_CONNECTION_TIMEOUT: Final[int] = 300
        MIN_READ_TIMEOUT: Final[int] = 1
        MAX_READ_TIMEOUT: Final[int] = 300
        MIN_WRITE_TIMEOUT: Final[int] = 1
        MAX_WRITE_TIMEOUT: Final[int] = 300

    # Enhanced Security Configuration
    class Security:
        """Security configuration constants with comprehensive algorithms."""

        DEFAULT_ENCRYPTION_ALGORITHM: Final[str] = "AES-256-GCM"
        DEFAULT_HASH_ALGORITHM: Final[str] = "SHA-256"
        DEFAULT_KEY_LENGTH: Final[int] = 32
        DEFAULT_SALT_LENGTH: Final[int] = 16

        # Security limits
        MIN_KEY_LENGTH: Final[int] = 16
        MAX_KEY_LENGTH: Final[int] = 64
        MIN_SALT_LENGTH: Final[int] = 8
        MAX_SALT_LENGTH: Final[int] = 32

        # Supported algorithms
        SUPPORTED_ENCRYPTION_ALGORITHMS: ClassVar[FlextTypes.StringList] = [
            "AES-256-GCM",
            "AES-128-GCM",
            "ChaCha20-Poly1305",
        ]
        SUPPORTED_HASH_ALGORITHMS: ClassVar[FlextTypes.StringList] = [
            "SHA-256",
            "SHA-512",
            "BLAKE2b",
            "BLAKE2s",
        ]

    # Enhanced Status Enums with comprehensive states
    class Status(StrEnum):
        """Pipeline status enumeration with comprehensive states."""

        PENDING = "pending"
        RUNNING = "running"
        COMPLETED = "completed"
        FAILED = "failed"
        CANCELLED = "cancelled"
        PAUSED = "paused"
        RETRYING = "retrying"
        TIMEOUT = "timeout"
        VALIDATING = "validating"
        TRANSFORMING = "transforming"

    class DataType(StrEnum):
        """Data type enumeration with comprehensive types."""

        RAW = "raw"
        PROCESSED = "processed"
        TRANSFORMED = "transformed"
        VALIDATED = "validated"
        ARCHIVED = "archived"
        STAGED = "staged"
        CLEANSED = "cleansed"
        ENRICHED = "enriched"

    class OperationType(StrEnum):
        """Operation type enumeration with comprehensive operations."""

        EXTRACT = "extract"
        LOAD = "load"
        TRANSFORM = "transform"
        VALIDATE = "validate"
        ARCHIVE = "archive"
        SYNC = "sync"
        MERGE = "merge"
        CLEANSE = "cleanse"
        ENRICH = "enrich"

    # Enhanced Validation Constants
    class Validation:
        """Validation constants with comprehensive limits."""

        # Batch processing limits
        MIN_BATCH_SIZE: Final[int] = 1
        MAX_BATCH_SIZE: Final[int] = 100000

        # Timeout limits
        MIN_TIMEOUT: Final[int] = 1
        MAX_TIMEOUT: Final[int] = 3600

        # Retry limits
        MIN_RETRY_ATTEMPTS: Final[int] = 0
        MAX_RETRY_ATTEMPTS: Final[int] = 10
        MIN_RETRY_DELAY: Final[float] = 0.1
        MAX_RETRY_DELAY: Final[float] = 300.0

        # String length limits
        MIN_NAME_LENGTH: Final[int] = 1
        MAX_NAME_LENGTH: Final[int] = 255
        MIN_DESCRIPTION_LENGTH: Final[int] = 0
        MAX_DESCRIPTION_LENGTH: Final[int] = 1000

        # Numeric limits
        MIN_PERCENTAGE: Final[float] = 0.0
        MAX_PERCENTAGE: Final[float] = 100.0
        MIN_COUNT: Final[int] = 0
        MAX_COUNT: Final[int] = 1000000

    # Enhanced Error Messages with comprehensive coverage
    class ErrorMessages:
        """Error message constants with comprehensive error coverage."""

        # Connection errors
        CONNECTION_FAILED = "Failed to connect to Oracle WMS"
        CONNECTION_TIMEOUT = "Connection to Oracle WMS timed out"
        CONNECTION_REFUSED = "Connection to Oracle WMS was refused"
        CONNECTION_LOST = "Connection to Oracle WMS was lost"

        # Query errors
        QUERY_TIMEOUT = "Query execution timed out"
        QUERY_FAILED = "Query execution failed"
        QUERY_SYNTAX_ERROR = "Query syntax error"
        QUERY_PERMISSION_DENIED = "Query permission denied"

        # Validation errors
        VALIDATION_FAILED = "Data validation failed"
        VALIDATION_TIMEOUT = "Data validation timed out"
        VALIDATION_SCHEMA_ERROR = "Data validation schema error"

        # Processing errors
        PROCESSING_FAILED = "Data processing failed"
        PROCESSING_TIMEOUT = "Data processing timed out"
        PROCESSING_MEMORY_ERROR = "Data processing memory error"
        PROCESSING_DISK_ERROR = "Data processing disk error"

        # Configuration errors
        CONFIGURATION_INVALID = "Invalid configuration"
        CONFIGURATION_MISSING = "Required configuration missing"
        CONFIGURATION_TYPE_ERROR = "Configuration type error"

        # Permission errors
        PERMISSION_DENIED = "Permission denied"
        PERMISSION_INSUFFICIENT = "Insufficient permissions"
        PERMISSION_EXPIRED = "Permissions expired"

        # Resource errors
        RESOURCE_NOT_FOUND = "Resource not found"
        RESOURCE_UNAVAILABLE = "Resource unavailable"
        RESOURCE_LOCKED = "Resource locked"
        RESOURCE_EXHAUSTED = "Resource exhausted"

        # General errors
        UNKNOWN_ERROR = "Unknown error occurred"
        INTERNAL_ERROR = "Internal error occurred"
        EXTERNAL_SERVICE_ERROR = "External service error"
        NETWORK_ERROR = "Network error occurred"

    # Enhanced Monitoring Constants
    class Monitoring:
        """Monitoring and metrics constants."""

        # Metrics collection intervals
        DEFAULT_METRICS_INTERVAL: Final[int] = 60  # seconds
        MIN_METRICS_INTERVAL: Final[int] = 10  # seconds
        MAX_METRICS_INTERVAL: Final[int] = 3600  # 1 hour

        # Performance thresholds
        PERFORMANCE_WARNING_THRESHOLD: Final[float] = 1000.0  # milliseconds
        PERFORMANCE_CRITICAL_THRESHOLD: Final[float] = 5000.0  # milliseconds

        # Memory thresholds
        MEMORY_WARNING_THRESHOLD: Final[float] = 80.0  # percentage
        MEMORY_CRITICAL_THRESHOLD: Final[float] = 95.0  # percentage

        # CPU thresholds
        CPU_WARNING_THRESHOLD: Final[float] = 80.0  # percentage
        CPU_CRITICAL_THRESHOLD: Final[float] = 95.0  # percentage

    # Enhanced Integration Constants
    class Integration:
        """Integration and external system constants."""

        # External system types
        SYSTEM_TYPE_ORACLE: Final[str] = "oracle"
        SYSTEM_TYPE_POSTGRESQL: Final[str] = "postgresql"
        SYSTEM_TYPE_MYSQL: Final[str] = "mysql"
        SYSTEM_TYPE_MONGODB: Final[str] = "mongodb"
        SYSTEM_TYPE_REDIS: Final[str] = "redis"

        # Integration protocols
        PROTOCOL_JDBC: Final[str] = "jdbc"
        PROTOCOL_ODBC: Final[str] = "odbc"
        PROTOCOL_REST: Final[str] = "rest"
        PROTOCOL_GRAPHQL: Final[str] = "graphql"
        PROTOCOL_GRPC: Final[str] = "grpc"

        # Supported formats
        FORMAT_JSON: Final[str] = "json"
        FORMAT_XML: Final[str] = "xml"
        FORMAT_CSV: Final[str] = "csv"
        FORMAT_PARQUET: Final[str] = "parquet"
        FORMAT_AVRO: Final[str] = "avro"
