#!/usr/bin/env python3
"""
Generate Large Dataset for db-5 POS Retail (phppos schema).
Same as db-2 - generates ~1 GB of phppos_sales, phppos_items, phppos_people, phppos_locations data.
"""

import logging
import random
from pathlib import Path
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE = Path(__file__).parent.parent / 'data'
TARGET = 1.0 * 1024**3  # 1 GB

CATEGORIES = ['Fuel', 'Snacks', 'Beverages', 'Grocery', 'Automotive', 'Tobacco', 'Lottery', 'Food']
PAYMENT_TYPES = ['Cash', 'Credit', 'Debit', 'Check', 'Gift Card']


def main():
    BASE.mkdir(parents=True, exist_ok=True)
    all_sql = []
    size = 0

    logger.info("Seeding people, locations, items, employees...")
    for i in range(1, 5001):
        all_sql.append(f"""INSERT INTO phppos_people (person_id, first_name, last_name, phone_number, email, address_1, city, state, zip, country) VALUES
({i}, 'First{i}', 'Last{i}', '555-{i:07d}', 'user{i}@example.com', '{i} Main St', 'City{i%100}', 'CA', '{10000+i%90000}', 'US')
ON CONFLICT (person_id) DO NOTHING;""")
    for i in range(1, 101):
        all_sql.append(f"""INSERT INTO phppos_locations (location_id, name, address, phone) VALUES
({i}, 'Store {i}', '{i*100} Retail Ave', '555-{i:06d}')
ON CONFLICT (location_id) DO NOTHING;""")
    for i in range(1, 501):
        all_sql.append(f"""INSERT INTO phppos_items (item_id, name, category, cost_price, unit_price, deleted) VALUES
({i}, 'Item {i}', '{random.choice(CATEGORIES)}', {random.uniform(0.5, 50):.2f}, {random.uniform(1, 100):.2f}, 0)
ON CONFLICT (item_id) DO NOTHING;""")
    for i in range(1, 101):
        all_sql.append(f"""INSERT INTO phppos_employees (username, password, person_id) VALUES
('emp{i}', 'hash{i}', {min(i, 5000)});""")

    for s in all_sql:
        size += len(s.encode('utf-8'))

    logger.info("Generating phppos_sales (main bulk)...")
    sale_id = 1
    while size < TARGET:
        for _ in range(10000):
            emp = random.randint(1, 100)
            cust = random.randint(1, 5000) if random.random() > 0.2 else None
            loc = random.randint(1, 100)
            t = datetime.now() - timedelta(days=random.randint(0, 365), hours=random.randint(0, 23))
            cust_val = str(cust) if cust else 'NULL'
            s = f"""INSERT INTO phppos_sales (sale_id, employee_id, sale_time, customer_id, payment_type, location_id) VALUES
({sale_id}, {emp}, '{t}', {cust_val}, '{random.choice(PAYMENT_TYPES)}', {loc})
ON CONFLICT (sale_id) DO NOTHING;"""
            all_sql.append(s)
            size += len(s.encode('utf-8'))
            sale_id += 1
        if sale_id % 100000 == 1:
            logger.info(f"  {sale_id-1:,} sales, {size/(1024**3):.2f} GB")
        if size >= TARGET:
            break

    out = BASE / 'data_large.sql'
    with open(out, 'w') as f:
        f.write('\n'.join(all_sql))
    logger.info(f"Done: {out} ({out.stat().st_size/(1024**3):.2f} GB)")


if __name__ == '__main__':
    main()
