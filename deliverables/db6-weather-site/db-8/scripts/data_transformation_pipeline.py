#!/usr/bin/env python3
"""
Data Transformation Pipeline for db-8
Transforms raw data (CSV, JSON) into database-ready format with cleaning, validation, and enrichment
"""

import os
import sys
import json
import csv
import logging
import traceback
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Iterator
import re

# Import timestamp utility
try:
    from timestamp_utils import get_est_timestamp
except ImportError:
    root_scripts = Path(__file__).parent.parent.parent / 'scripts'
    sys.path.insert(0, str(root_scripts))
    from timestamp_utils import get_est_timestamp

# Data processing imports
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("Warning: pandas not available. Some transformations will be limited.")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataTransformer:
    """Transforms and cleans data before loading into database"""
    
    def __init__(self, input_dir: Path, output_dir: Path):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.stats = {
            'files_processed': 0,
            'records_transformed': 0,
            'records_cleaned': 0,
            'records_enriched': 0,
            'errors': []
        }
    
    def normalize_string(self, text: str) -> str:
        """Normalize string: trim, lowercase, remove extra spaces"""
        if not text:
            return ''
        return ' '.join(text.strip().lower().split())
    
    def clean_email(self, email: str) -> Optional[str]:
        """Validate and clean email address"""
        if not email:
            return None
        email = email.strip().lower()
        # Basic email validation
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(pattern, email):
            return email
        return None
    
    def clean_url(self, url: str) -> Optional[str]:
        """Clean and validate URL"""
        if not url:
            return None
        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url
    
    def normalize_location(self, city: str, state: str) -> tuple:
        """Normalize city and state names"""
        city = self.normalize_string(city).title() if city else ''
        state = state.upper().strip()[:2] if state else ''
        return city, state
    
    def enrich_job_title(self, title: str) -> Dict:
        """Enrich job title with normalized version and category"""
        normalized = self.normalize_string(title)
        
        # Categorize job titles
        categories = {
            'engineering': ['engineer', 'developer', 'programmer', 'architect', 'devops', 'sre'],
            'data': ['data scientist', 'data engineer', 'data analyst', 'ml engineer', 'analyst'],
            'management': ['manager', 'director', 'lead', 'head', 'vp', 'chief'],
            'product': ['product manager', 'product owner', 'pm'],
            'design': ['designer', 'ux', 'ui', 'design'],
            'sales': ['sales', 'account executive', 'business development'],
            'marketing': ['marketing', 'growth', 'content', 'seo'],
            'operations': ['operations', 'ops', 'coordinator', 'specialist']
        }
        
        category = 'other'
        title_lower = normalized.lower()
        for cat, keywords in categories.items():
            if any(keyword in title_lower for keyword in keywords):
                category = cat
                break
        
        return {
            'normalized': normalized,
            'category': category
        }
    
    def transform_user_profiles(self, input_file: Path) -> Path:
        """Transform user profiles CSV"""
        logger.info(f"Transforming user profiles: {input_file}")
        output_file = self.output_dir / 'user_profiles_transformed.csv'
        
        records_processed = 0
        records_cleaned = 0
        
        with open(input_file, 'r', encoding='utf-8') as infile, \
             open(output_file, 'w', encoding='utf-8', newline='') as outfile:
            
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in reader:
                records_processed += 1
                
                # Clean email
                if 'email' in row:
                    row['email'] = self.clean_email(row.get('email', ''))
                
                # Normalize location
                if 'location_city' in row and 'location_state' in row:
                    city, state = self.normalize_location(
                        row.get('location_city', ''),
                        row.get('location_state', '')
                    )
                    row['location_city'] = city
                    row['location_state'] = state
                
                # Clean URLs
                for url_field in ['linkedin_url', 'github_url', 'portfolio_url']:
                    if url_field in row:
                        row[url_field] = self.clean_url(row.get(url_field, ''))
                
                # Normalize job title
                if 'current_job_title' in row:
                    row['current_job_title'] = self.normalize_string(row.get('current_job_title', ''))
                
                # Normalize company name
                if 'current_company' in row:
                    row['current_company'] = self.normalize_string(row.get('current_company', ''))
                
                writer.writerow(row)
                records_cleaned += 1
                
                if records_processed % 100000 == 0:
                    logger.info(f"Processed {records_processed:,} user profiles")
        
        self.stats['records_transformed'] += records_processed
        self.stats['records_cleaned'] += records_cleaned
        logger.info(f"Transformed {records_cleaned:,} user profiles")
        return output_file
    
    def transform_companies(self, input_file: Path) -> Path:
        """Transform companies CSV"""
        logger.info(f"Transforming companies: {input_file}")
        output_file = self.output_dir / 'companies_transformed.csv'
        
        records_processed = 0
        records_cleaned = 0
        
        with open(input_file, 'r', encoding='utf-8') as infile, \
             open(output_file, 'w', encoding='utf-8', newline='') as outfile:
            
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in reader:
                records_processed += 1
                
                # Normalize company name
                if 'company_name' in row:
                    row['company_name'] = self.normalize_string(row.get('company_name', ''))
                    if 'company_name_normalized' in row:
                        row['company_name_normalized'] = row['company_name'].lower().replace(' ', '_')
                
                # Normalize location
                if 'headquarters_city' in row and 'headquarters_state' in row:
                    city, state = self.normalize_location(
                        row.get('headquarters_city', ''),
                        row.get('headquarters_state', '')
                    )
                    row['headquarters_city'] = city
                    row['headquarters_state'] = state
                
                # Clean URLs
                for url_field in ['website_url', 'linkedin_url']:
                    if url_field in row:
                        row[url_field] = self.clean_url(row.get(url_field, ''))
                
                # Normalize industry
                if 'industry' in row:
                    row['industry'] = self.normalize_string(row.get('industry', '')).title()
                
                writer.writerow(row)
                records_cleaned += 1
                
                if records_processed % 100000 == 0:
                    logger.info(f"Processed {records_processed:,} companies")
        
        self.stats['records_transformed'] += records_processed
        self.stats['records_cleaned'] += records_cleaned
        logger.info(f"Transformed {records_cleaned:,} companies")
        return output_file
    
    def transform_job_postings(self, input_file: Path) -> Path:
        """Transform job postings CSV"""
        logger.info(f"Transforming job postings: {input_file}")
        output_file = self.output_dir / 'job_postings_transformed.csv'
        
        records_processed = 0
        records_cleaned = 0
        
        with open(input_file, 'r', encoding='utf-8') as infile, \
             open(output_file, 'w', encoding='utf-8', newline='') as outfile:
            
            reader = csv.DictReader(infile)
            fieldnames = list(reader.fieldnames)
            
            # Add normalized fields if not present
            if 'job_title_normalized' not in fieldnames:
                fieldnames.append('job_title_normalized')
            if 'job_category' not in fieldnames:
                fieldnames.append('job_category')
            
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in reader:
                records_processed += 1
                
                # Enrich job title
                if 'job_title' in row:
                    title = row.get('job_title', '')
                    enriched = self.enrich_job_title(title)
                    row['job_title'] = enriched['normalized']
                    row['job_title_normalized'] = enriched['normalized'].lower().replace(' ', '_')
                    row['job_category'] = enriched['category']
                
                # Normalize location
                if 'location_city' in row and 'location_state' in row:
                    city, state = self.normalize_location(
                        row.get('location_city', ''),
                        row.get('location_state', '')
                    )
                    row['location_city'] = city
                    row['location_state'] = state
                
                # Clean URLs
                for url_field in ['application_url', 'source_url']:
                    if url_field in row:
                        row[url_field] = self.clean_url(row.get(url_field, ''))
                
                # Normalize work model and job type
                if 'work_model' in row:
                    row['work_model'] = self.normalize_string(row.get('work_model', ''))
                if 'job_type' in row:
                    row['job_type'] = self.normalize_string(row.get('job_type', ''))
                
                writer.writerow(row)
                records_cleaned += 1
                
                if records_processed % 100000 == 0:
                    logger.info(f"Processed {records_processed:,} job postings")
        
        self.stats['records_transformed'] += records_processed
        self.stats['records_cleaned'] += records_cleaned
        logger.info(f"Transformed {records_cleaned:,} job postings")
        return output_file
    
    def transform_applications(self, input_file: Path) -> Path:
        """Transform job applications CSV"""
        logger.info(f"Transforming applications: {input_file}")
        output_file = self.output_dir / 'job_applications_transformed.csv'
        
        records_processed = 0
        records_cleaned = 0
        
        with open(input_file, 'r', encoding='utf-8') as infile, \
             open(output_file, 'w', encoding='utf-8', newline='') as outfile:
            
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in reader:
                records_processed += 1
                
                # Normalize application status
                if 'application_status' in row:
                    row['application_status'] = self.normalize_string(row.get('application_status', ''))
                
                # Normalize application method
                if 'application_method' in row:
                    row['application_method'] = self.normalize_string(row.get('application_method', ''))
                
                writer.writerow(row)
                records_cleaned += 1
                
                if records_processed % 100000 == 0:
                    logger.info(f"Processed {records_processed:,} applications")
        
        self.stats['records_transformed'] += records_processed
        self.stats['records_cleaned'] += records_cleaned
        logger.info(f"Transformed {records_cleaned:,} applications")
        return output_file
    
    def transform_recommendations(self, input_file: Path) -> Path:
        """Transform job recommendations CSV"""
        logger.info(f"Transforming recommendations: {input_file}")
        output_file = self.output_dir / 'job_recommendations_transformed.csv'
        
        records_processed = 0
        records_cleaned = 0
        
        with open(input_file, 'r', encoding='utf-8') as infile, \
             open(output_file, 'w', encoding='utf-8', newline='') as outfile:
            
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in reader:
                records_processed += 1
                
                # Normalize recommendation reason
                if 'recommendation_reason' in row:
                    row['recommendation_reason'] = self.normalize_string(row.get('recommendation_reason', ''))
                
                writer.writerow(row)
                records_cleaned += 1
                
                if records_processed % 100000 == 0:
                    logger.info(f"Processed {records_processed:,} recommendations")
        
        self.stats['records_transformed'] += records_processed
        self.stats['records_cleaned'] += records_cleaned
        logger.info(f"Transformed {records_cleaned:,} recommendations")
        return output_file
    
    def transform_generic_csv(self, input_file: Path) -> Path:
        """Transform generic CSV file (for internet-pulled data)"""
        logger.info(f"Transforming generic CSV: {input_file}")
        output_file = self.output_dir / f"{input_file.stem}_transformed{input_file.suffix}"
        
        records_processed = 0
        records_cleaned = 0
        
        try:
            with open(input_file, 'r', encoding='utf-8', errors='ignore') as infile, \
                 open(output_file, 'w', encoding='utf-8', newline='') as outfile:
                
                reader = csv.DictReader(infile)
                fieldnames = reader.fieldnames
                if not fieldnames:
                    logger.warning(f"No headers found in {input_file}")
                    return output_file
                
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for row in reader:
                    records_processed += 1
                    
                    # Basic cleaning - normalize string fields
                    cleaned_row = {}
                    for key, value in row.items():
                        if isinstance(value, str):
                            cleaned_row[key] = self.normalize_string(value)
                        else:
                            cleaned_row[key] = value
                    
                    writer.writerow(cleaned_row)
                    records_cleaned += 1
                    
                    if records_processed % 100000 == 0:
                        logger.info(f"Processed {records_processed:,} records")
            
            self.stats['records_transformed'] += records_processed
            self.stats['records_cleaned'] += records_cleaned
            logger.info(f"Transformed {records_cleaned:,} records from {input_file.name}")
            
        except Exception as e:
            error_msg = f"Error transforming {input_file.name}: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            self.stats['errors'].append(error_msg)
        
        return output_file
    
    def transform_all(self) -> Dict:
        """Transform all data files"""
        logger.info("Starting data transformation pipeline")
        
        transformations = {
            'user_profiles.csv': self.transform_user_profiles,
            'companies.csv': self.transform_companies,
            'job_postings.csv': self.transform_job_postings,
            'job_applications.csv': self.transform_applications,
            'job_recommendations.csv': self.transform_recommendations
        }
        
        # Transform known files
        for filename, transform_func in transformations.items():
            input_file = self.input_dir / filename
            if input_file.exists():
                try:
                    transform_func(input_file)
                    self.stats['files_processed'] += 1
                except Exception as e:
                    error_msg = f"Error transforming {filename}: {str(e)}\n{traceback.format_exc()}"
                    logger.error(error_msg)
                    self.stats['errors'].append(error_msg)
            else:
                logger.warning(f"Input file not found: {input_file}")
        
        # Transform any other CSV/JSON files (for internet-pulled data)
        for file_path in self.input_dir.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in ['.csv', '.json']:
                # Skip already processed files
                if file_path.name in [f for f in transformations.keys()]:
                    continue
                
                try:
                    if file_path.suffix.lower() == '.csv':
                        self.transform_generic_csv(file_path)
                        self.stats['files_processed'] += 1
                    elif file_path.suffix.lower() == '.json':
                        # For JSON files, convert to CSV first or handle separately
                        logger.info(f"Skipping JSON file (not yet implemented): {file_path.name}")
                except Exception as e:
                    error_msg = f"Error transforming {file_path.name}: {str(e)}\n{traceback.format_exc()}"
                    logger.error(error_msg)
                    self.stats['errors'].append(error_msg)
        
        # Generate transformation report
        report = {
            'transformation_date': get_est_timestamp(),
            'input_directory': str(self.input_dir),
            'output_directory': str(self.output_dir),
            'stats': self.stats,
            'files_transformed': self.stats['files_processed']
        }
        
        report_file = self.output_dir.parent / 'results' / f'transformation_report_{get_est_timestamp()}.json'
        report_file.parent.mkdir(parents=True, exist_ok=True)
        report_file.write_text(json.dumps(report, indent=2))
        
        logger.info("Data transformation pipeline complete")
        return report


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Transform data for db-8')
    parser.add_argument('--input-dir', type=str, default='data/generated',
                       help='Input directory with raw CSV files')
    parser.add_argument('--output-dir', type=str, default='data/transformed',
                       help='Output directory for transformed CSV files')
    
    args = parser.parse_args()
    
    transformer = DataTransformer(args.input_dir, args.output_dir)
    report = transformer.transform_all()
    
    print("\n" + "="*70)
    print("Data Transformation Complete")
    print("="*70)
    print(f"Files processed: {report['stats']['files_processed']}")
    print(f"Records transformed: {report['stats']['records_transformed']:,}")
    print(f"Records cleaned: {report['stats']['records_cleaned']:,}")
    print(f"Errors: {len(report['stats']['errors'])}")
    print(f"Output directory: {args.output_dir}")
    print("="*70)


if __name__ == '__main__':
    main()
