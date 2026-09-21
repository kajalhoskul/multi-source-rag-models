select
    store_id as store_sk,
    store_id,
    store_name,
    region
from {{ ref('stg_stores') }}
