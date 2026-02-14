# M&A Workflow SQL Queries - db-16

## Overview

Database 16 contains **30 extremely complex SQL queries** specifically designed for **M&A (Mergers & Acquisitions) due diligence workflows** for large real estate firms. All queries support flood risk assessment for acquisition target evaluation and deal decision-making.

## Query Categories

### 1. Pre-Acquisition Assessment (Queries 1-3)

#### Query 1: Pre-Acquisition Multi-Factor Flood Risk Assessment
**Use Case:** M&A Due Diligence - Pre-Acquisition Property-Level Flood Risk Assessment for Acquisition Target Evaluation

**Purpose:** Comprehensive flood risk assessment combining FEMA flood zones, NOAA sea level rise projections, USGS streamflow data, and NASA flood models. Provides multi-factor risk scoring and financial impact estimation.

**Key Features:**
- Spatial joins (ST_WITHIN, ST_DISTANCE, ST_INTERSECTS)
- Temporal projections (5-10, 20-30, 50-100 years)
- Multi-factor risk scoring (FEMA 40%, Sea Level Rise 25%, Streamflow 20%, NASA 15%)
- Financial impact modeling (estimated damage, annual loss)

#### Query 2: Acquisition Target Portfolio Risk Analysis
**Use Case:** M&A Due Diligence - Acquisition Target Portfolio-Wide Flood Risk Analysis with Geographic Risk Clustering

**Purpose:** Portfolio-level risk aggregation with geographic clustering, spatial hotspot detection, and risk concentration analysis.

**Key Features:**
- Geographic clustering algorithms
- Risk hotspot detection
- Portfolio diversification metrics
- Risk concentration by region

#### Query 3: Historical Flood Event Due Diligence Analysis
**Use Case:** M&A Due Diligence - Historical Flood Event Analysis for Acquisition Target Risk Assessment

**Purpose:** Historical flood frequency patterns, temporal clustering, severity trends, and recurrence interval analysis.

**Key Features:**
- Temporal pattern analysis
- Frequency calculations
- Recurrence interval analysis
- Geographic recurrence hotspots

### 2. Coastal & Sea Level Rise Analysis (Queries 4, 14)

#### Query 4: Sea Level Rise Impact Projections
**Use Case:** M&A Due Diligence - Coastal Acquisition Target Risk Assessment - Multi-Horizon Sea Level Rise Impact Analysis

**Purpose:** Sea level rise projections across 5, 10, 20, 30, 50, and 100-year horizons comparing multiple scenarios (Low, Intermediate-Low, Intermediate, Intermediate-High, High, Extreme).

**Key Features:**
- Multi-horizon temporal projections
- Scenario comparison
- Property vulnerability assessments
- Long-term risk assessment

#### Query 14: NOAA Sea Level Rise Scenario Comparison
**Use Case:** M&A Due Diligence - Sea Level Rise Analysis - NOAA Sea Level Rise Scenario Comparison for Coastal Acquisition Targets

**Purpose:** Compare different NOAA sea level rise scenarios for coastal properties.

### 3. Streamflow & Riverine Risk (Queries 5, 15)

#### Query 5: Streamflow Flood Frequency Analysis
**Use Case:** M&A Due Diligence - Streamflow Risk Analysis - Streamflow Flood Frequency Analysis for Acquisition Target Risk Assessment

**Purpose:** Riverine flood risk analysis using USGS streamflow gauge data and historical patterns.

**Key Features:**
- Gauge network coverage analysis
- Historical pattern recognition
- Flood frequency calculations
- Recurrence probability assessment

#### Query 15: USGS Streamflow Historical Pattern Recognition
**Use Case:** M&A Due Diligence - Historical Pattern Analysis - USGS Streamflow Historical Pattern Recognition

**Purpose:** Historical streamflow pattern analysis for acquisition targets.

### 4. Model Validation & Performance (Queries 6, 16, 23)

#### Query 6: NASA Flood Model Performance Evaluation
**Use Case:** M&A Due Diligence - Model Validation - NASA Flood Model Performance Evaluation

**Purpose:** Evaluate NASA flood model accuracy and performance metrics.

**Key Features:**
- Model accuracy assessment
- Performance metrics
- Prediction reliability evaluation

#### Query 16: NASA Model Prediction Accuracy Assessment
**Use Case:** M&A Due Diligence - Model Accuracy Assessment - NASA Model Prediction Accuracy Assessment

**Purpose:** Assess NASA model prediction accuracy for acquisition targets.

#### Query 23: Model Performance Comparison
**Use Case:** M&A Due Diligence - Model Comparison - Model Performance Comparison

**Purpose:** Compare performance across different flood models.

### 5. Spatial Analysis (Queries 7, 10, 17, 20)

#### Query 7: Property-Flood Zone Intersection Analysis
**Use Case:** M&A Due Diligence - Spatial Risk Analysis - Property-Flood Zone Intersection Analysis

**Purpose:** Spatial relationships between properties and flood zones.

**Key Features:**
- Spatial intersection analysis
- Flood zone proximity
- Spatial risk exposure

#### Query 10: Geographic Risk Clustering
**Use Case:** M&A Due Diligence - Geographic Risk Analysis - Geographic Risk Clustering

**Purpose:** Geographic clustering of risk for portfolio evaluation.

#### Query 17: Spatial Join Optimization
**Use Case:** M&A Due Diligence - Spatial Analysis Optimization - Spatial Join Optimization

**Purpose:** Optimize spatial joins for risk assessment.

#### Query 20: Geographic Risk Distribution Analysis
**Use Case:** M&A Due Diligence - Geographic Distribution Analysis - Geographic Risk Distribution Analysis

**Purpose:** Analyze geographic distribution of risk across portfolios.

### 6. Risk Scoring & Assessment (Queries 8, 9, 11, 12, 18, 19, 21, 24, 25)

#### Query 8: Risk Trend Analysis Over Time
**Use Case:** M&A Due Diligence - Risk Trend Analysis - Risk Trend Analysis Over Time

**Purpose:** Analyze risk trends over time for acquisition targets.

#### Query 9: Property Vulnerability Scoring
**Use Case:** M&A Due Diligence - Vulnerability Assessment - Property Vulnerability Scoring

**Purpose:** Calculate vulnerability scores for acquisition targets.

#### Query 11: Financial Impact Modeling
**Use Case:** M&A Due Diligence - Financial Risk Analysis - Flood Risk Financial Impact Modeling for Acquisition Pricing

**Purpose:** Model financial impact of flood risk on acquisition pricing and deal structuring.

**Key Features:**
- Damage cost estimation
- Annual loss calculations
- Acquisition pricing impact
- Deal structuring recommendations

#### Query 12: FEMA Flood Zone Risk Classification
**Use Case:** M&A Due Diligence - FEMA Zone Analysis - FEMA Flood Zone Risk Classification

**Purpose:** Classify FEMA flood zone risks for acquisition targets.

#### Query 18: Multi-Source Risk Score Fusion
**Use Case:** M&A Due Diligence - Risk Score Fusion - Multi-Source Risk Score Fusion

**Purpose:** Combine risk scores from multiple data sources.

#### Query 19: Temporal Risk Projection Analysis
**Use Case:** M&A Due Diligence - Temporal Risk Analysis - Temporal Risk Projection Analysis

**Purpose:** Project risk over multiple time horizons.

#### Query 21: Property Elevation vs Flood Risk Correlation
**Use Case:** M&A Due Diligence - Elevation Risk Analysis - Property Elevation vs Flood Risk Correlation

**Purpose:** Analyze correlation between property elevation and flood risk.

#### Query 24: Property Type Risk Analysis
**Use Case:** M&A Due Diligence - Property Type Analysis - Property Type Risk Analysis

**Purpose:** Analyze risk by property type (Residential, Commercial, Industrial, Mixed-Use).

#### Query 25: Recursive Flood Risk Propagation
**Use Case:** M&A Due Diligence - Recursive Risk Analysis - Recursive Flood Risk Propagation

**Purpose:** Recursive analysis of flood risk propagation.

### 7. Portfolio Analysis (Queries 13, 22, 27)

#### Query 13: Acquisition Target Portfolio Risk Summary
**Use Case:** M&A Due Diligence - Acquisition Target Portfolio Analysis - Portfolio Risk Summary Generation

**Purpose:** Generate comprehensive portfolio risk summaries for M&A deal evaluation.

#### Query 22: Acquisition Target Portfolio Diversification Risk Analysis
**Use Case:** M&A Due Diligence - Diversification Analysis - Portfolio Diversification Risk Analysis

**Purpose:** Analyze portfolio diversification and risk concentration.

#### Query 27: High-Risk Property Identification
**Use Case:** M&A Due Diligence - Risk Identification - High-Risk Property Identification for Deal-Breaker Analysis

**Purpose:** Identify high-risk properties that could be deal-breakers.

**Key Features:**
- Deal-breaker identification
- Risk threshold analysis
- Property screening

### 8. Historical Analysis (Queries 22, 26)

#### Query 22: Historical Flood Event Impact Assessment
**Use Case:** M&A Due Diligence - Historical Impact Assessment - Historical Flood Event Impact Assessment

**Purpose:** Assess historical flood event impacts on acquisition targets.

#### Query 26: Historical Flood Event Impact Assessment
**Use Case:** M&A Due Diligence - Historical Impact Assessment - Historical Flood Event Impact Assessment

**Purpose:** Analyze historical flood impacts.

### 9. Data Quality & Operations (Query 16)

#### Query 16: Data Quality Metrics Analysis
**Use Case:** M&A Due Diligence - Data Quality Assessment - Data Quality Metrics Analysis

**Purpose:** Assess data quality for risk assessment reliability.

### 10. Post-Acquisition (Query 28)

#### Query 28: Post-Acquisition Risk Mitigation Cost-Benefit Analysis
**Use Case:** M&A Post-Acquisition - Risk Mitigation Planning - Post-Acquisition Flood Risk Mitigation Cost-Benefit Analysis

**Purpose:** Analyze cost-benefit of risk mitigation strategies for acquired properties.

**Key Features:**
- Mitigation cost analysis
- Benefit calculations
- ROI projections
- Strategy recommendations

### 11. Comprehensive Reporting (Query 30)

#### Query 30: M&A Due Diligence Comprehensive Flood Risk Assessment Report
**Use Case:** M&A Due Diligence - Comprehensive Due Diligence Report - Comprehensive Flood Risk Assessment Report

**Purpose:** Generate comprehensive due diligence reports for M&A transaction decision-making.

**Key Features:**
- Complete risk assessment
- Multi-factor analysis
- Financial impact summary
- Decision recommendations

## Query Complexity

All queries feature:
- **Deep nested CTEs** (8-9+ levels)
- **Spatial operations** (PostGIS GEOGRAPHY functions)
- **Complex aggregations** with window functions
- **Temporal analysis** (multi-horizon projections)
- **Multi-source data fusion** (FEMA, NOAA, USGS, NASA)
- **Financial modeling** (damage estimates, annual loss)
- **Risk scoring algorithms** (0-100 scale)
- **Cross-database compatibility** (PostgreSQL)

## Database Schema

### Core Tables
- `real_estate_properties` - Property locations and characteristics
- `fema_flood_zones` - FEMA flood zone designations
- `noaa_sea_level_rise` - Sea level rise projections
- `usgs_streamflow_gauges` - Streamflow gauge locations
- `usgs_streamflow_observations` - Streamflow measurements
- `nasa_flood_models` - NASA flood model predictions
- `flood_risk_assessments` - Comprehensive risk assessments
- `historical_flood_events` - Historical flood records
- `portfolio_risk_summaries` - Portfolio-level aggregations

## Usage

All queries are designed for:
- **Pre-acquisition due diligence** - Evaluate acquisition targets
- **Portfolio risk assessment** - Assess overall deal risk
- **Financial impact analysis** - Inform acquisition pricing
- **Go/no-go decisions** - Data-driven M&A decision-making
- **Deal structuring** - Risk-based deal terms
- **Post-acquisition planning** - Risk mitigation strategies

## File Locations

- **Queries:** `db-16/queries/queries.md` (30 queries with full SQL)
- **Query Metadata:** `db-16/queries/queries.json` (Structured query data)
- **Schema:** `db-16/data/schema.sql` (Database schema definition)
