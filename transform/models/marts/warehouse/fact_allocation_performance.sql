{{ config(
    materialized='table',
    tags=['mart', 'fact', 'allocation', 'performance'],
    post_hook="{{ oracle_analyze_table() }}"
) }}

with allocation_performance as (
    select * from {{ ref('int_allocation_performance') }}
),

daily_allocation_summary as (
    select
        date_trunc('day', created_at) as allocation_date,
        location_id,
        item_id,
        allocated_by_user,
        allocation_status_group,
        quantity_tier,
        created_day_type,
        created_time_type,
        
        -- Counts and totals
        count(*) as total_allocations,
        sum(quantity_allocated) as total_quantity_allocated,
        count(distinct order_id) as unique_orders_count,
        
        -- Performance metrics
        avg(processing_time_seconds) as avg_processing_time_seconds,
        percentile_cont(0.5) within group (order by processing_time_seconds) as median_processing_time_seconds,
        min(processing_time_seconds) as min_processing_time_seconds,
        max(processing_time_seconds) as max_processing_time_seconds,
        
        -- Fulfillment metrics
        count(case when allocation_status = 'SHIPPED' end) as shipped_count,
        count(case when allocation_status = 'SHIPPED' end) * 100.0 / count(*) as fulfillment_rate_pct,
        avg(case when fulfillment_time_seconds is not null then fulfillment_time_seconds end) as avg_fulfillment_time_seconds,
        
        -- Quality metrics
        count(case when data_quality_score = 'Excellent' end) as excellent_quality_count,
        count(case when data_quality_score = 'Good' end) as good_quality_count,
        count(case when data_quality_score = 'Poor' end) as poor_quality_count,
        count(case when data_quality_score = 'Excellent' end) * 100.0 / count(*) as excellent_quality_rate_pct,
        
        -- Performance indicators
        count(case when processing_performance_vs_location = 'Above Average' end) as above_avg_location_performance_count,
        count(case when processing_performance_vs_user = 'Above Personal Average' end) as above_avg_user_performance_count,
        
        -- Priority analysis
        avg(priority_level) as avg_priority_level,
        count(case when priority_level = 1 end) as high_priority_count,
        
        -- Efficiency metrics
        count(case when processing_time_seconds <= 3600 end) as within_1hour_count,
        count(case when processing_time_seconds <= 1800 end) as within_30min_count,
        count(case when processing_time_seconds <= 3600 end) * 100.0 / count(*) as within_1hour_rate_pct,
        
        -- Metadata
        min(created_at) as first_allocation_time,
        max(last_updated_at) as last_allocation_update_time
        
from allocation_performance
    group by 
        date_trunc('day', created_at),
        location_id,
        item_id,
        allocated_by_user,
        allocation_status_group,
        quantity_tier,
        created_day_type,
        created_time_type
),

enriched_facts as (
    select
        f.*,
        
        -- Date attributes
        extract(year from f.allocation_date) as allocation_year,
        extract(month from f.allocation_date) as allocation_month,
        extract(day from f.allocation_date) as allocation_day,
        extract(dow from f.allocation_date) as allocation_day_of_week,
        to_char(f.allocation_date, 'YYYY-MM') as allocation_year_month,
        to_char(f.allocation_date, 'YYYY-"W"WW') as allocation_year_week,
        
        -- Performance categories
        case
            when f.fulfillment_rate_pct >= 95 then 'Excellent'
            when f.fulfillment_rate_pct >= 85 then 'Good'
            when f.fulfillment_rate_pct >= 70 then 'Average'
            else 'Poor'
        end as fulfillment_performance_category,
        
        case
            when f.within_1hour_rate_pct >= 90 then 'Excellent'
            when f.within_1hour_rate_pct >= 75 then 'Good'
            when f.within_1hour_rate_pct >= 50 then 'Average'
            else 'Poor'
        end as speed_performance_category,
        
        case
            when f.excellent_quality_rate_pct >= 95 then 'Excellent'
            when f.excellent_quality_rate_pct >= 85 then 'Good'
            when f.excellent_quality_rate_pct >= 70 then 'Average'
            else 'Poor'
        end as quality_performance_category,
        
        -- Business metrics
        f.total_quantity_allocated / nullif(f.total_allocations, 0) as avg_quantity_per_allocation,
        f.shipped_count / nullif(f.unique_orders_count, 0) as avg_shipped_per_order,
        
        -- Efficiency scores (0-100)
        least(100, f.fulfillment_rate_pct * 0.4 + f.within_1hour_rate_pct * 0.3 + f.excellent_quality_rate_pct * 0.3) as overall_efficiency_score,
        
        -- Surrogate keys for dimension lookups
        {{ dbt_utils.surrogate_key(['allocation_date', 'location_id', 'item_id', 'allocated_by_user']) }} as fact_key,
        {{ dbt_utils.surrogate_key(['allocation_date']) }} as date_key,
        {{ dbt_utils.surrogate_key(['location_id']) }} as location_key,
        {{ dbt_utils.surrogate_key(['item_id']) }} as item_key,
        
        -- Metadata
        current_timestamp as fact_created_at,
        current_timestamp as fact_updated_at
        
from daily_allocation_summary f
)

select * from enriched_facts
