#!/usr/bin/env python3
"""
Extract all SQL queries from queries.md files into structured JSON files
"""

import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List


class QueryExtractor:
    """Extract queries from queries.md files"""

    @staticmethod
    def extract_queries(markdown_file: Path) -> List[Dict[str, str]]:
        """Extract all SQL queries from a queries.md file"""
        with open(markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()

        queries = []

        # Find all SQL code blocks with their positions
        sql_pattern = r'```sql\s*(.*?)```'
        sql_blocks = list(re.finditer(sql_pattern, content, re.DOTALL | re.IGNORECASE))

        # Find all query headers: ## Query N: Description (or any line with Query N:)
        query_header_pattern = r'## Query (\d+):\s*(.+?)$'
        query_headers = []
        for line_num, line in enumerate(content.split('\n'), 1):
            match = re.search(query_header_pattern, line, re.IGNORECASE)
            if match:
                # Calculate position in content
                pos = content[:content.find(line)].rfind('\n') + 1 if line in content else 0
                query_headers.append({
                    'number': int(match.group(1)),
                    'description': match.group(2).strip(),
                    'line': line_num,
                    'position': content.find(line)
                })

        # Match query headers with SQL blocks
        for i, header in enumerate(query_headers):
            # Find the SQL block that comes after this header
            header_pos = header['position']
            matching_sql = None

            # Find the next SQL block after this header
            for sql_match in sql_blocks:
                if sql_match.start() > header_pos:
                    # Check if there's a closer header between this header and the SQL block
                    has_closer_header = False
                    for h in query_headers:
                        if h['position'] > header_pos and h['position'] < sql_match.start():
                            has_closer_header = True
                            break

                    if not has_closer_header:
                        matching_sql = sql_match.group(1).strip()
                        break

            # If no SQL found after header, try to find the next SQL block that hasn't been used
            if not matching_sql:
                # Find the first unused SQL block
                used_sql_positions = [q.get('sql_position', -1) for q in queries]
                for sql_match in sql_blocks:
                    if sql_match.start() not in used_sql_positions and sql_match.start() > header_pos:
                        matching_sql = sql_match.group(1).strip()
                        break

            if matching_sql:
                # Extract additional metadata from the query section
                query_section_start = header['position']
                # Find the end of this query section (next query header or end of file)
                next_header_pos = len(content)
                for h in query_headers:
                    if h['position'] > query_section_start:
                        next_header_pos = h['position']
                        break

                query_section = content[query_section_start:next_header_pos]

                # Extract complexity, expected output, etc.
                complexity_match = re.search(r'\*\*Complexity:\*\*\s*(.+?)(?:\n|$)', query_section, re.IGNORECASE)
                complexity = complexity_match.group(1).strip() if complexity_match else None

                expected_output_match = re.search(r'\*\*Expected Output:\*\*\s*(.+?)(?:\n|$)', query_section, re.IGNORECASE)
                expected_output = expected_output_match.group(1).strip() if expected_output_match else None

                queries.append({
                    'number': header['number'],
                    'description': header['description'],
                    'complexity': complexity,
                    'expected_output': expected_output,
                    'sql': matching_sql,
                    'line_number': header['line']
                })

        # If no headers found but SQL blocks exist, use SQL blocks directly
        if not queries and sql_blocks:
            for i, sql_match in enumerate(sql_blocks, 1):
                queries.append({
                    'number': i,
                    'description': f'Query {i}',
                    'complexity': None,
                    'expected_output': None,
                    'sql': sql_match.group(1).strip(),
                    'line_number': None
                })

        return sorted(queries, key=lambda x: x['number'])

    @staticmethod
    def extract_to_json(markdown_file: Path, output_file: Path):
        """Extract queries and save to JSON file"""
        queries = QueryExtractor.extract_queries(markdown_file)

        output_data = {
            'source_file': str(markdown_file),
            'extraction_timestamp': datetime.now().isoformat(),
            'total_queries': len(queries),
            'queries': queries
        }

        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        return output_data


def main():
    """Main execution"""
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent.parent

    print("=" * 70)
    print("EXTRACTING QUERIES TO JSON FILES")
    print("=" * 70)

    extractor = QueryExtractor()

    for db_num in range(1, 6):
        db_dir = root_dir / f'db-{db_num}'
        queries_file = db_dir / 'queries' / 'queries.md'

        if not queries_file.exists():
            print(f"\n⚠️  Skipping db-{db_num}: queries.md not found")
            continue

        print(f"\n📖 Extracting queries from db-{db_num}...")

        # Extract to JSON
        output_file = db_dir / 'queries' / 'queries.json'
        output_data = extractor.extract_to_json(queries_file, output_file)

        print(f"  ✅ Extracted {output_data['total_queries']} queries")
        print(f"  ✅ Saved to: {output_file}")

        # Show sample
        if output_data['queries']:
            sample = output_data['queries'][0]
            print(f"  Sample Query {sample['number']}: {sample['description'][:60]}...")

    print("\n" + "=" * 70)
    print("EXTRACTION COMPLETE")
    print("=" * 70)


if __name__ == '__main__':
    main()
