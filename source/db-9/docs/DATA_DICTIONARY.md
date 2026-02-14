# Data Dictionary - db-9 Shipping Intelligence Database

## Overview

This data dictionary provides detailed descriptions of all tables and columns in the Shipping Intelligence Database (db-9).

## Tables

### shipping_carriers

Stores carrier information including USPS, UPS, FedEx, and other shipping carriers.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| carrier_id | VARCHAR(50) | NO | Primary key. Unique carrier identifier |
| carrier_name | VARCHAR(100) | NO | Carrier display name (e.g., "United States Postal Service") |
| carrier_code | VARCHAR(10) | NO | Unique carrier code (USPS, UPS, FEDEX) |
| carrier_type | VARCHAR(50) | YES | Carrier type: Postal, Courier, or Freight |
| api_endpoint | VARCHAR(500) | YES | API endpoint URL for carrier API |
| rate_api_version | VARCHAR(50) | YES | Rate API version number |
| tracking_api_version | VARCHAR(50) | YES | Tracking API version number |
| commercial_pricing_available | BOOLEAN | YES | Whether commercial pricing is available |
| requires_account | BOOLEAN | YES | Whether carrier requires account setup |
| active_status | BOOLEAN | YES | Whether carrier is currently active |
| created_at | TIMESTAMP_NTZ | YES | Record creation timestamp |
| updated_at | TIMESTAMP_NTZ | YES | Record last update timestamp |

### shipping_zones

Stores zone information for rate calculations. Zones determine shipping rates based on origin and destination ZIP codes.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| zone_id | VARCHAR(255) | NO | Primary key. Unique zone identifier |
| carrier_id | VARCHAR(50) | NO | Foreign key to shipping_carriers |
| origin_zip_code | VARCHAR(10) | NO | Origin ZIP code (5-digit or ZIP+4) |
| destination_zip_code | VARCHAR(10) | NO | Destination ZIP code (5-digit or ZIP+4) |
| zone_number | INTEGER | NO | Zone number (typically 1-8 for domestic USPS) |
| zone_type | VARCHAR(50) | YES | Zone type: Domestic, International, Alaska, Hawaii |
| distance_miles | NUMERIC(10, 2) | YES | Distance between origin and destination in miles |
| transit_days_min | INTEGER | YES | Minimum transit days for this zone |
| transit_days_max | INTEGER | YES | Maximum transit days for this zone |
| effective_date | DATE | NO | When zone mapping becomes effective |
| expiration_date | DATE | YES | When zone mapping expires (NULL if current) |
| created_at | TIMESTAMP_NTZ | YES | Record creation timestamp |

### shipping_service_types

Stores available service types for each carrier (e.g., Priority Mail, Ground, Express).

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| service_id | VARCHAR(255) | NO | Primary key. Unique service identifier |
| carrier_id | VARCHAR(50) | NO | Foreign key to shipping_carriers |
| service_code | VARCHAR(50) | NO | Service code (e.g., "PRIORITY", "GROUND") |
| service_name | VARCHAR(255) | NO | Service display name |
| service_category | VARCHAR(100) | YES | Service category: Express, Ground, Priority, Economy |
| domestic_available | BOOLEAN | YES | Whether service is available for domestic shipments |
| international_available | BOOLEAN | YES | Whether service is available for international shipments |
| max_weight_lbs | NUMERIC(10, 2) | YES | Maximum weight in pounds for this service |
| max_dimensions_length | NUMERIC(10, 2) | YES | Maximum length in inches |
| max_dimensions_width | NUMERIC(10, 2) | YES | Maximum width in inches |
| max_dimensions_height | NUMERIC(10, 2) | YES | Maximum height in inches |
| tracking_included | BOOLEAN | YES | Whether tracking is included |
| insurance_available | BOOLEAN | YES | Whether insurance is available |
| signature_required | BOOLEAN | YES | Whether signature is required |
| active_status | BOOLEAN | YES | Whether service is currently active |
| created_at | TIMESTAMP_NTZ | YES | Record creation timestamp |

### shipping_rates

Stores historical and current shipping rates for different carriers, services, zones, and weights.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| rate_id | VARCHAR(255) | NO | Primary key. Unique rate identifier |
| carrier_id | VARCHAR(50) | NO | Foreign key to shipping_carriers |
| service_id | VARCHAR(255) | NO | Foreign key to shipping_service_types |
| zone_id | VARCHAR(255) | YES | Foreign key to shipping_zones |
| weight_lbs | NUMERIC(10, 4) | NO | Package weight in pounds |
| weight_oz | NUMERIC(10, 4) | YES | Package weight in ounces |
| length_inches | NUMERIC(10, 2) | YES | Package length in inches |
| width_inches | NUMERIC(10, 2) | YES | Package width in inches |
| height_inches | NUMERIC(10, 2) | YES | Package height in inches |
| dimensional_weight_lbs | NUMERIC(10, 4) | YES | Calculated dimensional weight |
| cubic_volume_cubic_inches | NUMERIC(12, 4) | YES | Cubic volume in cubic inches |
| rate_amount | NUMERIC(10, 2) | NO | Base rate amount |
| rate_type | VARCHAR(50) | YES | Rate type: Retail, Commercial, Daily, Cubic |
| surcharge_amount | NUMERIC(10, 2) | YES | Additional surcharge amount |
| total_rate | NUMERIC(10, 2) | NO | Total rate including surcharges |
| effective_date | DATE | NO | When rate becomes effective |
| expiration_date | DATE | YES | When rate expires (NULL if current) |
| rate_source | VARCHAR(100) | YES | Rate source: API, Manual, Bulk Import |
| created_at | TIMESTAMP_NTZ | YES | Record creation timestamp |

### packages

Stores package information including dimensions, weight, and package type.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| package_id | VARCHAR(255) | NO | Primary key. Unique package identifier |
| user_id | VARCHAR(255) | YES | User identifier (if applicable) |
| package_reference | VARCHAR(255) | YES | User-provided package reference |
| weight_lbs | NUMERIC(10, 4) | NO | Package weight in pounds |
| weight_oz | NUMERIC(10, 4) | YES | Package weight in ounces |
| length_inches | NUMERIC(10, 2) | NO | Package length in inches |
| width_inches | NUMERIC(10, 2) | NO | Package width in inches |
| height_inches | NUMERIC(10, 2) | NO | Package height in inches |
| dimensional_weight_lbs | NUMERIC(10, 4) | YES | Calculated dimensional weight |
| cubic_volume_cubic_inches | NUMERIC(12, 4) | YES | Cubic volume in cubic inches |
| package_type | VARCHAR(50) | YES | Package type: Envelope, Box, Tube, Flat |
| package_value | NUMERIC(10, 2) | YES | Declared package value |
| contents_description | VARCHAR(500) | YES | Description of package contents |
| created_at | TIMESTAMP_NTZ | YES | Record creation timestamp |
| updated_at | TIMESTAMP_NTZ | YES | Record last update timestamp |

### shipments

Stores shipment records with origin and destination addresses, carrier selection, and shipment status.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| shipment_id | VARCHAR(255) | NO | Primary key. Unique shipment identifier |
| package_id | VARCHAR(255) | NO | Foreign key to packages |
| carrier_id | VARCHAR(50) | NO | Foreign key to shipping_carriers |
| service_id | VARCHAR(255) | NO | Foreign key to shipping_service_types |
| tracking_number | VARCHAR(255) | YES | Carrier tracking number |
| origin_name | VARCHAR(255) | YES | Origin name/company |
| origin_address_line1 | VARCHAR(255) | YES | Origin address line 1 |
| origin_address_line2 | VARCHAR(255) | YES | Origin address line 2 |
| origin_city | VARCHAR(100) | YES | Origin city |
| origin_state | VARCHAR(2) | YES | Origin state code |
| origin_zip_code | VARCHAR(10) | NO | Origin ZIP code |
| origin_country | VARCHAR(2) | YES | Origin country code (default: US) |
| destination_name | VARCHAR(255) | YES | Destination name/company |
| destination_address_line1 | VARCHAR(255) | YES | Destination address line 1 |
| destination_address_line2 | VARCHAR(255) | YES | Destination address line 2 |
| destination_city | VARCHAR(100) | YES | Destination city |
| destination_state | VARCHAR(2) | YES | Destination state code |
| destination_zip_code | VARCHAR(10) | NO | Destination ZIP code |
| destination_country | VARCHAR(2) | YES | Destination country code (default: US) |
| zone_id | VARCHAR(255) | YES | Foreign key to shipping_zones |
| rate_id | VARCHAR(255) | YES | Foreign key to shipping_rates |
| label_cost | NUMERIC(10, 2) | YES | Label/shipping cost |
| insurance_cost | NUMERIC(10, 2) | YES | Insurance cost |
| signature_cost | NUMERIC(10, 2) | YES | Signature confirmation cost |
| total_cost | NUMERIC(10, 2) | NO | Total shipment cost |
| shipment_status | VARCHAR(50) | YES | Status: Pending, Label Created, In Transit, Delivered, Exception |
| label_created_at | TIMESTAMP_NTZ | YES | When label was created |
| estimated_delivery_date | DATE | YES | Estimated delivery date |
| actual_delivery_date | DATE | YES | Actual delivery date |
| created_at | TIMESTAMP_NTZ | YES | Record creation timestamp |
| updated_at | TIMESTAMP_NTZ | YES | Record last update timestamp |

### tracking_events

Stores tracking events for shipments, providing visibility into package movement.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| event_id | VARCHAR(255) | NO | Primary key. Unique event identifier |
| shipment_id | VARCHAR(255) | NO | Foreign key to shipments |
| tracking_number | VARCHAR(255) | NO | Tracking number |
| event_timestamp | TIMESTAMP_NTZ | NO | Event timestamp |
| event_type | VARCHAR(100) | YES | Event type: Label Created, In Transit, Out for Delivery, Delivered, Exception |
| event_status | VARCHAR(100) | YES | Event status code |
| event_location | VARCHAR(255) | YES | Event location |
| event_city | VARCHAR(100) | YES | Event city |
| event_state | VARCHAR(2) | YES | Event state code |
| event_zip_code | VARCHAR(10) | YES | Event ZIP code |
| event_country | VARCHAR(2) | YES | Event country code |
| event_description | VARCHAR(1000) | YES | Event description |
| carrier_status_code | VARCHAR(50) | YES | Carrier-specific status code |
| raw_event_data | VARIANT | YES | Raw JSON data from carrier API |
| created_at | TIMESTAMP_NTZ | YES | Record creation timestamp |

## Additional Tables

### rate_comparison_results
Stores rate comparison results across multiple carriers for package shipping scenarios.

### address_validation_results
Stores address validation results from USPS Address API including validated addresses and validation status.

### shipping_adjustments
Stores shipping adjustments and discrepancies identified by carrier APIs (weight, dimensions, zone corrections).

### shipping_analytics
Stores aggregated shipping analytics and metrics for reporting and analysis.

### international_customs
Stores customs information for international shipments including duty amounts and customs status.

### api_rate_request_log
Stores API rate request logs for monitoring API performance and usage.

### bulk_shipping_presets
Stores preset configurations for bulk shipping operations.

---
**Last Updated:** 2026-02-04
