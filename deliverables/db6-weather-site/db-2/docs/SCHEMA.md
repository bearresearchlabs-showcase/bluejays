# LUCASA Database Schema Documentation

## Database Overview

**Database Name:** LUCASA Mini-Supermarket POS System
**Engine:** MySQL/InnoDB
**Character Set:** UTF-8 (utf8_unicode_ci)
**Total Tables:** 58
**Database Type:** Point of Sale (POS) and Inventory Management System

### Business Context

LUCASA is a comprehensive Point of Sale system for a mini-supermarket operation. The database manages:
- Sales transactions and payments
- Inventory tracking across multiple locations
- Product and item kit management
- Customer and supplier relationships
- Employee management and permissions
- Store accounts and gift cards
- Tax calculations and pricing tiers
- Integration with eTIMS (Electronic Tax Invoice Management System) for Kenya

---

## Database Architecture

### Core Design Principles

1. **Multi-Location Support**: The system supports multiple store locations with location-specific pricing and inventory
2. **Flexible Pricing**: Supports multiple price tiers, location-based pricing, employee-specific pricing, and promotional pricing
3. **Comprehensive Tax System**: Up to 5 different tax rates per transaction with cumulative tax support
4. **Audit Trail**: Tracks changes to employees and sales with full audit history
5. **Soft Deletes**: Most tables use a `deleted` flag instead of hard deletes to preserve data integrity
6. **ERP Integration**: Built-in support for external ERP system integration
7. **eTIMS Compliance**: Integrated support for Kenya's tax invoice management system

### Key Technical Features

- **Decimal Precision**: Financial values stored as `decimal(23,10)` for high precision
- **Timestamp Tracking**: Automatic timestamp tracking for transactions
- **Composite Keys**: Extensive use of composite primary keys for relationship tables
- **Normalized Design**: Well-normalized structure with separate tables for taxes, pricing tiers, and line items

---

## Module Groupings

### 1. People & Accounts Module
Core entities representing individuals and their roles in the system.

| Table | Purpose |
|-------|---------|
| `phppos_people` | Base table for all persons (customers, employees, suppliers, expenses) |
| `phppos_customers` | Customer-specific information and account balances |
| `phppos_employees` | Employee login credentials and settings |
| `phppos_employees_audit` | Audit trail for employee changes |
| `phppos_employees_locations` | Employee-to-location assignments |
| `phppos_suppliers` | Supplier information |
| `phppos_expenses` | Expense tracking linked to people |

### 2. Products & Inventory Module
Product definitions, inventory tracking, and stock management.

| Table | Purpose |
|-------|---------|
| `phppos_items` | Individual product/item definitions |
| `phppos_items_taxes` | Tax configurations for items |
| `phppos_items_tier_prices` | Tier-based pricing for items |
| `phppos_item_kits` | Product bundles/kits |
| `phppos_item_kits_taxes` | Tax configurations for item kits |
| `phppos_item_kits_tier_prices` | Tier-based pricing for item kits |
| `phppos_item_kit_items` | Items contained within kits |
| `phppos_inventory` | Inventory transaction history |
| `phppos_giftcards` | Gift card balances and tracking |

### 3. Location-Based Pricing & Inventory Module
Location-specific overrides for pricing and stock levels.

| Table | Purpose |
|-------|---------|
| `phppos_location_items` | Location-specific item pricing and inventory |
| `phppos_location_items_taxes` | Location-specific item tax overrides |
| `phppos_location_items_tier_prices` | Location-specific tier pricing for items |
| `phppos_location_item_kits` | Location-specific item kit pricing |
| `phppos_location_item_kits_taxes` | Location-specific item kit tax overrides |
| `phppos_location_item_kits_tier_prices` | Location-specific tier pricing for item kits |

### 4. Employee-Based Pricing & Inventory Module
Employee-specific pricing and inventory tracking (for commission/tracking purposes).

| Table | Purpose |
|-------|---------|
| `phppos_employee_items` | Employee-specific item pricing and inventory |
| `phppos_employee_items_taxes` | Employee-specific item tax configurations |
| `phppos_employee_items_tier_prices` | Employee-specific tier pricing for items |
| `phppos_employee_item_kits` | Employee-specific item kit pricing |
| `phppos_employee_item_kits_taxes` | Employee-specific item kit tax configurations |
| `phppos_employee_item_kits_tier_prices` | Employee-specific tier pricing for item kits |
| `phppos_employee_inventory` | Employee-specific inventory transactions |

### 5. Sales Module
Transaction processing, line items, taxes, and payments.

| Table | Purpose |
|-------|---------|
| `phppos_sales` | Main sales transaction header |
| `phppos_sales_audit` | Audit trail for sales changes |
| `phppos_sales_items` | Individual items sold in a transaction |
| `phppos_sales_items_taxes` | Taxes applied to sold items |
| `phppos_sales_item_kits` | Item kits sold in a transaction |
| `phppos_sales_item_kits_taxes` | Taxes applied to sold item kits |
| `phppos_sales_payments` | Payment methods and amounts for sales |
| `phppos_store_accounts` | Customer store account transactions |

### 6. Employee Sales Module
Separate tracking for employee sales (possibly for testing or internal transactions).

| Table | Purpose |
|-------|---------|
| `phppos_employee_sales` | Employee sales transaction header |
| `phppos_employee_sales_items` | Items in employee sales |
| `phppos_employee_sales_items_taxes` | Taxes for employee sale items |
| `phppos_employee_sales_item_kits` | Item kits in employee sales |
| `phppos_employee_sales_item_kits_taxes` | Taxes for employee sale item kits |
| `phppos_employee_sales_payments` | Payments for employee sales |

### 7. Receiving/Purchasing Module
Stock receiving from suppliers.

| Table | Purpose |
|-------|---------|
| `phppos_receivings` | Receiving transaction header |
| `phppos_receivings_items` | Items received from suppliers |

### 8. Allocations Module
Stock allocations between employees or locations.

| Table | Purpose |
|-------|---------|
| `phppos_allocations` | Allocation transaction header |
| `phppos_allocations_items` | Items allocated in transaction |

### 9. System & Configuration Module
Application settings, security, and permissions.

| Table | Purpose |
|-------|---------|
| `phppos_app_config` | Application configuration key-value pairs |
| `phppos_app_files` | File storage (logos, images) |
| `phppos_locations` | Store location definitions |
| `phppos_modules` | System module definitions |
| `phppos_modules_actions` | Available actions within modules |
| `phppos_permissions` | User permissions by module |
| `phppos_permissions_actions` | User permissions for specific actions |
| `phppos_price_tiers` | Price tier definitions |
| `phppos_register_log` | Cash register open/close log |
| `phppos_sessions` | User session management |
| `phppos_admin_otp` | One-time passwords for admin access |

---

## Complete Table Reference

### 1. phppos_admin_otp
**Purpose:** One-time password management for administrative access

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| otp_id | int(11) | PRIMARY KEY | Unique OTP identifier |
| otp_code | varchar(10) | NOT NULL | The OTP code |
| username | varchar(255) | NOT NULL | Associated username |
| created_at | timestamp | DEFAULT current_timestamp() | Creation timestamp |
| expires_at | timestamp | NOT NULL | Expiration timestamp |
| used | tinyint(1) | DEFAULT 0 | Whether OTP has been used |
| ip_address | varchar(45) | NULL | IP address of request |

### 2. phppos_allocations
**Purpose:** Stock allocation transactions between employees or locations

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| allocation_id | int(11) | PRIMARY KEY | Unique allocation identifier |
| allocation_time | timestamp | DEFAULT current_timestamp() | When allocation occurred |
| supplier_id | int(11) | NULL | Related supplier |
| employee_id | int(11) | NOT NULL DEFAULT 0 | Employee creating allocation |
| allocated_employee_id | int(11) | NOT NULL | Employee receiving allocation |
| location_id | int(11) | NOT NULL | Location for allocation |
| comment | text | NOT NULL | Allocation notes |
| payment_type | varchar(255) | NULL | Payment method |
| deleted | int(11) | DEFAULT 0 | Soft delete flag |
| deleted_by | int(11) | NULL | Who deleted the record |

### 3. phppos_allocations_items
**Purpose:** Line items for allocation transactions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| allocation_id | int(11) | PRIMARY KEY (composite) | Reference to allocation |
| item_id | int(11) | PRIMARY KEY (composite) | Reference to item |
| line | int(11) | PRIMARY KEY (composite) | Line number in transaction |
| description | varchar(255) | NULL | Item description override |
| serialnumber | varchar(255) | NULL | Serial number if applicable |
| quantity_purchased | decimal(23,10) | DEFAULT 0 | Quantity allocated |
| item_cost_price | decimal(23,10) | NOT NULL | Cost price |
| item_wholesale_price | decimal(23,10) | NULL | Wholesale price |
| item_unit_price | decimal(23,10) | NOT NULL | Unit price |
| discount_percent | int(11) | DEFAULT 0 | Discount percentage |

### 4. phppos_app_config
**Purpose:** Application configuration settings (key-value store)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| key | varchar(255) | PRIMARY KEY | Configuration key |
| value | text | NOT NULL | Configuration value |

**Key Settings:**
- `company`: Store name (LUCASA MINI-SUPERMARKET)
- `currency_symbol`: Currency (Ksh - Kenyan Shilling)
- `default_tax_1_name`: Primary tax name (Vat)
- `default_tax_1_rate`: Primary tax rate (16%)
- `etims_*`: eTIMS integration settings for Kenya tax compliance

### 5. phppos_app_files
**Purpose:** Binary file storage (company logos, product images)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| file_id | int(11) | PRIMARY KEY | Unique file identifier |
| file_name | varchar(255) | NOT NULL | Original filename |
| file_data | longblob | NOT NULL | Binary file data |

### 6. phppos_customers
**Purpose:** Customer information and account balances

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| person_id | int(11) | FOREIGN KEY → phppos_people | Link to person record |
| account_number | varchar(255) | UNIQUE | Customer account number |
| customer_number | varchar(255) | UNIQUE | Customer ID number |
| company_name | varchar(255) | NOT NULL | Company/Business name |
| location_id | int(11) | NULL | Primary location |
| balance | decimal(23,10) | DEFAULT 0 | Store account balance |
| taxable | int(11) | DEFAULT 1 | Whether customer is taxable |
| tax_id | varchar(255) | NULL | Tax identification number |
| cc_token | varchar(255) | NULL | Credit card token |
| cc_preview | varchar(255) | NULL | Masked credit card number |
| card_issuer | varchar(255) | DEFAULT '' | Credit card issuer |
| tier_id | int(11) | FOREIGN KEY → phppos_price_tiers | Price tier |
| deleted | int(11) | DEFAULT 0 | Soft delete flag |

**Foreign Keys:**
- `person_id` → `phppos_people(person_id)`
- `tier_id` → `phppos_price_tiers(id)`

### 7. phppos_employees
**Purpose:** Employee accounts and authentication

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| person_id | int(11) | FOREIGN KEY → phppos_people | Link to person record |
| username | varchar(255) | UNIQUE | Login username |
| password | varchar(255) | NOT NULL | Hashed password |
| language | varchar(255) | NULL | Preferred language |
| account_number | varchar(255) | NULL | Employee account number |
| company_name | varchar(255) | NULL | Company name |
| balance | decimal(23,10) | DEFAULT 0 | Employee account balance |
| tier_id | int(11) | NULL | Price tier |
| deleted | int(11) | DEFAULT 0 | Soft delete flag |
| hide_from_switch_user | tinyint(1) | DEFAULT 0 | Hide from user switcher |

**Foreign Keys:**
- `person_id` → `phppos_people(person_id)`

### 8. phppos_employees_audit
**Purpose:** Audit trail for employee record changes

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| audit_id | int(11) | PRIMARY KEY | Unique audit record ID |
| employee_id | int(10) | NOT NULL | Employee being audited |
| action_type | varchar(50) | NOT NULL | CREATE, UPDATE, DELETE, PASSWORD_CHANGE |
| field_name | varchar(100) | NULL | Field that was changed |
| old_value | text | NULL | Previous value |
| new_value | text | NULL | New value |
| changed_by | int(10) | NOT NULL | Employee who made change |
| changed_at | timestamp | DEFAULT current_timestamp() | When change occurred |
| ip_address | varchar(45) | NULL | IP address of change |
| user_agent | varchar(255) | NULL | Browser/client info |
| notes | text | NULL | Additional notes |

### 9. phppos_employees_locations
**Purpose:** Many-to-many relationship between employees and locations

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| employee_id | int(11) | PRIMARY KEY (composite), FOREIGN KEY | Employee reference |
| location_id | int(11) | PRIMARY KEY (composite), FOREIGN KEY | Location reference |

**Foreign Keys:**
- `employee_id` → `phppos_employees(person_id)`
- `location_id` → `phppos_locations(location_id)`

### 10. phppos_employee_inventory
**Purpose:** Employee-specific inventory transactions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| trans_id | int(11) | PRIMARY KEY | Transaction ID |
| trans_items | int(11) | DEFAULT 0 | Item ID |
| trans_user | int(11) | DEFAULT 0 | User performing transaction |
| trans_date | timestamp | DEFAULT current_timestamp() | Transaction date |
| trans_comment | text | NOT NULL | Transaction notes |
| trans_inventory | decimal(23,10) | DEFAULT 0 | Inventory change amount |
| employee_id | int(11) | NOT NULL | Associated employee |
| location_id | int(11) | NOT NULL | Location of transaction |
| quantity_left | varchar(45) | NULL | Quantity remaining |
| quantity_before | varchar(255) | NULL | Quantity before transaction |

### 11. phppos_employee_items
**Purpose:** Employee-specific item pricing and inventory

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| employee_id | int(11) | PRIMARY KEY (composite) | Employee reference |
| item_id | int(11) | PRIMARY KEY (composite) | Item reference |
| location_id | int(11) | NULL | Location reference |
| location | varchar(255) | DEFAULT '' | Location description |
| cost_price | decimal(23,10) | NULL | Employee-specific cost price |
| wholesale_price | decimal(23,10) | NULL | Employee-specific wholesale price |
| unit_price | decimal(23,10) | NULL | Employee-specific unit price |
| promo_price | decimal(23,10) | NULL | Employee-specific promo price |
| start_date | date | NULL | Promotion start date |
| end_date | date | NULL | Promotion end date |
| quantity | decimal(23,10) | DEFAULT 0 | Employee's stock quantity |
| reorder_level | decimal(23,10) | NULL | Reorder threshold |
| override_default_tax | int(11) | DEFAULT 0 | Whether to override default taxes |

### 12. phppos_employee_items_taxes
**Purpose:** Tax configurations for employee-specific items

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | int(11) | PRIMARY KEY | Tax configuration ID |
| employee_id | int(11) | NOT NULL | Employee reference |
| item_id | int(11) | NOT NULL | Item reference |
| name | varchar(255) | NOT NULL | Tax name |
| percent | decimal(16,3) | NOT NULL | Tax percentage |
| cumulative | int(11) | DEFAULT 0 | Whether tax is cumulative |

**Unique Constraint:** (`employee_id`, `item_id`, `name`, `percent`)

### 13. phppos_employee_items_tier_prices
**Purpose:** Price tier overrides for employee-specific items

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| tier_id | int(11) | PRIMARY KEY (composite) | Price tier reference |
| item_id | int(11) | PRIMARY KEY (composite) | Item reference |
| employee_id | int(11) | PRIMARY KEY (composite) | Employee reference |
| unit_price | decimal(23,10) | DEFAULT 0 | Tier-specific price |
| percent_off | int(11) | NULL | Percentage discount |

### 14. phppos_employee_item_kits
**Purpose:** Employee-specific item kit pricing

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| employee_id | int(11) | PRIMARY KEY (composite) | Employee reference |
| item_kit_id | int(11) | PRIMARY KEY (composite) | Item kit reference |
| unit_price | decimal(23,10) | NULL | Employee-specific unit price |
| cost_price | decimal(23,10) | NULL | Employee-specific cost price |
| override_default_tax | int(11) | DEFAULT 0 | Whether to override default taxes |

### 15. phppos_employee_item_kits_taxes
**Purpose:** Tax configurations for employee-specific item kits

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | int(11) | PRIMARY KEY | Tax configuration ID |
| employee_id | int(11) | NOT NULL | Employee reference |
| item_kit_id | int(11) | NOT NULL | Item kit reference |
| name | varchar(255) | NOT NULL | Tax name |
| percent | decimal(16,3) | NOT NULL | Tax percentage |
| cumulative | int(11) | DEFAULT 0 | Whether tax is cumulative |

**Unique Constraint:** (`employee_id`, `item_kit_id`, `name`, `percent`)

### 16. phppos_employee_item_kits_tier_prices
**Purpose:** Price tier overrides for employee-specific item kits

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| tier_id | int(11) | PRIMARY KEY (composite) | Price tier reference |
| item_kit_id | int(11) | PRIMARY KEY (composite) | Item kit reference |
| employee_id | int(11) | PRIMARY KEY (composite) | Employee reference |
| unit_price | decimal(23,10) | DEFAULT 0 | Tier-specific price |
| percent_off | int(11) | NULL | Percentage discount |

### 17. phppos_employee_sales
**Purpose:** Employee sales transactions (separate from regular sales)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| sale_id | int(11) | PRIMARY KEY | Unique sale identifier |
| sale_time | timestamp | DEFAULT current_timestamp() | Sale timestamp |
| customer_id | int(11) | NULL | Customer reference |
| employee_id | int(11) | DEFAULT 0 | Selling employee |
| comment | text | NOT NULL | Sale notes |
| show_comment_on_receipt | int(11) | DEFAULT 0 | Display comment on receipt |
| payment_type | varchar(255) | NULL | Primary payment method |
| cc_ref_no | varchar(255) | NOT NULL | Credit card reference |
| auth_code | varchar(255) | DEFAULT '' | Authorization code |
| deleted | int(11) | DEFAULT 0 | Soft delete flag |
| deleted_by | int(11) | NULL | Who deleted the sale |
| suspended | int(11) | DEFAULT 0 | Whether sale is suspended |
| store_account_payment | int(11) | DEFAULT 0 | Paid from store account |
| location_id | int(11) | NOT NULL | Sale location |
| etims_invoice_number | varchar(255) | NULL | eTIMS invoice number |
| etims_scu_id | varchar(255) | NULL | eTIMS sales control unit ID |
| etims_cu_inv_no | varchar(255) | NULL | eTIMS control unit invoice number |
| etims_internal_data | varchar(255) | NULL | eTIMS internal data |
| etims_receipt_signature | varchar(255) | NULL | eTIMS receipt signature |
| etims_signature_link | text | NULL | eTIMS signature verification link |
| etims_version | varchar(50) | NULL | eTIMS version |

### 18. phppos_employee_sales_items
**Purpose:** Line items for employee sales

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| sale_id | int(11) | PRIMARY KEY (composite) | Sale reference |
| item_id | int(11) | PRIMARY KEY (composite) | Item reference |
| line | int(11) | PRIMARY KEY (composite) | Line number |
| description | varchar(255) | NULL | Item description override |
| serialnumber | varchar(255) | NULL | Serial number |
| quantity_purchased | decimal(23,10) | DEFAULT 0 | Quantity sold |
| item_cost_price | decimal(23,10) | NOT NULL | Cost price |
| item_unit_price | decimal(23,10) | NOT NULL | Selling price |
| discount_percent | int(11) | DEFAULT 0 | Discount percentage |

### 19. phppos_employee_sales_items_taxes
**Purpose:** Taxes applied to employee sale items

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| sale_id | int(11) | PRIMARY KEY (composite) | Sale reference |
| item_id | int(11) | PRIMARY KEY (composite) | Item reference |
| line | int(11) | PRIMARY KEY (composite) | Line number |
| name | varchar(255) | PRIMARY KEY (composite) | Tax name |
| percent | decimal(15,3) | PRIMARY KEY (composite) | Tax percentage |
| cumulative | int(11) | DEFAULT 0 | Whether tax is cumulative |

### 20. phppos_employee_sales_item_kits
**Purpose:** Item kits sold in employee sales

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| sale_id | int(11) | PRIMARY KEY (composite) | Sale reference |
| item_kit_id | int(11) | PRIMARY KEY (composite) | Item kit reference |
| line | int(11) | PRIMARY KEY (composite) | Line number |
| description | varchar(255) | NULL | Kit description override |
| quantity_purchased | decimal(23,10) | DEFAULT 0 | Quantity sold |
| item_kit_cost_price | decimal(23,10) | NOT NULL | Cost price |
| item_kit_unit_price | decimal(23,10) | NOT NULL | Selling price |
| discount_percent | int(11) | DEFAULT 0 | Discount percentage |

### 21. phppos_employee_sales_item_kits_taxes
**Purpose:** Taxes applied to employee sale item kits

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| sale_id | int(11) | PRIMARY KEY (composite) | Sale reference |
| item_kit_id | int(11) | PRIMARY KEY (composite) | Item kit reference |
| line | int(11) | PRIMARY KEY (composite) | Line number |
| name | varchar(255) | PRIMARY KEY (composite) | Tax name |
| percent | decimal(15,3) | PRIMARY KEY (composite) | Tax percentage |
| cumulative | int(11) | DEFAULT 0 | Whether tax is cumulative |

### 22. phppos_employee_sales_payments
**Purpose:** Payment records for employee sales

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| payment_id | int(11) | PRIMARY KEY | Unique payment ID |
| sale_id | int(11) | NOT NULL | Sale reference |
| payment_type | varchar(255) | NOT NULL | Payment method |
| payment_amount | decimal(23,10) | NOT NULL | Amount paid |
| truncated_card | varchar(255) | DEFAULT '' | Masked card number |
| card_issuer | varchar(255) | DEFAULT '' | Card issuer |
| payment_date | timestamp | DEFAULT current_timestamp() | Payment timestamp |

### 23. phppos_expenses
**Purpose:** Expense tracking

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| person_id | int(11) | NOT NULL | Person who incurred expense |
| expense_name | varchar(255) | NOT NULL | Expense description |
| category | varchar(255) | NULL | Expense category |
| amount_spent | decimal(23,10) | NOT NULL | Amount spent |
| date_created | timestamp | DEFAULT current_timestamp() | Date of expense |
| deleted | int(11) | DEFAULT 0 | Soft delete flag |

### 24. phppos_giftcards
**Purpose:** Gift card management

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| giftcard_id | int(11) | PRIMARY KEY | Unique gift card ID |
| giftcard_number | varchar(255) | UNIQUE | Gift card number |
| value | decimal(23,10) | NOT NULL | Current balance |
| customer_id | int(11) | NULL | Associated customer |
| deleted | int(11) | DEFAULT 0 | Soft delete flag |

### 25. phppos_inventory
**Purpose:** Inventory transaction history

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| trans_id | int(11) | PRIMARY KEY | Transaction ID |
| trans_items | int(11) | DEFAULT 0, FOREIGN KEY | Item ID |
| trans_user | int(11) | DEFAULT 0, FOREIGN KEY | User performing transaction |
| trans_date | timestamp | DEFAULT current_timestamp() | Transaction date |
| trans_comment | text | NOT NULL | Transaction notes |
| trans_inventory | decimal(23,10) | DEFAULT 0 | Inventory change amount |
| location_id | int(11) | NOT NULL, FOREIGN KEY | Location of transaction |
| quantity_left | varchar(45) | NULL | Quantity remaining |
| quantity_before | varchar(255) | NULL | Quantity before transaction |

**Foreign Keys:**
- `trans_items` → `phppos_items(item_id)`
- `trans_user` → `phppos_employees(person_id)`
- `location_id` → `phppos_locations(location_id)`

### 26. phppos_items
**Purpose:** Product/item master data

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| item_id | int(11) | PRIMARY KEY | Unique item identifier |
| name | varchar(255) | NOT NULL | Item name |
| category | varchar(255) | NOT NULL | Item category |
| supplier_id | int(11) | NULL | Default supplier |
| item_number | varchar(255) | UNIQUE | SKU/item number |
| product_id | varchar(255) | UNIQUE | Product ID |
| description | varchar(255) | NOT NULL | Item description |
| tax_included | int(11) | DEFAULT 0 | Whether price includes tax |
| cost_price | decimal(23,10) | NOT NULL | Cost price |
| wholesale_price | decimal(23,10) | NULL | Wholesale price |
| unit_price | decimal(23,10) | NOT NULL | Retail price |
| promo_price | decimal(23,10) | NULL | Promotional price |
| start_date | date | NULL | Promotion start date |
| end_date | date | NULL | Promotion end date |
| reorder_level | decimal(23,10) | NULL | Minimum stock threshold |
| allow_alt_description | tinyint(1) | NOT NULL | Allow description override |
| is_serialized | tinyint(1) | NOT NULL | Whether item is serialized |
| image_id | int(11) | NULL | Reference to product image |
| override_default_tax | int(11) | DEFAULT 0 | Whether to override default taxes |
| is_service | int(11) | DEFAULT 0 | Whether item is a service |
| deleted | int(11) | DEFAULT 0 | Soft delete flag |
| etims_tax_type | varchar(50) | NULL | eTIMS tax classification |

### 27. phppos_items_taxes
**Purpose:** Tax configurations for items

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | int(11) | PRIMARY KEY | Tax configuration ID |
| item_id | int(11) | NOT NULL | Item reference |
| name | varchar(255) | NOT NULL | Tax name |
| percent | decimal(15,3) | NOT NULL | Tax percentage |
| cumulative | int(11) | DEFAULT 0 | Whether tax is cumulative |

**Unique Constraint:** (`item_id`, `name`, `percent`)

### 28. phppos_items_tier_prices
**Purpose:** Price tier pricing for items

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| tier_id | int(11) | PRIMARY KEY (composite) | Price tier reference |
| item_id | int(11) | PRIMARY KEY (composite) | Item reference |
| unit_price | decimal(23,10) | DEFAULT 0 | Tier-specific price |
| percent_off | int(11) | NULL | Percentage discount |

### 29. phppos_item_kits
**Purpose:** Item kit/bundle definitions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| item_kit_id | int(11) | PRIMARY KEY | Unique item kit identifier |
| item_kit_number | varchar(255) | UNIQUE | Kit SKU/number |
| product_id | varchar(255) | UNIQUE | Product ID |
| name | varchar(255) | NOT NULL | Kit name |
| description | varchar(255) | NOT NULL | Kit description |
| category | varchar(255) | NOT NULL | Kit category |
| tax_included | int(11) | DEFAULT 0 | Whether price includes tax |
| unit_price | decimal(23,10) | NULL | Kit retail price |
| cost_price | decimal(23,10) | NULL | Kit cost price |
| override_default_tax | int(11) | DEFAULT 0 | Whether to override default taxes |
| deleted | int(11) | DEFAULT 0 | Soft delete flag |

### 30. phppos_item_kits_taxes
**Purpose:** Tax configurations for item kits

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | int(11) | PRIMARY KEY | Tax configuration ID |
| item_kit_id | int(11) | NOT NULL | Item kit reference |
| name | varchar(255) | NOT NULL | Tax name |
| percent | decimal(15,3) | NOT NULL | Tax percentage |
| cumulative | int(11) | DEFAULT 0 | Whether tax is cumulative |

**Unique Constraint:** (`item_kit_id`, `name`, `percent`)

### 31. phppos_item_kits_tier_prices
**Purpose:** Price tier pricing for item kits

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| tier_id | int(11) | PRIMARY KEY (composite) | Price tier reference |
| item_kit_id | int(11) | PRIMARY KEY (composite) | Item kit reference |
| unit_price | decimal(23,10) | DEFAULT 0 | Tier-specific price |
| percent_off | int(11) | NULL | Percentage discount |

### 32. phppos_item_kit_items
**Purpose:** Items contained within item kits

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| item_kit_id | int(11) | PRIMARY KEY (composite) | Item kit reference |
| item_id | int(11) | PRIMARY KEY (composite) | Item reference |
| quantity | decimal(23,10) | PRIMARY KEY (composite) | Quantity of item in kit |

### 33. phppos_locations
**Purpose:** Store location definitions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| location_id | int(11) | PRIMARY KEY | Unique location identifier |
| name | text | NULL | Location name |
| address | text | NULL | Location address |
| phone | text | NULL | Phone number |
| fax | text | NULL | Fax number |
| email | text | NULL | Email address |
| receive_stock_alert | text | NULL | Whether to receive stock alerts |
| stock_alert_email | text | NULL | Email for stock alerts |
| timezone | text | NULL | Location timezone |
| mailchimp_api_key | text | NULL | Mailchimp API key |
| enable_credit_card_processing | text | NULL | Enable CC processing |
| merchant_id | text | NULL | Payment processor merchant ID |
| merchant_password | text | NULL | Payment processor password |
| default_tax_1_rate | text | NULL | Location-specific tax 1 rate |
| default_tax_1_name | text | NULL | Location-specific tax 1 name |
| default_tax_2_rate | text | NULL | Location-specific tax 2 rate |
| default_tax_2_name | text | NULL | Location-specific tax 2 name |
| default_tax_2_cumulative | text | NULL | Whether tax 2 is cumulative |
| default_tax_3_rate | text | NULL | Location-specific tax 3 rate |
| default_tax_3_name | text | NULL | Location-specific tax 3 name |
| default_tax_4_rate | text | NULL | Location-specific tax 4 rate |
| default_tax_4_name | text | NULL | Location-specific tax 4 name |
| default_tax_5_rate | text | NULL | Location-specific tax 5 rate |
| default_tax_5_name | text | NULL | Location-specific tax 5 name |
| deleted | int(11) | DEFAULT 0 | Soft delete flag |

### 34. phppos_location_items
**Purpose:** Location-specific item pricing and inventory

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| location_id | int(11) | PRIMARY KEY (composite) | Location reference |
| item_id | int(11) | PRIMARY KEY (composite) | Item reference |
| location | varchar(255) | DEFAULT '' | Location description |
| cost_price | decimal(23,10) | NULL | Location-specific cost price |
| wholesale_price | decimal(23,10) | NULL | Location-specific wholesale price |
| unit_price | decimal(23,10) | NULL | Location-specific unit price |
| promo_price | decimal(23,10) | NULL | Location-specific promo price |
| start_date | date | NULL | Promotion start date |
| end_date | date | NULL | Promotion end date |
| quantity | decimal(23,10) | DEFAULT 0 | Stock quantity at location |
| reorder_level | decimal(23,10) | NULL | Location reorder threshold |
| override_default_tax | int(11) | DEFAULT 0 | Whether to override default taxes |

### 35. phppos_location_items_taxes
**Purpose:** Location-specific item tax configurations

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | int(11) | PRIMARY KEY | Tax configuration ID |
| location_id | int(11) | NOT NULL | Location reference |
| item_id | int(11) | NOT NULL | Item reference |
| name | varchar(255) | NOT NULL | Tax name |
| percent | decimal(16,3) | NOT NULL | Tax percentage |
| cumulative | int(11) | DEFAULT 0 | Whether tax is cumulative |

**Unique Constraint:** (`location_id`, `item_id`, `name`, `percent`)

### 36. phppos_location_items_tier_prices
**Purpose:** Location-specific tier pricing for items

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| tier_id | int(11) | PRIMARY KEY (composite) | Price tier reference |
| item_id | int(11) | PRIMARY KEY (composite) | Item reference |
| location_id | int(11) | PRIMARY KEY (composite) | Location reference |
| unit_price | decimal(23,10) | DEFAULT 0 | Tier-specific price |
| percent_off | int(11) | NULL | Percentage discount |

### 37. phppos_location_item_kits
**Purpose:** Location-specific item kit pricing

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| location_id | int(11) | PRIMARY KEY (composite) | Location reference |
| item_kit_id | int(11) | PRIMARY KEY (composite) | Item kit reference |
| unit_price | decimal(23,10) | NULL | Location-specific unit price |
| cost_price | decimal(23,10) | NULL | Location-specific cost price |
| override_default_tax | int(11) | DEFAULT 0 | Whether to override default taxes |

### 38. phppos_location_item_kits_taxes
**Purpose:** Location-specific item kit tax configurations

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | int(11) | PRIMARY KEY | Tax configuration ID |
| location_id | int(11) | NOT NULL | Location reference |
| item_kit_id | int(11) | NOT NULL | Item kit reference |
| name | varchar(255) | NOT NULL | Tax name |
| percent | decimal(16,3) | NOT NULL | Tax percentage |
| cumulative | int(11) | DEFAULT 0 | Whether tax is cumulative |

**Unique Constraint:** (`location_id`, `item_kit_id`, `name`, `percent`)

### 39. phppos_location_item_kits_tier_prices
**Purpose:** Location-specific tier pricing for item kits

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| tier_id | int(11) | PRIMARY KEY (composite) | Price tier reference |
| item_kit_id | int(11) | PRIMARY KEY (composite) | Item kit reference |
| location_id | int(11) | PRIMARY KEY (composite) | Location reference |
| unit_price | decimal(23,10) | DEFAULT 0 | Tier-specific price |
| percent_off | int(11) | NULL | Percentage discount |

### 40. phppos_modules
**Purpose:** System module definitions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| module_id | varchar(100) | PRIMARY KEY | Unique module identifier |
| name_lang_key | varchar(255) | UNIQUE | Language key for module name |
| desc_lang_key | varchar(255) | UNIQUE | Language key for description |
| sort | int(11) | NOT NULL | Display sort order |
| icon | varchar(255) | NOT NULL | Icon identifier |

### 41. phppos_modules_actions
**Purpose:** Available actions within modules

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| action_id | varchar(100) | PRIMARY KEY (composite) | Action identifier |
| module_id | varchar(100) | PRIMARY KEY (composite) | Module reference |
| action_name_key | varchar(100) | NOT NULL | Language key for action name |
| sort | int(11) | NOT NULL | Display sort order |

### 42. phppos_people
**Purpose:** Base table for all persons in the system

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| person_id | int(11) | PRIMARY KEY | Unique person identifier |
| first_name | varchar(255) | NOT NULL | First name |
| last_name | varchar(255) | NOT NULL | Last name |
| phone_number | varchar(255) | NOT NULL | Phone number |
| email | varchar(255) | NOT NULL | Email address |
| address_1 | varchar(255) | NOT NULL | Address line 1 |
| address_2 | varchar(255) | NOT NULL | Address line 2 |
| city | varchar(255) | NOT NULL | City |
| state | varchar(255) | NOT NULL | State/Province |
| zip | varchar(255) | NOT NULL | Postal code |
| country | varchar(255) | NOT NULL | Country |
| comments | text | NOT NULL | Notes about person |
| image_id | int(11) | NULL | Profile image reference |
| created_time | timestamp | NULL | Record creation time |
| updated_time | timestamp | NULL | Last update time |
| created_by | int(11) | NULL | Who created record |
| updated_by | int(11) | NULL | Who last updated record |

### 43. phppos_permissions
**Purpose:** Module-level permissions for users

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| module_id | varchar(100) | PRIMARY KEY (composite) | Module reference |
| person_id | int(11) | PRIMARY KEY (composite) | Person reference |

### 44. phppos_permissions_actions
**Purpose:** Action-level permissions for users

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| module_id | varchar(100) | PRIMARY KEY (composite) | Module reference |
| person_id | int(11) | PRIMARY KEY (composite) | Person reference |
| action_id | varchar(100) | PRIMARY KEY (composite) | Action reference |

### 45. phppos_price_tiers
**Purpose:** Price tier definitions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | int(11) | PRIMARY KEY | Unique tier identifier |
| name | varchar(255) | NOT NULL | Tier name |

### 46. phppos_receivings
**Purpose:** Stock receiving transaction header

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| receiving_id | int(11) | PRIMARY KEY | Unique receiving identifier |
| receiving_time | timestamp | DEFAULT current_timestamp() | Receiving timestamp |
| supplier_id | int(11) | NULL | Supplier reference |
| employee_id | int(11) | DEFAULT 0 | Employee processing receiving |
| comment | text | NOT NULL | Receiving notes |
| payment_type | varchar(255) | NULL | Payment method |
| deleted | int(11) | DEFAULT 0 | Soft delete flag |
| deleted_by | int(11) | NULL | Who deleted the record |
| location_id | int(11) | NOT NULL | Receiving location |

### 47. phppos_receivings_items
**Purpose:** Line items for receiving transactions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| receiving_id | int(11) | PRIMARY KEY (composite) | Receiving reference |
| item_id | int(11) | PRIMARY KEY (composite) | Item reference |
| line | int(11) | PRIMARY KEY (composite) | Line number |
| description | varchar(255) | NULL | Item description override |
| serialnumber | varchar(255) | NULL | Serial number |
| quantity_purchased | decimal(23,10) | DEFAULT 0 | Quantity received |
| item_cost_price | decimal(23,10) | NOT NULL | Cost price |
| item_wholesale_price | decimal(23,10) | NULL | Wholesale price |
| item_unit_price | decimal(23,10) | NOT NULL | Unit price |
| discount_percent | int(11) | DEFAULT 0 | Discount percentage |

### 48. phppos_register_log
**Purpose:** Cash register shift tracking

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| register_log_id | int(11) | PRIMARY KEY | Unique log entry ID |
| employee_id | int(11) | NOT NULL | Employee reference |
| shift_start | timestamp | NOT NULL | Shift start time |
| shift_end | timestamp | NOT NULL | Shift end time |
| open_amount | decimal(23,10) | NOT NULL | Opening cash amount |
| close_amount | decimal(23,10) | NOT NULL | Closing cash amount |
| cash_sales_amount | decimal(23,10) | NOT NULL | Cash sales during shift |
| deleted | int(11) | DEFAULT 0 | Soft delete flag |

### 49. phppos_sales
**Purpose:** Main sales transaction header

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| sale_id | int(11) | PRIMARY KEY | Unique sale identifier |
| sale_time | timestamp | DEFAULT current_timestamp() | Sale timestamp |
| customer_id | int(11) | NULL | Customer reference |
| employee_id | int(11) | DEFAULT 0 | Selling employee |
| comment | text | NULL | Sale notes |
| show_comment_on_receipt | int(11) | DEFAULT 0 | Display comment on receipt |
| invoice_number | int(11) | UNIQUE | Invoice number |
| payment_type | varchar(255) | NULL | Primary payment method |
| cc_ref_no | varchar(255) | NULL | Credit card reference |
| auth_code | varchar(255) | DEFAULT '' | Authorization code |
| deleted | int(11) | DEFAULT 0 | Soft delete flag |
| deleted_by | int(11) | NULL | Who deleted the sale |
| suspended | int(11) | DEFAULT 0 | Whether sale is suspended |
| allocated | int(11) | DEFAULT 0 | Whether stock is allocated |
| store_account_payment | int(11) | DEFAULT 0 | Paid from store account |
| location_id | int(11) | NULL | Sale location |
| erp_integration | int(11) | DEFAULT 0 | Whether sent to ERP |
| etims_invoice_number | varchar(255) | NULL | eTIMS invoice number |
| etims_scu_id | varchar(255) | NULL | eTIMS sales control unit ID |
| etims_cu_inv_no | varchar(255) | NULL | eTIMS control unit invoice number |
| etims_internal_data | varchar(255) | NULL | eTIMS internal data |
| etims_receipt_signature | varchar(255) | NULL | eTIMS receipt signature |
| etims_signature_link | text | NULL | eTIMS signature verification link |
| etims_version | varchar(50) | NULL | eTIMS version |

### 50. phppos_sales_audit
**Purpose:** Audit trail for sales changes

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| audit_id | int(11) | PRIMARY KEY | Unique audit record ID |
| sale_id | int(10) | NOT NULL | Sale being audited |
| action_type | varchar(50) | NOT NULL | CREATE, UPDATE, DELETE, SUSPEND, COMPLETE |
| field_name | varchar(100) | NULL | Field that was changed |
| old_value | text | NULL | Previous value |
| new_value | text | NULL | New value |
| changed_by | int(10) | NOT NULL | Employee who made change |
| changed_at | timestamp | DEFAULT current_timestamp() | When change occurred |
| ip_address | varchar(45) | NULL | IP address of change |
| user_agent | varchar(255) | NULL | Browser/client info |
| notes | text | NULL | Additional notes |

### 51. phppos_sales_items
**Purpose:** Line items for sales transactions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| sale_id | int(11) | PRIMARY KEY (composite) | Sale reference |
| item_id | int(11) | PRIMARY KEY (composite) | Item reference |
| line | int(11) | PRIMARY KEY (composite) | Line number |
| description | varchar(255) | NULL | Item description override |
| serialnumber | varchar(255) | NULL | Serial number |
| quantity_purchased | decimal(23,10) | DEFAULT 0 | Quantity sold |
| item_cost_price | decimal(23,10) | NOT NULL | Cost price |
| item_unit_price | decimal(23,10) | NOT NULL | Selling price |
| discount_percent | int(11) | DEFAULT 0 | Discount percentage |
| price_mode | varchar(255) | NULL | Pricing mode used |

### 52. phppos_sales_items_taxes
**Purpose:** Taxes applied to sale items

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| sale_id | int(11) | PRIMARY KEY (composite) | Sale reference |
| item_id | int(11) | PRIMARY KEY (composite) | Item reference |
| line | int(11) | PRIMARY KEY (composite) | Line number |
| name | varchar(255) | PRIMARY KEY (composite) | Tax name |
| percent | decimal(15,3) | PRIMARY KEY (composite) | Tax percentage |
| cumulative | int(11) | DEFAULT 0 | Whether tax is cumulative |

### 53. phppos_sales_item_kits
**Purpose:** Item kits sold in sales transactions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| sale_id | int(11) | PRIMARY KEY (composite) | Sale reference |
| item_kit_id | int(11) | PRIMARY KEY (composite) | Item kit reference |
| line | int(11) | PRIMARY KEY (composite) | Line number |
| description | varchar(255) | NULL | Kit description override |
| quantity_purchased | decimal(23,10) | DEFAULT 0 | Quantity sold |
| item_kit_cost_price | decimal(23,10) | NOT NULL | Cost price |
| item_kit_unit_price | decimal(23,10) | NOT NULL | Selling price |
| discount_percent | int(11) | DEFAULT 0 | Discount percentage |
| price_mode | varchar(255) | NULL | Pricing mode used |

### 54. phppos_sales_item_kits_taxes
**Purpose:** Taxes applied to sale item kits

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| sale_id | int(11) | PRIMARY KEY (composite) | Sale reference |
| item_kit_id | int(11) | PRIMARY KEY (composite) | Item kit reference |
| line | int(11) | PRIMARY KEY (composite) | Line number |
| name | varchar(255) | PRIMARY KEY (composite) | Tax name |
| percent | decimal(15,3) | PRIMARY KEY (composite) | Tax percentage |
| cumulative | int(11) | DEFAULT 0 | Whether tax is cumulative |

### 55. phppos_sales_payments
**Purpose:** Payment records for sales transactions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| payment_id | int(11) | PRIMARY KEY | Unique payment ID |
| sale_id | int(11) | NOT NULL | Sale reference |
| payment_type | varchar(255) | NOT NULL | Payment method |
| payment_amount | decimal(23,10) | NOT NULL | Amount paid |
| truncated_card | varchar(255) | DEFAULT '' | Masked card number |
| card_issuer | varchar(255) | DEFAULT '' | Card issuer |
| payment_date | timestamp | DEFAULT current_timestamp() | Payment timestamp |

### 56. phppos_sessions
**Purpose:** User session management

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| session_id | varchar(40) | PRIMARY KEY | Session identifier |
| ip_address | varchar(45) | NOT NULL | IP address |
| user_agent | varchar(120) | NOT NULL | Browser/client info |
| last_activity | int(10) UNSIGNED | NOT NULL | Last activity timestamp |
| user_data | text | NULL | Serialized session data |

### 57. phppos_store_accounts
**Purpose:** Customer store account transactions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| sno | int(11) | PRIMARY KEY | Unique transaction number |
| customer_id | int(11) | NOT NULL | Customer reference |
| sale_id | int(11) | NULL | Related sale |
| transaction_amount | decimal(23,10) | DEFAULT 0 | Transaction amount |
| date | timestamp | DEFAULT current_timestamp() | Transaction date |
| balance | decimal(23,10) | DEFAULT 0 | Running balance |
| comment | text | NOT NULL | Transaction notes |
| deleted | int(11) | DEFAULT 0 | Soft delete flag |

### 58. phppos_suppliers
**Purpose:** Supplier information

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| person_id | int(11) | NOT NULL | Link to person record |
| company_name | varchar(255) | NOT NULL | Supplier company name |
| account_number | varchar(255) | UNIQUE | Supplier account number |
| deleted | int(11) | DEFAULT 0 | Soft delete flag |

---

## Composite Primary Keys

The following tables use composite primary keys (multiple columns):

| Table | Composite Key Columns | Purpose |
|-------|----------------------|---------|
| phppos_allocations_items | allocation_id, item_id, line | Unique line items per allocation |
| phppos_employees_locations | employee_id, location_id | Many-to-many relationship |
| phppos_employee_items | employee_id, item_id | Employee-specific item settings |
| phppos_employee_items_tier_prices | tier_id, item_id, employee_id | 3-way pricing relationship |
| phppos_employee_item_kits | employee_id, item_kit_id | Employee-specific kit settings |
| phppos_employee_item_kits_tier_prices | tier_id, item_kit_id, employee_id | 3-way pricing relationship |
| phppos_employee_sales_items | sale_id, item_id, line | Unique line items per sale |
| phppos_employee_sales_items_taxes | sale_id, item_id, line, name, percent | Unique tax per line item |
| phppos_employee_sales_item_kits | sale_id, item_kit_id, line | Unique kit lines per sale |
| phppos_employee_sales_item_kits_taxes | sale_id, item_kit_id, line, name, percent | Unique tax per kit line |
| phppos_items_tier_prices | tier_id, item_id | Tier pricing for items |
| phppos_item_kits_tier_prices | tier_id, item_kit_id | Tier pricing for kits |
| phppos_item_kit_items | item_kit_id, item_id, quantity | Items in kit with quantities |
| phppos_location_items | location_id, item_id | Location-specific item settings |
| phppos_location_items_tier_prices | tier_id, item_id, location_id | 3-way pricing relationship |
| phppos_location_item_kits | location_id, item_kit_id | Location-specific kit settings |
| phppos_location_item_kits_tier_prices | tier_id, item_kit_id, location_id | 3-way pricing relationship |
| phppos_modules_actions | action_id, module_id | Module action definitions |
| phppos_permissions | module_id, person_id | Module permissions |
| phppos_permissions_actions | module_id, person_id, action_id | Action-level permissions |
| phppos_receivings_items | receiving_id, item_id, line | Unique line items per receiving |
| phppos_sales_items | sale_id, item_id, line | Unique line items per sale |
| phppos_sales_items_taxes | sale_id, item_id, line, name, percent | Unique tax per line item |
| phppos_sales_item_kits | sale_id, item_kit_id, line | Unique kit lines per sale |
| phppos_sales_item_kits_taxes | sale_id, item_kit_id, line, name, percent | Unique tax per kit line |

---

## Foreign Key Relationships

The database implements referential integrity through the following foreign key constraints:

### People & Accounts
```
phppos_customers.person_id → phppos_people.person_id
phppos_customers.tier_id → phppos_price_tiers.id
phppos_employees.person_id → phppos_people.person_id
phppos_employees_locations.employee_id → phppos_employees.person_id
phppos_employees_locations.location_id → phppos_locations.location_id
```

### Inventory
```
phppos_inventory.trans_items → phppos_items.item_id
phppos_inventory.trans_user → phppos_employees.person_id
phppos_inventory.location_id → phppos_locations.location_id
```

### Logical Relationships (not enforced by FK constraints)

While the database only has 8 explicit foreign key constraints, there are many logical relationships:

**Sales Relationships:**
- sales → customer_id, employee_id, location_id
- sales_items → sale_id, item_id
- sales_item_kits → sale_id, item_kit_id
- sales_payments → sale_id

**Receiving Relationships:**
- receivings → supplier_id, employee_id, location_id
- receivings_items → receiving_id, item_id

**Pricing Relationships:**
- location_items → location_id, item_id
- employee_items → employee_id, item_id
- items_tier_prices → tier_id, item_id

---

## Entity-Relationship Overview

### Core Entity Diagram

```
┌──────────────┐
│   PEOPLE     │ (Base table for all persons)
└──────┬───────┘
       │
       ├──────► CUSTOMERS (person_id, tier_id)
       │
       ├──────► EMPLOYEES (person_id) ──┬──► EMPLOYEES_LOCATIONS
       │                                 │
       │                                 └──► PERMISSIONS
       │
       └──────► SUPPLIERS (person_id)


┌──────────────┐
│    ITEMS     │ (Products)
└──────┬───────┘
       │
       ├──────► ITEMS_TAXES
       │
       ├──────► ITEMS_TIER_PRICES (tier_id)
       │
       ├──────► LOCATION_ITEMS (location_id, item_id)
       │        └──► LOCATION_ITEMS_TAXES
       │        └──► LOCATION_ITEMS_TIER_PRICES
       │
       ├──────► EMPLOYEE_ITEMS (employee_id, item_id)
       │        └──► EMPLOYEE_ITEMS_TAXES
       │        └──► EMPLOYEE_ITEMS_TIER_PRICES
       │
       └──────► INVENTORY (trans_items, location_id)


┌──────────────┐
│  ITEM_KITS   │ (Product bundles)
└──────┬───────┘
       │
       ├──────► ITEM_KIT_ITEMS (contains individual items)
       │
       ├──────► ITEM_KITS_TAXES
       │
       └──────► ITEM_KITS_TIER_PRICES


┌──────────────┐
│    SALES     │ (customer_id, employee_id, location_id)
└──────┬───────┘
       │
       ├──────► SALES_ITEMS (sale_id, item_id)
       │        └──► SALES_ITEMS_TAXES
       │
       ├──────► SALES_ITEM_KITS (sale_id, item_kit_id)
       │        └──► SALES_ITEM_KITS_TAXES
       │
       ├──────► SALES_PAYMENTS (sale_id)
       │
       └──────► SALES_AUDIT


┌──────────────┐
│  RECEIVINGS  │ (supplier_id, employee_id, location_id)
└──────┬───────┘
       │
       └──────► RECEIVINGS_ITEMS (receiving_id, item_id)


┌──────────────┐
│  LOCATIONS   │ (Store locations)
└──────────────┘
       │
       ├──────► LOCATION_ITEMS
       │
       ├──────► LOCATION_ITEM_KITS
       │
       └──────► EMPLOYEES_LOCATIONS
```

### Pricing Hierarchy

The system supports a sophisticated pricing hierarchy:

```
Base Price (items table)
    ↓
Location Override (location_items) [if exists]
    ↓
Employee Override (employee_items) [if exists]
    ↓
Tier Price (items_tier_prices, location_items_tier_prices, employee_items_tier_prices) [if customer has tier]
    ↓
Promotional Price (promo_price with date range) [if active]
    ↓
Final Price
```

---

## Important Indexes

### Primary Key Indexes
All tables have primary key indexes (automatically created with PRIMARY KEY constraint).

### Unique Indexes

| Table | Column(s) | Purpose |
|-------|-----------|---------|
| phppos_customers | account_number | Unique customer account |
| phppos_customers | customer_number | Unique customer ID |
| phppos_employees | username | Unique login username |
| phppos_giftcards | giftcard_number | Unique gift card |
| phppos_items | item_number | Unique SKU/item number |
| phppos_items | product_id | Unique product ID |
| phppos_item_kits | item_kit_number | Unique kit number |
| phppos_item_kits | product_id | Unique product ID |
| phppos_modules | name_lang_key | Unique module name |
| phppos_modules | desc_lang_key | Unique module description |
| phppos_sales | invoice_number | Unique invoice number |
| phppos_suppliers | account_number | Unique supplier account |

### Tax Unique Constraints
To prevent duplicate tax entries:
- `phppos_employee_items_taxes`: (employee_id, item_id, name, percent)
- `phppos_employee_item_kits_taxes`: (employee_id, item_kit_id, name, percent)
- `phppos_items_taxes`: (item_id, name, percent)
- `phppos_item_kits_taxes`: (item_kit_id, name, percent)
- `phppos_location_items_taxes`: (location_id, item_id, name, percent)
- `phppos_location_item_kits_taxes`: (location_id, item_kit_id, name, percent)

---

## Data Integrity Patterns

### Soft Delete Pattern
Most tables implement soft deletes using a `deleted` flag:
- `deleted = 0`: Active record
- `deleted = 1`: Logically deleted
- Often includes `deleted_by` to track who deleted the record

Tables with soft delete:
- customers, employees, items, item_kits, suppliers
- sales, receivings, allocations
- giftcards, expenses, store_accounts
- locations, register_log

### Audit Trail Pattern
Critical tables maintain full audit history:
- `phppos_employees_audit`: Tracks all employee changes
- `phppos_sales_audit`: Tracks all sales modifications

Audit fields include:
- action_type (CREATE, UPDATE, DELETE, etc.)
- field_name, old_value, new_value
- changed_by, changed_at
- ip_address, user_agent

### Timestamp Pattern
All transactional tables include timestamps:
- `sale_time`, `receiving_time`, `allocation_time`
- Default to `current_timestamp()`
- Immutable transaction timing

### Override Pattern
Three-level override system for pricing and taxes:
1. Base level (items/item_kits)
2. Location level (location_items/location_item_kits)
3. Employee level (employee_items/employee_item_kits)

Each level has:
- Price fields (cost_price, unit_price, wholesale_price, promo_price)
- `override_default_tax` flag
- Associated tax tables

---

## Special Features

### eTIMS Integration (Kenya Tax Compliance)
Multiple tables include eTIMS fields for compliance with Kenya Revenue Authority:
- `etims_invoice_number`: Official tax invoice number
- `etims_scu_id`: Sales Control Unit ID
- `etims_cu_inv_no`: Control Unit Invoice Number
- `etims_internal_data`: Internal transaction data
- `etims_receipt_signature`: Digital signature
- `etims_signature_link`: QR code/verification link
- `etims_version`: eTIMS protocol version

### ERP Integration
- `erp_integration` flag in sales table
- Configurable ERP endpoint in app_config
- Tracks which sales have been sent to external ERP systems

### Multi-Location Support
- Complete location-based pricing and inventory
- Location-specific tax rates (up to 5 different taxes)
- Employee-to-location assignments
- Location-specific configurations

### Store Account System
- Customer credit accounts tracked in `store_accounts`
- Running balance maintained
- Links to sales transactions
- Separate from regular payment processing

### Price Tiers
- Customer segments (wholesale, retail, VIP, etc.)
- Tier-specific pricing at item, location, and employee levels
- Both fixed prices and percentage discounts supported

---

## Summary Statistics

- **Total Tables:** 58
- **Foreign Key Constraints:** 8 (logical relationships are much more extensive)
- **Composite Primary Keys:** 24 tables
- **Unique Constraints:** 12 (plus 6 tax-specific unique constraints)
- **Soft Delete Support:** ~15 tables
- **Audit Trail Support:** 2 tables (employees, sales)
- **Maximum Tax Rates per Transaction:** 5
- **Decimal Precision:** 23 digits total, 10 decimal places for financial values

---

## Database Maintenance Notes

### Data Retention
- Soft deletes preserve historical data
- Audit tables maintain complete change history
- Session data can be purged periodically
- Consider archiving old sales/receivings data

### Performance Considerations
- Large transaction tables: sales_items, sales_items_taxes (can grow very large)
- Inventory table tracks all stock movements
- Consider partitioning by date for sales tables
- Index on sale_time, receiving_time for date-range queries

### Backup Priorities
**Critical (Must Backup):**
- phppos_people (base table for all persons)
- phppos_items, phppos_item_kits (product catalog)
- phppos_sales, phppos_sales_* (transaction data)
- phppos_customers, phppos_employees
- phppos_app_config

**Important (Should Backup):**
- phppos_inventory (stock movements)
- phppos_receivings, phppos_receivings_items
- phppos_store_accounts (customer credit)
- phppos_*_audit (audit trails)

**Transient (Can Skip/Truncate):**
- phppos_sessions (can be recreated)
- phppos_admin_otp (expires automatically)

---

## Version Information

**Database Schema Version:** Not explicitly versioned in schema
**Character Set:** utf8_unicode_ci
**Engine:** InnoDB (supports transactions and foreign keys)
**Company:** LUCASA MINI-SUPERMARKET
**Currency:** Ksh (Kenyan Shilling)
**Primary Tax:** VAT at 16%

---

*Document Rebuilt: 2024*
*Source: /home/zaibaki/Databases/database/full_dump.sql*
*Total Database Size: 224.5 MB*
