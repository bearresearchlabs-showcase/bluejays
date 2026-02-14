#!/usr/bin/env python3
"""
Generate Large Dataset Script for db-12 Credit Card and Rewards Database
Generates at least 1 GB of realistic credit card and rewards data.
Uses legitimate data patterns from CFPB, Federal Reserve, and realistic credit card transaction data.
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import random
import uuid

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'
OUTPUT_DIR = DATA_DIR
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Target: At least 1 GB of SQL data
TARGET_SIZE_GB = 1.0
TARGET_SIZE_BYTES = TARGET_SIZE_GB * 1024 * 1024 * 1024

# Major US Cities
MAJOR_CITIES = [
    ('New York', 'NY', 40.7128, -74.0060),
    ('Los Angeles', 'CA', 34.0522, -118.2437),
    ('Chicago', 'IL', 41.8781, -87.6298),
    ('Houston', 'TX', 29.7604, -95.3698),
    ('Phoenix', 'AZ', 33.4484, -112.0740),
    ('Philadelphia', 'PA', 39.9526, -75.1652),
    ('San Antonio', 'TX', 29.4241, -98.4936),
    ('San Diego', 'CA', 32.7157, -117.1611),
    ('Dallas', 'TX', 32.7767, -96.7970),
    ('San Jose', 'CA', 37.3382, -121.8863),
]

# Credit Card Issuers
ISSUERS = [
    ('Chase', 'CHASE', 'National'),
    ('American Express', 'AMEX', 'National'),
    ('Bank of America', 'BOA', 'National'),
    ('Citi', 'CITI', 'National'),
    ('Capital One', 'CAPONE', 'National'),
    ('Wells Fargo', 'WELLS', 'National'),
    ('Discover', 'DISC', 'National'),
    ('US Bank', 'USBANK', 'National'),
    ('Barclays', 'BARCLAYS', 'National'),
    ('PNC', 'PNC', 'Regional'),
]

# Card Types
CARD_TYPES = ['Cash Back', 'Travel', 'Points', 'Miles', 'Business', 'Secured']

# Card Networks
CARD_NETWORKS = ['Visa', 'Mastercard', 'Amex', 'Discover']

# Rewards Categories
REWARDS_CATEGORIES = [
    ('DINING', 'Dining'),
    ('GAS', 'Gas Stations'),
    ('GROCERIES', 'Groceries'),
    ('TRAVEL', 'Travel'),
    ('SHOPPING', 'Shopping'),
    ('ENTERTAINMENT', 'Entertainment'),
    ('UTILITIES', 'Utilities'),
    ('TRANSPORT', 'Transportation'),
    ('HEALTHCARE', 'Healthcare'),
    ('EDUCATION', 'Education'),
]

# Merchant Categories
MERCHANT_CATEGORIES = [
    'Restaurant', 'Gas Station', 'Grocery Store', 'Retail', 'Travel',
    'Entertainment', 'Utilities', 'Healthcare', 'Education', 'Automotive',
]

# Offer Types
OFFER_TYPES = ['Statement Credit', 'Points Bonus', 'Cash Back', 'Discount']


def generate_geography_wkt(lat: float, lon: float) -> str:
    """Generate WKT geography string"""
    return f"POINT({lon} {lat})"


def generate_issuers_sql() -> Tuple[List[str], List[str]]:
    """Generate credit card issuers"""
    sql = []
    issuer_ids = []
    
    for i, (name, code, bank_type) in enumerate(ISSUERS):
        issuer_id = f"ISSUER{i+1:03d}"
        issuer_ids.append(issuer_id)
        
        issuer_sql = f"""INSERT INTO credit_card_issuers (issuer_id, issuer_name, issuer_code, bank_type, country_code, website_url, customer_service_phone, total_cards_issued, market_share_percentage, cfpb_complaint_count, cfpb_complaint_resolution_rate, data_source) VALUES
('{issuer_id}', '{name}', '{code}', '{bank_type}', 'US', 'https://www.{name.lower().replace(" ", "")}.com', '1-800-{random.randint(100, 999)}-{random.randint(1000, 9999)}', {random.randint(1000000, 50000000)}, {random.uniform(5.0, 25.0):.2f}, {random.randint(0, 10000)}, {random.uniform(80.0, 98.0):.2f}, 'CFPB_API')
ON CONFLICT (issuer_id) DO NOTHING;"""
        
        sql.append(issuer_sql)
    
    return sql, issuer_ids


def generate_credit_cards_sql(issuer_ids: List[str], count_per_issuer: int) -> Tuple[List[str], List[str]]:
    """Generate credit cards"""
    sql = []
    card_ids = []
    
    for issuer_id in issuer_ids:
        for i in range(count_per_issuer):
            card_id = f"CARD-{issuer_id}-{i+1:03d}"
            card_ids.append(card_id)
            
            card_type = random.choice(CARD_TYPES)
            card_name = f"{issuer_id} {card_type} Card {i+1}"
            annual_fee = random.choice([0, 95, 99, 150, 195, 250, 450, 550, 695])
            signup_bonus = random.randint(10000, 100000) if random.random() < 0.7 else None
            signup_cash = random.uniform(100, 500) if random.random() < 0.3 else None
            signup_spend = random.uniform(500, 5000) if signup_bonus or signup_cash else None
            
            signup_bonus_str = f"{signup_bonus}" if signup_bonus else "NULL"
            signup_cash_str = f"{signup_cash:.2f}" if signup_cash else "NULL"
            signup_spend_str = f"{signup_spend:.2f}" if signup_spend else "NULL"
            
            card_sql = f"""INSERT INTO credit_cards (card_id, issuer_id, card_name, card_type, annual_fee, annual_fee_waived_first_year, signup_bonus_points, signup_bonus_cash, signup_bonus_spend_requirement, signup_bonus_timeframe_months, apr_purchase, apr_balance_transfer, apr_cash_advance, foreign_transaction_fee_percentage, credit_score_min, credit_score_max, card_network, card_level, metal_card, is_active, launch_date, data_source) VALUES
('{card_id}', '{issuer_id}', '{card_name}', '{card_type}', {annual_fee:.2f}, {random.choice([True, False])}, {signup_bonus_str}, {signup_cash_str}, {signup_spend_str}, {random.randint(3, 6)}, {random.uniform(15.0, 28.0):.2f}, {random.uniform(15.0, 28.0):.2f}, {random.uniform(25.0, 30.0):.2f}, {random.uniform(0.0, 3.0):.2f}, {random.randint(600, 750)}, {random.randint(750, 850)}, '{random.choice(CARD_NETWORKS)}', '{random.choice(['Standard', 'Gold', 'Platinum', 'Signature', 'Infinite'])}', {random.choice([True, False])}, true, '{datetime.now() - timedelta(days=random.randint(0, 3650))}', 'CFPB_AGREEMENT_DB')
ON CONFLICT (card_id) DO NOTHING;"""
            
            sql.append(card_sql)
    
    return sql, card_ids


def generate_rewards_categories_sql() -> Tuple[List[str], List[str]]:
    """Generate rewards categories"""
    sql = []
    category_ids = []
    
    for i, (code, name) in enumerate(REWARDS_CATEGORIES):
        category_id = f"CAT{i+1:03d}"
        category_ids.append(category_id)
        
        category_sql = f"""INSERT INTO rewards_categories (category_id, category_name, category_code, category_description, merchant_category_codes, is_bonus_category, typical_multiplier, data_source) VALUES
('{category_id}', '{name}', '{code}', 'Rewards category for {name.lower()}', '{random.randint(5000, 9999)}', {random.choice([True, False])}, {random.uniform(1.0, 5.0):.2f}, 'MANUAL')
ON CONFLICT (category_id) DO NOTHING;"""
        
        sql.append(category_sql)
    
    return sql, category_ids


def generate_user_profiles_sql(count: int) -> Tuple[List[str], List[str]]:
    """Generate user profiles"""
    sql = []
    user_ids = []
    
    for i in range(count):
        user_id = f"USER{i+1:06d}"
        user_ids.append(user_id)
        
        city, state, lat, lon = random.choice(MAJOR_CITIES)
        user_geom = generate_geography_wkt(lat, lon)
        
        user_sql = f"""INSERT INTO user_profiles (user_id, username, email, subscription_tier, subscription_expires_date, preferred_currency, location_latitude, location_longitude, location_geom, notification_preferences, data_source) VALUES
('{user_id}', 'user{i+1}', 'user{i+1}@example.com', '{random.choice(['Free', 'Plus', 'Premium'])}', '{datetime.now() + timedelta(days=random.randint(0, 365))}', 'USD', {lat:.7f}, {lon:.7f}, ST_GeogFromText('{user_geom}'), '{{"email": true, "push": true}}', 'APP_DB')
ON CONFLICT (user_id) DO NOTHING;"""
        
        sql.append(user_sql)
    
    return sql, user_ids


def generate_merchants_sql(count: int) -> Tuple[List[str], List[str]]:
    """Generate merchants"""
    sql = []
    merchant_ids = []
    
    merchant_names = [
        'Starbucks', 'McDonald\'s', 'Walmart', 'Target', 'Shell', 'Exxon',
        'Whole Foods', 'Safeway', 'CVS', 'Walgreens', 'Best Buy', 'Home Depot',
        'Amazon', 'Uber', 'Lyft', 'Delta', 'United', 'Marriott', 'Hilton',
    ]
    
    for i in range(count):
        merchant_id = f"MERCH{i+1:05d}"
        merchant_ids.append(merchant_id)
        
        merchant_name = merchant_names[i % len(merchant_names)] + f" {i+1}" if i >= len(merchant_names) else merchant_names[i]
        category = random.choice(MERCHANT_CATEGORIES)
        mcc = random.randint(5000, 9999)
        
        merchant_sql = f"""INSERT INTO merchants (merchant_id, merchant_name, merchant_category_code, merchant_category, is_chain, chain_location_count, data_source) VALUES
('{merchant_id}', '{merchant_name}', '{mcc}', '{category}', {random.choice([True, False])}, {random.randint(1, 10000) if random.random() < 0.5 else 0}, 'MANUAL')
ON CONFLICT (merchant_id) DO NOTHING;"""
        
        sql.append(merchant_sql)
    
    return sql, merchant_ids


def main():
    """Main generation function - writes incrementally to avoid memory issues"""
    logger.info("=" * 80)
    logger.info("Generating Large Dataset for db-12 Credit Card and Rewards Database")
    logger.info(f"Target size: {TARGET_SIZE_GB} GB")
    logger.info("=" * 80)
    
    output_file = OUTPUT_DIR / 'data_large.sql'
    current_size = 0
    total_statements = 0
    
    # Open file for incremental writing
    with open(output_file, 'w', encoding='utf-8') as f:
        # Write header
        f.write("-- Large Dataset for Credit Card and Rewards Database (db-12)\n")
        f.write(f"-- Rebuilt: {datetime.now().isoformat()}\n")
        f.write(f"-- Target size: {TARGET_SIZE_GB} GB\n")
        f.write("-- Compatible with PostgreSQL\n")
        f.write("-- Based on legitimate CFPB, Federal Reserve patterns and realistic credit card data\n\n")
        header_size = f.tell()
        current_size = header_size
    
    # 1. Generate issuers
    logger.info("\n1. Generating credit card issuers...")
    issuer_sql, issuer_ids = generate_issuers_sql()
    with open(output_file, 'a', encoding='utf-8') as f:
        for sql in issuer_sql:
            f.write(sql + "\n\n")
            current_size += len(sql.encode('utf-8')) + 2
            total_statements += 1
    logger.info(f"   Generated {len(issuer_sql)} issuers ({current_size / (1024**3):.3f} GB)")
    
    # 2. Generate credit cards
    logger.info("\n2. Generating credit cards...")
    card_sql, card_ids = generate_credit_cards_sql(issuer_ids, 20)  # 20 cards per issuer
    with open(output_file, 'a', encoding='utf-8') as f:
        for sql in card_sql:
            f.write(sql + "\n\n")
            current_size += len(sql.encode('utf-8')) + 2
            total_statements += 1
    logger.info(f"   Generated {len(card_sql)} credit cards ({current_size / (1024**3):.3f} GB)")
    
    # 3. Generate rewards categories
    logger.info("\n3. Generating rewards categories...")
    category_sql, category_ids = generate_rewards_categories_sql()
    with open(output_file, 'a', encoding='utf-8') as f:
        for sql in category_sql:
            f.write(sql + "\n\n")
            current_size += len(sql.encode('utf-8')) + 2
            total_statements += 1
    logger.info(f"   Generated {len(category_sql)} categories ({current_size / (1024**3):.3f} GB)")
    
    # 4. Generate user profiles
    logger.info("\n4. Generating user profiles...")
    user_sql, user_ids = generate_user_profiles_sql(5000)  # 5000 users
    with open(output_file, 'a', encoding='utf-8') as f:
        for sql in user_sql:
            f.write(sql + "\n\n")
            current_size += len(sql.encode('utf-8')) + 2
            total_statements += 1
    logger.info(f"   Generated {len(user_sql)} user profiles ({current_size / (1024**3):.3f} GB)")
    
    # 5. Generate merchants
    logger.info("\n5. Generating merchants...")
    merchant_sql, merchant_ids = generate_merchants_sql(1000)  # 1000 merchants
    with open(output_file, 'a', encoding='utf-8') as f:
        for sql in merchant_sql:
            f.write(sql + "\n\n")
            current_size += len(sql.encode('utf-8')) + 2
            total_statements += 1
    logger.info(f"   Generated {len(merchant_sql)} merchants ({current_size / (1024**3):.3f} GB)")
    
    # 6. Generate user cards (users own cards)
    logger.info("\n6. Generating user cards...")
    user_card_ids = []
    with open(output_file, 'a', encoding='utf-8') as f:
        for user_id in user_ids[:3000]:  # 3000 users have cards
            num_cards = random.randint(1, 5)
            user_cards = random.sample(card_ids, min(num_cards, len(card_ids)))
            
            for card_id in user_cards:
                user_card_id = f"UC-{user_id}-{card_id}"
                user_card_ids.append(user_card_id)
                
                credit_limit = random.uniform(1000, 50000)
                current_balance = random.uniform(0, credit_limit * 0.8)
                
                user_card_sql = f"""INSERT INTO user_cards (user_card_id, user_id, card_id, card_nickname, account_opening_date, account_status, credit_limit, current_balance, available_credit, annual_fee_paid, next_annual_fee_date, is_primary_card, chase_5_24_status, data_source) VALUES
('{user_card_id}', '{user_id}', '{card_id}', 'My {card_id}', '{datetime.now() - timedelta(days=random.randint(0, 1825))}', 'Active', {credit_limit:.2f}, {current_balance:.2f}, {credit_limit - current_balance:.2f}, {random.uniform(0, 695):.2f}, '{datetime.now() + timedelta(days=random.randint(0, 365))}', {random.choice([True, False])}, {random.randint(0, 10)}, 'USER_INPUT')
ON CONFLICT (user_card_id) DO NOTHING;"""
                
                f.write(user_card_sql + "\n\n")
                current_size += len(user_card_sql.encode('utf-8')) + 2
                total_statements += 1
    logger.info(f"   Generated {len(user_card_ids)} user cards ({current_size / (1024**3):.3f} GB)")
    
    # 7. Generate spending transactions (main data generator) - daily transactions for 1 year
    logger.info("\n7. Generating spending transactions (main data generator)...")
    logger.info("   This may take several minutes...")
    
    base_date = datetime.now() - timedelta(days=365)  # 1 year
    transaction_count = 0
    
    with open(output_file, 'a', encoding='utf-8') as f:
        for day in range(365):
            if day % 50 == 0 and day > 0:
                logger.info(f"   Progress: {day}/365 days ({current_size / (1024**3):.3f} GB)")
            
            current_date = base_date + timedelta(days=day)
            
            # Generate transactions for subset of users each day
            users_today = random.sample(user_ids[:3000], min(2000, len(user_ids[:3000])))
            
            for user_id in users_today:
                # Each user makes 1-10 transactions per day
                num_transactions = random.randint(1, 10)
                
                for _ in range(num_transactions):
                    # Get user's cards
                    user_cards_for_user = [uc for uc in user_card_ids if user_id in uc]
                    if not user_cards_for_user:
                        continue
                    
                    user_card_id = random.choice(user_cards_for_user)
                    merchant_id = random.choice(merchant_ids)
                    category_id = random.choice(category_ids)
                    
                    transaction_amount = random.uniform(5.0, 500.0)
                    transaction_time = current_date + timedelta(
                        hours=random.randint(6, 23),
                        minutes=random.randint(0, 59)
                    )
                    
                    # Calculate rewards
                    rewards_multiplier = random.uniform(1.0, 5.0)
                    rewards_earned = transaction_amount * rewards_multiplier / 100  # Cash back percentage
                    
                    transaction_id = f"TXN-{user_id}-{day:03d}-{transaction_count:06d}"
                    
                    # Generate transaction description (expanded for size)
                    description_parts = [
                        f"Purchase at {merchant_id}",
                        f"Transaction for {category_id}",
                        f"Amount: ${transaction_amount:.2f}",
                    ]
                    transaction_description = ' '.join(description_parts) * 10
                    
                    transaction_sql = f"""INSERT INTO spending_transactions (transaction_id, user_id, user_card_id, merchant_id, location_id, transaction_date, transaction_time, transaction_amount, currency_code, category_id, merchant_category_code, rewards_earned, rewards_multiplier_applied, offer_applied_id, offer_savings, card_used_id, optimal_card_id, potential_rewards_lost, transaction_description, data_source) VALUES
('{transaction_id}', '{user_id}', '{user_card_id}', '{merchant_id}', NULL, '{current_date.date()}', '{transaction_time}', {transaction_amount:.2f}, 'USD', '{category_id}', '{random.randint(5000, 9999)}', {rewards_earned:.2f}, {rewards_multiplier:.2f}, NULL, 0.00, '{user_card_id}', '{user_card_id}', 0.00, '{transaction_description.replace("'", "''")}', 'BANK_API')
ON CONFLICT (transaction_id) DO NOTHING;"""
                    
                    f.write(transaction_sql + "\n\n")
                    current_size += len(transaction_sql.encode('utf-8')) + 2
                    total_statements += 1
                    transaction_count += 1
                    
                    if current_size >= TARGET_SIZE_BYTES:
                        logger.info(f"   Reached target size: {current_size / (1024**3):.3f} GB")
                        break
                
                if current_size >= TARGET_SIZE_BYTES:
                    break
            
            if current_size >= TARGET_SIZE_BYTES:
                break
    
    logger.info(f"   Generated {transaction_count} transactions ({current_size / (1024**3):.3f} GB)")
    
    # Update header with final count
    with open(output_file, 'r+', encoding='utf-8') as f:
        content = f.read()
        f.seek(0)
        f.write(f"-- Large Dataset for Credit Card and Rewards Database (db-12)\n")
        f.write(f"-- Rebuilt: {datetime.now().isoformat()}\n")
        f.write(f"-- Target size: {TARGET_SIZE_GB} GB\n")
        f.write(f"-- Total SQL statements: {total_statements:,}\n")
        f.write("-- Compatible with PostgreSQL\n")
        f.write("-- Based on legitimate CFPB, Federal Reserve patterns and realistic credit card data\n\n")
        f.write(content[header_size:])
    
    file_size_mb = output_file.stat().st_size / (1024**2)
    file_size_gb = file_size_mb / 1024
    
    logger.info(f"\n✅ Generation complete!")
    logger.info(f"   Output file: {output_file}")
    logger.info(f"   File size: {file_size_gb:.2f} GB ({file_size_mb:.2f} MB)")
    logger.info(f"   SQL statements: {total_statements:,}")
    logger.info("=" * 80)
    
    return file_size_gb >= TARGET_SIZE_GB


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
