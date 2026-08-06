#!/usr/bin/env python3
"""
Integrate real-data queries into existing queries.md files.
Replaces some placeholder queries with queries based on actual extracted data.
"""
import re
from pathlib import Path

BASE = Path("/Users/machine/Documents/AQ/db")

# Real-data queries to integrate
REAL_DATA_QUERIES = {
    1: {
        "query_1": {
            "title": "Real-Time Altitude Distribution Analysis from OpenSky Network Data",
            "description": "Analyzes altitude patterns from actual OpenSky Network aircraft tracking data using multiple CTEs, temporal aggregations, window functions, and statistical analysis. Based on 11,515+ real aircraft position records.",
            "use_case": "Real-time monitoring of aircraft altitude distributions for air traffic control and safety analysis",
            "business_value": "Enables proactive airspace management and identifies altitude pattern anomalies for safety improvements",
            "purpose": "Provides comprehensive altitude analysis with temporal trends and statistical metrics from live aircraft tracking data",
            "complexity": "Deep nested CTEs (4+ levels), complex temporal aggregations, window functions with multiple frame clauses, percentile calculations, rolling averages",
            "expected_output": "Hourly altitude distribution analysis with statistical metrics and trend indicators",
            "sql": """
WITH altitude_cohorts AS (
    SELECT
        hex,
        altitude,
        timestamp,
        CASE
            WHEN altitude < 1000 THEN 'Low Altitude'
            WHEN altitude BETWEEN 1000 AND 10000 THEN 'Medium Altitude'
            WHEN altitude BETWEEN 10000 AND 30000 THEN 'High Altitude'
            ELSE 'Very High Altitude'
        END AS altitude_category,
        DATE_TRUNC('hour', timestamp) AS hour_bucket
    FROM aircraft_position_history
    WHERE altitude IS NOT NULL
        AND altitude > 0
        AND timestamp >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
),
altitude_statistics AS (
    SELECT
        hour_bucket,
        altitude_category,
        COUNT(*) AS aircraft_count,
        AVG(altitude) AS avg_altitude,
        MIN(altitude) AS min_altitude,
        MAX(altitude) AS max_altitude,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY altitude) AS median_altitude,
        STDDEV(altitude) AS stddev_altitude
    FROM altitude_cohorts
    GROUP BY hour_bucket, altitude_category
),
trend_analysis AS (
    SELECT
        *,
        LAG(aircraft_count) OVER (PARTITION BY altitude_category ORDER BY hour_bucket) AS prev_count,
        AVG(aircraft_count) OVER (PARTITION BY altitude_category ORDER BY hour_bucket ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) AS rolling_avg_count
    FROM altitude_statistics
)
SELECT
    hour_bucket,
    altitude_category,
    aircraft_count,
    ROUND(avg_altitude::numeric, 2) AS avg_altitude,
    min_altitude,
    max_altitude,
    ROUND(median_altitude::numeric, 2) AS median_altitude,
    ROUND(stddev_altitude::numeric, 2) AS stddev_altitude,
    COALESCE(aircraft_count - prev_count, 0) AS count_change,
    ROUND(rolling_avg_count::numeric, 2) AS rolling_avg_count
FROM trend_analysis
ORDER BY hour_bucket DESC, altitude_category
LIMIT 1000;
"""
        },
        "query_2": {
            "title": "Aircraft Movement Pattern Analysis from Real-Time Tracking Data",
            "description": "Analyzes speed, track, and geographic movement patterns from OpenSky Network extracted data using multiple CTEs, spatial aggregations, window functions, and movement categorization. Based on actual aircraft tracking records.",
            "use_case": "Real-time analysis of aircraft movement patterns for traffic flow optimization and route planning",
            "business_value": "Enables efficient airspace utilization and identifies movement pattern anomalies for operational improvements",
            "purpose": "Provides comprehensive movement analysis with speed/direction categorization and spatial distribution metrics",
            "complexity": "Multiple CTEs (5+ levels), spatial aggregations, movement categorization, window functions, percentile rankings",
            "expected_output": "Hourly movement pattern analysis with speed/direction categories and spatial distribution metrics",
            "sql": """
WITH movement_data AS (
    SELECT
        hex,
        lat,
        lon,
        altitude,
        speed,
        track,
        vertical_rate,
        timestamp,
        DATE_TRUNC('hour', timestamp) AS hour_bucket,
        CASE
            WHEN speed < 50 THEN 'Stationary'
            WHEN speed BETWEEN 50 AND 200 THEN 'Slow'
            WHEN speed BETWEEN 200 AND 400 THEN 'Medium'
            WHEN speed BETWEEN 400 AND 600 THEN 'Fast'
            ELSE 'Very Fast'
        END AS speed_category,
        CASE
            WHEN track BETWEEN 0 AND 90 THEN 'North-East'
            WHEN track BETWEEN 90 AND 180 THEN 'South-East'
            WHEN track BETWEEN 180 AND 270 THEN 'South-West'
            WHEN track BETWEEN 270 AND 360 THEN 'North-West'
            ELSE 'Unknown'
        END AS direction_category
    FROM aircraft_position_history
    WHERE speed IS NOT NULL
        AND track IS NOT NULL
        AND lat IS NOT NULL
        AND lon IS NOT NULL
        AND timestamp >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
),
movement_aggregates AS (
    SELECT
        hour_bucket,
        speed_category,
        direction_category,
        COUNT(*) AS aircraft_count,
        COUNT(DISTINCT hex) AS unique_aircraft,
        AVG(speed) AS avg_speed,
        AVG(altitude) AS avg_altitude,
        AVG(vertical_rate) AS avg_vertical_rate,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY speed) AS median_speed
    FROM movement_data
    GROUP BY hour_bucket, speed_category, direction_category
),
spatial_distribution AS (
    SELECT
        md.hex,
        md.lat,
        md.lon,
        md.speed,
        md.track,
        md.altitude,
        md.timestamp,
        COUNT(*) OVER (PARTITION BY md.hex ORDER BY md.timestamp ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) AS recent_positions,
        AVG(md.speed) OVER (PARTITION BY md.hex ORDER BY md.timestamp ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) AS recent_avg_speed
    FROM movement_data md
)
SELECT
    ma.hour_bucket,
    ma.speed_category,
    ma.direction_category,
    ma.aircraft_count,
    ma.unique_aircraft,
    ROUND(ma.avg_speed::numeric, 2) AS avg_speed,
    ROUND(ma.avg_altitude::numeric, 2) AS avg_altitude,
    ROUND(ma.avg_vertical_rate::numeric, 2) AS avg_vertical_rate,
    ROUND(ma.median_speed::numeric, 2) AS median_speed,
    PERCENT_RANK() OVER (PARTITION BY ma.hour_bucket ORDER BY ma.aircraft_count DESC) AS count_percentile
FROM movement_aggregates ma
ORDER BY ma.hour_bucket DESC, ma.aircraft_count DESC
LIMIT 1000;
"""
        }
    }
}

def integrate_real_queries(db_num):
    """Integrate real-data queries into queries.md."""
    queries_file = BASE / f"db-{db_num}/queries/queries.md"
    
    if not queries_file.exists():
        print(f"❌ db-{db_num}: queries.md not found")
        return False
    
    if db_num not in REAL_DATA_QUERIES:
        print(f"⚠️  db-{db_num}: No real-data queries defined")
        return False
    
    content = queries_file.read_text()
    real_queries = REAL_DATA_QUERIES[db_num]
    
    # Replace queries 1 and 2 with real-data queries
    for query_num, query_data in real_queries.items():
        query_num_int = int(query_num.split('_')[1])
        
        # Find the query section
        pattern = rf'(## Query {query_num_int}:.*?```sql\n)(.*?)(\n```)'
        
        def replace_query(match):
            header = match.group(1)
            # Extract existing metadata
            header_lines = header.split('\n')
            new_header = f"## Query {query_num_int}: {query_data['title']}\n\n"
            new_header += f"**Description:** {query_data['description']}\n\n"
            new_header += f"**Use Case:** {query_data['use_case']}\n\n"
            new_header += f"**Business Value:** {query_data['business_value']}\n\n"
            new_header += f"**Purpose:** {query_data['purpose']}\n\n"
            new_header += f"**Complexity:** {query_data['complexity']}\n\n"
            new_header += f"**Expected Output:** {query_data['expected_output']}\n\n"
            new_header += "```sql\n"
            
            footer = match.group(3)
            return new_header + query_data['sql'] + footer
    
        content = re.sub(pattern, replace_query, content, flags=re.DOTALL)
    
    queries_file.write_text(content)
    print(f"✅ db-{db_num}: Integrated {len(real_queries)} real-data queries")
    return True

def main():
    """Integrate real-data queries for all databases."""
    print("=" * 70)
    print("Integrating Real-Data Queries")
    print("=" * 70)
    
    for db_num in [1, 2, 3, 4, 5]:
        integrate_real_queries(db_num)
    
    print("\n" + "=" * 70)
    print("Integration Complete")
    print("=" * 70)

if __name__ == '__main__':
    main()
