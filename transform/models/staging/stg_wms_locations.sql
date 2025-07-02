{{ config(
    materialized='view',
    tags=['staging', 'master_data', 'locations']
) }}

with source_data as (
    select * from {{ source('wms_raw', 'location') }}
),

cleaned_data as (
    select
        -- Primary keys
        location_id,
        upper(trim(location_code)) as location_code,
        
        -- Business fields
        upper(trim(location_type)) as location_type,
        coalesce(zone_id, 'UNKNOWN') as zone_id,
        coalesce(aisle, '00') as aisle,
        coalesce(bay, '00') as bay,
        coalesce(level, '01') as level,
        upper(trim(is_active)) as is_active,
        
        -- Additional fields with defaults
        coalesce(capacity_volume, 0) as capacity_volume,
        coalesce(capacity_weight, 0) as capacity_weight,
        coalesce(current_volume, 0) as current_volume,
        coalesce(current_weight, 0) as current_weight,
        
        -- Location characteristics
        upper(trim(coalesce(temperature_zone, 'AMBIENT'))) as temperature_zone,
        upper(trim(coalesce(security_level, 'STANDARD'))) as security_level,
        coalesce(pick_sequence, 999999) as pick_sequence,
        
        -- Computed fields
        case
            when capacity_volume > 0 then 
                round((current_volume * 100.0 / capacity_volume), 2)
            else 0
        end as volume_utilization_pct,
        
        case
            when capacity_weight > 0 then 
                round((current_weight * 100.0 / capacity_weight), 2)
            else 0
        end as weight_utilization_pct,
        
        -- Zone and area calculations
        zone_id || '-' || aisle as zone_aisle,
        zone_id || '-' || aisle || '-' || bay as zone_aisle_bay,
        
        -- Location hierarchy
        case
            when location_type = 'PICK' then 1
            when location_type = 'FORWARD' then 2  
            when location_type = 'RESERVE' then 3
            when location_type = 'BULK' then 4
            when location_type = 'STAGE' then 5
            else 6
        end as type_priority,
        
        -- Metadata columns from Singer
        _sdc_extracted_at,
        _sdc_batched_at,
        _sdc_received_at,
        _sdc_table_version,
        
        -- Data quality flags
        case when length(trim(location_code)) < 3 then true else false end as has_invalid_code,
        case when location_type not in ('PICK', 'RESERVE', 'BULK', 'STAGE', 'FORWARD', 'DOCK', 'DAMAGED') 
             then true else false end as has_invalid_type,
        case when is_active not in ('Y', 'N') then true else false end as has_invalid_status,
        case when capacity_volume < 0 or capacity_weight < 0 then true else false end as has_invalid_capacity
        
    from source_data
),

location_efficiency as (
    select
        location_id,
        -- Calculate location efficiency score
        greatest(volume_utilization_pct, weight_utilization_pct) as max_utilization_pct,
        least(volume_utilization_pct, weight_utilization_pct) as min_utilization_pct,
        
        case
            when capacity_volume = 0 and capacity_weight = 0 then 'UNLIMITED'
            when greatest(volume_utilization_pct, weight_utilization_pct) > 95 then 'FULL'
            when greatest(volume_utilization_pct, weight_utilization_pct) > 80 then 'HIGH'
            when greatest(volume_utilization_pct, weight_utilization_pct) > 60 then 'MEDIUM'
            when greatest(volume_utilization_pct, weight_utilization_pct) > 20 then 'LOW'
            else 'EMPTY'
        end as utilization_status,
        
        case
            when location_type = 'PICK' and greatest(volume_utilization_pct, weight_utilization_pct) between 40 and 80 then 'OPTIMAL'
            when location_type = 'RESERVE' and greatest(volume_utilization_pct, weight_utilization_pct) between 60 and 90 then 'OPTIMAL'
            when location_type = 'BULK' and greatest(volume_utilization_pct, weight_utilization_pct) > 70 then 'OPTIMAL'
            else 'SUBOPTIMAL'
        end as efficiency_status
        
    from cleaned_data
),

final as (
    select
        c.*,
        e.max_utilization_pct,
        e.min_utilization_pct,
        e.utilization_status,
        e.efficiency_status,
        
        -- Overall data quality score
        case 
            when c.has_invalid_code or c.has_invalid_type or 
                 c.has_invalid_status or c.has_invalid_capacity then 'Poor'
            when c.zone_id = 'UNKNOWN' or c.aisle = '00' then 'Good'
            else 'Excellent'
        end as data_quality_score,
        
        -- Location characteristics for operations
        case
            when c.location_type = 'PICK' and c.pick_sequence <= 1000 then 'PRIME_PICK'
            when c.location_type = 'PICK' then 'STANDARD_PICK'
            when c.location_type = 'FORWARD' then 'FORWARD_RESERVE'
            when c.location_type = 'RESERVE' then 'BULK_RESERVE'
            when c.location_type = 'STAGE' then 'STAGING'
            else 'OTHER'
        end as operational_category,
        
        -- Accessibility rating
        case
            when c.level = '01' and c.location_type = 'PICK' then 'HIGH_ACCESS'
            when c.level in ('01', '02') and c.location_type in ('PICK', 'FORWARD') then 'MEDIUM_ACCESS'
            when c.location_type = 'BULK' then 'EQUIPMENT_ACCESS'
            else 'LOW_ACCESS'
        end as accessibility_rating
        
    from cleaned_data c
    join location_efficiency e on c.location_id = e.location_id
)

select * from final