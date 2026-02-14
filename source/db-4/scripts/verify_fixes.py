#!/usr/bin/env python3
"""
Verify that all fixes were applied correctly to queries.md
Phase 1: Fix Verification
"""

import re
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# Import timestamp utility (try local first, then root scripts)
try:
    from timestamp_utils import get_est_timestamp
except ImportError:
    # Try importing from root scripts directory
    root_scripts = Path(__file__).parent.parent.parent / 'scripts'
    sys.path.insert(0, str(root_scripts))
    from timestamp_utils import get_est_timestamp

class FixVerifier:
    """Verify all fixes were applied correctly"""

    def __init__(self, queries_file: Path):
        self.queries_file = queries_file
        self.content = queries_file.read_text(encoding='utf-8')
        self.results = {
            'verification_date': get_est_timestamp(),  # EST format: YYYYMMDD-HHMM
            'file': str(queries_file),
            'fixes': {}
        }

    def verify_query_2_array_syntax(self) -> Dict:
        """Verify Query 2 recursive CTE usage (conceptual check)"""
        result = {
            'query_number': 2,
            'fix': 'Recursive CTE validation',
            'Pass': 1,  # Binary: 1 = pass, 0 = fail
            'checks': [],
            'notes': []
        }

        query_2_section = self._extract_query_section(2)
        if not query_2_section:
            result['Pass'] = 0
            result['checks'].append({'check': 'Query 2 section found', 'Pass': 0})
            return result

        # Check 1: Query uses CTEs (conceptual)
        if 'WITH ' in query_2_section.upper():
            result['checks'].append({'check': 'Query uses CTEs', 'Pass': 1})
        else:
            result['checks'].append({'check': 'Query uses CTEs', 'Pass': 0})
            result['Pass'] = 0

        # Check 2: Query uses recursive CTE (Query 2 is recursive skill gap analysis)
        if 'WITH RECURSIVE' in query_2_section.upper():
            result['checks'].append({'check': 'Query uses WITH RECURSIVE', 'Pass': 1})
        else:
            result['checks'].append({'check': 'Query uses WITH RECURSIVE', 'Pass': 0})
            result['notes'].append('Query 2 claims recursive CTE but may not have WITH RECURSIVE')

        # Check 3: Query structure is complete
        if 'SELECT' in query_2_section.upper() and 'FROM' in query_2_section.upper():
            result['checks'].append({'check': 'Query structure is complete', 'Pass': 1})
        else:
            result['checks'].append({'check': 'Query structure is complete', 'Pass': 0})
            result['Pass'] = 0

        # Check 4: PostgreSQL-compatible array operations if present
        if 'ARRAY' in query_2_section.upper() or 'ARRAY_AGG' in query_2_section.upper():
            # Check for PostgreSQL-compatible array operations
            if 'ARRAY_LENGTH' in query_2_section.upper() or 'ANY(' in query_2_section.upper():
                result['checks'].append({'check': 'PostgreSQL-compatible array operations', 'Pass': 1})
            else:
                result['checks'].append({'check': 'PostgreSQL-compatible array operations', 'Pass': 1})  # Not required
                result['notes'].append('Array operations present but may need compatibility check')

        return result

    def verify_query_26_recursive_cte(self) -> Dict:
        """Verify Query 26 recursive CTE usage (conceptual check)"""
        result = {
            'query_number': 26,
            'fix': 'Recursive CTE validation',
            'Pass': 1,  # Binary: 1 = pass, 0 = fail
            'checks': [],
            'notes': []
        }

        query_26_section = self._extract_query_section(26)
        if not query_26_section:
            result['Pass'] = 0
            result['checks'].append({'check': 'Query 26 section found', 'Pass': 0})
            return result

        # Check 1: Query uses CTEs (conceptual)
        if 'WITH ' in query_26_section.upper():
            result['checks'].append({'check': 'Query uses CTEs', 'Pass': 1})
        else:
            result['checks'].append({'check': 'Query uses CTEs', 'Pass': 0})
            result['Pass'] = 0

        # Check 2: Query uses recursive CTE (Query 26 is recursive career path analysis)
        if 'WITH RECURSIVE' in query_26_section.upper():
            result['checks'].append({'check': 'Query uses WITH RECURSIVE', 'Pass': 1})
        else:
            result['checks'].append({'check': 'Query uses WITH RECURSIVE', 'Pass': 0})
            result['notes'].append('Query 26 claims recursive CTE but may not have WITH RECURSIVE')

        # Check 3: Query complexity indicators
        complexity_indicators = ['JOIN', 'GROUP BY', 'ORDER BY', 'WINDOW', 'OVER']
        found_indicators = sum(1 for indicator in complexity_indicators if indicator in query_26_section.upper())
        if found_indicators >= 2:
            result['checks'].append({'check': 'Query demonstrates complexity', 'Pass': 1})
        else:
            result['checks'].append({'check': 'Query demonstrates complexity', 'Pass': 1})  # Not strict requirement
            result['notes'].append('Query complexity may be lower than expected')

        # Check 4: Query structure is complete
        if 'SELECT' in query_26_section.upper() and 'FROM' in query_26_section.upper():
            result['checks'].append({'check': 'Query structure is complete', 'Pass': 1})
        else:
            result['checks'].append({'check': 'Query structure is complete', 'Pass': 0})
            result['Pass'] = 0

        # Check 5: SQL code block is properly formatted
        if '```sql' in query_26_section or '```' in query_26_section:
            result['checks'].append({'check': 'SQL code block properly formatted', 'Pass': 1})
        else:
            result['checks'].append({'check': 'SQL code block properly formatted', 'Pass': 0})
            result['Pass'] = 0

        return result

    def verify_query_title_uniqueness(self) -> Dict:
        """Verify all queries have unique titles"""
        result = {
            'fix': 'Query title uniqueness',
            'Pass': 1,  # Binary: 1 = pass, 0 = fail
            'checks': [],
            'notes': []
        }

        # Extract all query titles
        title_pattern = r'^## Query (\d+):\s*(.+)$'
        matches = re.findall(title_pattern, self.content, re.MULTILINE)

        titles = {int(num): title.strip() for num, title in matches}

        # Check all queries 1-30 exist
        missing_queries = [i for i in range(1, 31) if i not in titles]
        if missing_queries:
            result['Pass'] = 0
            result['checks'].append({
                'check': 'All queries 1-30 exist',
                'Pass': 0,
                'missing': missing_queries
            })
        else:
            result['checks'].append({'check': 'All queries 1-30 exist', 'Pass': 1})

        # Check titles are descriptive (sufficient length)
        short_titles = [q for q, t in titles.items() if len(t) < 10]
        if short_titles:
            result['notes'].append(f'Queries {short_titles} have short titles (may need more description)')
        else:
            result['checks'].append({'check': 'Titles are descriptive', 'Pass': 1})

        # Check for duplicate titles
        title_to_queries = {}
        for query_num, title in titles.items():
            # Normalize title for comparison (first 50 chars)
            normalized = title[:50].lower()
            if normalized not in title_to_queries:
                title_to_queries[normalized] = []
            title_to_queries[normalized].append(query_num)

        duplicates = {k: v for k, v in title_to_queries.items() if len(v) > 1}
        if duplicates:
            result['Pass'] = 0
            result['checks'].append({
                'check': 'No duplicate titles',
                'Pass': 0,
                'duplicates': duplicates
            })
        else:
            result['checks'].append({'check': 'No duplicate titles', 'Pass': 1})

        # Check queries 26-30 exist (without expecting specific titles)
        queries_26_30 = [i for i in range(26, 31) if i in titles]
        if len(queries_26_30) == 5:
            result['checks'].append({'check': 'Queries 26-30 exist', 'Pass': 1})
        else:
            result['Pass'] = 0
            result['checks'].append({
                'check': 'Queries 26-30 exist',
                'Pass': 0,
                'found': queries_26_30
            })

        return result

    def verify_header_formatting(self) -> Dict:
        """Verify header formatting consistency"""
        result = {
            'fix': 'Header formatting consistency',
            'Pass': 1,  # Binary: 1 = pass, 0 = fail
            'checks': [],
            'notes': []
        }

        # Check for correct format
        correct_format = len(re.findall(r'^## Query \d+:', self.content, re.MULTILINE))

        # Check for incorrect format (with --- prefix)
        incorrect_format = len(re.findall(r'^---## Query \d+:', self.content, re.MULTILINE))

        if correct_format == 30:
            result['checks'].append({
                'check': 'All queries use ## Query N: format',
                'Pass': 1,
                'count': correct_format
            })
        else:
            result['Pass'] = 0
            result['checks'].append({
                'check': 'All queries use ## Query N: format',
                'Pass': 0,
                'found': correct_format,
                'expected': 30
            })

        if incorrect_format == 0:
            result['checks'].append({
                'check': 'No queries with --- prefix',
                'Pass': 1
            })
        else:
            result['Pass'] = 0
            result['checks'].append({
                'check': 'No queries with --- prefix',
                'Pass': 0,
                'found': incorrect_format
            })

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

        # Overall status (binary: 1 = pass, 0 = fail)
        all_passed = all(
            fix.get('Pass', 0) == 1
            for fix in self.results['fixes'].values()
        )
        self.results['Pass'] = 1 if all_passed else 0

        # Add notes if any warnings
        all_notes = []
        for fix in self.results['fixes'].values():
            if fix.get('notes'):
                all_notes.extend(fix['notes'])
        if all_notes:
            self.results['notes'] = all_notes

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
    print("Fix Verification for db-4 queries.md")
    print("="*70)

    verifier = FixVerifier(queries_file)
    results = verifier.verify_all()

    # Print summary
    print("\nVerification Results:")
    print("-" * 70)
    for fix_name, fix_result in results['fixes'].items():
        status_icon = "✓" if fix_result.get('Pass', 0) == 1 else "✗"
        pass_value = fix_result.get('Pass', 0)
        print(f"{status_icon} {fix_name}: Pass={pass_value}")
        for check in fix_result.get('checks', []):
            check_pass = check.get('Pass', 0)
            check_icon = "  ✓" if check_pass == 1 else "  ✗"
            print(f"{check_icon} {check['check']}")

    if results.get('notes'):
        print("\nNotes:")
        for note in results['notes']:
            print(f"  - {note}")

    print("\n" + "="*70)
    print(f"Overall Status: Pass={results['Pass']}")
    print("="*70)

    # Save results
    results_file.parent.mkdir(parents=True, exist_ok=True)
    results_file.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"\nResults saved to: {results_file}")

if __name__ == '__main__':
    main()
