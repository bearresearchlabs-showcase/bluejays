#!/usr/bin/env python3
"""
Ensure all nodes are connected and add titles to diagrams
"""
import re
import sys
from pathlib import Path

def parse_diagram_section(lines, start_idx):
    """Parse a diagram section starting at start_idx"""
    nodes = {}  # node_name -> line_number
    connections = []  # (from, to, label, line_number)
    title = None
    direction = None
    
    i = start_idx
    while i < len(lines):
        line = lines[i].strip()
        
        # Check for title comment
        if line.startswith('//') and not title:
            title = line[2:].strip()
        
        # Check for direction statement
        if line.startswith('direction'):
            direction = line
            i += 1
            continue
        
        # Check for node definition
        node_match = re.match(r'^"([^"]+)"\s*(?:\[icon:[^\]]+\])?', line)
        if node_match:
            node_name = node_match.group(1)
            if node_name not in nodes:
                nodes[node_name] = i
        
        # Check for connection
        conn_match = re.match(r'^"([^"]+)"\s*>\s*"([^"]+)"\s*:\s*"([^"]+)"', line)
        if conn_match:
            from_node = conn_match.group(1)
            to_node = conn_match.group(2)
            label = conn_match.group(3)
            connections.append((from_node, to_node, label, i))
        
        # End of diagram section (next diagram starts or end of file)
        if i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if next_line.startswith('//') and 'direction' in '\n'.join(lines[i+1:i+3]):
                break
        
        i += 1
    
    return {
        'title': title,
        'direction': direction,
        'nodes': nodes,
        'connections': connections,
        'end_idx': i
    }

def connect_isolated_nodes(diagram):
    """Add connections for isolated nodes"""
    nodes = set(diagram['nodes'].keys())
    connected_nodes = set()
    
    # Find all connected nodes
    for from_node, to_node, _, _ in diagram['connections']:
        connected_nodes.add(from_node)
        connected_nodes.add(to_node)
    
    # Find isolated nodes
    isolated = nodes - connected_nodes
    
    new_connections = []
    if isolated:
        # Connect isolated nodes to the main graph
        # Strategy: connect to the first connected node, or create a hub connection
        if connected_nodes:
            hub_node = list(connected_nodes)[0]
            for isolated_node in isolated:
                new_connections.append((isolated_node, hub_node, "Connected"))
        else:
            # All nodes are isolated - create a chain
            isolated_list = list(isolated)
            for i in range(len(isolated_list) - 1):
                new_connections.append((isolated_list[i], isolated_list[i + 1], "Related"))
    
    return new_connections

def ensure_title(diagram, default_title):
    """Ensure diagram has a title"""
    if not diagram['title'] or diagram['title'].strip() == '':
        return default_title
    return diagram['title']

def process_file(filepath):
    """Process file to connect all nodes and ensure titles"""
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    new_lines = []
    i = 0
    diagram_num = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Check if this is the start of a new diagram
        if line.startswith('//') or (line.startswith('direction') and i > 0):
            # Parse this diagram section
            diagram = parse_diagram_section(lines, i)
            
            # Ensure title
            if not diagram['title'] or diagram['title'].strip() == '':
                diagram['title'] = f"Diagram {diagram_num + 1}"
            
            # Add title comment
            new_lines.append(f"// {diagram['title']}\n")
            
            # Add direction
            if diagram['direction']:
                new_lines.append(f"{diagram['direction']}\n")
                new_lines.append("\n")
            
            # Add all nodes
            for node_name, line_idx in sorted(diagram['nodes'].items(), key=lambda x: x[1]):
                node_line = lines[line_idx].rstrip()
                new_lines.append(f"{node_line}\n")
            
            # Add existing connections
            for from_node, to_node, label, line_idx in diagram['connections']:
                conn_line = lines[line_idx].rstrip()
                new_lines.append(f"{conn_line}\n")
            
            # Add connections for isolated nodes
            new_connections = connect_isolated_nodes(diagram)
            for from_node, to_node, label in new_connections:
                new_lines.append(f'"{from_node}" > "{to_node}": "{label}"\n')
            
            new_lines.append("\n")
            
            i = diagram['end_idx']
            diagram_num += 1
        else:
            new_lines.append(lines[i])
            i += 1
    
    return ''.join(new_lines)

def main():
    if len(sys.argv) < 2:
        print("Usage: python connect_all_nodes.py <file1> [file2] ...")
        sys.exit(1)
    
    for filepath in sys.argv[1:]:
        filepath = Path(filepath)
        if not filepath.exists():
            print(f"Error: {filepath} not found")
            continue
        
        new_content = process_file(filepath)
        
        with open(filepath, 'w') as f:
            f.write(new_content)
        
        print(f"Processed {filepath}")

if __name__ == "__main__":
    main()
