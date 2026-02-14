#!/usr/bin/env python3
"""
Combine all use case diagrams into a single diagram
"""
import re
import sys
from pathlib import Path
from collections import OrderedDict

def find_use_case_sections(content):
    """Find all use case sections"""
    lines = content.split('\n')
    use_cases = []
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Look for use case title
        if line.startswith('// Use Case'):
            title = line[2:].strip()
            # Find direction statement
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            
            if j < len(lines) and lines[j].strip().startswith('direction'):
                # Found a use case section
                start_idx = i
                direction_line = j
                
                # Find end (next use case or next main section)
                end_idx = len(lines)
                for k in range(direction_line + 1, len(lines)):
                    next_line = lines[k].strip()
                    # Stop at next use case or next main section (not a use case)
                    if next_line.startswith('//'):
                        if not next_line.startswith('// Use Case'):
                            end_idx = k
                            break
                        elif k > direction_line + 5:  # Not the same use case
                            end_idx = k
                            break
                
                use_cases.append({
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
    
    return use_cases

def extract_nodes_and_connections(section_lines):
    """Extract all nodes and connections from a section"""
    nodes = OrderedDict()  # node_name -> full_line
    connections = []
    
    for line in section_lines:
        stripped = line.strip()
        
        # Skip comments and direction
        if stripped.startswith('//') or stripped.startswith('direction') or not stripped:
            continue
        
        # Extract node definitions (lines with [icon: but not connections)
        node_match = re.match(r'^"([^"]+)"\s*(\[icon:[^\]]+\])', stripped)
        if node_match and '>' not in stripped:
            node_name = node_match.group(1)
            icon_part = node_match.group(2)
            if node_name not in nodes:
                nodes[node_name] = f'"{node_name}" {icon_part}'
        
        # Extract connections
        conn_match = re.match(r'^"([^"]+)"\s*>\s*"([^"]+)"\s*:\s*"([^"]+)"', stripped)
        if conn_match:
            from_node = conn_match.group(1)
            to_node = conn_match.group(2)
            label = conn_match.group(3)
            connections.append((from_node, to_node, label))
    
    return nodes, connections

def combine_use_cases(content):
    """Combine all use case sections into one"""
    lines = content.split('\n')
    
    # Find all use case sections
    use_cases = find_use_case_sections(content)
    
    if not use_cases:
        print("No use case sections found")
        return content
    
    # Find where use cases start in the file
    first_use_case_start = use_cases[0]['start']
    last_use_case_end = use_cases[-1]['end']
    
    # Collect all nodes and connections from all use cases
    all_nodes = OrderedDict()
    all_connections = []
    use_case_titles = []
    
    for uc in use_cases:
        use_case_titles.append(uc['title'])
        nodes, connections = extract_nodes_and_connections(uc['lines'])
        all_nodes.update(nodes)
        all_connections.extend(connections)
    
    # Build the combined use case section
    combined_section = []
    combined_section.append("// All M&A Use Cases - Combined")
    combined_section.append("")
    combined_section.append("direction right")
    combined_section.append("")
    
    # Add all unique nodes
    for node_line in all_nodes.values():
        combined_section.append(node_line)
    
    combined_section.append("")
    
    # Add all connections
    for from_node, to_node, label in all_connections:
        combined_section.append(f'"{from_node}" > "{to_node}": "{label}"')
    
    # Ensure all nodes are connected (connect isolated nodes)
    connected_nodes = set()
    for from_node, to_node, _ in all_connections:
        connected_nodes.add(from_node)
        connected_nodes.add(to_node)
    
    isolated = set(all_nodes.keys()) - connected_nodes
    if isolated:
        # Connect isolated nodes to the main graph
        if connected_nodes:
            hub = list(connected_nodes)[0]
            for node in isolated:
                combined_section.append(f'"{node}" > "{hub}": "Related"')
        elif len(isolated) > 1:
            isolated_list = list(isolated)
            for i in range(len(isolated_list) - 1):
                combined_section.append(f'"{isolated_list[i]}" > "{isolated_list[i + 1]}": "Related"')
    
    combined_section.append("")
    combined_section.append("")
    
    # Rebuild the file: everything before use cases + combined use cases + everything after
    before_use_cases = '\n'.join(lines[:first_use_case_start])
    after_use_cases = '\n'.join(lines[last_use_case_end:])
    combined_use_cases = '\n'.join(combined_section)
    
    # Combine everything
    result = before_use_cases
    if result and not result.endswith('\n'):
        result += '\n'
    result += combined_use_cases
    if after_use_cases.strip():
        result += after_use_cases
    
    return result

def main():
    if len(sys.argv) < 2:
        print("Usage: python combine_use_cases.py <file1> [file2] ...")
        sys.exit(1)
    
    for filepath in sys.argv[1:]:
        filepath = Path(filepath)
        if not filepath.exists():
            print(f"Error: {filepath} not found")
            continue
        
        with open(filepath, 'r') as f:
            content = f.read()
        
        new_content = combine_use_cases(content)
        
        with open(filepath, 'w') as f:
            f.write(new_content)
        
        print(f"Combined use cases in {filepath}")

if __name__ == "__main__":
    main()
