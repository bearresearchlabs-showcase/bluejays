---
title: Shipping Intelligence Database — Documentation
description: Installation guide, specifications, schema, data dictionary.
database: db-9
---

# Shipping Intelligence Database — Documentation

**Database:** db-9  
**Content:** Installation guide, specifications, schema, data dictionary.

---

## Installation Guide

### Step 1: Prerequisites

Ensure PostgreSQL is installed. See specifications for version requirements.

---

### Step 2: Create Database

Create a new database for this schema.

```bash
createdb -U postgres db_9
```

---

### Step 3: Load Schema

Load schema.sql to create tables, indexes, and constraints.

```bash
psql -U postgres -d db_9 -f schema.sql
```

---

### Step 4: Load Data (Optional)

Load sample data from data.sql if available.

```bash
psql -U postgres -d db_9 -f data.sql
```

---

## Specifications

- **PostgreSQL:** 14+
- **Disk:** 100 MB minimum
- **Memory:** 256 MB minimum
- **Platforms:** PostgreSQL

Standard PostgreSQL. No extensions required unless noted.

---

## Schema Overview

**Total tables:** 14

- `shipping_carriers` — (see data dictionary)
- `shipping_zones` — (see data dictionary)
- `shipping_service_types` — (see data dictionary)
- `shipping_rates` — (see data dictionary)
- `packages` — (see data dictionary)
- `shipments` — (see data dictionary)
- `tracking_events` — (see data dictionary)
- `rate_comparison_results` — (see data dictionary)
- `address_validation_results` — (see data dictionary)
- `shipping_adjustments` — (see data dictionary)
- `bulk_shipping_presets` — (see data dictionary)
- `shipping_analytics` — (see data dictionary)
- `international_customs` — (see data dictionary)
- `api_rate_request_log` — (see data dictionary)

---

## Data Dictionary

### `shipping_carriers`

- `carrier_id` VARCHAR(50) PRIMARY KEY
- `carrier_name` VARCHAR(100) NOT NULL
- `carrier_code` VARCHAR(10) UNIQUE, NOT NULL — 'USPS', 'UPS', 'FEDEX'
- `carrier_type` VARCHAR(50)  — 'Postal', 'Courier', 'Freight'
- `api_endpoint` VARCHAR(500) 
- `rate_api_version` VARCHAR(50) 
- `tracking_api_version` VARCHAR(50) 
- `commercial_pricing_available` BOOLEAN 
- `requires_account` BOOLEAN 
- `active_status` BOOLEAN 
- `created_at` TIMESTAMP 
- `updated_at` TIMESTAMP 

### `shipping_zones`

- `zone_id` VARCHAR(255) PRIMARY KEY
- `carrier_id` VARCHAR(50) NOT NULL
- `origin_zip_code` VARCHAR(10) NOT NULL
- `destination_zip_code` VARCHAR(10) NOT NULL
- `zone_number` INTEGER NOT NULL
- `zone_type` VARCHAR(50)  — 'Domestic', 'International', 'Alaska', 'Hawaii'
- `distance_miles` NUMERIC(10, 2) 
- `transit_days_min` INTEGER 
- `transit_days_max` INTEGER 
- `effective_date` DATE NOT NULL
- `expiration_date` DATE 
- `created_at` TIMESTAMP 

### `shipping_service_types`

- `service_id` VARCHAR(255) PRIMARY KEY
- `carrier_id` VARCHAR(50) NOT NULL
- `service_code` VARCHAR(50) NOT NULL
- `service_name` VARCHAR(255) NOT NULL
- `service_category` VARCHAR(100)  — 'Express', 'Ground', 'Priority', 'Economy'
- `domestic_available` BOOLEAN 
- `international_available` BOOLEAN 
- `max_weight_lbs` NUMERIC(10, 2) 
- `max_dimensions_length` NUMERIC(10, 2) 
- `max_dimensions_width` NUMERIC(10, 2) 
- `max_dimensions_height` NUMERIC(10, 2) 
- `tracking_included` BOOLEAN 
- `insurance_available` BOOLEAN 
- `signature_required` BOOLEAN 
- `active_status` BOOLEAN 
- `created_at` TIMESTAMP 

### `shipping_rates`

- `rate_id` VARCHAR(255) PRIMARY KEY
- `carrier_id` VARCHAR(50) NOT NULL
- `service_id` VARCHAR(255) NOT NULL
- `zone_id` VARCHAR(255) 
- `weight_lbs` NUMERIC(10, 4) NOT NULL
- `weight_oz` NUMERIC(10, 4) 
- `length_inches` NUMERIC(10, 2) 
- `width_inches` NUMERIC(10, 2) 
- `height_inches` NUMERIC(10, 2) 
- `dimensional_weight_lbs` NUMERIC(10, 4) 
- `cubic_volume_cubic_inches` NUMERIC(12, 4) 
- `rate_amount` NUMERIC(10, 2) NOT NULL
- `rate_type` VARCHAR(50)  — 'Retail', 'Commercial', 'Daily', 'Cubic'
- `surcharge_amount` NUMERIC(10, 2) 
- `total_rate` NUMERIC(10, 2) NOT NULL
- `effective_date` DATE NOT NULL
- `expiration_date` DATE 
- `rate_source` VARCHAR(100)  — 'API', 'Manual', 'Bulk Import'
- `created_at` TIMESTAMP 

### `packages`

- `package_id` VARCHAR(255) PRIMARY KEY
- `user_id` VARCHAR(255) 
- `package_reference` VARCHAR(255) 
- `weight_lbs` NUMERIC(10, 4) NOT NULL
- `weight_oz` NUMERIC(10, 4) 
- `length_inches` NUMERIC(10, 2) NOT NULL
- `width_inches` NUMERIC(10, 2) NOT NULL
- `height_inches` NUMERIC(10, 2) NOT NULL
- `dimensional_weight_lbs` NUMERIC(10, 4) 
- `cubic_volume_cubic_inches` NUMERIC(12, 4) 
- `package_type` VARCHAR(50)  — 'Envelope', 'Box', 'Tube', 'Flat'
- `package_value` NUMERIC(10, 2) 
- `contents_description` VARCHAR(500) 
- `created_at` TIMESTAMP 
- `updated_at` TIMESTAMP 

### `shipments`

- `shipment_id` VARCHAR(255) PRIMARY KEY
- `package_id` VARCHAR(255) NOT NULL
- `carrier_id` VARCHAR(50) NOT NULL
- `service_id` VARCHAR(255) NOT NULL
- `tracking_number` VARCHAR(255) 
- `origin_name` VARCHAR(255) 
- `origin_address_line1` VARCHAR(255) 
- `origin_address_line2` VARCHAR(255) 
- `origin_city` VARCHAR(100) 
- `origin_state` VARCHAR(2) 
- `origin_zip_code` VARCHAR(10) NOT NULL
- `origin_country` VARCHAR(2) 
- `destination_name` VARCHAR(255) 
- `destination_address_line1` VARCHAR(255) 
- `destination_address_line2` VARCHAR(255) 
- `destination_city` VARCHAR(100) 
- `destination_state` VARCHAR(2) 
- `destination_zip_code` VARCHAR(10) NOT NULL
- `destination_country` VARCHAR(2) 
- `zone_id` VARCHAR(255) 
- `rate_id` VARCHAR(255) 
- `label_cost` NUMERIC(10, 2) 
- `insurance_cost` NUMERIC(10, 2) 
- `signature_cost` NUMERIC(10, 2) 
- `total_cost` NUMERIC(10, 2) NOT NULL
- `shipment_status` VARCHAR(50)  — 'Pending', 'Label Created', 'In Transit', 'Delivered', 'Exception'
- `label_created_at` TIMESTAMP 
- `estimated_delivery_date` DATE 
- `actual_delivery_date` DATE 
- `created_at` TIMESTAMP 
- `updated_at` TIMESTAMP 

### `tracking_events`

- `event_id` VARCHAR(255) PRIMARY KEY
- `shipment_id` VARCHAR(255) NOT NULL
- `tracking_number` VARCHAR(255) NOT NULL
- `event_timestamp` TIMESTAMP NOT NULL
- `event_type` VARCHAR(100)  — 'Label Created', 'In Transit', 'Out for Delivery', 'Delivered', 'Exception'
- `event_status` VARCHAR(100) 
- `event_location` VARCHAR(255) 
- `event_city` VARCHAR(100) 
- `event_state` VARCHAR(2) 
- `event_zip_code` VARCHAR(10) 
- `event_country` VARCHAR(2) 
- `event_description` VARCHAR(1000) 
- `carrier_status_code` VARCHAR(50) 
- `raw_event_data` VARIANT  — JSON data from carrier API
- `created_at` TIMESTAMP 

### `rate_comparison_results`

- `comparison_id` VARCHAR(255) PRIMARY KEY
- `package_id` VARCHAR(255) NOT NULL
- `origin_zip_code` VARCHAR(10) NOT NULL
- `destination_zip_code` VARCHAR(10) NOT NULL
- `comparison_timestamp` TIMESTAMP 
- `cheapest_carrier_id` VARCHAR(50) 
- `cheapest_service_id` VARCHAR(255) 
- `cheapest_rate` NUMERIC(10, 2) 
- `fastest_carrier_id` VARCHAR(50) 
- `fastest_service_id` VARCHAR(255) 
- `fastest_transit_days` INTEGER 
- `total_options_count` INTEGER 
- `comparison_metadata` VARIANT  — JSON with all rate options
- `created_at` TIMESTAMP 

### `address_validation_results`

- `validation_id` VARCHAR(255) PRIMARY KEY
- `input_address_line1` VARCHAR(255) 
- `input_address_line2` VARCHAR(255) 
- `input_city` VARCHAR(100) 
- `input_state` VARCHAR(2) 
- `input_zip_code` VARCHAR(10) 
- `validated_address_line1` VARCHAR(255) 
- `validated_address_line2` VARCHAR(255) 
- `validated_city` VARCHAR(100) 
- `validated_state` VARCHAR(2) 
- `validated_zip_code` VARCHAR(10) 
- `validated_zip_plus_4` VARCHAR(10) 
- `validation_status` VARCHAR(50)  — 'Valid', 'Invalid', 'Corrected', 'Ambiguous'
- `delivery_point_code` VARCHAR(10) 
- `carrier_route` VARCHAR(10) 
- `dpv_confirmation` VARCHAR(50) 
- `cmra_flag` BOOLEAN 
- `vacant_flag` BOOLEAN 
- `residential_flag` BOOLEAN 
- `validation_timestamp` TIMESTAMP 
- `created_at` TIMESTAMP 

### `shipping_adjustments`

- `adjustment_id` VARCHAR(255) PRIMARY KEY
- `shipment_id` VARCHAR(255) 
- `tracking_number` VARCHAR(255) NOT NULL
- `adjustment_type` VARCHAR(100)  — 'Weight', 'Dimensions', 'Zone', 'Packaging'
- `original_amount` NUMERIC(10, 2) 
- `adjusted_amount` NUMERIC(10, 2) 
- `adjustment_amount` NUMERIC(10, 2) 
- `adjustment_reason` VARCHAR(500) 
- `adjustment_status` VARCHAR(50)  — 'Pending', 'Applied', 'Disputed', 'Resolved'
- `adjustment_date` DATE 
- `created_at` TIMESTAMP 

### `bulk_shipping_presets`

- `preset_id` VARCHAR(255) PRIMARY KEY
- `user_id` VARCHAR(255) 
- `preset_name` VARCHAR(255) NOT NULL
- `package_type` VARCHAR(50) 
- `default_weight_lbs` NUMERIC(10, 4) 
- `default_length_inches` NUMERIC(10, 2) 
- `default_width_inches` NUMERIC(10, 2) 
- `default_height_inches` NUMERIC(10, 2) 
- `default_service_id` VARCHAR(255) 
- `default_carrier_id` VARCHAR(50) 
- `default_insurance_amount` NUMERIC(10, 2) 
- `default_signature_required` BOOLEAN 
- `created_at` TIMESTAMP 
- `updated_at` TIMESTAMP 

### `shipping_analytics`

- `analytics_id` VARCHAR(255) PRIMARY KEY
- `analytics_date` DATE NOT NULL
- `carrier_id` VARCHAR(50) 
- `service_id` VARCHAR(255) 
- `total_shipments` INTEGER 
- `total_revenue` NUMERIC(12, 2) 
- `average_rate` NUMERIC(10, 2) 
- `total_packages` INTEGER 
- `total_weight_lbs` NUMERIC(12, 4) 
- `average_transit_days` NUMERIC(6, 2) 
- `on_time_delivery_rate` NUMERIC(5, 2) 
- `exception_rate` NUMERIC(5, 2) 
- `average_package_value` NUMERIC(10, 2) 
- `created_at` TIMESTAMP 

### `international_customs`

- `customs_id` VARCHAR(255) PRIMARY KEY
- `shipment_id` VARCHAR(255) NOT NULL
- `customs_declaration_number` VARCHAR(255) 
- `customs_value` NUMERIC(10, 2) NOT NULL
- `currency_code` VARCHAR(3) 
- `contents_description` VARCHAR(1000) 
- `hs_tariff_code` VARCHAR(20) 
- `country_of_origin` VARCHAR(2) 
- `customs_duty_amount` NUMERIC(10, 2) 
- `customs_tax_amount` NUMERIC(10, 2) 
- `customs_fees_amount` NUMERIC(10, 2) 
- `total_customs_amount` NUMERIC(10, 2) 
- `customs_status` VARCHAR(50)  — 'Pending', 'Cleared', 'Held', 'Returned'
- `customs_cleared_date` DATE 
- `created_at` TIMESTAMP 

### `api_rate_request_log`

- `log_id` VARCHAR(255) PRIMARY KEY
- `carrier_id` VARCHAR(50) NOT NULL
- `request_type` VARCHAR(50)  — 'Rate', 'Tracking', 'Address Validation'
- `origin_zip_code` VARCHAR(10) 
- `destination_zip_code` VARCHAR(10) 
- `weight_lbs` NUMERIC(10, 4) 
- `request_timestamp` TIMESTAMP 
- `response_time_ms` INTEGER 
- `response_status_code` INTEGER 
- `rate_returned` NUMERIC(10, 2) 
- `error_message` VARCHAR(1000) 
- `api_endpoint` VARCHAR(500) 
- `created_at` TIMESTAMP 

---

*Generated by documentation workflow. MDX-compatible markdown.*
