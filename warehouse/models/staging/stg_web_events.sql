select
    event_id,
    customer_id,
    product_id,
    event_type,
    cast(event_ts as timestamp) as event_ts
from {{ source('raw', 'web_events') }}
