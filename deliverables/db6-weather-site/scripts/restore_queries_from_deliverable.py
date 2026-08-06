#!/usr/bin/env python3
"""
Restore queries from deliverable JSON to source queries/ directory.
Creates queries.md and queries.json from db-{N}_deliverable.json.
"""
import json
import sys
from pathlib import Path

scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))
try:
    from timestamp_utils import get_est_timestamp
except ImportError:
    def get_est_timestamp():
        from datetime import datetime
        import pytz
        est = pytz.timezone('US/Eastern')
        return datetime.now(est).strftime('%Y%m%d-%H%M')

def generate_queries_md(queries: list) -> str:
    """Generate queries.md content from JSON query list"""
    lines = ["# SQL Queries for Database\n"]
    for q in queries:
        num = q.get('number', 0)
        title = q.get('title', f'Query {num}')
        desc = q.get('description', '')
        use_case = q.get('use_case', '')
        biz_val = q.get('business_value', '')
        purpose = q.get('purpose', '')
        complexity = q.get('complexity', '')
        expected = q.get('expected_output', '')
        sql = q.get('sql', '')
        lines.append(f"## Query {num}: {title}\n")
        lines.append(f"**Description:** {desc}\n")
        lines.append(f"**Use Case:** {use_case}\n")
        lines.append(f"**Business Value:** {biz_val}\n")
        lines.append(f"**Purpose:** {purpose}\n")
        lines.append(f"**Complexity:** {complexity}\n")
        lines.append(f"**Expected Output:** {expected}\n\n")
        lines.append("```sql\n")
        lines.append(sql.strip())
        lines.append("\n```\n\n")
    return "".join(lines)

def restore_for_db(db_num: int) -> bool:
    """Restore queries for a single database from deliverable JSON"""
    root = Path(__file__).parent.parent
    db_dir = root / f'db-{db_num}'
    deliverable_dir = db_dir / 'deliverable'
    json_path = None
    # Find db-{N}_deliverable.json in deliverable subdirs
    for sub in deliverable_dir.iterdir() if deliverable_dir.exists() else []:
        if sub.is_dir():
            candidate = sub / f'db-{db_num}_deliverable.json'
            if candidate.exists():
                json_path = candidate
                break
    if not json_path or not json_path.exists():
        print(f"  Deliverable JSON not found for db-{db_num}")
        return False
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)
    queries = data.get('queries', [])
    if not queries:
        print(f"  No queries in deliverable JSON for db-{db_num}")
        return False
    queries_dir = db_dir / 'queries'
    queries_dir.mkdir(parents=True, exist_ok=True)
    # Write queries.md
    md_content = generate_queries_md(queries)
    md_path = queries_dir / 'queries.md'
    md_path.write_text(md_content, encoding='utf-8')
    # Write queries.json
    queries_json = []
    for i, q in enumerate(queries):
        start = md_content.find(f"## Query {q['number']}:")
        line_num = md_content[:start].count('\n') + 1 if start >= 0 else i * 50 + 1
        queries_json.append({
            'number': q['number'],
            'title': q['title'],
            'description': q.get('description', ''),
            'use_case': q.get('use_case', ''),
            'business_value': q.get('business_value', ''),
            'purpose': q.get('purpose', ''),
            'complexity': q.get('complexity', ''),
            'expected_output': q.get('expected_output', ''),
            'sql': q.get('sql', ''),
            'line_number': line_num
        })
    json_data = {
        'source_file': str(md_path.relative_to(root)),
        'extraction_timestamp': get_est_timestamp(),
        'total_queries': len(queries_json),
        'queries': queries_json
    }
    json_path_out = queries_dir / 'queries.json'
    json_path_out.write_text(json.dumps(json_data, indent=2), encoding='utf-8')
    print(f"  db-{db_num}: Restored {len(queries)} queries -> queries.md, queries.json")
    return True

if __name__ == '__main__':
    dbs = [4, 5] if len(sys.argv) <= 1 else [int(x.replace('db-','')) for x in sys.argv[1:]]
    for n in dbs:
        restore_for_db(n)
