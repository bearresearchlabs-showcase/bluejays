#!/usr/bin/env python3
"""
Generate Large Dataset for db-3 Hierarchical Orders (table1, table2, table3).
Generates ~1 GB of hierarchical table data.
"""

import logging
import random
from pathlib import Path
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE = Path(__file__).parent.parent / 'data'
TARGET = 1.0 * 1024**3  # 1 GB

CATEGORIES = ['pending', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded']


def main():
    BASE.mkdir(parents=True, exist_ok=True)
    all_sql = []
    size = 0

    logger.info("Generating table1 (hierarchy root)...")
    id_val = 1
    while size < TARGET:
        for _ in range(50000):
            parent = random.randint(1, max(1, id_val - 1)) if id_val > 1 and random.random() > 0.3 else None
            parent_val = str(parent) if parent else 'NULL'
            val = round(random.uniform(10, 10000), 2)
            d = (datetime.now() - timedelta(days=random.randint(0, 365))).date()
            s = f"""INSERT INTO table1 (id, parent_id, name, value, category, date_col) VALUES
({id_val}, {parent_val}, 'Order{id_val}', {val}, '{random.choice(CATEGORIES)}', '{d}')
ON CONFLICT (id) DO NOTHING;"""
            all_sql.append(s)
            size += len(s.encode('utf-8'))
            id_val += 1
        if id_val % 500000 == 1:
            logger.info(f"  {id_val-1:,} rows, {size/(1024**3):.2f} GB")
        if size >= TARGET:
            break

    out = BASE / 'data_large.sql'
    with open(out, 'w') as f:
        f.write('\n'.join(all_sql))
    logger.info(f"Done: {out} ({out.stat().st_size/(1024**3):.2f} GB)")


if __name__ == '__main__':
    main()
