## LinkWay Data Dictionary

This document lists the core application tables and their columns, with simplified types and meanings. Internal Django/Celery tables are omitted for brevity.

> Types are simplified: e.g. `decimal` stands for `DecimalField(max_digits=…, decimal_places=…)`.

---

## 1. `authentication_user`

Holds all users (sellers, marketers, buyers, admins).

| Column                      | Type        | Description                                                  |
|-----------------------------|-------------|--------------------------------------------------------------|
| `id`                        | uuid (PK)   | Primary key for the user.                                   |
| `email`                     | string      | Unique login identifier.                                    |
| `role`                      | string      | One of `seller`, `marketer`, `buyer`, `admin`.             |
| `full_name`                 | string      | User’s full name.                                           |
| `phone_number`              | string?     | Contact phone number.                                       |
| `profile_image_url`         | text?       | URL or data URI for profile image.                          |
| `is_verified`               | bool        | Whether email/KYC is verified.                              |
| `is_active`                 | bool        | Whether the account can log in.                             |
| `is_staff`                  | bool        | Django admin/staff flag.                                    |
| `is_superuser`              | bool        | Superuser flag.                                             |
| `created_at`                | datetime    | When the user was created.                                  |
| `updated_at`                | datetime    | Last profile update.                                        |
| `last_login`                | datetime?   | Last time user logged in.                                   |
| `bvn`                       | string?     | Bank Verification Number (Nigerian context).                |
| `nin`                       | string?     | National Identification Number.                             |
| `kyc_status`                | string      | KYC status (`pending`, `approved`, etc.).                   |
| `kyc_verified_at`           | datetime?   | When KYC was approved.                                      |
| `bank_name`                 | string?     | Bank name for payouts.                                      |
| `account_number`            | string?     | 10-digit payout account number.                             |
| `account_name`              | string?     | Payout account name.                                        |
| `business_name`             | string?     | Business or brand name.                                     |
| `business_registration_number` | string?  | CAC/registration number if applicable.                      |
| `social_media_handles`      | JSON        | Map of platform → handle.                                   |
| `niche_categories`          | JSON        | List of niches (tags).                                      |
| `audience_size`             | int?        | Estimated audience/followers.                               |

---

## 2. `products_productcategory`

Product category hierarchy.

| Column        | Type      | Description                          |
|---------------|-----------|--------------------------------------|
| `id`          | int (PK)  | Category ID.                         |
| `name`        | string    | Category name (unique).              |
| `slug`        | string    | URL-safe slug (unique).              |
| `parent_id`   | int? (FK) | Parent category ID (self-relation).  |
| `description` | text?     | Optional description.                |
| `is_active`   | bool      | Whether category is active.          |
| `created_at`  | datetime  | When it was created.                 |

---

## 3. `products_product`

Products offered by sellers.

| Column                 | Type        | Description                                                  |
|------------------------|-------------|--------------------------------------------------------------|
| `id`                   | uuid (PK)   | Product ID.                                                 |
| `seller_id`            | uuid (FK)   | Seller (→ `authentication_user`).                          |
| `category_id`          | int? (FK)   | Category (→ `products_productcategory`).                    |
| `name`                 | string      | Product name.                                               |
| `slug`                 | string      | Unique slug for public URLs.                               |
| `description`          | text        | Full description.                                           |
| `short_description`    | string?     | Short/marketing blurb.                                     |
| `price`                | decimal     | Retail price.                                               |
| `compare_at_price`     | decimal?    | Original/strikethrough price.                              |
| `cost_price`           | decimal?    | Internal cost price.                                        |
| `commission_rate`      | decimal     | Marketer commission rate (percentage).                     |
| `commission_type`      | string      | `percentage` or `fixed`.                                   |
| `fixed_commission_amount` | decimal? | Fixed per-unit commission (when `commission_type=fixed`).  |
| `stock_quantity`       | int         | Units in stock.                                             |
| `sku`                  | string?     | Unique SKU.                                                 |
| `images`               | JSON        | List of image URLs or data URIs.                            |
| `specifications`       | JSON        | Arbitrary key/value spec data.                             |
| `is_active`            | bool        | Whether product can be bought/promoted.                    |
| `is_featured`          | bool        | Featured flag.                                              |
| `min_order_quantity`   | int         | Minimum quantity per order.                                |
| `max_order_quantity`   | int?        | Maximum quantity per order.                                |
| `weight_kg`            | decimal?    | Weight in kilograms.                                       |
| `dimensions`           | JSON?       | Length/width/height etc.                                   |
| `seo_title`            | string?     | SEO title override.                                         |
| `seo_description`      | text?       | SEO description.                                            |
| `seo_keywords`         | JSON        | List of keywords.                                           |
| `total_sales`          | int         | Units sold (aggregate).                                     |
| `total_revenue`        | decimal     | Total revenue from this product.                           |
| `average_rating`       | decimal     | Average review rating.                                      |
| `review_count`         | int         | Number of reviews.                                         |
| `created_at`           | datetime    | When product was created.                                  |
| `updated_at`           | datetime    | Last update.                                               |

---

## 4. `affiliates_affiliatelink`

Referral links for marketers.

| Column              | Type        | Description                                                  |
|---------------------|-------------|--------------------------------------------------------------|
| `id`                | uuid (PK)   | Link ID.                                                    |
| `marketer_id`       | uuid (FK)   | Marketer (→ `authentication_user`).                        |
| `product_id`        | uuid (FK)   | Product (→ `products_product`).                            |
| `unique_slug`       | string      | Short unique slug used in referral URLs.                    |
| `full_url`          | text        | Full public URL (backend or frontend).                      |
| `custom_alias`      | string?     | Optional human-readable alias.                             |
| `is_active`         | bool        | Whether the link can be used.                              |
| `expires_at`        | datetime?   | Optional expiry time.                                      |
| `click_count`       | int         | Total clicks.                                               |
| `conversion_count`  | int         | Number of conversions/orders.                              |
| `total_revenue`     | decimal     | Aggregate revenue from conversions.                        |
| `total_commission`  | decimal     | Aggregate gross commission generated.                      |
| `created_at`        | datetime    | When link was created.                                     |
| `last_clicked_at`   | datetime?   | Last click timestamp.                                      |

Uniqueness:

- `unique_slug` globally unique.
- `(marketer_id, product_id)` unique to prevent duplicate active links.

---

## 5. `affiliates_catalogue` & `affiliates_catalogue_links`

### `affiliates_catalogue`

| Column        | Type        | Description                                      |
|---------------|-------------|--------------------------------------------------|
| `id`          | uuid (PK)   | Catalogue ID.                                    |
| `marketer_id` | uuid (FK)   | Owner (→ `authentication_user`).                |
| `name`        | string      | Name (e.g. “Makeup Essentials”).                |
| `description` | text?       | Optional description.                            |
| `slug`        | string      | Unique slug for public URLs.                    |
| `is_active`   | bool        | Active flag (soft-delete when false).           |
| `created_at`  | datetime    | Creation time.                                   |

### `affiliates_catalogue_links`

| Column          | Type      | Description                                    |
|-----------------|-----------|------------------------------------------------|
| `id`            | int (PK)  | Row ID (implicit).                             |
| `catalogue_id`  | uuid (FK) | Catalogue (→ `affiliates_catalogue`).         |
| `affiliatelink_id` | uuid(FK) | Link (→ `affiliates_affiliatelink`).        |

---

## 6. `affiliates_clicktracking`

Per-click tracking for affiliate links.

| Column           | Type      | Description                                    |
|------------------|-----------|------------------------------------------------|
| `id`             | int (PK)  | Click ID.                                      |
| `link_id`        | uuid (FK) | Affiliate link clicked.                        |
| `ip_address`     | inet      | Remote IP address.                             |
| `user_agent`     | text?     | Raw user agent.                                |
| `device_type`    | string?   | Mobile / desktop / tablet etc.                 |
| `browser`        | string?   | Browser family.                                |
| `operating_system` | string? | OS family.                                     |
| `referrer_url`   | text?     | HTTP referrer.                                 |
| `landing_page_url` | text?   | Full URL of landing page.                     |
| `country_code`   | string?   | ISO country code.                             |
| `city`           | string?   | City name (if geo-resolved).                  |
| `session_id`     | string?   | Session identifier.                           |
| `cookie_id`      | string?   | Attribution cookie identifier.                |
| `clicked_at`     | datetime  | Timestamp of click.                            |
| `is_bot`         | bool      | Bot detection flag.                            |
| `is_suspicious`  | bool      | Flag when click is suspicious.                |
| `fraud_score`    | decimal   | Model score (0–1).                             |

---

## 7. `affiliates_attributiontracking`

Attribution chain for a cookie/session.

| Column               | Type        | Description                                      |
|----------------------|-------------|--------------------------------------------------|
| `id`                 | uuid (PK)   | Attribution ID.                                  |
| `cookie_id`          | string      | Unique cookie identifier.                        |
| `session_id`         | string?     | Session identifier.                              |
| `first_click_link_id`| uuid? (FK)  | First clicked link.                              |
| `last_click_link_id` | uuid? (FK)  | Last clicked link.                               |
| `attribution_model`  | string      | e.g. `last_click`.                               |
| `click_chain`        | JSON        | List of clicks (id, timestamp, weight).          |
| `created_at`         | datetime    | Created when first click was recorded.           |
| `expires_at`         | datetime    | Attribution expiry.                              |
| `converted`          | bool        | Whether an order converted.                      |
| `converted_at`       | datetime?   | When conversion happened.                        |
| `order_id`           | uuid? (FK)  | Linked order (→ `orders_order`).                 |

---

## 8. `orders_cart` & `orders_cartitem`

### `orders_cart`

| Column      | Type        | Description                         |
|-------------|-------------|-------------------------------------|
| `id`        | uuid (PK)   | Cart ID.                            |
| `buyer_id`  | uuid (FK)   | Buyer (→ `authentication_user`).   |
| `is_active` | bool        | Active cart flag.                  |
| `created_at`| datetime    | When the cart was created.         |
| `updated_at`| datetime    | Last update.                        |

### `orders_cartitem`

| Column       | Type        | Description                                      |
|--------------|-------------|--------------------------------------------------|
| `id`         | int (PK)    | Item ID.                                         |
| `cart_id`    | uuid (FK)   | Cart (→ `orders_cart`).                          |
| `product_id` | uuid (FK)   | Product (→ `products_product`).                  |
| `quantity`   | int         | Quantity in cart.                               |
| `unit_price` | decimal     | Price at time of adding to cart.               |
| `added_at`   | datetime    | Added timestamp.                                |

Unique constraint:

- `(cart_id, product_id)` – one row per product per cart.

---

## 9. `orders_customerorder`

Top-level checkout record.

| Column            | Type        | Description                                      |
|-------------------|-------------|--------------------------------------------------|
| `id`              | uuid (PK)   | CustomerOrder ID.                                |
| `order_number`    | string      | Human-readable ID (e.g. `CO-...`).               |
| `buyer_id`        | uuid (FK)   | Buyer (→ `authentication_user`).                |
| `customer_email`  | string      | Email used at checkout.                         |
| `customer_name`   | string      | Name used at checkout.                          |
| `customer_phone`  | string      | Phone used at checkout.                         |
| `shipping_address`| JSON        | Structured address (line1/city/state/country).  |
| `subtotal`        | decimal     | Items total (before shipping/tax).              |
| `shipping_fee`    | decimal     | Shipping cost.                                  |
| `tax_amount`      | decimal     | Tax amount.                                     |
| `total_amount`    | decimal     | Final amount charged.                           |
| `payment_status`  | string      | `pending`, `paid`, `failed`, etc.               |
| `payment_reference` | string    | Internal payment reference.                     |
| `paystack_reference` | string?  | External Paystack reference.                    |
| `created_at`      | datetime    | Created time.                                   |
| `updated_at`      | datetime    | Last update.                                    |
| `paid_at`         | datetime?   | When payment was confirmed.                     |

---

## 10. `orders_order`

Seller/product-level order line.

| Column             | Type        | Description                                      |
|--------------------|-------------|--------------------------------------------------|
| `id`               | uuid (PK)   | Order line ID.                                   |
| `order_number`     | string      | Human-readable ID (e.g. `ORD-...`).             |
| `customer_order_id`| uuid? (FK)  | Parent `orders_customerorder`.                  |
| `product_id`       | uuid (FK)   | Ordered product.                                |
| `seller_id`        | uuid (FK)   | Seller.                                         |
| `marketer_id`      | uuid? (FK)  | Marketer (if attributed).                       |
| `customer_email`   | string      | Buyer email at checkout.                        |
| `customer_name`    | string      | Buyer name at checkout.                         |
| `customer_phone`   | string      | Buyer phone at checkout.                        |
| `shipping_address` | JSON        | Shipping address.                               |
| `quantity`         | int         | Quantity ordered.                               |
| `unit_price`       | decimal     | Unit price used for billing.                    |
| `subtotal`         | decimal     | `unit_price * quantity`.                        |
| `shipping_fee`     | decimal     | Shipping portion allocated to this line.        |
| `tax_amount`       | decimal     | Tax portion for this line.                      |
| `total_amount`     | decimal     | Total for this line.                            |
| `commission_rate`  | decimal?    | Snapshot of commission rate at order time.     |
| `commission_amount`| decimal     | Commission gross amount (before platform fee). |
| `status`           | string      | `pending`, `processing`, `shipped`, etc.        |
| `payment_status`   | string      | `pending`, `paid`, `failed`, etc.              |
| `payment_method`   | string?     | e.g. `paystack`.                                |
| `payment_reference`| string?     | Legacy per-line payment ref.                    |
| `paystack_reference`| string?    | Provider reference.                             |
| `refund_status`    | string      | `none`, `requested`, `approved`, etc.          |
| `refund_amount`    | decimal     | Amount refunded.                                |
| `refund_reason`    | text?       | Explanation when refunded.                      |
| `refund_requested_at` | datetime?| When refund was requested.                      |
| `refund_processed_at` | datetime?| When refund was handled.                        |
| `attribution_cookie_id` | string?| Attribution cookie ID.                          |
| `notes`            | text?       | Internal notes.                                 |
| `created_at`       | datetime    | Creation time.                                  |
| `updated_at`       | datetime    | Last update.                                    |
| `paid_at`          | datetime?   | When payment was confirmed for this line.       |
| `shipped_at`       | datetime?   | When shipped.                                   |
| `delivered_at`     | datetime?   | When delivered.                                 |

---

## 11. `commissions_commission`

Marketer commission for a specific order line.

| Column             | Type        | Description                                      |
|--------------------|-------------|--------------------------------------------------|
| `id`               | uuid (PK)   | Commission ID.                                   |
| `order_id`         | uuid (FK)   | Order line (→ `orders_order`).                  |
| `marketer_id`      | uuid (FK)   | Marketer.                                       |
| `product_id`       | uuid? (FK)  | Product (nullable for backward compatibility).  |
| `gross_sale_amount`| decimal     | Order line subtotal.                            |
| `commission_rate`  | decimal     | Commission percentage at time of sale.          |
| `commission_amount`| decimal     | Gross commission (before platform fee).         |
| `platform_fee_rate`| decimal     | Platform fee rate (default ~2.5%).              |
| `platform_fee_amount`| decimal?  | Fee amount taken by platform.                   |
| `net_commission`   | decimal?    | Amount payable to marketer after fee.           |
| `status`           | string      | `pending`, `earned`, `held`, `approved`, `paid`, `reversed`. |
| `earned_at`        | datetime?   | When commission was earned.                     |
| `holdback_until`   | datetime?   | End of hold period.                             |
| `approved_at`      | datetime?   | When moved to `approved`.                       |
| `payout_id`        | uuid? (FK)  | Linked payout (→ `commissions_payout`).        |
| `paid_at`          | datetime?   | When paid out.                                  |
| `reversal_reason`  | text?       | Why reversed.                                   |
| `reversed_at`      | datetime?   | When reversed.                                  |
| `created_at`       | datetime    | Created time.                                   |

---

## 12. `commissions_payout` & `commissions_payoutcommission`

### `commissions_payout`

| Column                    | Type        | Description                                      |
|---------------------------|-------------|--------------------------------------------------|
| `id`                      | uuid (PK)   | Payout ID.                                       |
| `marketer_id`             | uuid (FK)   | Recipient marketer.                              |
| `payout_method`           | string      | e.g. `bank_transfer`.                            |
| `total_amount`            | decimal     | Total amount of this payout.                     |
| `commission_count`        | int         | Number of commissions included.                  |
| `bank_name`               | string?     | Bank used.                                       |
| `account_number`          | string?     | Destination account number.                      |
| `account_name`            | string?     | Destination account name.                        |
| `status`                  | string      | `pending`, `processing`, `completed`, `failed`, `cancelled`. |
| `paystack_transfer_reference` | string? | Paystack transfer reference.                     |
| `transfer_code`           | string?     | Paystack transfer code.                          |
| `failure_reason`          | text?       | Reason when failed/cancelled.                    |
| `requested_at`            | datetime    | When payout was requested.                       |
| `processed_at`            | datetime?   | When transfer was initiated.                     |
| `completed_at`            | datetime?   | When marked completed or cancelled.              |

### `commissions_payoutcommission`

| Column        | Type      | Description                              |
|---------------|-----------|------------------------------------------|
| `id`          | int (PK)  | Row ID.                                  |
| `payout_id`   | uuid (FK) | Payout (→ `commissions_payout`).        |
| `commission_id`| uuid(FK) | Commission (→ `commissions_commission`).|

Unique constraint:

- `(payout_id, commission_id)` – a commission can only appear once in a given payout.

---

## 13. `payments_paymentlog`

Raw payment logs from Paystack.

| Column     | Type      | Description                         |
|------------|-----------|-------------------------------------|
| `id`       | int (PK)  | Log ID.                             |
| `provider` | string    | Provider name (`paystack`).        |
| `reference`| string    | Unique reference.                   |
| `raw_payload` | JSON   | Full webhook/verification payload.  |
| `created_at` | datetime| When stored.                        |

---

## 14. `ai_services_aicontentlog`

AI-generated content history.

| Column             | Type      | Description                                      |
|--------------------|-----------|--------------------------------------------------|
| `id`               | int (PK)  | Log ID.                                         |
| `user_id`          | uuid (FK) | Requesting user.                                |
| `product_id`       | uuid (FK) | Product.                                        |
| `content_type`     | string    | Type (caption, script, etc.).                  |
| `prompt`           | text      | Prompt used.                                    |
| `generated_content`| text      | Output text.                                    |
| `platform`         | string    | Target platform (e.g. Instagram).              |
| `tone`             | string    | Requested tone.                                 |
| `was_used`         | bool      | Whether content was used.                       |
| `feedback_rating`  | int?      | Optional rating.                                |
| `tokens_used`      | int?      | Token count (if tracked).                       |
| `generation_time_ms`| int?     | Generation time.                                |
| `created_at`       | datetime  | When generated.                                 |

---

## 15. `ai_services_productrecommendation`

Product recommendations for marketers.

| Column                | Type      | Description                             |
|-----------------------|-----------|-----------------------------------------|
| `id`                  | int (PK)  | Recommendation ID.                      |
| `marketer_id`         | uuid (FK) | Marketer.                               |
| `product_id`          | uuid (FK) | Product.                                |
| `recommendation_score`| decimal   | Higher = stronger recommendation.       |
| `recommendation_reason`| text?    | Human-readable reason.                  |
| `match_factors`       | JSON      | Feature-level explanation.              |
| `was_promoted`        | bool      | Whether marketer promoted it.           |
| `promoted_at`         | datetime? | When it was promoted.                   |
| `created_at`          | datetime  | When generated.                         |
| `expires_at`          | datetime? | Recommendation expiry.                 |

---

## 16. `analytics_activitylog`

General activity log entries.

| Column        | Type      | Description                             |
|---------------|-----------|-----------------------------------------|
| `id`          | int (PK)  | Log ID.                                 |
| `user_id`     | uuid? (FK)| User who performed the action.         |
| `action`      | string    | Action name.                            |
| `entity_type` | string?   | Type of entity (order, product, etc.). |
| `entity_id`   | string?   | ID of the entity.                       |
| `ip_address`  | inet?     | IP associated with action.             |
| `user_agent`  | text?     | User agent string.                      |
| `metadata`    | JSON      | Extra details.                          |
| `created_at`  | datetime  | Timestamp.                              |

---

## 17. `analytics_frauddetectionlog`

Fraud detection model outputs.

| Column          | Type      | Description                             |
|-----------------|-----------|-----------------------------------------|
| `id`            | int (PK)  | Log ID.                                 |
| `entity_type`   | string    | Entity type (order, click, etc.).      |
| `entity_id`     | string    | Entity ID.                              |
| `fraud_type`    | string    | Type/category of fraud.                 |
| `fraud_score`   | decimal   | Score from model.                       |
| `indicators`    | JSON      | Features/indicators used.              |
| `action_taken`  | string    | E.g. blocked, flagged, allowed.        |
| `is_false_positive` | bool? | Review outcome.                         |
| `reviewed_by_id`| uuid? (FK)| Reviewing admin.                        |
| `reviewed_at`   | datetime? | Review timestamp.                       |
| `detected_at`   | datetime  | Detection timestamp.                    |

---

## 18. `notifications_notification`

In-app notifications.

| Column      | Type      | Description                         |
|-------------|-----------|-------------------------------------|
| `id`        | int (PK)  | Notification ID.                    |
| `user_id`   | uuid (FK) | Recipient user.                     |
| `title`     | string    | Notification title.                 |
| `body`      | text      | Notification body.                  |
| `is_read`   | bool      | Read/unread status.                 |
| `created_at`| datetime  | When created.                        |

---

This dictionary covers all core business tables used by LinkWay for users, products, affiliate tracking, orders, commissions, payouts, payments, AI features, analytics, and notifications. For exact constraints and indexes, refer to `database/schema.sql`.

