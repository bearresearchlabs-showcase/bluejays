#!/usr/bin/env python3
"""
Break up combined use cases into logical categories based on themes
"""
import re
import sys
from pathlib import Path
from collections import defaultdict

# Define categories based on query themes
DB16_CATEGORIES = {
    'Pre-Acquisition Assessment': {
        'queries': [1],
        'description': 'Individual property flood risk assessment for acquisition targets'
    },
    'Portfolio Risk Analysis': {
        'queries': [2, 16, 29],
        'description': 'Portfolio-level risk analysis and aggregation'
    },
    'Historical Flood Analysis': {
        'queries': [3, 14, 22],
        'description': 'Historical flood event analysis and pattern recognition'
    },
    'Sea Level Rise Analysis': {
        'queries': [4, 13],
        'description': 'Sea level rise projections and scenario comparison'
    },
    'Streamflow Analysis': {
        'queries': [5],
        'description': 'Streamflow flood frequency and gauge analysis'
    },
    'Model Performance': {
        'queries': [6, 15, 23],
        'description': 'Flood model performance evaluation and comparison'
    },
    'Spatial Analysis': {
        'queries': [7, 18],
        'description': 'Spatial joins and geographic risk analysis'
    },
    'Risk Trends & Projections': {
        'queries': [8, 20],
        'description': 'Temporal risk trend analysis and projections'
    },
    'Geographic Risk Analysis': {
        'queries': [9, 24],
        'description': 'Geographic clustering and distribution analysis'
    },
    'Vulnerability & Scoring': {
        'queries': [10, 21, 25],
        'description': 'Property vulnerability scoring and type analysis'
    },
    'Financial Impact': {
        'queries': [11, 28],
        'description': 'Financial impact modeling and cost-benefit analysis'
    },
    'FEMA Classification': {
        'queries': [12],
        'description': 'FEMA flood zone risk classification'
    },
    'Data Quality & Optimization': {
        'queries': [17],
        'description': 'Data quality metrics and spatial join optimization'
    },
    'Risk Score Fusion': {
        'queries': [19],
        'description': 'Multi-source risk score fusion'
    },
    'Advanced Risk Analysis': {
        'queries': [26, 27],
        'description': 'Recursive risk propagation and deal-breaker analysis'
    },
    'Comprehensive Reports': {
        'queries': [30],
        'description': 'Comprehensive M&A due diligence reports'
    }
}

def parse_combined_section(content):
    """Parse the combined use case section to extract nodes and connections"""
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
        return None, None, None, None
    
    # Extract nodes
    nodes = {}  # node_name -> full_line
    all_connections = []  # (from, to, label, use_case_num)
    
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
        
        # Connection - try to extract use case number from label
        conn_match = re.match(r'^"([^"]+)"\s*>\s*"([^"]+)"\s*:\s*"([^"]+)"', stripped)
        if conn_match:
            from_node = conn_match.group(1)
            to_node = conn_match.group(2)
            label = conn_match.group(3)
            
            # Try to determine use case from step number
            # Connections are numbered sequentially within each use case
            # We need to track which use case we're in based on connection patterns
            all_connections.append((from_node, to_node, label))
    
    return combined_start, combined_end, nodes, all_connections

def group_connections_by_category(connections, categories):
    """Group connections by category based on step numbering patterns"""
    # This is complex - connections restart numbering for each use case
    # We'll use a heuristic: look for connection patterns that suggest use case boundaries
    # For now, we'll distribute connections evenly or use a simpler approach
    
    connections_by_category = defaultdict(list)
    
    # Simple approach: distribute connections based on estimated counts per use case
    # Average ~15-20 connections per use case based on the file
    connections_per_uc = len(connections) // 30  # 30 use cases for db-16
    
    current_uc = 1
    uc_connections = []
    
    for i, (from_node, to_node, label) in enumerate(connections):
        uc_connections.append((from_node, to_node, label))
        
        # Check if we've reached the end of a use case
        # Look for patterns like "Returns JSON response" or "Displays" which often end use cases
        if 'Returns JSON response' in label or 'Displays' in label:
            # Find category for this use case
            for category, info in categories.items():
                if current_uc in info['queries']:
                    connections_by_category[category].extend(uc_connections)
                    break
            uc_connections = []
            current_uc += 1
        elif i > 0 and i % connections_per_uc == 0 and current_uc < 30:
            # Fallback: assign to category based on use case number
            for category, info in categories.items():
                if current_uc in info['queries']:
                    connections_by_category[category].extend(uc_connections)
                    break
            uc_connections = []
            current_uc += 1
    
    # Add remaining connections
    if uc_connections:
        for category, info in categories.items():
            if current_uc in info['queries']:
                connections_by_category[category].extend(uc_connections)
                break
    
    return connections_by_category

def create_category_diagrams(categories, nodes, connections_by_category):
    """Create separate diagram sections for each category"""
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
        diagram_lines.append(f"// {info['description']}")
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
        
        # Ensure all nodes are connected
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
        print("Usage: python categorize_by_themes.py <filepath>")
        sys.exit(1)
    
    filepath = Path(sys.argv[1])
    if not filepath.exists():
        print(f"Error: {filepath} not found")
        sys.exit(1)
    
    # Determine categories
    if 'db-16' in str(filepath):
        categories = DB16_CATEGORIES
    elif 'db-17' in str(filepath):
        # Will add db-17 categories later
        print("db-17 categories not yet implemented")
        sys.exit(1)
    else:
        print("Error: Cannot determine database")
        sys.exit(1)
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    combined_start, combined_end, nodes, all_connections = parse_combined_section(content)
    
    if combined_start is None:
        print("No combined section found")
        sys.exit(1)
    
    # Group connections by category
    connections_by_category = group_connections_by_category(all_connections, categories)
    
    # Create category diagrams
    category_diagrams = create_category_diagrams(categories, nodes, connections_by_category)
    
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
    
    print(f"Categorized use cases into {len(category_diagrams)} categories in {filepath}")

if __name__ == "__main__":
    main()
