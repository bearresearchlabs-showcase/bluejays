# Job Market Intelligence Database - db-8

**Deliverable:** db-8
**Status:** 🚧 In Progress
**Created:** 2026-02-04

## Overview

Job Market Intelligence and Targeted Application System integrating data from .gov sources (USAJobs.gov, BLS, Department of Labor) and aggregated sources. Supports targeted job applications, market analytics, skill demand analysis, and AI-powered job recommendations mirroring jobright.ai functionality.

## Structure

```
db-8/
├── queries/ # 30+ extremely complex SQL queries
├── results/ # Test results and validation reports
├── docs/ # Database documentation
├── data/ # Schema and data files
├── scripts/ # Utility scripts
├── research/ # ETL/ELT pipelines and research notebooks
└── metadata/ # Pipeline execution metadata
```

## Contents

- **Queries:** 30 extremely complex SQL queries in `queries/queries.md`
- **Results:** JSON test results in `results/`
- **Documentation:** Database documentation in `docs/`
- **Data:** Schema and data files in `data/`
- **Research:** ETL/ELT pipelines for job data ingestion in `research/`

## Database Schema

The database includes 12 core tables:

- **user_profiles** - User profiles for job matching
- **companies** - Employer/company information
- **job_postings** - Job listings from .gov and aggregated sources
- **skills** - Master list of skills/technologies
- **job_skills_requirements** - Job skill requirements
- **user_skills** - User skill profiles
- **job_applications** - Application tracking
- **job_recommendations** - AI-powered job recommendations
- **market_trends** - Aggregated market trends
- **job_market_analytics** - Detailed market analytics
- **data_source_metadata** - Data source tracking
- **user_job_search_history** - Search behavior tracking

## Data Sources

- **USAJobs.gov API** - Federal job listings
- **BLS Public Data API** - Employment statistics
- **Department of Labor Open Data Portal** - Labor datasets
- **State Employment Boards** - State-level job data
- **Aggregated Sources** - Commercial job aggregators

## Usage

### Phase 0: Query Extraction (REQUIRED)

```bash
cd db-8
python3 scripts/extract_queries_to_json.py
```

### Validation

```bash
# Phase 1: Fix verification
python3 scripts/verify_fixes.py

# Phase 2 & 4: Syntax validation and evaluation
python3 scripts/comprehensive_validator.py

# Phase 3: Execution testing
python3 scripts/execution_tester.py

# Phase 5: Generate final report
python3 scripts/generate_final_report.py
```

## Compatibility

All queries are designed to work across:
- PostgreSQL
 (Delta Lake)


## Features

- **AI-Powered Job Matching** - Multi-dimensional scoring algorithm
- **Market Intelligence** - Comprehensive trend analysis
- **Skill Demand Analysis** - Demand vs supply analysis
- **Application Tracking** - Success rate analysis
- **Company Intelligence** - Competitive analysis
- **Geographic Analysis** - Location-based insights
- **Salary Benchmarking** - Market positioning
- **Federal Job Analysis** - USAJobs.gov integration
- **Remote Work Trends** - Work model evolution
- **Predictive Analytics** - Market forecasting

## Research

See `research/etl_elt_pipeline.ipynb` for ETL/ELT pipeline implementation for job data ingestion from .gov sources.

## Related Documentation

- See `.cursor/rules/database-compatibility.mdc` for query requirements
- See `.cursor/rules/query-validation-suite.mdc` for validation workflow
- See `.cursor/rules/research-metadata-directories.mdc` for research directory usage

---
**Last Updated:** 2026-02-04
