#!/usr/bin/env python3
"""
Generate remaining queries 4-30 for db-7 maritime shipping intelligence
This script generates query templates that can be customized
"""

# Query templates with placeholders
query_templates = {
    4: {
        "title": "Carrier Performance Metrics with On-Time Performance Analysis",
        "use_case": "Carrier Selection - Comprehensive Carrier Performance Analysis with On-Time Performance Metrics for Shipping Line Evaluation",
        "description": "Enterprise-level carrier performance analysis with multi-level CTE nesting, on-time performance calculations, vessel utilization metrics, capacity analysis, and advanced window functions.",
        "business_value": "Carrier performance report showing on-time rates, vessel utilization, capacity metrics, and reliability scores. Helps shippers evaluate carriers and make informed shipping decisions.",
        "purpose": "Provides comprehensive carrier intelligence by analyzing performance metrics, calculating reliability scores, and enabling data-driven carrier selection.",
        "complexity": "Deep nested CTEs (7+ levels), temporal analysis, performance scoring, window functions with multiple frame clauses, percentile calculations, multi-metric aggregation"
    },
    5: {
        "title": "Port Statistics Aggregation with Throughput Analysis",
        "use_case": "Port Operations Management - Comprehensive Port Statistics Aggregation with Throughput Analysis for Terminal Planning",
        "description": "Enterprise-level port statistics aggregation with multi-level CTE nesting, throughput calculations, vessel call analysis, container flow metrics, and advanced window functions.",
        "business_value": "Port statistics report showing vessel calls, container throughput, berth utilization, and operational efficiency metrics. Helps port operators optimize terminal operations and plan capacity.",
        "purpose": "Provides comprehensive port intelligence by aggregating statistics, analyzing throughput patterns, and enabling data-driven port operations optimization.",
        "complexity": "Deep nested CTEs (7+ levels), temporal aggregation, throughput calculations, window functions with multiple frame clauses, percentile calculations, efficiency metrics"
    },
    6: {
        "title": "Sailing Capacity Utilization Analysis",
        "use_case": "Fleet Optimization - Comprehensive Sailing Capacity Utilization Analysis for Vessel Deployment Planning",
        "description": "Enterprise-level sailing capacity utilization analysis with multi-level CTE nesting, capacity calculations, utilization scoring, route analysis, and advanced window functions.",
        "business_value": "Capacity utilization report showing vessel utilization rates, route efficiency, and optimization opportunities. Helps shipping lines optimize fleet deployment and maximize capacity utilization.",
        "purpose": "Provides comprehensive capacity intelligence by analyzing utilization rates, identifying optimization opportunities, and enabling data-driven fleet deployment decisions.",
        "complexity": "Deep nested CTEs (7+ levels), capacity calculations, utilization scoring, window functions with multiple frame clauses, percentile calculations, route analysis"
    },
    7: {
        "title": "Multi-Port Route Analysis with Transshipment Detection",
        "use_case": "Route Planning - Comprehensive Multi-Port Route Analysis with Transshipment Detection for Logistics Optimization",
        "description": "Enterprise-level multi-port route analysis with recursive CTE traversal, transshipment detection, route path analysis, and advanced window functions.",
        "business_value": "Multi-port route report showing route paths, transshipment points, and connectivity analysis. Helps logistics companies optimize multi-port routes and identify transshipment opportunities.",
        "purpose": "Provides comprehensive route intelligence by analyzing multi-port routes, detecting transshipments, and enabling data-driven route planning decisions.",
        "complexity": "Recursive CTE with route traversal, transshipment detection, path analysis, window functions with multiple frame clauses, connectivity calculations"
    },
    8: {
        "title": "Vessel Utilization Analysis Across Carriers",
        "use_case": "Fleet Management - Comprehensive Vessel Utilization Analysis Across Carriers for Fleet Optimization",
        "description": "Enterprise-level vessel utilization analysis with multi-level CTE nesting, utilization calculations, carrier comparisons, and advanced window functions.",
        "business_value": "Vessel utilization report showing utilization rates across carriers, vessel performance, and optimization opportunities. Helps shipping lines optimize vessel deployment and improve utilization.",
        "purpose": "Provides comprehensive vessel intelligence by analyzing utilization rates, comparing carrier performance, and enabling data-driven fleet optimization decisions.",
        "complexity": "Deep nested CTEs (7+ levels), utilization calculations, carrier comparisons, window functions with multiple frame clauses, percentile calculations, performance metrics"
    },
    9: {
        "title": "Port Pair Demand Analysis",
        "use_case": "Market Analysis - Comprehensive Port Pair Demand Analysis for Trade Flow Intelligence",
        "description": "Enterprise-level port pair demand analysis with multi-level CTE nesting, demand calculations, trade flow analysis, and advanced window functions.",
        "business_value": "Port pair demand report showing trade volumes, demand trends, and market opportunities. Helps shipping lines identify high-demand routes and optimize service offerings.",
        "purpose": "Provides comprehensive demand intelligence by analyzing port pair volumes, identifying trends, and enabling data-driven service planning decisions.",
        "complexity": "Deep nested CTEs (7+ levels), demand calculations, trend analysis, window functions with multiple frame clauses, percentile calculations, market analysis"
    },
    10: {
        "title": "Voyage Completion Rate Analysis",
        "use_case": "Operational Excellence - Comprehensive Voyage Completion Rate Analysis for Service Reliability",
        "description": "Enterprise-level voyage completion rate analysis with multi-level CTE nesting, completion calculations, reliability scoring, and advanced window functions.",
        "business_value": "Voyage completion report showing completion rates, reliability metrics, and service quality indicators. Helps shipping lines improve service reliability and customer satisfaction.",
        "purpose": "Provides comprehensive voyage intelligence by analyzing completion rates, calculating reliability scores, and enabling data-driven service improvement decisions.",
        "complexity": "Deep nested CTEs (7+ levels), completion rate calculations, reliability scoring, window functions with multiple frame clauses, percentile calculations, service metrics"
    }
}

print("Query templates defined for queries 4-10")
print(f"Total templates: {len(query_templates)}")
