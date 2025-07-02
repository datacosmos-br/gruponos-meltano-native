{{ config(
    materialized='table',
    tags=['mart', 'fact', 'inventory', 'movement'],
    post_hook="{{ oracle_analyze_table() }}"
) }}

with allocation_movements as (
    select
        allocation_id as transaction_id,
        'ALLOCATION' as movement_type,
        item_id,
        location_id,
        order_id,
        quantity_allocated as quantity,
        'OUTBOUND' as direction,
        allocation_status,
        created_at as movement_date,
        last_updated_at,
        allocated_by_user as performed_by,
        
        -- Business context
        case
            when allocation_status = 'ALLOCATED' then 'RESERVED'
            when allocation_status = 'PICKED' then 'PICKED'
            when allocation_status = 'SHIPPED' then 'SHIPPED' 
            else 'OTHER'
        end as movement_status,
        
        priority_level,
        data_quality_score
        
    from {{ ref('stg_wms_allocation') }}
),

-- Generate inbound movements (simulated from order receipts)
-- In a real scenario, this would come from receiving/putaway data
simulated_inbound as (
    select
        'RCV_' || row_number() over (order by o.order_date) as transaction_id,
        'RECEIPT' as movement_type,
        d.item_id,
        'RECEIVING_DOCK' as location_id,
        o.order_id,
        d.quantity_ordered as quantity,
        'INBOUND' as direction,
        'COMPLETED' as allocation_status,
        o.order_date - interval '7' day as movement_date,  -- Simulate receipt 7 days before order
        o.order_date - interval '7' day as last_updated_at,
        'RECEIVING_SYSTEM' as performed_by,
        'RECEIVED' as movement_status,
        1 as priority_level,
        'Good' as data_quality_score
        
    from {{ ref('stg_wms_orders') }} o
    join {{ source('wms_raw', 'order_dtl') }} d on o.order_id = d.order_id
    where o.order_status in ('COMPLETED', 'SHIPPED')
      and o.order_date >= current_date - 90  -- Last 90 days only
),

combined_movements as (
    select * from allocation_movements
    union all
    select * from simulated_inbound
),

movement_analysis as (
    select
        m.*,
        
        -- Time dimensions
        extract(year from movement_date) as movement_year,
        extract(month from movement_date) as movement_month,
        extract(day from movement_date) as movement_day,
        extract(hour from movement_date) as movement_hour,
        extract(dow from movement_date) as movement_day_of_week,
        to_char(movement_date, 'YYYY-MM') as movement_year_month,
        to_char(movement_date, 'YYYY-"W"WW') as movement_year_week,
        
        -- Movement classifications
        case
            when extract(hour from movement_date) between 6 and 18 then 'BUSINESS_HOURS'
            else 'AFTER_HOURS'
        end as time_classification,
        
        case
            when extract(dow from movement_date) in (0, 6) then 'WEEKEND'  -- Sunday = 0, Saturday = 6
            else 'WEEKDAY'
        end as day_type,
        
        -- Quantity classifications
        case
            when quantity <= 10 then 'SMALL'
            when quantity <= 100 then 'MEDIUM'
            when quantity <= 1000 then 'LARGE'
            else 'BULK'
        end as quantity_tier,
        
        -- Performance metrics
        extract(hour from (last_updated_at - movement_date)) * 3600 + 
        extract(minute from (last_updated_at - movement_date)) * 60 + 
        extract(second from (last_updated_at - movement_date)) as processing_time_seconds,
        
        -- Running calculations by item
        {{ oracle_running_totals('quantity', ['item_id'], 'movement_date') }},
        
        -- Lag/Lead analysis for velocity
        {{ oracle_lag_lead_analysis('combined_movements', ['item_id'], 'movement_date', 'quantity') }},
        
        -- Percentile analysis for benchmarking
        {{ oracle_percentile_analysis('quantity', ['item_id', 'movement_type']) }}
        
    from combined_movements m
),

item_velocity_context as (
    select
        item_id,
        movement_type,
        count(*) as total_movements_90_days,
        sum(quantity) as total_quantity_90_days,
        avg(quantity) as avg_quantity_per_movement,
        
        -- Velocity calculations
        sum(case when direction = 'OUTBOUND' then quantity else 0 end) as total_outbound_qty,
        sum(case when direction = 'INBOUND' then quantity else 0 end) as total_inbound_qty,
        
        -- Frequency analysis
        count(*) * 1.0 / 90 as avg_movements_per_day,
        sum(quantity) * 1.0 / 90 as avg_quantity_per_day,
        
        -- Performance metrics
        avg(processing_time_seconds) as avg_processing_time_seconds,
        percentile_cont(0.5) within group (order by processing_time_seconds) as median_processing_time_seconds
        
    from movement_analysis
    where movement_date >= current_date - 90
    group by item_id, movement_type
),

final as (
    select
        m.*,
        
        -- Context from velocity analysis
        v.total_movements_90_days,
        v.total_quantity_90_days,
        v.avg_quantity_per_movement,
        v.total_outbound_qty,
        v.total_inbound_qty,
        v.avg_movements_per_day,
        v.avg_quantity_per_day,
        v.avg_processing_time_seconds as item_avg_processing_time,
        v.median_processing_time_seconds as item_median_processing_time,
        
        -- Derived metrics
        case
            when v.total_inbound_qty > 0 then 
                round((v.total_outbound_qty * 100.0 / v.total_inbound_qty), 2)
            else 0
        end as inventory_turnover_pct,
        
        case
            when v.avg_movements_per_day >= 5 then 'HIGH_VELOCITY'
            when v.avg_movements_per_day >= 1 then 'MEDIUM_VELOCITY'
            when v.avg_movements_per_day >= 0.1 then 'LOW_VELOCITY'
            else 'DORMANT'
        end as item_velocity_category,
        
        case
            when m.processing_time_seconds <= v.median_processing_time_seconds then 'FAST'
            when m.processing_time_seconds <= v.avg_processing_time_seconds then 'AVERAGE'
            else 'SLOW'
        end as processing_speed_vs_item_avg,
        
        -- Business impact scoring
        case
            when m.direction = 'OUTBOUND' and m.movement_status = 'SHIPPED' and 
                 m.processing_time_seconds <= 3600 then 100  -- Excellent
            when m.direction = 'OUTBOUND' and m.movement_status = 'SHIPPED' then 80   -- Good
            when m.direction = 'OUTBOUND' and m.movement_status = 'PICKED' then 60    -- In Progress
            when m.direction = 'INBOUND' and m.movement_status = 'RECEIVED' then 90   -- Good inbound
            else 40  -- Poor or incomplete
        end as business_impact_score,
        
        -- Surrogate keys
        {{ dbt_utils.surrogate_key(['transaction_id']) }} as movement_key,
        {{ dbt_utils.surrogate_key(['movement_date']) }} as date_key,
        {{ dbt_utils.surrogate_key(['item_id']) }} as item_key,
        {{ dbt_utils.surrogate_key(['location_id']) }} as location_key,
        
        -- Metadata
        current_timestamp as fact_created_at,
        current_timestamp as fact_updated_at
        
    from movement_analysis m
    left join item_velocity_context v on m.item_id = v.item_id and m.movement_type = v.movement_type
)

select * from final