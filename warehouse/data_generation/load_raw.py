"""Loads the raw CSV/JSONL extracts into the `raw` schema of the DuckDB
warehouse file, simulating the extract-and-load step of an ELT pipeline
that dbt then transforms.

Usage:
    python load_raw.py
"""
import os

import duckdb

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
DB_PATH = os.path.join(BASE_DIR, "warehouse.duckdb")
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")

CSV_TABLES = ["customers", "products", "stores", "orders", "order_items"]


def main():
    con = duckdb.connect(DB_PATH)
    con.execute("CREATE SCHEMA IF NOT EXISTS raw")

    for table in CSV_TABLES:
        csv_path = os.path.join(RAW_DIR, f"{table}.csv")
        con.execute(f"""
            CREATE OR REPLACE TABLE raw.{table} AS
            SELECT * FROM read_csv_auto('{csv_path}', header=True)
        """)
        count = con.execute(f"SELECT count(*) FROM raw.{table}").fetchone()[0]
        print(f"Loaded raw.{table}: {count} rows")

    events_path = os.path.join(RAW_DIR, "web_events.jsonl")
    con.execute(f"""
        CREATE OR REPLACE TABLE raw.web_events AS
        SELECT * FROM read_json_auto('{events_path}')
    """)
    count = con.execute("SELECT count(*) FROM raw.web_events").fetchone()[0]
    print(f"Loaded raw.web_events: {count} rows")

    con.close()


if __name__ == "__main__":
    main()
