-- Monthly cohort retention: for each signup-month cohort, what % of that
-- cohort's customers placed at least one order in each subsequent month
-- since signup.

with facts as (
    select * from {{ ref('fact_order_items') }}
    where is_completed
),

customers as (
    select * from {{ ref('dim_customers') }}
    where is_current
),

customer_cohort as (
    select
        customer_id,
        strftime(signup_date, '%Y-%m') as cohort_month,
        date_trunc('month', signup_date) as cohort_month_start
    from customers
),

customer_activity_months as (
    select distinct
        f.customer_id,
        date_trunc('month', f.order_date) as activity_month
    from facts f
),

cohort_activity as (
    select
        cc.cohort_month,
        cc.customer_id,
        cam.activity_month,
        date_diff('month', cc.cohort_month_start, cam.activity_month) as months_since_signup
    from customer_cohort cc
    inner join customer_activity_months cam
        on cc.customer_id = cam.customer_id
        and cam.activity_month >= cc.cohort_month_start
),

cohort_sizes as (
    select cohort_month, count(distinct customer_id) as cohort_size
    from customer_cohort
    group by 1
),

retention as (
    select
        ca.cohort_month,
        ca.months_since_signup,
        count(distinct ca.customer_id) as active_customers
    from cohort_activity ca
    group by 1, 2
)

select
    r.cohort_month,
    cs.cohort_size,
    r.months_since_signup,
    r.active_customers,
    round(100.0 * r.active_customers / nullif(cs.cohort_size, 0), 1) as retention_pct
from retention r
inner join cohort_sizes cs on r.cohort_month = cs.cohort_month
order by r.cohort_month, r.months_since_signup
