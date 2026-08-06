#!/usr/bin/env python3
"""
Generate large dataset for db-16 to reach ~2 GB
Creates realistic flood risk assessment data across all tables
"""

import random
from pathlib import Path
from datetime import datetime, timedelta

def generate_fema_flood_zones(count=5000):
    """Generate FEMA flood zones"""
    zones = []
    zone_codes = ['A', 'AE', 'AH', 'AO', 'V', 'VE', 'X', 'D']
    states = ['NY', 'CA', 'IL', 'FL', 'WA', 'TX', 'LA', 'NC', 'SC', 'GA', 'VA', 'MD', 'NJ', 'MA', 'CT', 'RI', 'NH', 'ME', 'OR', 'HI']
    
    for i in range(1, count + 1):
        state = random.choice(states)
        zone_code = random.choice(zone_codes)
        bfe = random.uniform(5.0, 25.0) if zone_code in ['AE', 'VE'] else None
        
        # Generate realistic coordinates for each state
        lat_base = {
            'NY': 40.7, 'CA': 34.0, 'IL': 41.9, 'FL': 25.8, 'WA': 47.6,
            'TX': 29.8, 'LA': 30.2, 'NC': 35.2, 'SC': 33.0, 'GA': 33.7,
            'VA': 37.5, 'MD': 39.0, 'NJ': 40.2, 'MA': 42.2, 'CT': 41.6,
            'RI': 41.8, 'NH': 43.2, 'ME': 44.3, 'OR': 45.5, 'HI': 21.3
        }
        lon_base = {
            'NY': -74.0, 'CA': -118.2, 'IL': -87.6, 'FL': -80.1, 'WA': -122.3,
            'TX': -95.4, 'LA': -91.2, 'NC': -79.0, 'SC': -80.9, 'GA': -84.4,
            'VA': -78.2, 'MD': -76.6, 'NJ': -74.4, 'MA': -71.0, 'CT': -72.7,
            'RI': -71.4, 'NH': -71.5, 'ME': -69.8, 'OR': -122.7, 'HI': -157.8
        }
        
        lat = lat_base.get(state, 40.0) + random.uniform(-0.5, 0.5)
        lon = lon_base.get(state, -74.0) + random.uniform(-0.5, 0.5)
        
        zones.append(f"('fz_{i:06d}', '{zone_code}', 'Flood Zone {zone_code}', {bfe if bfe else 'NULL'}, 'comm_{i:04d}', 'Community {i}', '{state}', '{state}{random.randint(1, 999):03d}', '2020-01-01', 'panel_{i:04d}', 'nfhl_{state}.shp', 'EPSG:4326', 'EPSG:4326', {lon - 0.1:.6f}, {lat - 0.1:.6f}, {lon + 0.1:.6f}, {lat + 0.1:.6f}, 'Success')")
    
    return zones

def generate_properties(count=200000):
    """Generate real estate properties"""
    properties = []
    property_types = ['Residential', 'Commercial', 'Industrial', 'Mixed-Use']
    states = ['NY', 'CA', 'IL', 'FL', 'WA', 'TX', 'LA', 'NC', 'SC', 'GA', 'VA', 'MD', 'NJ', 'MA', 'CT', 'RI', 'NH', 'ME', 'OR', 'HI']
    cities = {
        'NY': ['New York', 'Buffalo', 'Rochester'], 'CA': ['Los Angeles', 'San Francisco', 'San Diego'],
        'IL': ['Chicago', 'Aurora', 'Naperville'], 'FL': ['Miami', 'Tampa', 'Orlando'],
        'WA': ['Seattle', 'Spokane', 'Tacoma'], 'TX': ['Houston', 'Dallas', 'Austin'],
        'LA': ['New Orleans', 'Baton Rouge', 'Shreveport'], 'NC': ['Charlotte', 'Raleigh', 'Greensboro'],
        'SC': ['Charleston', 'Columbia', 'Greenville'], 'GA': ['Atlanta', 'Savannah', 'Augusta'],
        'VA': ['Virginia Beach', 'Norfolk', 'Richmond'], 'MD': ['Baltimore', 'Annapolis', 'Frederick'],
        'NJ': ['Newark', 'Jersey City', 'Paterson'], 'MA': ['Boston', 'Worcester', 'Springfield'],
        'CT': ['Hartford', 'New Haven', 'Stamford'], 'RI': ['Providence', 'Warwick', 'Cranston'],
        'NH': ['Manchester', 'Nashua', 'Concord'], 'ME': ['Portland', 'Lewiston', 'Bangor'],
        'OR': ['Portland', 'Eugene', 'Salem'], 'HI': ['Honolulu', 'Hilo', 'Kailua']
    }
    
    for i in range(1, count + 1):
        state = random.choice(states)
        city = random.choice(cities.get(state, ['City']))
        prop_type = random.choice(property_types)
        
        lat_base = {
            'NY': 40.7, 'CA': 34.0, 'IL': 41.9, 'FL': 25.8, 'WA': 47.6,
            'TX': 29.8, 'LA': 30.2, 'NC': 35.2, 'SC': 33.0, 'GA': 33.7,
            'VA': 37.5, 'MD': 39.0, 'NJ': 40.2, 'MA': 42.2, 'CT': 41.6,
            'RI': 41.8, 'NH': 43.2, 'ME': 44.3, 'OR': 45.5, 'HI': 21.3
        }
        lon_base = {
            'NY': -74.0, 'CA': -118.2, 'IL': -87.6, 'FL': -80.1, 'WA': -122.3,
            'TX': -95.4, 'LA': -91.2, 'NC': -79.0, 'SC': -80.9, 'GA': -84.4,
            'VA': -78.2, 'MD': -76.6, 'NJ': -74.4, 'MA': -71.0, 'CT': -72.7,
            'RI': -71.4, 'NH': -71.5, 'ME': -69.8, 'OR': -122.7, 'HI': -157.8
        }
        
        lat = lat_base.get(state, 40.0) + random.uniform(-0.5, 0.5)
        lon = lon_base.get(state, -74.0) + random.uniform(-0.5, 0.5)
        
        if prop_type == 'Residential':
            building_value = random.uniform(200000, 5000000)
            sqft = random.uniform(1000, 5000)
            floors = random.randint(1, 3)
        elif prop_type == 'Commercial':
            building_value = random.uniform(1000000, 20000000)
            sqft = random.uniform(5000, 100000)
            floors = random.randint(2, 30)
        elif prop_type == 'Industrial':
            building_value = random.uniform(2000000, 50000000)
            sqft = random.uniform(10000, 500000)
            floors = random.randint(1, 10)
        else:  # Mixed-Use
            building_value = random.uniform(500000, 15000000)
            sqft = random.uniform(3000, 75000)
            floors = random.randint(2, 20)
        
        land_value = building_value * random.uniform(0.2, 0.5)
        total_value = building_value + land_value
        elevation = random.uniform(0.0, 600.0)
        year_built = random.randint(1900, 2024)
        portfolio_id = f"port_{random.randint(1, 100):03d}"
        portfolio_name = f"Portfolio {random.randint(1, 100)}"
        acquisition_date = datetime(2010, 1, 1) + timedelta(days=random.randint(0, 5000))
        
        properties.append(f"('prop_{i:06d}', '{i} Main St, {city}, {state} {random.randint(10000, 99999)}', {lat:.7f}, {lon:.7f}, '{prop_type}', {building_value:.2f}, {land_value:.2f}, {total_value:.2f}, {sqft:.2f}, {year_built}, {floors}, {elevation:.2f}, '{state}', '{state}{random.randint(1, 999):03d}', '{city}', '{random.randint(10000, 99999)}', '{portfolio_id}', '{portfolio_name}', '{acquisition_date.date()}')")
    
    return properties

def generate_slr_projections(count=10000):
    """Generate NOAA sea level rise projections"""
    projections = []
    stations = [
        ('8518750', 'The Battery, NY', 40.7006, -74.0141),
        ('9410660', 'Los Angeles', 33.7194, -118.2728),
        ('8724580', 'Miami Beach', 25.7617, -80.1318),
        ('9447130', 'Seattle', 47.6062, -122.3394),
        ('8779770', 'Galveston, TX', 29.3014, -94.7977),
        ('8761724', 'New Orleans, LA', 29.9333, -90.0667),
        ('8658120', 'Wilmington, NC', 34.2278, -77.9536),
        ('8665530', 'Charleston, SC', 32.7817, -79.9247),
        ('8670870', 'Fort Pulaski, GA', 32.0333, -80.9000),
        ('8638610', 'Norfolk, VA', 36.9467, -76.3300)
    ]
    scenarios = ['Low', 'Intermediate-Low', 'Intermediate', 'Intermediate-High', 'High', 'Extreme']
    years = [2030, 2040, 2050, 2060, 2070, 2080, 2090, 2100]
    
    for i in range(1, count + 1):
        station_id, station_name, lat, lon = random.choice(stations)
        year = random.choice(years)
        scenario = random.choice(scenarios)
        
        # Base SLR values by scenario and year
        base_slr = {
            'Low': year * 0.01,
            'Intermediate-Low': year * 0.015,
            'Intermediate': year * 0.02,
            'Intermediate-High': year * 0.025,
            'High': year * 0.03,
            'Extreme': year * 0.04
        }
        slr_feet = base_slr.get(scenario, 0.5) + random.uniform(-0.1, 0.1)
        htf_days = int(slr_feet * 50) + random.randint(-10, 10)
        confidence = random.choice(['Low', 'Medium', 'High'])
        
        projections.append(f"('slr_{i:06d}', '{station_id}', '{station_name}', {lat:.7f}, {lon:.7f}, {year}, '{scenario}', {slr_feet:.3f}, '{confidence}', {htf_days}, 'NOAA_CO-OPS')")
    
    return projections

def generate_streamflow_gauges(count=2000):
    """Generate USGS streamflow gauges"""
    gauges = []
    states = ['NY', 'CA', 'IL', 'FL', 'WA', 'TX', 'LA', 'NC', 'SC', 'GA', 'VA', 'MD', 'NJ', 'MA', 'CT', 'RI', 'NH', 'ME', 'OR', 'HI']
    rivers = ['River', 'Creek', 'Stream', 'Bayou', 'Bay', 'Harbor', 'Sound', 'Channel']
    
    for i in range(1, count + 1):
        state = random.choice(states)
        river_name = f"{random.choice(['Main', 'Big', 'Little', 'East', 'West', 'North', 'South', state])} {random.choice(rivers)}"
        
        lat_base = {
            'NY': 40.7, 'CA': 34.0, 'IL': 41.9, 'FL': 25.8, 'WA': 47.6,
            'TX': 29.8, 'LA': 30.2, 'NC': 35.2, 'SC': 33.0, 'GA': 33.7,
            'VA': 37.5, 'MD': 39.0, 'NJ': 40.2, 'MA': 42.2, 'CT': 41.6,
            'RI': 41.8, 'NH': 43.2, 'ME': 44.3, 'OR': 45.5, 'HI': 21.3
        }
        lon_base = {
            'NY': -74.0, 'CA': -118.2, 'IL': -87.6, 'FL': -80.1, 'WA': -122.3,
            'TX': -95.4, 'LA': -91.2, 'NC': -79.0, 'SC': -80.9, 'GA': -84.4,
            'VA': -78.2, 'MD': -76.6, 'NJ': -74.4, 'MA': -71.0, 'CT': -72.7,
            'RI': -71.4, 'NH': -71.5, 'ME': -69.8, 'OR': -122.7, 'HI': -157.8
        }
        
        lat = lat_base.get(state, 40.0) + random.uniform(-0.5, 0.5)
        lon = lon_base.get(state, -74.0) + random.uniform(-0.5, 0.5)
        
        gauge_id = f"{random.randint(1000000, 9999999)}"
        drainage_area = random.uniform(10.0, 50000.0)
        flood_stage = random.uniform(3.0, 15.0)
        moderate_stage = flood_stage * 1.4
        major_stage = flood_stage * 1.8
        first_obs = datetime(1950, 1, 1) + timedelta(days=random.randint(0, 25000))
        last_obs = datetime.now()
        
        gauges.append(f"('{gauge_id}', 'Gauge {i} on {river_name}', {lat:.7f}, {lon:.7f}, {drainage_area:.2f}, {flood_stage:.2f}, {moderate_stage:.2f}, {major_stage:.2f}, '{state}', 'County {i}', '{river_name}', TRUE, '{first_obs.date()}', '{last_obs.date()}', 15)")
    
    return gauges

def generate_streamflow_observations(count=3000000):
    """Generate USGS streamflow observations"""
    observations = []
    gauge_ids = [f"{random.randint(1000000, 9999999)}" for _ in range(5000)]
    
    start_date = datetime(2020, 1, 1)
    for i in range(1, count + 1):
        gauge_id = random.choice(gauge_ids)
        obs_time = start_date + timedelta(hours=random.randint(0, 52560))  # ~6 years
        
        stage = random.uniform(0.5, 20.0)
        discharge = stage ** 2.5 * random.uniform(100, 1000)
        
        if stage < 3.0:
            category = 'None'
            percentile = random.uniform(0, 30)
        elif stage < 6.0:
            category = random.choice(['None', 'Action', 'Minor'])
            percentile = random.uniform(30, 70)
        elif stage < 10.0:
            category = random.choice(['Minor', 'Moderate'])
            percentile = random.uniform(70, 90)
        else:
            category = random.choice(['Moderate', 'Major'])
            percentile = random.uniform(90, 99.9)
        
        observations.append(f"('obs_usgs_{i:06d}', '{gauge_id}', '{obs_time}', {stage:.2f}, {discharge:.2f}, {stage:.2f}, '{category}', {percentile:.2f}, 'A')")
    
    return observations

def generate_nasa_models(count=1500000):
    """Generate NASA flood model outputs"""
    models = []
    model_names = ['GFMS', 'LIS', 'VIIRS', 'MODIS', 'FloodPlanet']
    
    for i in range(1, count + 1):
        model_name = random.choice(model_names)
        forecast_time = datetime(2020, 1, 1) + timedelta(hours=random.randint(0, 52560))
        
        lat = random.uniform(24.0, 50.0)
        lon = random.uniform(-125.0, -66.0)
        
        prob = random.uniform(0, 100)
        if prob < 20:
            severity = 'Low'
            depth = random.uniform(0, 0.5)
        elif prob < 50:
            severity = 'Low'
            depth = random.uniform(0.5, 2.0)
        elif prob < 75:
            severity = 'Moderate'
            depth = random.uniform(2.0, 5.0)
        else:
            severity = random.choice(['High', 'Extreme'])
            depth = random.uniform(5.0, 15.0)
        
        resolution = random.choice([250, 375, 500, 1000])
        
        source_file = f"{model_name.lower()}_{forecast_time.strftime('%Y%m%d_%H%M')}.nc"
        models.append(f"('nasa_{i:06d}', '{model_name}', '{forecast_time}', {lat:.7f}, {lon:.7f}, {depth:.2f}, {prob:.2f}, '{severity}', {resolution}, {lon - 0.01:.6f}, {lat - 0.01:.6f}, {lon + 0.01:.6f}, {lat + 0.01:.6f}, '{source_file}')")
    
    return models

def generate_assessments(count=500000):
    """Generate flood risk assessments"""
    assessments = []
    property_ids = [f"prop_{i:06d}" for i in range(1, 200001)]
    zone_codes = ['A', 'AE', 'AH', 'AO', 'V', 'VE', 'X', 'D']
    scenarios = ['Low', 'Intermediate-Low', 'Intermediate', 'Intermediate-High', 'High', 'Extreme']
    horizons = [0, 5, 10, 20, 30, 50, 100]
    
    for i in range(1, count + 1):
        property_id = random.choice(property_ids)
        assessment_date = datetime(2020, 1, 1) + timedelta(days=random.randint(0, 2000))
        horizon = random.choice(horizons)
        assessment_type = 'Current' if horizon == 0 else f'{horizon}-Year Projection'
        
        zone_code = random.choice(zone_codes)
        zone_id = f"fz_{random.randint(1, 5000):06d}"
        bfe = random.uniform(5.0, 25.0) if zone_code in ['AE', 'VE'] else None
        
        # Calculate risk scores
        fema_score = 85.0 if zone_code in ['VE', 'A'] else (70.0 if zone_code == 'AE' else 15.0)
        slr_feet = horizon * 0.02 + random.uniform(-0.1, 0.1) if horizon > 0 else None
        slr_score = min(100, (slr_feet or 0) * 20) if slr_feet else None
        streamflow_score = random.uniform(20.0, 60.0)
        nasa_score = random.uniform(15.0, 70.0)
        
        overall_score = (fema_score * 0.4 + streamflow_score * 0.3 + nasa_score * 0.3)
        if slr_score:
            overall_score = (fema_score * 0.3 + slr_score * 0.3 + streamflow_score * 0.2 + nasa_score * 0.2)
        
        if overall_score >= 70:
            category = 'Extreme'
        elif overall_score >= 50:
            category = 'High'
        elif overall_score >= 30:
            category = 'Moderate'
        else:
            category = 'Low'
        
        vulnerability = overall_score * 0.9
        exposure = overall_score * 0.85
        
        # Estimate financial impact
        base_value = random.uniform(500000, 20000000)
        damage_pct = overall_score / 100.0
        estimated_damage = base_value * damage_pct * random.uniform(0.3, 0.7)
        annual_loss = estimated_damage * random.uniform(0.05, 0.15)
        insurance_premium = base_value * 0.01 * (overall_score / 100.0) * random.uniform(0.5, 1.5)
        
        scenario_val = random.choice(scenarios) if slr_feet else 'NULL'
        htf_days_val = random.randint(5, 200) if slr_feet else 'NULL'
        gauge_id_val = random.randint(1000000, 9999999)
        nasa_severity = random.choice(['Low', 'Moderate', 'High', 'Extreme'])
        bfe_val = f"{bfe:.2f}" if bfe else 'NULL'
        slr_feet_val = f"{slr_feet:.3f}" if slr_feet else 'NULL'
        slr_score_val = f"{slr_score:.2f}" if slr_score else 'NULL'
        
        assessments.append(f"('assess_{i:06d}', '{property_id}', '{assessment_date.date()}', '{assessment_type}', {horizon}, '{zone_code}', '{zone_id}', {bfe_val}, {fema_score:.2f}, {slr_feet_val}, '{scenario_val}', {htf_days_val}, {slr_score_val}, '{gauge_id_val}', {random.randint(0, 50)}, {random.uniform(2.0, 15.0):.2f}, {streamflow_score:.2f}, {random.uniform(10.0, 80.0):.2f}, '{nasa_severity}', {nasa_score:.2f}, {overall_score:.2f}, '{category}', {vulnerability:.2f}, {exposure:.2f}, {estimated_damage:.2f}, {annual_loss:.2f}, {insurance_premium:.2f}, 'Multi-Factor Risk Assessment', 'FEMA NFHL, NOAA SLR, USGS Streamflow, NASA Models', 'High')")
    
    return assessments

def generate_intersections(count=1000000):
    """Generate property-flood zone intersections"""
    intersections = []
    property_ids = [f"prop_{i:06d}" for i in range(1, 200001)]
    zone_ids = [f"fz_{i:06d}" for i in range(1, 20001)]
    
    for i in range(1, count + 1):
        property_id = random.choice(property_ids)
        zone_id = random.choice(zone_ids)
        intersection_type = random.choice(['Within', 'Adjacent', 'Near'])
        distance = random.uniform(0, 1000) if intersection_type != 'Within' else 0
        elevation_diff = random.uniform(-5.0, 20.0)
        
        intersections.append(f"('int_{i:06d}', '{property_id}', '{zone_id}', '{intersection_type}', {distance:.2f}, {elevation_diff:.2f})")
    
    return intersections

def generate_historical_events(count=5000):
    """Generate historical flood events"""
    events = []
    event_types = ['Riverine', 'Coastal', 'Flash', 'Storm Surge', 'Tidal']
    states = ['NY', 'CA', 'IL', 'FL', 'WA', 'TX', 'LA', 'NC', 'SC', 'GA', 'VA', 'MD', 'NJ', 'MA', 'CT', 'RI', 'NH', 'ME', 'OR', 'HI']
    event_names = [
        'Hurricane', 'Tropical Storm', 'Flood', 'Flash Flood', 'River Flood',
        'Coastal Flood', 'Storm Surge', 'Tidal Flood', 'Heavy Rain', 'Snowmelt Flood'
    ]
    
    for i in range(1, count + 1):
        event_type = random.choice(event_types)
        state = random.choice(states)
        event_name = f"{random.choice(event_names)} {random.randint(2000, 2025)}"
        
        start_date = datetime(2000, 1, 1) + timedelta(days=random.randint(0, 9500))
        duration = random.randint(1, 7)
        end_date = start_date + timedelta(days=duration)
        
        peak_discharge = random.uniform(5000, 500000) if event_type == 'Riverine' else None
        peak_stage = random.uniform(5.0, 25.0)
        damage = random.uniform(1000000, 100000000000)
        fatalities = random.randint(0, 200)
        properties_affected = random.randint(100, 500000)
        
        events.append(f"('event_{i:06d}', '{event_name}', '{event_type}', '{start_date.date()}', '{end_date.date()}', {peak_discharge if peak_discharge else 'NULL'}, {peak_stage:.2f}, {damage:.2f}, {fatalities}, {properties_affected}, '{state}', '{state}{random.randint(1, 999):03d}', 'FEMA')")
    
    return events

def generate_model_metrics(count=1000):
    """Generate model performance metrics"""
    metrics = []
    model_names = ['GFMS', 'LIS', 'VIIRS', 'MODIS', 'FloodPlanet']
    
    for i in range(1, count + 1):
        model_name = random.choice(model_names)
        eval_date = datetime(2020, 1, 1) + timedelta(days=random.randint(0, 2000))
        period_start = eval_date - timedelta(days=365)
        period_end = eval_date
        
        total_pred = random.randint(10000, 100000)
        tp = int(total_pred * random.uniform(0.05, 0.15))
        tn = int(total_pred * random.uniform(0.70, 0.85))
        fp = int(total_pred * random.uniform(0.02, 0.08))
        fn = total_pred - tp - tn - fp
        
        accuracy = (tp + tn) / total_pred if total_pred > 0 else 0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        roc_auc = random.uniform(0.75, 0.95)
        mae = random.uniform(0.3, 0.7)
        rmse = random.uniform(0.5, 1.0)
        resolution = random.choice([250, 375, 500, 1000])
        temporal = random.choice([1, 3, 6, 12])
        
        metrics.append(f"('metric_{i:06d}', '{model_name}', '{eval_date.date()}', '{period_start.date()}', '{period_end.date()}', {total_pred}, {tp}, {tn}, {fp}, {fn}, {accuracy:.4f}, {precision:.4f}, {recall:.4f}, {f1:.4f}, {roc_auc:.4f}, {mae:.4f}, {rmse:.4f}, {resolution}, {temporal}, 'Performance evaluation for {model_name}')")
    
    return metrics

def generate_portfolio_summaries(count=500):
    """Generate portfolio risk summaries"""
    summaries = []
    
    for i in range(1, count + 1):
        portfolio_id = f"port_{i:03d}"
        portfolio_name = f"Portfolio {i}"
        summary_date = datetime(2020, 1, 1) + timedelta(days=random.randint(0, 2000))
        
        total_props = random.randint(10, 1000)
        avg_value = random.uniform(500000, 10000000)
        total_value = total_props * avg_value
        
        at_risk_pct = random.uniform(0.1, 0.8)
        extreme_pct = random.uniform(0.0, 0.2)
        high_pct = random.uniform(0.1, 0.4)
        moderate_pct = random.uniform(0.2, 0.5)
        low_pct = 1.0 - at_risk_pct
        
        props_at_risk = int(total_props * at_risk_pct)
        props_extreme = int(total_props * extreme_pct)
        props_high = int(total_props * high_pct)
        props_moderate = int(total_props * moderate_pct)
        props_low = total_props - props_at_risk
        
        risk_value = total_value * at_risk_pct
        extreme_value = total_value * extreme_pct
        high_value = total_value * high_pct
        moderate_value = total_value * moderate_pct
        low_value = total_value * low_pct
        
        avg_risk = (extreme_pct * 85 + high_pct * 65 + moderate_pct * 40 + low_pct * 15)
        median_risk = 50.0 if at_risk_pct > 0.5 else 25.0
        
        estimated_damage = risk_value * random.uniform(0.05, 0.15)
        annual_loss = estimated_damage * random.uniform(0.05, 0.10)
        concentration = at_risk_pct * 100
        diversification = (1.0 - concentration / 100) * 100
        
        summaries.append(f"('summ_{i:06d}', '{portfolio_id}', '{portfolio_name}', '{summary_date.date()}', {total_props}, {total_value:.2f}, {props_at_risk}, {props_extreme}, {props_high}, {props_moderate}, {props_low}, {risk_value:.2f}, {extreme_value:.2f}, {high_value:.2f}, {moderate_value:.2f}, {low_value:.2f}, {avg_risk:.2f}, {median_risk:.2f}, {estimated_damage:.2f}, {annual_loss:.2f}, {concentration:.2f}, {diversification:.2f})")
    
    return summaries

def generate_data_quality_metrics(count=500):
    """Generate data quality metrics"""
    metrics = []
    sources = ['FEMA NFHL', 'NOAA CO-OPS', 'USGS Water Data', 'NASA GFMS', 'NASA LIS', 'NASA VIIRS', 'NASA MODIS']
    
    for i in range(1, count + 1):
        source = random.choice(sources)
        metric_date = datetime(2020, 1, 1) + timedelta(days=random.randint(0, 2000))
        
        files_processed = random.randint(5, 50)
        files_successful = int(files_processed * random.uniform(0.85, 1.0))
        files_failed = files_processed - files_successful
        success_rate = (files_successful / files_processed * 100) if files_processed > 0 else 0
        
        total_records = random.randint(10000, 1000000)
        error_rate_pct = random.uniform(0.1, 2.0)
        records_with_errors = int(total_records * error_rate_pct / 100)
        
        spatial_coverage = random.uniform(100000, 10000000)
        temporal_coverage = random.choice([0, 24, 168, 720, 8760])
        freshness = random.choice([5, 15, 60, 180, 1440])
        
        completeness = random.uniform(0.90, 0.99)
        accuracy = random.uniform(0.90, 0.99)
        consistency = random.uniform(0.90, 0.99)
        timeliness = random.uniform(0.85, 0.98)
        overall = (completeness + accuracy + consistency + timeliness) / 4
        
        metrics.append(f"('dq_{i:06d}', '{metric_date.date()}', '{source}', {files_processed}, {files_successful}, {files_failed}, {success_rate:.2f}, {total_records}, {records_with_errors}, {error_rate_pct:.2f}, {spatial_coverage:.2f}, {temporal_coverage}, {freshness}, {completeness:.2f}, {accuracy:.2f}, {consistency:.2f}, {timeliness:.2f}, {overall:.2f})")
    
    return metrics

def main():
    """Generate large dataset"""
    output_file = Path(__file__).parent.parent / 'data' / 'data.sql'
    
    print("="*70)
    print("Generating Large Dataset for db-16 (~2 GB)")
    print("="*70)
    print()
    
    # Generate data for each table (increased counts to reach ~2 GB)
    print("Generating FEMA flood zones...")
    fema_zones = generate_fema_flood_zones(20000)
    
    print("Generating real estate properties...")
    properties = generate_properties(200000)
    
    print("Generating NOAA sea level rise projections...")
    slr_projections = generate_slr_projections(50000)
    
    print("Generating USGS streamflow gauges...")
    gauges = generate_streamflow_gauges(5000)
    
    print("Generating USGS streamflow observations...")
    observations = generate_streamflow_observations(3000000)
    
    print("Generating NASA flood models...")
    nasa_models = generate_nasa_models(1500000)
    
    print("Generating flood risk assessments...")
    assessments = generate_assessments(500000)
    
    print("Generating property-flood zone intersections...")
    intersections = generate_intersections(1000000)
    
    print("Generating historical flood events...")
    events = generate_historical_events(20000)
    
    print("Generating model performance metrics...")
    model_metrics = generate_model_metrics(5000)
    
    print("Generating portfolio risk summaries...")
    portfolio_summaries = generate_portfolio_summaries(2000)
    
    print("Generating data quality metrics...")
    dq_metrics = generate_data_quality_metrics(2000)
    
    # Write to file
    print()
    print("Writing data.sql file...")
    with open(output_file, 'w') as f:
        f.write("-- Sample Data for Flood Risk Assessment Database\n")
        f.write("-- Compatible with PostgreSQL\n")
        f.write("-- Production sample data for physical climate risk assessment system\n")
        f.write("-- Rebuilt: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n\n")
        
        # FEMA flood zones
        f.write("-- Insert FEMA flood zones\n")
        f.write("INSERT INTO fema_flood_zones (zone_id, zone_code, zone_description, base_flood_elevation, community_id, community_name, state_code, county_fips, effective_date, map_panel, source_file, source_crs, target_crs, spatial_extent_west, spatial_extent_south, spatial_extent_east, spatial_extent_north, transformation_status) VALUES\n")
        for i, zone in enumerate(fema_zones):
            f.write(zone)
            if i < len(fema_zones) - 1:
                f.write(",\n")
            else:
                f.write(";\n\n")
        
        # Real estate properties
        f.write("-- Insert real estate properties\n")
        f.write("INSERT INTO real_estate_properties (property_id, property_address, property_latitude, property_longitude, property_type, building_value, land_value, total_value, square_footage, year_built, number_of_floors, elevation_feet, state_code, county_fips, city_name, zip_code, portfolio_id, portfolio_name, acquisition_date) VALUES\n")
        batch_size = 1000
        for batch_start in range(0, len(properties), batch_size):
            batch = properties[batch_start:batch_start + batch_size]
            for i, prop in enumerate(batch):
                f.write(prop)
                if i < len(batch) - 1:
                    f.write(",\n")
                else:
                    f.write(";\n")
            if batch_start + batch_size < len(properties):
                f.write("\nINSERT INTO real_estate_properties (property_id, property_address, property_latitude, property_longitude, property_type, building_value, land_value, total_value, square_footage, year_built, number_of_floors, elevation_feet, state_code, county_fips, city_name, zip_code, portfolio_id, portfolio_name, acquisition_date) VALUES\n")
        f.write("\n")
        
        # NOAA sea level rise
        f.write("-- Insert NOAA sea level rise projections\n")
        f.write("INSERT INTO noaa_sea_level_rise (projection_id, station_id, station_name, station_latitude, station_longitude, projection_year, scenario, sea_level_rise_feet, confidence_level, high_tide_flooding_days, data_source) VALUES\n")
        batch_size = 1000
        for batch_start in range(0, len(slr_projections), batch_size):
            batch = slr_projections[batch_start:batch_start + batch_size]
            for i, proj in enumerate(batch):
                f.write(proj)
                if i < len(batch) - 1:
                    f.write(",\n")
                else:
                    f.write(";\n")
            if batch_start + batch_size < len(slr_projections):
                f.write("\nINSERT INTO noaa_sea_level_rise (projection_id, station_id, station_name, station_latitude, station_longitude, projection_year, scenario, sea_level_rise_feet, confidence_level, high_tide_flooding_days, data_source) VALUES\n")
        f.write("\n")
        
        # USGS gauges
        f.write("-- Insert USGS streamflow gauges\n")
        f.write("INSERT INTO usgs_streamflow_gauges (gauge_id, gauge_name, gauge_latitude, gauge_longitude, drainage_area_sq_miles, flood_stage_feet, moderate_flood_stage_feet, major_flood_stage_feet, state_code, county_name, river_name, active_status, first_observation_date, last_observation_date, update_frequency_minutes) VALUES\n")
        batch_size = 500
        for batch_start in range(0, len(gauges), batch_size):
            batch = gauges[batch_start:batch_start + batch_size]
            for i, gauge in enumerate(batch):
                f.write(gauge)
                if i < len(batch) - 1:
                    f.write(",\n")
                else:
                    f.write(";\n")
            if batch_start + batch_size < len(gauges):
                f.write("\nINSERT INTO usgs_streamflow_gauges (gauge_id, gauge_name, gauge_latitude, gauge_longitude, drainage_area_sq_miles, flood_stage_feet, moderate_flood_stage_feet, major_flood_stage_feet, state_code, county_name, river_name, active_status, first_observation_date, last_observation_date, update_frequency_minutes) VALUES\n")
        f.write("\n")
        
        # USGS observations
        f.write("-- Insert USGS streamflow observations\n")
        f.write("INSERT INTO usgs_streamflow_observations (observation_id, gauge_id, observation_time, gage_height_feet, discharge_cfs, stage_feet, flood_category, percentile_rank, data_quality_code) VALUES\n")
        batch_size = 5000
        for batch_start in range(0, len(observations), batch_size):
            batch = observations[batch_start:batch_start + batch_size]
            for i, obs in enumerate(batch):
                f.write(obs)
                if i < len(batch) - 1:
                    f.write(",\n")
                else:
                    f.write(";\n")
            if batch_start + batch_size < len(observations):
                f.write("\nINSERT INTO usgs_streamflow_observations (observation_id, gauge_id, observation_time, gage_height_feet, discharge_cfs, stage_feet, flood_category, percentile_rank, data_quality_code) VALUES\n")
        f.write("\n")
        
        # NASA models
        f.write("-- Insert NASA flood model outputs\n")
        f.write("INSERT INTO nasa_flood_models (model_id, model_name, forecast_time, grid_cell_latitude, grid_cell_longitude, inundation_depth_feet, flood_probability, flood_severity, model_resolution_meters, spatial_extent_west, spatial_extent_south, spatial_extent_east, spatial_extent_north, source_file) VALUES\n")
        batch_size = 5000
        for batch_start in range(0, len(nasa_models), batch_size):
            batch = nasa_models[batch_start:batch_start + batch_size]
            for i, model in enumerate(batch):
                f.write(model)
                if i < len(batch) - 1:
                    f.write(",\n")
                else:
                    f.write(";\n")
            if batch_start + batch_size < len(nasa_models):
                f.write("\nINSERT INTO nasa_flood_models (model_id, model_name, forecast_time, grid_cell_latitude, grid_cell_longitude, inundation_depth_feet, flood_probability, flood_severity, model_resolution_meters, spatial_extent_west, spatial_extent_south, spatial_extent_east, spatial_extent_north, source_file) VALUES\n")
        f.write("\n")
        
        # Flood risk assessments
        f.write("-- Insert flood risk assessments\n")
        f.write("INSERT INTO flood_risk_assessments (assessment_id, property_id, assessment_date, assessment_type, time_horizon_years, fema_zone_code, fema_zone_id, base_flood_elevation_feet, flood_zone_risk_score, sea_level_rise_feet, sea_level_rise_scenario, high_tide_flooding_days, sea_level_risk_score, nearest_gauge_id, historical_flood_frequency, flood_probability_percent, streamflow_risk_score, nasa_model_flood_probability, nasa_model_severity, nasa_model_risk_score, overall_risk_score, risk_category, vulnerability_score, exposure_score, estimated_damage_dollars, estimated_annual_loss, insurance_premium_estimate, assessment_methodology, data_sources_used, confidence_level) VALUES\n")
        batch_size = 5000
        for batch_start in range(0, len(assessments), batch_size):
            batch = assessments[batch_start:batch_start + batch_size]
            for i, assess in enumerate(batch):
                f.write(assess)
                if i < len(batch) - 1:
                    f.write(",\n")
                else:
                    f.write(";\n")
            if batch_start + batch_size < len(assessments):
                f.write("\nINSERT INTO flood_risk_assessments (assessment_id, property_id, assessment_date, assessment_type, time_horizon_years, fema_zone_code, fema_zone_id, base_flood_elevation_feet, flood_zone_risk_score, sea_level_rise_feet, sea_level_rise_scenario, high_tide_flooding_days, sea_level_risk_score, nearest_gauge_id, historical_flood_frequency, flood_probability_percent, streamflow_risk_score, nasa_model_flood_probability, nasa_model_severity, nasa_model_risk_score, overall_risk_score, risk_category, vulnerability_score, exposure_score, estimated_damage_dollars, estimated_annual_loss, insurance_premium_estimate, assessment_methodology, data_sources_used, confidence_level) VALUES\n")
        f.write("\n")
        
        # Intersections
        f.write("-- Insert property-flood zone intersections\n")
        f.write("INSERT INTO property_flood_zone_intersections (intersection_id, property_id, zone_id, intersection_type, distance_to_zone_feet, elevation_difference_feet) VALUES\n")
        batch_size = 5000
        for batch_start in range(0, len(intersections), batch_size):
            batch = intersections[batch_start:batch_start + batch_size]
            for i, inter in enumerate(batch):
                f.write(inter)
                if i < len(batch) - 1:
                    f.write(",\n")
                else:
                    f.write(";\n")
            if batch_start + batch_size < len(intersections):
                f.write("\nINSERT INTO property_flood_zone_intersections (intersection_id, property_id, zone_id, intersection_type, distance_to_zone_feet, elevation_difference_feet) VALUES\n")
        f.write("\n")
        
        # Historical events
        f.write("-- Insert historical flood events\n")
        f.write("INSERT INTO historical_flood_events (event_id, event_name, event_type, start_date, end_date, peak_discharge_cfs, peak_stage_feet, total_damage_dollars, fatalities, properties_affected, state_code, county_fips, data_source) VALUES\n")
        batch_size = 1000
        for batch_start in range(0, len(events), batch_size):
            batch = events[batch_start:batch_start + batch_size]
            for i, event in enumerate(batch):
                f.write(event)
                if i < len(batch) - 1:
                    f.write(",\n")
                else:
                    f.write(";\n")
            if batch_start + batch_size < len(events):
                f.write("\nINSERT INTO historical_flood_events (event_id, event_name, event_type, start_date, end_date, peak_discharge_cfs, peak_stage_feet, total_damage_dollars, fatalities, properties_affected, state_code, county_fips, data_source) VALUES\n")
        f.write("\n")
        
        # Model metrics
        f.write("-- Insert model performance metrics\n")
        f.write("INSERT INTO model_performance_metrics (metric_id, model_name, evaluation_date, evaluation_period_start, evaluation_period_end, total_predictions, true_positives, true_negatives, false_positives, false_negatives, accuracy, precision_score, recall_score, f1_score, roc_auc, mean_absolute_error, root_mean_squared_error, spatial_resolution_meters, temporal_resolution_hours, evaluation_notes) VALUES\n")
        batch_size = 500
        for batch_start in range(0, len(model_metrics), batch_size):
            batch = model_metrics[batch_start:batch_start + batch_size]
            for i, metric in enumerate(batch):
                f.write(metric)
                if i < len(batch) - 1:
                    f.write(",\n")
                else:
                    f.write(";\n")
            if batch_start + batch_size < len(model_metrics):
                f.write("\nINSERT INTO model_performance_metrics (metric_id, model_name, evaluation_date, evaluation_period_start, evaluation_period_end, total_predictions, true_positives, true_negatives, false_positives, false_negatives, accuracy, precision_score, recall_score, f1_score, roc_auc, mean_absolute_error, root_mean_squared_error, spatial_resolution_meters, temporal_resolution_hours, evaluation_notes) VALUES\n")
        f.write("\n")
        
        # Portfolio summaries
        f.write("-- Insert portfolio risk summaries\n")
        f.write("INSERT INTO portfolio_risk_summaries (summary_id, portfolio_id, portfolio_name, summary_date, total_properties, total_portfolio_value, properties_at_risk, properties_extreme_risk, properties_high_risk, properties_moderate_risk, properties_low_risk, total_risk_value, extreme_risk_value, high_risk_value, moderate_risk_value, low_risk_value, avg_risk_score, median_risk_score, total_estimated_damage, total_estimated_annual_loss, risk_concentration_percentage, geographic_diversification_score) VALUES\n")
        batch_size = 100
        for batch_start in range(0, len(portfolio_summaries), batch_size):
            batch = portfolio_summaries[batch_start:batch_start + batch_size]
            for i, summ in enumerate(batch):
                f.write(summ)
                if i < len(batch) - 1:
                    f.write(",\n")
                else:
                    f.write(";\n")
            if batch_start + batch_size < len(portfolio_summaries):
                f.write("\nINSERT INTO portfolio_risk_summaries (summary_id, portfolio_id, portfolio_name, summary_date, total_properties, total_portfolio_value, properties_at_risk, properties_extreme_risk, properties_high_risk, properties_moderate_risk, properties_low_risk, total_risk_value, extreme_risk_value, high_risk_value, moderate_risk_value, low_risk_value, avg_risk_score, median_risk_score, total_estimated_damage, total_estimated_annual_loss, risk_concentration_percentage, geographic_diversification_score) VALUES\n")
        f.write("\n")
        
        # Data quality metrics
        f.write("-- Insert data quality metrics\n")
        f.write("INSERT INTO data_quality_metrics (metric_id, metric_date, data_source, files_processed, files_successful, files_failed, success_rate, total_records, records_with_errors, error_rate, spatial_coverage_km2, temporal_coverage_hours, data_freshness_minutes, completeness_score, accuracy_score, consistency_score, timeliness_score, overall_quality_score) VALUES\n")
        batch_size = 100
        for batch_start in range(0, len(dq_metrics), batch_size):
            batch = dq_metrics[batch_start:batch_start + batch_size]
            for i, dq in enumerate(batch):
                f.write(dq)
                if i < len(batch) - 1:
                    f.write(",\n")
                else:
                    f.write(";\n")
            if batch_start + batch_size < len(dq_metrics):
                f.write("\nINSERT INTO data_quality_metrics (metric_id, metric_date, data_source, files_processed, files_successful, files_failed, success_rate, total_records, records_with_errors, error_rate, spatial_coverage_km2, temporal_coverage_hours, data_freshness_minutes, completeness_score, accuracy_score, consistency_score, timeliness_score, overall_quality_score) VALUES\n")
    
    file_size = output_file.stat().st_size
    file_size_gb = file_size / (1024**3)
    
    print()
    print("="*70)
    print(f"✓ Dataset generated successfully!")
    print(f"✓ File size: {file_size_gb:.2f} GB ({file_size:,} bytes)")
    print(f"✓ Total records:")
    print(f"  - FEMA flood zones: {len(fema_zones):,}")
    print(f"  - Real estate properties: {len(properties):,}")
    print(f"  - NOAA SLR projections: {len(slr_projections):,}")
    print(f"  - USGS gauges: {len(gauges):,}")
    print(f"  - USGS observations: {len(observations):,}")
    print(f"  - NASA models: {len(nasa_models):,}")
    print(f"  - Risk assessments: {len(assessments):,}")
    print(f"  - Intersections: {len(intersections):,}")
    print(f"  - Historical events: {len(events):,}")
    print(f"  - Model metrics: {len(model_metrics):,}")
    print(f"  - Portfolio summaries: {len(portfolio_summaries):,}")
    print(f"  - Data quality metrics: {len(dq_metrics):,}")
    print("="*70)

if __name__ == '__main__':
    main()
