-- Grain: one row per order line item.
--
-- Joins to dim_customers as of the order date (point-in-time SCD2 join).
-- Note that dbt snapshots only start recording history from the first time
-- `dbt snapshot` is run, so historical orders placed before the warehouse
-- ever existed cannot be matched by `order_date >= valid_from`. Instead we
-- pick, for each line item, the customer version with the SMALLEST
-- valid_to that still exceeds the order date -- i.e. the earliest customer
-- state that was current at (or, for pre-warehouse history, "eventually
-- became true as of") that date. This correctly attributes an order to a
-- customer's pre-change attributes (e.g. their loyalty tier before an
-- upgrade) rather than always using their current attributes.

with items as (
    select * from {{ ref('int_order_items_priced') }}
),

customers as (
    select * from {{ ref('dim_customers') }}
),

matched as (
    select
        i.order_item_id,
        i.order_id,
        i.customer_id,
        i.product_id,
        i.store_id,
        i.order_date,
        i.channel,
        i.order_status,
        i.is_completed,
        i.quantity,
        i.unit_price,
        i.discount_rate,
        i.gross_revenue,
        i.discount_amount,
        i.net_revenue,
        c.customer_sk,
        row_number() over (
            partition by i.order_item_id
            order by c.valid_to asc
        ) as version_rank
    from items i
    inner join customers c
        on i.customer_id = c.customer_id
        and i.order_date < c.valid_to
)

select
    order_item_id,
    order_id,
    customer_sk,
    customer_id,
    product_id,
    store_id,
    order_date,
    channel,
    order_status,
    is_completed,
    quantity,
    unit_price,
    discount_rate,
    gross_revenue,
    discount_amount,
    net_revenue
from matched
where version_rank = 1
