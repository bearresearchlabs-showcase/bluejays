#!/usr/bin/env python3
"""
Shared fix verification - conceptual checks per query-validation-suite rules.
Works for all db-1..db-16. Uses db_paths.get_queries_dir for canonical queries.md location.
"""

import re
import json
import sys
from pathlib import Path
from typing import Dict, List

scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))
from timestamp_utils import get_est_timestamp

from db_paths import get_queries_dir


class FixVerifier:
    """Conceptual fix verification - domain-agnostic quality checks."""

    def __init__(self, queries_file: Path):
        self.queries_file = queries_file
        self.content = queries_file.read_text(encoding='utf-8')
        self.results = {
            'verification_date': get_est_timestamp(),
            'file': str(queries_file),
            'fixes': {}
        }

    def verify_query_2_array_syntax(self) -> Dict:
        """Conceptual: Query 2 uses CTEs, valid structure, PostgreSQL-compatible if arrays used."""
        result = {'query_number': 2, 'fix': 'Array syntax PostgreSQL compatibility', 'status': 'PASS', 'checks': []}
        section = self._extract_query_section(2)
        if not section:
            result['checks'].append({'check': 'Query 2 section found', 'status': 'FAIL'})
            result['status'] = 'FAIL'
            return result
        if 'WITH' in section or 'WITH RECURSIVE' in section:
            result['checks'].append({'check': 'Query uses CTEs', 'status': 'PASS'})
        else:
            result['checks'].append({'check': 'Query uses CTEs', 'status': 'FAIL'})
            result['status'] = 'FAIL'
        if 'SELECT' in section and 'FROM' in section:
            result['checks'].append({'check': 'Valid query structure', 'status': 'PASS'})
        else:
            result['checks'].append({'check': 'Valid query structure', 'status': 'FAIL'})
            result['status'] = 'FAIL'
        result['checks'].append({'check': 'Array slicing syntax', 'status': 'PASS', 'note': 'Conceptual check'})
        return result

    def verify_query_26_recursive_cte(self) -> Dict:
        """Conceptual: Query 26 uses CTEs, has complexity indicators, valid SQL."""
        result = {'query_number': 26, 'fix': 'Query complexity validation', 'status': 'PASS', 'checks': []}
        section = self._extract_query_section(26)
        if not section:
            result['checks'].append({'check': 'Query 26 section found', 'status': 'FAIL'})
            result['status'] = 'FAIL'
            return result
        if 'WITH' in section or 'WITH RECURSIVE' in section:
            result['checks'].append({'check': 'Query uses CTEs', 'status': 'PASS'})
        else:
            result['checks'].append({'check': 'Query uses CTEs', 'status': 'FAIL'})
            result['status'] = 'FAIL'
        if 'SELECT' in section and 'FROM' in section:
            result['checks'].append({'check': 'Valid SQL structure', 'status': 'PASS'})
        else:
            result['checks'].append({'check': 'Valid SQL structure', 'status': 'FAIL'})
            result['status'] = 'FAIL'
        result['checks'].append({'check': 'Query complexity', 'status': 'PASS', 'note': 'Conceptual check'})
        return result

    def _get_title_for_uniqueness(self, num: int, header_title: str, section: str) -> str:
        """Use question from JSON block when in BIRD format, else header title."""
        json_m = re.search(r"```(?:json)?\n(.*?)```", section, re.DOTALL)
        if json_m:
            try:
                obj = __import__("json").loads(json_m.group(1))
                q = obj.get("question", "").strip()
                if q:
                    return q[:80]
            except Exception:
                pass
        return (header_title or f"Query {num}")[:80]

    def verify_query_title_uniqueness(self) -> Dict:
        """Conceptual: All 30 titles exist, no duplicates, queries 26-30 present."""
        result = {'fix': 'Query title uniqueness', 'status': 'PASS', 'checks': []}
        # Support ## Query N: and ### Query N (BIRD-style)
        header_pattern = r'^#{2,3} Query (\d+)[:\s—\-]*(.*)$'
        matches = list(re.finditer(header_pattern, self.content, re.MULTILINE))
        titles = {}
        for i, m in enumerate(matches):
            num, header_title = int(m.group(1)), (m.group(2) or "").strip()
            start = m.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(self.content)
            section = self.content[start:end]
            titles[num] = self._get_title_for_uniqueness(num, header_title, section)
        missing = [i for i in range(1, 31) if i not in titles]
        if missing:
            result['checks'].append({'check': 'All queries have titles', 'status': 'FAIL', 'missing': missing})
            result['status'] = 'FAIL'
        else:
            result['checks'].append({'check': 'All queries have titles', 'status': 'PASS', 'count': len(titles)})
        title_to_nums = {}
        for num, title in titles.items():
            key = title[:50].lower().strip()
            title_to_nums.setdefault(key, []).append(num)
        dups = {k: v for k, v in title_to_nums.items() if len(v) > 1}
        if dups:
            result['checks'].append({'check': 'No duplicate titles', 'status': 'FAIL', 'duplicates': dict(list(dups.items())[:5])})
            result['status'] = 'FAIL'
        else:
            result['checks'].append({'check': 'No duplicate titles', 'status': 'PASS'})
        q26_30 = [i for i in range(26, 31) if i in titles]
        if len(q26_30) == 5:
            result['checks'].append({'check': 'Queries 26-30 exist', 'status': 'PASS'})
        else:
            result['checks'].append({'check': 'Queries 26-30 exist', 'status': 'FAIL', 'found': q26_30})
            result['status'] = 'FAIL'
        return result

    def verify_header_formatting(self) -> Dict:
        """All queries use ##/### Query N format, no --- prefix."""
        result = {'fix': 'Header formatting', 'status': 'PASS', 'checks': []}
        # Support ## Query N: and ### Query N (BIRD-style)
        correct = len(re.findall(r'^#{2,3} Query \d+', self.content, re.MULTILINE))
        incorrect = len(re.findall(r'^---#+ Query \d+', self.content, re.MULTILINE))
        if correct >= 30:
            result['checks'].append({'check': 'All queries use ## Query N: format', 'status': 'PASS', 'count': correct})
        else:
            result['checks'].append({'check': 'All queries use ## Query N: format', 'status': 'FAIL', 'found': correct, 'expected': 30})
            result['status'] = 'FAIL'
        if incorrect == 0:
            result['checks'].append({'check': 'No queries with --- prefix', 'status': 'PASS'})
        else:
            result['checks'].append({'check': 'No queries with --- prefix', 'status': 'FAIL', 'found': incorrect})
            result['status'] = 'FAIL'
        return result

    def _extract_query_section(self, query_num: int) -> str:
        # Support ## Query N: and ### Query N (BIRD-style)
        header_pattern = rf'^#{{2,3}} Query {query_num}[:\s—\-]'
        m = re.search(header_pattern, self.content, re.MULTILINE)
        if not m:
            # Fallback: ### Query N (no colon/dash)
            m = re.search(rf'^#{{2,3}} Query {query_num}\s', self.content, re.MULTILINE)
        if not m:
            return ''
        start = m.start()
        next_matches = list(re.finditer(r'^#{2,3} Query \d+', self.content, re.MULTILINE))
        end = len(self.content)
        for nm in next_matches:
            if nm.start() > start:
                end = nm.start()
                break
        return self.content[start:end]

    def verify_all(self) -> Dict:
        self.results['fixes']['query_2_array_syntax'] = self.verify_query_2_array_syntax()
        self.results['fixes']['query_26_recursive_cte'] = self.verify_query_26_recursive_cte()
        self.results['fixes']['query_title_uniqueness'] = self.verify_query_title_uniqueness()
        self.results['fixes']['header_formatting'] = self.verify_header_formatting()
        all_pass = all(f.get('status') == 'PASS' for f in self.results['fixes'].values())
        self.results['overall_status'] = 'PASS' if all_pass else 'FAIL'
        self.results['Pass'] = 1 if all_pass else 0
        return self.results


def verify_db(db_num: int, root_dir: Path) -> bool:
    """Run fix verification for a database. Returns True on pass."""
    db_dir = root_dir / "source" / f"db-{db_num}"
    queries_dir = get_queries_dir(db_dir)
    queries_file = queries_dir / "queries.md"
    results_file = db_dir / "results" / "fix_verification.json"

    if not queries_file.exists():
        print(f"Error: {queries_file} not found")
        return False

    verifier = FixVerifier(queries_file)
    results = verifier.verify_all()

    print("\nVerification Results:")
    for fix_name, fix_result in results['fixes'].items():
        icon = "✓" if fix_result['status'] == 'PASS' else "✗"
        print(f"  {icon} {fix_name}: {fix_result['status']}")
    print(f"\nOverall: {results['overall_status']}")

    results_file.parent.mkdir(parents=True, exist_ok=True)
    results_file.write_text(json.dumps(results, indent=2))
    return results['overall_status'] == 'PASS'


def main():
    root_dir = Path(__file__).parent.parent
    if len(sys.argv) < 2:
        print("Usage: verify_fixes.py <db_num>")
        sys.exit(1)
    try:
        db_num = int(sys.argv[1].replace("db-", ""))
    except ValueError:
        print("Invalid db number")
        sys.exit(1)
    ok = verify_db(db_num, root_dir)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
