#!/usr/bin/env python3
"""
Append queries 10-30 to queries.md with full SQL implementations
"""

import json
from pathlib import Path

# Load templates
script_dir = Path(__file__).parent
generate_script = script_dir / "generate_queries_10_30.py"
exec(open(generate_script).read())

queries_md = script_dir.parent / "queries" / "queries.md"

# Read current content
with open(queries_md, 'r') as f:
    content = f.read()

# Find the note to replace
note_marker = "[Note: Queries 10-30 continue"
if note_marker in content:
    # Split at the note
    parts = content.split(note_marker)
    base_content = parts[0].rstrip()
    
    # Generate queries 10-30
    queries_text = "\n\n"
    for query_num in range(10, 31):
        template = QUERY_TEMPLATES[query_num]
        sql = generate_query_sql(query_num, template)
        
        queries_text += f"""## Query {query_num}: {template['title']}

**Description:** {template['description']}

**Use Case:** {template['use_case']}

**Business Value:** {template['business_value']}

**Purpose:** Enables data-driven decision making through advanced analytics and business intelligence.

**Complexity:** {template['complexity']}

**Expected Output:** Query results with analysis and recommendations.

```sql
{sql}
```

"""
    
    # Write updated content
    new_content = base_content + queries_text.rstrip() + "\n"
    
    with open(queries_md, 'w') as f:
        f.write(new_content)
    
    print(f"✓ Added queries 10-30 to {queries_md}")
    print(f"Total queries: 30")
else:
    print("Note marker not found. Appending to end of file.")
    queries_text = "\n\n"
    for query_num in range(10, 31):
        template = QUERY_TEMPLATES[query_num]
        sql = generate_query_sql(query_num, template)
        
        queries_text += f"""## Query {query_num}: {template['title']}

**Description:** {template['description']}

**Use Case:** {template['use_case']}

**Business Value:** {template['business_value']}

**Purpose:** Enables data-driven decision making through advanced analytics and business intelligence.

**Complexity:** {template['complexity']}

**Expected Output:** Query results with analysis and recommendations.

```sql
{sql}
```

"""
    
    with open(queries_md, 'a') as f:
        f.write(queries_text.rstrip() + "\n")
    
    print(f"✓ Appended queries 10-30 to {queries_md}")
