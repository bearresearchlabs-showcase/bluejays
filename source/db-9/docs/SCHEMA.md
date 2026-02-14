# Database Schema Documentation - db-9 Shipping Intelligence

## Overview

The Shipping Intelligence Database (db-9) provides comprehensive shipping rate comparison, zone analysis, tracking analytics, and cost optimization capabilities. The schema is designed to support multi-carrier shipping intelligence similar to Pirate Ship's functionality.

## Schema Architecture

The database consists of 15 core tables organized into the following categories:

### Core Shipping Tables
- **shipping_carriers**: Carrier information (USPS, UPS, FedEx, etc.)
- **shipping_zones**: Zone information for rate calculations
- **shipping_service_types**: Available service types (Priority Mail, Ground, Express, etc.)
- **shipping_rates**: Historical and current shipping rates
- **packages**: Package information for shipments
- **shipments**: Shipment records with origin and destination

### Analytics and Intelligence Tables
- **tracking_events**: Tracking events for shipments
- **rate_comparison_results**: Rate comparison results across carriers
- **address_validation_results**: Address validation results from USPS Address API
- **shipping_adjustments**: Shipping adjustments and discrepancies
- **shipping_analytics**: Aggregated shipping analytics and metrics
- **international_customs**: Customs information for international shipments
- **api_rate_request_log**: API rate request logs for monitoring

### Configuration Tables
- **bulk_shipping_presets**: Preset configurations for bulk shipping

## Table Descriptions

### shipping_carriers

Stores carrier information including USPS, UPS, FedEx, and other shipping carriers.

**Key Columns:**
- `carrier_id` (VARCHAR(50), PK): Unique carrier identifier
- `carrier_name` (VARCHAR(100)): Carrier display name
- `carrier_code` (VARCHAR(10), UNIQUE): Carrier code (USPS, UPS, FEDEX)
- `carrier_type` (VARCHAR(50)): Carrier type (Postal, Courier, Freight)
- `api_endpoint` (VARCHAR(500)): API endpoint URL
- `commercial_pricing_available` (BOOLEAN): Whether commercial pricing is available
- `active_status` (BOOLEAN): Whether carrier is currently active

### shipping_zones

Stores zone information for rate calculations. Zones determine shipping rates based on origin and destination ZIP codes.

**Key Columns:**
- `zone_id` (VARCHAR(255), PK): Unique zone identifier
- `carrier_id` (VARCHAR(50), FK): Reference to shipping_carriers
- `origin_zip_code` (VARCHAR(10)): Origin ZIP code
- `destination_zip_code` (VARCHAR(10)): Destination ZIP code
- `zone_number` (INTEGER): Zone number (1-8 for domestic)
- `zone_type` (VARCHAR(50)): Zone type (Domestic, International, Alaska, Hawaii)
- `distance_miles` (NUMERIC(10, 2)): Distance in miles
- `transit_days_min` (INTEGER): Minimum transit days
- `transit_days_max` (INTEGER): Maximum transit days

### shipping_service_types

Stores available service types for each carrier (e.g., Priority Mail, Ground, Express).

**Key Columns:**
- `service_id` (VARCHAR(255), PK): Unique service identifier
- `carrier_id` (VARCHAR(50), FK): Reference to shipping_carriers
- `service_code` (VARCHAR(50)): Service code
- `service_name` (VARCHAR(255)): Service display name
- `service_category` (VARCHAR(100)): Service category (Express, Ground, Priority, Economy)
- `max_weight_lbs` (NUMERIC(10, 2)): Maximum weight in pounds
- `tracking_included` (BOOLEAN): Whether tracking is included
- `insurance_available` (BOOLEAN): Whether insurance is available

### shipping_rates

Stores historical and current shipping rates for different carriers, services, zones, and weights.

**Key Columns:**
- `rate_id` (VARCHAR(255), PK): Unique rate identifier
- `carrier_id` (VARCHAR(50), FK): Reference to shipping_carriers
- `service_id` (VARCHAR(255), FK): Reference to shipping_service_types
- `zone_id` (VARCHAR(255), FK): Reference to shipping_zones
- `weight_lbs` (NUMERIC(10, 4)): Package weight in pounds
- `rate_amount` (NUMERIC(10, 2)): Base rate amount
- `total_rate` (NUMERIC(10, 2)): Total rate including surcharges
- `rate_type` (VARCHAR(50)): Rate type (Retail, Commercial, Daily, Cubic)
- `effective_date` (DATE): When rate becomes effective
- `expiration_date` (DATE): When rate expires

### packages

Stores package information including dimensions, weight, and package type.

**Key Columns:**
- `package_id` (VARCHAR(255), PK): Unique package identifier
- `weight_lbs` (NUMERIC(10, 4)): Package weight in pounds
- `length_inches` (NUMERIC(10, 2)): Package length in inches
- `width_inches` (NUMERIC(10, 2)): Package width in inches
- `height_inches` (NUMERIC(10, 2)): Package height in inches
- `dimensional_weight_lbs` (NUMERIC(10, 4)): Calculated dimensional weight
- `package_type` (VARCHAR(50)): Package type (Envelope, Box, Tube, Flat)
- `package_value` (NUMERIC(10, 2)): Declared package value

### shipments

Stores shipment records with origin and destination addresses, carrier selection, and shipment status.

**Key Columns:**
- `shipment_id` (VARCHAR(255), PK): Unique shipment identifier
- `package_id` (VARCHAR(255), FK): Reference to packages
- `carrier_id` (VARCHAR(50), FK): Reference to shipping_carriers
- `service_id` (VARCHAR(255), FK): Reference to shipping_service_types
- `tracking_number` (VARCHAR(255)): Carrier tracking number
- `origin_zip_code` (VARCHAR(10)): Origin ZIP code
- `destination_zip_code` (VARCHAR(10)): Destination ZIP code
- `total_cost` (NUMERIC(10, 2)): Total shipment cost
- `shipment_status` (VARCHAR(50)): Shipment status (Pending, Label Created, In Transit, Delivered, Exception)
- `estimated_delivery_date` (DATE): Estimated delivery date
- `actual_delivery_date` (DATE): Actual delivery date

### tracking_events

Stores tracking events for shipments, providing visibility into package movement.

**Key Columns:**
- `event_id` (VARCHAR(255), PK): Unique event identifier
- `shipment_id` (VARCHAR(255), FK): Reference to shipments
- `tracking_number` (VARCHAR(255)): Tracking number
- `event_timestamp` (TIMESTAMP_NTZ): Event timestamp
- `event_type` (VARCHAR(100)): Event type (Label Created, In Transit, Out for Delivery, Delivered, Exception)
- `event_location` (VARCHAR(255)): Event location
- `event_description` (VARCHAR(1000)): Event description
- `raw_event_data` (VARIANT): Raw JSON data from carrier API

## Relationships

### Primary Relationships
- `shipping_zones.carrier_id` → `shipping_carriers.carrier_id`
- `shipping_service_types.carrier_id` → `shipping_carriers.carrier_id`
- `shipping_rates.carrier_id` → `shipping_carriers.carrier_id`
- `shipping_rates.service_id` → `shipping_service_types.service_id`
- `shipping_rates.zone_id` → `shipping_zones.zone_id`
- `shipments.package_id` → `packages.package_id`
- `shipments.carrier_id` → `shipping_carriers.carrier_id`
- `shipments.service_id` → `shipping_service_types.service_id`
- `shipments.zone_id` → `shipping_zones.zone_id`
- `tracking_events.shipment_id` → `shipments.shipment_id`

## Indexes

The schema includes indexes for performance optimization:

- `idx_shipping_zones_carrier_origin_dest`: Index on carrier_id, origin_zip_code, destination_zip_code
- `idx_shipping_rates_carrier_service`: Index on carrier_id, service_id
- `idx_shipping_rates_weight`: Index on weight_lbs
- `idx_shipments_tracking_number`: Index on tracking_number
- `idx_shipments_status`: Index on shipment_status
- `idx_tracking_events_shipment`: Index on shipment_id
- `idx_tracking_events_timestamp`: Index on event_timestamp
- `idx_rate_comparison_package`: Index on package_id
- `idx_address_validation_zip`: Index on validated_zip_code
- `idx_api_rate_request_log_carrier`: Index on carrier_id, request_timestamp

## Data Types

The schema uses standard SQL data types compatible with PostgreSQL:

- **VARCHAR**: Variable-length strings
- **NUMERIC**: Decimal numbers with precision
- **INTEGER**: Whole numbers
- **BOOLEAN**: True/false values
- **DATE**: Date values
- **TIMESTAMP_NTZ**: Timestamp without timezone
- **VARIANT**: JSON/variant data (Snowflake/Databricks)

## Compatibility

The schema is designed to work across:
- **PostgreSQL**: Full support with standard SQL
- **Databricks**: Delta Lake compatible
- **Snowflake**: Full support with VARIANT for JSON data

## Usage Notes

1. **Rate Lookups**: Use `shipping_rates` table with joins to `shipping_zones` for zone-based rate calculations
2. **Tracking**: Query `tracking_events` filtered by `shipment_id` or `tracking_number` for package tracking
3. **Address Validation**: Use `address_validation_results` for address validation and standardization
4. **Analytics**: Query `shipping_analytics` for aggregated metrics and `rate_comparison_results` for rate comparisons

---
**Last Updated:** 2026-02-04
