#!/usr/bin/env python3
"""
Add business use cases to all queries in queries.md
"""

from pathlib import Path
import re

# Business use case mappings
BUSINESS_USE_CASES = {
    6: {
        "title": "Spatial Join Optimization Analysis with Boundary-Forecast Matching Efficiency Metrics",
        "use_case": "Custom Weather Impact Modeling - Boundary-Forecast Matching Efficiency for Logistics Optimization",
        "deliverable": "Analysis of how efficiently forecasts match to client-defined boundaries with optimization recommendations. Helps logistics companies optimize forecast-to-delivery-zone matching for faster route planning.",
        "value": "Optimizes forecast-to-boundary matching for faster client deliverables and improved operational efficiency."
    },
    7: {
        "title": "Weather Station Network Coverage Analysis with Spatial Gap Detection and Coverage Optimization",
        "use_case": "Supply Chain and Fleet Management - Station Coverage Gap Analysis for Route Planning",
        "deliverable": "Map showing gaps in weather station coverage along routes with coverage density metrics. Fleet management companies can identify areas where additional monitoring may be needed.",
        "value": "Identifies areas where additional weather monitoring may be needed to ensure adequate coverage for logistics operations."
    },
    8: {
        "title": "Forecast Accuracy Trend Analysis with Temporal Error Pattern Detection",
        "use_case": "Forensic Meteorology - Historical Forecast Accuracy Assessment for Legal Cases",
        "deliverable": "Trend analysis showing forecast accuracy over time with error pattern detection. Provides evidence of forecast reliability for insurance claim disputes and legal cases.",
        "value": "Provides quantitative evidence of forecast reliability for legal proceedings and insurance claim validation."
    },
    9: {
        "title": "Transformation Log Error Analysis with Root Cause Detection",
        "use_case": "Internal Operations - Data Pipeline Error Root Cause Analysis",
        "deliverable": "Error pattern analysis for data transformation failures with root cause identification. Internal operations team can identify systematic data processing issues.",
        "value": "Improves data pipeline reliability by identifying and resolving systematic data processing issues."
    },
    10: {
        "title": "Snowflake Load Performance Analysis with Throughput Optimization Metrics",
        "use_case": "Internal Operations - Data Warehouse Performance Optimization",
        "deliverable": "Performance metrics for data loading operations with throughput analysis. Operations team can optimize data loading for faster client report generation.",
        "value": "Ensures timely data availability for client projects by optimizing data warehouse performance."
    },
    11: {
        "title": "Boundary Forecast Aggregation Analysis with Multi-Level Spatial Summarization",
        "use_case": "Custom Weather Impact Modeling - Aggregated Forecasts by Boundary for Retail Operations",
        "deliverable": "Summary forecasts aggregated by client-defined boundaries (counties, zones). Retail chains can get aggregated temperature forecasts for each store location's county.",
        "value": "Provides simplified forecasts for specific geographic areas enabling location-based business decisions."
    },
    12: {
        "title": "Observation Forecast Validation Analysis with Accuracy Scoring",
        "use_case": "Forensic Meteorology - Forecast vs. Observation Validation for Legal Evidence",
        "deliverable": "Validation report comparing forecasts to actual observations with accuracy scoring. Legal cases require documentation that forecasts were accurate at specific times/locations.",
        "value": "Provides evidence of forecast accuracy for legal proceedings and insurance claim validation."
    },
    13: {
        "title": "Multi-Boundary Spatial Intersection Analysis with Overlap Detection",
        "use_case": "Custom Map Development - Boundary Overlap Detection for Real Estate Development",
        "deliverable": "Analysis of overlapping boundaries (e.g., fire zones overlapping counties) with intersection metrics. Real estate developers can understand which fire zones overlap with property boundaries.",
        "value": "Helps clients understand complex geographic relationships for property and risk assessment."
    },
    14: {
        "title": "Temporal Forecast Consistency Analysis with Persistence Metrics",
        "use_case": "Supply Chain and Fleet Management - Forecast Stability Assessment for Route Planning",
        "deliverable": "Analysis of how forecasts change over time (persistence metrics) with stability indicators. Shipping companies can assess if forecasts are stable enough for multi-day route planning.",
        "value": "Helps clients understand forecast reliability windows for planning purposes."
    },
    15: {
        "title": "Parameter Forecast Distribution Analysis with Statistical Profiling",
        "use_case": "Physical Climate Risk Assessment - Statistical Weather Profiling for Insurance Underwriting",
        "deliverable": "Statistical distribution analysis of forecast parameters with percentile rankings. Insurance companies need statistical profiles of weather parameters for underwriting decisions.",
        "value": "Identifies normal vs. extreme weather patterns for risk assessment and insurance pricing."
    },
    16: {
        "title": "Geospatial Forecast Interpolation Analysis with Spatial Gradient Detection",
        "use_case": "Custom Weather Impact Modeling - Spatial Gradient Detection for Precision Agriculture",
        "deliverable": "Analysis of how weather parameters change across space with gradient calculations. Agriculture companies can understand temperature gradients across farmland for precision farming.",
        "value": "Identifies spatial gradients for precise location-specific forecasts enabling precision agriculture."
    },
    17: {
        "title": "Weather Pattern Clustering Analysis with Spatial-Temporal Pattern Detection",
        "use_case": "Physical Climate Risk Assessment - Pattern-Based Risk Identification for Renewable Energy",
        "deliverable": "Identification of recurring weather patterns with clustering metrics. Energy companies can identify patterns that affect renewable energy generation.",
        "value": "Helps predict future weather patterns based on historical clusters for energy planning."
    },
    18: {
        "title": "Forecast Model Performance Comparison with Multi-Model Analysis",
        "use_case": "Forensic Meteorology - Multi-Model Analysis for Comprehensive Legal Evidence",
        "deliverable": "Comparison of different forecast models' performance with accuracy metrics. Court cases require comparison of multiple forecast models to establish weather conditions.",
        "value": "Provides comprehensive analysis using multiple models for legal evidence and risk assessment."
    },
    19: {
        "title": "Spatial Forecast Gradient Analysis with Directional Pattern Detection",
        "use_case": "Energy and Power Load Forecasting - Directional Weather Pattern Detection for Load Prediction",
        "deliverable": "Analysis of directional weather patterns (e.g., temperature fronts) with movement indicators. Utility companies can predict temperature front movement for load forecasting.",
        "value": "Helps predict weather movement for energy load forecasting and grid management."
    },
    20: {
        "title": "Boundary Forecast Anomaly Detection with Statistical Outlier Identification",
        "use_case": "Physical Climate Risk Assessment - Extreme Event Detection for Emergency Management",
        "deliverable": "Identification of anomalous weather patterns within boundaries with outlier metrics. Emergency management needs anomaly detection for early warning systems.",
        "value": "Early warning system for extreme weather events enabling proactive risk management."
    },
    21: {
        "title": "Multi-Source Data Integration Analysis with Cross-Source Validation",
        "use_case": "Custom Weather Impact Modeling - Cross-Source Validation for Data Quality Assurance",
        "deliverable": "Validation report comparing multiple data sources (GRIB2, API) with consistency metrics. Client projects require validation that forecasts match observations.",
        "value": "Ensures data consistency across sources for reliable client deliverables."
    },
    22: {
        "title": "Forecast Uncertainty Quantification with Confidence Interval Analysis",
        "use_case": "Supply Chain and Fleet Management - Confidence Interval Analysis for Risk-Aware Planning",
        "deliverable": "Forecast confidence intervals with uncertainty quantification for decision-making. Logistics companies need confidence intervals to assess risk of weather delays.",
        "value": "Provides uncertainty ranges for risk-aware planning and decision-making."
    },
    23: {
        "title": "Spatial Forecast Correlation Analysis with Cross-Location Dependency Detection",
        "use_case": "Energy and Power Load Forecasting - Cross-Location Dependency Detection for Wind Farm Operations",
        "deliverable": "Analysis of weather correlations between locations with dependency metrics. Wind farm operators can understand wind correlation between turbine locations.",
        "value": "Helps predict weather at one location based on another for distributed energy systems."
    },
    24: {
        "title": "Temporal Forecast Persistence Analysis with Forecast Stability Metrics",
        "use_case": "Supply Chain and Fleet Management - Forecast Stability Metrics for Multi-Day Planning",
        "deliverable": "Analysis of how long forecasts remain accurate with persistence indicators. Delivery companies need to know forecast stability for multi-day route planning.",
        "value": "Helps clients understand forecast reliability windows for extended planning horizons."
    },
    25: {
        "title": "Boundary Forecast Aggregation Hierarchy with Multi-Level Summarization",
        "use_case": "Custom Map Development - Multi-Level Forecast Summarization for State Agencies",
        "deliverable": "Forecasts aggregated at multiple geographic levels (state, county, zone) with hierarchy metrics. State agencies need forecasts at both state and county levels.",
        "value": "Provides forecasts at different scales enabling multi-level decision-making."
    },
    26: {
        "title": "Weather Event Detection Analysis with Extreme Event Identification",
        "use_case": "Forensic Meteorology - Extreme Event Identification for Insurance Claims",
        "deliverable": "Identification and documentation of extreme weather events with event characteristics. Insurance claims require documentation of extreme weather event occurrence.",
        "value": "Provides evidence of extreme events for insurance/legal cases."
    },
    27: {
        "title": "Forecast Skill Score Calculation with Model Performance Metrics",
        "use_case": "Forensic Meteorology - Model Performance Metrics for Quantitative Legal Evidence",
        "deliverable": "Skill scores quantifying forecast model performance with statistical metrics. Court cases require quantitative proof of forecast model reliability.",
        "value": "Provides quantitative metrics of forecast quality for legal evidence."
    },
    28: {
        "title": "Spatial Forecast Interpolation Validation with Cross-Validation Metrics",
        "use_case": "Custom Weather Impact Modeling - Interpolation Accuracy Assessment for Location-Specific Forecasts",
        "deliverable": "Validation of forecast interpolation accuracy with cross-validation metrics. Clients need forecasts for specific locations, validation ensures accuracy.",
        "value": "Ensures accurate forecasts for locations without direct observations."
    },
    29: {
        "title": "Multi-Parameter Forecast Ensemble Analysis with Ensemble Statistics",
        "use_case": "Physical Climate Risk Assessment - Ensemble Statistics for Comprehensive Risk Quantification",
        "deliverable": "Ensemble analysis combining multiple weather parameters with statistical summaries. Climate risk assessment requires ensemble analysis of temperature, precipitation, and wind.",
        "value": "Provides comprehensive risk assessment using multiple parameters for climate risk analysis."
    },
    30: {
        "title": "Boundary Forecast Statistical Summary with Comprehensive Analytics",
        "use_case": "Custom Weather Impact Modeling - Comprehensive Boundary Analytics for Business Planning",
        "deliverable": "Complete statistical summary of forecasts by boundary with comprehensive metrics. Clients need complete statistical summary for business planning and decision-making.",
        "value": "Provides comprehensive analytics for client decision-making and strategic planning."
    }
}

def update_queries():
    """Update queries.md with business use cases"""
    script_dir = Path(__file__).parent
    queries_file = script_dir.parent / 'queries' / 'queries.md'

    with open(queries_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern to match query headers
    pattern = r'(## Query (\d+):\s*[^\n]+)\n\n(\*\*Description:\*\*[^\n]+)'

    def replace_query(match):
        query_num = int(match.group(2))
        original_title = match.group(1)
        original_desc = match.group(3)

        if query_num in BUSINESS_USE_CASES:
            uc = BUSINESS_USE_CASES[query_num]
            return f"""{original_title}

**Business Use Case:** **{uc['use_case']}**

{original_desc}

**Client Deliverable:** {uc['deliverable']}

**Business Value:** {uc['value']}"""
        return match.group(0)

    updated_content = re.sub(pattern, replace_query, content)

    # Write updated content
    with open(queries_file, 'w', encoding='utf-8') as f:
        f.write(updated_content)

    print(f"✅ Updated queries.md with business use cases for queries 6-30")

if __name__ == '__main__':
    update_queries()
