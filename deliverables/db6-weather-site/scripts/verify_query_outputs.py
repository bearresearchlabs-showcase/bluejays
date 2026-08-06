#!/usr/bin/env python3
"""
Verify that each query returns distinct information consistent with business logic.
"""

import re
from pathlib import Path
from collections import defaultdict

def extract_select_columns(queries_file, query_num):
    """Extract SELECT columns for a specific query"""
    with open(queries_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the query
    query_start = content.find(f'## Query {query_num}:') or content.find(f'---## Query {query_num}:')
    if query_start == -1:
        return []

    # Find the SELECT clause
    select_match = re.search(r'SELECT\s+(.+?)\s+FROM\s+\w+', content[query_start:query_start+5000], re.DOTALL | re.IGNORECASE)
    if not select_match:
        return []

    select_clause = select_match.group(1)

    # Extract column names (handle aliases)
    columns = []
    # Match: column_name AS alias or just column_name
    col_pattern = r'(\w+(?:\.\w+)?(?:_\w+)*)\s*(?:AS\s+(\w+))?'
    matches = re.finditer(col_pattern, select_clause)

    for match in matches:
        col = match.group(1)
        alias = match.group(2)
        if col and col not in ['SELECT', 'FROM', 'WHERE', 'GROUP', 'ORDER', 'HAVING']:
            columns.append(alias if alias else col.split('.')[-1])

    return columns[:30]  # First 30 columns

def analyze_query_outputs(db_num):
    """Analyze what each query returns"""
    base_path = Path(__file__).parent.parent
    queries_file = base_path / f'db-{db_num}' / 'queries' / 'queries.md'

    if not queries_file.exists():
        return

    print(f"\n{'='*80}")
    print(f"DATABASE {db_num} - QUERY OUTPUT ANALYSIS")
    print(f"{'='*80}\n")

    # Extract columns for each query
    query_outputs = {}
    for q_num in range(1, 31):
        columns = extract_select_columns(queries_file, q_num)
        query_outputs[q_num] = columns

    # Find queries with similar outputs
    column_sets = {}
    for q_num, cols in query_outputs.items():
        col_set = frozenset(cols[:10])  # First 10 columns as signature
        if col_set not in column_sets:
            column_sets[col_set] = []
        column_sets[col_set].append(q_num)

    # Report similar outputs
    similar = {cols: nums for cols, nums in column_sets.items() if len(nums) > 1}
    if similar:
        print("⚠️  Queries with similar output columns (first 10):")
        for cols, nums in sorted(similar.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
            print(f"\n  Queries {', '.join(map(str, nums))}:")
            print(f"    Columns: {', '.join(list(cols)[:10])}")

    # Report unique outputs
    unique = {cols: nums for cols, nums in column_sets.items() if len(nums) == 1}
    print(f"\n✅ {len(unique)} queries have unique output signatures")

    # Show sample outputs
    print(f"\n{'='*80}")
    print("SAMPLE QUERY OUTPUTS (first 10 columns):")
    print(f"{'='*80}\n")
    for q_num in [1, 2, 3, 11, 12, 20]:
        cols = query_outputs.get(q_num, [])
        print(f"Query {q_num:2d}: {', '.join(cols[:10])}")

def main():
    for db_num in [2, 3, 4, 5]:
        analyze_query_outputs(db_num)

if __name__ == '__main__':
    main()
