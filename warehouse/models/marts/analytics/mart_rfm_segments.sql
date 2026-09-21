-- RFM (Recency, Frequency, Monetary) scoring and segmentation per customer.
-- Each dimension is scored 1 (worst) to 5 (best) using NTILE, then combined
-- into a named segment.

with facts as (
    select * from {{ ref('fact_order_items') }}
    where is_completed
),

as_of as (
    select max(order_date) as as_of_date from facts
),

customer_orders as (
    select
        customer_id,
        max(order_date) as last_order_date,
        count(distinct order_id) as frequency,
        sum(net_revenue) as monetary
    from facts
    group by 1
),

rfm_base as (
    select
        co.customer_id,
        date_diff('day', co.last_order_date, a.as_of_date) as recency_days,
        co.frequency,
        co.monetary
    from customer_orders co
    cross join as_of a
),

scored as (
    select
        customer_id,
        recency_days,
        frequency,
        monetary,
        -- lower recency_days is better, so invert the tile order
        6 - ntile(5) over (order by recency_days) as recency_score,
        ntile(5) over (order by frequency) as frequency_score,
        ntile(5) over (order by monetary) as monetary_score
    from rfm_base
)

select
    customer_id,
    recency_days,
    frequency,
    monetary,
    recency_score,
    frequency_score,
    monetary_score,
    (recency_score + frequency_score + monetary_score) as rfm_total_score,
    case
        when recency_score >= 4 and frequency_score >= 4 and monetary_score >= 4 then 'Champions'
        when recency_score >= 4 and frequency_score >= 3 then 'Loyal Customers'
        when recency_score >= 4 and frequency_score <= 2 then 'New / Promising'
        when recency_score between 2 and 3 and frequency_score >= 3 then 'At Risk'
        when recency_score <= 2 and frequency_score >= 4 then 'Cant Lose Them'
        when recency_score <= 2 and frequency_score <= 2 then 'Hibernating'
        else 'Needs Attention'
    end as rfm_segment
from scored
