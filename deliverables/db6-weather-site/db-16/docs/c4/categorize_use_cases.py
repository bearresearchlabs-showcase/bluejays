#!/usr/bin/env python3
"""
Break up combined use cases into categories
"""
import re
import sys
from pathlib import Path
from collections import defaultdict

# Define categories for db-16
DB16_CATEGORIES = {
    'Pre-Acquisition Assessment': [1],
    'Portfolio Risk Analysis': [2, 16, 29],
    'Historical Flood Analysis': [3, 14, 22],
    'Sea Level Rise Analysis': [4, 13],
    'Streamflow Analysis': [5],
    'Model Performance Evaluation': [6, 15, 23],
    'Spatial Analysis': [7, 18],
    'Risk Trend Analysis': [8, 20],
    'Geographic Risk Analysis': [9, 24],
    'Vulnerability & Scoring': [10, 21, 25],
    'Financial Impact Analysis': [11, 28],
    'FEMA Classification': [12],
    'Data Quality & Optimization': [17],
    'Risk Score Fusion': [19],
    'Recursive Risk Analysis': [26],
    'Deal-Breaker Analysis': [27],
    'Comprehensive Reports': [30]
}

# Define categories for db-17
DB17_CATEGORIES = {
    'Document Upload & Processing': [1, 12, 13, 15, 16],
    'Search & Discovery': [2, 3, 4, 8, 9, 17, 18],
    'Collection Management': [5, 6],
    'Analytics & Monitoring': [7, 10, 11, 19],
    'Access Control': [14],
    'Export & Reporting': [20]
}

def find_use_case_sections(content):
    """Find all use case sections in the combined diagram"""
    lines = content.split('\n')
    use_cases = []
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Look for use case title
        if line.startswith('// Use Case'):
            # Extract use case number
            match = re.search(r'Use Case (\d+):', line)
            if match:
                uc_num = int(match.group(1))
                title = line[2:].strip()
                use_cases.append({
                    'number': uc_num,
                    'title': title,
                    'line': i
                })
        i += 1
    
    return use_cases

def extract_use_case_data(content, use_case_num):
    """Extract nodes and connections for a specific use case from the combined section"""
    # This is a simplified version - we'll need to parse the combined section
    # and extract data based on connection labels that reference the use case number
    pass

def categorize_use_cases(filepath, categories):
    """Categorize use cases and create separate diagrams"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # Find the combined use case section
    combined_start = None
    combined_end = None
    
    for i, line in enumerate(lines):
        if 'All M&A Use Cases - Combined' in line:
            combined_start = i
            # Find the end
            for j in range(i + 1, len(lines)):
                if lines[j].strip().startswith('//') and j > i + 10:
                    combined_end = j
                    break
            if combined_end is None:
                combined_end = len(lines)
            break
    
    if combined_start is None:
        print(f"No combined use case section found in {filepath}")
        return content
    
    # Extract the combined section
    combined_section = lines[combined_start:combined_end]
    
    # Parse nodes and connections
    nodes = {}  # node_name -> full_line
    connections_by_category = defaultdict(list)  # category -> [(from, to, label)]
    
    in_nodes = True
    for line in combined_section:
        stripped = line.strip()
        
        if stripped.startswith('//') or stripped.startswith('direction') or not stripped:
            continue
        
        # Node definition
        node_match = re.match(r'^"([^"]+)"\s*(\[icon:[^\]]+\])', stripped)
        if node_match and '>' not in stripped:
            node_name = node_match.group(1)
            icon_part = node_match.group(2)
            if node_name not in nodes:
                nodes[node_name] = f'"{node_name}" {icon_part}'
            in_nodes = False
        
        # Connection
        conn_match = re.match(r'^"([^"]+)"\s*>\s*"([^"]+)"\s*:\s*"([^"]+)"', stripped)
        if conn_match:
            from_node = conn_match.group(1)
            to_node = conn_match.group(2)
            label = conn_match.group(3)
            
            # Try to determine which category this connection belongs to
            # by checking the label for use case numbers
            uc_match = re.search(r'(\d+)\.', label)
            if uc_match:
                uc_num = int(uc_match.group(1))
                # Find category for this use case
                for category, uc_list in categories.items():
                    if uc_num in uc_list:
                        connections_by_category[category].append((from_node, to_node, label))
                        break
            else:
                # Generic connection - add to all categories or a default
                for category in categories.keys():
                    connections_by_category[category].append((from_node, to_node, label))
    
    # Build categorized sections
    categorized_sections = []
    
    for category, uc_list in categories.items():
        category_connections = connections_by_category.get(category, [])
        
        if not category_connections:
            continue
        
        # Get unique nodes for this category
        category_nodes = set()
        for from_node, to_node, _ in category_connections:
            category_nodes.add(from_node)
            category_nodes.add(to_node)
        
        # Build section
        section = []
        section.append(f"// Use Cases - {category}")
        section.append("")
        section.append("direction right")
        section.append("")
        
        # Add nodes
        for node_name in sorted(category_nodes):
            if node_name in nodes:
                section.append(nodes[node_name])
        
        section.append("")
        
        # Add connections
        for from_node, to_node, label in category_connections:
            section.append(f'"{from_node}" > "{to_node}": "{label}"')
        
        # Ensure all nodes are connected
        connected_nodes = set()
        for from_node, to_node, _ in category_connections:
            connected_nodes.add(from_node)
            connected_nodes.add(to_node)
        
        isolated = category_nodes - connected_nodes
        if isolated and connected_nodes:
            hub = list(connected_nodes)[0]
            for node in isolated:
                section.append(f'"{node}" > "{hub}": "Related"')
        
        section.append("")
        section.append("")
        
        categorized_sections.append('\n'.join(section))
    
    # Rebuild file
    before_combined = '\n'.join(lines[:combined_start])
    after_combined = '\n'.join(lines[combined_end:])
    
    result = before_combined
    if result and not result.endswith('\n'):
        result += '\n'
    result += '\n'.join(categorized_sections)
    if after_combined.strip():
        result += after_combined
    
    return result

def main():
    if len(sys.argv) < 2:
        print("Usage: python categorize_use_cases.py <db-16-file|db-17-file>")
        sys.exit(1)
    
    filepath = Path(sys.argv[1])
    if not filepath.exists():
        print(f"Error: {filepath} not found")
        sys.exit(1)
    
    # Determine which database
    if 'db-16' in str(filepath):
        categories = DB16_CATEGORIES
    elif 'db-17' in str(filepath):
        categories = DB17_CATEGORIES
    else:
        print("Error: Cannot determine database from filepath")
        sys.exit(1)
    
    new_content = categorize_use_cases(filepath, categories)
    
    with open(filepath, 'w') as f:
        f.write(new_content)
    
    print(f"Categorized use cases in {filepath}")

if __name__ == "__main__":
    main()
