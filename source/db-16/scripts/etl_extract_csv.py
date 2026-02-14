import os
import csv
import json
from pathlib import Path
from typing import List, Dict, Any

def read_csv_file(filepath: str) -> List[Dict[str, Any]]:
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def read_csv_no_headers(filepath: str, columns: List[str]) -> List[Dict[str, Any]]:
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= len(columns):
                record = {col: row[i] if i < len(row) else None for i, col in enumerate(columns)}
                data.append(record)
    return data

def extract_fema_csv(db17_path: str) -> List[Dict[str, Any]]:
    csv_path = Path(db17_path) / "data" / "blob-storage" / "documents" / "datagov_flood_datasets.csv"
    if not csv_path.exists():
        return []
    
    columns = [
        "dataset_id", "title", "organization", "tags", "format", "url",
        "metadata_created", "metadata_modified", "notes", "license_id",
        "state", "county", "zone_code", "zone_description", "bfe",
        "latitude", "longitude", "geometry", "community_name", "effective_date"
    ]
    
    return read_csv_no_headers(str(csv_path), columns)

def extract_noaa_csv(db17_path: str) -> List[Dict[str, Any]]:
    csv_path = Path(db17_path) / "data" / "blob-storage" / "documents" / "noaa_coops_stations.csv"
    if not csv_path.exists():
        return []
    
    columns = [
        "active", "greatlakes", "station_id", "name", "state", "timezone",
        "timezone_offset", "harmonic", "superseded", "datums", "benchmarks",
        "tidepredoffsets", "nearby", "products", "disclaimers", "notices",
        "station_type", "station_type_id", "details_url", "sensors_url",
        "floodlevels_url", "datums_url", "harcon_url", "benchmarks_url",
        "tidepredoffsets_url", "ofsmapoffsets_url", "nearby_url", "products_url",
        "disclaimers_url", "notices_url"
    ]
    
    return read_csv_no_headers(str(csv_path), columns)

def extract_usgs_csv(db17_path: str) -> List[Dict[str, Any]]:
    csv_path = Path(db17_path) / "data" / "blob-storage" / "documents" / "usgs_streamflow_observations.csv"
    if not csv_path.exists():
        return []
    
    columns = [
        "agency", "site_no", "datetime", "tz_cd", "gage_height_va",
        "gage_height_cd", "discharge_va", "discharge_cd", "water_temp_va",
        "water_temp_cd", "ph_va", "ph_cd", "turbidity_va", "turbidity_cd",
        "oxygen_va", "oxygen_cd", "conductance_va", "conductance_cd",
        "wtemp_va", "wtemp_cd", "air_temp_va", "air_temp_cd", "barometric_pressure_va",
        "barometric_pressure_cd", "precipitation_va", "precipitation_cd",
        "wind_speed_va", "wind_speed_cd", "wind_direction_va", "wind_direction_cd"
    ]
    
    return read_csv_no_headers(str(csv_path), columns)

def extract_nasa_csv(db17_path: str) -> List[Dict[str, Any]]:
    csv_path = Path(db17_path) / "data" / "blob-storage" / "documents" / "nasa_neo.csv"
    if not csv_path.exists():
        return []
    
    columns = [
        "id", "neo_reference_id", "name", "nasa_jpl_url", "absolute_magnitude_h",
        "estimated_diameter_min_km", "estimated_diameter_max_km",
        "is_potentially_hazardous_asteroid", "close_approach_date",
        "close_approach_date_full", "epoch_date_close_approach",
        "relative_velocity_km_per_sec", "relative_velocity_km_per_hour",
        "miss_distance_astronomical", "miss_distance_lunar",
        "miss_distance_km", "miss_distance_miles", "orbiting_body"
    ]
    
    return read_csv_no_headers(str(csv_path), columns)

def extract_historical_csv(db17_path: str) -> List[Dict[str, Any]]:
    csv_path = Path(db17_path) / "data" / "blob-storage" / "documents" / "usgs_earthquakes.csv"
    if not csv_path.exists():
        return []
    
    columns = [
        "time", "latitude", "longitude", "depth", "mag", "magType",
        "nst", "gap", "dmin", "rms", "net", "id", "updated", "place",
        "type", "horizontalError", "depthError", "magError", "magNst",
        "status", "locationSource", "magSource"
    ]
    
    return read_csv_no_headers(str(csv_path), columns)

def save_extracted_data(data: List[Dict[str, Any]], output_path: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, default=str)

def main():
    db17_path = os.getenv('DB17_PATH', '../db-17')
    output_dir = Path(__file__).parent.parent / "data" / "extracted"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    fema_data = extract_fema_csv(db17_path)
    save_extracted_data(fema_data, str(output_dir / "fema_extracted.json"))
    
    noaa_data = extract_noaa_csv(db17_path)
    save_extracted_data(noaa_data, str(output_dir / "noaa_extracted.json"))
    
    usgs_data = extract_usgs_csv(db17_path)
    save_extracted_data(usgs_data, str(output_dir / "usgs_extracted.json"))
    
    nasa_data = extract_nasa_csv(db17_path)
    save_extracted_data(nasa_data, str(output_dir / "nasa_extracted.json"))
    
    historical_data = extract_historical_csv(db17_path)
    save_extracted_data(historical_data, str(output_dir / "historical_extracted.json"))

if __name__ == "__main__":
    main()
