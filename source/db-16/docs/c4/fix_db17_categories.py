#!/usr/bin/env python3
"""
Properly categorize db-17 use cases by analyzing connection patterns
"""
import re
import sys
from pathlib import Path
from collections import defaultdict

# db-17 categories based on use case patterns
DB17_CATEGORIES = {
    'Document Upload & Processing': {
        'keywords': ['Upload', 'Processing', 'Text Extractor', 'Metadata Extractor', 'Document Processor', 'Blob Storage'],
        'apis': ['Document API']
    },
    'Search & Discovery': {
        'keywords': ['Search', 'Semantic', 'Full-Text', 'Hybrid', 'Search API', 'Search Engine', 'Embedding'],
        'apis': ['Search API']
    },
    'Collection Management': {
        'keywords': ['Collection', 'Collection API', 'Deal', 'Relationship'],
        'apis': ['Collection API']
    },
    'Analytics & Monitoring': {
        'keywords': ['Analytics', 'Analytics API', 'Analytics Engine', 'Query Analytics', 'Usage Analytics', 'Monitoring'],
        'apis': ['Analytics API']
    },
    'Access Control': {
        'keywords': ['Access Control', 'Access Control API', 'Compliance', 'Compliance Officer'],
        'apis': ['Access Control API']
    },
    'Export & Reporting': {
        'keywords': ['Export', 'Reporting', 'Report'],
        'apis': []
    }
}

def parse_db17_section(content):
    """Parse db-17 use case section"""
    lines = content.split('\n')
    
    # Find use case section
    use_case_start = None
    use_case_end = None
    
    for i, line in enumerate(lines):
        if 'Use Cases - Document Upload' in line:
            use_case_start = i
        if use_case_start and line.strip().startswith('//') and 'Code Diagram' in line:
            use_case_end = i
            break
    
    if use_case_end is None:
        use_case_end = len(lines)
    
    if use_case_start is None:
        return None, None, {}, []
    
    # Extract nodes and connections
    nodes = {}
    connections = []
    
    for i in range(use_case_start, use_case_end):
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
    
    return use_case_start, use_case_end, nodes, connections

def categorize_connections(connections, nodes, categories):
    """Categorize connections based on node names and patterns"""
    connections_by_category = defaultdict(list)
    
    for from_node, to_node, label in connections:
        # Determine category based on node names
        category_found = None
        
        for category, info in categories.items():
            # Check if any node matches keywords
            matches_keyword = any(
                keyword.lower() in from_node.lower() or keyword.lower() in to_node.lower()
                for keyword in info['keywords']
            )
            matches_api = any(
                api.lower() in from_node.lower() or api.lower() in to_node.lower()
                for api in info['apis']
            )
            
            if matches_keyword or matches_api:
                category_found = category
                break
        
        # Default to first category if no match
        if category_found is None:
            category_found = list(categories.keys())[0]
        
        connections_by_category[category_found].append((from_node, to_node, label))
    
    return connections_by_category

def create_category_diagrams(categories, nodes, connections_by_category):
    """Create diagram sections for each category"""
    diagrams = []
    
    for category, info in categories.items():
        category_connections = connections_by_category.get(category, [])
        
        if not category_connections:
            continue
        
        # Get unique nodes for this category
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
    filepath = Path('db-17/docs/c4/C4_COMPLETE_ERASER_IO.code')
    
    if not filepath.exists():
        print(f"Error: {filepath} not found")
        sys.exit(1)
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    use_case_start, use_case_end, nodes, connections = parse_db17_section(content)
    
    if use_case_start is None:
        print("No use case section found")
        sys.exit(1)
    
    # Categorize connections
    connections_by_category = categorize_connections(connections, nodes, DB17_CATEGORIES)
    
    # Create category diagrams
    category_diagrams = create_category_diagrams(DB17_CATEGORIES, nodes, connections_by_category)
    
    # Rebuild file
    lines = content.split('\n')
    before_use_cases = '\n'.join(lines[:use_case_start])
    after_use_cases = '\n'.join(lines[use_case_end:])
    
    result = before_use_cases
    if result and not result.endswith('\n'):
        result += '\n'
    result += '\n'.join(category_diagrams)
    if after_use_cases.strip():
        result += after_use_cases
    
    with open(filepath, 'w') as f:
        f.write(result)
    
    print(f"Created {len(category_diagrams)} categories for db-17")

if __name__ == "__main__":
    main()
