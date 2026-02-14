#!/usr/bin/env python3
"""
Split Eraser.io code file into individual diagram files
Each diagram (separated by 'direction right') becomes its own file
"""
import re
import sys
from pathlib import Path

def split_diagrams(input_file, output_dir):
    """Split a single Eraser.io code file into individual diagram files"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(input_file, 'r') as f:
        content = f.read()
    
    # Split by 'direction right' (each diagram starts with this)
    diagrams = re.split(r'(?=^direction\s+(right|left|up|down))', content, flags=re.MULTILINE)
    
    diagram_files = []
    diagram_num = 0
    
    for i in range(0, len(diagrams), 2):
        if i + 1 < len(diagrams):
            direction = diagrams[i + 1] if diagrams[i + 1].strip() else 'direction right'
            diagram_content = diagrams[i].strip()
            
            if not diagram_content:
                continue
            
            # Extract title from comments
            title_match = re.search(r'//\s*(.+?)(?:\n|$)', diagram_content)
            if title_match:
                title = title_match.group(1).strip()
                # Clean up title for filename
                filename = re.sub(r'[^\w\s-]', '', title)
                filename = re.sub(r'\s+', '_', filename)
                filename = filename.lower()[:50]  # Limit length
            else:
                filename = f"diagram_{diagram_num:02d}"
            
            # Combine direction and content
            full_diagram = f"{direction}\n\n{diagram_content}"
            
            # Write to file
            output_file = output_dir / f"{filename}.code"
            with open(output_file, 'w') as f:
                f.write(full_diagram)
            
            diagram_files.append(output_file)
            diagram_num += 1
    
    return diagram_files

def main():
    if len(sys.argv) < 3:
        print("Usage: python split_diagrams.py <input_file> <output_directory>")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])
    
    diagram_files = split_diagrams(input_file, output_dir)
    
    print(f"Split {input_file} into {len(diagram_files)} diagram files:")
    for f in diagram_files[:10]:
        print(f"  - {f.name}")
    if len(diagram_files) > 10:
        print(f"  ... and {len(diagram_files) - 10} more")

if __name__ == "__main__":
    main()
