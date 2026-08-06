#!/usr/bin/env python3
"""
Update docker-compose.yml to add Streamlit ports for each database
"""

import yaml
from pathlib import Path

BASE_DIR = Path('/Users/machine/Documents/AQ/db')
COMPOSE_FILE = BASE_DIR / 'docker' / 'docker-compose.yml'

# Streamlit port mapping (8501 + db number offset)
STREAMLIT_PORTS = {
    'db-6': 8506,
    'db-7': 8507,
    'db-8': 8508,
    'db-9': 8509,
    'db-10': 8510,
    'db-11': 8511,
    'db-12': 8512,
    'db-13': 8513,
    'db-14': 8514,
    'db-15': 8515,
}

def update_compose_file():
    """Update docker-compose.yml with Streamlit ports."""
    
    with open(COMPOSE_FILE) as f:
        compose_data = yaml.safe_load(f)
    
    # Update each service
    for service_name, streamlit_port in STREAMLIT_PORTS.items():
        if service_name in compose_data['services']:
            service = compose_data['services'][service_name]
            
            # Add Streamlit port if not present
            if 'ports' in service:
                # Check if Streamlit port already exists
                streamlit_port_exists = any(
                    f'{streamlit_port}:8501' in str(port) for port in service['ports']
                )
                
                if not streamlit_port_exists:
                    service['ports'].append(f"{streamlit_port}:8501")
                    print(f"✅ Added Streamlit port {streamlit_port}:8501 for {service_name}")
            else:
                service['ports'] = [f"{streamlit_port}:8501"]
                print(f"✅ Created ports section with Streamlit port {streamlit_port}:8501 for {service_name}")
    
    # Write updated compose file
    with open(COMPOSE_FILE, 'w') as f:
        yaml.dump(compose_data, f, default_flow_style=False, sort_keys=False)
    
    print(f"\n✅ Updated {COMPOSE_FILE}")

if __name__ == '__main__':
    update_compose_file()
