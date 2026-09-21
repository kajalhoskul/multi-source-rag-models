-- SCD Type 2 customer dimension, built directly from the dbt snapshot.
-- Each row is a version of a customer valid for [valid_from, valid_to).

with snapshot as (
    select * from {{ ref('customers_snapshot') }}
)

select
    dbt_scd_id as customer_sk,
    customer_id,
    full_name,
    email,
    city,
    state,
    loyalty_tier,
    signup_date,
    dbt_valid_from as valid_from,
    coalesce(dbt_valid_to, timestamp '9999-12-31') as valid_to,
    dbt_valid_to is null as is_current
from snapshot
