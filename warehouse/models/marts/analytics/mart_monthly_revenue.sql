-- Monthly revenue trend with month-over-month growth, by channel.

with facts as (
    select * from {{ ref('fact_order_items') }}
    where is_completed
),

monthly as (
    select
        strftime(order_date, '%Y-%m') as year_month,
        channel,
        count(distinct order_id) as order_count,
        count(distinct customer_id) as customer_count,
        sum(net_revenue) as net_revenue
    from facts
    group by 1, 2
),

with_growth as (
    select
        *,
        round(net_revenue / nullif(customer_count, 0), 2) as revenue_per_customer,
        round(net_revenue / nullif(order_count, 0), 2) as avg_order_value,
        lag(net_revenue) over (partition by channel order by year_month) as prev_month_revenue
    from monthly
)

select
    year_month,
    channel,
    order_count,
    customer_count,
    net_revenue,
    avg_order_value,
    revenue_per_customer,
    prev_month_revenue,
    round(
        100.0 * (net_revenue - prev_month_revenue) / nullif(prev_month_revenue, 0), 1
    ) as mom_growth_pct
from with_growth
order by year_month, channel
