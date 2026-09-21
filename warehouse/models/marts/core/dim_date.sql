-- Date spine covering the full range of order activity, generated with
-- DuckDB's generate_series rather than a seed/package dependency.

with bounds as (
    select
        min(order_date) as min_date,
        max(order_date) as max_date
    from {{ ref('stg_orders') }}
),

spine as (
    select unnest(generate_series(
        (select min_date from bounds),
        (select max_date from bounds),
        interval 1 day
    ))::date as date_day
)

select
    date_day,
    year(date_day) as year,
    quarter(date_day) as quarter,
    month(date_day) as month,
    strftime(date_day, '%Y-%m') as year_month,
    day(date_day) as day_of_month,
    dayofweek(date_day) as day_of_week,
    dayname(date_day) as day_name,
    dayofweek(date_day) in (0, 6) as is_weekend
from spine
