select
    product_id as product_sk,
    product_id,
    product_name,
    category,
    unit_price,
    is_active
from {{ ref('stg_products') }}
