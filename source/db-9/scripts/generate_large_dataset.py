#!/usr/bin/env python3
"""
Generate Large Dataset Script for db-9 Shipping Intelligence Database
Generates at least 1 GB of synthetic shipping rate, shipment, and analytics data.
"""

import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Tuple
import random
import uuid

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'
OUTPUT_DIR = DATA_DIR
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TARGET_SIZE_GB = 1.0
TARGET_SIZE_BYTES = TARGET_SIZE_GB * 1024 * 1024 * 1024

CARRIERS = [
    ('USPS', 'US Postal Service', 'Postal'),
    ('UPS', 'United Parcel Service', 'Courier'),
    ('FEDEX', 'FedEx', 'Courier'),
    ('DHL', 'DHL Express', 'Courier'),
    ('ONTRAC', 'OnTrac', 'Courier'),
]

SERVICES = [
    ('Priority Mail', 'Express'),
    ('Ground', 'Ground'),
    ('Express', 'Express'),
    ('2-Day', 'Express'),
    ('Overnight', 'Express'),
    ('Economy', 'Economy'),
    ('Standard', 'Ground'),
]

US_ZIPS = [f"{random.randint(10001, 99999)}" for _ in range(500)]
for i in range(500):
    US_ZIPS[i] = f"{random.randint(10001, 99999)}"


def generate_carriers_sql() -> Tuple[List[str], List[str]]:
    sql = []
    carrier_ids = []
    for i, (code, name, ctype) in enumerate(CARRIERS):
        cid = f"carrier-{code.lower()}"
        carrier_ids.append(cid)
        sql.append(f"""INSERT INTO shipping_carriers (carrier_id, carrier_name, carrier_code, carrier_type, commercial_pricing_available, requires_account, active_status) VALUES
('{cid}', '{name}', '{code}', '{ctype}', {random.choice([True, False])}, {random.choice([True, False])}, TRUE)
ON CONFLICT (carrier_id) DO NOTHING;""")
    return sql, carrier_ids


def generate_services_sql(carrier_ids: List[str]) -> Tuple[List[str], List[str]]:
    sql = []
    service_ids = []
    for cid in carrier_ids:
        for i, (sname, scat) in enumerate(SERVICES[:4]):
            sid = f"{cid}-svc-{i}"
            service_ids.append(sid)
            sql.append(f"""INSERT INTO shipping_service_types (service_id, carrier_id, service_code, service_name, service_category, domestic_available, international_available, active_status) VALUES
('{sid}', '{cid}', '{sname.replace(" ", "_")[:20]}', '{sname}', '{scat}', TRUE, {random.choice([True, False])}, TRUE)
ON CONFLICT (service_id) DO NOTHING;""")
    return sql, service_ids


def generate_zones_sql(carrier_ids: List[str]) -> Tuple[List[str], List[str]]:
    sql = []
    zone_ids = []
    for cid in carrier_ids:
        for i in range(min(100, len(US_ZIPS) * 2)):
            orig = random.choice(US_ZIPS)
            dest = random.choice(US_ZIPS)
            zid = f"{cid}-zone-{orig}-{dest}-{i}"
            zone_ids.append(zid)
            sql.append(f"""INSERT INTO shipping_zones (zone_id, carrier_id, origin_zip_code, destination_zip_code, zone_number, zone_type, distance_miles, transit_days_min, transit_days_max, effective_date) VALUES
('{zid}', '{cid}', '{orig}', '{dest}', {random.randint(1, 8)}, 'Domestic', {random.uniform(50, 3000):.2f}, {random.randint(1, 3)}, {random.randint(2, 7)}, '{datetime.now().date()}')
ON CONFLICT (zone_id) DO NOTHING;""")
    return sql, zone_ids


def generate_rates_sql(carrier_ids: List[str], service_ids: List[str], zone_ids: List[str]) -> List[str]:
    sql = []
    current_size = 0
    records = 0
    target = TARGET_SIZE_BYTES
    batch = 0
    while current_size < target:
        batch += 1
        for cid in carrier_ids:
            for sid in [s for s in service_ids if cid in s]:
                for _ in range(5000):
                    zone_id = random.choice(zone_ids)
                    zone_val = f"'{zone_id}'"
                    weight = round(random.uniform(0.1, 70.0), 4)
                    rate_amt = round(random.uniform(5.99, 150.99), 2)
                    total = round(rate_amt * (1 + random.uniform(0, 0.15)), 2)
                    rid = f"rate-{uuid.uuid4().hex[:16]}"
                    eff = (datetime.now() - timedelta(days=random.randint(0, 365))).date()
                    s = f"""INSERT INTO shipping_rates (rate_id, carrier_id, service_id, zone_id, weight_lbs, rate_amount, rate_type, surcharge_amount, total_rate, effective_date, rate_source) VALUES
('{rid}', '{cid}', '{sid}', {zone_val}, {weight}, {rate_amt}, 'Retail', 0, {total}, '{eff}', 'API')
ON CONFLICT (rate_id) DO NOTHING;"""
                    sql.append(s)
                    current_size += len(s.encode('utf-8'))
                    records += 1
                    if records % 100000 == 0:
                        logger.info(f"  Generated {records:,} shipping rates ({current_size / (1024**3):.2f} GB)")
                    if current_size >= target:
                        return sql
    return sql


def main():
    logger.info("=" * 80)
    logger.info("Generating Large Dataset for db-9 Shipping Intelligence")
    logger.info(f"Target size: {TARGET_SIZE_GB} GB")
    logger.info("=" * 80)
    
    all_sql = []
    
    logger.info("\n1. Generating carriers...")
    carrier_sql, carrier_ids = generate_carriers_sql()
    all_sql.extend(carrier_sql)
    
    logger.info("\n2. Generating service types...")
    service_sql, service_ids = generate_services_sql(carrier_ids)
    all_sql.extend(service_sql)
    
    logger.info("\n3. Generating zones...")
    zone_sql, zone_ids = generate_zones_sql(carrier_ids)
    all_sql.extend(zone_sql)
    
    logger.info("\n4. Generating shipping rates (main data)...")
    rate_sql = generate_rates_sql(carrier_ids, service_ids, zone_ids)
    all_sql.extend(rate_sql)
    
    logger.info(f"\n5. Writing SQL to {OUTPUT_DIR / 'data_large.sql'}...")
    output_path = OUTPUT_DIR / 'data_large.sql'
    with open(output_path, 'w', encoding='utf-8') as f:
        for stmt in all_sql:
            f.write(stmt + '\n')
    
    file_size = output_path.stat().st_size
    logger.info("\n✅ Generation complete!")
    logger.info(f"   Output file: {output_path}")
    logger.info(f"   File size: {file_size / (1024**3):.2f} GB ({file_size / (1024**2):.2f} MB)")
    logger.info(f"   SQL statements: {len(all_sql):,}")
    logger.info("=" * 80)


if __name__ == '__main__':
    main()
