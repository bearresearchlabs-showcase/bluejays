#!/usr/bin/env python3
"""
Ingest weather data from NWS API (api.weather.gov)
Includes forecasts, observations, alerts, and station data
"""

import json
import requests
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time

try:
    import databricks.connector
    SNOWFLAKE_AVAILABLE = True
except ImportError:
    SNOWFLAKE_AVAILABLE = False

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False


class NWSAPIIngester:
    """Ingest data from National Weather Service API"""

    BASE_URL = "https://api.weather.gov"
    USER_AGENT = "WeatherConsultingService/1.0 (contact@example.com)"

    def __init__(self, db_type='databricks'):
        self.db_type = db_type
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.USER_AGENT,
            'Accept': 'application/json'
        })
        self.script_dir = Path(__file__).parent
        self.root_dir = self.script_dir.parent.parent.parent

    def get_db_connection(self):
        """Get database connection"""
        if self.db_type == 'databricks':
            return self._get_databricks_connection()
        elif self.db_type == 'postgresql':
            return self._get_postgres_connection()
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")

    def _get_databricks_connection(self):
        """Get Databricks connection"""
        if not SNOWFLAKE_AVAILABLE:
            return None

        creds_file = self.root_dir / 'results' / 'databricks_credentials.json'
        if not creds_file.exists():
            return None

        with open(creds_file, 'r') as f:
            creds = json.load(f)

        account = creds.get('databricks_account', '')
        user = creds.get('databricks_user', '')
        role = creds.get('databricks_role', 'ACCOUNTADMIN')
        token = creds.get('databricks_token', '')

        conn_params = {
            'account': account,
            'user': user,
            'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH'),
            'database': os.getenv('SNOWFLAKE_DATABASE', 'DB6'),
            'schema': os.getenv('SNOWFLAKE_SCHEMA', 'PUBLIC'),
            'role': role
        }

        if token:
            conn_params['password'] = token
        else:
            conn_params['password'] = os.getenv('SNOWFLAKE_PASSWORD', '')

        try:
            return databricks.connector.connect(**conn_params)
        except Exception as e:
            print(f"❌ Databricks connection failed: {e}")
            return None

    def _get_postgres_connection(self):
        """Get PostgreSQL connection"""
        if not POSTGRES_AVAILABLE:
            return None

        import os
        host = os.getenv('POSTGRES_HOST', '127.0.0.1')
        port = os.getenv('POSTGRES_PORT_DB6', '5437')

        conn_params = {
            'host': host,
            'port': port,
            'database': os.getenv('POSTGRES_DB', 'db6'),
            'user': os.getenv('POSTGRES_USER', 'postgres'),
            'password': os.getenv('POSTGRES_PASSWORD', 'postgres'),
            'connect_timeout': 10
        }

        try:
            return psycopg2.connect(**conn_params)
        except Exception as e:
            print(f"❌ PostgreSQL connection failed: {e}")
            return None

    def get_stations(self, state: str = None, limit: int = 100) -> List[Dict]:
        """Get weather stations"""
        url = f"{self.BASE_URL}/stations"
        params = {'limit': limit}
        if state:
            params['state'] = state

        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('features', [])
        except Exception as e:
            print(f"⚠️  Error fetching stations: {e}")
            return []

    def get_observations(self, station_id: str) -> Optional[Dict]:
        """Get latest observations from a station"""
        url = f"{self.BASE_URL}/stations/{station_id}/observations/latest"

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"⚠️  Error fetching observations for {station_id}: {e}")
            return None

    def get_forecast(self, grid_id: str, x: int, y: int) -> Optional[Dict]:
        """Get forecast for a grid point"""
        url = f"{self.BASE_URL}/gridpoints/{grid_id}/{x},{y}/forecast"

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"⚠️  Error fetching forecast: {e}")
            return None

    def get_alerts(self, area: str = 'US') -> List[Dict]:
        """Get active weather alerts"""
        url = f"{self.BASE_URL}/alerts/active/area/{area}"

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('features', [])
        except Exception as e:
            print(f"⚠️  Error fetching alerts: {e}")
            return []

    def ingest_stations(self, conn, states: List[str] = None):
        """Ingest weather station data"""
        if states is None:
            states = ['NY', 'CA', 'IL', 'FL', 'WA']  # Sample states

        print(f"\n📥 Ingesting NWS station data...")

        cursor = conn.cursor()
        stations_ingested = 0

        for state in states:
            stations = self.get_stations(state=state, limit=50)

            for station_feature in stations:
                props = station_feature.get('properties', {})
                geom = station_feature.get('geometry', {})

                station_id = props.get('stationIdentifier', '')
                if not station_id:
                    continue

                # Insert or update station
                insert_sql = """
                INSERT INTO weather_stations
                (station_id, station_name, station_latitude, station_longitude,
                 state_code, cwa_code, station_type, active_status,
                 first_observation_date, last_observation_date, update_frequency_minutes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (station_id) DO UPDATE SET
                    station_name = EXCLUDED.station_name,
                    station_latitude = EXCLUDED.station_latitude,
                    station_longitude = EXCLUDED.station_longitude,
                    last_observation_date = EXCLUDED.last_observation_date
                """

                try:
                    cursor.execute(insert_sql, (
                        station_id,
                        props.get('name', ''),
                        geom.get('coordinates', [None, None])[1],  # lat
                        geom.get('coordinates', [None, None])[0],  # lon
                        state,
                        props.get('cwa', [None])[0] if isinstance(props.get('cwa'), list) else props.get('cwa'),
                        'ASOS',  # Default type
                        True,
                        None,  # first_observation_date
                        datetime.now().date(),  # last_observation_date
                        5  # update_frequency_minutes
                    ))
                    stations_ingested += 1
                except Exception as e:
                    print(f"  ⚠️  Error inserting station {station_id}: {e}")
                    conn.rollback()
                    continue

            time.sleep(0.5)  # Rate limiting

        conn.commit()
        cursor.close()
        print(f"  ✅ Ingested {stations_ingested} stations")
        return stations_ingested

    def ingest_observations(self, conn, station_ids: List[str] = None):
        """Ingest latest observations"""
        if station_ids is None:
            # Get stations from database
            cursor = conn.cursor()
            cursor.execute("SELECT station_id FROM weather_stations LIMIT 20")
            station_ids = [row[0] for row in cursor.fetchall()]
            cursor.close()

        print(f"\n📥 Ingesting NWS observations for {len(station_ids)} stations...")

        cursor = conn.cursor()
        observations_ingested = 0

        for station_id in station_ids:
            obs_data = self.get_observations(station_id)
            if not obs_data:
                continue

            props = obs_data.get('properties', {})
            geom = obs_data.get('geometry', {})

            observation_id = f"{station_id}_{props.get('timestamp', datetime.now().isoformat())}"

            insert_sql = """
            INSERT INTO weather_observations
            (observation_id, station_id, station_name, observation_time,
             station_latitude, station_longitude, temperature, dewpoint,
             humidity, wind_speed, wind_direction, pressure, visibility,
             sky_cover, precipitation_amount, data_freshness_minutes,
             load_timestamp, data_source)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (observation_id) DO NOTHING
            """

            try:
                obs_time = datetime.fromisoformat(
                    props.get('timestamp', '').replace('Z', '+00:00')
                )

                cursor.execute(insert_sql, (
                    observation_id,
                    station_id,
                    props.get('station', ''),
                    obs_time,
                    geom.get('coordinates', [None, None])[1],
                    geom.get('coordinates', [None, None])[0],
                    props.get('temperature', {}).get('value'),
                    props.get('dewpoint', {}).get('value'),
                    props.get('relativeHumidity', {}).get('value'),
                    props.get('windSpeed', {}).get('value'),
                    props.get('windDirection', {}).get('value'),
                    props.get('barometricPressure', {}).get('value'),
                    props.get('visibility', {}).get('value'),
                    props.get('skyCondition', ''),
                    props.get('precipitationLastHour', {}).get('value'),
                    0,  # data_freshness_minutes
                    datetime.now(),
                    'NWS_API'
                ))
                observations_ingested += 1
            except Exception as e:
                print(f"  ⚠️  Error inserting observation for {station_id}: {e}")
                conn.rollback()
                continue

            time.sleep(0.2)  # Rate limiting

        conn.commit()
        cursor.close()
        print(f"  ✅ Ingested {observations_ingested} observations")
        return observations_ingested


def main():
    """Main execution"""
    print("="*70)
    print("NWS API DATA INGESTION FOR DB-6")
    print("="*70)

    ingester = NWSAPIIngester(db_type='databricks')
    conn = ingester.get_db_connection()

    if not conn:
        print("❌ Database connection failed")
        return

    try:
        # Ingest stations
        ingester.ingest_stations(conn, states=['NY', 'CA', 'IL', 'FL', 'WA'])

        # Ingest observations
        ingester.ingest_observations(conn)

        print("\n✅ NWS API ingestion complete")

    finally:
        conn.close()


if __name__ == '__main__':
    main()
