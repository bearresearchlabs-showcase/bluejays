#!/usr/bin/env python3
"""
Ensure all nodes are connected and each diagram has a clear title
"""
import re
import sys
from pathlib import Path

def find_diagram_sections(content):
    """Find all diagram sections in the content"""
    sections = []
    lines = content.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Look for diagram start (comment followed by direction)
        if line.startswith('//'):
            title = line[2:].strip()
            # Look ahead for direction statement
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            
            if j < len(lines) and lines[j].strip().startswith('direction'):
                # Found a diagram section
                start_idx = i
                direction_line = j
                
                # Find end of this diagram (next diagram start or end of file)
                end_idx = len(lines)
                for k in range(direction_line + 1, len(lines)):
                    if lines[k].strip().startswith('//') and k > direction_line + 5:
                        # Check if next section has direction
                        for m in range(k + 1, min(k + 5, len(lines))):
                            if lines[m].strip().startswith('direction'):
                                end_idx = k
                                break
                        if end_idx < len(lines):
                            break
                
                sections.append({
                    'title': title,
                    'start': start_idx,
                    'direction_line': direction_line,
                    'end': end_idx,
                    'lines': lines[start_idx:end_idx]
                })
                i = end_idx
            else:
                i += 1
        else:
            i += 1
    
    return sections

def get_nodes_and_connections(section_lines):
    """Extract nodes and connections from a diagram section"""
    nodes = set()
    connections = []
    
    for line in section_lines:
        stripped = line.strip()
        
        # Extract node definitions
        node_match = re.search(r'"([^"]+)"\s*(?:\[icon:[^\]]+\])?', stripped)
        if node_match and '>' not in stripped:  # Not a connection line
            nodes.add(node_match.group(1))
        
        # Extract connections
        conn_match = re.match(r'^"([^"]+)"\s*>\s*"([^"]+)"\s*:\s*"([^"]+)"', stripped)
        if conn_match:
            from_node = conn_match.group(1)
            to_node = conn_match.group(2)
            label = conn_match.group(3)
            connections.append((from_node, to_node, label))
            nodes.add(from_node)
            nodes.add(to_node)
    
    return nodes, connections

def connect_isolated_nodes(nodes, connections):
    """Connect isolated nodes to the main graph"""
    connected_nodes = set()
    for from_node, to_node, _ in connections:
        connected_nodes.add(from_node)
        connected_nodes.add(to_node)
    
    isolated = nodes - connected_nodes
    new_connections = []
    
    if isolated:
        # If there are connected nodes, connect isolated ones to them
        if connected_nodes:
            hub = list(connected_nodes)[0]
            for node in isolated:
                new_connections.append((node, hub, "Related"))
        # If all nodes are isolated, create a chain
        elif len(isolated) > 1:
            isolated_list = list(isolated)
            for i in range(len(isolated_list) - 1):
                new_connections.append((isolated_list[i], isolated_list[i + 1], "Related"))
    
    return new_connections

def rebuild_section(section):
    """Rebuild a diagram section with connections and title"""
    lines = section['lines']
    
    # Extract nodes and connections
    nodes_set, connections = get_nodes_and_connections(lines)
    
    # Find isolated nodes and add connections
    new_connections = connect_isolated_nodes(nodes_set, connections)
    
    # Rebuild the section
    result = []
    
    # Title
    title = section['title']
    if not title or title.strip() == '':
        title = "Untitled Diagram"
    result.append(f"// {title}")
    result.append("")
    
    # Direction
    direction_found = False
    node_lines = []
    connection_lines = []
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('direction'):
            result.append(stripped)
            result.append("")
            direction_found = True
        elif stripped.startswith('//'):
            continue  # Skip other comments
        elif '>' in stripped and ':' in stripped:
            connection_lines.append(line.rstrip())
        elif re.match(r'^"[^"]+"', stripped):
            node_lines.append(line.rstrip())
    
    if not direction_found:
        result.append("direction right")
        result.append("")
    
    # Add nodes
    result.extend(node_lines)
    result.append("")
    
    # Add existing connections
    result.extend(connection_lines)
    
    # Add new connections for isolated nodes
    for from_node, to_node, label in new_connections:
        result.append(f'"{from_node}" > "{to_node}": "{label}"')
    
    return '\n'.join(result) + '\n\n'

def process_file(filepath):
    """Process file to ensure all nodes connected and titles present"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    sections = find_diagram_sections(content)
    
    if not sections:
        print(f"No diagram sections found in {filepath}")
        return content
    
    # Rebuild each section
    rebuilt_sections = []
    for section in sections:
        rebuilt = rebuild_section(section)
        rebuilt_sections.append(rebuilt)
    
    return '\n'.join(rebuilt_sections)

def main():
    if len(sys.argv) < 2:
        print("Usage: python ensure_connections_and_titles.py <file1> [file2] ...")
        sys.exit(1)
    
    for filepath in sys.argv[1:]:
        filepath = Path(filepath)
        if not filepath.exists():
            print(f"Error: {filepath} not found")
            continue
        
        new_content = process_file(filepath)
        
        with open(filepath, 'w') as f:
            f.write(new_content)
        
        print(f"Processed {filepath}: Connected all nodes and ensured titles")

if __name__ == "__main__":
    main()
