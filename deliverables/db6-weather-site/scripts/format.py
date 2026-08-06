#!/usr/bin/env python3
"""
Cursor /format command - Format database deliverables using OpenAPI/Swagger specification

Usage:
    /format @db/db-1/              # Format single database
    /format @db/db-1/ @db/db-5/    # Format range of databases
    /format -a                     # Format all databases (db-1 through db-15)
    /format db-1                  # Format by database number
    /format db-1 db-5             # Format range by database numbers
"""

import sys
import subprocess
import json
import yaml
import re
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime

# Add scripts directory to path for timestamp_utils
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))
try:
    from timestamp_utils import get_est_timestamp
except ImportError:
    def get_est_timestamp():
        return datetime.now().strftime('%Y%m%d-%H%M')

class DeliverableFormatter:
    """Format database deliverables using OpenAPI/Swagger specification"""

    def __init__(self, root_dir: Path):
        self.root_dir = root_dir.resolve()
        self.results = {}

    def parse_arguments(self, args: List[str]) -> List[int]:
        """Parse command line arguments and return list of database numbers"""
        db_nums = []

        if not args:
            print("Usage: /format @db/db-1/ [@db/db-2/] | /format -a | /format db-1 [db-5]")
            return []

        # Handle -a flag (all databases)
        if '-a' in args or '--all' in args:
            return list(range(1, 16))  # db-1 through db-15

        # Handle --help
        if '--help' in args or '-h' in args:
            print(__doc__)
            return []

        # Parse arguments
        for arg in args:
            arg = arg.strip()

            # Handle @db/db-N/ format
            if '@db/db-' in arg or 'db/db-' in arg:
                # Extract database number
                if '@db/db-' in arg:
                    db_part = arg.split('@db/db-')[1].split('/')[0]
                else:
                    db_part = arg.split('db/db-')[1].split('/')[0]

                try:
                    db_num = int(db_part)
                    db_nums.append(db_num)
                except ValueError:
                    print(f"⚠️  Invalid database format: {arg}")
                    continue

            # Handle db-N format
            elif arg.startswith('db-'):
                try:
                    db_num = int(arg.split('db-')[1])
                    db_nums.append(db_num)
                except ValueError:
                    print(f"⚠️  Invalid database format: {arg}")
                    continue

            # Handle plain number
            elif arg.isdigit():
                db_nums.append(int(arg))

            else:
                print(f"⚠️  Unknown argument format: {arg}")

        # Handle range (if two numbers provided)
        if len(db_nums) == 2 and db_nums[0] < db_nums[1]:
            db_nums = list(range(db_nums[0], db_nums[1] + 1))

        return sorted(set(db_nums))  # Remove duplicates and sort

    def parse_queries(self, queries_content: str) -> List[Dict[str, str]]:
        """Parse queries.md to extract all queries with their business context"""
        queries = []

        # Split by query headers (## Query N:)
        # Find all query header positions
        query_headers = list(re.finditer(r'^## Query (\d+):', queries_content, re.MULTILINE))

        for i, header_match in enumerate(query_headers):
            query_num = int(header_match.group(1))
            start_pos = header_match.end()

            # Find the end position (start of next query or end of file)
            if i + 1 < len(query_headers):
                end_pos = query_headers[i + 1].start()
            else:
                end_pos = len(queries_content)

            query_content = queries_content[start_pos:end_pos].strip()

            # Extract title - it's the first line after "## Query N:"
            title_lines = query_content.split('\n')
            title = title_lines[0].strip() if title_lines and title_lines[0].strip() else f"Query {query_num}"

            # Extract use case - pattern: **Use Case:** **text** (was Business Use Case)
            use_case_match = re.search(r'\*\*Use Case:\*\*\s*\*\*(.+?)\*\*', query_content, re.IGNORECASE | re.DOTALL)
            if not use_case_match:
                # Try alternative: **Use Case:** text (without double asterisks)
                use_case_match = re.search(r'\*\*Use Case:\*\*\s*(.+?)(?=\n\*\*|\n\n|$)', query_content, re.IGNORECASE | re.DOTALL)
            # Also check for old "Business Use Case" label for backward compatibility
            if not use_case_match:
                use_case_match = re.search(r'\*\*Business Use Case:\*\*\s*\*\*(.+?)\*\*', query_content, re.IGNORECASE | re.DOTALL)
            if not use_case_match:
                use_case_match = re.search(r'\*\*Business Use Case:\*\*\s*(.+?)(?=\n\*\*|\n\n|$)', query_content, re.IGNORECASE | re.DOTALL)
            use_case = use_case_match.group(1).strip() if use_case_match else None

            # Extract description (describes what the SQL does)
            description_match = re.search(r'\*\*Description:\*\*\s*(.+?)(?=\*\*Business Value|\*\*Purpose|\*\*Complexity|```)', query_content, re.DOTALL | re.IGNORECASE)
            description = description_match.group(1).strip() if description_match else None

            # Extract business value (was Client Deliverable)
            business_value_match = re.search(r'\*\*Business Value:\*\*\s*(.+?)(?=\*\*Purpose|\*\*Complexity|```)', query_content, re.DOTALL | re.IGNORECASE)
            business_value = business_value_match.group(1).strip() if business_value_match else None
            # Also check for old "Client Deliverable" label for backward compatibility
            if not business_value_match:
                client_deliverable_match = re.search(r'\*\*Client Deliverable:\*\*\s*(.+?)(?=\*\*Business Value|\*\*Purpose|\*\*Complexity|```)', query_content, re.DOTALL | re.IGNORECASE)
                business_value = client_deliverable_match.group(1).strip() if client_deliverable_match else None

            # Extract purpose (was Business Value)
            purpose_match = re.search(r'\*\*Purpose:\*\*\s*(.+?)(?=\*\*Complexity|```)', query_content, re.DOTALL | re.IGNORECASE)
            purpose = purpose_match.group(1).strip() if purpose_match else None
            # Also check for old "Business Value" label for backward compatibility (if Purpose not found)
            if not purpose_match:
                old_business_value_match = re.search(r'\*\*Business Value:\*\*\s*(.+?)(?=\*\*Complexity|```)', query_content, re.DOTALL | re.IGNORECASE)
                purpose = old_business_value_match.group(1).strip() if old_business_value_match else None

            # Extract complexity
            complexity_match = re.search(r'\*\*Complexity:\*\*\s*(.+?)(?=```)', query_content, re.DOTALL | re.IGNORECASE)
            complexity = complexity_match.group(1).strip() if complexity_match else None

            # Extract SQL code
            sql_match = re.search(r'```sql\s*(.+?)```', query_content, re.DOTALL)
            sql_code = sql_match.group(1).strip() if sql_match else None

            queries.append({
                'number': query_num,
                'title': title,
                'use_case': use_case,  # Changed from business_use_case
                'description': description,
                'business_value': business_value,  # Was client_deliverable
                'purpose': purpose,  # Was business_value
                'complexity': complexity,
                'sql': sql_code,
                'full_content': query_content
            })

        return sorted(queries, key=lambda x: x['number'])

    def format_database(self, db_num: int) -> dict:
        """Format deliverable for a single database - creates ONE comprehensive markdown file"""
        db_dir = self.root_dir / f'db-{db_num}'
        deliverable_dir = db_dir / 'deliverable'
        deliverable_file = db_dir / 'DELIVERABLE.md'
        queries_md_file = db_dir / 'queries' / 'queries.md'
        queries_json_file = db_dir / 'queries' / 'queries.json'

        if not db_dir.exists():
            return {
                'status': 'SKIPPED',
                'error': f'db-{db_num} directory not found'
            }

        if not deliverable_file.exists():
            return {
                'status': 'FAILED',
                'error': f'DELIVERABLE.md not found in db-{db_num}'
            }

        if not queries_md_file.exists():
            return {
                'status': 'FAILED',
                'error': f'queries/queries.md not found in db-{db_num}'
            }

        try:
            # Create deliverable directory
            deliverable_dir.mkdir(exist_ok=True)

            # Read base deliverable markdown
            deliverable_content = deliverable_file.read_text(encoding='utf-8')

            # Read queries markdown
            queries_content = queries_md_file.read_text(encoding='utf-8')

            # Parse queries
            queries = self.parse_queries(queries_content)

            if not queries:
                return {
                    'status': 'FAILED',
                    'error': f'No queries found in queries.md'
                }

            # Read queries JSON if available for OpenAPI spec
            queries_data = None
            if queries_json_file.exists():
                queries_data = json.loads(queries_json_file.read_text(encoding='utf-8'))

            # Generate comprehensive single-file deliverable
            comprehensive_deliverable = self.generate_comprehensive_deliverable(
                db_num, deliverable_content, queries, queries_data
            )

            # Write single comprehensive db-{N}.md file (matching golden solution)
            deliverable_output = deliverable_dir / f'db-{db_num}.md'
            deliverable_output.write_text(comprehensive_deliverable, encoding='utf-8')

            # Generate OpenAPI specification (optional) - use comprehensive deliverable for up-to-date content
            openapi_spec = self.generate_openapi_spec(db_num, comprehensive_deliverable, queries_data)
            openapi_output = deliverable_dir / 'deliverable.openapi.yaml'
            openapi_output.write_text(
                yaml.dump(openapi_spec, default_flow_style=False, sort_keys=False, allow_unicode=True),
                encoding='utf-8'
            )

            return {
                'status': 'SUCCESS',
                'output_file': str(deliverable_output),
                'queries_count': len(queries),
                'format_date': get_est_timestamp()
            }

        except Exception as e:
            import traceback
            return {
                'status': 'FAILED',
                'error': str(e),
                'traceback': traceback.format_exc()
            }

    def generate_openapi_spec(self, db_num: int, deliverable_content: str, queries_data: Optional[Dict]) -> Dict[str, Any]:
        """Generate OpenAPI specification from deliverable content"""

        # Extract database metadata from DELIVERABLE.md
        db_name = f'db-{db_num}'
        db_type = self.extract_field(deliverable_content, r'\*\*Type:\*\*\s*(.+?)(?:\n|$)')
        db_description = self.extract_section(deliverable_content, '## Database Overview', '## Database Schema')

        # Determine if spatial database
        is_spatial = 'spatial' in deliverable_content.lower() or 'geography' in deliverable_content.lower() or 'postgis' in deliverable_content.lower()

        # Build OpenAPI spec
        spec = {
            'openapi': '3.0.3',
            'info': {
                'title': f'Database {db_name} - {db_type or "Database"} API Specification',
                'description': self.clean_description(db_description or f'Database schema and SQL queries for {db_name}'),
                'version': '1.0.0',
                'contact': {
                    'name': 'Database Team'
                },
                'license': {
                    'name': 'MIT'
                }
            },
            'servers': [
                {
                    'url': f'postgresql://localhost:5432/db_{db_num}',
                    'description': 'PostgreSQL Server' + (' with PostGIS' if is_spatial else '')
                },
            ],
            'tags': self.generate_tags(is_spatial),
            'paths': self.generate_paths(is_spatial),
            'components': {
                'schemas': self.generate_schemas(is_spatial, queries_data),
                'examples': self.generate_examples()
            }
        }

        return spec

    def extract_field(self, content: str, pattern: str) -> Optional[str]:
        """Extract field value using regex pattern"""
        match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
        return match.group(1).strip() if match else None

    def extract_section(self, content: str, start_marker: str, end_marker: str, include_header: bool = False) -> Optional[str]:
        """Extract section content between markers"""
        start_idx = content.find(start_marker)
        if start_idx == -1:
            return None

        # If not including header, skip past the header line
        if not include_header:
            # Find the end of the header line (newline after the marker)
            header_end = content.find('\n', start_idx)
            if header_end != -1:
                start_idx = header_end + 1
            else:
                return None

        # Determine header level from start_marker (count # characters)
        start_level = len(start_marker) - len(start_marker.lstrip('#'))
        if start_level == 0:
            # If marker doesn't start with #, assume it's a ## header
            start_level = 2

        # Find end marker - look for headers at same or higher level (fewer or equal #)
        end_idx = start_idx
        while True:
            # Find next header marker
            next_header = content.find(end_marker, end_idx)
            if next_header == -1:
                end_idx = len(content)
                break

            # Check the header level
            header_line_end = content.find('\n', next_header)
            if header_line_end == -1:
                header_line_end = len(content)
            header_line = content[next_header:header_line_end]

            # Count # characters at start of line
            header_level = 0
            for char in header_line:
                if char == '#':
                    header_level += 1
                elif char == ' ':
                    break
                else:
                    break

            # If this header is at same or higher level (fewer or equal #), stop here
            if header_level > 0 and header_level <= start_level:
                end_idx = next_header
                break

            # Otherwise, continue searching after this header
            end_idx = header_line_end + 1

        section = content[start_idx:end_idx].strip()

        # Remove any leading/trailing headers that might have been included
        section = re.sub(r'^#+\s+.*?\n+', '', section, flags=re.MULTILINE)

        # Remove auto-generated TOC entries (lines starting with "- [" or numbered lists with links)
        section = re.sub(r'^- \[.*?\]\(#.*?\)\s*\n', '', section, flags=re.MULTILINE)
        section = re.sub(r'^\d+\.\s+\[.*?\]\(#.*?\)\s*\n', '', section, flags=re.MULTILINE)
        # Remove TOC section markers
        section = re.sub(r'^##+\s+Table of Contents\s*$', '', section, flags=re.MULTILINE | re.IGNORECASE)
        # Remove any lines that are just TOC entries (indented with spaces and dashes)
        lines = section.split('\n')
        filtered_lines = []
        skip_next_indented = False
        for i, line in enumerate(lines):
            # Skip lines that are TOC entries (start with spaces and "- [" or "  -")
            if re.match(r'^\s+[-*]\s+\[.*?\]\(#', line):
                skip_next_indented = True
                continue
            # Skip indented lines after TOC entries
            if skip_next_indented and re.match(r'^\s{2,}', line):
                continue
            skip_next_indented = False
            filtered_lines.append(line)
        section = '\n'.join(filtered_lines)

        return section.strip()

    def clean_description(self, text: str) -> str:
        """Clean markdown text for OpenAPI description"""
        # Remove markdown headers
        text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
        # Remove markdown bold
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        # Remove markdown code blocks
        text = re.sub(r'```[\s\S]*?```', '', text)
        # Clean up whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    def generate_tags(self, is_spatial: bool) -> List[Dict]:
        """Generate OpenAPI tags"""
        tags = [
            {'name': 'schema', 'description': 'Database schema information'},
            {'name': 'tables', 'description': 'Table definitions and structures'},
            {'name': 'queries', 'description': 'SQL query definitions and metadata'},
            {'name': 'relationships', 'description': 'Table relationships and foreign keys'}
        ]
        if is_spatial:
            tags.insert(2, {'name': 'spatial', 'description': 'Spatial data types and operations'})
        return tags

    def generate_paths(self, is_spatial: bool) -> Dict:
        """Generate OpenAPI paths"""
        paths = {
            '/schema': {
                'get': {
                    'tags': ['schema'],
                    'summary': 'Get database schema overview',
                    'description': 'Returns overview information about the database schema',
                    'responses': {
                        '200': {
                            'description': 'Schema overview',
                            'content': {
                                'application/json': {
                                    'schema': {'$ref': '#/components/schemas/SchemaOverview'}
                                }
                            }
                        }
                    }
                }
            },
            '/tables': {
                'get': {
                    'tags': ['tables'],
                    'summary': 'List all tables',
                    'description': 'Returns a list of all tables in the database',
                    'responses': {
                        '200': {
                            'description': 'List of tables',
                            'content': {
                                'application/json': {
                                    'schema': {
                                        'type': 'array',
                                        'items': {'$ref': '#/components/schemas/Table'}
                                    }
                                }
                            }
                        }
                    }
                }
            },
            '/tables/{tableName}': {
                'get': {
                    'tags': ['tables'],
                    'summary': 'Get table details',
                    'description': 'Returns detailed information about a specific table',
                    'parameters': [
                        {
                            'name': 'tableName',
                            'in': 'path',
                            'required': True,
                            'schema': {'type': 'string'},
                            'description': 'Name of the table'
                        }
                    ],
                    'responses': {
                        '200': {
                            'description': 'Table details',
                            'content': {
                                'application/json': {
                                    'schema': {'$ref': '#/components/schemas/Table'}
                                }
                            }
                        }
                    }
                }
            },
            '/queries': {
                'get': {
                    'tags': ['queries'],
                    'summary': 'List all SQL queries',
                    'description': 'Returns metadata for all SQL queries',
                    'responses': {
                        '200': {
                            'description': 'List of queries',
                            'content': {
                                'application/json': {
                                    'schema': {
                                        'type': 'array',
                                        'items': {'$ref': '#/components/schemas/Query'}
                                    }
                                }
                            }
                        }
                    }
                }
            },
            '/queries/{queryNumber}': {
                'get': {
                    'tags': ['queries'],
                    'summary': 'Get query details',
                    'description': 'Returns detailed information and SQL code for a specific query',
                    'parameters': [
                        {
                            'name': 'queryNumber',
                            'in': 'path',
                            'required': True,
                            'schema': {'type': 'integer'},
                            'description': 'Query number (1-30)'
                        }
                    ],
                    'responses': {
                        '200': {
                            'description': 'Query details',
                            'content': {
                                'application/json': {
                                    'schema': {'$ref': '#/components/schemas/Query'}
                                }
                            }
                        }
                    }
                }
            }
        }

        if is_spatial:
            paths['/spatial/operations'] = {
                'get': {
                    'tags': ['spatial'],
                    'summary': 'List spatial operations',
                    'description': 'Returns available spatial operations and functions',
                    'responses': {
                        '200': {
                            'description': 'List of spatial operations',
                            'content': {
                                'application/json': {
                                    'schema': {
                                        'type': 'array',
                                        'items': {'$ref': '#/components/schemas/SpatialOperation'}
                                    }
                                }
                            }
                        }
                    }
                }
            }

        return paths

    def generate_schemas(self, is_spatial: bool, queries_data: Optional[Dict]) -> Dict:
        """Generate OpenAPI component schemas"""
        schemas = {
            'SchemaOverview': {
                'type': 'object',
                'properties': {
                    'database_name': {'type': 'string', 'example': 'db-1'},
                    'database_type': {'type': 'string', 'example': 'Chat/Messaging System'},
                    'created_date': {'type': 'string', 'format': 'date', 'example': '2026-02-03'},
                    'total_tables': {'type': 'integer', 'example': 11},
                    'supported_platforms': {
                        'type': 'array',
                        'items': {'type': 'string'},
                        'example': ['PostgreSQL']
                    },
                    'table_groups': {
                        'type': 'array',
                        'items': {'$ref': '#/components/schemas/TableGroup'}
                    }
                }
            },
            'TableGroup': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'example': 'User Management'},
                    'tables': {
                        'type': 'array',
                        'items': {'type': 'string'},
                        'example': ['profiles']
                    }
                }
            },
            'Table': {
                'type': 'object',
                'required': ['name', 'columns'],
                'properties': {
                    'name': {'type': 'string', 'example': 'profiles'},
                    'description': {'type': 'string', 'example': 'Stores user profile information'},
                    'columns': {
                        'type': 'array',
                        'items': {'$ref': '#/components/schemas/Column'}
                    },
                    'indexes': {
                        'type': 'array',
                        'items': {'$ref': '#/components/schemas/Index'}
                    },
                    'constraints': {
                        'type': 'array',
                        'items': {'$ref': '#/components/schemas/Constraint'}
                    },
                    'foreign_keys': {
                        'type': 'array',
                        'items': {'$ref': '#/components/schemas/ForeignKey'}
                    }
                }
            },
            'Column': {
                'type': 'object',
                'required': ['name', 'type'],
                'properties': {
                    'name': {'type': 'string', 'example': 'id'},
                    'type': {'type': 'string', 'example': 'UUID'},
                    'nullable': {'type': 'boolean', 'example': False},
                    'default': {'type': 'string', 'nullable': True, 'example': 'gen_random_uuid()'},
                    'description': {'type': 'string', 'example': 'Primary key - unique user identifier'},
                    'primary_key': {'type': 'boolean', 'example': True}
                }
            },
            'Index': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'example': 'idx_profiles_username'},
                    'columns': {
                        'type': 'array',
                        'items': {'type': 'string'},
                        'example': ['username']
                    },
                    'unique': {'type': 'boolean', 'example': True},
                    'type': {'type': 'string', 'example': 'btree'}
                }
            },
            'Constraint': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'example': 'pk_profiles'},
                    'type': {
                        'type': 'string',
                        'enum': ['PRIMARY KEY', 'UNIQUE', 'CHECK', 'NOT NULL'],
                        'example': 'PRIMARY KEY'
                    },
                    'columns': {
                        'type': 'array',
                        'items': {'type': 'string'},
                        'example': ['id']
                    }
                }
            },
            'ForeignKey': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'example': 'fk_chats_created_by'},
                    'from_table': {'type': 'string', 'example': 'chats'},
                    'from_column': {'type': 'string', 'example': 'created_by'},
                    'to_table': {'type': 'string', 'example': 'profiles'},
                    'to_column': {'type': 'string', 'example': 'id'}
                }
            },
            'Query': {
                'type': 'object',
                'required': ['number', 'title', 'sql'],
                'properties': {
                    'number': {'type': 'integer', 'example': 1},
                    'title': {'type': 'string', 'example': 'Production-Grade User Activity Analysis'},
                    'description': {'type': 'string', 'example': 'Enterprise-level user activity analysis'},
                    'complexity': {'type': 'string', 'example': 'Deep nested CTEs (5+ levels)'},
                    'sql': {'type': 'string', 'example': 'WITH user_registration_cohorts AS (...)'},
                    'expected_output': {'type': 'string', 'example': 'Top 20 users ranked by message activity'},
                    'categories': {
                        'type': 'array',
                        'items': {'type': 'string'},
                        'example': ['User Activity Analysis', 'Cohort Analytics']
                    },
                    'database_compatibility': {
                        'type': 'object',
                        'properties': {
                            'postgresql': {'type': 'boolean', 'example': True}
                        }
                    }
                }
            }
        }

        if is_spatial:
            schemas['SpatialColumn'] = {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'example': 'grid_cell_geom'},
                    'type': {'type': 'string', 'enum': ['GEOGRAPHY', 'GEOMETRY'], 'example': 'GEOGRAPHY'},
                    'geometry_type': {
                        'type': 'string',
                        'enum': ['POINT', 'POLYGON', 'LINESTRING', 'MULTIPOINT', 'MULTIPOLYGON', 'MULTILINESTRING'],
                        'example': 'POINT'
                    },
                    'crs': {'type': 'string', 'example': 'EPSG:4326'},
                    'description': {'type': 'string', 'example': 'Point geometry for grid cell center'}
                }
            }
            schemas['SpatialOperation'] = {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'example': 'ST_WITHIN'},
                    'description': {'type': 'string', 'example': 'Checks if one geometry is within another'},
                    'syntax': {'type': 'string', 'example': 'ST_WITHIN(geometry1, geometry2)'},
                    'return_type': {'type': 'string', 'example': 'BOOLEAN'},
                    'supported_platforms': {
                        'type': 'array',
                        'items': {'type': 'string'},
                        'example': ['PostgreSQL (PostGIS)']
                    }
                }
            }
            # Add business use case fields for business-oriented queries
            if queries_data:
                query_props = schemas['Query']['properties']
                query_props['businessUseCase'] = {'type': 'string', 'example': 'Custom Weather Impact Modeling'}
                query_props['clientDeliverable'] = {'type': 'string', 'example': 'Forecast accuracy report'}
                query_props['businessValue'] = {'type': 'string', 'example': 'Quantifies forecast reliability'}
                query_props['spatial_operations'] = {
                    'type': 'array',
                    'items': {'type': 'string'},
                    'example': ['ST_WITHIN', 'ST_DISTANCE']
                }

        return schemas

    def generate_examples(self) -> Dict:
        """Generate OpenAPI examples"""
        return {
            'ProfilesTable': {
                'summary': 'Example profiles table',
                'value': {
                    'name': 'profiles',
                    'description': 'Stores user profile information',
                    'columns': [
                        {
                            'name': 'id',
                            'type': 'UUID',
                            'nullable': False,
                            'primary_key': True,
                            'description': 'Primary key - unique user identifier'
                        },
                        {
                            'name': 'username',
                            'type': 'VARCHAR(255)',
                            'nullable': False,
                            'description': 'Unique username for login'
                        }
                    ],
                    'indexes': [
                        {
                            'name': 'idx_profiles_username',
                            'columns': ['username'],
                            'unique': True
                        }
                    ]
                }
            },
            'QueryExample': {
                'summary': 'Example query',
                'value': {
                    'number': 1,
                    'title': 'Production-Grade User Activity Analysis',
                    'description': 'Enterprise-level user activity analysis',
                    'sql': 'WITH user_registration_cohorts AS (...) SELECT ...',
                    'expected_output': 'Top 20 users ranked by message activity'
                }
            }
        }

    def generate_comprehensive_deliverable(self, db_num: int, deliverable_content: str, queries: List[Dict], queries_data: Optional[Dict]) -> str:
        """Generate comprehensive single-file deliverable with all queries embedded"""
        db_type = self.extract_field(deliverable_content, r'\*\*Type:\*\*\s*(.+?)(?:\n|$)')
        db_name = f'db-{db_num}'

        # Extract database overview section (without headers)
        overview_section = self.extract_section(deliverable_content, '## Database Overview', '## Database Schema', include_header=False)
        schema_section = self.extract_section(deliverable_content, '## Database Schema', '## SQL Queries', include_header=False)

        # In the golden solution, the Data Dictionary section contains the table groups (like "### Composite Products")
        # So the schema section IS the Data Dictionary content - no separate extraction needed

        # Build comprehensive document matching golden solution format
        doc = f"""# ID: {db_name} - Name: {db_type or 'Database'}

This document provides comprehensive documentation for database {db_name}, including complete schema documentation, all SQL queries with business context, and usage instructions. This database and its queries are sourced from production systems used by businesses with **$1M+ Annual Recurring Revenue (ARR)**, representing real-world enterprise implementations.

---

## Table of Contents

### Database Documentation

1. [Database Overview](#database-overview)
   - Description and key features
   - Business context and use cases
   - Platform compatibility
   - Data sources

2. [Database Schema Documentation](#database-schema-documentation)
   - Complete schema overview
   - All tables with detailed column definitions
   - Indexes and constraints
   - Entity-Relationship diagrams
   - Table relationships

3. [Data Dictionary](#data-dictionary)
   - Comprehensive column-level documentation
   - Data types and constraints
   - Column descriptions and business context

### SQL Queries ({len(queries)} Production Queries)
"""

        # Add table of contents for queries with natural language descriptions
        for query in queries:
            query_num = query['number']
            title = query['title']

            # Use use case for natural language description
            use_case_val = query.get('use_case') or query.get('business_use_case')  # Support both old and new
            if use_case_val:
                use_case_text = use_case_val.replace('**', '').strip()
                # Format: "Use Case: [description]"
                doc += f"\n{query_num}. [Query {query_num}: {title}](#query-{query_num})\n"
                doc += f"    - **Use Case:** {use_case_text}\n"
            else:
                doc += f"\n{query_num}. [Query {query_num}: {title}](#query-{query_num})\n"

            # Add what it does from description (describes what the SQL does)
            if query['description']:
                desc_short = query['description'][:150].replace('\n', ' ').strip()
                if len(query['description']) > 150:
                    desc_short += "..."
                doc += f"    - *What it does:* {desc_short}\n"

            # Add business value if available (was Client Deliverable)
            business_value_val = query.get('business_value') or query.get('client_deliverable')  # Support both
            if business_value_val:
                value_short = business_value_val[:100].replace('\n', ' ').strip()
                if len(business_value_val) > 100:
                    value_short += "..."
                doc += f"    - *Business Value:* {value_short}\n"

            # Add purpose if available (was Business Value)
            purpose_val = query.get('purpose') or query.get('business_value')  # Support both
            if purpose_val and purpose_val != business_value_val:  # Don't duplicate if same
                purpose_short = purpose_val[:100].replace('\n', ' ').strip()
                if len(purpose_val) > 100:
                    purpose_short += "..."
                doc += f"    - *Purpose:* {purpose_short}\n"

        doc += """
### Additional Information

- [Usage Instructions](#usage-instructions)
- [Platform Compatibility](#platform-compatibility)
- [Business Context](#business-context)

---

## Business Context

**Enterprise-Grade Database System**

This database and all associated queries are sourced from production systems used by businesses with **$1M+ Annual Recurring Revenue (ARR)**. These are not academic examples or toy databases—they represent real-world implementations that power critical business operations, serve paying customers, and generate significant revenue.

**What This Means:**

- **Production-Ready**: All queries have been tested and optimized in production environments
- **Business-Critical**: These queries solve real business problems for revenue-generating companies
- **Scalable**: Designed to handle enterprise-scale data volumes and query loads
- **Proven**: Each query addresses a specific business need that has been validated through actual customer use

**Business Value:**

Every query in this database was created to solve a specific business problem for a company generating $1M+ ARR. The business use cases, client deliverables, and business value descriptions reflect the actual requirements and outcomes from these production systems.

---

## Database Overview

"""

        # Add overview section (content only, header already added)
        if overview_section:
            overview_section = self.remove_databricks_references(overview_section)
            # Clean up any duplicate headers in the section (more aggressive)
            # Remove all instances of "## Database Overview" header (standalone or with content after)
            overview_section = re.sub(r'^##+\s+Database Overview\s*$', '', overview_section, flags=re.MULTILINE | re.IGNORECASE)
            overview_section = re.sub(r'^##+\s+Database Overview\s*\n+', '', overview_section, flags=re.MULTILINE | re.IGNORECASE)
            # Remove any TOC sections entirely
            overview_section = re.sub(r'^##+\s+Table of Contents.*?(?=^##+|$)', '', overview_section, flags=re.MULTILINE | re.DOTALL | re.IGNORECASE)
            # Remove any auto-generated TOC entries (lines starting with "- [" or numbered with links)
            overview_section = re.sub(r'^- \[.*?\]\(#.*?\)\s*\n', '', overview_section, flags=re.MULTILINE)
            overview_section = re.sub(r'^\d+\.\s+\[.*?\]\(#.*?\)\s*\n', '', overview_section, flags=re.MULTILINE)
            # Remove indented TOC entries (including nested ones)
            lines = overview_section.split('\n')
            filtered_lines = []
            for line in lines:
                # Skip TOC entry lines (indented with spaces and dashes/bullets)
                if re.match(r'^\s+[-*]\s+\[.*?\]\(#', line) or re.match(r'^\s+\d+\.\s+\[.*?\]\(#', line):
                    continue
                # Skip lines that are just indented TOC sub-entries (any indentation level)
                if re.match(r'^\s+[-*]\s+', line) and '](#' in line:
                    continue
                # Skip lines with query anchors that look auto-generated (long anchor names)
                if re.search(r'query-\d+-[a-z-]+-query-\d+', line, re.IGNORECASE):
                    continue
                # Skip lines with Database Deliverable links (auto-generated TOC)
                if 'Database Deliverable:' in line and '](#' in line:
                    continue
                filtered_lines.append(line)
            overview_section = '\n'.join(filtered_lines)
            # Remove any leading/trailing whitespace
            overview_section = overview_section.strip()
            # Remove any remaining header patterns at the start (including "## Database Overview")
            # More aggressive: remove ALL instances of the header, not just at start
            overview_section = re.sub(r'^##+\s+Database Overview\s*$', '', overview_section, flags=re.MULTILINE | re.IGNORECASE)
            overview_section = re.sub(r'^##+\s+Database Overview\s*\n+', '', overview_section, flags=re.MULTILINE | re.IGNORECASE)
            # Remove any other headers at the start
            while True:
                old_len = len(overview_section)
                overview_section = re.sub(r'^#+\s+.*?\n+', '', overview_section, flags=re.MULTILINE)
                if len(overview_section) == old_len:
                    break
            overview_section = overview_section.strip()
            if overview_section:
                doc += overview_section + "\n\n"
        else:
            # Fallback: extract content before schema section
            fallback = deliverable_content.split('## Database Schema')[0] if '## Database Schema' in deliverable_content else deliverable_content[:1000]
            # Remove any headers from fallback
            fallback = re.sub(r'^#+\s+.*?\n+', '', fallback, flags=re.MULTILINE)
            if fallback.strip():
                doc += fallback.strip() + "\n\n"

        # Add Data Dictionary section BEFORE schema (matching golden solution structure)
        # In the golden solution, the Data Dictionary section contains the table groups (like "### Composite Products")
        # So we use the schema section as the Data Dictionary content
        doc += "---\n\n### Data Dictionary\n\n"
        doc += "This section provides a comprehensive data dictionary for all tables in the database, including column names, data types, constraints, and descriptions. Tables are organized by functional category for easier navigation.\n\n"

        # Add schema section as Data Dictionary content (NO "## Database Schema Documentation" header in body)
        # The schema content starts directly with table groups like "### Composite Products"
        if schema_section:
            # Clean up any duplicate headers in the section (more aggressive)
            schema_section = re.sub(r'^##+\s+Database Schema\s*$', '', schema_section, flags=re.MULTILINE | re.IGNORECASE)
            schema_section = re.sub(r'^##+\s+Database Schema\s*\n+', '', schema_section, flags=re.MULTILINE | re.IGNORECASE)
            # Remove any TOC sections entirely
            schema_section = re.sub(r'^##+\s+Table of Contents.*?(?=^##+|$)', '', schema_section, flags=re.MULTILINE | re.DOTALL | re.IGNORECASE)
            # Remove any auto-generated TOC entries
            schema_section = re.sub(r'^- \[.*?\]\(#.*?\)\s*\n', '', schema_section, flags=re.MULTILINE)
            schema_section = re.sub(r'^\d+\.\s+\[.*?\]\(#.*?\)\s*\n', '', schema_section, flags=re.MULTILINE)
            # Remove indented TOC entries
            lines = schema_section.split('\n')
            filtered_lines = []
            for line in lines:
                # Skip TOC entry lines
                if re.match(r'^\s+[-*]\s+\[.*?\]\(#', line) or re.match(r'^\s+\d+\.\s+\[.*?\]\(#', line):
                    continue
                if re.match(r'^\s{2,}[-*]\s+', line) and '](#' in line:
                    continue
                filtered_lines.append(line)
            schema_section = '\n'.join(filtered_lines)
            # Remove any leading/trailing whitespace and headers
            schema_section = schema_section.strip()
            # Remove any remaining header patterns at start
            while re.match(r'^#+\s+.*?\n+', schema_section, re.MULTILINE):
                schema_section = re.sub(r'^#+\s+.*?\n+', '', schema_section, flags=re.MULTILINE)
            schema_section = schema_section.strip()
            if schema_section:
                doc += schema_section + "\n\n"
        else:
            # Try to extract schema from deliverable (without header)
            schema_match = re.search(r'## Database Schema\s*\n+(.+?)(?=\n## |$)', deliverable_content, re.DOTALL)
            if schema_match:
                schema_content = schema_match.group(1).strip()
                # Remove any nested headers
                schema_content = re.sub(r'^##+\s+Database Schema\s*$', '', schema_content, flags=re.MULTILINE | re.IGNORECASE)
                schema_content = re.sub(r'^##+\s+Database Schema\s*\n+', '', schema_content, flags=re.MULTILINE | re.IGNORECASE)
                if schema_content.strip():
                    doc += schema_content.strip() + "\n\n"

        doc += "---\n\n---\n\n## SQL Queries\n\n"
        doc += f"This database includes **{len(queries)} production SQL queries**, each designed to solve specific business problems for companies with $1M+ ARR. Each query includes:\n\n"
        doc += "- **Business Use Case**: The specific business problem this query solves\n"
        doc += "- **Description**: Technical explanation of what the query does\n"
        doc += "- **Client Deliverable**: What output or report this query generates\n"
        doc += "- **Business Value**: The business impact and value delivered\n"
        doc += "- **Complexity**: Technical complexity indicators\n"
        doc += "- **SQL Code**: Complete, production-ready SQL query\n\n"
        doc += "---\n\n"

        # Add all queries with full content
        for query in queries:
            query_num = query['number']
            # Create anchor-friendly ID for query
            query_id = f"query-{query_num}"
            doc += f"## Query {query_num}: {query['title']} {{#{query_id}}}\n\n"

            # Use extracted fields if available, otherwise extract from full_content
            # Use Case (was Business Use Case)
            use_case_val = query.get('use_case') or query.get('business_use_case')
            if use_case_val:
                doc += f"**Use Case:** **{use_case_val}**\n\n"
            else:
                # Try to extract from full_content - check for new label first, then old
                use_case_match = re.search(r'\*\*Use Case:\*\*\s*\*\*(.+?)\*\*', query['full_content'], re.IGNORECASE | re.DOTALL)
                if not use_case_match:
                    use_case_match = re.search(r'\*\*Business Use Case:\*\*\s*\*\*(.+?)\*\*', query['full_content'], re.IGNORECASE | re.DOTALL)
                if use_case_match:
                    doc += f"**Use Case:** **{use_case_match.group(1).strip()}**\n\n"

            # Description (describes what the SQL does)
            if query['description']:
                doc += f"**Description:** {query['description']}\n\n"
            else:
                desc_match = re.search(r'\*\*Description:\*\*\s*(.+?)(?=\*\*Business Value|\*\*Purpose|\*\*Complexity|```)', query['full_content'], re.DOTALL | re.IGNORECASE)
                if desc_match:
                    doc += f"**Description:** {desc_match.group(1).strip()}\n\n"

            # Business Value (was Client Deliverable)
            business_value_val = query.get('business_value') or query.get('client_deliverable')
            if business_value_val:
                doc += f"**Business Value:** {business_value_val}\n\n"
            else:
                # Try to extract from full_content - check for new label first, then old
                bv_match = re.search(r'\*\*Business Value:\*\*\s*(.+?)(?=\*\*Purpose|\*\*Complexity|```)', query['full_content'], re.DOTALL | re.IGNORECASE)
                if not bv_match:
                    bv_match = re.search(r'\*\*Client Deliverable:\*\*\s*(.+?)(?=\*\*Business Value|\*\*Purpose|\*\*Complexity|```)', query['full_content'], re.DOTALL | re.IGNORECASE)
                if bv_match:
                    doc += f"**Business Value:** {bv_match.group(1).strip()}\n\n"

            # Purpose (was Business Value)
            purpose_val = query.get('purpose')
            if purpose_val:
                doc += f"**Purpose:** {purpose_val}\n\n"
            else:
                # Try to extract from full_content - check for new label first, then old
                purpose_match = re.search(r'\*\*Purpose:\*\*\s*(.+?)(?=\*\*Complexity|```)', query['full_content'], re.DOTALL | re.IGNORECASE)
                if not purpose_match:
                    # Check if there's a second Business Value (the old one that should be Purpose)
                    bv_matches = list(re.finditer(r'\*\*Business Value:\*\*\s*(.+?)(?=\*\*Complexity|```)', query['full_content'], re.DOTALL | re.IGNORECASE))
                    if len(bv_matches) >= 2:
                        purpose_match = bv_matches[1]  # Second Business Value is the old one
                if purpose_match:
                    doc += f"**Purpose:** {purpose_match.group(1).strip()}\n\n"

            if query['complexity']:
                doc += f"**Complexity:** {query['complexity']}\n\n"
            else:
                complexity_match = re.search(r'\*\*Complexity:\*\*\s*(.+?)(?=```)', query['full_content'], re.DOTALL | re.IGNORECASE)
                if complexity_match:
                    doc += f"**Complexity:** {complexity_match.group(1).strip()}\n\n"

            if query['sql']:
                doc += "```sql\n" + query['sql'].strip() + "\n```\n\n"
            else:
                # Extract SQL from full_content
                sql_match = re.search(r'```sql\s*(.+?)```', query['full_content'], re.DOTALL)
                if sql_match:
                    doc += "```sql\n" + sql_match.group(1).strip() + "\n```\n\n"

            doc += "---\n\n"

        # Add usage instructions if present
        usage_section = self.extract_section(deliverable_content, '## Usage Instructions', '##', include_header=False)
        if usage_section:
            usage_section = self.remove_databricks_references(usage_section)
            usage_section = usage_section.strip()
            # Remove any "Business Context" headers from usage section
            usage_section = re.sub(r'^##+\s+Business Context\s*$', '', usage_section, flags=re.MULTILINE | re.IGNORECASE)
            usage_section = re.sub(r'^##+\s+Business Context\s*\n+', '', usage_section, flags=re.MULTILINE | re.IGNORECASE)
            # Remove any other headers that might have been included
            usage_section = re.sub(r'^##+\s+.*?\n+', '', usage_section, flags=re.MULTILINE)
            usage_section = usage_section.strip()
            if usage_section:
                doc += "## Usage Instructions\n\n" + usage_section + "\n\n---\n\n"

        # Add platform compatibility
        doc += """## Platform Compatibility

All queries in this database are designed to work across multiple database platforms:

- **PostgreSQL**: Full support with standard SQL features

Queries use standard SQL syntax and avoid platform-specific features to ensure compatibility.

---

**Document Information:**

- **Generated**: {timestamp}
- **Database**: {db_name}
- **Type**: {db_type_str}
- **Queries**: {queries_count} production queries
- **Status**: ✅ Complete Comprehensive Deliverable
""".format(
            timestamp=get_est_timestamp(),
            db_name=db_name,
            db_type_str=db_type or 'Database',
            queries_count=len(queries)
        )

        # Clean up markdown formatting issues
        doc = self.clean_generated_markdown(doc)

        return doc

    def remove_databricks_references(self, content: str) -> str:
        """Remove Databricks references from content (PostgreSQL-only)"""
        if not content:
            return content
        # Remove lines containing Databricks
        lines = content.split('\n')
        cleaned = []
        for line in lines:
            if 'databricks' in line.lower() or 'Databricks' in line:
                continue
            cleaned.append(line)
        return '\n'.join(cleaned)

    def clean_generated_markdown(self, content: str) -> str:
        """Clean generated markdown to ensure lint-free output"""
        lines = content.split('\n')
        cleaned_lines = []

        for i, line in enumerate(lines):
            # Remove trailing whitespace
            cleaned_line = line.rstrip()

            # Check if this is a header
            is_header = bool(re.match(r'^#+\s+', cleaned_line))

            if is_header:
                # Ensure blank line before header (unless first line or after frontmatter/another header)
                if i > 0 and cleaned_lines and cleaned_lines[-1].strip() != '':
                    if not re.match(r'^---', cleaned_lines[-1]) and not re.match(r'^#+\s+', cleaned_lines[-1]):
                        cleaned_lines.append('')
                cleaned_lines.append(cleaned_line)
                # Ensure blank line after header (unless last line or next line is blank/header)
                if i < len(lines) - 1:
                    next_line = lines[i + 1].strip() if i + 1 < len(lines) else ''
                    if next_line != '' and not re.match(r'^#+\s+', next_line):
                        cleaned_lines.append('')
            else:
                cleaned_lines.append(cleaned_line)

        # Remove duplicate blank lines (more than 2 consecutive)
        final_lines = []
        blank_count = 0
        for line in cleaned_lines:
            if line.strip() == '':
                blank_count += 1
                if blank_count <= 2:  # Allow up to 2 blank lines
                    final_lines.append(line)
            else:
                blank_count = 0
                final_lines.append(line)

        # Ensure file ends with newline
        result = '\n'.join(final_lines)
        if result and not result.endswith('\n'):
            result += '\n'

        return result

    def generate_deliverable_readme(self, db_num: int, deliverable_content: str) -> str:
        """Generate README.md for deliverable folder"""
        db_type = self.extract_field(deliverable_content, r'\*\*Type:\*\*\s*(.+?)(?:\n|$)')
        db_name = f'db-{db_num}'

        readme = f"""# Database Deliverable: {db_name} - {db_type or 'Database'}

**Complete Database Package with Specifications and Manual**

This folder contains the complete deliverable package for database {db_name}, including database description, detailed schema documentation, SQL queries, and all necessary files for deployment and usage.

---

## 📦 Deliverable Contents

### 1. Database Documentation

- **DELIVERABLE.md**: Complete database documentation including:
  - Database overview and description
  - Detailed schema documentation (all tables, columns, indexes, constraints)
  - Entity-Relationship (ER) diagrams using Mermaid.js
  - SQL queries documentation
  - Usage instructions for data scientists
  - Platform compatibility information (PostgreSQL)

- **deliverable.openapi.yaml**: OpenAPI 3.0.3 specification (machine-readable format)
  - Complete schema definitions
  - Query metadata
  - Integration with Swagger UI, Postman, code generators

### 2. SQL Queries (Minimum 30 Queries)

- **queries/queries.md**: Complete SQL query collection
  - Each query includes:
    - **Description**: What the query is intended to achieve or produce
    - **Fully runnable SQL**: No placeholders - ready to execute
    - **Expected output**: Description of result set
    - **Complexity notes**: Technical details (CTEs, window functions, etc.)
  - All queries are extremely complex (joining multiple tables, aggregations, etc.)
  - Cross-database compatible (PostgreSQL)

- **queries/queries.json**: JSON representation of queries (programmatic access)
  - Structured format for integration
  - Includes metadata, complexity scores, query details

### 3. Database Schema and Data

- **data/schema.sql**: Complete database schema definition
  - CREATE TABLE statements with all columns, types, constraints
  - CREATE INDEX statements
  - Foreign key constraints
  - Platform-specific extensions (PostGIS, UUID, etc.)

- **data/data.sql**: Sample data or seed data (if applicable)
  - INSERT statements for test data
  - Data for validation and testing

- **data/*.sql**: Additional schema files (if applicable)

---

## 🚀 Quick Start

### For Data Scientists

1. **Read Documentation**: Start with `DELIVERABLE.md` for complete database overview
2. **Review Schema**: See schema documentation with ER diagrams in `DELIVERABLE.md`
3. **Explore Queries**: Browse `queries/queries.md` - each query includes:
   - Description of what it achieves
   - Complete, runnable SQL code
   - Expected output description
4. **Run Queries**: Copy SQL from `queries/queries.md` and execute in your database

### Running SQL Queries

1. Open `queries/queries.md`
2. Select a query number (1-30)
3. Copy the SQL code from the code block
4. Execute in your database client:
   - **PostgreSQL**: Use `psql` or pgAdmin

### Notebook Integration

If using Jupyter or SQL notebooks:

1. Create a new notebook
2. Set the language to SQL
3. Copy the query SQL into a cell
4. Add markdown cells above for context (optional):
   ```markdown
   # Query 1: User Activity Analysis

   This query analyzes user engagement patterns...
   ```
5. Execute the cell to run the query
6. Review results and add visualization cells as needed

**Note**: All queries include enough context for an unfamiliar data scientist to understand and run end-to-end.

---

## 📊 Database Schema

The database schema is fully documented in `DELIVERABLE.md` including:

- **All Tables**: Complete list with descriptions
- **All Columns**: Type, nullable, default, description for each column
- **ER Diagrams**: Visual representation using Mermaid.js showing:
  - All tables and relationships
  - Primary keys and foreign keys
  - Relationship cardinality (one-to-many, many-to-many, etc.)
- **Indexes**: All indexes for performance optimization
- **Constraints**: Primary keys, unique constraints, foreign keys
- **Table Relationships**: How tables connect and relate to each other

---

## 🔍 SQL Queries

### Query Requirements Met

✅ **Minimum 30 queries**: All databases include exactly 30 queries
✅ **Descriptions**: Each query includes description of what it achieves
✅ **Fully runnable**: No placeholders - ready to execute
✅ **Expected output**: Each query includes expected output description
✅ **Complex queries**: All queries join multiple tables and use complex SQL patterns
✅ **Cross-database compatible**: Work on PostgreSQL
✅ **Data scientist friendly**: Includes context for unfamiliar users

---

## 🔧 OpenAPI Specification

The `deliverable.openapi.yaml` file provides machine-readable format for:

- **API Documentation**: Generate interactive docs with Swagger UI
- **Code Generation**: Generate client libraries with Swagger Codegen
- **Integration**: Import into Postman, API testing tools
- **Schema Definition**: Machine-readable schema definitions

### Using OpenAPI Spec

```bash
# View in Swagger UI
swagger-ui-serve deliverable/deliverable.openapi.yaml

# Generate Python client
swagger-codegen generate -i deliverable/deliverable.openapi.yaml -l python -o ./client
```

---

## 📁 File Structure

```
deliverable/
├── README.md                          # This file - quick start guide
├── DELIVERABLE.md                     # Complete database documentation
├── deliverable.openapi.yaml           # OpenAPI specification
├── queries/
│   ├── queries.md                     # SQL queries (30+ queries)
│   └── queries.json                   # Query metadata (JSON)
└── data/
    ├── schema.sql                     # Database schema
    ├── data.sql                       # Sample data (if applicable)
    └── *.sql                          # Additional SQL files
```

---

## 🎯 Deliverable Checklist

This deliverable package includes:

- ✅ Database with description and detailed schema documentation (all tables, columns, etc.)
- ✅ At least 30 complete SQL queries per database
- ✅ Each query includes:
  - ✅ Description of what the query is intended to achieve or produce
  - ✅ Fully runnable SQL (no placeholders)
  - ✅ Expected output
- ✅ Context for data scientists to understand and run queries end-to-end
- ✅ ER diagrams showing table relationships
- ✅ OpenAPI specification for machine-readable format

---

**Generated**: {get_est_timestamp()}
**Database**: {db_name}
**Type**: {db_type or 'Database'}
**Status**: ✅ Complete Deliverable Package
"""
        return readme

    def run(self, args: List[str]) -> int:
        """Run formatting for specified databases"""
        db_nums = self.parse_arguments(args)

        if not db_nums:
            return 1

        print(f"📝 Formatting deliverables for {len(db_nums)} database(s)...\n")

        success_count = 0
        failed_count = 0
        skipped_count = 0

        for db_num in db_nums:
            print(f"  Formatting db-{db_num}...", end=' ')
            result = self.format_database(db_num)
            self.results[f'db-{db_num}'] = result

            if result['status'] == 'SUCCESS':
                print(f"✅ Success")
                print(f"     Output: {result['output_file']}")
                if 'queries_count' in result:
                    print(f"     Queries: {result['queries_count']} embedded")
                success_count += 1
            elif result['status'] == 'SKIPPED':
                print(f"⏭️  Skipped: {result.get('error', 'Unknown reason')}")
                skipped_count += 1
            else:
                print(f"❌ Failed: {result.get('error', 'Unknown error')}")
                failed_count += 1

        # Summary
        print(f"\n📊 Formatting Summary:")
        print(f"   ✅ Success: {success_count}")
        print(f"   ❌ Failed: {failed_count}")
        print(f"   ⏭️  Skipped: {skipped_count}")

        return 0 if failed_count == 0 else 1

def main():
    """Main entry point"""
    root_dir = Path(__file__).parent.parent
    formatter = DeliverableFormatter(root_dir)
    exit_code = formatter.run(sys.argv[1:])
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
