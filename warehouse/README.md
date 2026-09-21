# Retail Analytics Data Warehouse

A local, fully runnable **dbt + DuckDB** data warehouse for a synthetic
e-commerce business: real ELT/ELT-style layering, dimensional modeling
(star schema), Slowly Changing Dimension (Type 2) history tracking, data
quality tests, and an analytics dashboard -- all without any cloud
warehouse, credentials, or paid services.

## Why this exists

Most "RAG demo" or toy-script projects don't show what a data
analytics/warehousing stack actually looks like in industry. This project
does, at a small scale you can run end to end in seconds:

- A synthetic OLTP export (customers, products, stores, orders,
  order items) + a clickstream event log, generated with Faker.
- An **ELT pipeline**: raw extracts loaded as-is into DuckDB, then
  transformed in SQL with **dbt** across staging -> intermediate -> marts
  layers.
- A **star schema** (`fact_order_items` + `dim_customers`, `dim_products`,
  `dim_stores`, `dim_date`).
- **SCD Type 2** customer history via a dbt snapshot, with a fact table
  that joins to the dimension **as of the order date** (point-in-time
  correctness), not just the customer's current attributes.
- **Data quality tests**: 44 dbt schema tests (uniqueness, not-null,
  referential integrity, accepted values) plus a custom singular test.
- **Analytics marts** built with window functions: RFM customer
  segmentation, monthly cohort retention, and revenue trend analysis.
- A **dashboard** (Plotly, single self-contained HTML file) built directly
  from the marts.

## Architecture

```
data/raw/*.csv, *.jsonl          (Faker-generated OLTP extract + event log)
        |
        v   data_generation/load_raw.py
   raw.*  (DuckDB tables, exact copy of the source extracts)
        |
        v   dbt models/staging   (light typing/renaming, 1:1 with sources)
   stg_customers, stg_products, stg_stores, stg_orders,
   stg_order_items, stg_web_events
        |
        v   dbt models/intermediate (business logic: pricing, joins)
   int_order_items_priced
        |
        v   dbt models/marts/core   (star schema)
   dim_customers (SCD2)   dim_products   dim_stores   dim_date
                     \         |          /
                      fact_order_items
        |
        v   dbt models/marts/analytics
   mart_monthly_revenue   mart_rfm_segments   mart_cohort_retention
        |
        v   dashboard/build_dashboard.py
   dashboard/dashboard.html
```

`snapshots/customers_snapshot.sql` sits alongside `raw.customers` and feeds
`dim_customers`: every time `dbt snapshot` runs, it detects changes to
`loyalty_tier`, `city`, or `state` and inserts a new dimension row rather
than overwriting the old one, closing out the old row's `dbt_valid_to`.

### The point-in-time SCD2 join

A naive fact-to-dimension join (`fact.customer_id = dim.customer_id`) would
always show a customer's *current* loyalty tier, even for orders placed
before they were upgraded. `fact_order_items` instead joins on
`order_date < dim.valid_to`, picking the dimension version with the
**smallest** `valid_to` that still exceeds the order date -- i.e. the
customer's attributes as they actually were at order time. See the comment
in `models/marts/core/fact_order_items.sql` for why this differs from a
textbook `valid_from <= date < valid_to` range join (snapshots only start
recording history from when you first run them, so there's no `valid_from`
reaching back into pre-warehouse history).

## Setup

```bash
pip install -r requirements.txt
```

## Running everything

```bash
./run_pipeline.sh
```

This generates the raw data, loads it, snapshots + transforms it, runs all
44 tests, **mutates ~12% of customers** (simulating loyalty-tier upgrades
and address changes) to demonstrate SCD2 capturing a real change, re-runs
the pipeline, and builds the dashboard at `dashboard/dashboard.html`.

To run steps individually:

```bash
python3 data_generation/generate_data.py     # generate raw/*.csv, *.jsonl
python3 data_generation/load_raw.py          # load into warehouse.duckdb (raw schema)
dbt snapshot --profiles-dir .                # capture customer history
dbt run --profiles-dir .                     # build staging -> intermediate -> marts
dbt test --profiles-dir .                    # run all 44 data quality tests
python3 dashboard/build_dashboard.py         # build dashboard/dashboard.html
```

Explore the warehouse directly:

```bash
python3 -c "import duckdb; duckdb.connect('warehouse.duckdb').sql('select * from main_analytics.mart_rfm_segments limit 10').show()"
```

## Project layout

```
data_generation/       synthetic data generator + raw loader
data/raw/               generated OLTP + event-log extracts
models/staging/         1:1 typed/cleaned views over each raw source
models/intermediate/    business logic (order-line pricing)
models/marts/core/      star schema: dims + fact
models/marts/analytics/ RFM segmentation, cohort retention, revenue trend
snapshots/               SCD Type 2 customer history
macros/                  shared SQL macros
tests/                   custom singular data test
dashboard/               Plotly dashboard builder + output HTML
```
