#!/usr/bin/env python3
"""
Fix description vs evidence in db-16 queries.json: description = context, evidence = justification.
Description: domain, purpose, who needs it, why.
Evidence: how the query implements it, technical approach (CTEs, joins, window functions).
"""
import json
import re
from pathlib import Path

BASE = Path(__file__).parent.parent
SRC = BASE / "source" / "db-16" / "app" / "QUERIES" / "queries.json"

# db-16: description = context only; evidence = technical justification only
# Descriptions kept as-is (already context-focused); evidence extracted from "The query" onwards

DB16_DESCRIPTIONS = {
    1: "A real estate investment firm is conducting due diligence on potential property acquisitions and needs to understand comprehensive flood risk exposure.",
    2: "A real estate acquisition team has identified multiple properties across different geographic regions and needs to understand spatial risk patterns before finalizing purchase decisions.",
    3: "During the due diligence process for property acquisitions, the investment team needs to understand the actual historical flood experience of target properties, not just theoretical risk scores.",
    4: "An institutional investor is building a long-term coastal real estate portfolio and must understand how climate change and sea level rise will affect property values and flood risk over multiple decades.",
    5: "A property acquisition team is evaluating sites near rivers and streams where riverine flooding is the primary risk driver, requiring analysis of actual streamflow measurements rather than coastal or precipitation-based models.",
    6: "The Flood Risk Assessment team needs to evaluate the accuracy and reliability of NASA's flood prediction models against actual flood events for model validation.",
    7: "Urban planners and insurance underwriters require detailed understanding of which properties fall within designated flood zones to assess exposure and inform zoning decisions.",
    8: "Climate change and urban development are altering flood risk profiles across regions, making historical trend analysis essential for long-term planning.",
    9: "Flood risk is not uniformly distributed but tends to cluster in specific geographic areas due to topography, drainage patterns, and development density. Understanding these clusters helps emergency services position resources strategically and guides infrastructure investment decisions.",
    10: "Property-level vulnerability assessment requires integrating multiple risk dimensions including flood zone classification, structural characteristics, historical flood events, and socioeconomic factors. Insurance companies and government agencies need standardized vulnerability scores to prioritize interventions and set appropriate coverage terms.",
    11: "Our investment team is evaluating multiple acquisition targets in flood-prone areas and needs to quantify the financial risk exposure.",
    12: "Our insurance underwriting department must align premium pricing with the latest FEMA flood zone designations, which range from high-risk Special Flood Hazard Areas (SFHA) to moderate and low-risk zones.",
    13: "Our coastal property development division is planning infrastructure investments with 30-50 year horizons and must account for climate-driven sea level rise. NOAA provides multiple probabilistic scenarios that project different rates of sea level increase.",
    14: "Our flood forecasting and emergency management team monitors riverine flood risk for properties adjacent to major waterways. USGS streamflow gauge data reveals recurring flood patterns, seasonal peaks, and long-term trend shifts that inform risk scoring and early warning systems.",
    15: "Our climate risk analytics team integrates NASA's flood prediction models. These predictions must be validated against actual flood occurrences to assess model reliability before incorporating them into operational risk management workflows.",
    16: "Our real estate investment team is evaluating multiple property portfolios for potential acquisition in flood-prone regions. We need to assess the aggregate flood risk exposure across these portfolios to inform acquisition decisions and pricing strategies.",
    17: "Our flood risk assessment operations rely on accurate and complete data from multiple sources. Data quality issues such as missing risk scores, outdated assessments, or mismatched property-to-flood-zone linkages can lead to incorrect risk evaluations and poor business decisions.",
    18: "Our flood risk assessment platform processes millions of property records that must be spatially matched to flood zone boundaries. Traditional spatial joins using full geometric intersection operations are computationally expensive and cause query timeouts on large datasets.",
    19: "Our flood risk assessment practice utilizes risk scores from multiple independent sources including FEMA flood maps, private insurance models, climate projection services, and historical claim databases. Investment decisions require a comprehensive, weighted risk score that synthesizes all available data sources.",
    20: "Climate change, infrastructure development, and environmental factors are causing flood risk profiles to change dynamically over time. Investment decisions require understanding not just current flood risk but projected risk evolution over the asset lifecycle.",
    21: "The flood risk management team needs to understand whether property elevation is a reliable predictor of flood risk to improve risk assessment models and inform insurance underwriting decisions.",
    22: "Following several major flood events, the risk assessment department needs to evaluate the actual impact of past floods on properties to validate risk models, calculate insurance payouts, and update future risk predictions.",
    23: "The analytics team has deployed multiple flood risk prediction models and needs to evaluate which model provides the most accurate risk assessments to determine which should be used for production risk scoring.",
    24: "Urban planners and insurance underwriters need to understand the geographic distribution of flood risk to prioritize infrastructure investments, set regional insurance rates, and identify areas requiring enhanced flood mitigation measures.",
    25: "Insurance underwriters need to understand how flood risk varies by property type (residential, commercial, industrial, etc.) to establish accurate premium rates, coverage limits, and risk-based underwriting guidelines.",
    26: "The Flood Risk Assessment team needs to understand how flood events cascade through connected geographical zones.",
    27: "During M&A due diligence for a real estate portfolio acquisition, the investment team must identify properties with flood risk severe enough to terminate negotiations or significantly reduce valuation.",
    28: "After acquiring a property portfolio with flood exposure, the asset management team needs to prioritize capital allocation for risk mitigation measures such as elevation, flood barriers, or drainage improvements.",
    29: "The acquisitions team is evaluating multiple property portfolios as potential targets and needs to understand concentration risk from flood exposure.",
    30: "The M&A team requires a comprehensive flood risk assessment report covering all material aspects of environmental exposure for a target property portfolio.",
}

DB16_EVIDENCE = {
    1: "The query joins flood_zones, properties, and risk_scores tables on property identifiers, aggregates risk components by property, calculates composite risk scores using weighted averages, applies risk category thresholds (low/medium/high/extreme), and computes financial impact estimates based on property value.",
    2: "The query spatially joins properties with flood_zones using geographic coordinates, groups properties by region and sub-region, calculates aggregate risk metrics (average, maximum, standard deviation) for each geographic cluster, identifies hotspots where risk scores exceed regional thresholds, and uses window functions for cluster rankings.",
    3: "The query joins properties with historical flood event records, groups events by property and time dimensions (year, season, decade), calculates event frequencies and time intervals between occurrences, and uses window functions to compute rolling averages of event frequency and recurrence intervals.",
    4: "The query filters properties within coastal proximity thresholds, joins with sea level rise projection models for each time horizon and scenario, calculates flood zone changes as properties migrate from lower to higher risk zones, and aggregates exposure by scenario.",
    5: "The query identifies properties within catchment areas of stream gauges, joins properties with the nearest upstream and downstream gauge stations, retrieves historical discharge data, and calculates recurrence intervals and peak flow statistics for flood frequency analysis.",
    6: "The query joins flood model predictions with actual flood observations, groups results by model version and time period, calculates performance metrics such as precision, recall, and RMSE, uses window functions to compute rolling accuracy trends and comparative benchmarks, applies quartile analysis to segment prediction errors, and handles NULL values for incomplete observation data.",
    7: "The query performs spatial joins between properties and flood_zones tables to identify intersections, groups results by flood zone classification and property type, calculates aggregate metrics including total property count, assessed value exposure, and average risk scores per zone, and uses window functions to rank zones by exposure level and compute percentile distributions.",
    8: "The query extracts risk scores with associated timestamps, groups data by time periods (monthly, quarterly, yearly) and geographic dimensions, calculates aggregate risk metrics and growth rates for each period, uses window functions to compute rolling averages, year-over-year comparisons, and moving trend indicators, applies quartile analysis to identify accelerating risk areas, and handles NULL values in historical records.",
    9: "The query groups data by geographic coordinates and administrative boundaries, calculates density metrics and aggregate risk scores for each area, identifies clusters using spatial proximity and risk threshold criteria, uses window functions to compute cluster rankings and comparative metrics between clusters, and applies quartile analysis to segment cluster risk levels.",
    10: "The query joins properties with flood_zones and risk_scores tables, aggregates multiple risk dimensions including location-based hazard levels, property characteristics like elevation and construction type, historical loss data, and proximity to water bodies, applies weighting factors to different risk components, and uses window functions for percentile rankings.",
    11: "The query performs multi-dimensional aggregation by grouping properties by flood zone classification and risk tier, calculates summary statistics including total property values at risk, average risk scores, and value quartiles to identify concentration risk. Window functions compute rolling averages of historical flood events and year-over-year risk score changes. LEFT JOINs ensure all properties are included even with missing data.",
    12: "The query groups properties by FEMA flood zone designations (A, AE, V, VE, X, etc.) and calculates aggregate metrics including property counts per zone, total insured values, and average risk scores. Statistical functions compute quartile distributions of risk scores within each zone to identify outliers and concentration. Window functions generate zone rankings and comparative metrics.",
    13: "The query creates scenario-based groupings by categorizing properties according to their elevation relative to each NOAA projection threshold (0.5m, 1.0m, 1.5m, 2.0m sea level rise by 2100). Aggregation functions calculate properties at risk, total asset values exposed, and risk trajectory by scenario.",
    14: "The query aggregates USGS streamflow measurements by time periods (monthly, seasonal, annual) and gauge locations, calculating statistical measures including mean discharge, peak flows, base flows, and flow variability coefficients. Window functions compute rolling averages, trend indicators, and comparative metrics across gauges.",
    15: "The query joins NASA model predictions (forecasted flood zones or risk probabilities) with observed flood outcomes, groups by model and geography, calculates accuracy metrics (precision, recall, MAE, RMSE), and uses window functions for model comparison and confidence intervals.",
    16: "The query joins properties with their corresponding flood zones and risk scores, groups properties by portfolio identifier and flood zone category, computes aggregate metrics including total exposure value, average risk scores, and property counts, and calculates quartile distributions of risk scores within each portfolio.",
    17: "The query performs completeness checks by counting NULL and missing values in critical fields across all three tables, calculates consistency metrics by identifying properties without matching flood zone assignments or risk scores, groups quality metrics by data source and property type, and uses window functions for trend analysis.",
    18: "The query employs spatial indexing hints to leverage pre-built spatial indexes on property locations and flood zone geometries, uses bounding box pre-filtering to quickly eliminate non-overlapping candidates, and applies staged filtering to reduce computational load.",
    19: "The query pivots risk scores from different sources stored in the risk_scores table, applies source-specific weighting factors, aggregates into a composite score using weighted averages, and uses window functions for percentile rankings across the portfolio.",
    20: "The query extracts historical risk score time series for each property, groups by property and time period, calculates trend metrics and rate-of-change indicators, uses window functions for rolling averages and year-over-year comparisons, and projects risk evolution over hold periods.",
    21: "The query joins properties with their associated flood zones and risk scores, groups properties by elevation ranges or quartiles, calculates aggregate risk metrics (mean, median, standard deviation) for each elevation band, applies window functions to compute rolling averages and percentile rankings, and uses correlation coefficients to measure the strength of the elevation-risk relationship.",
    22: "The query retrieves historical flood events with their occurrence dates and severity levels, joins with affected properties within flood zone boundaries, groups results by flood event and property characteristics, calculates aggregated impact metrics including number of properties affected, total estimated damages, and average risk score changes before and after events. Window functions compute running totals and event rankings.",
    23: "The query extracts predicted risk scores from multiple models alongside actual flood outcomes for each property, groups results by model identifier and time period, calculates performance metrics including prediction accuracy, MAE, RMSE, and confusion matrix statistics (true positives, false positives, etc.). Window functions compute percentile rankings of model performance.",
    24: "The query groups properties by geographic dimensions such as flood zone designation, county, zip code, or grid coordinates, calculates aggregate risk metrics for each geographic unit including average risk score, property count, high-risk property percentage, and risk score quartiles. Window functions compute regional rankings and compare each area's risk to neighboring regions.",
    25: "The query groups properties by type classification (single-family residential, multi-family, commercial, industrial, etc.), joins with associated flood zones and risk scores, calculates aggregate statistics for each property type including average risk score, median risk score, risk score distribution quartiles, count of high-risk properties, and percentage of properties in flood zones. Window functions compute type-level rankings.",
    26: "The query uses recursive CTEs to traverse zone connectivity relationships, joins flood_zones with properties and risk_scores tables, groups results by zone hierarchy levels, computes aggregate risk scores at each propagation level using window functions for cumulative impact analysis, calculates rolling averages to identify risk acceleration patterns, and handles NULL values in zone connectivity data.",
    27: "The query joins properties with flood_zones and risk_scores tables using LEFT JOINs to capture properties with missing risk data, filters for properties exceeding critical risk thresholds (top quartile), groups results by zone and property characteristics, computes aggregate exposure metrics including total property value at risk and count of critically exposed assets, and uses window functions to rank and compare exposure levels.",
    28: "The query joins properties with risk_scores and flood_zones tables, groups properties by current risk level and mitigation scenario, computes baseline risk exposure values and potential losses, calculates mitigation costs by property type and zone characteristics using CASE statements, and uses window functions to calculate risk reduction percentages and payback periods across different mitigation strategies.",
    29: "The query aggregates properties from target portfolios joining flood_zones and risk_scores tables, groups by target portfolio identifier, zone type, and risk tier, computes concentration metrics including Herfindahl index for geographic and risk dispersion, uses window functions to calculate portfolio-level statistics and compare each target against benchmark diversification ratios, and analyzes correlation between portfolio composition and risk exposure.",
    30: "The query performs complex joins across flood_zones, properties, and risk_scores tables using LEFT JOINs to ensure complete coverage including properties with incomplete data, groups results by multiple dimensions including zone type, property characteristics, and risk categories, and computes extensive aggregate metrics including total exposure value, risk score distributions, and concentration metrics.",
}


def fix_db16(path: Path) -> bool:
    with open(path) as f:
        data = json.load(f)
    changed = False
    for q in data.get("queries", []):
        n = q.get("number")
        if n in DB16_DESCRIPTIONS and n in DB16_EVIDENCE:
            if q.get("description") != DB16_DESCRIPTIONS[n] or q.get("evidence") != DB16_EVIDENCE[n]:
                q["description"] = DB16_DESCRIPTIONS[n]
                q["evidence"] = DB16_EVIDENCE[n]
                changed = True
    if changed:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Updated {path}")
    return changed


def main():
    if SRC.exists():
        fix_db16(SRC)
    else:
        print(f"Not found: {SRC}")


if __name__ == "__main__":
    main()
