with source as (
    select * from {{ source('raw', 'customers') }}
)

select
    customer_id,
    full_name,
    email,
    city,
    state,
    loyalty_tier,
    cast(signup_date as date) as signup_date,
    cast(extracted_at as timestamp) as extracted_at
from source
