-- Singular test: fails if any line item has negative net revenue, which
-- would indicate a data quality bug in discounting logic upstream.

select order_item_id, net_revenue
from {{ ref('fact_order_items') }}
where net_revenue < 0
