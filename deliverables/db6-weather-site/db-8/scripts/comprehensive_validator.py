#!/usr/bin/env python3
"""
Comprehensive validation script for db-8 queries.md
Performs syntax validation, execution testing, and comprehensive evaluation
Phase 2 & 4: Syntax Validation and Comprehensive Evaluation
"""

import os
import re
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import traceback

# Import timestamp utility (try local first, then root scripts)
try:
    from timestamp_utils import get_est_timestamp
except ImportError:
    # Try importing from root scripts directory
    root_scripts = Path(__file__).parent.parent.parent / 'scripts'
    sys.path.insert(0, str(root_scripts))
    from timestamp_utils import get_est_timestamp

# Database connection imports
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PG_AVAILABLE = True
except ImportError:
    PG_AVAILABLE = False

try:
    import snowflake.connector
    SNOWFLAKE_AVAILABLE = True
except ImportError:
    SNOWFLAKE_AVAILABLE = False

try:
    from databricks import sql
    DATABRICKS_AVAILABLE = True
except ImportError:
    DATABRICKS_AVAILABLE = False

class QueryExtractor:
    """Extract SQL queries from queries.md files"""

    @staticmethod
    def extract_queries(md_file: Path) -> List[Dict[str, str]]:
        """Extract queries from markdown file"""
        queries = []

        if not md_file.exists():
            return queries

        content = md_file.read_text(encoding='utf-8')

        # Pattern to find all query headers
        query_header_pattern = r'^## Query (\d+):\s*(.+)$'
        headers = list(re.finditer(query_header_pattern, content, re.MULTILINE))

        for i, header_match in enumerate(headers):
            query_num = int(header_match.group(1))
            title = header_match.group(2).strip()
            start_pos = header_match.start()

            # Find the end position (next query header or end of file)
            if i + 1 < len(headers):
                end_pos = headers[i + 1].start()
            else:
                end_pos = len(content)

            # Extract the section for this query
            query_section = content[start_pos:end_pos]

            # Find SQL code block in this section
            sql_pattern = r'```(?:sql)?\n(.*?)```'
            sql_match = re.search(sql_pattern, query_section, re.DOTALL)

            if sql_match:
                sql = sql_match.group(1).strip()

                queries.append({
                    'number': query_num,
                    'title': title,
                    'sql': sql,
                    'description': title[:200] if title else f"Query {query_num}"
                })

        return sorted(queries, key=lambda x: x['number'])

class SyntaxValidator:
    """Validate SQL syntax on different databases"""

    def __init__(self):
        self.pg_conn = None
        self.sf_conn = None
        self.db_conn = None
        self.results = {
            'postgresql': {'available': False, 'queries': []},
            'snowflake': {'available': False, 'queries': []},
            'databricks': {'available': False, 'queries': []}
        }

    def connect_postgresql(self, config: Dict) -> bool:
        """Connect to PostgreSQL"""
        if not PG_AVAILABLE:
            return False

        try:
            self.pg_conn = psycopg2.connect(
                host=config.get('host', 'localhost'),
                port=config.get('port', 5432),
                database=config.get('database', 'postgres'),
                user=config.get('user', os.environ.get('USER', 'postgres')),
                password=config.get('password', '')
            )
            self.results['postgresql']['available'] = True
            return True
        except Exception as e:
            print(f"PostgreSQL connection failed: {e}")
            return False

    def connect_databricks(self, config: Dict) -> bool:
        """Connect to Databricks"""
        if not DATABRICKS_AVAILABLE:
            return False

        try:
            self.db_conn = sql.connect(
                server_hostname=config.get('server_hostname'),
                http_path=config.get('http_path'),
                access_token=config.get('access_token')
            )
            self.results['databricks']['available'] = True
            return True
        except Exception as e:
            print(f"Databricks connection failed: {e}")
            return False

    def validate_syntax_postgresql(self, query: Dict) -> Dict:
        """Validate SQL syntax on PostgreSQL using EXPLAIN"""
        result = {
            'query_number': query['number'],
            'success': False,
            'error': None,
            'error_type': None
        }

        if not self.pg_conn:
            result['error'] = 'PostgreSQL not connected'
            return result

        try:
            cursor = self.pg_conn.cursor()
            # Use EXPLAIN to validate syntax without executing
            explain_sql = f"EXPLAIN {query['sql']}"
            cursor.execute(explain_sql)
            cursor.fetchall()  # Consume results
            cursor.close()
            result['success'] = True
        except Exception as e:
            result['error'] = str(e)
            result['error_type'] = type(e).__name__

        return result

    def validate_syntax_databricks(self, query: Dict) -> Dict:
        """Validate SQL syntax on Databricks using EXPLAIN"""
        result = {
            'query_number': query['number'],
            'success': False,
            'error': None,
            'error_type': None
        }

        if not self.db_conn:
            result['error'] = 'Databricks not connected'
            return result

        try:
            cursor = self.db_conn.cursor()
            # Use EXPLAIN to validate syntax
            explain_sql = f"EXPLAIN {query['sql']}"
            cursor.execute(explain_sql)
            cursor.fetchall()
            cursor.close()
            result['success'] = True
        except Exception as e:
            result['error'] = str(e)
            result['error_type'] = type(e).__name__

        return result

    def validate_all_queries(self, queries: List[Dict], pg_config: Dict = None, db_config: Dict = None):
        """Validate syntax for all queries"""
        print("\n" + "="*70)
        print("Syntax Validation")
        print("="*70)

        # PostgreSQL validation
        if pg_config and self.connect_postgresql(pg_config):
            print(f"\nValidating on PostgreSQL...")
            for query in queries:
                print(f"  Query {query['number']}/{len(queries)}...", end=' ', flush=True)
                result = self.validate_syntax_postgresql(query)
                self.results['postgresql']['queries'].append(result)
                if result['success']:
                    print("✓")
                else:
                    print(f"✗ {result['error'][:60]}")
            if self.pg_conn:
                self.pg_conn.close()

        # Databricks validation
        if db_config and self.connect_databricks(db_config):
            print(f"\nValidating on Databricks...")
            for query in queries:
                print(f"  Query {query['number']}/{len(queries)}...", end=' ', flush=True)
                result = self.validate_syntax_databricks(query)
                self.results['databricks']['queries'].append(result)
                if result['success']:
                    print("✓")
                else:
                    print(f"✗ {result['error'][:60]}")
            if self.db_conn:
                self.db_conn.close()

class QueryEvaluator:
    """Evaluate queries against requirements"""

    @staticmethod
    def evaluate_query_count(queries: List[Dict]) -> Dict:
        """Evaluate query count"""
        count = len(queries)
        return {
            'requirement': 'Exactly 30 queries',
            'found': count,
            'Pass': 1 if count == 30 else 0,  # Binary: 1 = pass, 0 = fail
            'notes': [f'Found {count} queries, expected 30'] if count != 30 else []
        }

    @staticmethod
    def evaluate_recursive_cte_usage(queries: List[Dict]) -> Dict:
        """Evaluate recursive CTE usage"""
        results = []
        for query in queries:
            # Check for WITH RECURSIVE
            sql_upper = query['sql'].upper()
            has_recursive = bool(re.search(r'\bWITH\s+RECURSIVE\b', sql_upper))

            claims_recursive = 'recursive' in query['description'].lower() or 'recursive' in query['title'].lower()

            status = 'PASS'
            if claims_recursive and not has_recursive:
                status = 'FAIL'
            elif has_recursive and not claims_recursive:
                status = 'WARNING'  # Has recursive but doesn't claim it

            results.append({
                'query_number': query['number'],
                'has_recursive': has_recursive,
                'claims_recursive': claims_recursive,
                'status': status
            })

        mismatched = [r for r in results if r['status'] == 'FAIL']
        return {
            'requirement': 'Queries claiming recursive CTE must have WITH RECURSIVE',
            'total_queries': len(queries),
            'queries_with_recursive': sum(1 for r in results if r['has_recursive']),
            'mismatched': len(mismatched),
            'Pass': 1 if len(mismatched) == 0 else 0,  # Binary: 1 = pass, 0 = fail
            'details': results,
            'mismatched_queries': mismatched,
            'notes': [f'{len(mismatched)} queries with mismatched recursive CTE claims'] if mismatched else []
        }

    @staticmethod
    def evaluate_cte_usage(queries: List[Dict]) -> Dict:
        """Evaluate CTE usage"""
        results = []
        for query in queries:
            has_cte = 'WITH ' in query['sql'].upper()
            results.append({
                'query_number': query['number'],
                'has_cte': has_cte
            })

        queries_without_cte = [r for r in results if not r['has_cte']]
        return {
            'requirement': 'All queries must use CTEs',
            'total_queries': len(queries),
            'queries_with_cte': sum(1 for r in results if r['has_cte']),
            'queries_without_cte': len(queries_without_cte),
            'Pass': 1 if len(queries_without_cte) == 0 else 0,  # Binary: 1 = pass, 0 = fail
            'queries_without_cte_list': queries_without_cte,
            'notes': [f'{len(queries_without_cte)} queries without CTEs'] if queries_without_cte else []
        }

    @staticmethod
    def evaluate_complexity(queries: List[Dict]) -> Dict:
        """Evaluate query complexity"""
        complexity_scores = []
        for query in queries:
            sql_upper = query['sql'].upper()
            # Count CTEs - look for WITH ... AS patterns
            cte_pattern = r'\bWITH\s+(?:RECURSIVE\s+)?\w+\s+AS\s*\('
            cte_matches = re.findall(cte_pattern, sql_upper)
            cte_count = len(cte_matches)

            # Count recursive CTEs
            recursive_cte_count = len(re.findall(r'\bWITH\s+RECURSIVE\b', sql_upper))

            score = {
                'query_number': query['number'],
                'cte_count': cte_count,
                'recursive_cte_count': recursive_cte_count,
                'join_count': len(re.findall(r'\b(INNER|LEFT|RIGHT|FULL)\s+JOIN\b', sql_upper)),
                'window_function_count': len(re.findall(r'\b(ROW_NUMBER|RANK|DENSE_RANK|LEAD|LAG|PERCENT_RANK|NTILE|FIRST_VALUE|LAST_VALUE)\s*\(', sql_upper)),
                'aggregation_count': len(re.findall(r'\b(COUNT|SUM|AVG|MAX|MIN|PERCENTILE_CONT|PERCENTILE_DISC)\s*\(', sql_upper)),
                'subquery_count': len(re.findall(r'\(\s*SELECT\s+', sql_upper))
            }
            complexity_scores.append(score)

        avg_cte = sum(s['cte_count'] for s in complexity_scores) / len(complexity_scores) if complexity_scores else 0
        avg_join = sum(s['join_count'] for s in complexity_scores) / len(complexity_scores) if complexity_scores else 0
        avg_window = sum(s['window_function_count'] for s in complexity_scores) / len(complexity_scores) if complexity_scores else 0

        return {
            'requirement': 'Queries must demonstrate high complexity',
            'complexity_scores': complexity_scores,
            'average_cte_count': avg_cte,
            'average_join_count': avg_join,
            'average_window_function_count': avg_window,
            'Pass': 1 if avg_cte >= 1.0 and avg_join >= 1.0 else 0  # Binary: 1 = pass, 0 = fail
        }

def main():
    """Main validation function"""
    script_dir = Path(__file__).parent
    queries_file = script_dir.parent / 'queries' / 'queries.md'
    results_file = script_dir.parent / 'results' / 'comprehensive_validation_report.json'

    if not queries_file.exists():
        print(f"Error: {queries_file} not found")
        return

    print("="*70)
    print("Comprehensive Validation for db-8 queries.md")
    print("="*70)

    # Extract queries
    extractor = QueryExtractor()
    queries = extractor.extract_queries(queries_file)

    if len(queries) != 30:
        print(f"Warning: Expected 30 queries, found {len(queries)}")

    print(f"\nExtracted {len(queries)} queries")

    # Initialize results
    results = {
        'validation_date': get_est_timestamp(),  # EST format: YYYYMMDD-HHMM
        'database': 'db-8',
        'file': str(queries_file),
        'total_queries': len(queries),
        'syntax_validation': {},
        'evaluation': {}
    }

    # Phase 2: Syntax Validation
    validator = SyntaxValidator()

    # Database configurations
    pg_config = {
        'host': os.environ.get('PG_HOST', 'localhost'),
        'port': int(os.environ.get('PG_PORT', 5432)),
        'user': os.environ.get('PG_USER', os.environ.get('USER', 'postgres')),
        'password': os.environ.get('PG_PASSWORD', ''),
        'database': os.environ.get('PG_DATABASE', 'db_8_validation')
    }

    db_config = {
        'server_hostname': os.environ.get('DATABRICKS_SERVER_HOSTNAME'),
        'http_path': os.environ.get('DATABRICKS_HTTP_PATH'),
        'access_token': os.environ.get('DATABRICKS_TOKEN')
    }

    # Check if configs are available
    if not all([db_config.get('server_hostname'), db_config.get('http_path'), db_config.get('access_token')]):
        print("\n⚠️  Databricks credentials not found. Skipping Databricks validation.")
        db_config = None

    if not PG_AVAILABLE:
        print("\n⚠️  psycopg2 not available. Skipping PostgreSQL validation.")
        pg_config = None

    validator.validate_all_queries(queries, pg_config, db_config)
    results['syntax_validation'] = validator.results

    # Phase 4: Comprehensive Evaluation
    print("\n" + "="*70)
    print("Comprehensive Evaluation")
    print("="*70)

    evaluator = QueryEvaluator()

    # Query count
    count_result = evaluator.evaluate_query_count(queries)
    print(f"\nQuery Count: {count_result['found']}/30 - Pass={count_result['Pass']}")
    results['evaluation']['query_count'] = count_result

    # Recursive CTE usage
    recursive_result = evaluator.evaluate_recursive_cte_usage(queries)
    print(f"Recursive CTE Usage: {recursive_result['queries_with_recursive']} queries with recursive CTE")
    if recursive_result['mismatched'] > 0:
        print(f"  ⚠️  {recursive_result['mismatched']} queries with mismatched claims")
    results['evaluation']['recursive_cte_usage'] = recursive_result

    # CTE usage
    cte_result = evaluator.evaluate_cte_usage(queries)
    print(f"CTE Usage: {cte_result['queries_with_cte']}/{cte_result['total_queries']} queries use CTEs")
    if cte_result['queries_without_cte'] > 0:
        print(f"  ⚠️  {cte_result['queries_without_cte']} queries without CTEs")
    results['evaluation']['cte_usage'] = cte_result

    # Complexity
    complexity_result = evaluator.evaluate_complexity(queries)
    print(f"Complexity: Avg {complexity_result['average_cte_count']:.1f} CTEs, "
          f"{complexity_result['average_join_count']:.1f} joins, "
          f"{complexity_result['average_window_function_count']:.1f} window functions per query")
    results['evaluation']['complexity'] = complexity_result

    # Save results
    results_file.parent.mkdir(parents=True, exist_ok=True)
    results_file.write_text(json.dumps(results, indent=2, default=str, ensure_ascii=False))
    print(f"\n{'='*70}")
    print(f"Results saved to: {results_file}")
    print("="*70)

if __name__ == '__main__':
    main()
