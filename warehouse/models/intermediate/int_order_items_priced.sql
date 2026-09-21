with order_items as (
    select * from {{ ref('stg_order_items') }}
),

orders as (
    select * from {{ ref('stg_orders') }}
),

priced as (
    select
        oi.order_item_id,
        oi.order_id,
        oi.product_id,
        o.customer_id,
        o.store_id,
        o.order_date,
        o.channel,
        o.order_status,
        o.is_completed,
        oi.quantity,
        oi.unit_price,
        oi.discount_rate,
        round(oi.quantity * oi.unit_price, 2) as gross_revenue,
        round(oi.quantity * oi.unit_price * oi.discount_rate, 2) as discount_amount,
        round(oi.quantity * oi.unit_price * (1 - oi.discount_rate), 2) as net_revenue
    from order_items oi
    inner join orders o on oi.order_id = o.order_id
)

select * from priced
