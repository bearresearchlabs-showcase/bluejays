#!/usr/bin/env python3
"""
Create PostgreSQL instance using APT programmatic API
Supports multiple provisioning methods: Aptible, local Docker, cloud providers
"""

import os
import json
import subprocess
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional


class PostgreSQLProvisioner:
    """Provision PostgreSQL instances programmatically"""

    def __init__(self):
        self.api_key = os.getenv('APT_API_KEY') or os.getenv('APTIBLE_API_KEY')
        self.api_url = os.getenv('APT_API_URL', 'https://api.aptible.com')
        self.environment_id = os.getenv('APT_ENVIRONMENT_ID')

    def provision_aptible(self, db_name: str, plan: str = 'development') -> Dict:
        """Create PostgreSQL instance on Aptible"""
        if not self.api_key:
            raise ValueError("APT_API_KEY or APTIBLE_API_KEY environment variable required")

        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Aptible-Version': '1'
        }

        # Create database
        payload = {
            'handle': db_name,
            'type': 'postgresql',
            'environment_id': self.environment_id,
            'plan': plan
        }

        try:
            response = requests.post(
                f'{self.api_url}/databases',
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()

            db_data = response.json()

            return {
                'success': True,
                'provider': 'aptible',
                'database_id': db_data.get('id'),
                'handle': db_data.get('handle'),
                'connection_url': db_data.get('connection_url'),
                'endpoint': db_data.get('endpoint'),
                'port': db_data.get('port'),
                'database': db_data.get('database'),
                'username': db_data.get('username'),
                'password': db_data.get('password'),
                'created_at': datetime.now().isoformat()
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'provider': 'aptible'
            }

    def provision_docker(self, db_name: str, port: Optional[int] = None) -> Dict:
        """Create PostgreSQL instance using Docker"""
        container_name = f'postgres-{db_name}'
        password = os.getenv('POSTGRES_PASSWORD', 'postgres')

        # Use different ports for different databases to avoid conflicts
        if port is None:
            # Map db1->5432, db2->5433, db3->5434, etc.
            db_num = db_name.replace('db', '').replace('_test', '')
            try:
                port = 5432 + int(db_num) - 1 if db_num.isdigit() else 5432
            except:
                port = 5432

        try:
            # Check if container already exists
            result = subprocess.run(
                ['docker', 'ps', '-a', '--filter', f'name={container_name}', '--format', '{{.Names}}'],
                capture_output=True,
                text=True
            )

            if container_name in result.stdout:
                # Stop and remove existing container
                subprocess.run(['docker', 'stop', container_name], check=False)
                subprocess.run(['docker', 'rm', container_name], check=False)

            # Create new container
            cmd = [
                'docker', 'run', '-d',
                '--name', container_name,
                '-e', f'POSTGRES_PASSWORD={password}',
                '-e', f'POSTGRES_DB={db_name}',
                '-p', f'{port}:5432',
                'postgres:15'
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            container_id = result.stdout.strip()

            # Wait for PostgreSQL to be ready
            import time
            for _ in range(30):
                check_result = subprocess.run(
                    ['docker', 'exec', container_name, 'pg_isready', '-U', 'postgres'],
                    capture_output=True,
                    check=False
                )
                if check_result.returncode == 0:
                    break
                time.sleep(1)

            return {
                'success': True,
                'provider': 'docker',
                'container_name': container_name,
                'container_id': container_id,
                'host': 'localhost',
                'port': port,
                'database': db_name,
                'username': 'postgres',
                'password': password,
                'connection_string': f'postgresql://postgres:{password}@localhost:{port}/{db_name}',
                'created_at': datetime.now().isoformat()
            }
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'error': str(e),
                'provider': 'docker'
            }

    def provision_local(self, db_name: str) -> Dict:
        """Create PostgreSQL instance locally (using brew/apt)"""
        try:
            # Check if PostgreSQL is installed
            result = subprocess.run(
                ['which', 'psql'],
                capture_output=True,
                check=False
            )

            if result.returncode != 0:
                return {
                    'success': False,
                    'error': 'PostgreSQL not found. Install with: brew install postgresql@15',
                    'provider': 'local'
                }

            # Check if PostgreSQL is running
            result = subprocess.run(
                ['pg_isready'],
                capture_output=True,
                check=False
            )

            if result.returncode != 0:
                # Try to start PostgreSQL
                subprocess.run(['brew', 'services', 'start', 'postgresql@15'], check=False)
                import time
                time.sleep(3)

            # Create database
            subprocess.run(
                ['dropdb', '--if-exists', db_name],
                capture_output=True,
                check=False
            )

            result = subprocess.run(
                ['createdb', db_name],
                capture_output=True,
                check=True
            )

            # Get connection info
            user = os.getenv('USER', 'postgres')
            host = 'localhost'
            port = 5432

            return {
                'success': True,
                'provider': 'local',
                'host': host,
                'port': port,
                'database': db_name,
                'username': user,
                'connection_string': f'postgresql://{user}@{host}:{port}/{db_name}',
                'created_at': datetime.now().isoformat()
            }
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'error': str(e),
                'provider': 'local'
            }

    def provision(self, db_name: str, method: Optional[str] = None) -> Dict:
        """Provision PostgreSQL instance using specified method"""
        if method is None:
            # Auto-detect method based on available credentials
            if self.api_key:
                method = 'aptible'
            elif subprocess.run(['which', 'docker'], capture_output=True).returncode == 0:
                method = 'docker'
            else:
                method = 'local'

        print(f"Provisioning PostgreSQL instance '{db_name}' using method: {method}")

        if method == 'aptible':
            return self.provision_aptible(db_name)
        elif method == 'docker':
            return self.provision_docker(db_name)
        elif method == 'local':
            return self.provision_local(db_name)
        else:
            return {
                'success': False,
                'error': f'Unknown provisioning method: {method}',
                'provider': method
            }


def main():
    """Main execution"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 create_postgresql_instance.py <db_name> [method]")
        print("Methods: aptible, docker, local (auto-detect if not specified)")
        sys.exit(1)

    db_name = sys.argv[1]
    method = sys.argv[2] if len(sys.argv) > 2 else None

    provisioner = PostgreSQLProvisioner()
    result = provisioner.provision(db_name, method)

    # Save result
    output_file = Path(f'../results/postgresql_provision_{db_name}.json')
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)

    # Print result
    print("\n" + "="*70)
    print("PROVISIONING RESULT")
    print("="*70)
    print(json.dumps(result, indent=2))

    if result.get('success'):
        print("\n✅ PostgreSQL instance created successfully!")
        if 'connection_string' in result:
            print(f"Connection string: {result['connection_string']}")

        # Set environment variables for testing
        if result.get('host'):
            print(f"\nSet environment variables:")
            print(f"  export POSTGRES_HOST={result.get('host', 'localhost')}")
            print(f"  export POSTGRES_PORT={result.get('port', 5432)}")
            print(f"  export POSTGRES_DB={result.get('database', db_name)}")
            print(f"  export POSTGRES_USER={result.get('username', 'postgres')}")
            if result.get('password'):
                print(f"  export POSTGRES_PASSWORD={result['password']}")
    else:
        print(f"\n❌ Failed to create PostgreSQL instance: {result.get('error')}")
        sys.exit(1)


if __name__ == '__main__':
    main()
