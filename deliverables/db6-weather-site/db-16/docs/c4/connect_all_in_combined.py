#!/usr/bin/env python3
"""
Ensure all nodes in the combined use case diagram are connected
"""
import re
import sys
from pathlib import Path

def process_file(filepath):
    """Process file to connect all nodes in combined use case section"""
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    # Find the combined use case section
    combined_start = None
    combined_end = None
    
    for i, line in enumerate(lines):
        if 'All M&A Use Cases' in line:
            combined_start = i
            # Find the end (next section or end of file)
            for j in range(i + 1, len(lines)):
                if lines[j].strip().startswith('//') and j > i + 10:
                    combined_end = j
                    break
            if combined_end is None:
                combined_end = len(lines)
            break
    
    if combined_start is None:
        print(f"No combined use case section found in {filepath}")
        return
    
    # Extract nodes and connections from combined section
    section_lines = lines[combined_start:combined_end]
    nodes = set()
    connections = []
    
    for line in section_lines:
        stripped = line.strip()
        
        # Extract node definitions
        node_match = re.search(r'"([^"]+)"\s*(?:\[icon:[^\]]+\])?', stripped)
        if node_match and '>' not in stripped and not stripped.startswith('//') and not stripped.startswith('direction'):
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
    
    # Find isolated nodes
    connected_nodes = set()
    for from_node, to_node, _ in connections:
        connected_nodes.add(from_node)
        connected_nodes.add(to_node)
    
    isolated = nodes - connected_nodes
    
    if not isolated:
        print(f"All nodes already connected in {filepath}")
        return
    
    # Connect isolated nodes
    new_connections = []
    if connected_nodes:
        # Connect isolated nodes to the first connected node (hub)
        hub = list(connected_nodes)[0]
        for node in isolated:
            new_connections.append((node, hub, "Related"))
    elif len(isolated) > 1:
        # All nodes are isolated - create a chain
        isolated_list = list(isolated)
        for i in range(len(isolated_list) - 1):
            new_connections.append((isolated_list[i], isolated_list[i + 1], "Related"))
    
    # Insert new connections before the end of the section
    insert_pos = combined_end - 1
    while insert_pos > combined_start and not lines[insert_pos].strip():
        insert_pos -= 1
    
    # Add new connections
    for from_node, to_node, label in new_connections:
        lines.insert(insert_pos + 1, f'"{from_node}" > "{to_node}": "{label}"\n')
    
    # Write back
    with open(filepath, 'w') as f:
        f.writelines(lines)
    
    print(f"Connected {len(isolated)} isolated nodes in {filepath}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python connect_all_in_combined.py <file1> [file2] ...")
        sys.exit(1)
    
    for filepath in sys.argv[1:]:
        filepath = Path(filepath)
        if not filepath.exists():
            print(f"Error: {filepath} not found")
            continue
        process_file(filepath)

if __name__ == "__main__":
    main()
