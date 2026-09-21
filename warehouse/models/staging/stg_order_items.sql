select
    order_item_id,
    order_id,
    product_id,
    quantity,
    {{ cents_to_dollars('unit_price_cents') }} as unit_price,
    discount_pct / 100.0 as discount_rate
from {{ source('raw', 'order_items') }}
