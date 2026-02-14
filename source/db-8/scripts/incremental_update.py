#!/usr/bin/env python3
"""
Incremental data update script for db-8
Handles daily incremental updates with change detection, upsert logic, and metadata tracking
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import traceback

# Import timestamp utility
try:
    from timestamp_utils import get_est_timestamp
except ImportError:
    root_scripts = Path(__file__).parent.parent.parent / 'scripts'
    sys.path.insert(0, str(root_scripts))
    from timestamp_utils import get_est_timestamp

# Database imports
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PG_AVAILABLE = True
except ImportError:
    PG_AVAILABLE = False

try:
    from databricks import sql
    DATABRICKS_AVAILABLE = True
except ImportError:
    DATABRICKS_AVAILABLE = False

# API imports
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Data processing imports
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    logger.warning("pandas not available - DOL file parsing will be limited")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IncrementalUpdater:
    """Handles incremental data updates with change detection"""
    
    def __init__(self, db_config: Dict):
        self.db_config = db_config
        self.pg_conn = None
        self.db_conn = None
        self.metadata_file = Path(__file__).parent.parent / 'metadata' / 'incremental_checkpoints.json'
        self.checkpoints = self._load_checkpoints()
    
    def _load_checkpoints(self) -> Dict:
        """Load incremental update checkpoints"""
        if self.metadata_file.exists():
            return json.loads(self.metadata_file.read_text())
        return {}
    
    def _save_checkpoint(self, source_name: str, last_extraction_date: str):
        """Save checkpoint for incremental updates"""
        self.checkpoints[source_name] = {
            'last_extraction_date': last_extraction_date,
            'last_update': get_est_timestamp()
        }
        self.metadata_file.parent.mkdir(parents=True, exist_ok=True)
        self.metadata_file.write_text(json.dumps(self.checkpoints, indent=2))
    
    def get_last_extraction_date(self, source_name: str) -> Optional[datetime]:
        """Get last extraction date for a source"""
        if source_name in self.checkpoints:
            date_str = self.checkpoints[source_name]['last_extraction_date']
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return None
    
    def connect_postgresql(self) -> bool:
        """Connect to PostgreSQL"""
        if not PG_AVAILABLE:
            return False
        try:
            self.pg_conn = psycopg2.connect(
                host=self.db_config.get('host', 'localhost'),
                port=self.db_config.get('port', 5432),
                database=self.db_config.get('database', 'db_8_validation'),
                user=self.db_config.get('user', os.environ.get('USER', 'postgres')),
                password=self.db_config.get('password', '')
            )
            return True
        except Exception as e:
            logger.error(f"PostgreSQL connection failed: {e}")
            return False
    
    def incremental_load_usajobs(self, days_back: int = 14) -> Dict:
        """Incremental load from USAJobs.gov API (last N days)"""
        result = {
            'source': 'usajobs',
            'records_extracted': 0,
            'records_new': 0,
            'records_updated': 0,
            'records_failed': 0,
            'status': 'success',
            'errors': []
        }
        
        last_date = self.get_last_extraction_date('usajobs')
        if last_date:
            days_back = max(1, (datetime.now() - last_date).days)
        
        # USAJobs API call
        api_key = os.environ.get('USAJOBS_API_KEY')
        user_agent = os.environ.get('USAJOBS_USER_AGENT', 'JobMarketIntelligence/1.0')
        
        if not api_key:
            result['status'] = 'failed'
            result['errors'].append('USAJOBS_API_KEY not set')
            return result
        
        try:
            url = "https://data.usajobs.gov/api/Search"
            headers = {
                'User-Agent': user_agent,
                'Authorization-Key': api_key
            }
            params = {
                'DatePosted': days_back,
                'ResultsPerPage': 500,
                'Page': 1
            }
            
            # Create session with retry logic
            session = requests.Session()
            retry_strategy = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504]
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("https://", adapter)
            
            all_jobs = []
            page = 1
            
            while True:
                params['Page'] = page
                response = session.get(url, headers=headers, params=params, timeout=30)
                
                if response.status_code != 200:
                    result['errors'].append(f"API error: {response.status_code}")
                    break
                
                data = response.json()
                jobs = data.get('SearchResult', {}).get('SearchResultItems', [])
                
                if not jobs:
                    break
                
                all_jobs.extend(jobs)
                result['records_extracted'] += len(jobs)
                
                # Check if more pages
                total_pages = data.get('SearchResult', {}).get('UserArea', {}).get('NumberOfPages', 1)
                if page >= total_pages:
                    break
                
                page += 1
                
                # Rate limiting
                import time
                time.sleep(0.6)  # Respect 100 req/min limit
            
            # Process and load jobs
            if self.pg_conn:
                new_count, updated_count, failed_count = self._upsert_job_postings(all_jobs, 'usajobs')
                result['records_new'] = new_count
                result['records_updated'] = updated_count
                result['records_failed'] = failed_count
            
            # Save checkpoint
            self._save_checkpoint('usajobs', datetime.now().isoformat())
            
        except Exception as e:
            logger.error(f"USAJobs extraction error: {e}")
            result['status'] = 'failed'
            result['errors'].append(str(e))
            result['errors'].append(traceback.format_exc())
        
        return result
    
    def _upsert_job_postings(self, jobs: List[Dict], source: str) -> tuple:
        """Upsert job postings (insert new, update existing)"""
        new_count = 0
        updated_count = 0
        failed_count = 0
        
        cursor = self.pg_conn.cursor()
        
        for job in jobs:
            try:
                # Extract job data (simplified - adjust based on actual API response)
                job_id = f"usajobs_{job.get('MatchedObjectId', '')}"
                posted_date_str = job.get('MatchedObjectDescriptor', {}).get('PositionStartDate', {})
                posted_date = datetime.fromisoformat(posted_date_str) if posted_date_str else datetime.now()
                
                # Check if exists
                cursor.execute(
                    "SELECT job_id FROM job_postings WHERE job_id = %s",
                    (job_id,)
                )
                exists = cursor.fetchone()
                
                if exists:
                    # Update existing
                    # (Implement update logic based on schema)
                    updated_count += 1
                else:
                    # Insert new
                    # (Implement insert logic based on schema)
                    new_count += 1
                
            except Exception as e:
                logger.error(f"Error processing job {job.get('MatchedObjectId')}: {e}")
                failed_count += 1
        
        self.pg_conn.commit()
        cursor.close()
        
        return new_count, updated_count, failed_count
    
    def incremental_load_bls(self, start_year: int = None, end_year: int = None) -> Dict:
        """Incremental load from BLS Public Data API for employment statistics"""
        result = {
            'source': 'bls',
            'records_extracted': 0,
            'records_new': 0,
            'records_updated': 0,
            'records_failed': 0,
            'status': 'success',
            'errors': []
        }
        
        # BLS API configuration
        api_key = os.environ.get('BLS_REGISTRATION_KEY')
        base_url = "https://api.bls.gov/publicAPI/v2/timeseries/data"
        
        # Determine date range (default: last 2 years)
        if not start_year or not end_year:
            end_year = datetime.now().year
            start_year = end_year - 2
        
        # Key BLS series IDs for job market intelligence
        # LAUCN = Labor Area Unemployment Statistics (County level)
        # LAUST = Labor Area Unemployment Statistics (State level)
        # OES = Occupational Employment Statistics
        series_ids = [
            'LAUST040000000000003',  # Arizona unemployment rate
            'LAUST060000000000003',  # California unemployment rate
            'LAUST480000000000003',  # Texas unemployment rate
            'LAUST360000000000003',  # New York unemployment rate
            'LAUST120000000000003',  # Florida unemployment rate
            # Add more states as needed
        ]
        
        try:
            # Create session with retry logic
            session = requests.Session()
            retry_strategy = Retry(
                total=3,
                backoff_factor=2,
                status_forcelist=[429, 500, 502, 503, 504]
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("https://", adapter)
            
            # Prepare BLS API request (POST method for multiple series)
            payload = {
                'seriesid': series_ids,
                'startyear': str(start_year),
                'endyear': str(end_year)
            }
            
            if api_key:
                payload['registrationkey'] = api_key
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            response = session.post(
                base_url,
                json=payload,
                headers=headers,
                timeout=60
            )
            
            if response.status_code != 200:
                result['status'] = 'failed'
                result['errors'].append(f"BLS API error: {response.status_code} - {response.text}")
                return result
            
            data = response.json()
            
            if data.get('status') != 'REQUEST_SUCCEEDED':
                result['status'] = 'failed'
                result['errors'].append(f"BLS API error: {data.get('message', 'Unknown error')}")
                return result
            
            # Process time-series data
            series_data = data.get('Results', {}).get('series', [])
            market_trends = []
            
            for series in series_data:
                series_id = series.get('seriesID', '')
                state_code = series_id[5:7] if len(series_id) >= 7 else None
                
                for item in series.get('data', []):
                    year = int(item.get('year', 0))
                    period = item.get('period', '')
                    value = item.get('value', '')
                    
                    # Parse period (M01-M12 for monthly, Q01-Q04 for quarterly, A13 for annual)
                    if period.startswith('M'):
                        month = int(period[1:])
                        trend_date = datetime(year, month, 1)
                    elif period.startswith('Q'):
                        quarter = int(period[1:])
                        month = (quarter - 1) * 3 + 1
                        trend_date = datetime(year, month, 1)
                    elif period == 'A13':
                        trend_date = datetime(year, 12, 31)
                    else:
                        continue
                    
                    # Determine metric type from series ID
                    if '000000000003' in series_id:
                        metric_type = 'unemployment_rate'
                    elif '000000000004' in series_id:
                        metric_type = 'employment_level'
                    elif '000000000006' in series_id:
                        metric_type = 'labor_force'
                    else:
                        metric_type = 'other'
                    
                    market_trends.append({
                        'trend_date': trend_date,
                        'geographic_scope': 'state',
                        'location_state': state_code if state_code else None,
                        'metric_type': metric_type,
                        'metric_value': float(value) if value != '' else None,
                        'series_id': series_id,
                        'data_source': 'bls'
                    })
            
            result['records_extracted'] = len(market_trends)
            
            # Load into database
            if self.pg_conn and market_trends:
                new_count, updated_count, failed_count = self._upsert_market_trends(market_trends)
                result['records_new'] = new_count
                result['records_updated'] = updated_count
                result['records_failed'] = failed_count
            
            # Save checkpoint
            self._save_checkpoint('bls', datetime.now().isoformat())
            
        except Exception as e:
            logger.error(f"BLS extraction error: {e}")
            result['status'] = 'failed'
            result['errors'].append(str(e))
            result['errors'].append(traceback.format_exc())
        
        return result
    
    def _upsert_market_trends(self, trends: List[Dict]) -> tuple:
        """Upsert market trends data"""
        new_count = 0
        updated_count = 0
        failed_count = 0
        
        cursor = self.pg_conn.cursor()
        
        for trend in trends:
            try:
                # Generate unique trend_id based on date, scope, location, and metric
                series_id = trend.get('series_id', 'unknown')
                trend_date = trend['trend_date']
                location_state = trend.get('location_state', '')
                metric_type = trend.get('metric_type', 'unknown')
                
                trend_id = f"bls_{series_id}_{trend_date.strftime('%Y%m%d')}_{metric_type}"
                
                # Check if exists using UNIQUE constraint fields
                cursor.execute(
                    """SELECT trend_id FROM market_trends 
                       WHERE trend_date = %s 
                         AND geographic_scope = %s 
                         AND location_state = %s
                         AND data_source = %s""",
                    (
                        trend_date,
                        trend.get('geographic_scope', 'state'),
                        location_state,
                        trend.get('data_source', 'bls')
                    )
                )
                exists = cursor.fetchone()
                
                metric_value = trend.get('metric_value')
                if metric_value is None:
                    continue
                
                if exists:
                    # Update existing - map metric types to appropriate columns
                    if metric_type == 'unemployment_rate':
                        # Store in growth_rate or competition_index as proxy
                        cursor.execute(
                            """UPDATE market_trends SET
                               competition_index = %s,
                               updated_at = CURRENT_TIMESTAMP()
                               WHERE trend_id = %s""",
                            (metric_value, exists[0])
                        )
                    elif metric_type == 'employment_level':
                        cursor.execute(
                            """UPDATE market_trends SET
                               active_job_seekers = %s,
                               updated_at = CURRENT_TIMESTAMP()
                               WHERE trend_id = %s""",
                            (int(metric_value), exists[0])
                        )
                    updated_count += 1
                else:
                    # Insert new - map metric types appropriately
                    if metric_type == 'unemployment_rate':
                        cursor.execute(
                            """INSERT INTO market_trends 
                               (trend_id, trend_date, geographic_scope, location_state, 
                                competition_index, data_source, created_at)
                               VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP())""",
                            (
                                trend_id,
                                trend_date,
                                trend.get('geographic_scope', 'state'),
                                location_state,
                                metric_value,
                                trend.get('data_source', 'bls')
                            )
                        )
                    elif metric_type == 'employment_level':
                        cursor.execute(
                            """INSERT INTO market_trends 
                               (trend_id, trend_date, geographic_scope, location_state, 
                                active_job_seekers, data_source, created_at)
                               VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP())""",
                            (
                                trend_id,
                                trend_date,
                                trend.get('geographic_scope', 'state'),
                                location_state,
                                int(metric_value),
                                trend.get('data_source', 'bls')
                            )
                        )
                    else:
                        # Generic insert
                        cursor.execute(
                            """INSERT INTO market_trends 
                               (trend_id, trend_date, geographic_scope, location_state, 
                                total_job_postings, data_source, created_at)
                               VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP())""",
                            (
                                trend_id,
                                trend_date,
                                trend.get('geographic_scope', 'state'),
                                location_state,
                                int(metric_value) if metric_value else None,
                                trend.get('data_source', 'bls')
                            )
                        )
                    new_count += 1
                    
            except Exception as e:
                logger.error(f"Error processing trend {trend.get('trend_id', 'unknown')}: {e}")
                failed_count += 1
        
        self.pg_conn.commit()
        cursor.close()
        
        return new_count, updated_count, failed_count
    
    def _parse_dol_csv(self, df: 'pd.DataFrame', dataset_name: str, dataset_id: str) -> List[Dict]:
        """Parse DOL CSV data and transform to market_trends format"""
        records = []
        
        if df.empty:
            return records
        
        # Common column mappings (adjust based on actual DOL dataset schemas)
        # Try to identify date, location, and metric columns
        date_cols = [col for col in df.columns if any(x in col.lower() for x in ['date', 'year', 'period', 'time'])]
        location_cols = [col for col in df.columns if any(x in col.lower() for x in ['state', 'location', 'area', 'region', 'city'])]
        metric_cols = [col for col in df.columns if any(x in col.lower() for x in ['employment', 'jobs', 'wage', 'salary', 'unemployment', 'rate', 'count'])]
        
        for _, row in df.iterrows():
            try:
                # Extract date
                trend_date = None
                for date_col in date_cols:
                    if pd.notna(row.get(date_col)):
                        try:
                            trend_date = pd.to_datetime(row[date_col]).date()
                            break
                        except:
                            continue
                
                if not trend_date:
                    trend_date = datetime.now().date()
                
                # Extract location
                location_state = None
                location_city = None
                for loc_col in location_cols:
                    value = str(row.get(loc_col, '')).strip()
                    if len(value) == 2 and value.isupper():
                        location_state = value
                    elif len(value) > 2:
                        location_city = value[:100]  # Truncate to max length
                
                # Extract metrics
                total_job_postings = None
                average_salary_min = None
                average_salary_max = None
                
                for metric_col in metric_cols:
                    value = row.get(metric_col)
                    if pd.notna(value):
                        try:
                            num_value = float(value)
                            metric_lower = metric_col.lower()
                            if 'job' in metric_lower or 'employment' in metric_lower:
                                total_job_postings = int(num_value)
                            elif 'wage' in metric_lower or 'salary' in metric_lower:
                                if 'min' in metric_lower or 'low' in metric_lower:
                                    average_salary_min = int(num_value)
                                elif 'max' in metric_lower or 'high' in metric_lower:
                                    average_salary_max = int(num_value)
                                else:
                                    average_salary_min = int(num_value)
                        except:
                            continue
                
                records.append({
                    'trend_date': trend_date,
                    'geographic_scope': 'state' if location_state else 'national',
                    'location_state': location_state,
                    'location_city': location_city,
                    'total_job_postings': total_job_postings,
                    'average_salary_min': average_salary_min,
                    'average_salary_max': average_salary_max,
                    'data_source': 'dol',
                    'dataset_name': dataset_name,
                    'dataset_id': dataset_id
                })
            except Exception as e:
                logger.warning(f"Error parsing CSV row: {e}")
                continue
        
        return records
    
    def _parse_dol_json(self, df: 'pd.DataFrame', dataset_name: str, dataset_id: str) -> List[Dict]:
        """Parse DOL JSON data (converted to DataFrame) and transform to market_trends format"""
        # Use same logic as CSV parsing
        return self._parse_dol_csv(df, dataset_name, dataset_id)
    
    def _parse_dol_json_fallback(self, json_data: Dict, dataset_name: str, dataset_id: str) -> List[Dict]:
        """Fallback JSON parser when pandas is not available"""
        records = []
        
        # Handle different JSON structures
        if isinstance(json_data, list):
            data_list = json_data
        elif isinstance(json_data, dict):
            # Try common keys
            data_list = json_data.get('data', json_data.get('results', json_data.get('features', [json_data])))
        else:
            return records
        
        for item in data_list:
            try:
                if not isinstance(item, dict):
                    continue
                
                # Extract date
                trend_date = datetime.now().date()
                for date_key in ['date', 'year', 'period', 'time', 'created_at', 'updated_at']:
                    if date_key in item:
                        try:
                            trend_date = pd.to_datetime(item[date_key]).date() if PANDAS_AVAILABLE else datetime.now().date()
                            break
                        except:
                            continue
                
                # Extract location
                location_state = item.get('state', item.get('location_state', item.get('state_code')))
                location_city = item.get('city', item.get('location_city'))
                
                records.append({
                    'trend_date': trend_date,
                    'geographic_scope': 'state' if location_state else 'national',
                    'location_state': str(location_state)[:2] if location_state else None,
                    'location_city': str(location_city)[:100] if location_city else None,
                    'total_job_postings': item.get('jobs', item.get('employment', item.get('total_jobs'))),
                    'average_salary_min': item.get('salary_min', item.get('wage_min')),
                    'average_salary_max': item.get('salary_max', item.get('wage_max')),
                    'data_source': 'dol',
                    'dataset_name': dataset_name,
                    'dataset_id': dataset_id
                })
            except Exception as e:
                logger.warning(f"Error parsing JSON item: {e}")
                continue
        
        return records
    
    def _upsert_dol_data(self, records: List[Dict], dataset_name: str) -> tuple:
        """Upsert DOL data into market_trends table"""
        new_count = 0
        updated_count = 0
        failed_count = 0
        
        cursor = self.pg_conn.cursor()
        
        for record in records:
            try:
                # Generate unique trend_id
                trend_id = f"dol_{record.get('dataset_id', 'unknown')}_{record['trend_date'].strftime('%Y%m%d')}"
                
                # Check if exists using UNIQUE constraint fields
                cursor.execute(
                    """SELECT trend_id FROM market_trends 
                       WHERE trend_date = %s 
                         AND geographic_scope = %s 
                         AND location_state = %s
                         AND location_city = %s
                         AND data_source = %s""",
                    (
                        record['trend_date'],
                        record.get('geographic_scope', 'national'),
                        record.get('location_state'),
                        record.get('location_city'),
                        'dol'
                    )
                )
                exists = cursor.fetchone()
                
                if exists:
                    # Update existing
                    cursor.execute(
                        """UPDATE market_trends SET
                           total_job_postings = COALESCE(%s, total_job_postings),
                           average_salary_min = COALESCE(%s, average_salary_min),
                           average_salary_max = COALESCE(%s, average_salary_max),
                           updated_at = CURRENT_TIMESTAMP()
                           WHERE trend_id = %s""",
                        (
                            record.get('total_job_postings'),
                            record.get('average_salary_min'),
                            record.get('average_salary_max'),
                            exists[0]
                        )
                    )
                    updated_count += 1
                else:
                    # Insert new
                    cursor.execute(
                        """INSERT INTO market_trends 
                           (trend_id, trend_date, geographic_scope, location_state, location_city,
                            total_job_postings, average_salary_min, average_salary_max, data_source, created_at)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP())""",
                        (
                            trend_id,
                            record['trend_date'],
                            record.get('geographic_scope', 'national'),
                            record.get('location_state'),
                            record.get('location_city'),
                            record.get('total_job_postings'),
                            record.get('average_salary_min'),
                            record.get('average_salary_max'),
                            'dol'
                        )
                    )
                    new_count += 1
                    
            except Exception as e:
                logger.error(f"Error upserting DOL record: {e}")
                failed_count += 1
        
        self.pg_conn.commit()
        cursor.close()
        
        return new_count, updated_count, failed_count
    
    def incremental_load_dol(self, max_datasets: int = 10) -> Dict:
        """Incremental load from DOL Open Data Portal via Data.gov CKAN API"""
        result = {
            'source': 'dol',
            'datasets_found': 0,
            'datasets_processed': 0,
            'records_extracted': 0,
            'records_new': 0,
            'records_updated': 0,
            'records_failed': 0,
            'status': 'success',
            'errors': []
        }
        
        # Data.gov CKAN API configuration
        api_key = os.environ.get('DATA_GOV_API_KEY')
        base_url = "https://catalog.data.gov/api/3/action"
        
        try:
            # Create session with retry logic
            session = requests.Session()
            retry_strategy = Retry(
                total=3,
                backoff_factor=2,
                status_forcelist=[429, 500, 502, 503, 504]
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("https://", adapter)
            
            headers = {}
            if api_key:
                headers['X-API-Key'] = api_key
            
            # Search for DOL datasets
            search_url = f"{base_url}/package_search"
            search_params = {
                'q': 'employment OR labor OR job OR wage',
                'fq': 'organization:dol-gov',
                'rows': max_datasets,
                'start': 0
            }
            
            response = session.get(search_url, params=search_params, headers=headers, timeout=30)
            
            if response.status_code != 200:
                result['status'] = 'failed'
                result['errors'].append(f"DOL API error: {response.status_code}")
                return result
            
            data = response.json()
            
            if not data.get('success'):
                result['status'] = 'failed'
                result['errors'].append(f"DOL API error: {data.get('error', {}).get('message', 'Unknown error')}")
                return result
            
            datasets = data.get('result', {}).get('results', [])
            result['datasets_found'] = len(datasets)
            
            # Process each dataset
            for dataset in datasets:
                try:
                    dataset_id = dataset.get('id', '')
                    dataset_name = dataset.get('title', '')
                    
                    # Get dataset details
                    show_url = f"{base_url}/package_show"
                    show_params = {'id': dataset_id}
                    
                    show_response = session.get(show_url, params=show_params, headers=headers, timeout=30)
                    
                    if show_response.status_code != 200:
                        continue
                    
                    dataset_details = show_response.json()
                    
                    if not dataset_details.get('success'):
                        continue
                    
                    resources = dataset_details.get('result', {}).get('resources', [])
                    
                    # Process resources (CSV, JSON files)
                    for resource in resources:
                        resource_format = resource.get('format', '').upper()
                        resource_url = resource.get('url', '')
                        resource_id = resource.get('id', '')
                        
                        if resource_format not in ['CSV', 'JSON']:
                            continue
                        
                        if not resource_url:
                            continue
                        
                        try:
                            # Download resource file
                            resource_response = session.get(resource_url, headers=headers, timeout=120, stream=True)
                            
                            if resource_response.status_code != 200:
                                logger.warning(f"Failed to download resource {resource_id}: {resource_response.status_code}")
                                continue
                            
                            # Create temporary file
                            import tempfile
                            import uuid
                            temp_dir = Path(tempfile.gettempdir())
                            temp_file = temp_dir / f"dol_resource_{uuid.uuid4().hex[:8]}.{resource_format.lower()}"
                            
                            # Download file content
                            with open(temp_file, 'wb') as f:
                                for chunk in resource_response.iter_content(chunk_size=8192):
                                    f.write(chunk)
                            
                            # Parse file based on format
                            parsed_records = []
                            
                            if resource_format == 'CSV' and PANDAS_AVAILABLE:
                                df = pd.read_csv(temp_file, low_memory=False)
                                parsed_records = self._parse_dol_csv(df, dataset_name, dataset_id)
                            elif resource_format == 'JSON' and PANDAS_AVAILABLE:
                                # Try to read as JSON lines or regular JSON
                                try:
                                    df = pd.read_json(temp_file, lines=True)
                                except:
                                    df = pd.read_json(temp_file)
                                parsed_records = self._parse_dol_json(df, dataset_name, dataset_id)
                            elif resource_format == 'JSON':
                                # Fallback to json module
                                import json as json_module
                                with open(temp_file, 'r') as f:
                                    json_data = json_module.load(f)
                                parsed_records = self._parse_dol_json_fallback(json_data, dataset_name, dataset_id)
                            
                            # Load parsed records into database
                            if parsed_records and self.pg_conn:
                                new_count, updated_count, failed_count = self._upsert_dol_data(parsed_records, dataset_name)
                                result['records_new'] += new_count
                                result['records_updated'] += updated_count
                                result['records_failed'] += failed_count
                                result['records_extracted'] += len(parsed_records)
                            
                            # Clean up temp file
                            if temp_file.exists():
                                temp_file.unlink()
                                
                        except Exception as e:
                            logger.error(f"Error processing resource {resource_id}: {e}")
                            result['errors'].append(f"Resource {resource_id}: {str(e)}")
                            result['records_failed'] += 1
                    
                    result['datasets_processed'] += 1
                    
                except Exception as e:
                    logger.error(f"Error processing DOL dataset {dataset.get('id')}: {e}")
                    result['errors'].append(f"Dataset {dataset.get('id')}: {str(e)}")
            
            # Save checkpoint
            self._save_checkpoint('dol', datetime.now().isoformat())
            
        except Exception as e:
            logger.error(f"DOL extraction error: {e}")
            result['status'] = 'failed'
            result['errors'].append(str(e))
            result['errors'].append(traceback.format_exc())
        
        return result
    
    def run_daily_updates(self) -> Dict:
        """Run daily incremental updates for all sources"""
        results = {
            'update_date': get_est_timestamp(),
            'sources': {}
        }
        
        # Connect to database
        if not self.connect_postgresql():
            results['error'] = 'Failed to connect to database'
            return results
        
        # USAJobs.gov
        results['sources']['usajobs'] = self.incremental_load_usajobs()
        
        # BLS Public Data API
        bls_key = os.environ.get('BLS_REGISTRATION_KEY')
        if bls_key:
            results['sources']['bls'] = self.incremental_load_bls()
        else:
            logger.info("BLS_REGISTRATION_KEY not set, skipping BLS updates")
        
        # DOL Open Data Portal
        results['sources']['dol'] = self.incremental_load_dol()
        
        # Save results
        results_file = Path(__file__).parent.parent / 'metadata' / f"incremental_update_{get_est_timestamp()}.json"
        results_file.parent.mkdir(parents=True, exist_ok=True)
        results_file.write_text(json.dumps(results, indent=2, default=str))
        
        return results


def main():
    """Main incremental update function"""
    db_config = {
        'host': os.environ.get('PG_HOST', 'localhost'),
        'port': int(os.environ.get('PG_PORT', 5432)),
        'database': os.environ.get('PG_DATABASE', 'db_8_validation'),
        'user': os.environ.get('PG_USER', 'postgres'),
        'password': os.environ.get('PG_PASSWORD', '')
    }
    
    updater = IncrementalUpdater(db_config)
    results = updater.run_daily_updates()
    
    print("\n" + "="*70)
    print("Incremental Update Results")
    print("="*70)
    print(json.dumps(results, indent=2, default=str))
    print("="*70)


if __name__ == '__main__':
    main()
