# Validators Module

**Enterprise Data Validation and Quality Assurance for GrupoNOS Meltano Native**

This module provides comprehensive multi-layer data validation with business rule enforcement, data quality monitoring, and performance tracking, built on FLEXT validation standards with railway-oriented programming patterns.

## Components

### `data_validator.py` - Core Data Validation System

Enterprise data validation system with multi-layer validation chains and comprehensive business rule enforcement.

#### Key Classes

##### `GruponosMeltanoDataValidator`

Primary data validation system with enterprise features:

- **Multi-Layer Validation**: Schema, business rules, data quality, and referential integrity
- **Railway-Oriented Programming**: FlextResult chains for clean error propagation
- **Performance Monitoring**: Validation performance tracking and optimization
- **Configurable Rules**: Dynamic business rule configuration and management
- **Quality Metrics**: Comprehensive data quality scoring and reporting

#### Validation Layers

##### 1. Schema Validation

- **Structure Validation**: Ensures data matches expected schema structure
- **Type Checking**: Validates data types and format compliance
- **Required Fields**: Enforces required field presence and non-null constraints
- **Field Validation**: Individual field validation with custom rules

##### 2. Business Rule Validation

- **Oracle WMS Rules**: WMS-specific business logic validation
- **Cross-Field Validation**: Rules spanning multiple fields or records
- **Conditional Logic**: Complex conditional validation scenarios
- **Custom Rules**: Configurable custom business rules

##### 3. Data Quality Validation

- **Completeness Checks**: Data completeness analysis and scoring
- **Accuracy Validation**: Data accuracy verification against known patterns
- **Consistency Checks**: Cross-record consistency validation
- **Anomaly Detection**: Statistical anomaly detection and reporting

##### 4. Referential Integrity

- **Foreign Key Validation**: Reference integrity across related entities
- **Consistency Checks**: Data consistency across multiple tables
- **Constraint Validation**: Business constraint enforcement

## Usage Examples

### Basic Data Validation

```python
from gruponos_meltano_native.validators import (
    GruponosMeltanoDataValidator,
    create_gruponos_meltano_validator_for_environment
)

# Create validator for current environment
validator = create_gruponos_meltano_validator_for_environment()

# Validate allocation data
allocation_data = [
    {
        "allocation_id": "A001",
        "item_code": "ITEM001",
        "quantity": 100,
        "facility_code": "DC01",
        "location": "A1-B2-C3"
    },
    # ... more records
]

# Execute validation chain
validation_result = await validator.validate_allocation_data(allocation_data)

if validation_result.success:
    validated_data = validation_result.data
    print(f"Validation passed: {len(validated_data)} records validated")
else:
    print(f"Validation failed: {validation_result.error}")
    # Access detailed validation errors
    for error in validation_result.validation_errors:
        print(f"  - {error.field}: {error.message}")
```

### ETL Pipeline Integration

```python
class ETLDataProcessor:
    def __init__(self, validator: GruponosMeltanoDataValidator):
        self.validator = validator

    async def process_wms_data(self, raw_data):
        """Process WMS data with comprehensive validation."""
        return (
            await self.validator.validate_schema(raw_data)
            .flat_map_async(lambda schema_valid:
                self.validator.validate_business_rules(schema_valid))
            .flat_map_async(lambda business_valid:
                self.validator.validate_data_quality(business_valid))
            .flat_map_async(lambda quality_valid:
                self.validator.validate_referential_integrity(quality_valid))
            .map_async(lambda final_valid:
                self.validator.enrich_with_metadata(final_valid))
        )
```

### Advanced Validation Configuration

```python
from gruponos_meltano_native.validators import ValidationRules, DataQualityThresholds

# Configure validation rules
validation_config = {
    "schema_rules": {
        "allocation": {
            "required_fields": ["allocation_id", "item_code", "quantity", "facility_code"],
            "field_types": {
                "allocation_id": str,
                "item_code": str,
                "quantity": int,
                "facility_code": str,
                "location": str
            },
            "field_constraints": {
                "quantity": {"min": 1, "max": 999999},
                "facility_code": {"pattern": r"^[A-Z]{2}\d{2}$"},
                "location": {"pattern": r"^[A-Z]\d+-[A-Z]\d+-[A-Z]\d+$"}
            }
        }
    },

    "business_rules": {
        "allocation": [
            {
                "name": "positive_quantity",
                "description": "Allocation quantity must be positive",
                "condition": lambda record: record.get("quantity", 0) > 0,
                "error_message": "Allocation quantity must be greater than zero"
            },
            {
                "name": "valid_facility",
                "description": "Facility code must be valid",
                "condition": lambda record: record.get("facility_code") in ["DC01", "DC02", "DC03"],
                "error_message": "Invalid facility code"
            }
        ]
    },

    "quality_thresholds": {
        "completeness_threshold": 0.95,
        "accuracy_threshold": 0.98,
        "consistency_threshold": 0.99
    }
}

# Create validator with custom configuration
validator = GruponosMeltanoDataValidator(validation_config)
```

## Validation Patterns

### Railway-Oriented Validation

```python
def validate_wms_data_pipeline(data: List[dict]) -> FlextResult[List[dict]]:
    """Comprehensive validation pipeline with error propagation."""

    return (
        validate_basic_structure(data)
        .flat_map(lambda structured: validate_required_fields(structured))
        .flat_map(lambda required: validate_field_types(required))
        .flat_map(lambda typed: validate_business_constraints(typed))
        .flat_map(lambda constrained: validate_data_quality_metrics(constrained))
        .flat_map(lambda quality: validate_cross_record_consistency(quality))
        .map(lambda consistent: enrich_with_validation_metadata(consistent))
    )
```

### Batch Validation with Performance Monitoring

```python
class BatchValidator:
    def __init__(self, validator: GruponosMeltanoDataValidator):
        self.validator = validator
        self.performance_tracker = ValidationPerformanceTracker()

    async def validate_large_dataset(self, data: List[dict], batch_size: int = 1000):
        """Validate large dataset in batches with performance tracking."""
        total_records = len(data)
        validated_records = []
        validation_errors = []

        with self.performance_tracker.track_operation("batch_validation"):
            for i in range(0, total_records, batch_size):
                batch = data[i:i + batch_size]

                batch_result = await self.validator.validate_batch(batch)

                if batch_result.success:
                    validated_records.extend(batch_result.data)
                else:
                    validation_errors.extend(batch_result.validation_errors)

                # Report progress
                progress = ((i + len(batch)) / total_records) * 100
                print(f"Validation progress: {progress:.1f}%")

        if validation_errors:
            return FlextResult[None].fail(f"Validation failed with {len(validation_errors)} errors")

        return FlextResult[None].ok(validated_records)
```

### Custom Validation Rules

```python
class WMSBusinessRules:
    """WMS-specific business rule implementations."""

    @staticmethod
    def validate_allocation_consistency(record: dict) -> FlextResult[dict]:
        """Validate allocation record consistency."""
        # Check item-location compatibility
        item_code = record.get("item_code")
        location = record.get("location")

        if not WMSBusinessRules._is_valid_item_location_combination(item_code, location):
            return FlextResult[None].fail(
                f"Item {item_code} cannot be allocated to location {location}"
            )

        # Check quantity limits
        quantity = record.get("quantity", 0)
        max_quantity = WMSBusinessRules._get_max_quantity_for_location(location)

        if quantity > max_quantity:
            return FlextResult[None].fail(
                f"Quantity {quantity} exceeds maximum {max_quantity} for location {location}"
            )

        return FlextResult[None].ok(record)

    @staticmethod
    def validate_order_completion_rules(order_records: List[dict]) -> FlextResult[List[dict]]:
        """Validate order completion business rules."""
        # Group by order ID
        orders = {}
        for record in order_records:
            order_id = record.get("order_id")
            if order_id not in orders:
                orders[order_id] = []
            orders[order_id].append(record)

        # Validate each order
        validated_records = []
        for order_id, order_lines in orders.items():
            order_validation = WMSBusinessRules._validate_single_order(order_lines)

            if order_validation.is_failure:
                return FlextResult[None].fail(f"Order {order_id} validation failed: {order_validation.error}")

            validated_records.extend(order_validation.data)

        return FlextResult[None].ok(validated_records)
```

## Data Quality Monitoring

### Quality Metrics Collection

```python
class DataQualityMonitor:
    def __init__(self, validator: GruponosMeltanoDataValidator):
        self.validator = validator
        self.quality_history = []

    async def assess_data_quality(self, data: List[dict]) -> dict:
        """Comprehensive data quality assessment."""

        # Completeness analysis
        completeness_score = self._calculate_completeness(data)

        # Accuracy analysis
        accuracy_score = await self._calculate_accuracy(data)

        # Consistency analysis
        consistency_score = self._calculate_consistency(data)

        # Uniqueness analysis
        uniqueness_score = self._calculate_uniqueness(data)

        # Overall quality score
        overall_score = (
            completeness_score * 0.3 +
            accuracy_score * 0.3 +
            consistency_score * 0.25 +
            uniqueness_score * 0.15
        )

        quality_report = {
            "timestamp": datetime.utcnow().isoformat(),
            "record_count": len(data),
            "completeness_score": completeness_score,
            "accuracy_score": accuracy_score,
            "consistency_score": consistency_score,
            "uniqueness_score": uniqueness_score,
            "overall_quality_score": overall_score,
            "quality_grade": self._get_quality_grade(overall_score)
        }

        self.quality_history.append(quality_report)
        return quality_report

    def _get_quality_grade(self, score: float) -> str:
        """Convert quality score to letter grade."""
        if score >= 0.95:
            return "A"
        elif score >= 0.90:
            return "B"
        elif score >= 0.80:
            return "C"
        elif score >= 0.70:
            return "D"
        else:
            return "F"
```

### Anomaly Detection

```python
class DataAnomalyDetector:
    def __init__(self):
        self.baseline_metrics = {}

    async def detect_anomalies(self, current_data: List[dict]) -> List[dict]:
        """Detect data anomalies using statistical analysis."""
        anomalies = []

        # Volume anomaly detection
        current_volume = len(current_data)
        expected_volume_range = self._get_expected_volume_range()

        if not (expected_volume_range["min"] <= current_volume <= expected_volume_range["max"]):
            anomalies.append({
                "type": "volume_anomaly",
                "severity": "warning",
                "message": f"Data volume {current_volume} outside expected range {expected_volume_range}",
                "recommendation": "Investigate data source for potential issues"
            })

        # Pattern anomaly detection
        pattern_anomalies = await self._detect_pattern_anomalies(current_data)
        anomalies.extend(pattern_anomalies)

        # Distribution anomaly detection
        distribution_anomalies = self._detect_distribution_anomalies(current_data)
        anomalies.extend(distribution_anomalies)

        return anomalies
```

## Configuration

### Environment Variables

```bash
# Validation configuration
GRUPONOS_VALIDATION_ENABLED=true
GRUPONOS_VALIDATION_STRICT_MODE=false
GRUPONOS_VALIDATION_BATCH_SIZE=1000

# Quality thresholds
GRUPONOS_DATA_QUALITY_COMPLETENESS_THRESHOLD=0.95
GRUPONOS_DATA_QUALITY_ACCURACY_THRESHOLD=0.98
GRUPONOS_DATA_QUALITY_CONSISTENCY_THRESHOLD=0.99

# Performance settings
GRUPONOS_VALIDATION_TIMEOUT_SECONDS=300
GRUPONOS_VALIDATION_MAX_ERRORS=100
GRUPONOS_VALIDATION_PARALLEL_WORKERS=4
```

## Testing Support

### Mock Validator

```python
class MockDataValidator:
    def __init__(self, should_pass=True):
        self.should_pass = should_pass
        self.validation_calls = []

    async def validate_allocation_data(self, data):
        self.validation_calls.append(("allocation", len(data)))

        if self.should_pass:
            return FlextResult[None].ok(data)
        else:
            return FlextResult[None].fail("Mock validation failure")

    def get_validation_call_count(self):
        return len(self.validation_calls)
```

### Validation Testing Utilities

```python
class ValidationTestUtils:
    @staticmethod
    def create_valid_allocation_record():
        return {
            "allocation_id": "A001",
            "item_code": "ITEM001",
            "quantity": 100,
            "facility_code": "DC01",
            "location": "A1-B2-C3",
            "mod_ts": datetime.utcnow()
        }

    @staticmethod
    def create_invalid_allocation_record():
        return {
            "allocation_id": "",  # Invalid: empty ID
            "item_code": "ITEM001",
            "quantity": -10,  # Invalid: negative quantity
            "facility_code": "INVALID",  # Invalid: bad facility code
            "location": "BADLOC"  # Invalid: bad location format
        }
```

## Development Guidelines

### Validation Design Principles

1. **Layer Separation**: Clear separation between validation layers
2. **Railway-Oriented**: Use FlextResult for clean error propagation
3. **Performance Aware**: Optimize for large dataset validation
4. **Configurable**: Support environment-specific validation rules
5. **Observable**: Comprehensive logging and monitoring

### Business Rule Implementation

1. **Testable**: All business rules must be unit testable
2. **Documented**: Clear documentation of business logic
3. **Configurable**: Support dynamic rule configuration
4. **Performance**: Optimize expensive validation operations
5. **Maintainable**: Clean, readable validation code

---

**Purpose**: Enterprise data validation and quality assurance  
**Architecture**: Multi-layer validation with railway-oriented programming  
**Performance**: Optimized for large dataset validation  
**Quality**: Comprehensive data quality monitoring and reporting
