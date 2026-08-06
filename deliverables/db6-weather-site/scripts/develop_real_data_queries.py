#!/usr/bin/env python3
"""
Develop queries based on real extracted .gov data.
This script analyzes extracted data and generates queries that use actual data patterns.
"""
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import re

BASE = Path("/Users/machine/Documents/AQ/db")

def analyze_extracted_data(db_num):
    """Analyze extracted data to understand patterns."""
    research_dir = BASE / f"db-{db_num}" / "research"
    data_dir = BASE / f"db-{db_num}" / "data"
    
    # Check for extracted data files
    extracted_files = []
    if (research_dir / "opensky_extract.csv").exists():
        extracted_files.append(research_dir / "opensky_extract.csv")
    if (data_dir / "data_gov_extract.sql").exists():
        extracted_files.append(data_dir / "data_gov_extract.sql")
    
    analysis = {
        "database": f"db-{db_num}",
        "extracted_files": [str(f) for f in extracted_files],
        "data_patterns": {},
        "query_suggestions": []
    }
    
    # Analyze CSV if exists
    for file_path in extracted_files:
        if file_path.suffix == '.csv':
            try:
                df = pd.read_csv(file_path)
                analysis["data_patterns"][file_path.name] = {
                    "row_count": len(df),
                    "columns": list(df.columns),
                    "date_range": None,
                    "numeric_ranges": {}
                }
                
                # Analyze numeric columns
                for col in df.columns:
                    if df[col].dtype in ['int64', 'float64']:
                        analysis["data_patterns"][file_path.name]["numeric_ranges"][col] = {
                            "min": float(df[col].min()),
                            "max": float(df[col].max()),
                            "mean": float(df[col].mean()),
                            "std": float(df[col].std())
                        }
                
                # Analyze date columns
                for col in df.columns:
                    if 'date' in col.lower() or 'time' in col.lower():
                        try:
                            df[col] = pd.to_datetime(df[col])
                            analysis["data_patterns"][file_path.name]["date_range"] = {
                                "min": str(df[col].min()),
                                "max": str(df[col].max())
                            }
                        except:
                            pass
                
                # Generate query suggestions based on data
                if 'altitude' in df.columns:
                    analysis["query_suggestions"].append({
                        "type": "altitude_analysis",
                        "description": "Analyze altitude distributions and patterns",
                        "columns": ["altitude", "hex", "timestamp"]
                    })
                
                if 'speed' in df.columns and 'track' in df.columns:
                    analysis["query_suggestions"].append({
                        "type": "movement_analysis",
                        "description": "Analyze aircraft speed and direction patterns",
                        "columns": ["speed", "track", "lat", "lon"]
                    })
                
            except Exception as e:
                analysis["errors"] = str(e)
    
    return analysis

def generate_real_data_query(db_num, query_type, analysis):
    """Generate a query based on real data patterns."""
    
    if db_num == 1:  # Airplane Tracking
        if query_type == "altitude_analysis":
            return """
-- Query: Real-Time Altitude Distribution Analysis
-- Based on OpenSky Network extracted data
-- Analyzes altitude patterns from actual aircraft tracking data

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
        
        elif query_type == "movement_analysis":
            return """
-- Query: Aircraft Movement Pattern Analysis
-- Based on OpenSky Network extracted data
-- Analyzes speed, track, and geographic movement patterns

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
    
    return None

def main():
    """Main analysis and query generation."""
    print("=" * 70)
    print("Developing Queries Based on Real Extracted Data")
    print("=" * 70)
    
    for db_num in [1, 2, 3, 4, 5]:
        print(f"\nAnalyzing db-{db_num}...")
        analysis = analyze_extracted_data(db_num)
        
        # Save analysis
        analysis_file = BASE / f"db-{db_num}" / "research" / "data_analysis.json"
        analysis_file.write_text(json.dumps(analysis, indent=2))
        print(f"✅ Analysis saved to {analysis_file.name}")
        
        # Generate queries based on analysis
        if analysis.get("query_suggestions"):
            print(f"  Found {len(analysis['query_suggestions'])} query suggestions")
            for suggestion in analysis["query_suggestions"]:
                query = generate_real_data_query(db_num, suggestion["type"], analysis)
                if query:
                    print(f"  ✅ Generated {suggestion['type']} query")
    
    print("\n" + "=" * 70)
    print("Query Development Complete")
    print("=" * 70)

if __name__ == '__main__':
    main()
