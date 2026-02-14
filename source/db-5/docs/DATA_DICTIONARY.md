# DB-5 Data Dictionary – Lucasa POS Retail

Column-level reference for all phppos tables in db-5. Types are PostgreSQL types.

---

## 1. `phppos_people`

Base table for all persons (customers, employees, suppliers).

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `first_name` | varchar(255) | yes | — | First name |
| `last_name` | varchar(255) | yes | — | Last name |
| `phone_number` | varchar(50) | yes | — | Phone number |
| `email` | varchar(255) | yes | — | Email address |
| `address_1` | varchar(255) | yes | — | Address line 1 |
| `address_2` | varchar(255) | yes | — | Address line 2 |
| `city` | varchar(255) | yes | — | City |
| `state` | varchar(50) | yes | — | State/region |
| `zip` | varchar(20) | yes | — | Postal code |
| `country` | varchar(100) | yes | — | Country |
| `comments` | text | yes | — | Notes |
| `person_id` | integer | **PK** | — | Unique person identifier |

**Constraints:** Primary key: `person_id`

---

## 2. `phppos_employees`

Employee accounts linked to people.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `username` | varchar(255) | yes | — | Login username |
| `password` | varchar(255) | yes | — | Password hash |
| `person_id` | integer | yes | — | FK to phppos_people |
| `balance` | numeric(15,2) | yes | 0 | Employee balance |
| `deleted` | integer | yes | 0 | Soft delete flag |
| `hide_from_switch_user` | integer | yes | 0 | Hide from user switcher |

**Constraints:** Foreign key: `person_id` → `phppos_people(person_id)`

---

## 3. `phppos_employees_locations`

Assigns employees to store locations.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `employee_id` | integer | yes | — | FK to phppos_employees (person_id) |
| `location_id` | integer | yes | — | FK to phppos_locations |

**Constraints:** Foreign keys: `employee_id` → `phppos_people(person_id)`, `location_id` → `phppos_locations(location_id)`

---

## 4. `phppos_items`

Product/item master data.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `name` | varchar(255) | yes | — | Item name |
| `category` | varchar(255) | yes | — | Category |
| `description` | text | yes | — | Description |
| `cost_price` | numeric(15,2) | yes | 0 | Cost price |
| `unit_price` | numeric(15,2) | yes | 0 | Selling price |
| `item_id` | integer | **PK** | — | Unique item identifier |
| `allow_alt_description` | integer | yes | 0 | Allow alternate description |
| `is_serialized` | integer | yes | 0 | Serial number tracking |
| `override_default_tax` | integer | yes | 0 | Override default tax |
| `is_service` | integer | yes | 0 | Service item flag |
| `deleted` | integer | yes | 0 | Soft delete flag |

**Constraints:** Primary key: `item_id`

---

## 5. `phppos_locations`

Store location definitions.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `location_id` | integer | **PK** | — | Unique location identifier |
| `name` | varchar(255) | yes | — | Location name |
| `address` | text | yes | — | Address |
| `phone` | varchar(50) | yes | — | Phone |
| `fax` | varchar(50) | yes | — | Fax |
| `email` | varchar(255) | yes | — | Email |
| `receive_stock_alert` | varchar(10) | yes | '0' | Stock alert enabled |
| `stock_alert_email` | varchar(255) | yes | — | Alert email |
| `timezone` | varchar(100) | yes | — | Timezone |
| `mailchimp_api_key` | varchar(255) | yes | — | Mailchimp key |
| `enable_credit_card_processing` | varchar(10) | yes | '0' | CC processing |
| `merchant_id` | varchar(255) | yes | — | Merchant ID |
| `merchant_password` | varchar(255) | yes | — | Merchant password |
| `default_tax_1_rate` | numeric(10,2) | yes | — | Tax 1 rate |
| `default_tax_1_name` | varchar(255) | yes | — | Tax 1 name |
| `default_tax_2_rate` | numeric(10,2) | yes | — | Tax 2 rate |
| `default_tax_2_name` | varchar(255) | yes | — | Tax 2 name |
| `default_tax_2_cumulative` | varchar(10) | yes | '0' | Tax 2 cumulative |
| `default_tax_3_rate` | numeric(10,2) | yes | — | Tax 3 rate |
| `default_tax_3_name` | varchar(255) | yes | — | Tax 3 name |
| `default_tax_4_rate` | numeric(10,2) | yes | — | Tax 4 rate |
| `default_tax_4_name` | varchar(255) | yes | — | Tax 4 name |
| `default_tax_5_rate` | numeric(10,2) | yes | — | Tax 5 rate |
| `default_tax_5_name` | varchar(255) | yes | — | Tax 5 name |
| `deleted` | integer | yes | 0 | Soft delete flag |

**Constraints:** Primary key: `location_id`

---

## 6. `phppos_location_items`

Location-specific inventory quantities.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `location_id` | integer | yes | — | FK to phppos_locations |
| `item_id` | integer | yes | — | FK to phppos_items |
| `quantity` | numeric(15,2) | yes | 0 | Quantity on hand |

**Constraints:** Foreign keys: `location_id` → `phppos_locations(location_id)`, `item_id` → `phppos_items(item_id)`

---

## 7. `phppos_sales`

Main sales transaction header.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `sale_id` | integer | **PK** | — | Unique sale identifier |
| `employee_id` | integer | yes | — | FK to phppos_employees (person_id) |
| `sale_time` | timestamp | yes | — | Sale timestamp |
| `customer_id` | integer | yes | — | Customer (person_id) |
| `payment_type` | varchar(50) | yes | — | Payment method |
| `location_id` | integer | yes | — | FK to phppos_locations |

**Constraints:** Primary key: `sale_id`. Foreign keys: `employee_id` → `phppos_people(person_id)`, `location_id` → `phppos_locations(location_id)`

---

## Sample Query Patterns

### Sales by employee with person details
```sql
SELECT s.sale_id, s.sale_time, s.payment_type,
       p.first_name, p.last_name, p.email
FROM phppos_sales s
JOIN phppos_people p ON s.employee_id = p.person_id
WHERE s.sale_time >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY s.sale_time DESC;
```

### Inventory by location
```sql
SELECT l.name AS location_name, i.name AS item_name, li.quantity
FROM phppos_location_items li
JOIN phppos_locations l ON li.location_id = l.location_id
JOIN phppos_items i ON li.item_id = i.item_id
WHERE i.deleted = 0 AND l.deleted = 0
ORDER BY l.name, i.name;
```

### Sales summary by location
```sql
SELECT l.name, COUNT(*) AS sale_count
FROM phppos_sales s
JOIN phppos_locations l ON s.location_id = l.location_id
WHERE s.sale_time >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY l.name
ORDER BY sale_count DESC;
```
