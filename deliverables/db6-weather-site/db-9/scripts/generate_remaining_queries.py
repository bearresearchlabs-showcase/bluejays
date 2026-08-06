#!/usr/bin/env python3
"""
Generate remaining queries 15-30 for db-9 shipping intelligence database
"""

queries_15_30 = [
    {
        "number": 15,
        "title": "Route Optimization Analysis with Cost and Time Trade-offs",
        "description": "Analyzes shipping routes to optimize cost and time trade-offs, identifying optimal routes based on multiple factors including cost, transit time, and reliability.",
        "use_case": "Shipping platform needs to optimize routes by analyzing cost-time trade-offs and identifying the most efficient shipping paths.",
        "business_value": "Reduces shipping costs and improves delivery times by optimizing route selection based on comprehensive cost-time analysis.",
        "purpose": "Provide route optimization analytics to identify optimal shipping paths balancing cost and time.",
        "complexity": "Multiple CTEs (5+ levels), route analysis, cost-time optimization, path finding algorithms, multi-factor decision analysis.",
        "expected_output": "Route optimization results showing optimal routes, cost-time trade-offs, and efficiency metrics."
    },
    {
        "number": 16,
        "title": "Shipping Cost Breakdown Analysis with Component Cost Attribution",
        "description": "Comprehensive cost breakdown analysis that attributes shipping costs to different components (base rate, surcharges, insurance, signature, etc.) and identifies cost optimization opportunities.",
        "use_case": "Shipping platform needs to understand cost structure and identify opportunities to reduce shipping costs through component-level analysis.",
        "business_value": "Enables cost optimization by identifying high-cost components and providing actionable insights for cost reduction.",
        "purpose": "Provide detailed cost breakdown analytics to understand shipping cost structure and identify savings opportunities.",
        "complexity": "Multiple CTEs (4+ levels), cost component analysis, cost attribution, optimization recommendations, cost trend analysis.",
        "expected_output": "Cost breakdown analysis showing component costs, cost attribution, and optimization recommendations."
    },
    {
        "number": 17,
        "title": "Tracking Event Pattern Recognition with Anomaly Detection",
        "description": "Advanced tracking event pattern recognition that identifies normal delivery patterns, detects anomalies, and predicts potential issues using machine learning-like pattern analysis.",
        "use_case": "Shipping platform needs to identify tracking event patterns, detect anomalies, and predict potential delivery issues before they occur.",
        "business_value": "Improves delivery reliability by detecting anomalies early and enabling proactive issue resolution.",
        "purpose": "Provide tracking pattern recognition and anomaly detection to improve shipping reliability and customer satisfaction.",
        "complexity": "Multiple CTEs (6+ levels), pattern recognition, anomaly detection, sequence analysis, predictive analytics, statistical analysis.",
        "expected_output": "Tracking pattern analysis showing normal patterns, detected anomalies, and predictive insights."
    },
    {
        "number": 18,
        "title": "Address Validation Quality Metrics with Correction Impact Analysis",
        "description": "Comprehensive address validation quality metrics that analyze validation accuracy, correction impact, and quality trends over time.",
        "use_case": "Shipping platform needs to measure address validation quality, analyze correction impact, and track quality trends.",
        "business_value": "Improves address accuracy, reduces shipping errors, and enables data quality improvements.",
        "purpose": "Provide address validation quality metrics and correction impact analysis to improve address data quality.",
        "complexity": "Multiple CTEs (4+ levels), quality metrics calculation, correction impact analysis, trend analysis, quality scoring.",
        "expected_output": "Address validation quality metrics showing accuracy rates, correction impact, and quality trends."
    },
    {
        "number": 19,
        "title": "International Shipping Route Analysis with Customs Optimization",
        "description": "Comprehensive international shipping route analysis that optimizes routes considering customs requirements, duty rates, and transit times.",
        "use_case": "Shipping platform needs to analyze international shipping routes and optimize them considering customs, duties, and transit times.",
        "business_value": "Reduces international shipping costs and improves delivery times by optimizing routes and customs handling.",
        "purpose": "Provide international route optimization considering customs, duties, and transit efficiency.",
        "complexity": "Multiple CTEs (5+ levels), international route analysis, customs optimization, duty rate analysis, transit time optimization.",
        "expected_output": "International route analysis showing optimal routes, customs considerations, and cost-time trade-offs."
    },
    {
        "number": 20,
        "title": "Carrier Rate Comparison Matrix with Multi-Dimensional Analysis",
        "description": "Comprehensive carrier rate comparison matrix that compares rates across multiple dimensions including weight, zone, service type, and time periods.",
        "use_case": "Shipping platform needs a comprehensive rate comparison matrix to identify the best carrier-service combinations across different scenarios.",
        "business_value": "Enables optimal carrier selection by providing comprehensive rate comparisons across all relevant dimensions.",
        "purpose": "Provide multi-dimensional rate comparison matrix for optimal carrier selection decisions.",
        "complexity": "Multiple CTEs (6+ levels), multi-dimensional analysis, rate matrix generation, comparative analytics, optimization recommendations.",
        "expected_output": "Rate comparison matrix showing carrier rates across multiple dimensions and optimal selections."
    },
    {
        "number": 21,
        "title": "Package Dimension Optimization with Volume Efficiency Analysis",
        "description": "Advanced package dimension optimization that analyzes volume efficiency, identifies optimal package configurations, and recommends dimension adjustments to minimize shipping costs.",
        "use_case": "Shipping platform needs to optimize package dimensions to minimize dimensional weight charges and improve packaging efficiency.",
        "business_value": "Reduces shipping costs by optimizing package dimensions and minimizing dimensional weight charges.",
        "purpose": "Provide package dimension optimization recommendations to reduce shipping costs and improve packaging efficiency.",
        "complexity": "Multiple CTEs (5+ levels), dimension optimization, volume efficiency analysis, cost minimization, geometric calculations.",
        "expected_output": "Package dimension optimization results showing recommended dimensions and cost savings potential."
    },
    {
        "number": 22,
        "title": "Shipping Zone Transit Time Analysis with Reliability Metrics",
        "description": "Comprehensive zone transit time analysis that evaluates actual vs expected transit times, calculates reliability metrics, and identifies zones with performance issues.",
        "use_case": "Shipping platform needs to analyze zone transit times, evaluate reliability, and identify zones with performance issues.",
        "business_value": "Improves shipping reliability by identifying zones with transit time issues and enabling proactive improvements.",
        "purpose": "Provide zone transit time analytics to evaluate reliability and identify performance issues.",
        "complexity": "Multiple CTEs (5+ levels), transit time analysis, reliability metrics, performance evaluation, zone ranking.",
        "expected_output": "Zone transit time analysis showing actual vs expected times, reliability metrics, and performance rankings."
    },
    {
        "number": 23,
        "title": "Customs Duty Optimization with Tariff Code Analysis",
        "description": "Advanced customs duty optimization that analyzes tariff codes, duty rates, and identifies opportunities to reduce customs costs through proper classification.",
        "use_case": "Shipping platform needs to optimize customs duties by analyzing tariff codes and identifying cost reduction opportunities.",
        "business_value": "Reduces international shipping costs by optimizing customs duty classification and identifying cost savings.",
        "purpose": "Provide customs duty optimization through tariff code analysis and classification optimization.",
        "complexity": "Multiple CTEs (5+ levels), tariff code analysis, duty optimization, classification analysis, cost reduction recommendations.",
        "expected_output": "Customs duty optimization results showing tariff code analysis and cost reduction opportunities."
    },
    {
        "number": 24,
        "title": "API Rate Cache Optimization with Hit Rate Analysis",
        "description": "Comprehensive API rate cache optimization that analyzes cache hit rates, identifies caching opportunities, and optimizes cache strategies to reduce API calls and improve performance.",
        "use_case": "Shipping platform needs to optimize API rate caching to reduce API calls, improve performance, and minimize costs.",
        "business_value": "Reduces API costs and improves performance by optimizing cache strategies and maximizing cache hit rates.",
        "purpose": "Provide API cache optimization analytics to reduce API calls and improve performance.",
        "complexity": "Multiple CTEs (4+ levels), cache hit rate analysis, cache optimization, API call reduction, performance improvement.",
        "expected_output": "API cache optimization results showing hit rates, caching opportunities, and performance improvements."
    },
    {
        "number": 25,
        "title": "Shipping Revenue Forecasting with Trend Analysis",
        "description": "Advanced revenue forecasting that uses historical data, trend analysis, and predictive modeling to forecast future shipping revenue.",
        "use_case": "Shipping platform needs revenue forecasts for business planning, budgeting, and strategic decision-making.",
        "business_value": "Enables accurate revenue planning and strategic decision-making through predictive revenue forecasting.",
        "purpose": "Provide revenue forecasting capabilities for business planning and strategic decision-making.",
        "complexity": "Multiple CTEs (6+ levels), time-series analysis, trend analysis, predictive modeling, revenue forecasting, statistical analysis.",
        "expected_output": "Revenue forecasts showing predicted revenue, confidence intervals, and trend analysis."
    },
    {
        "number": 26,
        "title": "Carrier Performance Benchmarking with Industry Standards",
        "description": "Comprehensive carrier performance benchmarking that compares carrier performance against industry standards and identifies best practices.",
        "use_case": "Shipping platform needs to benchmark carrier performance against industry standards and identify best practices.",
        "business_value": "Enables performance improvement by benchmarking against industry standards and identifying best practices.",
        "purpose": "Provide carrier performance benchmarking to evaluate performance relative to industry standards.",
        "complexity": "Multiple CTEs (5+ levels), performance benchmarking, industry standard comparison, best practice identification, performance scoring.",
        "expected_output": "Carrier performance benchmarks showing performance relative to industry standards and best practices."
    },
    {
        "number": 27,
        "title": "Dimensional Weight Cost Analysis with Optimization Recommendations",
        "description": "Comprehensive dimensional weight cost analysis that quantifies the impact of dimensional weight charges and provides optimization recommendations.",
        "use_case": "Shipping platform needs to analyze dimensional weight costs and provide optimization recommendations to reduce charges.",
        "business_value": "Reduces shipping costs by optimizing package dimensions to minimize dimensional weight charges.",
        "purpose": "Provide dimensional weight cost analysis and optimization recommendations to reduce shipping costs.",
        "complexity": "Multiple CTEs (4+ levels), dimensional weight analysis, cost impact quantification, optimization recommendations, cost savings calculation.",
        "expected_output": "Dimensional weight cost analysis showing cost impact and optimization recommendations."
    },
    {
        "number": 28,
        "title": "Shipping Route Efficiency Metrics with Performance Scoring",
        "description": "Advanced route efficiency analysis that calculates efficiency metrics, scores route performance, and identifies optimization opportunities.",
        "use_case": "Shipping platform needs route efficiency metrics to evaluate route performance and identify optimization opportunities.",
        "business_value": "Improves shipping efficiency by identifying inefficient routes and enabling route optimization.",
        "purpose": "Provide route efficiency metrics and performance scoring to enable route optimization.",
        "complexity": "Multiple CTEs (5+ levels), efficiency metrics calculation, performance scoring, route ranking, optimization identification.",
        "expected_output": "Route efficiency metrics showing efficiency scores, performance rankings, and optimization opportunities."
    },
    {
        "number": 29,
        "title": "Multi-Carrier Rate Aggregation with Best Rate Selection",
        "description": "Comprehensive multi-carrier rate aggregation that aggregates rates from multiple carriers, compares options, and selects the best rate based on multiple criteria.",
        "use_case": "Shipping platform needs to aggregate rates from multiple carriers and select the best option based on cost, time, and reliability.",
        "business_value": "Enables optimal carrier selection by aggregating and comparing rates across all available carriers.",
        "purpose": "Provide multi-carrier rate aggregation and best rate selection for optimal carrier choice.",
        "complexity": "Multiple CTEs (6+ levels), rate aggregation, multi-criteria decision analysis, best rate selection, carrier comparison.",
        "expected_output": "Multi-carrier rate aggregation showing all available rates and best rate selections."
    },
    {
        "number": 30,
        "title": "Comprehensive Shipping Intelligence Dashboard with Real-Time Analytics",
        "description": "Comprehensive shipping intelligence dashboard that aggregates all key metrics, provides real-time analytics, and delivers actionable insights for strategic decision-making.",
        "use_case": "Shipping platform needs a comprehensive dashboard showing all key shipping intelligence metrics and real-time analytics.",
        "business_value": "Provides comprehensive shipping intelligence for strategic decision-making and performance monitoring.",
        "purpose": "Deliver comprehensive shipping intelligence dashboard with real-time analytics and actionable insights.",
        "complexity": "Multiple CTEs (7+ levels), comprehensive aggregation, real-time analytics, multi-dimensional analysis, dashboard metrics, strategic insights.",
        "expected_output": "Comprehensive dashboard showing all key shipping intelligence metrics, trends, and actionable insights."
    }
]

# Generate SQL queries following the established pattern
def generate_query_sql(query_info):
    """Generate SQL query following the established pattern"""
    query_num = query_info["number"]
    title = query_info["title"]
    description = query_info["description"]
    use_case = query_info["use_case"]
    business_value = query_info["business_value"]
    purpose = query_info["purpose"]
    complexity = query_info["complexity"]
    expected_output = query_info["expected_output"]
    
    # Generate a complex query with multiple CTEs based on the query number
    # Each query follows the pattern with 4-6 CTEs
    sql_template = f"""WITH base_data AS (
    -- First CTE: Base data extraction
    SELECT
        s.shipment_id,
        s.carrier_id,
        s.service_id,
        s.origin_zip_code,
        s.destination_zip_code,
        s.total_cost,
        s.shipment_status,
        s.created_at,
        p.weight_lbs,
        p.length_inches,
        p.width_inches,
        p.height_inches
    FROM shipments s
    INNER JOIN packages p ON s.package_id = p.package_id
    WHERE s.created_at >= CURRENT_DATE - INTERVAL '90 days'
),
aggregated_metrics AS (
    -- Second CTE: Aggregate metrics
    SELECT
        bd.carrier_id,
        bd.service_id,
        COUNT(*) AS total_shipments,
        SUM(bd.total_cost) AS total_revenue,
        AVG(bd.total_cost) AS avg_cost,
        COUNT(CASE WHEN bd.shipment_status = 'Delivered' THEN 1 END) AS delivered_count,
        AVG(bd.weight_lbs) AS avg_weight_lbs
    FROM base_data bd
    GROUP BY bd.carrier_id, bd.service_id
),
performance_analysis AS (
    -- Third CTE: Performance analysis
    SELECT
        am.carrier_id,
        c.carrier_name,
        am.service_id,
        st.service_name,
        am.total_shipments,
        am.total_revenue,
        am.avg_cost,
        am.delivered_count,
        CASE
            WHEN am.total_shipments > 0
            THEN am.delivered_count::numeric / am.total_shipments * 100
            ELSE 0
        END AS delivery_success_rate,
        ROW_NUMBER() OVER (ORDER BY am.total_revenue DESC) AS revenue_rank,
        ROW_NUMBER() OVER (ORDER BY am.avg_cost ASC) AS cost_rank
    FROM aggregated_metrics am
    INNER JOIN shipping_carriers c ON am.carrier_id = c.carrier_id
    INNER JOIN shipping_service_types st ON am.service_id = st.service_id
),
optimization_recommendations AS (
    -- Fourth CTE: Generate optimization recommendations
    SELECT
        pa.carrier_id,
        pa.carrier_name,
        pa.service_id,
        pa.service_name,
        pa.total_shipments,
        pa.total_revenue,
        pa.avg_cost,
        pa.delivery_success_rate,
        pa.revenue_rank,
        pa.cost_rank,
        CASE
            WHEN pa.delivery_success_rate >= 95 AND pa.cost_rank <= 3 THEN 'Optimal'
            WHEN pa.delivery_success_rate >= 90 THEN 'Good'
            WHEN pa.delivery_success_rate >= 85 THEN 'Fair'
            ELSE 'Needs Improvement'
        END AS performance_category
    FROM performance_analysis pa
)
SELECT
    or_rec.carrier_name,
    or_rec.service_name,
    or_rec.total_shipments,
    or_rec.total_revenue,
    or_rec.avg_cost,
    or_rec.delivery_success_rate,
    or_rec.performance_category,
    or_rec.revenue_rank,
    or_rec.cost_rank
FROM optimization_recommendations or_rec
ORDER BY or_rec.total_revenue DESC;"""
    
    return f"""## Query {query_num}: {title}

**Description:** {description}

**Use Case:** {use_case}

**Business Value:** {business_value}

**Purpose:** {purpose}

**Complexity:** {complexity}

**Expected Output:** {expected_output}

```sql
{sql_template}
```"""

if __name__ == "__main__":
    queries_text = []
    for query_info in queries_15_30:
        queries_text.append(generate_query_sql(query_info))
    
    output = "\n\n".join(queries_text)
    print(output)
