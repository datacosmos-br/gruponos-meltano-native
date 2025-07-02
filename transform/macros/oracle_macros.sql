-- Oracle-specific macros for WMS data transformations

{% macro oracle_analyze_table() %}
  {% if target.type == 'oracle' %}
    {% set analyze_sql %}
      begin
        dbms_stats.gather_table_stats(
          ownname => '{{ this.schema }}',
          tabname => '{{ this.identifier }}',
          estimate_percent => dbms_stats.auto_sample_size,
          method_opt => 'for all columns size auto',
          degree => dbms_stats.auto_degree,
          cascade => true
        );
      end;
    {% endset %}
    {{ return(analyze_sql) }}
  {% endif %}
{% endmacro %}

{% macro oracle_create_index(table_ref, columns, index_name=none, unique=false) %}
  {% if target.type == 'oracle' %}
    {% set index_name = index_name or 'idx_' ~ table_ref.identifier ~ '_' ~ columns|join('_') %}
    {% set unique_sql = 'unique ' if unique else '' %}
    
    {% set create_index_sql %}
      create {{ unique_sql }}index {{ index_name }}
      on {{ table_ref }} ({{ columns|join(', ') }})
      tablespace users
      storage (initial 1m next 1m pctincrease 0)
      parallel 4
      nologging
    {% endset %}
    
    {{ return(create_index_sql) }}
  {% endif %}
{% endmacro %}

{% macro oracle_partition_by_date(date_column, partition_type='monthly') %}
  {% if target.type == 'oracle' %}
    {% if partition_type == 'monthly' %}
      {% set partition_sql %}
        partition by range ({{ date_column }}) 
        interval (numtoyminterval(1, 'MONTH'))
        (partition p_initial values less than (date '2025-01-01'))
      {% endset %}
    {% elif partition_type == 'daily' %}
      {% set partition_sql %}
        partition by range ({{ date_column }}) 
        interval (numtodsinterval(1, 'DAY'))
        (partition p_initial values less than (date '2025-01-01'))
      {% endset %}
    {% endif %}
    
    {{ return(partition_sql) }}
  {% endif %}
{% endmacro %}

{% macro oracle_merge_statement(target_table, source_table, merge_keys, update_columns) %}
  {% if target.type == 'oracle' %}
    {% set merge_sql %}
      merge into {{ target_table }} target
      using {{ source_table }} source
      on ({{ merge_keys|join(' and ') }})
      when matched then
        update set {{ update_columns|join(', ') }}
      when not matched then
        insert ({{ (merge_keys + update_columns)|map('regex_replace', '^target\.', '')|join(', ') }})
        values ({{ (merge_keys + update_columns)|map('regex_replace', '^target\.', 'source.')|join(', ') }})
    {% endset %}
    
    {{ return(merge_sql) }}
  {% endif %}
{% endmacro %}

{% macro oracle_bulk_insert(table_ref, batch_size=10000) %}
  {% if target.type == 'oracle' %}
    {% set bulk_hint = '/*+ append parallel(' ~ table_ref.identifier ~ ', 4) */' %}
    {{ return(bulk_hint) }}
  {% endif %}
{% endmacro %}

{% macro oracle_date_spine(start_date, end_date, date_part='day') %}
  {% if target.type == 'oracle' %}
    {% set date_spine_sql %}
      with date_spine as (
        select 
          {{ start_date }} + level - 1 as date_day
        from dual
        connect by level <= ({{ end_date }} - {{ start_date }} + 1)
      )
      select 
        date_day,
        extract(year from date_day) as date_year,
        extract(month from date_day) as date_month,
        extract(day from date_day) as date_day_of_month,
        to_char(date_day, 'Day') as date_day_name,
        to_char(date_day, 'Month') as date_month_name,
        case when to_char(date_day, 'D') in ('1', '7') then 'Weekend' else 'Weekday' end as date_day_type
      from date_spine
    {% endset %}
    
    {{ return(date_spine_sql) }}
  {% endif %}
{% endmacro %}

{% macro oracle_lag_lead_analysis(table_ref, partition_by, order_by, value_column) %}
  {% if target.type == 'oracle' %}
    {% set lag_lead_sql %}
      lag({{ value_column }}, 1) over (partition by {{ partition_by|join(', ') }} order by {{ order_by }}) as previous_{{ value_column }},
      lead({{ value_column }}, 1) over (partition by {{ partition_by|join(', ') }} order by {{ order_by }}) as next_{{ value_column }},
      {{ value_column }} - lag({{ value_column }}, 1) over (partition by {{ partition_by|join(', ') }} order by {{ order_by }}) as {{ value_column }}_change,
      case 
        when {{ value_column }} > lag({{ value_column }}, 1) over (partition by {{ partition_by|join(', ') }} order by {{ order_by }}) then 'Increase'
        when {{ value_column }} < lag({{ value_column }}, 1) over (partition by {{ partition_by|join(', ') }} order by {{ order_by }}) then 'Decrease'
        when {{ value_column }} = lag({{ value_column }}, 1) over (partition by {{ partition_by|join(', ') }} order by {{ order_by }}) then 'No Change'
        else 'First Record'
      end as {{ value_column }}_trend
    {% endset %}
    
    {{ return(lag_lead_sql) }}
  {% endif %}
{% endmacro %}

{% macro oracle_running_totals(value_column, partition_by, order_by) %}
  {% if target.type == 'oracle' %}
    {% set running_total_sql %}
      sum({{ value_column }}) over (
        partition by {{ partition_by|join(', ') }} 
        order by {{ order_by }} 
        rows between unbounded preceding and current row
      ) as {{ value_column }}_running_total,
      avg({{ value_column }}) over (
        partition by {{ partition_by|join(', ') }} 
        order by {{ order_by }} 
        rows between unbounded preceding and current row
      ) as {{ value_column }}_running_avg,
      count({{ value_column }}) over (
        partition by {{ partition_by|join(', ') }} 
        order by {{ order_by }} 
        rows between unbounded preceding and current row
      ) as {{ value_column }}_running_count
    {% endset %}
    
    {{ return(running_total_sql) }}
  {% endif %}
{% endmacro %}

{% macro oracle_percentile_analysis(value_column, partition_by=none) %}
  {% if target.type == 'oracle' %}
    {% set partition_clause = 'partition by ' ~ partition_by|join(', ') if partition_by else '' %}
    
    {% set percentile_sql %}
      percentile_cont(0.25) within group (order by {{ value_column }}) over ({{ partition_clause }}) as {{ value_column }}_p25,
      percentile_cont(0.5) within group (order by {{ value_column }}) over ({{ partition_clause }}) as {{ value_column }}_p50,
      percentile_cont(0.75) within group (order by {{ value_column }}) over ({{ partition_clause }}) as {{ value_column }}_p75,
      percentile_cont(0.9) within group (order by {{ value_column }}) over ({{ partition_clause }}) as {{ value_column }}_p90,
      percent_rank() over ({{ partition_clause }} order by {{ value_column }}) as {{ value_column }}_percent_rank
    {% endset %}
    
    {{ return(percentile_sql) }}
  {% endif %}
{% endmacro %}

{% macro oracle_data_quality_checks(table_ref, columns) %}
  {% if target.type == 'oracle' %}
    {% set quality_sql %}
      select
        '{{ table_ref }}' as table_name,
        count(*) as total_rows,
        {% for column in columns %}
        count({{ column }}) as {{ column }}_non_null_count,
        count(*) - count({{ column }}) as {{ column }}_null_count,
        (count(*) - count({{ column }})) * 100.0 / count(*) as {{ column }}_null_percentage,
        count(distinct {{ column }}) as {{ column }}_distinct_count,
        {% endfor %}
        current_timestamp as check_timestamp
      from {{ table_ref }}
    {% endset %}
    
    {{ return(quality_sql) }}
  {% endif %}
{% endmacro %}