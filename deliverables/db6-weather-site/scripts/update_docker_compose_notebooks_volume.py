#!/usr/bin/env python3
"""
Update docker-compose.yml to add notebooks volume mount for all services
"""

import re
from pathlib import Path

BASE_DIR = Path('/Users/machine/Documents/AQ/db')
COMPOSE_FILE = BASE_DIR / 'docker' / 'docker-compose.yml'

def update_compose_file():
    """Update docker-compose.yml with notebooks volume."""
    
    with open(COMPOSE_FILE) as f:
        content = f.read()
    
    # Pattern to match volumes section for each service
    # We need to add the notebooks volume before db-*-data volume
    pattern = r'(volumes:\s*\n\s*- \.\.\/client\/db\/db-(\d+):/workspace/client/db/db-\2:ro\s*\n\s*- \.\.\/db-\2:/workspace/db/db-\2:ro)\s*\n\s*(- db-\2-data:/var/lib/postgresql/data)'
    
    replacement = r'\1\n    - ../docker/notebooks:/workspace/docker/notebooks:ro\n    \3'
    
    updated_content = re.sub(pattern, replacement, content)
    
    # Write updated file
    with open(COMPOSE_FILE, 'w') as f:
        f.write(updated_content)
    
    print(f"✅ Updated {COMPOSE_FILE} with notebooks volume mount")

if __name__ == '__main__':
    update_compose_file()
