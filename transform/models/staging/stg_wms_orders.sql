{{ config(
    materialized='view',
    tags=['staging', 'orders']
) }}

with order_headers as (
    select * from {{ source('wms_raw', 'order_hdr') }}
),

order_details as (
    select * from {{ source('wms_raw', 'order_dtl') }}
),

order_header_cleaned as (
    select
        -- Primary keys
        order_id,
        customer_id,
        
        -- Business fields
        upper(trim(order_status)) as order_status,
        total_amount,
        
        -- Dates
        cast(order_date as timestamp) as order_date,
        cast(last_updated as timestamp) as last_updated_at,
        coalesce(cast(requested_ship_date as timestamp), 
                 cast(order_date as timestamp) + interval '7' day) as requested_ship_date,
        
        -- Additional fields
        coalesce(order_type, 'STANDARD') as order_type,
        coalesce(priority_code, 'NORMAL') as priority_code,
        coalesce(ship_to_address_id, customer_id) as ship_to_address_id,
        
        -- Metadata
        _sdc_extracted_at,
        _sdc_batched_at,
        _sdc_received_at,
        _sdc_table_version,
        
        -- Calculated fields
        case 
            when order_status in ('NEW', 'CONFIRMED') then 'Open'
            when order_status = 'IN_PROGRESS' then 'Processing'
            when order_status = 'COMPLETED' then 'Completed'
            when order_status = 'CANCELLED' then 'Cancelled'
            else 'Unknown'
        end as order_status_group,
        
        -- Business calculations
        extract(day from (current_timestamp - cast(order_date as timestamp))) as days_since_order,
        
        -- Data quality flags
        case when total_amount <= 0 then true else false end as has_invalid_amount,
        case when order_status not in ({{ "'" + "', '".join(var('valid_order_statuses')) + "'" }}) 
             then true else false end as has_invalid_status
        
    from order_headers
),

order_detail_aggregated as (
    select
        order_id,
        count(*) as line_count,
        sum(quantity_ordered) as total_quantity_ordered,
        sum(line_total) as calculated_total_amount,
        avg(unit_price) as avg_unit_price,
        min(unit_price) as min_unit_price,
        max(unit_price) as max_unit_price,
        count(distinct item_id) as unique_item_count
        
    from order_details
    group by order_id
),

final as (
    select
        h.*,
        
        -- Order details aggregations
        coalesce(d.line_count, 0) as line_count,
        coalesce(d.total_quantity_ordered, 0) as total_quantity_ordered,
        coalesce(d.calculated_total_amount, 0) as calculated_total_amount,
        coalesce(d.avg_unit_price, 0) as avg_unit_price,
        coalesce(d.min_unit_price, 0) as min_unit_price,
        coalesce(d.max_unit_price, 0) as max_unit_price,
        coalesce(d.unique_item_count, 0) as unique_item_count,
        
        -- Data quality checks
        case when abs(h.total_amount - coalesce(d.calculated_total_amount, 0)) > 0.01 
             then true else false end as has_amount_variance,
             
        -- Business classifications
        case 
            when h.total_amount < 100 then 'Small'
            when h.total_amount < 1000 then 'Medium'
            when h.total_amount < 10000 then 'Large'
            else 'Enterprise'
        end as order_size_category,
        
        case
            when h.priority_code = 'URGENT' then 1
            when h.priority_code = 'HIGH' then 2
            when h.priority_code = 'NORMAL' then 3
            else 4
        end as priority_rank,
        
        -- Overall data quality score
        case 
            when h.has_invalid_amount or h.has_invalid_status or 
                 (abs(h.total_amount - coalesce(d.calculated_total_amount, 0)) > 0.01) then 'Poor'
            when d.line_count = 0 then 'Poor'
            when h.order_type = 'STANDARD' and d.line_count > 0 then 'Excellent'
            else 'Good'
        end as data_quality_score
        
    from order_header_cleaned h
    left join order_detail_aggregated d on h.order_id = d.order_id
)

select * from final