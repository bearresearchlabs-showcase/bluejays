#!/usr/bin/env python3
"""
Import C4 model diagrams to Eraser.io workspace
Workspace: https://app.eraser.io/workspace/xs4eGrR8v2KRhJsJbm4X
API Token: 191Pty6OikJY1NQsy0NI
"""

import json
import requests
from pathlib import Path

ERASER_API_TOKEN = "191Pty6OikJY1NQsy0NI"
ERASER_WORKSPACE_ID = "xs4eGrR8v2KRhJsJbm4X"
ERASER_API_BASE = "https://app.eraser.io/api/v1"

def read_eraser_code_file(filepath):
    """Read Eraser.io code file"""
    with open(filepath, 'r') as f:
        return f.read()

def create_diagram_in_eraser(code_content, diagram_name):
    """Create diagram in Eraser.io workspace"""
    
    headers = {
        "Authorization": f"Bearer {ERASER_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Eraser.io diagram creation payload
    payload = {
        "workspace_id": ERASER_WORKSPACE_ID,
        "name": diagram_name,
        "content": code_content,
        "format": "eraser-code"
    }
    
    endpoints = [
        f"{ERASER_API_BASE}/workspaces/{ERASER_WORKSPACE_ID}/diagrams",
        f"{ERASER_API_BASE}/diagrams",
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.post(
                endpoint,
                headers=headers,
                json=payload,
                timeout=15
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                print(f"✓ Created diagram: {diagram_name}")
                print(f"  Diagram ID: {result.get('id', 'N/A')}")
                print(f"  URL: {result.get('url', result.get('web_url', 'N/A'))}")
                return result
            elif response.status_code == 401:
                print(f"⚠ Authentication failed for {endpoint}")
            elif response.status_code == 400:
                print(f"⚠ Bad Request: {response.text[:200]}")
        except Exception as e:
            print(f"⚠ Error with {endpoint}: {str(e)[:100]}")
            continue
    
    return None

def main():
    """Main function"""
    print("=" * 70)
    print("Importing C4 Model Diagrams to Eraser.io")
    print(f"Workspace: {ERASER_WORKSPACE_ID}")
    print("=" * 70)
    
    code_file = Path(__file__).parent / "C4_ERASER_IO.code"
    
    if not code_file.exists():
        print(f"✗ Code file not found: {code_file}")
        return
    
    code_content = read_eraser_code_file(code_file)
    
    # Split into individual diagrams (each diagram { } block)
    diagrams = []
    current_diagram = []
    in_diagram = False
    brace_count = 0
    
    for line in code_content.split('\n'):
        if line.strip().startswith('diagram {'):
            if current_diagram:
                diagrams.append('\n'.join(current_diagram))
            current_diagram = [line]
            in_diagram = True
            brace_count = line.count('{') - line.count('}')
        elif in_diagram:
            current_diagram.append(line)
            brace_count += line.count('{') - line.count('}')
            if brace_count == 0 and '}' in line:
                diagrams.append('\n'.join(current_diagram))
                current_diagram = []
                in_diagram = False
    
    if current_diagram:
        diagrams.append('\n'.join(current_diagram))
    
    print(f"\nFound {len(diagrams)} diagrams to import\n")
    
    for i, diagram_code in enumerate(diagrams, 1):
        # Extract diagram name from comments or use default
        diagram_name = f"db-16 C4 Model - Diagram {i}"
        
        # Try to extract name from comments
        for line in diagram_code.split('\n'):
            if '//' in line and ('Level' in line or 'Use Case' in line):
                diagram_name = line.split('//')[1].strip()
                break
        
        print(f"Importing: {diagram_name}")
        result = create_diagram_in_eraser(diagram_code, diagram_name)
        
        if result:
            print(f"  ✓ Success\n")
        else:
            print(f"  ⚠ Failed - try manual import\n")
    
    print("=" * 70)
    print("Import Complete!")
    print("\nIf API import failed, use manual import:")
    print("1. Open: https://app.eraser.io/workspace/xs4eGrR8v2KRhJsJbm4X")
    print("2. Create new diagram")
    print(f"3. Copy contents of: {code_file}")
    print("4. Paste into Eraser.io editor")
    print("=" * 70)

if __name__ == "__main__":
    main()
