#!/usr/bin/env python3
"""
Query Performance Optimizer for db-8
Analyzes queries, identifies optimization opportunities, and suggests index improvements
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
import re

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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QueryPerformanceOptimizer:
    """Analyzes and optimizes SQL queries for performance"""
    
    def __init__(self, db_config: Dict, queries_json_path: Path):
        self.db_config = db_config
        self.queries_json_path = queries_json_path
        self.pg_conn = None
        self.queries = self._load_queries()
        self.optimization_recommendations = []
    
    def _load_queries(self) -> List[Dict]:
        """Load queries from JSON file"""
        if not self.queries_json_path.exists():
            logger.error(f"Queries JSON not found: {self.queries_json_path}")
            return []
        
        data = json.loads(self.queries_json_path.read_text())
        return data.get('queries', [])
    
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
    
    def analyze_query_patterns(self) -> Dict:
        """Analyze query patterns to identify common access patterns"""
        patterns = {
            'table_access': {},
            'join_patterns': {},
            'filter_patterns': {},
            'aggregation_patterns': {},
            'window_function_usage': {},
            'cte_depth': []
        }
        
        for query in self.queries:
            sql = query.get('sql', '')
            
            # Count table accesses
            tables = re.findall(r'\bFROM\s+(\w+)\b|\bJOIN\s+(\w+)\b', sql, re.IGNORECASE)
            for match in tables:
                table = match[0] or match[1]
                patterns['table_access'][table] = patterns['table_access'].get(table, 0) + 1
            
            # Count CTEs
            cte_count = len(re.findall(r'\bWITH\s+\w+\s+AS\b', sql, re.IGNORECASE))
            patterns['cte_depth'].append({
                'query_number': query.get('number'),
                'cte_count': cte_count
            })
            
            # Identify filter patterns
            where_clauses = re.findall(r'\bWHERE\s+([^GROUP|ORDER|LIMIT]+)', sql, re.IGNORECASE | re.DOTALL)
            for clause in where_clauses:
                # Extract column names from WHERE clause
                columns = re.findall(r'\b(\w+)\s*[=<>]', clause, re.IGNORECASE)
                for col in columns:
                    patterns['filter_patterns'][col] = patterns['filter_patterns'].get(col, 0) + 1
        
        return patterns
    
    def recommend_indexes(self, patterns: Dict) -> List[Dict]:
        """Recommend indexes based on query patterns"""
        recommendations = []
        
        # Common filter columns
        filter_columns = sorted(
            patterns['filter_patterns'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:20]  # Top 20 most filtered columns
        
        for column, count in filter_columns:
            # Extract table name from column (simplified - assumes column names are unique or table.column format)
            table = self._guess_table_for_column(column)
            
            if table:
                recommendations.append({
                    'type': 'single_column_index',
                    'table': table,
                    'column': column,
                    'priority': 'high' if count > 5 else 'medium',
                    'usage_count': count,
                    'sql': f"CREATE INDEX IF NOT EXISTS idx_{table}_{column} ON {table}({column});"
                })
        
        # Composite indexes for common join + filter patterns
        # job_postings with location_state and is_active
        recommendations.append({
            'type': 'composite_index',
            'table': 'job_postings',
            'columns': ['posted_date', 'location_state', 'is_active'],
            'priority': 'high',
            'usage_count': 'high',
            'sql': "CREATE INDEX IF NOT EXISTS idx_job_postings_date_location_active ON job_postings(posted_date DESC, location_state, is_active) WHERE is_active = TRUE;"
        })
        
        # user_skills with user_id and skill_id
        recommendations.append({
            'type': 'composite_index',
            'table': 'user_skills',
            'columns': ['user_id', 'skill_id'],
            'priority': 'high',
            'usage_count': 'high',
            'sql': "CREATE INDEX IF NOT EXISTS idx_user_skills_user_skill ON user_skills(user_id, skill_id);"
        })
        
        # job_skills_requirements with job_id and requirement_type
        recommendations.append({
            'type': 'composite_index',
            'table': 'job_skills_requirements',
            'columns': ['job_id', 'requirement_type'],
            'priority': 'high',
            'usage_count': 'high',
            'sql': "CREATE INDEX IF NOT EXISTS idx_job_skills_req_job_type ON job_skills_requirements(job_id, requirement_type);"
        })
        
        return recommendations
    
    def _guess_table_for_column(self, column: str) -> Optional[str]:
        """Guess table name for a column (simplified heuristic)"""
        # Common column patterns
        column_to_table = {
            'user_id': 'user_profiles',
            'job_id': 'job_postings',
            'company_id': 'companies',
            'skill_id': 'skills',
            'application_id': 'job_applications',
            'recommendation_id': 'job_recommendations',
            'trend_id': 'market_trends',
            'posted_date': 'job_postings',
            'location_state': 'job_postings',
            'is_active': 'job_postings',
            'application_status': 'job_applications',
            'match_score': 'job_recommendations',
            'trend_date': 'market_trends'
        }
        
        return column_to_table.get(column)
    
    def analyze_query_complexity(self) -> Dict:
        """Analyze query complexity metrics"""
        complexity_metrics = []
        
        for query in self.queries:
            sql = query.get('sql', '')
            
            metrics = {
                'query_number': query.get('number'),
                'title': query.get('title', ''),
                'cte_count': len(re.findall(r'\bWITH\s+\w+\s+AS\b', sql, re.IGNORECASE)),
                'join_count': len(re.findall(r'\bJOIN\b', sql, re.IGNORECASE)),
                'subquery_count': len(re.findall(r'\(SELECT\b', sql, re.IGNORECASE)),
                'window_function_count': len(re.findall(r'\bOVER\s*\(', sql, re.IGNORECASE)),
                'aggregation_count': len(re.findall(r'\b(COUNT|SUM|AVG|MAX|MIN|GROUP BY)\b', sql, re.IGNORECASE)),
                'sql_length': len(sql),
                'estimated_complexity': 'low'
            }
            
            # Calculate complexity score
            complexity_score = (
                metrics['cte_count'] * 2 +
                metrics['join_count'] * 1.5 +
                metrics['subquery_count'] * 1.5 +
                metrics['window_function_count'] * 2 +
                metrics['aggregation_count'] * 1
            )
            
            if complexity_score > 20:
                metrics['estimated_complexity'] = 'very_high'
            elif complexity_score > 15:
                metrics['estimated_complexity'] = 'high'
            elif complexity_score > 10:
                metrics['estimated_complexity'] = 'medium'
            else:
                metrics['estimated_complexity'] = 'low'
            
            metrics['complexity_score'] = complexity_score
            complexity_metrics.append(metrics)
        
        return {
            'queries': complexity_metrics,
            'summary': {
                'total_queries': len(complexity_metrics),
                'avg_complexity_score': sum(m['complexity_score'] for m in complexity_metrics) / len(complexity_metrics) if complexity_metrics else 0,
                'high_complexity_count': sum(1 for m in complexity_metrics if m['estimated_complexity'] in ['high', 'very_high'])
            }
        }
    
    def generate_optimization_report(self) -> Dict:
        """Generate comprehensive optimization report"""
        patterns = self.analyze_query_patterns()
        index_recommendations = self.recommend_indexes(patterns)
        complexity_analysis = self.analyze_query_complexity()
        
        report = {
            'report_date': get_est_timestamp(),
            'database': 'db-8',
            'query_patterns': patterns,
            'index_recommendations': index_recommendations,
            'complexity_analysis': complexity_analysis,
            'optimization_priority': {
                'high': [r for r in index_recommendations if r.get('priority') == 'high'],
                'medium': [r for r in index_recommendations if r.get('priority') == 'medium'],
                'low': [r for r in index_recommendations if r.get('priority') == 'low']
            }
        }
        
        return report
    
    def save_report(self, report: Dict, output_path: Path):
        """Save optimization report to file"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2, default=str))
        logger.info(f"Optimization report saved to {output_path}")


def main():
    """Main optimization function"""
    db_config = {
        'host': os.environ.get('PG_HOST', 'localhost'),
        'port': int(os.environ.get('PG_PORT', 5432)),
        'database': os.environ.get('PG_DATABASE', 'db_8_validation'),
        'user': os.environ.get('PG_USER', 'postgres'),
        'password': os.environ.get('PG_PASSWORD', '')
    }
    
    queries_json_path = Path(__file__).parent.parent / 'queries' / 'queries.json'
    
    optimizer = QueryPerformanceOptimizer(db_config, queries_json_path)
    
    # Generate report
    report = optimizer.generate_optimization_report()
    
    # Save report
    output_path = Path(__file__).parent.parent / 'results' / f"query_optimization_report_{get_est_timestamp()}.json"
    optimizer.save_report(report, output_path)
    
    print("\n" + "="*70)
    print("Query Performance Optimization Report")
    print("="*70)
    print(f"Total Queries Analyzed: {report['complexity_analysis']['summary']['total_queries']}")
    print(f"Average Complexity Score: {report['complexity_analysis']['summary']['avg_complexity_score']:.2f}")
    print(f"High Complexity Queries: {report['complexity_analysis']['summary']['high_complexity_count']}")
    print(f"\nIndex Recommendations: {len(report['index_recommendations'])}")
    print(f"  - High Priority: {len(report['optimization_priority']['high'])}")
    print(f"  - Medium Priority: {len(report['optimization_priority']['medium'])}")
    print("="*70)
    print(f"\nReport saved to: {output_path}")


if __name__ == '__main__':
    main()
