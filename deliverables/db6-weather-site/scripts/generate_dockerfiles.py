#!/usr/bin/env python3
"""
Generate Dockerfiles for each db-* database
"""

from pathlib import Path

BASE_DIR = Path('/Users/machine/Documents/AQ/db')
DOCKER_DIR = BASE_DIR / 'docker'
TEMPLATE_FILE = DOCKER_DIR / 'Dockerfile.template'

DATABASES = [f'db-{i}' for i in range(6, 16)]

def generate_dockerfile(db_name: str):
    """Generate Dockerfile for a specific database."""
    
    # Read template
    with open(TEMPLATE_FILE) as f:
        template = f.read()
    
    # Database-specific customizations can go here
    # For now, all databases use the same Dockerfile
    
    # Write Dockerfile
    dockerfile_path = DOCKER_DIR / f'Dockerfile.{db_name}'
    with open(dockerfile_path, 'w') as f:
        f.write(template)
    
    print(f"✅ Generated {dockerfile_path.relative_to(BASE_DIR)}")

def main():
    """Generate all Dockerfiles."""
    print("="*80)
    print("GENERATING DOCKERFILES FOR ALL DATABASES")
    print("="*80)
    
    for db_name in DATABASES:
        generate_dockerfile(db_name)
    
    print(f"\n{'='*80}")
    print("All Dockerfiles generated!")
    print(f"{'='*80}")

if __name__ == '__main__':
    main()
