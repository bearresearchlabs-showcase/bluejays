#!/usr/bin/env python3
"""
Extract queries from queries.md and create/update queries.json
Abstracts all query information into JSON format for programmatic access
Phase 0: Query Abstraction (REQUIRED)
"""

import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import sys

# Add root scripts directory to path for timestamp_utils
script_dir = Path(__file__).parent
root_dir = script_dir.parent.parent
root_scripts = root_dir / 'scripts'
sys.path.insert(0, str(root_scripts))

try:
    from timestamp_utils import get_est_timestamp
except ImportError:
    # Fallback if timestamp_utils not found
    def get_est_timestamp():
        return datetime.now().strftime('%Y%m%d-%H%M')

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

            # Extract SQL block
            sql_pattern = r'```(?:sql)?\n(.*?)```'
            sql_match = re.search(sql_pattern, query_section, re.DOTALL)

            if not sql_match:
                continue

            sql_start = sql_match.start()
            description_text = query_section[:sql_start]

            # Extract description (explains what the SQL does technically)
            description_match = re.search(r'\*\*Description:\*\*\s*(.+?)(?:\n\n|\*\*|$)', description_text, re.DOTALL | re.IGNORECASE)
            description = description_match.group(1).strip() if description_match else title

            # Extract use_case (was Business Use Case)
            use_case_match = re.search(r'\*\*Use Case:\*\*\s*(.+?)(?:\n\n|\*\*|$)', description_text, re.DOTALL | re.IGNORECASE)
            use_case = use_case_match.group(1).strip() if use_case_match else ""

            # Extract business_value (was Client Deliverable)
            business_value_match = re.search(r'\*\*Business Value:\*\*\s*(.+?)(?:\n\n|\*\*|$)', description_text, re.DOTALL | re.IGNORECASE)
            business_value = business_value_match.group(1).strip() if business_value_match else ""

            # Extract purpose (was Business Value)
            purpose_match = re.search(r'\*\*Purpose:\*\*\s*(.+?)(?:\n\n|\*\*|$)', description_text, re.DOTALL | re.IGNORECASE)
            purpose = purpose_match.group(1).strip() if purpose_match else ""

            # Extract complexity
            complexity_match = re.search(r'\*\*Complexity:\*\*\s*(.+?)(?:\n\n|\*\*|$)', description_text, re.DOTALL | re.IGNORECASE)
            complexity = complexity_match.group(1).strip() if complexity_match else ""

            # Extract expected output
            expected_output_match = re.search(r'\*\*Expected Output:\*\*\s*(.+?)(?:\n\n|\*\*|$)', description_text, re.DOTALL | re.IGNORECASE)
            expected_output = expected_output_match.group(1).strip() if expected_output_match else "Query results"

            # Extract SQL
            sql = sql_match.group(1).strip()

            # Clean up extracted text (remove markdown formatting)
            def clean_text(text):
                if not text:
                    return ""
                text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
                text = re.sub(r'`([^`]+)`', r'\1', text)
                text = re.sub(r'\n+', ' ', text)
                return text.strip()

            query_data = {
                'number': query_num,
                'title': title,
                'description': clean_text(description)[:1000] if description else title[:200],
                'use_case': clean_text(use_case)[:500] if use_case else "",
                'business_value': clean_text(business_value)[:500] if business_value else "",
                'purpose': clean_text(purpose)[:500] if purpose else "",
                'complexity': clean_text(complexity)[:500] if complexity else "",
                'expected_output': clean_text(expected_output)[:500] if expected_output else "Query results",
                'sql': sql,
                'line_number': line_number
            }

            self.queries.append(query_data)

        return sorted(self.queries, key=lambda x: x['number'])

    def generate_json(self) -> Dict:
        """Generate queries.json structure"""
        return {
            'source_file': str(self.queries_file.relative_to(self.queries_file.parent.parent)),
            'extraction_timestamp': get_est_timestamp(),  # EST format: YYYYMMDD-HHMM
            'total_queries': len(self.queries),
            'queries': self.queries
        }

    def save_json(self, output_file: Path):
        """Save queries.json to file"""
        json_data = self.generate_json()
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(json.dumps(json_data, indent=2, ensure_ascii=False), encoding='utf-8')
        return json_data

def main():
    """Main function"""
    script_dir = Path(__file__).parent
    db_dir = script_dir.parent
    queries_file = db_dir / 'queries' / 'queries.md'
    output_file = db_dir / 'queries' / 'queries.json'

    if not queries_file.exists():
        print(f"❌ ERROR: queries.md not found at {queries_file}")
        sys.exit(1)

    print("="*70)
    print("Phase 0: Query Abstraction - Extract queries.md to queries.json")
    print("="*70)
    print()

    extractor = QueryExtractor(queries_file)
    queries = extractor.extract_all_queries()

    if len(queries) == 0:
        print("❌ ERROR: No queries found in queries.md")
        sys.exit(1)

    if len(queries) != 30:
        print(f"⚠️  WARNING: Expected 30 queries, found {len(queries)}")

    json_data = extractor.save_json(output_file)

    print(f"✓ Extracted {len(queries)} queries")
    print(f"✓ Saved to {output_file}")
    print(f"✓ Extraction timestamp: {json_data['extraction_timestamp']}")
    print()
    print("="*70)
    print("Phase 0 Complete! queries.json is ready for validation.")
    print("="*70)

if __name__ == '__main__':
    main()
