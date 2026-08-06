#!/usr/bin/env python3
"""
Split combined use cases into logical categories
"""
import re
import sys
from pathlib import Path
from collections import defaultdict

# Categories for db-16 based on query themes
DB16_CATEGORIES = {
    'Pre-Acquisition Assessment': [1],
    'Portfolio Risk Analysis': [2, 16, 29],
    'Historical Flood Analysis': [3, 14, 22],
    'Sea Level Rise Analysis': [4, 13],
    'Streamflow Analysis': [5],
    'Model Performance': [6, 15, 23],
    'Spatial Analysis': [7, 18],
    'Risk Trends & Projections': [8, 20],
    'Geographic Risk Analysis': [9, 24],
    'Vulnerability & Scoring': [10, 21, 25],
    'Financial Impact': [11, 28],
    'FEMA Classification': [12],
    'Data Quality & Optimization': [17],
    'Risk Score Fusion': [19],
    'Advanced Risk Analysis': [26, 27],
    'Comprehensive Reports': [30]
}

# Categories for db-17
DB17_CATEGORIES = {
    'Document Upload & Processing': [1, 12, 13, 15, 16],
    'Search & Discovery': [2, 3, 4, 8, 9, 17, 18],
    'Collection Management': [5, 6],
    'Analytics & Monitoring': [7, 10, 11, 19],
    'Access Control': [14],
    'Export & Reporting': [20]
}

def parse_combined_section(content):
    """Parse the combined use case section"""
    lines = content.split('\n')
    
    # Find combined section
    combined_start = None
    combined_end = None
    
    for i, line in enumerate(lines):
        if 'All M&A Use Cases - Combined' in line:
            combined_start = i
            for j in range(i + 1, len(lines)):
                if lines[j].strip().startswith('//') and j > i + 10:
                    combined_end = j
                    break
            if combined_end is None:
                combined_end = len(lines)
            break
    
    if combined_start is None:
        return None, None, {}, []
    
    # Extract nodes and connections
    nodes = {}
    connections = []
    
    for i in range(combined_start, combined_end):
        line = lines[i]
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
        
        # Connection
        conn_match = re.match(r'^"([^"]+)"\s*>\s*"([^"]+)"\s*:\s*"([^"]+)"', stripped)
        if conn_match:
            from_node = conn_match.group(1)
            to_node = conn_match.group(2)
            label = conn_match.group(3)
            connections.append((from_node, to_node, label))
    
    return combined_start, combined_end, nodes, connections

def group_connections_by_use_case(connections):
    """Group connections by use case number based on step numbering"""
    # Connections restart numbering for each use case
    # Pattern: connections end with "Displays" or "Returns JSON response"
    use_case_connections = defaultdict(list)
    current_uc = 1
    uc_buffer = []
    
    for from_node, to_node, label in connections:
        uc_buffer.append((from_node, to_node, label))
        
        # Check for use case boundary markers
        if 'Displays' in label or ('Returns JSON response' in label and len(uc_buffer) > 5):
            use_case_connections[current_uc] = uc_buffer.copy()
            uc_buffer = []
            current_uc += 1
    
    # Add remaining
    if uc_buffer:
        use_case_connections[current_uc] = uc_buffer
    
    return use_case_connections

def create_category_diagrams(categories, nodes, use_case_connections):
    """Create diagram sections for each category"""
    diagrams = []
    
    for category, uc_list in categories.items():
        # Collect all connections for use cases in this category
        category_connections = []
        for uc_num in uc_list:
            if uc_num in use_case_connections:
                category_connections.extend(use_case_connections[uc_num])
        
        if not category_connections:
            continue
        
        # Get unique nodes
        category_nodes = set()
        for from_node, to_node, _ in category_connections:
            category_nodes.add(from_node)
            category_nodes.add(to_node)
        
        # Build diagram
        diagram_lines = []
        diagram_lines.append(f"// Use Cases - {category}")
        diagram_lines.append("")
        diagram_lines.append("direction right")
        diagram_lines.append("")
        
        # Add nodes
        for node_name in sorted(category_nodes):
            if node_name in nodes:
                diagram_lines.append(nodes[node_name])
        
        diagram_lines.append("")
        
        # Add connections
        for from_node, to_node, label in category_connections:
            diagram_lines.append(f'"{from_node}" > "{to_node}": "{label}"')
        
        # Ensure all nodes connected
        connected_nodes = set()
        for from_node, to_node, _ in category_connections:
            connected_nodes.add(from_node)
            connected_nodes.add(to_node)
        
        isolated = category_nodes - connected_nodes
        if isolated and connected_nodes:
            hub = list(connected_nodes)[0]
            for node in isolated:
                diagram_lines.append(f'"{node}" > "{hub}": "Related"')
        
        diagram_lines.append("")
        diagram_lines.append("")
        
        diagrams.append('\n'.join(diagram_lines))
    
    return diagrams

def main():
    if len(sys.argv) < 2:
        print("Usage: python split_by_categories.py <filepath>")
        sys.exit(1)
    
    filepath = Path(sys.argv[1])
    if not filepath.exists():
        print(f"Error: {filepath} not found")
        sys.exit(1)
    
    # Determine categories
    if 'db-16' in str(filepath):
        categories = DB16_CATEGORIES
    elif 'db-17' in str(filepath):
        categories = DB17_CATEGORIES
    else:
        print("Error: Cannot determine database")
        sys.exit(1)
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    combined_start, combined_end, nodes, connections = parse_combined_section(content)
    
    if combined_start is None:
        print("No combined section found")
        sys.exit(1)
    
    # Group connections by use case
    use_case_connections = group_connections_by_use_case(connections)
    
    # Create category diagrams
    category_diagrams = create_category_diagrams(categories, nodes, use_case_connections)
    
    # Rebuild file
    lines = content.split('\n')
    before_combined = '\n'.join(lines[:combined_start])
    after_combined = '\n'.join(lines[combined_end:])
    
    result = before_combined
    if result and not result.endswith('\n'):
        result += '\n'
    result += '\n'.join(category_diagrams)
    if after_combined.strip():
        result += after_combined
    
    with open(filepath, 'w') as f:
        f.write(result)
    
    print(f"Split use cases into {len(category_diagrams)} categories in {filepath}")

if __name__ == "__main__":
    main()
