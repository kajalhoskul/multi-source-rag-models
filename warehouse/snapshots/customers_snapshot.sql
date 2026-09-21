{% snapshot customers_snapshot %}

{{
    config(
        unique_key='customer_id',
        strategy='check',
        check_cols=['loyalty_tier', 'city', 'state'],
    )
}}

select
    customer_id,
    full_name,
    email,
    city,
    state,
    loyalty_tier,
    signup_date
from {{ source('raw', 'customers') }}

{% endsnapshot %}
