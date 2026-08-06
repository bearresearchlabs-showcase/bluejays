import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from etl_extract_csv import main as extract_main
from etl_transform_fema import transform_fema_data
from etl_transform_noaa import transform_noaa_data
from etl_transform_usgs import transform_usgs_data
from etl_transform_nasa import transform_nasa_data
from etl_transform_historical import transform_historical_data
from etl_load_postgresql import main as load_main

def run_etl_pipeline():
    base_dir = Path(__file__).parent.parent
    extracted_dir = base_dir / "data" / "extracted"
    transformed_dir = base_dir / "data" / "transformed"
    
    extracted_dir.mkdir(parents=True, exist_ok=True)
    transformed_dir.mkdir(parents=True, exist_ok=True)
    
    print("Step 1: Extracting CSV files from db-17...")
    extract_main()
    
    print("Step 2: Transforming FEMA data...")
    transform_fema_data(
        str(extracted_dir / "fema_extracted.json"),
        str(transformed_dir / "fema_transformed.json")
    )
    
    print("Step 3: Transforming NOAA data...")
    transform_noaa_data(
        str(extracted_dir / "noaa_extracted.json"),
        str(transformed_dir / "noaa_transformed.json")
    )
    
    print("Step 4: Transforming USGS data...")
    transform_usgs_data(
        str(extracted_dir / "usgs_extracted.json"),
        str(transformed_dir / "usgs_gauges_transformed.json"),
        str(transformed_dir / "usgs_observations_transformed.json")
    )
    
    print("Step 5: Transforming NASA data...")
    transform_nasa_data(
        str(extracted_dir / "nasa_extracted.json"),
        str(transformed_dir / "nasa_transformed.json")
    )
    
    print("Step 6: Transforming historical data...")
    transform_historical_data(
        str(extracted_dir / "historical_extracted.json"),
        str(transformed_dir / "historical_transformed.json")
    )
    
    print("Step 7: Loading data into PostgreSQL...")
    load_main()
    
    print("ETL pipeline completed successfully")

if __name__ == "__main__":
    run_etl_pipeline()
