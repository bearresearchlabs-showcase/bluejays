# Lucasa Database - Data Dictionary

## Overview
This document provides comprehensive column-level documentation for all 58 tables in the lucasa database (phpPOS system). The database manages a point-of-sale system with support for inventory, sales, customers, employees, and eTIMS (Electronic Tax Invoice Management System) integration.

**Database Charset:** UTF-8 Unicode (utf8_unicode_ci)
**Storage Engine:** InnoDB
**Rebuilt:** 2026-02-02

---

## Table of Contents

1. [Admin & Authentication](#admin--authentication)
2. [Customers & Suppliers](#customers--suppliers)
3. [Employees & Permissions](#employees--permissions)
4. [Inventory Management](#inventory-management)
5. [Items & Products](#items--products)
6. [Sales & Transactions](#sales--transactions)
7. [Allocations & Receivings](#allocations--receivings)
8. [Payments & Financial](#payments--financial)
9. [Locations & Configuration](#locations--configuration)
10. [Audit & Logging](#audit--logging)

---

## Admin & Authentication

### phppos_admin_otp

Stores one-time passwords for administrative authentication.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `otp_id` | int(11) | PRIMARY KEY, NOT NULL | Unique identifier for the OTP record |
| `otp_code` | varchar(10) | NOT NULL, INDEXED | The one-time password code |
| `username` | varchar(255) | NOT NULL, INDEXED | Username associated with the OTP |
| `created_at` | timestamp | NOT NULL, DEFAULT current_timestamp() | When the OTP was generated |
| `expires_at` | timestamp | NOT NULL, DEFAULT '0000-00-00 00:00:00', INDEXED | When the OTP expires |
| `used` | tinyint(1) | NOT NULL, DEFAULT 0, INDEXED | Flag indicating if OTP has been used (0=unused, 1=used) |
| `ip_address` | varchar(45) | NULL | IP address from which OTP was requested (supports IPv6) |

**Indexes:**
- PRIMARY KEY: `otp_id`
- COMPOSITE KEY: `otp_code`, `username`, `used`
- KEY: `expires_at`

**Business Logic:**
- OTPs are time-limited security codes for administrative access
- System should validate OTP hasn't been used and hasn't expired
- IP address tracking for security auditing

---

### phppos_sessions

Manages active user sessions.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `session_id` | varchar(40) | PRIMARY KEY, NOT NULL, DEFAULT '0' | Unique session identifier |
| `ip_address` | varchar(45) | NOT NULL, DEFAULT '0' | User's IP address (IPv4/IPv6) |
| `user_agent` | varchar(120) | NOT NULL | Browser/client user agent string |
| `last_activity` | int(10) UNSIGNED | NOT NULL, DEFAULT 0, INDEXED | Unix timestamp of last activity |
| `user_data` | text | NULL | Serialized session data |

**Indexes:**
- PRIMARY KEY: `session_id`
- KEY: `last_activity` (for session cleanup/expiry)

**Business Logic:**
- Session management for logged-in users
- `last_activity` used to expire inactive sessions
- `user_data` typically stores serialized PHP session information

---

## Customers & Suppliers

### phppos_customers

Stores customer information and account details.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `person_id` | int(11) | NOT NULL, INDEXED, FK → phppos_people | Reference to person record |
| `account_number` | varchar(255) | NULL, UNIQUE | Customer account identifier |
| `customer_number` | varchar(255) | NULL, UNIQUE | Alternative customer identifier |
| `company_name` | varchar(255) | NOT NULL | Company/business name |
| `location_id` | int(11) | NULL | Associated location/branch |
| `balance` | decimal(23,10) | NOT NULL, DEFAULT 0.0000000000 | Current account balance |
| `taxable` | int(11) | NOT NULL, DEFAULT 1 | Whether customer is subject to tax (1=taxable, 0=tax-exempt) |
| `tax_id` | varchar(255) | NULL | Tax identification number (TIN) |
| `cc_token` | varchar(255) | NULL, INDEXED | Credit card token for stored payments |
| `cc_preview` | varchar(255) | NULL | Masked credit card number (e.g., ****1234) |
| `card_issuer` | varchar(255) | DEFAULT '' | Credit card issuer (Visa, Mastercard, etc.) |
| `tier_id` | int(11) | NULL, FK → phppos_price_tiers | Pricing tier for special pricing |
| `deleted` | int(11) | NOT NULL, DEFAULT 0, INDEXED | Soft delete flag (0=active, 1=deleted) |

**Foreign Keys:**
- `person_id` → `phppos_people(person_id)`
- `tier_id` → `phppos_price_tiers(id)`

**Indexes:**
- UNIQUE: `account_number`, `customer_number`
- KEY: `person_id`, `deleted`, `cc_token`, `tier_id`

**Business Logic:**
- Uses soft delete pattern (deleted flag)
- Balance tracks store credit or account receivables
- Supports stored payment methods via tokenization
- Tier-based pricing for wholesale/VIP customers

**Example Values:**
- `balance`: 150.5000000000 (customer owes $150.50)
- `taxable`: 1 (customer is taxable)
- `cc_preview`: "************1234"

---

### phppos_suppliers

Stores supplier/vendor information.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `person_id` | int(11) | NOT NULL, INDEXED, FK → phppos_people | Reference to person record |
| `company_name` | varchar(255) | NOT NULL | Supplier company name |
| `account_number` | varchar(255) | NULL, UNIQUE | Supplier account number |
| `deleted` | int(11) | NOT NULL, DEFAULT 0, INDEXED | Soft delete flag (0=active, 1=deleted) |

**Foreign Keys:**
- `person_id` → `phppos_people(person_id)`

**Indexes:**
- UNIQUE: `account_number`
- KEY: `person_id`, `deleted`

**Business Logic:**
- Minimal supplier-specific fields beyond person data
- Uses soft delete pattern
- Contact details stored in phppos_people table

---

### phppos_people

Master table for person records (customers, employees, suppliers).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `person_id` | int(11) | PRIMARY KEY, NOT NULL | Unique person identifier |
| `first_name` | varchar(255) | NOT NULL, INDEXED | Person's first name |
| `last_name` | varchar(255) | NOT NULL, INDEXED | Person's last name |
| `phone_number` | varchar(255) | NOT NULL | Contact phone number |
| `email` | varchar(255) | NOT NULL, INDEXED | Email address |
| `address_1` | varchar(255) | NOT NULL | Primary street address |
| `address_2` | varchar(255) | NOT NULL | Secondary address (apt, suite, etc.) |
| `city` | varchar(255) | NOT NULL | City name |
| `state` | varchar(255) | NOT NULL | State/province |
| `zip` | varchar(255) | NOT NULL | Postal/ZIP code |
| `country` | varchar(255) | NOT NULL | Country name |
| `comments` | text | NOT NULL | Additional notes about person |
| `image_id` | int(11) | NULL, FK → phppos_app_files | Profile image reference |
| `created_time` | timestamp | NULL | Record creation timestamp |
| `updated_time` | timestamp | NULL | Last update timestamp |
| `created_by` | int(11) | NULL | Employee who created record |
| `updated_by` | int(11) | NULL | Employee who last updated record |

**Foreign Keys:**
- `image_id` → `phppos_app_files(file_id)`

**Indexes:**
- PRIMARY KEY: `person_id`
- KEY: `first_name`, `last_name`, `email`, `image_id`

**Business Logic:**
- Central person entity supporting multiple roles
- One person record can be customer, employee, or supplier
- Full address and contact information
- Audit trail with created/updated timestamps

**Example Values:**
- `first_name`: "John"
- `last_name`: "Doe"
- `email`: "john.doe@example.com"
- `phone_number`: "+254712345678"

---

## Employees & Permissions

### phppos_employees

Employee records and authentication details.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `person_id` | int(11) | NOT NULL, INDEXED, FK → phppos_people | Reference to person record (PK) |
| `username` | varchar(255) | NULL, UNIQUE | Login username |
| `password` | varchar(255) | NOT NULL | Hashed password |
| `language` | varchar(255) | NULL | Preferred interface language |
| `account_number` | varchar(255) | NULL | Employee account number |
| `company_name` | varchar(255) | NULL | Associated company (if applicable) |
| `balance` | decimal(23,10) | NOT NULL, DEFAULT 0.0000000000 | Employee account balance |
| `tier_id` | int(11) | NULL | Pricing tier for employee purchases |
| `deleted` | int(11) | NOT NULL, DEFAULT 0, INDEXED | Soft delete flag (0=active, 1=deleted) |
| `hide_from_switch_user` | tinyint(1) | NOT NULL, DEFAULT 0 | Hide from user switching interface (1=hidden) |

**Foreign Keys:**
- `person_id` → `phppos_people(person_id)`

**Indexes:**
- UNIQUE: `username`
- KEY: `person_id`, `deleted`

**Business Logic:**
- `person_id` serves as primary key
- Password should be hashed (bcrypt, SHA-256, etc.)
- `balance` for employee purchase accounts
- `hide_from_switch_user` for admin/super-user accounts

**Security Notes:**
- Passwords stored hashed, never plaintext
- Username must be unique across system

---

### phppos_employees_audit

Audit trail for employee record changes.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `audit_id` | int(11) | PRIMARY KEY, NOT NULL | Unique audit record identifier |
| `employee_id` | int(10) | NOT NULL, INDEXED | Employee being audited |
| `action_type` | varchar(50) | NOT NULL, INDEXED | Type of action (CREATE, UPDATE, DELETE, PASSWORD_CHANGE) |
| `field_name` | varchar(100) | NULL | Field that was changed |
| `old_value` | text | NULL | Previous field value |
| `new_value` | text | NULL | New field value |
| `changed_by` | int(10) | NOT NULL, INDEXED | Employee who made the change |
| `changed_at` | timestamp | NOT NULL, DEFAULT current_timestamp(), INDEXED | When change occurred |
| `ip_address` | varchar(45) | NULL | IP address of user making change |
| `user_agent` | varchar(255) | NULL | Browser/client user agent |
| `notes` | text | NULL | Additional notes about change |

**Indexes:**
- PRIMARY KEY: `audit_id`
- KEY: `employee_id`, `changed_by`, `changed_at`, `action_type`

**Business Logic:**
- Complete audit trail for employee management
- Tracks who changed what, when, and from where
- Special tracking for password changes
- Field-level change tracking

**Example Values:**
- `action_type`: "PASSWORD_CHANGE", "UPDATE", "DELETE"
- `field_name`: "username", "balance"
- `old_value`: "john.smith"
- `new_value`: "jsmith"

---

### phppos_employees_locations

Maps employees to locations they can access.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `employee_id` | int(11) | PRIMARY KEY, NOT NULL, FK → phppos_employees | Employee reference |
| `location_id` | int(11) | PRIMARY KEY, NOT NULL, FK → phppos_locations | Location reference |

**Foreign Keys:**
- `employee_id` → `phppos_employees(person_id)`
- `location_id` → `phppos_locations(location_id)`

**Indexes:**
- PRIMARY KEY: `employee_id`, `location_id` (composite)
- KEY: `location_id`

**Business Logic:**
- Many-to-many relationship
- Employees can access multiple locations
- Used for access control and data filtering

---

### phppos_permissions

Module-level permissions for users.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `module_id` | varchar(100) | PRIMARY KEY, NOT NULL | Module identifier (e.g., "items", "sales") |
| `person_id` | int(11) | PRIMARY KEY, NOT NULL, INDEXED | Person/employee reference |

**Indexes:**
- PRIMARY KEY: `module_id`, `person_id` (composite)
- KEY: `person_id`

**Business Logic:**
- Coarse-grained permission control
- Grants access to entire modules
- Use with phppos_permissions_actions for fine-grained control

**Example Values:**
- `module_id`: "items", "sales", "reports", "customers"

---

### phppos_permissions_actions

Action-level permissions within modules.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `module_id` | varchar(100) | PRIMARY KEY, NOT NULL | Module identifier |
| `person_id` | int(11) | PRIMARY KEY, NOT NULL, INDEXED | Person/employee reference |
| `action_id` | varchar(100) | PRIMARY KEY, NOT NULL, INDEXED | Specific action identifier |

**Indexes:**
- PRIMARY KEY: `module_id`, `person_id`, `action_id` (composite)
- KEY: `person_id`, `action_id`

**Business Logic:**
- Fine-grained permission control
- Controls specific actions within modules
- Examples: "add", "edit", "delete", "view"

**Example Values:**
- `module_id`: "items"
- `action_id`: "add", "edit", "delete", "search"

---

### phppos_modules

Defines system modules.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `module_id` | varchar(100) | PRIMARY KEY, NOT NULL | Unique module identifier |
| `name_lang_key` | varchar(255) | NOT NULL, UNIQUE | Language key for module name |
| `desc_lang_key` | varchar(255) | NOT NULL, UNIQUE | Language key for description |
| `sort` | int(11) | NOT NULL | Display sort order |
| `icon` | varchar(255) | NOT NULL | Icon class/path for UI |

**Indexes:**
- PRIMARY KEY: `module_id`
- UNIQUE: `name_lang_key`, `desc_lang_key`

**Business Logic:**
- Defines available system modules
- Supports internationalization via language keys
- Controls menu ordering and icons

---

### phppos_modules_actions

Defines available actions within modules.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `action_id` | varchar(100) | PRIMARY KEY, NOT NULL | Action identifier |
| `module_id` | varchar(100) | PRIMARY KEY, NOT NULL, FK → phppos_modules | Parent module |
| `action_name_key` | varchar(100) | NOT NULL | Language key for action name |
| `sort` | int(11) | NOT NULL | Display sort order |

**Foreign Keys:**
- `module_id` → `phppos_modules(module_id)`

**Indexes:**
- PRIMARY KEY: `action_id`, `module_id` (composite)
- KEY: `module_id`

**Business Logic:**
- Defines granular permissions per module
- Supports internationalization
- Controls action ordering in UI

---

## Inventory Management

### phppos_inventory

Inventory transaction log.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `trans_id` | int(11) | PRIMARY KEY, NOT NULL | Unique transaction identifier |
| `trans_items` | int(11) | NOT NULL, DEFAULT 0, INDEXED, FK → phppos_items | Item involved in transaction |
| `trans_user` | int(11) | NOT NULL, DEFAULT 0, INDEXED, FK → phppos_employees | Employee performing transaction |
| `trans_date` | timestamp | NOT NULL, DEFAULT current_timestamp() | Transaction timestamp |
| `trans_comment` | text | NOT NULL | Transaction notes/reason |
| `trans_inventory` | decimal(23,10) | NOT NULL, DEFAULT 0.0000000000 | Inventory change amount (+/-) |
| `location_id` | int(11) | NOT NULL, INDEXED, FK → phppos_locations | Location where transaction occurred |
| `quantity_left` | varchar(45) | NULL | Quantity remaining after transaction |
| `quantity_before` | varchar(255) | NULL | Quantity before transaction |

**Foreign Keys:**
- `trans_items` → `phppos_items(item_id)`
- `trans_user` → `phppos_employees(person_id)`
- `location_id` → `phppos_locations(location_id)`

**Indexes:**
- PRIMARY KEY: `trans_id`
- KEY: `trans_items`, `trans_user`, `location_id`

**Business Logic:**
- Complete audit trail of inventory changes
- Positive values = inventory increase
- Negative values = inventory decrease
- Tracks before/after quantities for verification

**Example Values:**
- `trans_inventory`: 50.0000000000 (added 50 units)
- `trans_inventory`: -10.0000000000 (removed 10 units)
- `trans_comment`: "Stock count adjustment"

---

### phppos_employee_inventory

Employee-specific inventory transactions.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `trans_id` | int(11) | PRIMARY KEY, NOT NULL | Unique transaction identifier |
| `trans_items` | int(11) | NOT NULL, DEFAULT 0 | Item reference |
| `trans_user` | int(11) | NOT NULL, DEFAULT 0 | User performing transaction |
| `trans_date` | timestamp | NOT NULL, DEFAULT current_timestamp() | Transaction timestamp |
| `trans_comment` | text | NOT NULL | Transaction notes |
| `trans_inventory` | decimal(23,10) | NOT NULL, DEFAULT 0.0000000000 | Inventory change amount |
| `employee_id` | int(11) | NOT NULL, INDEXED | Employee whose inventory is affected |
| `location_id` | int(11) | NOT NULL | Location reference |
| `quantity_left` | varchar(45) | NULL | Remaining quantity |
| `quantity_before` | varchar(255) | NULL | Quantity before transaction |

**Indexes:**
- PRIMARY KEY: `trans_id`
- KEY: `trans_items`, `trans_user`, `employee_id`

**Business Logic:**
- Tracks inventory assigned to specific employees
- Similar to phppos_inventory but employee-specific
- Used for field sales, samples, or consignment

---

## Items & Products

### phppos_items

Master item/product catalog.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `item_id` | int(11) | PRIMARY KEY, NOT NULL | Unique item identifier |
| `name` | varchar(255) | NOT NULL, INDEXED | Item name/title |
| `category` | varchar(255) | NOT NULL, INDEXED | Item category |
| `supplier_id` | int(11) | NULL, INDEXED | Primary supplier reference |
| `item_number` | varchar(255) | NULL, UNIQUE | Internal item number/SKU |
| `product_id` | varchar(255) | NULL, UNIQUE | External product identifier (barcode/UPC) |
| `description` | varchar(255) | NOT NULL | Item description |
| `tax_included` | int(11) | NOT NULL, DEFAULT 0 | Whether price includes tax (1=included, 0=excluded) |
| `cost_price` | decimal(23,10) | NOT NULL | Item cost/purchase price |
| `wholesale_price` | decimal(23,10) | NULL | Wholesale selling price |
| `unit_price` | decimal(23,10) | NOT NULL | Retail selling price |
| `promo_price` | decimal(23,10) | NULL | Promotional/sale price |
| `start_date` | date | NULL | Promotion start date |
| `end_date` | date | NULL | Promotion end date |
| `reorder_level` | decimal(23,10) | NULL | Minimum quantity before reorder alert |
| `allow_alt_description` | tinyint(1) | NOT NULL | Allow description override at sale (1=yes, 0=no) |
| `is_serialized` | tinyint(1) | NOT NULL | Track by serial numbers (1=yes, 0=no) |
| `image_id` | int(11) | NULL, FK → phppos_app_files | Product image reference |
| `override_default_tax` | int(11) | NOT NULL, DEFAULT 0 | Use custom tax instead of defaults (1=override) |
| `is_service` | int(11) | NOT NULL, DEFAULT 0 | Service vs physical product (1=service) |
| `deleted` | int(11) | NOT NULL, DEFAULT 0, INDEXED | Soft delete flag (0=active, 1=deleted) |
| `etims_tax_type` | varchar(50) | NULL | eTIMS tax type code |

**Foreign Keys:**
- `supplier_id` → `phppos_suppliers(person_id)`
- `image_id` → `phppos_app_files(file_id)`

**Indexes:**
- PRIMARY KEY: `item_id`
- UNIQUE: `item_number`, `product_id`
- KEY: `supplier_id`, `name`, `category`, `deleted`, `image_id`

**Business Logic:**
- Core product catalog
- Supports time-based promotions
- eTIMS integration for tax compliance
- Serialized items tracked individually
- Services vs physical goods differentiation

**eTIMS Notes:**
- `etims_tax_type`: Tax classification for Kenya Revenue Authority
- Required for tax compliance in Kenya

**Example Values:**
- `item_number`: "ITM-001"
- `product_id`: "5012345678900" (barcode)
- `cost_price`: 50.0000000000
- `unit_price`: 100.0000000000
- `etims_tax_type`: "A" (standard rate)

---

### phppos_items_taxes

Tax configurations for items.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | int(11) | PRIMARY KEY, NOT NULL | Unique tax record identifier |
| `item_id` | int(11) | NOT NULL, INDEXED | Item reference |
| `name` | varchar(255) | NOT NULL | Tax name (e.g., "VAT", "Sales Tax") |
| `percent` | decimal(15,3) | NOT NULL | Tax percentage (e.g., 16.000 for 16%) |
| `cumulative` | int(11) | NOT NULL, DEFAULT 0 | Whether tax compounds on previous taxes |

**Indexes:**
- PRIMARY KEY: `id`
- UNIQUE: `item_id`, `name`, `percent` (composite)

**Business Logic:**
- Multiple taxes can apply to one item
- Cumulative taxes compound on subtotal + previous taxes
- Non-cumulative taxes apply only to subtotal

**Example Values:**
- `name`: "VAT", "County Tax"
- `percent`: 16.000 (16% tax)
- `cumulative`: 0 (non-compounding)

---

### phppos_items_tier_prices

Tier-based pricing for items.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `tier_id` | int(11) | PRIMARY KEY, NOT NULL | Price tier reference |
| `item_id` | int(11) | PRIMARY KEY, NOT NULL, INDEXED | Item reference |
| `unit_price` | decimal(23,10) | DEFAULT 0.0000000000 | Special price for this tier |
| `percent_off` | int(11) | NULL | Percentage discount (alternative to unit_price) |

**Indexes:**
- PRIMARY KEY: `tier_id`, `item_id` (composite)
- KEY: `item_id`

**Business Logic:**
- Volume/wholesale pricing
- Either specific price OR percentage off
- Applied based on customer's tier assignment

**Example Values:**
- `tier_id`: 1 (Wholesale)
- `unit_price`: 80.0000000000 (20% off retail)
- `percent_off`: 20 (alternative: 20% discount)

---

### phppos_item_kits

Product bundles/kits.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `item_kit_id` | int(11) | PRIMARY KEY, NOT NULL | Unique kit identifier |
| `item_kit_number` | varchar(255) | NULL, UNIQUE | Internal kit number/SKU |
| `product_id` | varchar(255) | NULL, UNIQUE | External product identifier |
| `name` | varchar(255) | NOT NULL, INDEXED | Kit name |
| `description` | varchar(255) | NOT NULL | Kit description |
| `category` | varchar(255) | NOT NULL | Kit category |
| `tax_included` | int(11) | NOT NULL, DEFAULT 0 | Whether kit price includes tax |
| `unit_price` | decimal(23,10) | NULL | Kit selling price |
| `cost_price` | decimal(23,10) | NULL | Kit cost (sum of component costs) |
| `override_default_tax` | int(11) | NOT NULL, DEFAULT 0 | Use custom tax settings |
| `deleted` | int(11) | NOT NULL, DEFAULT 0, INDEXED | Soft delete flag |

**Indexes:**
- PRIMARY KEY: `item_kit_id`
- UNIQUE: `item_kit_number`, `product_id`
- KEY: `name`, `deleted`

**Business Logic:**
- Bundles of multiple items sold as one
- Can have bundle discount vs sum of parts
- Components defined in phppos_item_kit_items

**Example Values:**
- `name`: "Starter Package"
- `unit_price`: 250.0000000000 (vs $300 if bought separately)

---

### phppos_item_kit_items

Components of item kits.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `item_kit_id` | int(11) | PRIMARY KEY, NOT NULL | Parent kit reference |
| `item_id` | int(11) | PRIMARY KEY, NOT NULL, INDEXED | Component item reference |
| `quantity` | decimal(23,10) | PRIMARY KEY, NOT NULL | Quantity of item in kit |

**Indexes:**
- PRIMARY KEY: `item_kit_id`, `item_id`, `quantity` (composite)
- KEY: `item_id`

**Business Logic:**
- Defines kit contents
- Each item-quantity combination is unique
- Selling kit decrements component inventory

**Example Values:**
- `item_kit_id`: 1
- `item_id`: 5
- `quantity`: 2.0000000000 (2 units of item #5)

---

### phppos_item_kits_taxes

Tax configurations for item kits.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | int(11) | PRIMARY KEY, NOT NULL | Unique tax record identifier |
| `item_kit_id` | int(11) | NOT NULL | Kit reference |
| `name` | varchar(255) | NOT NULL | Tax name |
| `percent` | decimal(15,3) | NOT NULL | Tax percentage |
| `cumulative` | int(11) | NOT NULL, DEFAULT 0 | Compound tax flag |

**Indexes:**
- PRIMARY KEY: `id`
- UNIQUE: `item_kit_id`, `name`, `percent` (composite)

**Business Logic:**
- Same as phppos_items_taxes but for kits
- Allows different tax treatment for bundles

---

### phppos_item_kits_tier_prices

Tier-based pricing for item kits.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `tier_id` | int(11) | PRIMARY KEY, NOT NULL | Price tier reference |
| `item_kit_id` | int(11) | PRIMARY KEY, NOT NULL, INDEXED | Kit reference |
| `unit_price` | decimal(23,10) | DEFAULT 0.0000000000 | Special price for this tier |
| `percent_off` | int(11) | NULL | Percentage discount |

**Indexes:**
- PRIMARY KEY: `tier_id`, `item_kit_id` (composite)
- KEY: `item_kit_id`

**Business Logic:**
- Volume/wholesale pricing for kits
- Same logic as phppos_items_tier_prices

---

## Sales & Transactions

### phppos_sales

Master sales transaction records.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `sale_id` | int(11) | PRIMARY KEY, NOT NULL | Unique sale identifier |
| `sale_time` | timestamp | NOT NULL, DEFAULT current_timestamp(), INDEXED | When sale occurred |
| `customer_id` | int(11) | NULL, INDEXED | Customer reference (null for walk-in) |
| `employee_id` | int(11) | NOT NULL, DEFAULT 0, INDEXED | Employee who processed sale |
| `comment` | text | NULL | Sale notes/comments |
| `show_comment_on_receipt` | int(11) | NOT NULL, DEFAULT 0 | Print comment on receipt (1=yes) |
| `invoice_number` | int(11) | NULL, UNIQUE | Sequential invoice number |
| `payment_type` | varchar(255) | NULL | Primary payment method |
| `cc_ref_no` | varchar(255) | NULL | Credit card reference number |
| `auth_code` | varchar(255) | DEFAULT '' | Credit card authorization code |
| `deleted` | int(11) | NOT NULL, DEFAULT 0, INDEXED | Soft delete flag (0=active, 1=deleted) |
| `deleted_by` | int(11) | NULL, INDEXED | Employee who deleted sale |
| `suspended` | int(11) | NOT NULL, DEFAULT 0 | Sale on hold (1=suspended, 0=completed) |
| `allocated` | int(11) | NOT NULL, DEFAULT 0 | Whether items allocated to employee |
| `store_account_payment` | int(11) | NOT NULL, DEFAULT 0, INDEXED | Paid via store account (1=yes) |
| `location_id` | int(11) | NULL, INDEXED | Location where sale occurred |
| `erp_integration` | int(11) | NOT NULL, DEFAULT 0 | Synced to ERP system (1=yes) |
| `etims_invoice_number` | varchar(255) | NULL | eTIMS official invoice number |
| `etims_scu_id` | varchar(255) | NULL | eTIMS Sales Control Unit ID |
| `etims_cu_inv_no` | varchar(255) | NULL | eTIMS Control Unit invoice number |
| `etims_internal_data` | varchar(255) | NULL | eTIMS internal reference data |
| `etims_receipt_signature` | varchar(255) | NULL | eTIMS digital signature |
| `etims_signature_link` | text | NULL | eTIMS signature verification URL |
| `etims_version` | varchar(50) | NULL | eTIMS protocol version |

**Indexes:**
- PRIMARY KEY: `sale_id`
- UNIQUE: `invoice_number`
- KEY: `customer_id`, `employee_id`, `deleted`, `location_id`, `deleted_by`
- COMPOSITE KEY: `location_id`, `store_account_payment`, `sale_time`, `sale_id`

**Business Logic:**
- Core sales transaction record
- Supports suspended (layaway) sales
- eTIMS fields for Kenya tax compliance
- Multiple payment types in phppos_sales_payments

**eTIMS Notes:**
- All etims_* fields required for Kenya Revenue Authority compliance
- `etims_invoice_number`: Official tax invoice number
- `etims_signature`: Cryptographic proof of submission
- `etims_signature_link`: QR code URL for receipt verification

**Example Values:**
- `invoice_number`: 12345
- `payment_type`: "Cash", "Credit Card", "M-Pesa"
- `suspended`: 1 (sale on hold)
- `etims_invoice_number`: "KRA-2026-000123"

---

### phppos_sales_audit

Audit trail for sales changes.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `audit_id` | int(11) | PRIMARY KEY, NOT NULL | Unique audit record identifier |
| `sale_id` | int(10) | NOT NULL, INDEXED | Sale being audited |
| `action_type` | varchar(50) | NOT NULL, INDEXED | Action type (CREATE, UPDATE, DELETE, SUSPEND, COMPLETE) |
| `field_name` | varchar(100) | NULL | Field that was changed |
| `old_value` | text | NULL | Previous field value |
| `new_value` | text | NULL | New field value |
| `changed_by` | int(10) | NOT NULL, INDEXED | Employee who made change |
| `changed_at` | timestamp | NOT NULL, DEFAULT current_timestamp(), INDEXED | When change occurred |
| `ip_address` | varchar(45) | NULL | IP address of user |
| `user_agent` | varchar(255) | NULL | Browser/client user agent |
| `notes` | text | NULL | Additional notes |

**Indexes:**
- PRIMARY KEY: `audit_id`
- KEY: `sale_id`, `changed_by`, `changed_at`, `action_type`

**Business Logic:**
- Complete audit trail for sales
- Tracks all changes to sales records
- Critical for financial compliance

---

### phppos_sales_items

Line items for sales (individual products).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `sale_id` | int(11) | PRIMARY KEY, NOT NULL, DEFAULT 0 | Parent sale reference |
| `item_id` | int(11) | PRIMARY KEY, NOT NULL, DEFAULT 0, INDEXED | Item sold |
| `line` | int(11) | PRIMARY KEY, NOT NULL, DEFAULT 0 | Line number in sale |
| `description` | varchar(255) | NULL | Item description (may override default) |
| `serialnumber` | varchar(255) | NULL | Serial number (for serialized items) |
| `quantity_purchased` | decimal(23,10) | NOT NULL, DEFAULT 0.0000000000 | Quantity sold |
| `item_cost_price` | decimal(23,10) | NOT NULL | Item cost at time of sale |
| `item_unit_price` | decimal(23,10) | NOT NULL | Selling price per unit |
| `discount_percent` | int(11) | NOT NULL, DEFAULT 0 | Line-level discount percentage |
| `price_mode` | varchar(255) | NULL | Pricing mode indicator |

**Indexes:**
- PRIMARY KEY: `sale_id`, `item_id`, `line` (composite)
- KEY: `item_id`

**Business Logic:**
- One record per item line in sale
- Multiple lines if same item sold with different prices/discounts
- Historical pricing preserved (cost_price, unit_price)
- Serial number tracking for warranty/returns

**Example Values:**
- `line`: 1, 2, 3 (line numbers)
- `quantity_purchased`: 2.5000000000 (2.5 units)
- `discount_percent`: 10 (10% off)

---

### phppos_sales_items_taxes

Taxes applied to sale line items.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `sale_id` | int(11) | PRIMARY KEY, NOT NULL | Parent sale reference |
| `item_id` | int(11) | PRIMARY KEY, NOT NULL, INDEXED | Item reference |
| `line` | int(11) | PRIMARY KEY, NOT NULL, DEFAULT 0 | Line number |
| `name` | varchar(255) | PRIMARY KEY, NOT NULL | Tax name |
| `percent` | decimal(15,3) | PRIMARY KEY, NOT NULL | Tax percentage at sale time |
| `cumulative` | int(11) | NOT NULL, DEFAULT 0 | Compound tax flag |

**Indexes:**
- PRIMARY KEY: `sale_id`, `item_id`, `line`, `name`, `percent` (composite)
- KEY: `item_id`

**Business Logic:**
- Historical tax rates preserved
- Multiple taxes can apply per line
- Tax amount calculated: (line_total × percent / 100)

---

### phppos_sales_item_kits

Line items for sales (item kits/bundles).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `sale_id` | int(11) | PRIMARY KEY, NOT NULL, DEFAULT 0 | Parent sale reference |
| `item_kit_id` | int(11) | PRIMARY KEY, NOT NULL, DEFAULT 0, INDEXED | Kit sold |
| `line` | int(11) | PRIMARY KEY, NOT NULL, DEFAULT 0 | Line number in sale |
| `description` | varchar(255) | NULL | Kit description |
| `quantity_purchased` | decimal(23,10) | NOT NULL, DEFAULT 0.0000000000 | Quantity sold |
| `item_kit_cost_price` | decimal(23,10) | NOT NULL | Kit cost at time of sale |
| `item_kit_unit_price` | decimal(23,10) | NOT NULL | Selling price per kit |
| `discount_percent` | int(11) | NOT NULL, DEFAULT 0 | Line-level discount percentage |
| `price_mode` | varchar(255) | NULL | Pricing mode indicator |

**Indexes:**
- PRIMARY KEY: `sale_id`, `item_kit_id`, `line` (composite)
- KEY: `item_kit_id`

**Business Logic:**
- Same structure as phppos_sales_items but for kits
- Kit components decremented from inventory automatically

---

### phppos_sales_item_kits_taxes

Taxes applied to sale kit lines.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `sale_id` | int(11) | PRIMARY KEY, NOT NULL | Parent sale reference |
| `item_kit_id` | int(11) | PRIMARY KEY, NOT NULL, INDEXED | Kit reference |
| `line` | int(11) | PRIMARY KEY, NOT NULL, DEFAULT 0 | Line number |
| `name` | varchar(255) | PRIMARY KEY, NOT NULL | Tax name |
| `percent` | decimal(15,3) | PRIMARY KEY, NOT NULL | Tax percentage |
| `cumulative` | int(11) | NOT NULL, DEFAULT 0 | Compound tax flag |

**Indexes:**
- PRIMARY KEY: `sale_id`, `item_kit_id`, `line`, `name`, `percent` (composite)
- KEY: `item_kit_id`

**Business Logic:**
- Same as phppos_sales_items_taxes but for kits

---

### phppos_sales_payments

Payment records for sales.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `payment_id` | int(11) | PRIMARY KEY, NOT NULL | Unique payment identifier |
| `sale_id` | int(11) | NOT NULL, INDEXED | Parent sale reference |
| `payment_type` | varchar(255) | NOT NULL | Payment method type |
| `payment_amount` | decimal(23,10) | NOT NULL | Amount paid via this method |
| `payment_date` | timestamp | NOT NULL, DEFAULT current_timestamp() | When payment received |
| `truncated_card` | varchar(255) | DEFAULT '' | Masked card number (****1234) |
| `card_issuer` | varchar(255) | DEFAULT '' | Card brand (Visa, Mastercard, etc.) |

**Indexes:**
- PRIMARY KEY: `payment_id`
- KEY: `sale_id`

**Business Logic:**
- Supports split payments (multiple methods per sale)
- One or more payment records per sale
- Sum of payment_amount should equal sale total

**Example Values:**
- `payment_type`: "Cash", "Credit Card", "M-Pesa", "Store Credit"
- `payment_amount`: 50.0000000000
- `truncated_card`: "************4532"

---

## Employee Sales (Duplicate Structure)

The following tables mirror the main sales structure but for employee-specific sales:

### phppos_employee_sales

Employee sales transactions (same structure as phppos_sales).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `sale_id` | int(11) | PRIMARY KEY, NOT NULL | Unique sale identifier |
| `sale_time` | timestamp | NOT NULL, DEFAULT current_timestamp() | Sale timestamp |
| `customer_id` | int(11) | NULL, INDEXED | Customer reference |
| `employee_id` | int(11) | NOT NULL, DEFAULT 0, INDEXED | Employee who processed sale |
| `comment` | text | NOT NULL | Sale notes |
| `show_comment_on_receipt` | int(11) | NOT NULL, DEFAULT 0 | Print comment flag |
| `payment_type` | varchar(255) | NULL | Payment method |
| `cc_ref_no` | varchar(255) | NOT NULL | Credit card reference |
| `auth_code` | varchar(255) | DEFAULT '' | Authorization code |
| `deleted` | int(11) | NOT NULL, DEFAULT 0, INDEXED | Soft delete flag |
| `deleted_by` | int(11) | NULL | Employee who deleted |
| `suspended` | int(11) | NOT NULL, DEFAULT 0 | Suspended sale flag |
| `store_account_payment` | int(11) | NOT NULL, DEFAULT 0 | Store account payment flag |
| `location_id` | int(11) | NOT NULL, INDEXED | Location reference |
| `etims_invoice_number` | varchar(255) | NULL | eTIMS invoice number |
| `etims_scu_id` | varchar(255) | NULL | eTIMS SCU ID |
| `etims_cu_inv_no` | varchar(255) | NULL | eTIMS CU invoice number |
| `etims_internal_data` | varchar(255) | NULL | eTIMS internal data |
| `etims_receipt_signature` | varchar(255) | NULL | eTIMS signature |
| `etims_signature_link` | text | NULL | eTIMS signature URL |
| `etims_version` | varchar(50) | NULL | eTIMS version |

**Business Logic:**
- Separate tracking for employee purchases vs customer sales
- Used for employee discount tracking
- Same eTIMS compliance requirements

---

### phppos_employee_sales_items

Employee sale line items (mirrors phppos_sales_items).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `sale_id` | int(11) | PRIMARY KEY, NOT NULL, DEFAULT 0 | Parent sale reference |
| `item_id` | int(11) | PRIMARY KEY, NOT NULL, DEFAULT 0, INDEXED | Item sold |
| `line` | int(11) | PRIMARY KEY, NOT NULL, DEFAULT 0 | Line number |
| `description` | varchar(255) | NULL | Item description |
| `serialnumber` | varchar(255) | NULL | Serial number |
| `quantity_purchased` | decimal(23,10) | NOT NULL, DEFAULT 0.0000000000 | Quantity sold |
| `item_cost_price` | decimal(23,10) | NOT NULL | Item cost price |
| `item_unit_price` | decimal(23,10) | NOT NULL | Selling price |
| `discount_percent` | int(11) | NOT NULL, DEFAULT 0 | Discount percentage |

---

### phppos_employee_sales_items_taxes

Taxes for employee sale items (mirrors phppos_sales_items_taxes).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `sale_id` | int(11) | PRIMARY KEY, NOT NULL | Parent sale reference |
| `item_id` | int(11) | PRIMARY KEY, NOT NULL, INDEXED | Item reference |
| `line` | int(11) | PRIMARY KEY, NOT NULL, DEFAULT 0 | Line number |
| `name` | varchar(255) | PRIMARY KEY, NOT NULL | Tax name |
| `percent` | decimal(15,3) | PRIMARY KEY, NOT NULL | Tax percentage |
| `cumulative` | int(11) | NOT NULL, DEFAULT 0 | Compound tax flag |

---

### phppos_employee_sales_item_kits

Employee sale kit items (mirrors phppos_sales_item_kits).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `sale_id` | int(11) | PRIMARY KEY, NOT NULL, DEFAULT 0 | Parent sale reference |
| `item_kit_id` | int(11) | PRIMARY KEY, NOT NULL, DEFAULT 0, INDEXED | Kit sold |
| `line` | int(11) | PRIMARY KEY, NOT NULL, DEFAULT 0 | Line number |
| `description` | varchar(255) | NULL | Kit description |
| `quantity_purchased` | decimal(23,10) | NOT NULL, DEFAULT 0.0000000000 | Quantity sold |
| `item_kit_cost_price` | decimal(23,10) | NOT NULL | Kit cost price |
| `item_kit_unit_price` | decimal(23,10) | NOT NULL | Selling price |
| `discount_percent` | int(11) | NOT NULL, DEFAULT 0 | Discount percentage |

---

### phppos_employee_sales_item_kits_taxes

Taxes for employee sale kits (mirrors phppos_sales_item_kits_taxes).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `sale_id` | int(11) | PRIMARY KEY, NOT NULL | Parent sale reference |
| `item_kit_id` | int(11) | PRIMARY KEY, NOT NULL, INDEXED | Kit reference |
| `line` | int(11) | PRIMARY KEY, NOT NULL, DEFAULT 0 | Line number |
| `name` | varchar(255) | PRIMARY KEY, NOT NULL | Tax name |
| `percent` | decimal(15,3) | PRIMARY KEY, NOT NULL | Tax percentage |
| `cumulative` | int(11) | NOT NULL, DEFAULT 0 | Compound tax flag |

---

### phppos_employee_sales_payments

Payment records for employee sales (mirrors phppos_sales_payments).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `payment_id` | int(11) | PRIMARY KEY, NOT NULL | Unique payment identifier |
| `sale_id` | int(11) | NOT NULL, INDEXED | Parent sale reference |
| `payment_type` | varchar(255) | NOT NULL | Payment method |
| `payment_amount` | decimal(23,10) | NOT NULL | Amount paid |
| `payment_date` | timestamp | NOT NULL, DEFAULT current_timestamp() | Payment timestamp |
| `truncated_card` | varchar(255) | DEFAULT '' | Masked card number |
| `card_issuer` | varchar(255) | DEFAULT '' | Card issuer |

---

## Employee Items (Location-Specific Pricing)

### phppos_employee_items

Employee-specific item pricing and inventory.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `employee_id` | int(11) | PRIMARY KEY, NOT NULL | Employee reference |
| `item_id` | int(11) | PRIMARY KEY, NOT NULL, INDEXED | Item reference |
| `location_id` | int(11) | NULL | Location reference |
| `location` | varchar(255) | NOT NULL, DEFAULT '' | Location description/name |
| `cost_price` | decimal(23,10) | NULL | Employee-specific cost price |
| `wholesale_price` | decimal(23,10) | NULL | Employee-specific wholesale price |
| `unit_price` | decimal(23,10) | NULL | Employee-specific retail price |
| `promo_price` | decimal(23,10) | NULL | Employee-specific promo price |
| `start_date` | date | NULL | Promotion start date |
| `end_date` | date | NULL | Promotion end date |
| `quantity` | decimal(23,10) | DEFAULT 0.0000000000 | Employee's inventory quantity |
| `reorder_level` | decimal(23,10) | NULL | Reorder threshold |
| `override_default_tax` | int(11) | NOT NULL, DEFAULT 0 | Custom tax override flag |

**Indexes:**
- PRIMARY KEY: `employee_id`, `item_id` (composite)
- KEY: `item_id`

**Business Logic:**
- Allows per-employee pricing (e.g., for sales reps)
- Employee-specific inventory tracking
- Supports employee-managed promotions

---

### phppos_employee_items_taxes

Tax overrides for employee items.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | int(11) | PRIMARY KEY, NOT NULL | Unique tax record identifier |
| `employee_id` | int(11) | NOT NULL | Employee reference |
| `item_id` | int(11) | NOT NULL, INDEXED | Item reference |
| `name` | varchar(255) | NOT NULL | Tax name |
| `percent` | decimal(16,3) | NOT NULL | Tax percentage |
| `cumulative` | int(11) | NOT NULL, DEFAULT 0 | Compound tax flag |

**Indexes:**
- PRIMARY KEY: `id`
- UNIQUE: `employee_id`, `item_id`, `name`, `percent` (composite)
- KEY: `item_id`

---

### phppos_employee_items_tier_prices

Tier pricing for employee items.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `tier_id` | int(11) | PRIMARY KEY, NOT NULL | Price tier reference |
| `item_id` | int(11) | PRIMARY KEY, NOT NULL | Item reference |
| `employee_id` | int(11) | PRIMARY KEY, NOT NULL | Employee reference |
| `unit_price` | decimal(23,10) | DEFAULT 0.0000000000 | Tier-specific price |
| `percent_off` | int(11) | NULL | Percentage discount |

**Indexes:**
- PRIMARY KEY: `tier_id`, `item_id`, `employee_id` (composite)
- KEY: `employee_id`, `item_id`

---

### phppos_employee_item_kits

Employee-specific kit pricing.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `employee_id` | int(11) | PRIMARY KEY, NOT NULL | Employee reference |
| `item_kit_id` | int(11) | PRIMARY KEY, NOT NULL, INDEXED | Kit reference |
| `unit_price` | decimal(23,10) | NULL | Employee-specific kit price |
| `cost_price` | decimal(23,10) | NULL | Employee-specific kit cost |
| `override_default_tax` | int(11) | NOT NULL, DEFAULT 0 | Custom tax override flag |

**Indexes:**
- PRIMARY KEY: `employee_id`, `item_kit_id` (composite)
- KEY: `item_kit_id`

---

### phppos_employee_item_kits_taxes

Tax overrides for employee kits.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | int(11) | PRIMARY KEY, NOT NULL | Unique tax record identifier |
| `employee_id` | int(11) | NOT NULL | Employee reference |
| `item_kit_id` | int(11) | NOT NULL, INDEXED | Kit reference |
| `name` | varchar(255) | NOT NULL | Tax name |
| `percent` | decimal(16,3) | NOT NULL | Tax percentage |
| `cumulative` | int(11) | NOT NULL, DEFAULT 0 | Compound tax flag |

**Indexes:**
- PRIMARY KEY: `id`
- UNIQUE: `employee_id`, `item_kit_id`, `name`, `percent` (composite)
- KEY: `item_kit_id`

---

### phppos_employee_item_kits_tier_prices

Tier pricing for employee kits.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `tier_id` | int(11) | PRIMARY KEY, NOT NULL | Price tier reference |
| `item_kit_id` | int(11) | PRIMARY KEY, NOT NULL | Kit reference |
| `employee_id` | int(11) | PRIMARY KEY, NOT NULL | Employee reference |
| `unit_price` | decimal(23,10) | DEFAULT 0.0000000000 | Tier-specific price |
| `percent_off` | int(11) | NULL | Percentage discount |

**Indexes:**
- PRIMARY KEY: `tier_id`, `item_kit_id`, `employee_id` (composite)
- KEY: `employee_id`, `item_kit_id`

---

## Allocations & Receivings

### phppos_allocations

Inventory allocations to employees.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `allocation_id` | int(11) | PRIMARY KEY, NOT NULL | Unique allocation identifier |
| `allocation_time` | timestamp | NOT NULL, DEFAULT current_timestamp() | When allocation occurred |
| `supplier_id` | int(11) | NULL, INDEXED | Supplier reference (if applicable) |
| `employee_id` | int(11) | NOT NULL, DEFAULT 0, INDEXED | Employee creating allocation |
| `allocated_employee_id` | int(11) | NOT NULL, INDEXED | Employee receiving allocation |
| `location_id` | int(11) | NOT NULL | Location reference |
| `comment` | text | NOT NULL | Allocation notes |
| `payment_type` | varchar(255) | NULL | Payment method (if applicable) |
| `deleted` | int(11) | NOT NULL, DEFAULT 0, INDEXED | Soft delete flag |
| `deleted_by` | int(11) | NULL | Employee who deleted allocation |

**Indexes:**
- PRIMARY KEY: `allocation_id`
- KEY: `supplier_id`, `employee_id`, `deleted`, `allocated_employee_id`

**Business Logic:**
- Assigns inventory from location to employee
- Used for field sales, samples, consignment
- `employee_id`: who created the allocation
- `allocated_employee_id`: who received the items

---

### phppos_allocations_items

Line items for allocations.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `allocation_id` | int(11) | PRIMARY KEY, NOT NULL, DEFAULT 0 | Parent allocation reference |
| `item_id` | int(11) | PRIMARY KEY, NOT NULL, DEFAULT 0, INDEXED | Item allocated |
| `line` | int(11) | PRIMARY KEY, NOT NULL | Line number |
| `description` | varchar(255) | NULL | Item description |
| `serialnumber` | varchar(255) | NULL | Serial number |
| `quantity_purchased` | decimal(23,10) | NOT NULL, DEFAULT 0.0000000000 | Quantity allocated |
| `item_cost_price` | decimal(23,10) | NOT NULL | Item cost |
| `item_wholesale_price` | decimal(23,10) | NULL | Wholesale price |
| `item_unit_price` | decimal(23,10) | NOT NULL | Retail price |
| `discount_percent` | int(11) | NOT NULL, DEFAULT 0 | Discount percentage |

**Indexes:**
- PRIMARY KEY: `allocation_id`, `item_id`, `line` (composite)
- KEY: `item_id`

**Business Logic:**
- Details of what was allocated
- Tracks pricing at time of allocation
- Multiple lines per allocation

---

### phppos_receivings

Purchase orders/inventory receiving records.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `receiving_id` | int(11) | PRIMARY KEY, NOT NULL | Unique receiving identifier |
| `receiving_time` | timestamp | NOT NULL, DEFAULT current_timestamp() | When goods received |
| `supplier_id` | int(11) | NULL, INDEXED | Supplier reference |
| `employee_id` | int(11) | NOT NULL, DEFAULT 0, INDEXED | Employee who processed receiving |
| `location_id` | int(11) | NOT NULL, INDEXED | Location receiving inventory |
| `comment` | text | NOT NULL | Receiving notes |
| `payment_type` | varchar(255) | NULL | Payment method |
| `deleted` | int(11) | NOT NULL, DEFAULT 0, INDEXED | Soft delete flag |
| `deleted_by` | int(11) | NULL | Employee who deleted receiving |

**Indexes:**
- PRIMARY KEY: `receiving_id`
- KEY: `supplier_id`, `employee_id`, `deleted`, `location_id`

**Business Logic:**
- Purchase order receipt/fulfillment
- Increases inventory at location
- Links to supplier for accounts payable

---

### phppos_receivings_items

Line items for receiving records.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `receiving_id` | int(11) | PRIMARY KEY, NOT NULL, DEFAULT 0 | Parent receiving reference |
| `item_id` | int(11) | PRIMARY KEY, NOT NULL, DEFAULT 0, INDEXED | Item received |
| `line` | int(11) | PRIMARY KEY, NOT NULL | Line number |
| `description` | varchar(255) | NULL | Item description |
| `serialnumber` | varchar(255) | NULL | Serial number |
| `quantity_purchased` | decimal(23,10) | NOT NULL, DEFAULT 0.0000000000 | Quantity received |
| `item_cost_price` | decimal(23,10) | NOT NULL | Purchase cost per unit |
| `item_wholesale_price` | decimal(23,10) | NULL | Suggested wholesale price |
| `item_unit_price` | decimal(23,10) | NOT NULL | Suggested retail price |
| `discount_percent` | int(11) | NOT NULL, DEFAULT 0 | Discount percentage |

**Indexes:**
- PRIMARY KEY: `receiving_id`, `item_id`, `line` (composite)
- KEY: `item_id`

**Business Logic:**
- Details of goods received
- Updates inventory quantity
- Records actual purchase cost

---

## Payments & Financial

### phppos_store_accounts

Customer store account transactions.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `sno` | int(11) | PRIMARY KEY, NOT NULL | Unique transaction number |
| `customer_id` | int(11) | NOT NULL, INDEXED | Customer reference |
| `sale_id` | int(11) | NULL, INDEXED | Associated sale (if applicable) |
| `transaction_amount` | decimal(23,10) | NOT NULL, DEFAULT 0.0000000000 | Transaction amount (+/-) |
| `balance` | decimal(23,10) | NOT NULL, DEFAULT 0.0000000000 | Account balance after transaction |
| `date` | timestamp | NOT NULL, DEFAULT current_timestamp() | Transaction date |
| `comment` | text | NOT NULL | Transaction description |
| `deleted` | int(11) | NOT NULL, DEFAULT 0, INDEXED | Soft delete flag |

**Indexes:**
- PRIMARY KEY: `sno`
- KEY: `deleted`, `sale_id`, `customer_id`

**Business Logic:**
- Customer credit/account receivables
- Positive amount = payment/credit
- Negative amount = charge/purchase
- Running balance maintained

**Example Values:**
- `transaction_amount`: 100.0000000000 (payment received)
- `transaction_amount`: -50.0000000000 (purchase charged)
- `balance`: 50.0000000000 (net balance)

---

### phppos_register_log

Cash register open/close log.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `register_log_id` | int(11) | PRIMARY KEY, NOT NULL | Unique log entry identifier |
| `employee_id` | int(11) | NOT NULL, INDEXED | Employee working register |
| `shift_start` | timestamp | NOT NULL, DEFAULT '0000-00-00 00:00:00' | Shift start time |
| `shift_end` | timestamp | NOT NULL, DEFAULT '0000-00-00 00:00:00' | Shift end time |
| `open_amount` | decimal(23,10) | NOT NULL | Starting cash amount |
| `close_amount` | decimal(23,10) | NOT NULL | Ending cash count |
| `cash_sales_amount` | decimal(23,10) | NOT NULL | Total cash sales during shift |
| `deleted` | int(11) | NOT NULL, DEFAULT 0, INDEXED | Soft delete flag |

**Indexes:**
- PRIMARY KEY: `register_log_id`
- KEY: `employee_id`, `deleted`

**Business Logic:**
- Cash drawer reconciliation
- Expected close = open + cash_sales
- Variance = close_amount - (open_amount + cash_sales_amount)

**Example Values:**
- `open_amount`: 200.0000000000 (starting cash)
- `cash_sales_amount`: 500.0000000000 (sales during shift)
- `close_amount`: 700.0000000000 (expected balance)

---

### phppos_expenses

Business expense tracking.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `person_id` | int(11) | NOT NULL, INDEXED | Person who incurred expense |
| `expense_name` | varchar(255) | NOT NULL | Expense description |
| `category` | varchar(255) | NULL | Expense category |
| `amount_spent` | decimal(23,10) | NOT NULL | Expense amount |
| `date_created` | timestamp | NOT NULL, DEFAULT current_timestamp() | When expense recorded |
| `deleted` | int(11) | NOT NULL, DEFAULT 0, INDEXED | Soft delete flag |

**Indexes:**
- KEY: `person_id`, `deleted`

**Business Logic:**
- Tracks business expenses
- Can be linked to employees for reimbursement
- Categorization for reporting

**Example Values:**
- `expense_name`: "Office supplies"
- `category`: "Operations"
- `amount_spent`: 45.5000000000

---

### phppos_giftcards

Gift card management.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `giftcard_id` | int(11) | PRIMARY KEY, NOT NULL | Unique gift card identifier |
| `giftcard_number` | varchar(255) | NULL, UNIQUE | Gift card number/code |
| `value` | decimal(23,10) | NOT NULL | Current gift card balance |
| `customer_id` | int(11) | NULL, INDEXED | Associated customer (if any) |
| `deleted` | int(11) | NOT NULL, DEFAULT 0, INDEXED | Soft delete flag |

**Foreign Keys:**
- `customer_id` → `phppos_customers(person_id)`

**Indexes:**
- PRIMARY KEY: `giftcard_id`
- UNIQUE: `giftcard_number`
- KEY: `deleted`, `customer_id`

**Business Logic:**
- Gift card balance tracking
- Value decrements with use, can be recharged
- Can be linked to customer or anonymous

**Example Values:**
- `giftcard_number`: "GC-2026-00123"
- `value`: 50.0000000000 (remaining balance)

---

### phppos_price_tiers

Customer pricing tiers definition.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | int(11) | PRIMARY KEY, NOT NULL | Unique tier identifier |
| `name` | varchar(255) | NOT NULL | Tier name |

**Indexes:**
- PRIMARY KEY: `id`

**Business Logic:**
- Defines customer pricing levels
- Used with *_tier_prices tables for special pricing
- Examples: "Retail", "Wholesale", "VIP"

**Example Values:**
- `id`: 1, `name`: "Retail"
- `id`: 2, `name`: "Wholesale"
- `id`: 3, `name`: "VIP"

---

## Locations & Configuration

### phppos_locations

Store locations/branches.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `location_id` | int(11) | PRIMARY KEY, NOT NULL | Unique location identifier |
| `name` | text | NULL | Location name |
| `address` | text | NULL | Street address |
| `phone` | text | NULL | Phone number |
| `fax` | text | NULL | Fax number |
| `email` | text | NULL | Location email |
| `receive_stock_alert` | text | NULL | Enable stock alerts (Y/N) |
| `stock_alert_email` | text | NULL | Email for stock alerts |
| `timezone` | text | NULL | Location timezone |
| `mailchimp_api_key` | text | NULL | MailChimp integration key |
| `enable_credit_card_processing` | text | NULL | Enable CC processing (Y/N) |
| `merchant_id` | text | NULL | Payment processor merchant ID |
| `merchant_password` | text | NULL | Payment processor password |
| `default_tax_1_rate` | text | NULL | Default tax 1 percentage |
| `default_tax_1_name` | text | NULL | Default tax 1 name |
| `default_tax_2_rate` | text | NULL | Default tax 2 percentage |
| `default_tax_2_name` | text | NULL | Default tax 2 name |
| `default_tax_2_cumulative` | text | NULL | Is tax 2 cumulative (Y/N) |
| `default_tax_3_rate` | text | NULL | Default tax 3 percentage |
| `default_tax_3_name` | text | NULL | Default tax 3 name |
| `default_tax_4_rate` | text | NULL | Default tax 4 percentage |
| `default_tax_4_name` | text | NULL | Default tax 4 name |
| `default_tax_5_rate` | text | NULL | Default tax 5 percentage |
| `default_tax_5_name` | text | NULL | Default tax 5 name |
| `deleted` | int(11) | DEFAULT 0, INDEXED | Soft delete flag |

**Indexes:**
- PRIMARY KEY: `location_id`
- KEY: `deleted`

**Business Logic:**
- Multi-location support
- Location-specific configuration
- Up to 5 default taxes per location
- Payment processor integration per location

**Example Values:**
- `name`: "Main Store", "Warehouse"
- `default_tax_1_name`: "VAT", `default_tax_1_rate`: "16"
- `timezone`: "Africa/Nairobi"

---

### phppos_location_items

Location-specific item inventory and pricing.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `location_id` | int(11) | PRIMARY KEY, NOT NULL | Location reference |
| `item_id` | int(11) | PRIMARY KEY, NOT NULL, INDEXED | Item reference |
| `location` | varchar(255) | NOT NULL, DEFAULT '' | Location description/bin |
| `cost_price` | decimal(23,10) | NULL | Location-specific cost |
| `wholesale_price` | decimal(23,10) | NULL | Location-specific wholesale |
| `unit_price` | decimal(23,10) | NULL | Location-specific retail |
| `promo_price` | decimal(23,10) | NULL | Location-specific promo |
| `start_date` | date | NULL | Promotion start date |
| `end_date` | date | NULL | Promotion end date |
| `quantity` | decimal(23,10) | DEFAULT 0.0000000000 | Quantity at location |
| `reorder_level` | decimal(23,10) | NULL | Reorder threshold |
| `override_default_tax` | int(11) | NOT NULL, DEFAULT 0 | Custom tax override flag |

**Indexes:**
- PRIMARY KEY: `location_id`, `item_id` (composite)
- KEY: `item_id`

**Business Logic:**
- Per-location inventory quantities
- Location-specific pricing
- Warehouse bin location tracking

---

### phppos_location_items_taxes

Location-specific item tax overrides.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | int(11) | PRIMARY KEY, NOT NULL | Unique tax record identifier |
| `location_id` | int(11) | NOT NULL | Location reference |
| `item_id` | int(11) | NOT NULL, INDEXED | Item reference |
| `name` | varchar(255) | NOT NULL | Tax name |
| `percent` | decimal(16,3) | NOT NULL | Tax percentage |
| `cumulative` | int(11) | NOT NULL, DEFAULT 0 | Compound tax flag |

**Indexes:**
- PRIMARY KEY: `id`
- UNIQUE: `location_id`, `item_id`, `name`, `percent` (composite)
- KEY: `item_id`

---

### phppos_location_items_tier_prices

Location and tier-specific item pricing.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `tier_id` | int(11) | PRIMARY KEY, NOT NULL | Price tier reference |
| `item_id` | int(11) | PRIMARY KEY, NOT NULL | Item reference |
| `location_id` | int(11) | PRIMARY KEY, NOT NULL | Location reference |
| `unit_price` | decimal(23,10) | DEFAULT 0.0000000000 | Tier-specific price |
| `percent_off` | int(11) | NULL | Percentage discount |

**Indexes:**
- PRIMARY KEY: `tier_id`, `item_id`, `location_id` (composite)
- KEY: `location_id`, `item_id`

---

### phppos_location_item_kits

Location-specific kit pricing.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `location_id` | int(11) | PRIMARY KEY, NOT NULL | Location reference |
| `item_kit_id` | int(11) | PRIMARY KEY, NOT NULL, INDEXED | Kit reference |
| `unit_price` | decimal(23,10) | NULL | Location-specific price |
| `cost_price` | decimal(23,10) | NULL | Location-specific cost |
| `override_default_tax` | int(11) | NOT NULL, DEFAULT 0 | Custom tax override flag |

**Indexes:**
- PRIMARY KEY: `location_id`, `item_kit_id` (composite)
- KEY: `item_kit_id`

---

### phppos_location_item_kits_taxes

Location-specific kit tax overrides.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | int(11) | PRIMARY KEY, NOT NULL | Unique tax record identifier |
| `location_id` | int(11) | NOT NULL | Location reference |
| `item_kit_id` | int(11) | NOT NULL, INDEXED | Kit reference |
| `name` | varchar(255) | NOT NULL | Tax name |
| `percent` | decimal(16,3) | NOT NULL | Tax percentage |
| `cumulative` | int(11) | NOT NULL, DEFAULT 0 | Compound tax flag |

**Indexes:**
- PRIMARY KEY: `id`
- UNIQUE: `location_id`, `item_kit_id`, `name`, `percent` (composite)
- KEY: `item_kit_id`

---

### phppos_location_item_kits_tier_prices

Location and tier-specific kit pricing.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `tier_id` | int(11) | PRIMARY KEY, NOT NULL | Price tier reference |
| `item_kit_id` | int(11) | PRIMARY KEY, NOT NULL | Kit reference |
| `location_id` | int(11) | PRIMARY KEY, NOT NULL | Location reference |
| `unit_price` | decimal(23,10) | DEFAULT 0.0000000000 | Tier-specific price |
| `percent_off` | int(11) | NULL | Percentage discount |

**Indexes:**
- PRIMARY KEY: `tier_id`, `item_kit_id`, `location_id` (composite)
- KEY: `location_id`, `item_kit_id`

---

### phppos_app_config

Application configuration settings.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `key` | varchar(255) | PRIMARY KEY, NOT NULL | Configuration key name |
| `value` | text | NOT NULL | Configuration value |

**Indexes:**
- PRIMARY KEY: `key`

**Business Logic:**
- Key-value configuration storage
- System-wide settings
- JSON or serialized values for complex settings

**Example Values:**
- `key`: "company_name", `value`: "My Store"
- `key`: "currency_symbol", `value`: "KSh"
- `key`: "timezone", `value`: "Africa/Nairobi"

---

### phppos_app_files

Binary file storage.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `file_id` | int(11) | PRIMARY KEY, NOT NULL | Unique file identifier |
| `file_name` | varchar(255) | NOT NULL | Original filename |
| `file_data` | longblob | NOT NULL | Binary file data |

**Indexes:**
- PRIMARY KEY: `file_id`

**Business Logic:**
- Stores images, documents, etc.
- Referenced by image_id fields in other tables
- LONGBLOB supports files up to 4GB

**Example Values:**
- `file_name`: "product-123.jpg"
- `file_data`: [binary image data]

---

## Summary Statistics

### Table Count
- **Total Tables:** 58

### Table Categories
- **Core Entities:** 8 (people, customers, suppliers, employees, items, item_kits, locations, price_tiers)
- **Sales Tables:** 10 (sales, sales_items, sales_item_kits, taxes, payments + employee variants)
- **Inventory:** 4 (inventory, employee_inventory, receivings, allocations)
- **Location-Specific:** 12 (location_items, location_item_kits + taxes/tier_prices)
- **Employee-Specific:** 14 (employee_items, employee_item_kits, employee_sales + variants)
- **Permissions:** 4 (modules, modules_actions, permissions, permissions_actions)
- **Audit:** 2 (employees_audit, sales_audit)
- **Configuration:** 4 (app_config, app_files, sessions, admin_otp)
- **Financial:** 4 (store_accounts, register_log, expenses, giftcards)

### Key Patterns

#### Soft Delete Pattern
Tables using `deleted` flag (0=active, 1=deleted):
- phppos_customers
- phppos_employees
- phppos_suppliers
- phppos_items
- phppos_item_kits
- phppos_sales
- phppos_allocations
- phppos_receivings
- phppos_expenses
- phppos_giftcards
- phppos_locations
- phppos_register_log
- phppos_store_accounts
- phppos_employee_sales

#### Audit Fields Pattern
Tables with audit trails:
- `created_time`, `updated_time`, `created_by`, `updated_by` (phppos_people)
- Dedicated audit tables (phppos_employees_audit, phppos_sales_audit)

#### eTIMS Integration Fields
Tables with eTIMS tax compliance fields:
- phppos_sales
- phppos_employee_sales
- phppos_items

eTIMS fields:
- `etims_invoice_number`: Official tax invoice number
- `etims_scu_id`: Sales Control Unit ID
- `etims_cu_inv_no`: Control Unit invoice number
- `etims_internal_data`: Internal reference data
- `etims_receipt_signature`: Digital signature
- `etims_signature_link`: QR code verification URL
- `etims_version`: Protocol version
- `etims_tax_type`: Tax classification (items)

#### Decimal Precision
Most monetary and quantity fields use `decimal(23,10)` for high precision:
- Supports values up to 9,999,999,999,999.9999999999
- 10 decimal places for fractional quantities
- Critical for accurate financial calculations

#### Multi-Location Support
The system supports multiple locations with:
- Location-specific inventory (`phppos_location_items`)
- Location-specific pricing
- Location-specific tax configurations
- Employee-location assignments

#### Pricing Hierarchy
1. Base item price (`phppos_items.unit_price`)
2. Location-specific override (`phppos_location_items.unit_price`)
3. Employee-specific override (`phppos_employee_items.unit_price`)
4. Tier-based pricing (`phppos_*_tier_prices`)
5. Promotional pricing (`promo_price` with date range)

---

## Data Integrity Notes

### Foreign Key Relationships
- All person-based entities link to `phppos_people(person_id)`
- Sales transactions link to customers, employees, locations
- Inventory transactions link to items, locations, users
- Tax records link to items/kits with unique constraints
- Tier pricing links to price_tiers table

### Unique Constraints
- Account numbers (customers, suppliers, employees)
- Item numbers and product IDs (barcodes)
- Gift card numbers
- Invoice numbers (sales)
- Session IDs
- Module and action identifiers

### Composite Keys
Many tables use composite primary keys for junction tables:
- `(location_id, item_id)` for location inventory
- `(employee_id, item_id)` for employee inventory
- `(sale_id, item_id, line)` for sale line items
- `(tier_id, item_id)` for tier pricing

---

## Version Information
This data dictionary is based on the MySQL dump structure from the lucasa database. The schema uses InnoDB storage engine with UTF-8 Unicode collation throughout, ensuring proper support for international characters and data integrity through foreign key constraints.

**eTIMS Compliance:** The database includes comprehensive support for the Kenya Revenue Authority's Electronic Tax Invoice Management System (eTIMS), with dedicated fields for tax invoice tracking, digital signatures, and QR code verification links.

**Audit Trail:** Critical tables include full audit logging (employees_audit, sales_audit) with field-level change tracking, IP addresses, and user agent information for security and compliance purposes.

**Multi-tenancy:** The system supports multiple locations with independent inventory, pricing, and tax configurations while maintaining centralized customer and product catalogs.
