{{ config(
    materialized='view',
    tags=['intermediate', 'allocation', 'performance']
) }}

with allocation_base as (
    select * from {{ ref('stg_wms_allocation') }}
),

allocation_metrics as (
    select
        allocation_id,
        order_id,
        item_id,
        location_id,
        allocation_status,
        allocation_status_group,
        quantity_allocated,
        created_at,
        last_updated_at,
        allocated_by_user,
        priority_level,
        
        -- Performance calculations
        extract(hour from (last_updated_at - created_at)) * 3600 + 
        extract(minute from (last_updated_at - created_at)) * 60 + 
        extract(second from (last_updated_at - created_at)) as processing_time_seconds,
        
        case
            when allocation_status = 'SHIPPED' then 
                extract(hour from (last_updated_at - created_at)) * 3600 + 
                extract(minute from (last_updated_at - created_at)) * 60 + 
                extract(second from (last_updated_at - created_at))
            else null
        end as fulfillment_time_seconds,
        
        -- Business day calculations (assuming weekdays only)
        case 
            when to_char(created_at, 'D') in ('1', '7') then 'Weekend'  -- Sunday = 1, Saturday = 7
            else 'Weekday'
        end as created_day_type,
        
        case 
            when extract(hour from created_at) between 6 and 18 then 'Business Hours'
            else 'After Hours'
        end as created_time_type,
        
        -- Volume classifications
        case
            when quantity_allocated <= 10 then 'Small'
            when quantity_allocated <= 100 then 'Medium'
            when quantity_allocated <= 1000 then 'Large'
            else 'Bulk'
        end as quantity_tier,
        
        data_quality_score
        
from allocation_base
),

location_performance as (
    select
        location_id,
        count(*) as total_allocations,
        avg(processing_time_seconds) as avg_processing_time_seconds,
        percentile_cont(0.5) within group (order by processing_time_seconds) as median_processing_time_seconds,
        avg(case when allocation_status = 'SHIPPED' then fulfillment_time_seconds end) as avg_fulfillment_time_seconds,
        
        -- Efficiency metrics
        count(case when allocation_status = 'SHIPPED' end) * 100.0 / count(*) as fulfillment_rate_pct,
        count(case when processing_time_seconds <= 3600 end) * 100.0 / count(*) as within_1hour_rate_pct,
        
        -- Quality metrics
        count(case when data_quality_score = 'Excellent' end) * 100.0 / count(*) as excellent_quality_rate_pct
        
from allocation_metrics
    group by location_id
),

user_performance as (
    select
        allocated_by_user,
        count(*) as total_allocations,
        avg(processing_time_seconds) as avg_processing_time_seconds,
        count(case when allocation_status = 'SHIPPED' end) * 100.0 / count(*) as fulfillment_rate_pct,
        count(case when data_quality_score = 'Excellent' end) * 100.0 / count(*) as excellent_quality_rate_pct,
        
        -- Productivity metrics
        count(*) * 1.0 / count(distinct date_trunc('day', created_at)) as avg_allocations_per_day,
        
        -- Specialization analysis
        count(distinct item_id) as unique_items_handled,
        count(distinct location_id) as unique_locations_used
        
from allocation_metrics
    where allocated_by_user != 'SYSTEM'
    group by allocated_by_user
),

final as (
    select
        a.*,
        
        -- Location performance context
        l.avg_processing_time_seconds as location_avg_processing_time,
        l.fulfillment_rate_pct as location_fulfillment_rate_pct,
        l.within_1hour_rate_pct as location_within_1hour_rate_pct,
        
        -- User performance context (only for non-system allocations)
        case when a.allocated_by_user != 'SYSTEM' then u.avg_processing_time_seconds end as user_avg_processing_time,
        case when a.allocated_by_user != 'SYSTEM' then u.fulfillment_rate_pct end as user_fulfillment_rate_pct,
        case when a.allocated_by_user != 'SYSTEM' then u.avg_allocations_per_day end as user_avg_allocations_per_day,
        
        -- Performance indicators
        case 
            when a.processing_time_seconds <= l.median_processing_time_seconds then 'Above Average'
            when a.processing_time_seconds <= l.avg_processing_time_seconds then 'Average'
            else 'Below Average'
        end as processing_performance_vs_location,
        
        case
            when a.allocated_by_user != 'SYSTEM' and a.processing_time_seconds <= u.avg_processing_time_seconds then 'Above Personal Average'
            when a.allocated_by_user != 'SYSTEM' then 'Below Personal Average'
            else 'System Allocation'
        end as processing_performance_vs_user
        
from allocation_metrics a
    left join location_performance l on a.location_id = l.location_id
    left join user_performance u on a.allocated_by_user = u.allocated_by_user
)

select * from final
