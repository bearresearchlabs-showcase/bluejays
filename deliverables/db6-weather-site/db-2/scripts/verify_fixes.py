#!/usr/bin/env python3
"""
Verify that all fixes were applied correctly to queries.md
"""

import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

class FixVerifier:
    """Verify all fixes were applied correctly"""

    def __init__(self, queries_file: Path):
        self.queries_file = queries_file
        self.content = queries_file.read_text(encoding='utf-8')
        self.results = {
            'verification_date': datetime.now().isoformat(),
            'file': str(queries_file),
            'fixes': {}
        }

    def verify_query_2_array_syntax(self) -> Dict:
        """Verify Query 2 array syntax fix"""
        result = {
            'query_number': 2,
            'fix': 'Array slicing syntax replacement',
            'status': 'PASS',
            'checks': []
        }

        # Check 1: path_preview_cte exists
        if 'path_preview_cte AS (' in self.content:
            result['checks'].append({'check': 'path_preview_cte CTE exists', 'status': 'PASS'})
        else:
            result['checks'].append({'check': 'path_preview_cte CTE exists', 'status': 'FAIL'})
            result['status'] = 'FAIL'

        # Check 2: No array slicing syntax [start:end] (PostgreSQL-specific)
        # Look for patterns like array[1:5] or array[start:end] but not ARRAY[...] constructors
        query_2_section = self._extract_query_section(2)
        array_slicing_pattern = r'(\w+)\[(\d+|\w+):(\d+|\w+)\]'
        matches = re.findall(array_slicing_pattern, query_2_section if query_2_section else self.content)
        # Filter out false positives - only check if it's not an ARRAY constructor
        actual_slicing = [m for m in matches if m[0].upper() != 'ARRAY']
        if not actual_slicing:
            result['checks'].append({'check': 'No array slicing syntax [start:end]', 'status': 'PASS'})
        else:
            result['checks'].append({
                'check': 'No array slicing syntax [start:end]',
                'status': 'FAIL',
                'found': actual_slicing[:5]  # Show first 5 matches
            })
            result['status'] = 'FAIL'

        # Check 3: ARRAY_LENGTH bounds checking present
        if 'ARRAY_LENGTH(ns.optimal_path, 1)' in self.content:
            result['checks'].append({'check': 'ARRAY_LENGTH bounds checking present', 'status': 'PASS'})
        else:
            result['checks'].append({'check': 'ARRAY_LENGTH bounds checking present', 'status': 'FAIL'})
            result['status'] = 'FAIL'

        # Check 4: FROM path_preview_cte ppc (not network_statistics ns)
        if query_2_section:
            if 'FROM path_preview_cte ppc' in query_2_section:
                result['checks'].append({'check': 'FROM clause uses path_preview_cte', 'status': 'PASS'})
            elif 'FROM network_statistics ns' in query_2_section and 'FROM path_preview_cte' not in query_2_section:
                result['checks'].append({
                    'check': 'FROM clause uses path_preview_cte',
                    'status': 'FAIL',
                    'note': 'Still using network_statistics instead of path_preview_cte'
                })
                result['status'] = 'FAIL'
            else:
                result['checks'].append({'check': 'FROM clause uses path_preview_cte', 'status': 'PASS'})

        return result

    def verify_query_26_recursive_cte(self) -> Dict:
        """Verify Query 26 recursive CTE addition"""
        result = {
            'query_number': 26,
            'fix': 'Recursive CTE addition',
            'status': 'PASS',
            'checks': []
        }

        query_26_section = self._extract_query_section(26)
        if not query_26_section:
            result['status'] = 'FAIL'
            result['checks'].append({'check': 'Query 26 section found', 'status': 'FAIL'})
            return result

        # Check 1: WITH RECURSIVE at start (required for recursive CTE in multi-CTE query)
        if 'WITH RECURSIVE' in query_26_section and 'file_type_hierarchy AS (' in query_26_section:
            result['checks'].append({'check': 'WITH RECURSIVE present for recursive CTE', 'status': 'PASS'})
        else:
            result['checks'].append({'check': 'WITH RECURSIVE present for recursive CTE', 'status': 'FAIL'})
            result['status'] = 'FAIL'

        # Check 2: Anchor query selects from file_type_stats
        if 'FROM file_type_stats fts' in query_26_section:
            result['checks'].append({'check': 'Anchor query selects from file_type_stats', 'status': 'PASS'})
        else:
            result['checks'].append({'check': 'Anchor query selects from file_type_stats', 'status': 'FAIL'})
            result['status'] = 'FAIL'

        # Check 3: Recursive step with UNION ALL
        if 'UNION ALL' in query_26_section and 'FROM file_type_hierarchy fth' in query_26_section:
            result['checks'].append({'check': 'Recursive step with UNION ALL', 'status': 'PASS'})
        else:
            result['checks'].append({'check': 'Recursive step with UNION ALL', 'status': 'FAIL'})
            result['status'] = 'FAIL'

        # Check 4: Termination condition
        if 'hierarchy_level < 5' in query_26_section:
            result['checks'].append({'check': 'Termination condition (hierarchy_level < 5)', 'status': 'PASS'})
        else:
            result['checks'].append({'check': 'Termination condition (hierarchy_level < 5)', 'status': 'FAIL'})
            result['status'] = 'FAIL'

        return result

    def verify_query_title_uniqueness(self) -> Dict:
        """Verify queries 26-30 have unique titles"""
        result = {
            'fix': 'Query title uniqueness',
            'status': 'PASS',
            'checks': []
        }

        # Extract all query titles
        title_pattern = r'^## Query (\d+):\s*(.+)$'
        matches = re.findall(title_pattern, self.content, re.MULTILINE)

        titles = {int(num): title.strip() for num, title in matches}

        # Expected unique titles for queries 26-30
        expected_titles = {
            26: 'Production-Grade File Type Hierarchy Analysis',
            27: 'Production-Grade Cumulative File Size Analysis',
            28: 'Production-Grade Cross-Table File Relationship Analysis',
            29: 'Production-Grade Deeply Nested File Type Analysis',
            30: 'Production-Grade Advanced Window Function Aggregation Analysis'
        }

        # Check each expected title
        for query_num, expected_prefix in expected_titles.items():
            if query_num in titles:
                actual_title = titles[query_num]
                if expected_prefix in actual_title:
                    result['checks'].append({
                        'check': f'Query {query_num} has unique title',
                        'status': 'PASS',
                        'title': actual_title[:80]
                    })
                else:
                    result['checks'].append({
                        'check': f'Query {query_num} has unique title',
                        'status': 'FAIL',
                        'expected_prefix': expected_prefix,
                        'actual': actual_title[:80]
                    })
                    result['status'] = 'FAIL'
            else:
                result['checks'].append({
                    'check': f'Query {query_num} found',
                    'status': 'FAIL'
                })
                result['status'] = 'FAIL'

        # Check for duplicate titles across all queries
        title_to_queries = {}
        for query_num, title in titles.items():
            # Normalize title for comparison (first 50 chars)
            normalized = title[:50].lower()
            if normalized not in title_to_queries:
                title_to_queries[normalized] = []
            title_to_queries[normalized].append(query_num)

        duplicates = {k: v for k, v in title_to_queries.items() if len(v) > 1}
        if duplicates:
            result['checks'].append({
                'check': 'No duplicate titles',
                'status': 'FAIL',
                'duplicates': duplicates
            })
            result['status'] = 'FAIL'
        else:
            result['checks'].append({'check': 'No duplicate titles', 'status': 'PASS'})

        return result

    def verify_header_formatting(self) -> Dict:
        """Verify header formatting consistency"""
        result = {
            'fix': 'Header formatting consistency',
            'status': 'PASS',
            'checks': []
        }

        # Check for correct format
        correct_format = len(re.findall(r'^## Query \d+:', self.content, re.MULTILINE))

        # Check for incorrect format (with --- prefix)
        incorrect_format = len(re.findall(r'^---## Query \d+:', self.content, re.MULTILINE))

        if correct_format == 30:
            result['checks'].append({
                'check': 'All queries use ## Query N: format',
                'status': 'PASS',
                'count': correct_format
            })
        else:
            result['checks'].append({
                'check': 'All queries use ## Query N: format',
                'status': 'FAIL',
                'found': correct_format,
                'expected': 30
            })
            result['status'] = 'FAIL'

        if incorrect_format == 0:
            result['checks'].append({
                'check': 'No queries with --- prefix',
                'status': 'PASS'
            })
        else:
            result['checks'].append({
                'check': 'No queries with --- prefix',
                'status': 'FAIL',
                'found': incorrect_format
            })
            result['status'] = 'FAIL'

        return result

    def _extract_query_section(self, query_num: int) -> str:
        """Extract the section for a specific query including SQL code block"""
        # Find the query header
        header_pattern = rf'^## Query {query_num}:'
        header_match = re.search(header_pattern, self.content, re.MULTILINE)
        if not header_match:
            return ''

        start_pos = header_match.start()

        # Find the next query header or end of file
        next_header_pattern = rf'^## Query \d+:'
        next_matches = list(re.finditer(next_header_pattern, self.content, re.MULTILINE))

        # Find the next query after this one
        end_pos = len(self.content)
        for match in next_matches:
            if match.start() > start_pos:
                end_pos = match.start()
                break

        return self.content[start_pos:end_pos]

    def verify_all(self) -> Dict:
        """Run all verification checks"""
        self.results['fixes']['query_2_array_syntax'] = self.verify_query_2_array_syntax()
        self.results['fixes']['query_26_recursive_cte'] = self.verify_query_26_recursive_cte()
        self.results['fixes']['query_title_uniqueness'] = self.verify_query_title_uniqueness()
        self.results['fixes']['header_formatting'] = self.verify_header_formatting()

        # Overall status
        all_passed = all(
            fix['status'] == 'PASS'
            for fix in self.results['fixes'].values()
        )
        self.results['overall_status'] = 'PASS' if all_passed else 'FAIL'

        return self.results

def main():
    """Main verification function"""
    script_dir = Path(__file__).parent
    queries_file = script_dir.parent / 'queries' / 'queries.md'
    results_file = script_dir.parent / 'results' / 'fix_verification.json'

    if not queries_file.exists():
        print(f"Error: {queries_file} not found")
        return

    print("="*70)
    print("Fix Verification for db-1 queries.md")
    print("="*70)

    verifier = FixVerifier(queries_file)
    results = verifier.verify_all()

    # Print summary
    print("\nVerification Results:")
    print("-" * 70)
    for fix_name, fix_result in results['fixes'].items():
        status_icon = "✓" if fix_result['status'] == 'PASS' else "✗"
        print(f"{status_icon} {fix_name}: {fix_result['status']}")
        for check in fix_result.get('checks', []):
            check_icon = "  ✓" if check['status'] == 'PASS' else "  ✗"
            print(f"{check_icon} {check['check']}")

    print("\n" + "="*70)
    print(f"Overall Status: {results['overall_status']}")
    print("="*70)

    # Save results
    results_file.parent.mkdir(parents=True, exist_ok=True)
    results_file.write_text(json.dumps(results, indent=2))
    print(f"\nResults saved to: {results_file}")

if __name__ == '__main__':
    main()
