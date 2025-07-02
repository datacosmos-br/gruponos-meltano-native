{{ config(
    materialized='table',
    tags=['mart', 'dimension', 'items'],
    post_hook="{{ oracle_analyze_table() }}"
) }}

with item_master as (
    select * from {{ source('wms_raw', 'item_master') }}
    where is_active = 'Y'
),

item_usage_stats as (
    select
        item_id,
        count(distinct order_id) as orders_count_last_90_days,
        sum(quantity_ordered) as total_quantity_ordered_last_90_days,
        avg(unit_price) as avg_unit_price_last_90_days,
        max(order_date) as last_order_date
    from {{ ref('stg_wms_orders') }} o
    join {{ source('wms_raw', 'order_dtl') }} d on o.order_id = d.order_id
    where o.order_date >= current_date - 90
    group by item_id
),

item_allocation_stats as (
    select
        item_id,
        count(*) as allocations_count_last_90_days,
        sum(quantity_allocated) as total_quantity_allocated_last_90_days,
        count(case when allocation_status = 'SHIPPED' end) as shipped_allocations_count,
        avg(case when allocation_status = 'SHIPPED' then 
            extract(hour from (last_updated_at - created_at)) * 3600 + 
            extract(minute from (last_updated_at - created_at)) * 60 + 
            extract(second from (last_updated_at - created_at))
        end) as avg_fulfillment_time_seconds
    from {{ ref('stg_wms_allocation') }}
    where created_at >= current_date - 90
    group by item_id
),

item_enriched as (
    select
        i.item_id,
        i.item_code,
        i.item_description,
        i.item_category,
        i.unit_of_measure,
        i.standard_cost,
        i.is_active,
        
        -- Usage metrics
        coalesce(u.orders_count_last_90_days, 0) as orders_count_last_90_days,
        coalesce(u.total_quantity_ordered_last_90_days, 0) as total_quantity_ordered_last_90_days,
        coalesce(u.avg_unit_price_last_90_days, i.standard_cost) as avg_unit_price_last_90_days,
        u.last_order_date,
        
        -- Allocation metrics
        coalesce(a.allocations_count_last_90_days, 0) as allocations_count_last_90_days,
        coalesce(a.total_quantity_allocated_last_90_days, 0) as total_quantity_allocated_last_90_days,
        coalesce(a.shipped_allocations_count, 0) as shipped_allocations_count,
        a.avg_fulfillment_time_seconds,
        
        -- Business classifications
        case
            when coalesce(u.orders_count_last_90_days, 0) = 0 then 'No Activity'
            when u.orders_count_last_90_days >= 30 then 'High Volume'
            when u.orders_count_last_90_days >= 10 then 'Medium Volume'
            when u.orders_count_last_90_days >= 1 then 'Low Volume'
            else 'No Activity'
        end as volume_category,
        
        case
            when i.standard_cost < 10 then 'Low Value'
            when i.standard_cost < 100 then 'Medium Value'
            when i.standard_cost < 1000 then 'High Value'
            else 'Premium Value'
        end as value_category,
        
        case
            when coalesce(a.shipped_allocations_count, 0) = 0 then null
            when a.shipped_allocations_count * 100.0 / a.allocations_count_last_90_days >= 95 then 'Excellent'
            when a.shipped_allocations_count * 100.0 / a.allocations_count_last_90_days >= 85 then 'Good'
            when a.shipped_allocations_count * 100.0 / a.allocations_count_last_90_days >= 70 then 'Average'
            else 'Poor'
        end as fulfillment_performance,
        
        -- Velocity metrics
        case
            when u.last_order_date >= current_date - 7 then 'Fast Moving'
            when u.last_order_date >= current_date - 30 then 'Regular Moving'
            when u.last_order_date >= current_date - 90 then 'Slow Moving'
            else 'Dormant'
        end as velocity_category,
        
        -- Metadata
        current_timestamp as dim_created_at,
        current_timestamp as dim_updated_at,
        
        -- Surrogate key
        {{ dbt_utils.surrogate_key(['item_id']) }} as item_key
        
    from item_master i
    left join item_usage_stats u on i.item_id = u.item_id
    left join item_allocation_stats a on i.item_id = a.item_id
)

select * from item_enriched