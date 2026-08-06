#!/usr/bin/env python3
"""
Analyze query diversity to ensure each query returns different business information.
"""

import re
from pathlib import Path
from collections import defaultdict

def extract_query_info(queries_file):
    """Extract query numbers, descriptions, and SELECT columns"""
    with open(queries_file, 'r', encoding='utf-8') as f:
        content = f.read()

    queries = []

    # Find all queries
    query_pattern = r'## Query (\d+):\s*(.+?)\n\n\*\*Description:\*\*\s*(.+?)\n\n'
    matches = re.finditer(query_pattern, content, re.DOTALL)

    for match in matches:
        query_num = int(match.group(1))
        title = match.group(2).strip()
        description = match.group(3).strip()

        # Find SELECT clause
        select_start = content.find(f'## Query {query_num}:', match.start())
        select_end = content.find('```', select_start + 100)
        if select_end == -1:
            select_end = len(content)

        query_sql = content[select_start:select_end]

        # Extract SELECT columns
        select_match = re.search(r'SELECT\s+(.+?)\s+FROM', query_sql, re.DOTALL | re.IGNORECASE)
        if select_match:
            select_clause = select_match.group(1)
            # Extract column names (simplified)
            columns = re.findall(r'(\w+(?:_\w+)*)\s*(?:AS\s+\w+)?,?', select_clause)
            columns = [c.strip() for c in columns if c.strip() and c.strip() not in ['SELECT', 'FROM']]
        else:
            columns = []

        queries.append({
            'number': query_num,
            'title': title,
            'description': description,
            'columns': columns[:20]  # First 20 columns
        })

    return queries

def analyze_diversity(queries):
    """Analyze query diversity"""
    print(f"\n{'='*80}")
    print(f"QUERY DIVERSITY ANALYSIS")
    print(f"{'='*80}\n")

    # Group by similar titles/descriptions
    title_groups = defaultdict(list)
    for q in queries:
        # Extract key words from title
        key_words = re.findall(r'\b(?:Analysis|Performance|Hierarchy|Chain|Status|Pattern|Rank|Total|Join|CTE)\b', q['title'], re.IGNORECASE)
        key = ' '.join(sorted(set(key_words)))
        title_groups[key].append(q)

    print("Query Groupings by Pattern:")
    print("-" * 80)
    for key, group in sorted(title_groups.items()):
        if len(group) > 1:
            print(f"\nPattern: {key}")
            for q in group:
                print(f"  Query {q['number']}: {q['title']}")

    # Check for unique business domains
    print(f"\n\n{'='*80}")
    print("BUSINESS DOMAIN ANALYSIS")
    print(f"{'='*80}\n")

    domains = {
        'Affiliate Performance': [],
        'Product Sales': [],
        'Category Analysis': [],
        'Commission Tracking': [],
        'Order Analysis': [],
        'Click Tracking': [],
        'Revenue Analysis': [],
        'Other': []
    }

    for q in queries:
        title_lower = q['title'].lower()
        desc_lower = q['description'].lower()

        if 'affiliate' in title_lower or 'marketer' in title_lower or 'referral' in title_lower:
            domains['Affiliate Performance'].append(q['number'])
        elif 'product' in title_lower and 'sales' in title_lower:
            domains['Product Sales'].append(q['number'])
        elif 'category' in title_lower or 'hierarchy' in title_lower:
            domains['Category Analysis'].append(q['number'])
        elif 'commission' in title_lower:
            domains['Commission Tracking'].append(q['number'])
        elif 'order' in title_lower:
            domains['Order Analysis'].append(q['number'])
        elif 'click' in title_lower or 'tracking' in title_lower:
            domains['Click Tracking'].append(q['number'])
        elif 'revenue' in title_lower:
            domains['Revenue Analysis'].append(q['number'])
        else:
            domains['Other'].append(q['number'])

    for domain, query_nums in domains.items():
        if query_nums:
            print(f"{domain}: Queries {', '.join(map(str, sorted(query_nums)))}")

    # Check column overlap
    print(f"\n\n{'='*80}")
    print("COLUMN OVERLAP ANALYSIS")
    print(f"{'='*80}\n")

    column_usage = defaultdict(list)
    for q in queries:
        for col in q['columns']:
            column_usage[col].append(q['number'])

    # Find columns used in multiple queries
    overlapping = {col: nums for col, nums in column_usage.items() if len(nums) > 5}
    if overlapping:
        print("Columns used in 6+ queries (potential overlap):")
        for col, nums in sorted(overlapping.items(), key=lambda x: len(x[1]), reverse=True)[:20]:
            print(f"  {col}: Used in queries {', '.join(map(str, sorted(nums)))}")

    return queries

def main():
    base_path = Path(__file__).parent.parent

    for db_num in [2, 3, 4, 5]:
        queries_file = base_path / f'db-{db_num}' / 'queries' / 'queries.md'
        if queries_file.exists():
            print(f"\n{'#'*80}")
            print(f"# DATABASE {db_num}")
            print(f"{'#'*80}")
            queries = extract_query_info(queries_file)
            analyze_diversity(queries)

if __name__ == '__main__':
    main()
