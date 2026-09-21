"""Generates a synthetic e-commerce raw dataset for the analytics warehouse.

Simulates what you'd actually get out of an OLTP export + event logs:
  - customers.csv   (OLTP extract, one row per customer AS OF extract time)
  - products.csv
  - stores.csv
  - orders.csv
  - order_items.csv
  - web_events.csv  (clickstream/event log, JSON lines)

Run twice with --mutate on the second run to simulate customers changing
loyalty tier / address between extracts, which is what the dbt snapshot
(SCD Type 2) is built to capture.

Usage:
    python generate_data.py                 # initial full generation
    python generate_data.py --mutate        # mutate ~12% of customers only
"""
import argparse
import csv
import json
import os
import random
from datetime import datetime, timedelta

from faker import Faker

SEED = 42
N_CUSTOMERS = 600
N_PRODUCTS = 150
N_STORES = 8
N_ORDERS = 6000
MONTHS_OF_HISTORY = 18

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")

CATEGORIES = {
    "Electronics": (30, 1200),
    "Home & Kitchen": (10, 400),
    "Sports & Outdoors": (8, 350),
    "Books": (5, 60),
    "Beauty": (5, 150),
    "Toys": (5, 120),
    "Apparel": (10, 250),
}
LOYALTY_TIERS = ["Bronze", "Silver", "Gold", "Platinum"]
LOYALTY_WEIGHTS = [0.55, 0.25, 0.15, 0.05]
CHANNELS = ["web", "mobile_app", "marketplace"]
EVENT_TYPES = ["page_view", "add_to_cart", "checkout_start", "purchase"]


def write_csv(path, rows, fieldnames):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def generate_customers(fake: Faker):
    customers = []
    start = datetime.now() - timedelta(days=MONTHS_OF_HISTORY * 30)
    for i in range(1, N_CUSTOMERS + 1):
        signup_date = start + timedelta(days=random.randint(0, MONTHS_OF_HISTORY * 30 - 1))
        customers.append({
            "customer_id": i,
            "full_name": fake.name(),
            "email": fake.unique.email(),
            "city": fake.city(),
            "state": fake.state_abbr(),
            "loyalty_tier": random.choices(LOYALTY_TIERS, weights=LOYALTY_WEIGHTS)[0],
            "signup_date": signup_date.date().isoformat(),
            "extracted_at": datetime.now().isoformat(timespec="seconds"),
        })
    return customers


def mutate_customers(fake: Faker, existing_rows):
    n_mutate = max(1, int(len(existing_rows) * 0.12))
    to_mutate = random.sample(existing_rows, n_mutate)
    upgrade_path = {"Bronze": "Silver", "Silver": "Gold", "Gold": "Platinum", "Platinum": "Platinum"}
    for row in to_mutate:
        if random.random() < 0.7:
            row["loyalty_tier"] = upgrade_path[row["loyalty_tier"]]
        else:
            row["city"] = fake.city()
            row["state"] = fake.state_abbr()
        row["extracted_at"] = datetime.now().isoformat(timespec="seconds")
    return existing_rows


def generate_products(fake: Faker):
    products = []
    for i in range(1, N_PRODUCTS + 1):
        category = random.choice(list(CATEGORIES.keys()))
        low, high = CATEGORIES[category]
        products.append({
            "product_id": i,
            "product_name": fake.catch_phrase(),
            "category": category,
            "unit_price_cents": random.randint(low * 100, high * 100),
            "is_active": random.random() > 0.05,
        })
    return products


def generate_stores(fake: Faker):
    stores = []
    for i in range(1, N_STORES + 1):
        stores.append({
            "store_id": i,
            "store_name": f"{fake.city()} Fulfillment Center",
            "region": random.choice(["Northeast", "Midwest", "South", "West"]),
        })
    return stores


def generate_orders_and_items(customers, products, stores):
    orders, items = [], []
    start = datetime.now() - timedelta(days=MONTHS_OF_HISTORY * 30)
    item_id = 1

    active_products = [p for p in products if p["is_active"]]

    for order_id in range(1, N_ORDERS + 1):
        customer = random.choice(customers)
        signup = datetime.fromisoformat(customer["signup_date"])
        earliest = max(start, signup)
        span_days = max((datetime.now() - earliest).days, 1)
        order_date = earliest + timedelta(days=random.randint(0, span_days - 1))

        order_status = random.choices(
            ["completed", "completed", "completed", "completed", "cancelled", "refunded"],
            k=1,
        )[0]

        orders.append({
            "order_id": order_id,
            "customer_id": customer["customer_id"],
            "store_id": random.choice(stores)["store_id"],
            "order_date": order_date.date().isoformat(),
            "channel": random.choice(CHANNELS),
            "order_status": order_status,
        })

        n_items = random.randint(1, 5)
        chosen_products = random.sample(active_products, min(n_items, len(active_products)))
        for product in chosen_products:
            qty = random.randint(1, 3)
            discount_pct = random.choice([0, 0, 0, 5, 10, 15, 20])
            items.append({
                "order_item_id": item_id,
                "order_id": order_id,
                "product_id": product["product_id"],
                "quantity": qty,
                "unit_price_cents": product["unit_price_cents"],
                "discount_pct": discount_pct,
            })
            item_id += 1

    return orders, items


def generate_web_events(customers, products, path):
    events = []
    start = datetime.now() - timedelta(days=MONTHS_OF_HISTORY * 30)
    for event_id in range(1, 20001):
        customer = random.choice(customers)
        signup = datetime.fromisoformat(customer["signup_date"])
        earliest = max(start, signup)
        span_seconds = max(int((datetime.now() - earliest).total_seconds()), 1)
        ts = earliest + timedelta(seconds=random.randint(0, span_seconds - 1))
        events.append({
            "event_id": event_id,
            "customer_id": customer["customer_id"],
            "product_id": random.choice(products)["product_id"],
            "event_type": random.choices(
                EVENT_TYPES, weights=[0.55, 0.25, 0.12, 0.08]
            )[0],
            "event_ts": ts.isoformat(timespec="seconds"),
        })

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for event in events:
            f.write(json.dumps(event) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mutate", action="store_true",
                         help="Mutate existing customers.csv instead of regenerating everything")
    args = parser.parse_args()

    random.seed(SEED)
    fake = Faker()
    Faker.seed(SEED)

    customers_path = os.path.join(OUT_DIR, "customers.csv")
    customer_fields = ["customer_id", "full_name", "email", "city", "state",
                        "loyalty_tier", "signup_date", "extracted_at"]

    if args.mutate:
        if not os.path.exists(customers_path):
            raise SystemExit("customers.csv not found - run without --mutate first")
        with open(customers_path, newline="", encoding="utf-8") as f:
            existing = list(csv.DictReader(f))
        mutated = mutate_customers(fake, existing)
        write_csv(customers_path, mutated, customer_fields)
        print(f"Mutated a subset of customers -> {customers_path}")
        return

    customers = generate_customers(fake)
    write_csv(customers_path, customers, customer_fields)

    products = generate_products(fake)
    write_csv(os.path.join(OUT_DIR, "products.csv"), products,
              ["product_id", "product_name", "category", "unit_price_cents", "is_active"])

    stores = generate_stores(fake)
    write_csv(os.path.join(OUT_DIR, "stores.csv"), stores,
              ["store_id", "store_name", "region"])

    orders, items = generate_orders_and_items(customers, products, stores)
    write_csv(os.path.join(OUT_DIR, "orders.csv"), orders,
              ["order_id", "customer_id", "store_id", "order_date", "channel", "order_status"])
    write_csv(os.path.join(OUT_DIR, "order_items.csv"), items,
              ["order_item_id", "order_id", "product_id", "quantity", "unit_price_cents", "discount_pct"])

    generate_web_events(customers, products, os.path.join(OUT_DIR, "web_events.jsonl"))

    print(f"Generated {len(customers)} customers, {len(products)} products, "
          f"{len(stores)} stores, {len(orders)} orders, {len(items)} order_items, "
          f"20000 web_events -> {OUT_DIR}")


if __name__ == "__main__":
    main()
