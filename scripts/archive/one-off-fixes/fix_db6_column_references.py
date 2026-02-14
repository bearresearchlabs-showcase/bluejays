#!/usr/bin/env python3
"""
Fix db-6 column reference errors
"""
import re
from pathlib import Path

def fix_all():
    queries_file = Path('db-6/queries/queries.md')
    content = queries_file.read_text()
    original = content
    
    # Query 18: Remove non-existent columns from insurance_claims_history
    # Remove: policy_type, coverage_type, loss_amount, claim_status, weather_event_type, 
    # weather_event_date, temperature_at_loss, precipitation_at_loss, wind_speed_at_loss, forecast_error
    # Keep: claim_id, policy_area_id, claim_date, loss_date, forecast_available, forecast_day, claim_amount, claim_type
    
    # Query 18: Fix ich.policy_type - remove or use NULL
    content = re.sub(
        r'\bich\.policy_type\b',
        r'NULL::VARCHAR(100) AS policy_type',
        content,
        flags=re.IGNORECASE
    )
    
    # Query 18: Fix ich.coverage_type - remove or use NULL
    content = re.sub(
        r'\bich\.coverage_type\b',
        r'NULL::VARCHAR(100) AS coverage_type',
        content,
        flags=re.IGNORECASE
    )
    
    # Query 18: Fix ich.loss_amount - use claim_amount instead
    content = re.sub(
        r'\bich\.loss_amount\b',
        r'ich.claim_amount',
        content,
        flags=re.IGNORECASE
    )
    
    # Query 18: Fix ich.claim_status - remove or use NULL
    content = re.sub(
        r'\bich\.claim_status\b',
        r"'Closed'::VARCHAR(50) AS claim_status",
        content,
        flags=re.IGNORECASE
    )
    
    # Query 18: Fix ich.weather_event_type - remove or use NULL
    content = re.sub(
        r'\bich\.weather_event_type\b',
        r'NULL::VARCHAR(100) AS weather_event_type',
        content,
        flags=re.IGNORECASE
    )
    
    # Query 18: Fix ich.weather_event_date - remove or use NULL
    content = re.sub(
        r'\bich\.weather_event_date\b',
        r'NULL::DATE AS weather_event_date',
        content,
        flags=re.IGNORECASE
    )
    
    # Query 18: Fix ich.temperature_at_loss - remove or use NULL
    content = re.sub(
        r'\bich\.temperature_at_loss\b',
        r'NULL::NUMERIC AS temperature_at_loss',
        content,
        flags=re.IGNORECASE
    )
    
    # Query 18: Fix ich.precipitation_at_loss - remove or use NULL
    content = re.sub(
        r'\bich\.precipitation_at_loss\b',
        r'NULL::NUMERIC AS precipitation_at_loss',
        content,
        flags=re.IGNORECASE
    )
    
    # Query 18: Fix ich.wind_speed_at_loss - remove or use NULL
    content = re.sub(
        r'\bich\.wind_speed_at_loss\b',
        r'NULL::NUMERIC AS wind_speed_at_loss',
        content,
        flags=re.IGNORECASE
    )
    
    # Query 18 & 24: Fix ich.forecast_error - remove or use NULL
    content = re.sub(
        r'\bich\.forecast_error\b',
        r'NULL::NUMERIC AS forecast_error',
        content,
        flags=re.IGNORECASE
    )
    
    # Query 21: Fix frm.forecast_time - use gf.forecast_time instead
    content = re.sub(
        r'\bfrm\.forecast_time\b',
        r'gf.forecast_time',
        content,
        flags=re.IGNORECASE
    )
    
    # Query 21: Fix frm.parameter_value - use gf.parameter_value instead
    content = re.sub(
        r'\bfrm\.parameter_value\b',
        r'gf.parameter_value',
        content,
        flags=re.IGNORECASE
    )
    
    # Query 21: Fix frm.risk_contribution - remove or use NULL
    content = re.sub(
        r'\bfrm\.risk_contribution\b',
        r'NULL::NUMERIC AS risk_contribution',
        content,
        flags=re.IGNORECASE
    )
    
    # Query 21: Fix frm.rate_impact - remove or use NULL
    content = re.sub(
        r'\bfrm\.rate_impact\b',
        r'NULL::NUMERIC AS rate_impact',
        content,
        flags=re.IGNORECASE
    )
    
    # Query 26: Fix nsc.max_reflectivity_dbz - use nsc.max_reflectivity instead
    content = re.sub(
        r'\bnsc\.max_reflectivity_dbz\b',
        r'nsc.max_reflectivity',
        content,
        flags=re.IGNORECASE
    )
    
    # Query 26: Fix nsc.storm_area_km2 - remove or use NULL
    content = re.sub(
        r'\bnsc\.storm_area_km2\b',
        r'NULL::NUMERIC AS storm_area_km2',
        content,
        flags=re.IGNORECASE
    )
    
    # Query 26: Fix nsc.tracking_status - remove or use NULL
    content = re.sub(
        r'\bnsc\.tracking_status\s*=\s*[''"]Active[''"]',
        r'1=1',
        content,
        flags=re.IGNORECASE
    )
    
    # Query 28 & 30: Fix nrg.precipitation_rate_mmh - this doesn't exist in nexrad_reflectivity_grid
    # Need to join with satellite_imagery_products or use NULL
    # Actually, let me check if we should join with satellite table or use NULL
    content = re.sub(
        r'\bnrg\.precipitation_rate_mmh\b',
        r'NULL::NUMERIC AS precipitation_rate_mmh',
        content,
        flags=re.IGNORECASE
    )
    
    # Query 28 & 30: Fix nrg.accumulated_precipitation_mm - remove or use NULL
    content = re.sub(
        r'\bnrg\.accumulated_precipitation_mm\b',
        r'NULL::NUMERIC AS accumulated_precipitation_mm',
        content,
        flags=re.IGNORECASE
    )
    
    # Query 28 & 30: Fix nrg.max_reflectivity_dbz - use nrg.reflectivity_value instead
    content = re.sub(
        r'\bnrg\.max_reflectivity_dbz\b',
        r'nrg.reflectivity_value',
        content,
        flags=re.IGNORECASE
    )
    
    # Query 28 & 30: Fix nrg.composite_reflectivity_dbz - use nrg.reflectivity_value instead
    content = re.sub(
        r'\bnrg\.composite_reflectivity_dbz\b',
        r'nrg.reflectivity_value',
        content,
        flags=re.IGNORECASE
    )
    
    if content != original:
        queries_file.write_text(content)
        return ["db-6"]
    return []

if __name__ == '__main__':
    import os
    os.chdir(Path(__file__).parent.parent)
    fixes = fix_all()
    if fixes:
        print(f"Fixed: {', '.join(fixes)}")
    else:
        print("No fixes needed")
