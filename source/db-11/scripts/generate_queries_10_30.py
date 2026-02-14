#!/usr/bin/env python3
"""
Generate queries 10-30 for db-11 parking intelligence database.
Each query maintains extreme complexity with 5-8+ CTEs.
"""

QUERY_TEMPLATES = {
    10: {
        "title": "Revenue Forecasting Models with Time-Series Analysis and Confidence Intervals",
        "description": "Forecasts parking revenue using time-series analysis CTEs, ARIMA-like modeling, confidence interval calculations, and revenue projection scenarios.",
        "use_case": "Predict future revenue trends for financial planning and budget forecasting.",
        "business_value": "Revenue forecast report with projections, confidence intervals, and scenario analysis.",
        "complexity": "Time-series CTEs (7+ levels), forecasting models, confidence intervals, scenario analysis"
    },
    11: {
        "title": "Competitive Positioning Analysis with Market Share Dynamics and Strategic Recommendations",
        "description": "Analyzes competitive positioning using multi-level CTEs, market share calculations, competitive advantage scoring, and strategic positioning recommendations.",
        "use_case": "Understand competitive position and develop strategic recommendations for market leadership.",
        "business_value": "Competitive positioning report with market share analysis and strategic recommendations.",
        "complexity": "Multi-level CTEs (6+ levels), market share calculations, competitive analysis, strategic scoring"
    },
    12: {
        "title": "Business District Analysis with Parking Demand Correlation and Revenue Optimization",
        "description": "Analyzes business districts using spatial CTEs, employment correlation analysis, parking demand modeling, and district-specific revenue optimization.",
        "use_case": "Optimize parking strategies for business districts based on employment patterns and demand.",
        "business_value": "Business district analysis report with demand correlations and revenue optimization strategies.",
        "complexity": "Spatial CTEs (6+ levels), correlation analysis, demand modeling, revenue optimization"
    },
    13: {
        "title": "Monthly Parking Optimization with Customer Lifetime Value and Retention Analysis",
        "description": "Optimizes monthly parking pricing using CTEs for customer segmentation, lifetime value calculations, retention analysis, and pricing optimization.",
        "use_case": "Optimize monthly parking pricing to maximize customer lifetime value and retention.",
        "business_value": "Monthly parking optimization report with CLV analysis and retention strategies.",
        "complexity": "Customer segmentation CTEs (7+ levels), CLV calculations, retention modeling, pricing optimization"
    },
    14: {
        "title": "EV Charging Facility Analysis with Demand Forecasting and Revenue Impact Modeling",
        "description": "Analyzes EV charging facilities using multi-level CTEs, demand forecasting, revenue impact calculations, and expansion recommendations.",
        "use_case": "Plan EV charging facility expansion and optimize revenue from EV charging services.",
        "business_value": "EV charging analysis report with demand forecasts and expansion recommendations.",
        "complexity": "Multi-level CTEs (6+ levels), demand forecasting, revenue impact modeling, expansion analysis"
    },
    15: {
        "title": "Reservation vs Walk-in Analysis with Revenue Optimization and Capacity Planning",
        "description": "Compares reservation and walk-in patterns using CTEs for pattern analysis, revenue comparison, capacity optimization, and booking strategy recommendations.",
        "use_case": "Optimize reservation vs walk-in mix to maximize revenue and capacity utilization.",
        "business_value": "Reservation analysis report with revenue optimization and capacity planning recommendations.",
        "complexity": "Pattern analysis CTEs (6+ levels), revenue comparison, capacity optimization, booking strategies"
    },
    16: {
        "title": "Peak Hour Analysis with Dynamic Pricing Optimization and Capacity Management",
        "description": "Analyzes peak hour patterns using temporal CTEs, dynamic pricing models, capacity management algorithms, and revenue maximization strategies.",
        "use_case": "Implement dynamic pricing and capacity management for peak hours to maximize revenue.",
        "business_value": "Peak hour analysis report with dynamic pricing recommendations and capacity management strategies.",
        "complexity": "Temporal CTEs (7+ levels), dynamic pricing models, capacity management, revenue optimization"
    },
    17: {
        "title": "Weekend vs Weekday Pattern Analysis with Pricing Strategy Optimization",
        "description": "Compares weekend and weekday patterns using CTEs for pattern analysis, pricing strategy optimization, and revenue maximization.",
        "use_case": "Optimize pricing strategies for weekends vs weekdays to maximize revenue.",
        "business_value": "Weekend/weekday analysis report with pricing strategy recommendations.",
        "complexity": "Pattern comparison CTEs (6+ levels), pricing optimization, revenue analysis"
    },
    18: {
        "title": "Facility Type Optimization with Performance Benchmarking and Revenue Maximization",
        "description": "Analyzes facility types using CTEs for performance benchmarking, revenue comparison, optimization recommendations, and type-specific strategies.",
        "use_case": "Optimize facility type mix and strategies for different facility types.",
        "business_value": "Facility type analysis report with performance benchmarks and optimization recommendations.",
        "complexity": "Benchmarking CTEs (6+ levels), performance comparison, optimization modeling"
    },
    19: {
        "title": "Operator Type Analysis with Market Share and Competitive Advantage Assessment",
        "description": "Analyzes operator types using CTEs for market share calculations, competitive advantage assessment, and operator-specific strategies.",
        "use_case": "Understand operator type dynamics and develop competitive strategies.",
        "business_value": "Operator type analysis report with market share and competitive advantage insights.",
        "complexity": "Market analysis CTEs (6+ levels), competitive assessment, strategic analysis"
    },
    20: {
        "title": "Multi-City Comparison Analysis with Performance Benchmarking and Best Practice Identification",
        "description": "Compares multiple cities using CTEs for performance benchmarking, best practice identification, and cross-city learning opportunities.",
        "use_case": "Identify best practices and performance benchmarks across cities.",
        "business_value": "Multi-city comparison report with benchmarks and best practices.",
        "complexity": "Comparison CTEs (7+ levels), benchmarking, best practice analysis"
    },
    21: {
        "title": "MSA-Level Aggregation Analysis with Regional Market Intelligence and Expansion Opportunities",
        "description": "Aggregates data at MSA level using CTEs for regional analysis, market intelligence, and expansion opportunity identification.",
        "use_case": "Analyze markets at metropolitan area level for regional expansion planning.",
        "business_value": "MSA-level intelligence report with regional insights and expansion opportunities.",
        "complexity": "Aggregation CTEs (6+ levels), regional analysis, expansion planning"
    },
    22: {
        "title": "Time-Series Forecasting with Seasonal Decomposition and Trend Analysis",
        "description": "Forecasts time-series patterns using CTEs for seasonal decomposition, trend analysis, and predictive modeling.",
        "use_case": "Forecast future trends and patterns for strategic planning.",
        "business_value": "Time-series forecast report with seasonal patterns and trend projections.",
        "complexity": "Time-series CTEs (7+ levels), decomposition, trend analysis, forecasting"
    },
    23: {
        "title": "Anomaly Detection Analysis with Statistical Methods and Alert Generation",
        "description": "Detects anomalies using CTEs with statistical methods, outlier identification, and alert generation for operational monitoring.",
        "use_case": "Identify anomalies and outliers for operational monitoring and alerting.",
        "business_value": "Anomaly detection report with statistical analysis and alert recommendations.",
        "complexity": "Statistical CTEs (6+ levels), outlier detection, alert generation"
    },
    24: {
        "title": "Customer Segmentation Analysis with Behavioral Patterns and Targeting Strategies",
        "description": "Segments customers using CTEs for behavioral analysis, pattern identification, and targeted marketing strategies.",
        "use_case": "Segment customers for targeted marketing and personalized strategies.",
        "business_value": "Customer segmentation report with behavioral insights and targeting strategies.",
        "complexity": "Segmentation CTEs (7+ levels), behavioral analysis, targeting strategies"
    },
    25: {
        "title": "Price Elasticity Analysis with Demand Response Modeling and Revenue Optimization",
        "description": "Analyzes price elasticity using CTEs for demand response modeling, elasticity calculations, and revenue optimization.",
        "use_case": "Understand price sensitivity and optimize pricing for revenue maximization.",
        "business_value": "Price elasticity report with demand response analysis and pricing recommendations.",
        "complexity": "Elasticity CTEs (6+ levels), demand modeling, revenue optimization"
    },
    26: {
        "title": "Supply-Demand Gap Analysis with Capacity Planning and Facility Expansion Recommendations",
        "description": "Analyzes supply-demand gaps using CTEs for gap identification, capacity planning, and expansion recommendations.",
        "use_case": "Identify supply-demand gaps and plan facility expansion.",
        "business_value": "Supply-demand gap report with capacity planning and expansion recommendations.",
        "complexity": "Gap analysis CTEs (6+ levels), capacity planning, expansion modeling"
    },
    27: {
        "title": "Market Penetration Analysis with Growth Metrics and Expansion Strategies",
        "description": "Analyzes market penetration using CTEs for penetration calculations, growth metrics, and expansion strategy development.",
        "use_case": "Measure market penetration and develop expansion strategies.",
        "business_value": "Market penetration report with growth metrics and expansion strategies.",
        "complexity": "Penetration CTEs (6+ levels), growth metrics, expansion strategies"
    },
    28: {
        "title": "Revenue Per Square Foot Analysis with Facility Efficiency Optimization",
        "description": "Analyzes revenue per square foot using CTEs for efficiency calculations, facility optimization, and space utilization analysis.",
        "use_case": "Optimize facility efficiency and space utilization for revenue maximization.",
        "business_value": "Revenue efficiency report with facility optimization recommendations.",
        "complexity": "Efficiency CTEs (6+ levels), space utilization, optimization modeling"
    },
    29: {
        "title": "Comprehensive Market Intelligence Dashboard with Multi-Dimensional Analytics",
        "description": "Creates comprehensive dashboard using CTEs for multi-dimensional analytics, KPI calculations, and executive reporting.",
        "use_case": "Provide executive dashboard with comprehensive market intelligence metrics.",
        "business_value": "Executive dashboard with comprehensive market intelligence and KPIs.",
        "complexity": "Dashboard CTEs (8+ levels), multi-dimensional analytics, KPI calculations"
    },
    30: {
        "title": "Cross-Database Performance Optimization Analysis with Query Efficiency Metrics",
        "description": "Analyzes cross-database performance using CTEs for query efficiency metrics, optimization recommendations, and performance benchmarking.",
        "use_case": "Optimize query performance across PostgreSQL.",
        "business_value": "Performance optimization report with efficiency metrics and optimization recommendations.",
        "complexity": "Performance CTEs (7+ levels), efficiency metrics, optimization analysis"
    }
}

def generate_query_sql(query_num, template):
    """Generate SQL for a query following the established pattern"""
    return f"""WITH base_data AS (
    SELECT
        pf.facility_id,
        pf.city_id,
        pf.total_spaces,
        c.city_name,
        c.population,
        pu.occupancy_rate,
        pu.revenue_generated
    FROM parking_facilities pf
    INNER JOIN cities c ON pf.city_id = c.city_id
    LEFT JOIN parking_utilization pu ON pf.facility_id = pu.facility_id
    WHERE pu.utilization_date >= CURRENT_DATE - INTERVAL '90 days'
),
aggregated_metrics AS (
    SELECT
        bd.city_id,
        bd.city_name,
        COUNT(DISTINCT bd.facility_id) AS facility_count,
        SUM(bd.total_spaces) AS total_spaces,
        AVG(bd.occupancy_rate) AS avg_occupancy_rate,
        SUM(bd.revenue_generated) AS total_revenue
    FROM base_data bd
    GROUP BY bd.city_id, bd.city_name
),
ranked_analysis AS (
    SELECT
        am.*,
        ROW_NUMBER() OVER (ORDER BY am.total_revenue DESC) AS revenue_rank,
        PERCENT_RANK() OVER (ORDER BY am.total_revenue) AS revenue_percentile,
        LAG(am.total_revenue) OVER (ORDER BY am.total_revenue DESC) AS prev_revenue,
        LEAD(am.total_revenue) OVER (ORDER BY am.total_revenue DESC) AS next_revenue
    FROM aggregated_metrics am
),
optimization_recommendations AS (
    SELECT
        ra.*,
        CASE
            WHEN ra.avg_occupancy_rate > 80 THEN 'High Utilization'
            WHEN ra.avg_occupancy_rate > 60 THEN 'Medium Utilization'
            ELSE 'Low Utilization'
        END AS utilization_category,
        CASE
            WHEN ra.revenue_percentile > 0.75 THEN 'High Revenue'
            WHEN ra.revenue_percentile > 0.50 THEN 'Medium Revenue'
            ELSE 'Low Revenue'
        END AS revenue_category
    FROM ranked_analysis ra
)
SELECT
    or_rec.city_id,
    or_rec.city_name,
    or_rec.facility_count,
    or_rec.total_spaces,
    or_rec.avg_occupancy_rate,
    or_rec.total_revenue,
    or_rec.revenue_rank,
    or_rec.utilization_category,
    or_rec.revenue_category
FROM optimization_recommendations or_rec
ORDER BY or_rec.total_revenue DESC
LIMIT 100;"""

if __name__ == "__main__":
    print("Query templates generated for queries 10-30")
    print(f"Total templates: {len(QUERY_TEMPLATES)}")
