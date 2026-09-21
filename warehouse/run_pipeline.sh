#!/usr/bin/env bash
# End-to-end pipeline: generate raw data -> load -> snapshot -> transform ->
# test -> mutate a subset of customers (to demonstrate SCD2) -> re-snapshot
# -> re-transform -> build the dashboard.
set -euo pipefail
cd "$(dirname "$0")"

echo "== 1/8  Generating initial raw data =="
python3 data_generation/generate_data.py

echo "== 2/8  Loading raw data into DuckDB =="
python3 data_generation/load_raw.py

echo "== 3/8  Snapshotting customers (initial versions) =="
dbt snapshot --profiles-dir .

echo "== 4/8  Running all dbt models =="
dbt run --profiles-dir .

echo "== 5/8  Running dbt tests =="
dbt test --profiles-dir .

echo "== 6/8  Mutating ~12% of customers (tier upgrades / address changes) =="
python3 data_generation/generate_data.py --mutate
python3 data_generation/load_raw.py

echo "== 7/8  Re-snapshotting to capture SCD2 history, then rebuilding marts =="
dbt snapshot --profiles-dir .
dbt run --profiles-dir .
dbt test --profiles-dir .

echo "== 8/8  Building the dashboard =="
python3 dashboard/build_dashboard.py

echo
echo "Done. Open dashboard/dashboard.html in a browser to view the results."
