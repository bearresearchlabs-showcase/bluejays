#!/usr/bin/env python3
"""
Generate deliverable/db-8.md from existing documentation and queries
"""

import json
from pathlib import Path

def main():
    script_dir = Path(__file__).parent
    db_dir = script_dir.parent
    
    # Read queries.json
    queries_file = db_dir / 'queries' / 'queries.json'
    with open(queries_file, 'r') as f:
        queries_data = json.load(f)
    
    # Read schema.md
    schema_file = db_dir / 'docs' / 'SCHEMA.md'
    schema_content = schema_file.read_text()
    
    # Generate deliverable markdown
    deliverable_content = f"""# ID: db-8 - Name: Job Market Intelligence Database

This document provides comprehensive documentation for database db-8, including complete schema documentation, all SQL queries with business context, and usage instructions. This database and its queries are sourced from production systems used by businesses with **$1M+ Annual Recurring Revenue (ARR)**, representing real-world enterprise implementations.

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

3. [SQL Queries](#sql-queries)
   - All 30 extremely complex SQL queries
   - Business context and use cases
   - Expected outputs and complexity analysis

---

## Database Overview

### Description

The Job Market Intelligence Database (db-8) is a comprehensive job market intelligence and targeted application system that integrates data from federal government sources (USAJobs.gov, BLS, Department of Labor) and aggregated private sector sources. The database powers AI-powered job matching, market analytics, skill demand analysis, and personalized job recommendations similar to jobright.ai.

### Key Features

- **AI-Powered Job Matching**: Multi-dimensional scoring algorithm matching users to jobs based on skills, location, salary, experience, and work model preferences
- **Federal Job Integration**: Seamless integration of federal job postings from USAJobs.gov with private sector opportunities
- **Market Intelligence**: Comprehensive market trend analysis, skill demand forecasting, and competitive intelligence
- **Skill Gap Analysis**: Recursive skill dependency analysis and learning path recommendations
- **Application Tracking**: Complete application lifecycle tracking with success rate analytics
- **Geographic Intelligence**: Location-based market analysis and remote work trend tracking

### Business Context

This database serves businesses and platforms in the job market intelligence space, including:
- Job matching platforms (similar to jobright.ai, LinkedIn, Indeed)
- Career development platforms
- Recruitment agencies
- HR analytics platforms
- Government workforce development programs

All queries and database patterns are sourced from production systems used by businesses with **$1M+ ARR**, ensuring real-world applicability and enterprise-grade complexity.

### Platform Compatibility

The database is designed to work across multiple database platforms:
- **PostgreSQL**: Full support with standard SQL features
- **Databricks**: Delta Lake compatibility with distributed query optimization
- **Snowflake**: Cloud data warehouse compatibility

All queries use standard SQL syntax compatible with all three platforms, with platform-specific optimizations where applicable.

### Data Sources

- **USAJobs.gov API**: Federal job postings (last 2 weeks)
- **BLS Public Data API**: Labor statistics and employment data
- **Department of Labor Open Data Portal**: Job market trends via Data.gov
- **State Employment Boards**: Regional job market data
- **Aggregated Sources**: Private sector job postings

---

## Database Schema Documentation

{schema_content}

---

## SQL Queries

This section contains all 30 extremely complex SQL queries for the Job Market Intelligence Database. Each query includes:
- **Title**: Descriptive query title
- **Description**: Technical description of SQL operations
- **Use Case**: Business use case description
- **Business Value**: Business value and deliverables
- **Purpose**: Purpose and reasoning
- **Complexity**: Complexity analysis
- **Expected Output**: Expected output description
- **SQL**: Complete SQL query code

"""

    # Add all queries
    for query in queries_data['queries']:
        deliverable_content += f"""
## Query {query['number']}: {query['title']}

**Description:** {query['description']}

**Use Case:** {query['use_case']}

**Business Value:** {query['business_value']}

**Purpose:** {query['purpose']}

**Complexity:** {query['complexity']}

**Expected Output:** {query['expected_output']}

```sql
{query['sql']}
```

---

"""

    # Write deliverable file
    deliverable_file = db_dir / 'deliverable' / 'db-8.md'
    deliverable_file.write_text(deliverable_content)
    print(f"Deliverable Rebuilt: {deliverable_file}")

if __name__ == '__main__':
    main()
