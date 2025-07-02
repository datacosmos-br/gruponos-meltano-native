{{ config(
    materialized='view',
    tags=['staging', 'master_data', 'items']
) }}

with source_data as (
    select * from {{ source('wms_raw', 'item_master') }}
),

cleaned_data as (
    select
        -- Primary keys
        item_id,
        upper(trim(item_code)) as item_code,
        
        -- Business fields
        trim(item_description) as item_description,
        upper(trim(coalesce(item_category, 'UNKNOWN'))) as item_category,
        upper(trim(unit_of_measure)) as unit_of_measure,
        standard_cost,
        upper(trim(is_active)) as is_active,
        
        -- Additional fields with defaults
        coalesce(item_weight, 0) as item_weight,
        coalesce(item_volume, 0) as item_volume,
        upper(trim(coalesce(storage_type, 'STANDARD'))) as storage_type,
        coalesce(shelf_life_days, 0) as shelf_life_days,
        upper(trim(coalesce(hazmat_class, 'NONE'))) as hazmat_class,
        
        -- Computed fields
        case 
            when item_description like '%PERISHABLE%' or shelf_life_days > 0 then 'Y'
            else 'N'
        end as is_perishable,
        
        case
            when hazmat_class != 'NONE' then 'Y'
            else 'N'
        end as is_hazmat,
        
        case
            when item_weight > 50 or item_volume > 1000 then 'OVERSIZED'
            when item_weight > 20 or item_volume > 500 then 'LARGE'
            when item_weight > 5 or item_volume > 100 then 'MEDIUM'
            else 'SMALL'
        end as size_category,
        
        -- Value categorization
        case
            when standard_cost < 10 then 'LOW_VALUE'
            when standard_cost < 100 then 'MEDIUM_VALUE'
            when standard_cost < 1000 then 'HIGH_VALUE'
            else 'PREMIUM_VALUE'
        end as value_category,
        
        -- Metadata columns from Singer
        _sdc_extracted_at,
        _sdc_batched_at,
        _sdc_received_at,
        _sdc_table_version,
        
        -- Data quality flags
        case when length(trim(item_code)) < 3 then true else false end as has_invalid_code,
        case when length(trim(item_description)) < 5 then true else false end as has_invalid_description,
        case when standard_cost < 0 then true else false end as has_invalid_cost,
        case when is_active not in ('Y', 'N') then true else false end as has_invalid_status
        
    from source_data
),

final as (
    select
        *,
        -- Data quality score
        case 
            when has_invalid_code or has_invalid_description or 
                 has_invalid_cost or has_invalid_status then 'Poor'
            when item_category = 'UNKNOWN' or storage_type = 'STANDARD' then 'Good'
            else 'Excellent'
        end as data_quality_score,
        
        -- Business classifications
        case
            when is_perishable = 'Y' and is_hazmat = 'Y' then 'SPECIAL_HANDLING'
            when is_perishable = 'Y' then 'PERISHABLE'
            when is_hazmat = 'Y' then 'HAZMAT'
            when size_category = 'OVERSIZED' then 'OVERSIZED'
            else 'STANDARD'
        end as handling_classification
        
    from cleaned_data
)

select * from final