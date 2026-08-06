#!/usr/bin/env python3
"""
Identify and catalog .gov and reputable data sources for each database.
This script researches and documents available data sources.
"""
import json
from pathlib import Path
from datetime import datetime

BASE = Path("/Users/machine/Documents/AQ/db")

# Comprehensive .gov and reputable data sources by database
GOV_DATA_SOURCES = {
    1: {  # Airplane Tracking
        "name": "Airplane Tracking",
        "sources": [
            {
                "name": "FAA Aircraft Registry",
                "url": "https://registry.faa.gov/aircraftinquiry/",
                "type": "government",
                "description": "Official FAA aircraft registration database",
                "data_types": ["aircraft_registration", "ownership", "airworthiness"],
                "access": "web_scraping",
                "rate_limit": "Respectful scraping",
                "update_frequency": "Daily"
            },
            {
                "name": "FAA Airport Data",
                "url": "https://www.faa.gov/airports/airport_safety/airportdata_5010",
                "type": "government",
                "description": "Airport information and statistics",
                "data_types": ["airport_info", "runway_data", "airport_statistics"],
                "access": "download",
                "rate_limit": "None",
                "update_frequency": "Monthly"
            },
            {
                "name": "FAA Flight Data",
                "url": "https://www.faa.gov/data_research/aviation_data_statistics/",
                "type": "government",
                "description": "Aviation statistics and flight data",
                "data_types": ["flight_statistics", "traffic_data", "safety_data"],
                "access": "download",
                "rate_limit": "None",
                "update_frequency": "Monthly"
            },
            {
                "name": "BTS Airline On-Time Performance",
                "url": "https://www.transtats.bts.gov/",
                "type": "government",
                "description": "Bureau of Transportation Statistics airline on-time data",
                "data_types": ["flight_delays", "on_time_performance", "cancellations"],
                "access": "download",
                "rate_limit": "None",
                "update_frequency": "Monthly"
            },
            {
                "name": "NASA Aviation Safety Reporting System",
                "url": "https://asrs.arc.nasa.gov/",
                "type": "government",
                "description": "Aviation safety incident reports",
                "data_types": ["safety_reports", "incidents", "near_misses"],
                "access": "download",
                "rate_limit": "None",
                "update_frequency": "Quarterly"
            },
            {
                "name": "OpenSky Network API",
                "url": "https://opensky-network.org/API",
                "type": "academic",
                "description": "Real-time and historical flight tracking (ETH Zurich)",
                "data_types": ["real_time_tracking", "historical_flights", "aircraft_states"],
                "access": "api",
                "rate_limit": "Unlimited (public)",
                "update_frequency": "Real-time"
            }
        ]
    },
    2: {  # Filling Station POS
        "name": "Filling Station POS",
        "sources": [
            {
                "name": "EIA Petroleum Price Data",
                "url": "https://www.eia.gov/petroleum/data.php",
                "type": "government",
                "description": "Energy Information Administration petroleum price data",
                "data_types": ["gasoline_prices", "diesel_prices", "crude_oil_prices"],
                "access": "api_download",
                "rate_limit": "5000 requests/day",
                "update_frequency": "Weekly"
            },
            {
                "name": "Alternative Fuel Data Center",
                "url": "https://afdc.energy.gov/data_download",
                "type": "government",
                "description": "DOE Alternative Fuel Data Center station locations",
                "data_types": ["station_locations", "fuel_types", "station_info"],
                "access": "download",
                "rate_limit": "None",
                "update_frequency": "Monthly"
            },
            {
                "name": "BLS Consumer Price Index - Gasoline",
                "url": "https://www.bls.gov/data/",
                "type": "government",
                "description": "Bureau of Labor Statistics CPI for gasoline",
                "data_types": ["price_indices", "inflation_data"],
                "access": "download",
                "rate_limit": "None",
                "update_frequency": "Monthly"
            },
            {
                "name": "Census Business Patterns - Gas Stations",
                "url": "https://www.census.gov/data/developers/data-sets/cbp-nonemp.html",
                "type": "government",
                "description": "Census business statistics for gas stations",
                "data_types": ["business_counts", "employment", "revenue"],
                "access": "api",
                "rate_limit": "None",
                "update_frequency": "Annual"
            },
            {
                "name": "FHWA Highway Statistics",
                "url": "https://www.fhwa.dot.gov/policyinformation/statistics.cfm",
                "type": "government",
                "description": "Federal Highway Administration traffic and fuel data",
                "data_types": ["traffic_volume", "fuel_consumption", "vehicle_miles"],
                "access": "download",
                "rate_limit": "None",
                "update_frequency": "Annual"
            }
        ]
    },
    3: {  # Linkway Ecommerce
        "name": "Linkway Ecommerce",
        "sources": [
            {
                "name": "Census E-Commerce Statistics",
                "url": "https://www.census.gov/data/tables/time-series/econ/e-stats.html",
                "type": "government",
                "description": "Census Bureau e-commerce statistics",
                "data_types": ["ecommerce_sales", "online_retail", "digital_commerce"],
                "access": "download",
                "rate_limit": "None",
                "update_frequency": "Quarterly"
            },
            {
                "name": "BLS Consumer Expenditure Survey",
                "url": "https://www.bls.gov/cex/",
                "type": "government",
                "description": "Consumer spending patterns and e-commerce",
                "data_types": ["consumer_spending", "purchase_patterns"],
                "access": "download",
                "rate_limit": "None",
                "update_frequency": "Annual"
            },
            {
                "name": "USPS Shipping Data",
                "url": "https://www.usps.com/business/web-tools-apis/",
                "type": "government",
                "description": "USPS shipping rates and tracking",
                "data_types": ["shipping_rates", "delivery_times", "tracking"],
                "access": "api",
                "rate_limit": "Varies",
                "update_frequency": "Real-time"
            },
            {
                "name": "Census Retail Trade",
                "url": "https://www.census.gov/retail/",
                "type": "government",
                "description": "Retail trade statistics including e-commerce",
                "data_types": ["retail_sales", "ecommerce_growth"],
                "access": "download",
                "rate_limit": "None",
                "update_frequency": "Monthly"
            }
        ]
    },
    4: {  # Seydam AI
        "name": "Seydam AI",
        "sources": [
            {
                "name": "NIST AI Risk Management Framework",
                "url": "https://www.nist.gov/itl/ai-risk-management-framework",
                "type": "government",
                "description": "NIST AI standards and frameworks",
                "data_types": ["ai_standards", "risk_frameworks", "best_practices"],
                "access": "download",
                "rate_limit": "None",
                "update_frequency": "Periodic"
            },
            {
                "name": "NSF AI Research Data",
                "url": "https://www.nsf.gov/statistics/",
                "type": "government",
                "description": "NSF research data on AI and machine learning",
                "data_types": ["research_data", "publications", "grants"],
                "access": "download",
                "rate_limit": "None",
                "update_frequency": "Ongoing"
            },
            {
                "name": "Data.gov AI Datasets",
                "url": "https://catalog.data.gov/dataset?tags=artificial-intelligence",
                "type": "government",
                "description": "Federal AI-related datasets",
                "data_types": ["ai_datasets", "ml_models", "training_data"],
                "access": "api_download",
                "rate_limit": "1000 req/hour",
                "update_frequency": "Varies"
            },
            {
                "name": "NIST Computer Security Resource Center",
                "url": "https://csrc.nist.gov/",
                "type": "government",
                "description": "AI security standards and guidelines",
                "data_types": ["security_standards", "vulnerabilities", "best_practices"],
                "access": "download",
                "rate_limit": "None",
                "update_frequency": "Periodic"
            }
        ]
    },
    5: {  # SharedAI
        "name": "SharedAI",
        "sources": [
            {
                "name": "Data.gov Social Media Datasets",
                "url": "https://catalog.data.gov/dataset?tags=social-media",
                "type": "government",
                "description": "Federal social media and communication datasets",
                "data_types": ["social_media_data", "communication_patterns"],
                "access": "api_download",
                "rate_limit": "1000 req/hour",
                "update_frequency": "Varies"
            },
            {
                "name": "Census Communication Statistics",
                "url": "https://www.census.gov/data/tables.html",
                "type": "government",
                "description": "Communication and internet usage statistics",
                "data_types": ["internet_usage", "communication_trends"],
                "access": "download",
                "rate_limit": "None",
                "update_frequency": "Annual"
            },
            {
                "name": "FCC Broadband Data",
                "url": "https://www.fcc.gov/general/broadband-deployment-data-fcc-form-477",
                "type": "government",
                "description": "FCC broadband deployment and usage data",
                "data_types": ["broadband_access", "internet_speeds", "coverage"],
                "access": "download",
                "rate_limit": "None",
                "update_frequency": "Semi-annual"
            },
            {
                "name": "NTIA Internet Use Survey",
                "url": "https://www.ntia.gov/data/internet-use-survey",
                "type": "government",
                "description": "NTIA internet and digital communication usage",
                "data_types": ["internet_usage", "digital_communication", "user_behavior"],
                "access": "download",
                "rate_limit": "None",
                "update_frequency": "Biannual"
            }
        ]
    }
}

def update_data_resources(db_num: int):
    """Update data_resources.json with comprehensive .gov sources."""
    research_dir = BASE / f"db-{db_num}" / "research"
    research_dir.mkdir(parents=True, exist_ok=True)
    
    resources_file = research_dir / "data_resources.json"
    
    # Load existing or create new
    if resources_file.exists():
        existing = json.loads(resources_file.read_text())
    else:
        existing = {
            "database": f"db-{db_num}",
            "name": "",
            "apis": [],
            "data_sources": [],
            "last_updated": ""
        }
    
    # Update with comprehensive sources
    db_info = GOV_DATA_SOURCES[db_num]
    existing["name"] = db_info["name"]
    existing["last_updated"] = datetime.now().isoformat()
    
    # Add .gov sources
    existing["gov_sources"] = db_info["sources"]
    
    # Keep existing APIs if they exist
    if "apis" not in existing or not existing["apis"]:
        existing["apis"] = []
    
    # Write updated resources
    resources_file.write_text(json.dumps(existing, indent=2))
    print(f"✅ db-{db_num}: Updated data_resources.json with {len(db_info['sources'])} .gov sources")

def main():
    """Update all databases with comprehensive .gov data sources."""
    print("=" * 70)
    print("Identifying and Cataloging .gov Data Sources")
    print("=" * 70)
    
    for db_num in [1, 2, 3, 4, 5]:
        update_data_resources(db_num)
    
    print("\n" + "=" * 70)
    print("Completed: All databases updated with .gov data sources")
    print("=" * 70)

if __name__ == '__main__':
    main()
