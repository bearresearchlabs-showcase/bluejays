#!/usr/bin/env python3
"""
Extract queries from queries.md and create/update queries.json
Abstracts all query information into JSON format for programmatic access
"""

import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import sys

# Add scripts directory to path for timestamp_utils
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))
from timestamp_utils import get_est_timestamp

class QueryExtractor:
    """Extract queries from queries.md and create queries.json"""

    def __init__(self, queries_file: Path):
        self.queries_file = queries_file
        self.content = queries_file.read_text(encoding='utf-8')
        self.queries = []

    def extract_all_queries(self) -> List[Dict]:
        """Extract all queries from queries.md"""
        # Pattern to find all query headers
        query_header_pattern = r'^## Query (\d+):\s*(.+)$'
        headers = list(re.finditer(query_header_pattern, self.content, re.MULTILINE))

        for i, header_match in enumerate(headers):
            query_num = int(header_match.group(1))
            title = header_match.group(2).strip()
            start_pos = header_match.start()
            line_number = self.content[:start_pos].count('\n') + 1

            # Find the end position (next query header or end of file)
            if i + 1 < len(headers):
                end_pos = headers[i + 1].start()
            else:
                end_pos = len(self.content)

            # Extract the section for this query
            query_section = self.content[start_pos:end_pos]

            # Extract description (between header and SQL block)
            sql_pattern = r'```(?:sql)?\n(.*?)```'
            sql_match = re.search(sql_pattern, query_section, re.DOTALL)

            if not sql_match:
                continue

            sql_start = sql_match.start()
            description_text = query_section[:sql_start]

            # Extract description
            description_lines = []
            for line in description_text.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    # Remove markdown formatting
                    line = re.sub(r'\*\*([^*]+)\*\*', r'\1', line)
                    line = re.sub(r'`([^`]+)`', r'\1', line)
                    if line:
                        description_lines.append(line)

            description = ' '.join(description_lines).strip()
            if not description:
                description = title

            # Extract complexity
            complexity_match = re.search(r'\*\*Complexity:\*\*\s*(.+?)(?:\n|$)', description_text, re.IGNORECASE)
            complexity = complexity_match.group(1).strip() if complexity_match else ""

            # Extract expected output
            expected_output_match = re.search(r'\*\*Expected Output:\*\*\s*(.+?)(?:\n|$)', description_text, re.IGNORECASE)
            expected_output = expected_output_match.group(1).strip() if expected_output_match else "Query results"

            # Extract SQL
            sql = sql_match.group(1).strip()

            query_data = {
                'number': query_num,
                'title': title,
                'description': description[:500] if description else title[:200],
                'complexity': complexity[:500] if complexity else "",
                'expected_output': expected_output[:200] if expected_output else "Query results",
                'sql': sql,
                'line_number': line_number
            }

            self.queries.append(query_data)

        return sorted(self.queries, key=lambda x: x['number'])

    def generate_json(self) -> Dict:
        """Generate queries.json structure"""
        return {
            'source_file': str(self.queries_file),
            'extraction_timestamp': get_est_timestamp(),  # EST format: YYYYMMDD-HHMM
            'total_queries': len(self.queries),
            'queries': self.queries
        }

    def save_json(self, output_file: Path):
        """Save queries.json to file"""
        json_data = self.generate_json()
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(json.dumps(json_data, indent=2, ensure_ascii=False))
        return json_data

def extract_queries_for_database(db_num: int, root_dir: Path) -> Optional[Dict]:
    """Extract queries for a specific database"""
    db_dir = root_dir / f'db-{db_num}'
    queries_file = db_dir / 'queries' / 'queries.md'
    output_file = db_dir / 'queries' / 'queries.json'

    if not queries_file.exists():
        print(f"⚠️  db-{db_num}: queries.md not found")
        return None

    print(f"Extracting queries from db-{db_num}...")

    extractor = QueryExtractor(queries_file)
    queries = extractor.extract_all_queries()

    if len(queries) == 0:
        print(f"  ⚠️  No queries found")
        return None

    json_data = extractor.save_json(output_file)

    print(f"  ✓ Extracted {len(queries)} queries")
    print(f"  ✓ Saved to {output_file}")

    return json_data

def main():
    """Main function"""
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent

    import sys

    if len(sys.argv) > 1:
        arg = sys.argv[1]
        # Handle db-N format
        if arg.startswith('db-'):
            db_nums = [int(arg.split('db-')[1])]
        # Handle plain number
        elif arg.isdigit():
            db_nums = [int(arg)]
        else:
            db_nums = [int(arg)]
    else:
        db_nums = list(range(1, 6))

    print("="*70)
    print("Extracting Queries to queries.json")
    print("="*70)
    print()

    all_results = {}

    for db_num in db_nums:
        result = extract_queries_for_database(db_num, root_dir)
        if result:
            all_results[f'db-{db_num}'] = {
                'total_queries': result['total_queries'],
                'extraction_timestamp': result['extraction_timestamp']
            }
        print()

    # Summary
    print("="*70)
    print("Extraction Summary")
    print("="*70)
    for db_name, result in all_results.items():
        print(f"{db_name}: {result['total_queries']} queries extracted")

    print()
    print("="*70)
    print("Extraction Complete!")
    print("="*70)

if __name__ == '__main__':
    main()
