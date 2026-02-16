-- Credit Card Database Sample Data
-- Production sample data for credit card and rewards optimization system

-- Insert sample credit card issuers
INSERT INTO credit_card_issuers (issuer_id, issuer_name, issuer_code, bank_type, country_code, website_url, customer_service_phone, total_cards_issued, market_share_percentage, cfpb_complaint_count, cfpb_complaint_resolution_rate) VALUES
('issuer_001', 'Chase Bank', 'CHASE', 'National', 'US', 'https://www.chase.com', '1-800-935-9935', 150000000, 18.5, 1250, 87.3),
('issuer_002', 'American Express', 'AMEX', 'National', 'US', 'https://www.americanexpress.com', '1-800-528-4800', 120000000, 15.2, 890, 92.1),
('issuer_003', 'Bank of America', 'BOA', 'National', 'US', 'https://www.bankofamerica.com', '1-800-432-1000', 95000000, 12.8, 1100, 85.7),
('issuer_004', 'Citibank', 'CITI', 'National', 'US', 'https://www.citi.com', '1-800-374-9700', 85000000, 11.3, 980, 88.5),
('issuer_005', 'Capital One', 'CAPONE', 'National', 'US', 'https://www.capitalone.com', '1-800-227-4825', 75000000, 9.7, 650, 91.2),
('issuer_006', 'Wells Fargo', 'WELLS', 'National', 'US', 'https://www.wellsfargo.com', '1-800-869-3557', 70000000, 8.9, 1350, 83.4),
('issuer_007', 'Discover', 'DISCOVER', 'National', 'US', 'https://www.discover.com', '1-800-347-2683', 60000000, 7.6, 420, 94.5),
('issuer_008', 'US Bank', 'USBANK', 'National', 'US', 'https://www.usbank.com', '1-800-872-2657', 45000000, 5.8, 580, 89.3);

-- Insert sample rewards categories
INSERT INTO rewards_categories (category_id, category_name, category_code, parent_category_id, category_description, merchant_category_codes, is_bonus_category, typical_multiplier) VALUES
('cat_001', 'Dining', 'DINING', NULL, 'Restaurants, cafes, bars, and food delivery services', '5812,5813,5814,5462', TRUE, 3.0),
('cat_002', 'Gas Stations', 'GAS', NULL, 'Gas stations and fuel purchases', '5541,5542', TRUE, 2.0),
('cat_003', 'Groceries', 'GROCERIES', NULL, 'Supermarkets and grocery stores', '5411', TRUE, 2.0),
('cat_004', 'Travel', 'TRAVEL', NULL, 'Airlines, hotels, car rentals, and travel agencies', '3000-3999,3501-3780,4511,4722', TRUE, 3.0),
('cat_005', 'Airlines', 'AIRLINES', 'cat_004', 'Airline tickets and airline-related purchases', '3000-3999', TRUE, 5.0),
('cat_006', 'Hotels', 'HOTELS', 'cat_004', 'Hotels, motels, and accommodations', '3501-3780', TRUE, 3.0),
('cat_007', 'Streaming Services', 'STREAMING', NULL, 'Netflix, Spotify, Hulu, and other streaming subscriptions', '5734,5815', TRUE, 1.5),
('cat_008', 'Drugstores', 'DRUGSTORES', NULL, 'Pharmacies and drugstores', '5912', TRUE, 1.5),
('cat_009', 'Entertainment', 'ENTERTAINMENT', NULL, 'Movies, concerts, sporting events', '7832,7922,7911', FALSE, 1.0),
('cat_010', 'General Purchases', 'GENERAL', NULL, 'All other purchases', NULL, FALSE, 1.0);

-- Insert sample credit cards
INSERT INTO credit_cards (card_id, issuer_id, card_name, card_type, annual_fee, annual_fee_waived_first_year, signup_bonus_points, signup_bonus_cash, signup_bonus_spend_requirement, signup_bonus_timeframe_months, apr_purchase, apr_balance_transfer, apr_cash_advance, foreign_transaction_fee_percentage, credit_score_min, credit_score_max, card_network, card_level, metal_card, authorized_user_fee, card_agreement_url, is_active, launch_date) VALUES
('card_001', 'issuer_001', 'Chase Sapphire Preferred', 'Travel', 95.00, TRUE, 60000, NULL, 4000.00, 3, 21.49, 21.49, 25.24, 0.00, 690, 850, 'Visa', 'Signature', FALSE, 0.00, 'https://www.chase.com/agreements', TRUE, '2009-08-01'),
('card_002', 'issuer_001', 'Chase Sapphire Reserve', 'Travel', 550.00, FALSE, 60000, NULL, 4000.00, 3, 22.49, 22.49, 26.24, 0.00, 720, 850, 'Visa', 'Signature', TRUE, 75.00, 'https://www.chase.com/agreements', TRUE, '2016-08-21'),
('card_003', 'issuer_002', 'American Express Gold Card', 'Travel', 250.00, FALSE, 60000, NULL, 4000.00, 6, NULL, NULL, 25.99, 0.00, 700, 850, 'Amex', 'Gold', TRUE, 0.00, 'https://www.americanexpress.com/terms', TRUE, '2018-10-04'),
('card_004', 'issuer_002', 'American Express Platinum Card', 'Travel', 695.00, FALSE, 80000, NULL, 6000.00, 6, NULL, NULL, 28.24, 0.00, 720, 850, 'Amex', 'Platinum', TRUE, 175.00, 'https://www.americanexpress.com/terms', TRUE, '1984-01-01'),
('card_005', 'issuer_003', 'Bank of America Premium Rewards', 'Travel', 95.00, FALSE, 50000, NULL, 3000.00, 3, 18.49, 18.49, 24.49, 0.00, 700, 850, 'Visa', 'Signature', FALSE, 0.00, 'https://www.bankofamerica.com/agreements', TRUE, '2017-09-01'),
('card_006', 'issuer_004', 'Citi Double Cash Card', 'Cash Back', 0.00, FALSE, NULL, NULL, NULL, NULL, 19.24, 19.24, 25.24, 3.00, 670, 850, 'Mastercard', 'Standard', FALSE, 0.00, 'https://www.citi.com/agreements', TRUE, '2014-08-01'),
('card_007', 'issuer_005', 'Capital One Venture X', 'Travel', 395.00, FALSE, 75000, NULL, 4000.00, 3, 19.99, 19.99, 26.99, 0.00, 700, 850, 'Visa', 'Signature', TRUE, 0.00, 'https://www.capitalone.com/agreements', TRUE, '2021-11-15'),
('card_008', 'issuer_006', 'Wells Fargo Active Cash', 'Cash Back', 0.00, FALSE, NULL, 200.00, 1000.00, 3, 20.24, 20.24, 24.99, 3.00, 670, 850, 'Visa', 'Standard', FALSE, 0.00, 'https://www.wellsfargo.com/agreements', TRUE, '2021-07-01'),
('card_009', 'issuer_007', 'Discover it Cash Back', 'Cash Back', 0.00, FALSE, NULL, NULL, NULL, NULL, 13.99, 13.99, 24.99, 0.00, 660, 850, 'Discover', 'Standard', FALSE, 0.00, 'https://www.discover.com/agreements', TRUE, '1986-01-01'),
('card_010', 'issuer_008', 'US Bank Altitude Reserve', 'Travel', 400.00, FALSE, 50000, NULL, 4500.00, 3, 21.24, 21.24, 25.24, 0.00, 720, 850, 'Visa', 'Infinite', TRUE, 0.00, 'https://www.usbank.com/agreements', TRUE, '2018-03-01');

-- Insert sample card rewards structure
INSERT INTO card_rewards_structure (reward_structure_id, card_id, category_id, rewards_multiplier, rewards_type, points_per_dollar, cash_back_percentage, annual_spend_limit, quarterly_spend_limit, monthly_spend_limit, effective_start_date, effective_end_date, is_active) VALUES
('reward_001', 'card_001', 'cat_001', 2.0, 'Points', 2.0, NULL, NULL, NULL, NULL, '2020-01-01', NULL, TRUE),
('reward_002', 'card_001', 'cat_004', 2.0, 'Points', 2.0, NULL, NULL, NULL, NULL, '2020-01-01', NULL, TRUE),
('reward_003', 'card_001', 'cat_010', 1.0, 'Points', 1.0, NULL, NULL, NULL, NULL, '2020-01-01', NULL, TRUE),
('reward_004', 'card_002', 'cat_001', 3.0, 'Points', 3.0, NULL, NULL, NULL, NULL, '2016-08-21', NULL, TRUE),
('reward_005', 'card_002', 'cat_004', 3.0, 'Points', 3.0, NULL, NULL, NULL, NULL, '2016-08-21', NULL, TRUE),
('reward_006', 'card_002', 'cat_010', 1.0, 'Points', 1.0, NULL, NULL, NULL, NULL, '2016-08-21', NULL, TRUE),
('reward_007', 'card_003', 'cat_001', 4.0, 'Points', 4.0, NULL, 25000.00, NULL, NULL, '2018-10-04', NULL, TRUE),
('reward_008', 'card_003', 'cat_003', 4.0, 'Points', 4.0, NULL, 25000.00, NULL, NULL, '2018-10-04', NULL, TRUE),
('reward_009', 'card_003', 'cat_010', 1.0, 'Points', 1.0, NULL, NULL, NULL, NULL, '2018-10-04', NULL, TRUE),
('reward_010', 'card_006', 'cat_010', 2.0, 'Cash Back', NULL, 2.0, NULL, NULL, NULL, '2014-08-01', NULL, TRUE),
('reward_011', 'card_008', 'cat_010', 2.0, 'Cash Back', NULL, 2.0, NULL, NULL, NULL, '2021-07-01', NULL, TRUE),
('reward_012', 'card_009', 'cat_001', 5.0, 'Cash Back', NULL, 5.0, NULL, NULL, 1500.00, '2024-01-01', '2024-03-31', TRUE),
('reward_013', 'card_009', 'cat_002', 5.0, 'Cash Back', NULL, 5.0, NULL, NULL, 1500.00, '2024-04-01', '2024-06-30', TRUE),
('reward_014', 'card_009', 'cat_003', 5.0, 'Cash Back', NULL, 5.0, NULL, NULL, 1500.00, '2024-07-01', '2024-09-30', TRUE),
('reward_015', 'card_009', 'cat_010', 1.0, 'Cash Back', NULL, 1.0, NULL, NULL, NULL, '2024-01-01', NULL, TRUE);

-- Insert sample merchants
INSERT INTO merchants (merchant_id, merchant_name, merchant_category_code, merchant_category, parent_merchant_id, website_url, is_chain, chain_location_count) VALUES
('merchant_001', 'Starbucks', '5812', 'Dining', NULL, 'https://www.starbucks.com', TRUE, 15000),
('merchant_002', 'Shell', '5541', 'Gas Stations', NULL, 'https://www.shell.com', TRUE, 14000),
('merchant_003', 'Whole Foods Market', '5411', 'Groceries', NULL, 'https://www.wholefoodsmarket.com', TRUE, 500),
('merchant_004', 'United Airlines', '3000', 'Airlines', NULL, 'https://www.united.com', TRUE, NULL),
('merchant_005', 'Marriott Hotels', '3501', 'Hotels', NULL, 'https://www.marriott.com', TRUE, 8000),
('merchant_006', 'Amazon', '5999', 'General Purchases', NULL, 'https://www.amazon.com', TRUE, NULL),
('merchant_007', 'Netflix', '5734', 'Streaming Services', NULL, 'https://www.netflix.com', TRUE, NULL),
('merchant_008', 'CVS Pharmacy', '5912', 'Drugstores', NULL, 'https://www.cvs.com', TRUE, 10000),
('merchant_009', 'Walmart', '5331', 'General Purchases', NULL, 'https://www.walmart.com', TRUE, 4700),
('merchant_010', 'Target', '5331', 'General Purchases', NULL, 'https://www.target.com', TRUE, 1900);

-- Insert sample bank offers
INSERT INTO bank_offers (offer_id, issuer_id, offer_name, offer_description, merchant_name, merchant_category, offer_type, discount_amount, discount_percentage, minimum_spend, maximum_discount, points_bonus_multiplier, offer_start_date, offer_end_date, redemption_deadline, terms_and_conditions, is_targeted, activation_required) VALUES
('offer_001', 'issuer_002', 'Spend $75+ at Starbucks, Get $15 Back', 'Get $15 back when you spend $75 or more at Starbucks', 'Starbucks', 'Dining', 'Statement Credit', 15.00, NULL, 75.00, 15.00, NULL, '2024-01-01', '2024-03-31', '2024-04-30', 'Valid for in-store and online purchases', FALSE, TRUE),
('offer_002', 'issuer_001', '10% Back at Gas Stations', 'Earn 10% cash back on gas station purchases up to $1,500', 'Shell', 'Gas Stations', 'Cash Back', NULL, 10.00, NULL, NULL, NULL, '2024-02-01', '2024-04-30', '2024-05-31', 'Up to $1,500 in purchases', FALSE, TRUE),
('offer_003', 'issuer_002', '5x Points at Grocery Stores', 'Earn 5x Membership Rewards points at grocery stores', 'Whole Foods Market', 'Groceries', 'Points Bonus', NULL, NULL, NULL, NULL, 5.0, '2024-01-15', '2024-06-30', NULL, 'Up to $25,000 in purchases per year', FALSE, TRUE),
('offer_004', 'issuer_003', '$200 Off United Airlines', 'Get $200 statement credit on United Airlines purchases over $500', 'United Airlines', 'Airlines', 'Statement Credit', 200.00, NULL, 500.00, 200.00, NULL, '2024-03-01', '2024-05-31', '2024-06-30', 'Valid for flights and vacation packages', TRUE, TRUE),
('offer_005', 'issuer_001', '20% Off Streaming Services', 'Get 20% cash back on streaming service subscriptions', 'Netflix', 'Streaming Services', 'Cash Back', NULL, 20.00, NULL, NULL, NULL, '2024-01-01', '2024-12-31', '2025-01-31', 'Up to $12 per month', FALSE, TRUE);

-- Insert sample card offer eligibility
INSERT INTO card_offer_eligibility (eligibility_id, offer_id, card_id, eligibility_status, activation_status) VALUES
('elig_001', 'offer_001', 'card_003', 'Eligible', 'Not Activated'),
('elig_002', 'offer_001', 'card_004', 'Eligible', 'Activated'),
('elig_003', 'offer_002', 'card_001', 'Eligible', 'Activated'),
('elig_004', 'offer_002', 'card_002', 'Eligible', 'Not Activated'),
('elig_005', 'offer_003', 'card_003', 'Eligible', 'Activated'),
('elig_006', 'offer_004', 'card_005', 'Targeted', 'Not Activated'),
('elig_007', 'offer_005', 'card_001', 'Eligible', 'Activated'),
('elig_008', 'offer_005', 'card_002', 'Eligible', 'Activated');
