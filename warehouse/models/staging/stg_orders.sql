select
    order_id,
    customer_id,
    store_id,
    cast(order_date as date) as order_date,
    channel,
    order_status,
    order_status = 'completed' as is_completed
from {{ source('raw', 'orders') }}
