# Insurance Rate Modeling Documentation - db-6

**Created:** 2026-02-03
**Purpose:** Insurance rate table determination using 7-14 day weather forecasts

## Overview

The insurance rate modeling extension enables insurance companies to calculate dynamic insurance rates based on forecasted weather risks. The system analyzes 7-14 day forecasts from December 3-17, 2025 to determine risk factors and generate rate tables.

## Key Features

1. **Risk Factor Calculation:** Analyzes multiple weather parameters (temperature, precipitation, wind, freeze, flood) to calculate comprehensive risk scores
2. **Rate Table Generation:** Generates insurance rate tables with risk-adjusted pricing based on forecast risk factors
3. **Multi-Day Forecast Comparison:** Compares rates across 7-14 day forecasts to select optimal forecast day
4. **Historical Validation:** Validates forecast-based rates against historical claims data
5. **Volatility Analysis:** Analyzes rate stability and volatility for consistent pricing
6. **Risk Ranking:** Ranks policy areas by risk level for portfolio management

## Database Schema

### Insurance Tables

#### insurance_policy_areas
Maps geographic boundaries to insurance policy coverage areas.

**Key Columns:**
- `policy_area_id` (VARCHAR, PK)
- `boundary_id` (VARCHAR) - References shapefile_boundaries
- `policy_type` (VARCHAR) - 'Property', 'Crop', 'Auto', 'Marine', 'General Liability'
- `coverage_type` (VARCHAR) - 'Homeowners', 'Commercial Property', 'Crop Insurance', etc.
- `risk_zone` (VARCHAR) - 'Low', 'Moderate', 'High', 'Very High'
- `base_rate_factor` (NUMERIC) - Multiplier for base rates

#### insurance_risk_factors
Stores calculated risk factors based on weather forecasts.

**Key Columns:**
- `risk_factor_id` (VARCHAR, PK)
- `policy_area_id` (VARCHAR) - References insurance_policy_areas
- `forecast_period_start` (DATE) - Dec 3, 2025
- `forecast_period_end` (DATE) - Dec 17, 2025
- `forecast_day` (INTEGER) - Days ahead: 7, 8, 9, ..., 14
- `forecast_date` (DATE) - Date when forecast was made
- `overall_risk_score` (NUMERIC) - Overall risk score (0-100)
- `risk_category` (VARCHAR) - 'Low', 'Moderate', 'High', 'Very High', 'Extreme'
- `cumulative_precipitation_risk` (NUMERIC)
- `temperature_extreme_risk` (NUMERIC)
- `wind_damage_risk` (NUMERIC)
- `freeze_risk` (NUMERIC)
- `flood_risk` (NUMERIC)
- `extreme_event_probability` (NUMERIC)

#### insurance_rate_tables
Stores calculated rate tables based on forecast risk factors.

**Key Columns:**
- `rate_table_id` (VARCHAR, PK)
- `policy_area_id` (VARCHAR) - References insurance_policy_areas
- `forecast_period_start` (DATE) - Dec 3, 2025
- `forecast_period_end` (DATE) - Dec 17, 2025
- `forecast_day` (INTEGER) - 7-14 days ahead
- `base_rate` (NUMERIC) - Base insurance rate
- `risk_adjusted_rate` (NUMERIC) - Risk-adjusted rate
- `risk_multiplier` (NUMERIC) - Multiplier applied to base rate
- `rate_tier` (VARCHAR) - 'Standard', 'Preferred', 'Substandard', 'High Risk'
- `confidence_level` (NUMERIC) - Confidence in forecast (0-100)

#### insurance_claims_history
Historical claims data for validation and comparison.

**Key Columns:**
- `claim_id` (VARCHAR, PK)
- `policy_area_id` (VARCHAR) - References insurance_policy_areas
- `loss_date` (DATE) - Date when loss occurred
- `loss_amount` (NUMERIC) - Claim amount
- `weather_event_type` (VARCHAR) - 'Hurricane', 'Tornado', 'Flood', 'Freeze', etc.
- `forecast_available` (BOOLEAN) - Whether forecast was available
- `forecast_error` (NUMERIC) - Forecast vs actual error

#### forecast_rate_mapping
Maps specific forecasts to rate calculations.

**Key Columns:**
- `mapping_id` (VARCHAR, PK)
- `forecast_id` (VARCHAR) - References grib2_forecasts
- `rate_table_id` (VARCHAR) - References insurance_rate_tables
- `risk_factor_id` (VARCHAR) - References insurance_risk_factors
- `risk_contribution` (NUMERIC) - Contribution to overall risk score
- `rate_impact` (NUMERIC) - Impact on rate calculation

#### rate_table_comparison
Compares rates across different forecast days (7-14 days).

**Key Columns:**
- `comparison_id` (VARCHAR, PK)
- `policy_area_id` (VARCHAR)
- `forecast_period_start` (DATE) - Dec 3, 2025
- `forecast_period_end` (DATE) - Dec 17, 2025
- `rate_day_7` through `rate_day_14` (NUMERIC) - Rates for each forecast day
- `recommended_rate` (NUMERIC) - Recommended rate
- `recommended_forecast_day` (INTEGER) - Which forecast day to use
- `confidence_score` (NUMERIC)

## Insurance Queries (31-40)

### Query 31: Insurance Risk Factor Calculation
Calculates comprehensive risk factors for insurance policy areas based on 7-14 day forecasts. Analyzes multiple weather parameters to determine extreme event probabilities, precipitation risk, temperature extremes, wind damage risk, freeze risk, and flood risk.

**Output:** Risk factor analysis report showing forecast-based risk scores for each policy area and forecast day.

### Query 32: Insurance Rate Table Generation
Generates insurance rate tables using risk factors calculated from 7-14 day forecasts. Calculates base rates, risk-adjusted rates, rate components, and rate tiers.

**Output:** Complete rate table showing rates for each policy area, forecast day, and coverage type.

### Query 33: Rate Table Comparison
Compares insurance rates across all forecast days (7-14 days ahead). Calculates rate statistics, volatility, trends, and recommends optimal forecast day.

**Output:** Rate comparison report showing rates by forecast day with volatility metrics.

### Query 34: Historical Claims Validation
Validates forecast-based risk factors against historical claims data. Compares forecast risk scores with actual claims to assess forecast accuracy.

**Output:** Validation report showing forecast risk vs actual claims with accuracy metrics.

### Query 35: Rate Volatility and Stability Analysis
Analyzes rate volatility and stability across 7-14 day forecasts. Identifies areas with high rate volatility and recommends stable pricing strategies.

**Output:** Rate volatility analysis with stability metrics and recommendations.

### Query 36: Policy Area Risk Ranking
Ranks policy areas by forecast-based risk scores. Provides comparative risk analysis across geographic areas.

**Output:** Risk ranking report showing policy areas ordered by risk level.

### Query 37: Forecast-to-Rate Impact Analysis
Analyzes how individual forecast parameters impact insurance rates. Quantifies the contribution of each weather parameter to final rate calculations.

**Output:** Parameter impact analysis showing which forecast parameters drive rate changes.

### Query 38: Multi-Day Forecast Ensemble Rate Analysis
Analyzes rates across multiple forecast days as an ensemble. Uses ensemble statistics to reduce forecast uncertainty and provide more stable pricing.

**Output:** Ensemble rate analysis with consensus rates and confidence intervals.

### Query 39: Forecast Day Selection Optimization
Determines optimal forecast day (7-14 days) for rate determination based on accuracy, confidence, and business requirements.

**Output:** Forecast day optimization report with recommended forecast days.

### Query 40: Comprehensive Insurance Rate Modeling Summary
Provides comprehensive summary of insurance rate modeling. Aggregates risk factors, rates, comparisons, validations, and recommendations into a single dashboard view.

**Output:** Comprehensive rate modeling summary dashboard with all key metrics.

## Usage Examples

### Calculate Risk Factors for Policy Area

```sql
-- Use Query 31 to calculate risk factors
SELECT * FROM insurance_risk_factors
WHERE policy_area_id = 'POLICY_AREA_001'
  AND forecast_period_start = DATE '2025-12-03'
  AND forecast_period_end = DATE '2025-12-17'
  AND forecast_day BETWEEN 7 AND 14;
```

### Generate Rate Tables

```sql
-- Use Query 32 to generate rate tables
SELECT * FROM insurance_rate_tables
WHERE policy_area_id = 'POLICY_AREA_001'
  AND forecast_period_start = DATE '2025-12-03'
  AND forecast_period_end = DATE '2025-12-17'
  AND forecast_day BETWEEN 7 AND 14;
```

### Compare Rates Across Forecast Days

```sql
-- Use Query 33 to compare rates
SELECT * FROM rate_table_comparison
WHERE policy_area_id = 'POLICY_AREA_001'
  AND forecast_period_start = DATE '2025-12-03'
  AND forecast_period_end = DATE '2025-12-17';
```

## Risk Scoring Methodology

### Overall Risk Score Calculation

The overall risk score is calculated as a weighted combination of individual risk components:

```
Overall Risk Score =
  (Precipitation Risk × 30%) +
  (Temperature Extreme Risk × 25%) +
  (Wind Damage Risk × 20%) +
  (Flood Risk × 15%) +
  (Extreme Event Probability × 10%)
```

### Risk Categories

- **Extreme:** Overall Risk Score ≥ 75
- **Very High:** Overall Risk Score ≥ 50
- **High:** Overall Risk Score ≥ 30
- **Moderate:** Overall Risk Score ≥ 15
- **Low:** Overall Risk Score < 15

### Rate Multipliers

- **Extreme Risk:** 2.5× base rate
- **Very High Risk:** 2.0× base rate
- **High Risk:** 1.5× base rate
- **Moderate Risk:** 1.25× base rate
- **Low Risk:** 1.0× base rate (no adjustment)

## Forecast Period

All insurance queries are designed for:
- **Forecast Period:** December 3-17, 2025
- **Forecast Days:** 7-14 days ahead
- **Forecast Dates:** December 3-17, 2025

## Compatibility

All insurance queries are designed to work across:
- PostgreSQL (with PostGIS)
 (Delta Lake)


## Data Requirements

To use the insurance rate modeling queries, ensure:

1. **Weather Forecasts:** GRIB2 forecasts loaded for December 3-17, 2025 period
2. **Policy Areas:** Insurance policy areas mapped to geographic boundaries
3. **Historical Claims:** Claims history data for validation (optional but recommended)
4. **Risk Factors:** Risk factors calculated using Query 31 before generating rate tables

## Best Practices

1. **Calculate Risk Factors First:** Run Query 31 to calculate risk factors before generating rate tables
2. **Compare Across Forecast Days:** Use Query 33 to compare rates across 7-14 day forecasts
3. **Validate with Historical Data:** Use Query 34 to validate forecast accuracy against historical claims
4. **Monitor Volatility:** Use Query 35 to identify areas with high rate volatility
5. **Use Ensemble Analysis:** Use Query 38 for more robust rate determination
6. **Optimize Forecast Day:** Use Query 39 to select optimal forecast day for each policy area

---

**Last Updated:** 2026-02-03
