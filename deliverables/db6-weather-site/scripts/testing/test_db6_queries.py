#!/usr/bin/env python3
"""
Test db-6 queries against PostgreSQL
Uses credentials from databricks_credentials.json
"""

import re
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import traceback

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    print("⚠️  psycopg2 not available. PostgreSQL testing will be skipped.")

try:
    import databricks.connector
    SNOWFLAKE_AVAILABLE = True
except ImportError:
    SNOWFLAKE_AVAILABLE = False
    print("⚠️  databricks-connector-python not available. Databricks testing will be skipped.")


class QueryParser:
    """Parse queries from queries.md files"""

    @staticmethod
    def extract_queries(markdown_file: Path) -> List[Dict[str, str]]:
        """Extract all SQL queries from a queries.md file"""
        with open(markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()

        queries = []

        # Pattern to match query sections: ## Query N: Description
        query_pattern = r'## Query (\d+):\s*(.+?)(?=## Query \d+:|```sql|$)'
        query_matches = list(re.finditer(query_pattern, content, re.DOTALL | re.IGNORECASE))

        # Also find SQL code blocks (exclude test sections)
        sql_pattern = r'```sql\s*(.*?)```'
        sql_blocks = []
        for match in re.finditer(sql_pattern, content, re.DOTALL | re.IGNORECASE):
            sql_content = match.group(1).strip()
            # Skip test sections that contain ellipsis or test comments
            if '-- Test' in sql_content or sql_content.count('...') > 2:
                continue
            sql_blocks.append(match)

        # Match queries with their SQL blocks
        for i, query_match in enumerate(query_matches):
            query_num = int(query_match.group(1))
            description = query_match.group(2).strip()

            # Find the SQL block that follows this query description
            query_start = query_match.end()
            sql_block = None

            # Find the next SQL block after this query header
            for sql_match in sql_blocks:
                if sql_match.start() > query_start:
                    # Check if there's a closer query header between this header and the SQL block
                    has_closer_header = False
                    for j, other_match in enumerate(query_matches):
                        if other_match.start() > query_start and other_match.start() < sql_match.start():
                            has_closer_header = True
                            break

                    if not has_closer_header:
                        sql_block = sql_match.group(1).strip()
                        # Remove ellipsis, test sections, and incomplete lines
                        lines = sql_block.split('\n')
                        cleaned_lines = []
                        skip_rest = False
                        for line in lines:
                            # Stop at test sections
                            if '-- Test' in line or 'Test Execution' in line:
                                skip_rest = True
                                break
                            # Skip lines with just "..." or incomplete code
                            if line.strip() == '...' or (line.strip().startswith('--') and '...' in line):
                                continue
                            # Skip lines that are just ellipsis in comments
                            if re.match(r'^\s*--\s*\.\.\.\s*$', line):
                                continue
                            cleaned_lines.append(line)

                        sql_block = '\n'.join(cleaned_lines).strip()
                        # Only use if it's a complete query (ends with semicolon)
                        if sql_block and sql_block.endswith(';'):
                            break
                        else:
                            sql_block = None

            if sql_block:
                queries.append({
                    'number': query_num,
                    'description': description,
                    'sql': sql_block
                })

        # If no structured queries found, extract all SQL blocks
        if not queries and sql_blocks:
            for i, sql_match in enumerate(sql_blocks, 1):
                queries.append({
                    'number': i,
                    'description': f'Query {i}',
                    'sql': sql_match.group(1).strip()
                })

        return sorted(queries, key=lambda x: x['number'])


class DatabaseTester:
    """Test SQL queries against databases"""

    def __init__(self, db_name: str, db_num: int, databricks_creds: Optional[Dict] = None):
        self.db_name = db_name
        self.db_num = db_num
        self.databricks_creds = databricks_creds or {}
        self.results = {
            'database': db_name,
            'database_number': db_num,
            'test_timestamp': datetime.now().isoformat(),
            'postgresql': {'available': POSTGRES_AVAILABLE, 'queries': []},
            'databricks': {'available': SNOWFLAKE_AVAILABLE, 'queries': []}
        }

    def get_postgres_connection(self):
        """Get PostgreSQL connection"""
        if not POSTGRES_AVAILABLE:
            return None

        import os
        # Map database numbers to ports: db1=5432, db2=5433, etc.
        port_mapping = {
            1: 5432,
            2: 5433,
            3: 5434,
            4: 5435,
            5: 5436,
            6: 5437  # db-6 uses port 5437
        }
        default_port = port_mapping.get(self.db_num, 5432)

        host = os.getenv('POSTGRES_HOST', 'localhost')
        if host == 'localhost':
            host = '127.0.0.1'

        db_specific_port = os.getenv(f'POSTGRES_PORT_DB{self.db_num}')
        if db_specific_port:
            port = int(db_specific_port)
        else:
            port = default_port

        conn_params = {
            'host': host,
            'port': port,
            'database': os.getenv('POSTGRES_DB', f'db{self.db_num}'),
            'user': os.getenv('POSTGRES_USER', 'postgres'),
            'password': os.getenv('POSTGRES_PASSWORD', 'postgres'),
            'connect_timeout': 10
        }

        try:
            return psycopg2.connect(**conn_params)
        except Exception as e:
            print(f"⚠️  PostgreSQL connection failed: {e}")
            return None

    def get_databricks_connection(self):
        """Get Databricks connection using credentials from JSON"""
        if not SNOWFLAKE_AVAILABLE:
            return None

        import os
        import base64
        import json as json_lib

        # Use credentials from JSON file if provided
        token = self.databricks_creds.get('databricks_token') or os.getenv('SNOWFLAKE_TOKEN')
        account = self.databricks_creds.get('databricks_account') or os.getenv('SNOWFLAKE_ACCOUNT', '')
        user = self.databricks_creds.get('databricks_user') or os.getenv('SNOWFLAKE_USER', '')

        # Try to decode token to get account info if not provided
        if token and not account:
            try:
                parts = token.split('.')
                if len(parts) >= 2:
                    payload = parts[1]
                    payload += '=' * (4 - len(payload) % 4)
                    decoded = json_lib.loads(base64.urlsafe_b64decode(payload))

                    if 'iss' in decoded:
                        iss = decoded['iss']
                        if iss.startswith('SF:'):
                            account = iss.split(':')[1]

                    if 'p' in decoded:
                        p_val = decoded['p']
                        if ':' in str(p_val):
                            user = str(p_val).split(':')[0]
            except:
                pass

        # Get role from credentials or environment
        role = self.databricks_creds.get('databricks_role') or os.getenv('SNOWFLAKE_ROLE', 'ACCOUNTADMIN')

        conn_params = {
            'account': account or os.getenv('SNOWFLAKE_ACCOUNT', ''),
            'user': user or os.getenv('SNOWFLAKE_USER', ''),
            'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH'),
            'database': os.getenv('SNOWFLAKE_DATABASE', f'DB{self.db_num}'),
            'schema': os.getenv('SNOWFLAKE_SCHEMA', 'PUBLIC'),
            'role': role
        }

        # Format account properly - try different formats
        account_formats = []
        if account:
            # Check if account has organization prefix (format: ORG-ACCOUNT)
            if '-' in account:
                # Account already in correct format (e.g., NNLTTOD-OP02778)
                account_formats = [account]
            elif '.' in account:
                # Account with dot separator
                account_formats = [account]
            else:
                # Try common region formats for GCP
                # Get organization if available
                org = self.databricks_creds.get('databricks_organization', '')
                if org:
                    account_formats = [
                        f"{org}-{account}",  # ORG-ACCOUNT format
                        account  # Just account name
                    ]
                else:
                    # Try common GCP region formats
                    account_formats = [
                        account,  # Just the account ID
                        f"{account}.us-central1",  # GCP region
                        f"{account}.us-east1",
                        f"{account}.us-west1"
                    ]

        # Use token if available
        # Note: Databricks Python connector token authentication may require different setup
        # Try multiple authentication methods and account formats
        last_error = None

        if token:
            # Method 1: Try OAuth with token as password
            for acc_format in account_formats:
                try:
                    test_params = conn_params.copy()
                    test_params['account'] = acc_format
                    test_params['password'] = token
                    test_params['authenticator'] = 'oauth'
                    conn = databricks.connector.connect(**test_params)
                    print(f"✅ Connected to Databricks using account: {acc_format}")
                    return conn
                except Exception as e1:
                    last_error = e1
                    # Method 2: Try without authenticator (token as password)
                    try:
                        test_params = conn_params.copy()
                        test_params['account'] = acc_format
                        test_params['password'] = token
                        if 'authenticator' in test_params:
                            del test_params['authenticator']  # Remove authenticator
                        conn = databricks.connector.connect(**test_params)
                        print(f"✅ Connected to Databricks using account: {acc_format}")
                        return conn
                    except Exception as e2:
                        last_error = e2
                        continue

        # Try password-based authentication if token didn't work
        password = os.getenv('SNOWFLAKE_PASSWORD', '')
        if password:
            for acc_format in account_formats:
                try:
                    test_params = conn_params.copy()
                    test_params['account'] = acc_format
                    test_params['password'] = password
                    if 'authenticator' in test_params:
                        del test_params['authenticator']
                    conn = databricks.connector.connect(**test_params)
                    print(f"✅ Connected to Databricks using account: {acc_format}")
                    return conn
                except Exception as e:
                    last_error = e
                    continue

        if not account:
            print(f"⚠️  Databricks credentials not configured.")
        else:
            print(f"⚠️  Databricks connection failed. Last error: {last_error}")
            print(f"   Tried account formats: {account_formats}")
            print(f"   Note: Token authentication may require additional setup.")
            print(f"   Consider using password-based authentication or checking account format.")

        return None

    def test_query_postgres(self, query: Dict[str, str], conn) -> Dict:
        """Test a single query against PostgreSQL"""
        result = {
            'query_number': query['number'],
            'description': query['description'],
            'success': False,
            'execution_time_ms': 0,
            'row_count': 0,
            'error': None,
            'error_type': None
        }

        if not conn:
            result['error'] = 'PostgreSQL connection not available'
            return result

        try:
            start_time = time.time()
            conn.rollback()

            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query['sql'])

                rows = cursor.fetchmany(1000)
                result['row_count'] = len(rows)

                if rows:
                    result['columns'] = list(rows[0].keys())

                if cursor.fetchone():
                    result['truncated'] = True
                    result['note'] = 'Results truncated to first 1000 rows'

            result['execution_time_ms'] = (time.time() - start_time) * 1000
            result['success'] = True

        except Exception as e:
            result['error'] = str(e)
            result['error_type'] = type(e).__name__
            result['execution_time_ms'] = (time.time() - start_time) * 1000

        return result

    def test_query_databricks(self, query: Dict[str, str], conn) -> Dict:
        """Test a single query against Databricks"""
        result = {
            'query_number': query['number'],
            'description': query['description'],
            'success': False,
            'execution_time_ms': 0,
            'row_count': 0,
            'error': None,
            'error_type': None
        }

        if not conn:
            result['error'] = 'Databricks connection not available'
            return result

        try:
            start_time = time.time()
            cursor = conn.cursor()

            cursor.execute(query['sql'])

            rows = cursor.fetchmany(1000)
            result['row_count'] = len(rows)

            if cursor.description:
                result['columns'] = [desc[0] for desc in cursor.description]

            if cursor.fetchone():
                result['truncated'] = True
                result['note'] = 'Results truncated to first 1000 rows'

            cursor.close()

            result['execution_time_ms'] = (time.time() - start_time) * 1000
            result['success'] = True

        except Exception as e:
            result['error'] = str(e)
            result['error_type'] = type(e).__name__
            result['execution_time_ms'] = (time.time() - start_time) * 1000

        return result

    def test_all_queries(self, queries: List[Dict[str, str]]):
        """Test all queries against both databases"""
        print(f"\n{'='*70}")
        print(f"Testing {len(queries)} queries for {self.db_name}")
        print(f"{'='*70}")

        # Test PostgreSQL
        if POSTGRES_AVAILABLE:
            print(f"\n📊 Testing PostgreSQL...")
            pg_conn = self.get_postgres_connection()
            if pg_conn:
                for query in queries:
                    result = self.test_query_postgres(query, pg_conn)
                    self.results['postgresql']['queries'].append(result)
                    status = "✅" if result['success'] else "❌"
                    print(f"  {status} Query {query['number']}: {result['execution_time_ms']:.2f}ms, {result['row_count']} rows")
                    if not result['success']:
                        print(f"     Error: {result['error']}")
                pg_conn.close()
            else:
                print("  ⚠️  PostgreSQL connection not available")
        else:
            print("  ⚠️  PostgreSQL testing skipped (psycopg2 not installed)")

        # Test Databricks
        if SNOWFLAKE_AVAILABLE:
            print(f"\n❄️  Testing Databricks...")
            sf_conn = self.get_databricks_connection()
            if sf_conn:
                for query in queries:
                    result = self.test_query_databricks(query, sf_conn)
                    self.results['databricks']['queries'].append(result)
                    status = "✅" if result['success'] else "❌"
                    print(f"  {status} Query {query['number']}: {result['execution_time_ms']:.2f}ms, {result['row_count']} rows")
                    if not result['success']:
                        print(f"     Error: {result['error']}")
                sf_conn.close()
            else:
                print("  ⚠️  Databricks connection not available")
        else:
            print("  ⚠️  Databricks testing skipped (databricks-connector-python not installed)")

        # Calculate statistics
        self._calculate_statistics()

    def _calculate_statistics(self):
        """Calculate test statistics"""
        for db_type in ['postgresql', 'databricks']:
            queries = self.results[db_type].get('queries', [])
            if queries:
                successful = [q for q in queries if q['success']]
                failed = [q for q in queries if not q['success']]

                self.results[db_type]['statistics'] = {
                    'total_queries': len(queries),
                    'successful': len(successful),
                    'failed': len(failed),
                    'success_rate': len(successful) / len(queries) * 100 if queries else 0,
                    'avg_execution_time_ms': sum(q['execution_time_ms'] for q in successful) / len(successful) if successful else 0,
                    'total_rows_returned': sum(q['row_count'] for q in successful)
                }

    def save_results(self, output_path: Path):
        """Save results to JSON file"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"\n✅ Results saved to: {output_path}")


def main():
    """Main execution"""
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent.parent

    print("="*70)
    print("TESTING DB-6 QUERIES")
    print("="*70)
    print(f"\nPostgreSQL available: {POSTGRES_AVAILABLE}")
    print(f"Databricks available: {SNOWFLAKE_AVAILABLE}")

    if not POSTGRES_AVAILABLE and not SNOWFLAKE_AVAILABLE:
        print("\n⚠️  No database connectors available. Install:")
        print("   pip install psycopg2-binary databricks-connector-python")
        return

    # Load Databricks credentials and set environment variables
    creds_file = root_dir / 'results' / 'databricks_credentials.json'
    databricks_creds = {}
    if creds_file.exists():
        with open(creds_file, 'r') as f:
            databricks_creds = json.load(f)
        print(f"\n✅ Loaded Databricks credentials from {creds_file}")

        # Set environment variables for Databricks connection
        import os
        if 'databricks_token' in databricks_creds:
            os.environ['SNOWFLAKE_TOKEN'] = databricks_creds['databricks_token']
        if 'databricks_account' in databricks_creds:
            os.environ['SNOWFLAKE_ACCOUNT'] = databricks_creds['databricks_account']
        if 'databricks_user' in databricks_creds:
            os.environ['SNOWFLAKE_USER'] = databricks_creds['databricks_user']
    else:
        print(f"\n⚠️  Databricks credentials file not found: {creds_file}")

    # Test db-6
    db_dir = root_dir / 'db-6'
    queries_file = db_dir / 'queries' / 'queries.md'

    if not queries_file.exists():
        print(f"\n⚠️  Queries file not found: {queries_file}")
        return

    # Parse queries
    print(f"\n📖 Parsing queries from db-6...")
    parser = QueryParser()
    queries = parser.extract_queries(queries_file)

    if not queries:
        print(f"  ⚠️  No queries found in {queries_file}")
        return

    print(f"  ✅ Found {len(queries)} queries")

    # Test queries
    tester = DatabaseTester('db-6', 6, databricks_creds)
    tester.test_all_queries(queries)

    # Save results
    results_file = db_dir / 'results' / 'query_test_results_postgres.json'
    tester.save_results(results_file)

    print("\n" + "="*70)
    print("TESTING COMPLETE")
    print("="*70)


if __name__ == '__main__':
    main()
