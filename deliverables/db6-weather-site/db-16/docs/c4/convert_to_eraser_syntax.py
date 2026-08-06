#!/usr/bin/env python3
"""
Convert C4-style Eraser.io code to proper Eraser.io cloud architecture syntax
Based on: https://docs.eraser.io/docs/syntax
"""
import re
import sys
from pathlib import Path

def parse_diagram_block(content):
    """Parse a diagram block and extract elements and relationships"""
    elements = {}  # var_name -> {"type": type, "label": label, "props": props}
    relationships = []
    
    # Extract title
    title_match = re.search(r'title:\s*"([^"]+)"', content)
    title = title_match.group(1) if title_match else ""
    
    # Extract all element definitions
    # person VarName "Label" { ... }
    patterns = [
        (r'person\s+(\w+)\s+"([^"]+)"(?:\s*\{[^}]*\})?', 'person'),
        (r'system\s+(\w+)\s+"([^"]+)"(?:\s*\{[^}]*\})?', 'system'),
        (r'external\s+(\w+)\s+"([^"]+)"(?:\s*\{[^}]*\})?', 'external'),
        (r'container\s+(\w+)\s+"([^"]+)"(?:\s*\{[^}]*\})?', 'container'),
        (r'component\s+(\w+)\s+"([^"]+)"(?:\s*\{[^}]*\})?', 'component'),
        (r'database\s+(\w+)\s+"([^"]+)"(?:\s*\{[^}]*\})?', 'database'),
    ]
    
    for pattern, elem_type in patterns:
        matches = re.finditer(pattern, content)
        for match in matches:
            var_name = match.group(1)
            label = match.group(2)
            elements[var_name] = {
                "type": elem_type,
                "label": label,
                "var_name": var_name
            }
    
    # Extract relationships: VarName1 -> VarName2 "label"
    rel_pattern = r'(\w+)\s*->\s*(\w+)\s+"([^"]+)"'
    rel_matches = re.finditer(rel_pattern, content)
    for match in rel_matches:
        from_var = match.group(1)
        to_var = match.group(2)
        label = match.group(3)
        relationships.append({
            "from": from_var,
            "to": to_var,
            "label": label
        })
    
    return title, elements, relationships

def convert_to_eraser_syntax(content):
    """Convert C4-style syntax to Eraser.io cloud architecture syntax"""
    result = []
    
    # Split by diagram blocks
    diagram_blocks = re.split(r'diagram\s*\{', content)
    
    for block in diagram_blocks[1:]:  # Skip first part
        # Find matching closing brace
        brace_count = 0
        diagram_content = ""
        for i, char in enumerate(block):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == -1:
                    diagram_content = block[:i]
                    break
        
        if not diagram_content.strip():
            continue
        
        title, elements, relationships = parse_diagram_block(diagram_content)
        
        # Convert to Eraser.io syntax
        converted = []
        if title:
            converted.append(f"// {title}")
        converted.append("direction right")
        converted.append("")
        
        # Icon mapping
        icon_map = {
            'person': 'user',
            'system': 'server',
            'external': 'cloud',
            'container': 'server',
            'component': 'component',
            'database': 'database'
        }
        
        color_map = {
            'person': None,
            'system': 'blue',
            'external': 'gray',
            'container': None,
            'component': None,
            'database': None
        }
        
        # Output elements
        for var_name, elem_info in elements.items():
            label = elem_info['label']
            elem_type = elem_info['type']
            icon = icon_map.get(elem_type, 'component')
            color = color_map.get(elem_type)
            
            if color:
                converted.append(f'"{label}" [icon: {icon}, color: {color}]')
            else:
                converted.append(f'"{label}" [icon: {icon}]')
        
        converted.append("")
        
        # Output relationships
        for rel in relationships:
            from_var = rel['from']
            to_var = rel['to']
            label = rel['label']
            
            # Map variable names to labels
            from_label = elements.get(from_var, {}).get('label', from_var)
            to_label = elements.get(to_var, {}).get('label', to_var)
            
            converted.append(f'"{from_label}" > "{to_label}": "{label}"')
        
        result.append("\n".join(converted))
    
    return "\n\n".join(result)

def main():
    if len(sys.argv) < 2:
        print("Usage: python convert_to_eraser_syntax.py <input_file> [output_file]")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else input_file.parent / f"{input_file.stem}_ERASER.code"
    
    with open(input_file, 'r') as f:
        content = f.read()
    
    converted = convert_to_eraser_syntax(content)
    
    with open(output_file, 'w') as f:
        f.write(converted)
    
    print(f"Converted {input_file} -> {output_file}")
    print(f"Output length: {len(converted)} characters")

if __name__ == "__main__":
    main()
