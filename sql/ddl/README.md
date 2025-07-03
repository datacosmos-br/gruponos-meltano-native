# Oracle DDL Files for WMS Tables

## Overview
These DDL files are generated from real WMS API schema discovery to ensure correct Oracle data types.

## Tables

### WMS_ALLOCATION
- **Columns**: 31
- **Primary Key**: ID, MOD_TS (composite for historical versioning)
- **Key columns**: All quantity fields are NUMBER type

### WMS_ORDER_HDR  
- **Columns**: 130
- **Primary Key**: ID, MOD_TS (composite for historical versioning)
- **Key columns**: All date fields are TIMESTAMP(6), all amount fields are NUMBER

### WMS_ORDER_DTL
- **Columns**: 95
- **Primary Key**: ID, MOD_TS (composite for historical versioning)
- **Key columns**:
  - COST: NUMBER (not VARCHAR2)
  - CUST_DATE_*: TIMESTAMP(6) (not VARCHAR2)
  - CUST_DECIMAL_*: NUMBER (not VARCHAR2)
  - CUST_NUMBER_*: NUMBER (not VARCHAR2)
  - SALE_PRICE: NUMBER
  - VOUCHER_AMOUNT: NUMBER

## Schema Discovery

Schemas are discovered from WMS API and saved to `sql/wms_schemas.json`.

To refresh schemas:
```bash
make discover-schemas
```

To recreate tables:
```bash
make recreate-tables
```

## Important Notes

1. **NO FALLBACK SCHEMAS**: The system will fail if proper schemas cannot be discovered. This prevents creating tables with incorrect structures.

2. **Schema File**: The file `sql/wms_schemas.json` contains the discovered schemas and should be kept in version control to ensure consistency.

3. **Type Mapping**: Oracle types are determined by field patterns:
   - Fields ending with `_date` or containing `date_`: TIMESTAMP(6)
   - Fields with `cost`, `price`, `amount`, `qty`: NUMBER
   - Fields with `decimal`, `number`: NUMBER
   - Boolean flags (`_flg`): NUMBER(1,0)

Generated on: 2025-07-02