#!/usr/bin/env python3
"""
Import Complete C4 Model Diagrams to Eraser.io
db-16 - All 30 Use Cases and Interactions

This script attempts to import all C4 diagrams from C4_COMPLETE_ERASER_IO.code
into the Eraser.io workspace via API.
"""

import requests
import json
import re
import sys
from pathlib import Path

# Eraser.io API Configuration
ERASER_API_TOKEN = "191Pty6OikJY1NQsy0NI"
ERASER_WORKSPACE_ID = "xs4eGrR8v2KRhJsJbm4X"
ERASER_API_BASE = "https://app.eraser.io/api/v1"

# Headers variants to try
HEADERS_VARIANTS = [
    {"Authorization": f"Bearer {ERASER_API_TOKEN}"},
    {"X-API-Token": ERASER_API_TOKEN},
    {"X-Eraser-Token": ERASER_API_TOKEN},
    {"Token": ERASER_API_TOKEN},
    {"API-Key": ERASER_API_TOKEN},
]

def read_eraser_code_file(filepath):
    """Read and parse Eraser.io code file into individual diagram blocks."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Split by diagram blocks
    diagrams = []
    pattern = r'diagram\s*\{[^}]*title:\s*"([^"]+)"[^}]*\n(.*?)\n\}'
    
    matches = re.finditer(pattern, content, re.DOTALL)
    for match in matches:
        title = match.group(1)
        diagram_code = match.group(0)
        diagrams.append({
            'title': title,
            'code': diagram_code
        })
    
    return diagrams

def create_diagram_in_eraser(code_content, diagram_name):
    """Attempt to create a diagram in Eraser.io via API."""
    endpoints = [
        f"/workspaces/{ERASER_WORKSPACE_ID}/diagrams",
        f"/diagrams",
        f"/workspaces/{ERASER_WORKSPACE_ID}/create-diagram",
        f"/create-diagram",
    ]
    
    payload_variants = [
        {"code": code_content, "title": diagram_name},
        {"content": code_content, "name": diagram_name},
        {"diagram": code_content, "title": diagram_name},
        {"data": {"code": code_content, "title": diagram_name}},
    ]
    
    for endpoint in endpoints:
        for headers in HEADERS_VARIANTS:
            for payload in payload_variants:
                try:
                    url = f"{ERASER_API_BASE}{endpoint}"
                    response = requests.post(
                        url,
                        headers=headers,
                        json=payload,
                        timeout=10
                    )
                    
                    if response.status_code == 200 or response.status_code == 201:
                        print(f"✓ Successfully created: {diagram_name}")
                        return True
                    elif response.status_code == 404:
                        continue  # Try next endpoint
                    elif response.status_code == 405:
                        continue  # Try next method
                    else:
                        print(f"  Status {response.status_code} for {diagram_name}")
                except Exception as e:
                    continue
    
    return False

def main():
    script_dir = Path(__file__).parent
    code_file = script_dir / "C4_COMPLETE_ERASER_IO.code"
    
    if not code_file.exists():
        print(f"Error: {code_file} not found")
        sys.exit(1)
    
    print(f"Reading diagrams from {code_file}...")
    diagrams = read_eraser_code_file(code_file)
    
    print(f"Found {len(diagrams)} diagrams to import")
    print(f"Workspace: {ERASER_WORKSPACE_ID}")
    print(f"API Base: {ERASER_API_BASE}\n")
    
    success_count = 0
    failed_count = 0
    
    for i, diagram in enumerate(diagrams, 1):
        title = diagram['title']
        code = diagram['code']
        
        print(f"[{i}/{len(diagrams)}] Attempting to create: {title}")
        
        if create_diagram_in_eraser(code, title):
            success_count += 1
        else:
            failed_count += 1
            print(f"  ✗ Failed to create via API: {title}")
            print(f"  → Manual import recommended (see ERASER_IO_IMPORT.md)")
    
    print(f"\n{'='*60}")
    print(f"Import Summary:")
    print(f"  Total diagrams: {len(diagrams)}")
    print(f"  Successfully created: {success_count}")
    print(f"  Failed (manual import needed): {failed_count}")
    print(f"{'='*60}")
    
    if failed_count > 0:
        print("\nFor manual import:")
        print("1. Open Eraser.io workspace: https://app.eraser.io/workspace/xs4eGrR8v2KRhJsJbm4X")
        print("2. Copy diagram code blocks from C4_COMPLETE_ERASER_IO.code")
        print("3. Paste into Eraser.io editor")
        print("4. See ERASER_IO_IMPORT.md for detailed instructions")

if __name__ == "__main__":
    main()
