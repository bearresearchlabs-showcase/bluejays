#!/usr/bin/env python3
"""
Add icons to all nodes that don't have icons
"""
import re
import sys
from pathlib import Path

# Icon mapping based on node name patterns
ICON_MAP = {
    # API/Service patterns
    'api': 'aws-api-gateway',
    'service': 'aws-lambda',
    'engine': 'aws-ec2',
    'processor': 'aws-lambda',
    'calculator': 'aws-lambda',
    'scorer': 'aws-lambda',
    'extractor': 'aws-lambda',
    'analyzer': 'aws-lambda',
    'manager': 'aws-lambda',
    'generator': 'aws-lambda',
    'executor': 'aws-lambda',
    'projector': 'aws-lambda',
    'aggregator': 'aws-lambda',
    
    # Database/Storage patterns
    'database': 'aws-rds',
    'db': 'aws-rds',
    'storage': 'aws-s3',
    'blob': 'aws-s3',
    'table': 'aws-dynamodb',
    'zones': 'aws-dynamodb',
    'properties': 'aws-dynamodb',
    'rise': 'aws-dynamodb',
    'gauges': 'aws-dynamodb',
    'observations': 'aws-dynamodb',
    'models': 'aws-dynamodb',
    'assessments': 'aws-dynamodb',
    'summaries': 'aws-dynamodb',
    'intersections': 'aws-dynamodb',
    'events': 'aws-dynamodb',
    'metrics': 'aws-dynamodb',
    'documents': 'aws-dynamodb',
    'metadata': 'aws-dynamodb',
    'index': 'aws-opensearch-service',
    'embeddings': 'aws-dynamodb',
    'relationships': 'aws-dynamodb',
    'collections': 'aws-dynamodb',
    'queries': 'aws-dynamodb',
    'log': 'aws-cloudwatch',
    
    # Search/Analytics patterns
    'search': 'aws-cloudsearch',
    'analytics': 'aws-quicksight',
    
    # Defaults
    'default': 'aws-ec2',
}

def get_icon_for_node(node_name):
    """Determine appropriate icon for a node name"""
    node_lower = node_name.lower()
    
    # Check for specific patterns
    for pattern, icon in ICON_MAP.items():
        if pattern in node_lower:
            return icon
    
    # Default icon
    return ICON_MAP['default']

def add_icons_to_file(filepath):
    """Add icons to all nodes missing icons"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Check if line is a node definition without icon
        # Pattern: "Node Name" (no [icon: ...] after it)
        match = re.match(r'^(\s*)"([^"]+)"(\s*)$', line)
        if match:
            indent = match.group(1)
            node_name = match.group(2)
            trailing = match.group(3)
            
            # Skip if it's a connection line (has >)
            if '>' in line:
                fixed_lines.append(line)
                continue
            
            # Get appropriate icon
            icon = get_icon_for_node(node_name)
            fixed_lines.append(f'{indent}"{node_name}" [icon: {icon}]{trailing}')
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def main():
    if len(sys.argv) < 2:
        print("Usage: python add_missing_icons.py <file1> [file2] ...")
        sys.exit(1)
    
    for filepath in sys.argv[1:]:
        filepath = Path(filepath)
        if not filepath.exists():
            print(f"Error: {filepath} not found")
            continue
        
        fixed_content = add_icons_to_file(filepath)
        
        with open(filepath, 'w') as f:
            f.write(fixed_content)
        
        print(f"Added icons to {filepath}")

if __name__ == "__main__":
    main()
