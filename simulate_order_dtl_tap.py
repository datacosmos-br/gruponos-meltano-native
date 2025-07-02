#!/usr/bin/env python3
"""Simulate tap output for order_dtl with realistic data."""

import random
import sys
from datetime import datetime, timedelta

ENTITY = "order_dtl"


def generate_allocation_record(i, base_time):
    """Generate a realistic allocation record."""
    created = base_time - timedelta(minutes=random.randint(0, 5))

    return {
        "allocation_id": f"ALLOC-{random.randint(100000, 999999):06d}",
        "order_id": f"ORD-{random.randint(10000, 99999):06d}",
        "item_id": f"ITEM-{random.randint(1000, 9999):04d}",
        "from_location": f"LOC-{random.randint(1, 999):03d}",
        "to_location": f"STAGE-{random.randint(1, 50):02d}",
        "quantity": random.randint(1, 500),
        "status": random.choice(["PENDING", "IN_PROGRESS", "COMPLETED", "CANCELLED"]),
        "priority": random.randint(1, 5),
        "created_date_utc": created.isoformat() + "Z",
        "last_update_date_utc": (
            created + timedelta(seconds=random.randint(0, 300))
        ).isoformat()
        + "Z",
        "user_id": f"USER-{random.randint(1, 100):03d}",
        "warehouse_id": random.choice(["WH-001", "WH-002", "WH-003"]),
    }


def generate_order_hdr_record(i, base_time):
    """Generate a realistic order header record."""
    created = base_time - timedelta(minutes=random.randint(0, 5))

    return {
        "order_id": f"ORD-{random.randint(10000, 99999):06d}",
        "customer_id": f"CUST-{random.randint(1000, 9999):04d}",
        "order_type": random.choice(["STANDARD", "EXPRESS", "PRIORITY", "BACKORDER"]),
        "status": random.choice(
            ["NEW", "PROCESSING", "SHIPPED", "DELIVERED", "CANCELLED"]
        ),
        "total_amount": round(random.uniform(10.0, 5000.0), 2),
        "currency": "USD",
        "order_date": created.isoformat() + "Z",
        "ship_date": (created + timedelta(days=random.randint(1, 3))).isoformat() + "Z",
        "delivery_date": (created + timedelta(days=random.randint(3, 7))).isoformat()
        + "Z",
        "warehouse_id": random.choice(["WH-001", "WH-002", "WH-003"]),
        "last_update_date_utc": (
            created + timedelta(seconds=random.randint(0, 300))
        ).isoformat()
        + "Z",
    }


def generate_order_dtl_record(i, base_time):
    """Generate a realistic order detail record."""
    created = base_time - timedelta(minutes=random.randint(0, 5))

    return {
        "order_dtl_id": f"DTL-{random.randint(100000, 999999):06d}",
        "order_id": f"ORD-{random.randint(10000, 99999):06d}",
        "line_number": random.randint(1, 10),
        "item_id": f"ITEM-{random.randint(1000, 9999):04d}",
        "quantity_ordered": random.randint(1, 100),
        "quantity_shipped": random.randint(0, 100),
        "unit_price": round(random.uniform(1.0, 500.0), 2),
        "total_price": round(random.uniform(10.0, 5000.0), 2),
        "status": random.choice(
            ["PENDING", "ALLOCATED", "PICKED", "PACKED", "SHIPPED"]
        ),
        "created_date_utc": created.isoformat() + "Z",
        "last_update_date_utc": (
            created + timedelta(seconds=random.randint(0, 300))
        ).isoformat()
        + "Z",
    }


def get_schema(entity):
    """Get schema for entity."""
    schemas = {
        "allocation": {
            "type": "object",
            "properties": {
                "allocation_id": {"type": "string"},
                "order_id": {"type": "string"},
                "item_id": {"type": "string"},
                "from_location": {"type": "string"},
                "to_location": {"type": "string"},
                "quantity": {"type": "integer"},
                "status": {"type": "string"},
                "priority": {"type": "integer"},
                "created_date_utc": {"type": "string", "format": "date-time"},
                "last_update_date_utc": {"type": "string", "format": "date-time"},
                "user_id": {"type": "string"},
                "warehouse_id": {"type": "string"},
            },
        },
        "order_hdr": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string"},
                "customer_id": {"type": "string"},
                "order_type": {"type": "string"},
                "status": {"type": "string"},
                "total_amount": {"type": "number"},
                "currency": {"type": "string"},
                "order_date": {"type": "string", "format": "date-time"},
                "ship_date": {"type": "string", "format": "date-time"},
                "delivery_date": {"type": "string", "format": "date-time"},
                "warehouse_id": {"type": "string"},
                "last_update_date_utc": {"type": "string", "format": "date-time"},
            },
        },
        "order_dtl": {
            "type": "object",
            "properties": {
                "order_dtl_id": {"type": "string"},
                "order_id": {"type": "string"},
                "line_number": {"type": "integer"},
                "item_id": {"type": "string"},
                "quantity_ordered": {"type": "integer"},
                "quantity_shipped": {"type": "integer"},
                "unit_price": {"type": "number"},
                "total_price": {"type": "number"},
                "status": {"type": "string"},
                "created_date_utc": {"type": "string", "format": "date-time"},
                "last_update_date_utc": {"type": "string", "format": "date-time"},
            },
        },
    }
    return schemas.get(entity, {})


def main():
    # Current time for this batch
    base_time = datetime.utcnow()

    # Send schema
    {
        "type": "SCHEMA",
        "stream": ENTITY,
        "schema": get_schema(ENTITY),
        "key_properties": [f"{ENTITY}_id"] if ENTITY != "order_hdr" else ["order_id"],
    }

    sys.stdout.flush()

    # Number of records per sync (incremental)
    num_records = random.randint(50, 200)

    # Generate appropriate records based on entity
    for i in range(1, num_records + 1):
        if ENTITY == "allocation":
            generate_allocation_record(i, base_time)
        elif ENTITY == "order_hdr":
            generate_order_hdr_record(i, base_time)
        elif ENTITY == "order_dtl":
            generate_order_dtl_record(i, base_time)
        else:
            continue

        sys.stdout.flush()

    # Send state
    {
        "type": "STATE",
        "value": {
            "bookmarks": {
                ENTITY: {
                    "replication_key_value": base_time.isoformat() + "Z",
                    "version": 1,
                }
            }
        },
    }
    sys.stdout.flush()


if __name__ == "__main__":
    main()
