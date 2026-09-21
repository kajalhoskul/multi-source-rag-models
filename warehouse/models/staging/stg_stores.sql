select
    store_id,
    store_name,
    region
from {{ source('raw', 'stores') }}
