with source as (
    select * from {{ source('raw', 'products') }}
)

select
    product_id,
    product_name,
    category,
    {{ cents_to_dollars('unit_price_cents') }} as unit_price,
    cast(is_active as boolean) as is_active
from source
