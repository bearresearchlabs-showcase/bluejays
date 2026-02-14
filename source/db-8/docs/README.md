# Job Market Intelligence Database - Documentation

**Database:** db-8
**Created:** 2026-02-04

## Overview

This database contains job market intelligence data from .gov sources (USAJobs.gov, BLS, Department of Labor) and aggregated sources. It supports targeted job applications, market analytics, skill demand analysis, and AI-powered job recommendations mirroring jobright.ai functionality.

## Database Schema

See `../data/schema.sql` for the complete database schema.

### Key Tables

- **user_profiles** - User profiles for job matching and application tracking
- **companies** - Employer/company information from job postings
- **job_postings** - Job listings from various .gov and aggregated sources
- **skills** - Master list of skills/technologies/competencies
- **job_skills_requirements** - Links job postings to required/desired skills
- **user_skills** - Links user profiles to their skills and proficiency levels
- **job_applications** - Tracks user applications to job postings
- **job_recommendations** - AI-generated job recommendations
- **market_trends** - Aggregated job market trends and statistics
- **job_market_analytics** - Detailed analytics for job market intelligence
- **data_source_metadata** - Tracks data sources and extraction metadata
- **user_job_search_history** - Tracks user search behavior for recommendations

## Queries

See `../queries/queries.md` for 30 extremely complex SQL queries.

All queries are designed to work across:
- PostgreSQL
 (Delta Lake)


## Data Sources

- **USAJobs.gov** - Federal job listings
- **BLS** - Bureau of Labor Statistics
- **Department of Labor** - Labor market data
- **Data.gov** - Federal open data

## Usage

1. Load schema: `psql -f data/schema.sql` (PostgreSQL)
2. Load data: `psql -f data/data.sql` (PostgreSQL)
3. Run queries: See `queries/queries.md`

---
**Last Updated:** 2026-02-04
