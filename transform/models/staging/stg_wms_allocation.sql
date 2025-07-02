{{ config(
    materialized='view',
    tags=['staging', 'allocation']
) }}

with source_data as (
    select * from {{ source('wms_raw', 'allocation') }}
),

cleaned_data as (
    select
        -- Primary keys
        allocation_id,
        order_id,
        item_id,
        location_id,
        
        -- Business fields
        quantity_allocated,
        upper(trim(allocation_status)) as allocation_status,
        
        -- Dates and timestamps
        cast(last_updated as timestamp) as last_updated_at,
        cast(created_date as timestamp) as created_at,
        
        -- Additional fields for tracking
        coalesce(allocated_by_user, 'SYSTEM') as allocated_by_user,
        coalesce(priority_level, 1) as priority_level,
        
        -- Metadata columns from Singer
        _sdc_extracted_at,
        _sdc_batched_at,
        _sdc_received_at,
        _sdc_table_version,
        
        -- Calculated fields
        case 
            when allocation_status = 'ALLOCATED' then 'Active'
            when allocation_status = 'RESERVED' then 'Active'
            when allocation_status = 'PICKED' then 'Fulfilled'
            when allocation_status = 'SHIPPED' then 'Fulfilled'
            else 'Unknown'
        end as allocation_status_group,
        
        -- Data quality flags
        case when quantity_allocated <= 0 then true else false end as has_invalid_quantity,
        case when allocation_status not in ({{ "'" + "', '".join(var('valid_allocation_statuses')) + "'" }}) 
             then true else false end as has_invalid_status
        
    from source_data
),

final as (
    select
        *,
        -- Add row quality score
        case 
            when has_invalid_quantity or has_invalid_status then 'Poor'
            when allocated_by_user = 'SYSTEM' then 'Good'
            else 'Excellent'
        end as data_quality_score
        
    from cleaned_data
)

select * from final