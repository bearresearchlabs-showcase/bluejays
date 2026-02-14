#!/usr/bin/env python3
"""
Generate Large Dataset for db-4 SharedAI Models.
Generates ~1 GB of models table data.
"""

import logging
import random
from pathlib import Path
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE = Path(__file__).parent.parent / 'data'
TARGET = 1.0 * 1024**3  # 1 GB

MODEL_NAMES = ['gpt-4', 'claude-3', 'llama-3', 'mistral', 'gemini', 'codellama', 'starcoder', 'falcon', 'phi', 'custom']


def main():
    BASE.mkdir(parents=True, exist_ok=True)
    all_sql = []
    size = 0

    logger.info("Generating models...")
    for i in range(1, 50_000_000):
        uid = random.randint(1, 100000)
        name = f"{random.choice(MODEL_NAMES)}-v{i%100}"
        t = datetime.now() - timedelta(days=random.randint(0, 365))
        s = f"""INSERT INTO models (id, name, user_id, created_at) VALUES
({i}, '{name}', {uid}, '{t}')
ON CONFLICT (id) DO NOTHING;"""
        all_sql.append(s)
        size += len(s.encode('utf-8'))
        if i % 500000 == 0:
            logger.info(f"  {i:,} models, {size/(1024**3):.2f} GB")
        if size >= TARGET:
            break

    out = BASE / 'data_large.sql'
    with open(out, 'w') as f:
        f.write('\n'.join(all_sql))
    logger.info(f"Done: {out} ({out.stat().st_size/(1024**3):.2f} GB)")


if __name__ == '__main__':
    main()
