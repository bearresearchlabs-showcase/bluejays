---
title: Job Market Intelligence Database — Documentation
description: Installation guide, specifications, schema, data dictionary.
database: db-8
---

# Job Market Intelligence Database — Documentation

**Database:** db-8  
**Content:** Installation guide, specifications, schema, data dictionary.

---

## Installation Guide

### Step 1: Prerequisites

Ensure PostgreSQL is installed. See specifications for version requirements.

---

### Step 2: Create Database

Create a new database for this schema.

```bash
createdb -U postgres db_8
```

---

### Step 3: Load Schema

Load schema.sql to create tables, indexes, and constraints.

```bash
psql -U postgres -d db_8 -f schema.sql
```

---

### Step 4: Load Data (Optional)

Load production data from data_large.sql when available (>= 1GB). No sample data.

```bash
psql -U postgres -d db_8 -f data_large.sql
```

---

## Specifications

- **PostgreSQL:** 14+
- **Disk:** 100 MB minimum
- **Memory:** 256 MB minimum
- **Platforms:** PostgreSQL

Standard PostgreSQL. No extensions required unless noted.

---

## Schema Overview

**Total tables:** 12

- `user_profiles` — (see data dictionary)
- `companies` — (see data dictionary)
- `job_postings` — (see data dictionary)
- `skills` — (see data dictionary)
- `job_skills_requirements` — (see data dictionary)
- `user_skills` — (see data dictionary)
- `job_applications` — (see data dictionary)
- `job_recommendations` — (see data dictionary)
- `market_trends` — (see data dictionary)
- `job_market_analytics` — (see data dictionary)
- `data_source_metadata` — (see data dictionary)
- `user_job_search_history` — (see data dictionary)

---

## Data Dictionary

### `user_profiles`

- `user_id` VARCHAR(255) PRIMARY KEY
- `email` VARCHAR(255) UNIQUE, NOT NULL
- `full_name` VARCHAR(255) 
- `location_city` VARCHAR(100) 
- `location_state` VARCHAR(2) 
- `location_country` VARCHAR(2) 
- `location_latitude` NUMERIC(10, 7) 
- `location_longitude` NUMERIC(10, 7) 
- `current_job_title` VARCHAR(255) 
- `current_company` VARCHAR(255) 
- `years_experience` INTEGER 
- `education_level` VARCHAR(50) 
- `resume_text` VARCHAR(16777216) 
- `linkedin_url` VARCHAR(500) 
- `github_url` VARCHAR(500) 
- `portfolio_url` VARCHAR(500) 
- `preferred_work_model` VARCHAR(50)  — 'remote', 'hybrid', 'onsite'
- `salary_expectation_min` INTEGER 
- `salary_expectation_max` INTEGER 
- `preferred_locations` VARCHAR(16777216)  — JSON array of preferred locations
- `created_at` TIMESTAMP 
- `updated_at` TIMESTAMP 
- `last_active_at` TIMESTAMP 
- `profile_completeness_score` NUMERIC(5, 2) 
- `is_active` BOOLEAN 

### `companies`

- `company_id` VARCHAR(255) PRIMARY KEY
- `company_name` VARCHAR(255) NOT NULL
- `company_name_normalized` VARCHAR(255)  — Normalized name for matching
- `industry` VARCHAR(100) 
- `company_size` VARCHAR(50)  — 'startup', 'small', 'medium', 'large', 'enterprise'
- `headquarters_city` VARCHAR(100) 
- `headquarters_state` VARCHAR(2) 
- `headquarters_country` VARCHAR(2) 
- `website_url` VARCHAR(500) 
- `linkedin_url` VARCHAR(500) 
- `description` VARCHAR(16777216) 
- `founded_year` INTEGER 
- `employee_count` INTEGER 
- `revenue_range` VARCHAR(50) 
- `is_federal_agency` BOOLEAN 
- `agency_code` VARCHAR(50)  — For federal agencies
- `data_source` VARCHAR(50)  — 'usajobs', 'bls', 'state_board', 'aggregated'
- `created_at` TIMESTAMP 
- `updated_at` TIMESTAMP 
- `company_rating` NUMERIC(3, 2)  — Average rating from reviews
- `total_reviews` INTEGER 

### `job_postings`

- `job_id` VARCHAR(255) PRIMARY KEY
- `company_id` VARCHAR(255) NOT NULL
- `job_title` VARCHAR(255) NOT NULL
- `job_title_normalized` VARCHAR(255)  — Normalized title for matching
- `job_description` VARCHAR(16777216) 
- `job_type` VARCHAR(50)  — 'full_time', 'part_time', 'contract', 'temporary', 'internship'
- `work_model` VARCHAR(50)  — 'remote', 'hybrid', 'onsite'
- `location_city` VARCHAR(100) 
- `location_state` VARCHAR(2) 
- `location_country` VARCHAR(2) 
- `location_latitude` NUMERIC(10, 7) 
- `location_longitude` NUMERIC(10, 7) 
- `salary_min` INTEGER 
- `salary_max` INTEGER 
- `salary_currency` VARCHAR(3) 
- `salary_type` VARCHAR(50)  — 'annual', 'hourly', 'monthly'
- `posted_date` TIMESTAMP NOT NULL
- `expiration_date` TIMESTAMP 
- `application_url` VARCHAR(1000) 
- `application_method` VARCHAR(50)  — 'url', 'email', 'ats', 'usajobs'
- `is_active` BOOLEAN 
- `is_federal_job` BOOLEAN 
- `usajobs_id` VARCHAR(255)  — USAJobs.gov job ID
- `agency_name` VARCHAR(255)  — For federal jobs
- `pay_plan` VARCHAR(50)  — For federal jobs
- `grade_level` VARCHAR(50)  — For federal jobs
- `data_source` VARCHAR(50) NOT NULL — 'usajobs', 'bls', 'state_board', 'aggregated'
- `source_url` VARCHAR(1000) 
- `industry` VARCHAR(100)  — Denormalized from companies for query performance
- `created_at` TIMESTAMP 
- `updated_at` TIMESTAMP 
- `view_count` INTEGER 
- `application_count` INTEGER 
- `match_score_avg` NUMERIC(5, 2)  — Average match score from recommendations
- `job_fingerprint` VARCHAR(500)  — Hash for deduplication/matching

### `skills`

- `skill_id` VARCHAR(255) PRIMARY KEY
- `skill_name` VARCHAR(255) UNIQUE, NOT NULL
- `skill_category` VARCHAR(100)  — 'programming', 'framework', 'tool', 'soft_skill', 'certification'
- `skill_type` VARCHAR(50)  — 'technical', 'soft', 'certification', 'language'
- `parent_skill_id` VARCHAR(255)  — For skill hierarchies
- `description` VARCHAR(16777216) 
- `popularity_score` NUMERIC(10, 2)  — Based on job posting frequency
- `created_at` TIMESTAMP 

### `job_skills_requirements`

- `requirement_id` VARCHAR(255) PRIMARY KEY
- `job_id` VARCHAR(255) NOT NULL
- `skill_id` VARCHAR(255) NOT NULL
- `requirement_type` VARCHAR(50)  — 'required', 'preferred', 'nice_to_have'
- `importance_score` NUMERIC(5, 2)  — 1-10 importance score
- `years_experience_required` NUMERIC(4, 1) 
- `extracted_from_description` BOOLEAN 
- `created_at` TIMESTAMP 

### `user_skills`

- `user_skill_id` VARCHAR(255) PRIMARY KEY
- `user_id` VARCHAR(255) NOT NULL
- `skill_id` VARCHAR(255) NOT NULL
- `proficiency_level` VARCHAR(50)  — 'beginner', 'intermediate', 'advanced', 'expert'
- `proficiency_score` NUMERIC(5, 2)  — 1-10 proficiency score
- `years_experience` NUMERIC(4, 1) 
- `last_used_date` DATE 
- `verified` BOOLEAN  — Skills verified through assessments/certifications
- `created_at` TIMESTAMP 
- `updated_at` TIMESTAMP 

### `job_applications`

- `application_id` VARCHAR(255) PRIMARY KEY
- `user_id` VARCHAR(255) NOT NULL
- `job_id` VARCHAR(255) NOT NULL
- `application_status` VARCHAR(50)  — 'draft', 'submitted', 'under_review', 'interview', 'offer', 'rejected', 'withdrawn'
- `application_date` TIMESTAMP 
- `submitted_at` TIMESTAMP 
- `status_updated_at` TIMESTAMP 
- `cover_letter_text` VARCHAR(16777216) 
- `resume_version` VARCHAR(255) 
- `match_score` NUMERIC(5, 2)  — Calculated match score at time of application
- `application_method` VARCHAR(50)  — 'direct', 'ats', 'email', 'usajobs'
- `application_reference_id` VARCHAR(255)  — External application ID
- `notes` VARCHAR(16777216) 
- `created_at` TIMESTAMP 
- `updated_at` TIMESTAMP 

### `job_recommendations`

- `recommendation_id` VARCHAR(255) PRIMARY KEY
- `user_id` VARCHAR(255) NOT NULL
- `job_id` VARCHAR(255) NOT NULL
- `match_score` NUMERIC(5, 2) NOT NULL — Overall match score (0-100)
- `skill_match_score` NUMERIC(5, 2)  — Skill alignment score
- `location_match_score` NUMERIC(5, 2)  — Location preference match
- `salary_match_score` NUMERIC(5, 2)  — Salary expectation match
- `experience_match_score` NUMERIC(5, 2)  — Experience level match
- `work_model_match_score` NUMERIC(5, 2)  — Work model preference match
- `recommendation_reason` VARCHAR(16777216)  — Explanation for recommendation
- `recommendation_rank` INTEGER  — Rank within user's recommendations
- `is_liked` BOOLEAN 
- `is_applied` BOOLEAN 
- `is_dismissed` BOOLEAN 
- `recommendation_date` TIMESTAMP 
- `expires_at` TIMESTAMP  — Recommendation expiration
- `created_at` TIMESTAMP 

### `market_trends`

- `trend_id` VARCHAR(255) PRIMARY KEY
- `trend_date` DATE NOT NULL
- `geographic_scope` VARCHAR(50)  — 'national', 'state', 'city', 'metro'
- `location_state` VARCHAR(2) 
- `location_city` VARCHAR(100) 
- `location_metro` VARCHAR(100) 
- `industry` VARCHAR(100) 
- `job_category` VARCHAR(100) 
- `total_job_postings` INTEGER 
- `new_job_postings` INTEGER  — New postings in period
- `active_job_seekers` INTEGER  — Estimated from application data
- `average_salary_min` INTEGER 
- `average_salary_max` INTEGER 
- `median_salary` INTEGER 
- `top_skills` VARCHAR(16777216)  — JSON array of top skills
- `skill_demand_trend` VARCHAR(16777216)  — JSON object of skill demand changes
- `competition_index` NUMERIC(5, 2)  — Applications per job ratio
- `growth_rate` NUMERIC(10, 4)  — Percentage growth in postings
- `data_source` VARCHAR(50)  — 'bls', 'aggregated', 'usajobs'
- `created_at` TIMESTAMP 

### `job_market_analytics`

- `analytics_id` VARCHAR(255) PRIMARY KEY
- `analysis_date` DATE NOT NULL
- `analysis_type` VARCHAR(50)  — 'daily', 'weekly', 'monthly', 'quarterly'
- `geographic_scope` VARCHAR(50) 
- `location_state` VARCHAR(2) 
- `location_city` VARCHAR(100) 
- `industry` VARCHAR(100) 
- `total_companies` INTEGER 
- `total_active_jobs` INTEGER 
- `remote_job_percentage` NUMERIC(5, 2) 
- `hybrid_job_percentage` NUMERIC(5, 2) 
- `average_time_to_fill_days` INTEGER 
- `average_applications_per_job` NUMERIC(10, 2) 
- `top_employers` VARCHAR(16777216)  — JSON array
- `emerging_skills` VARCHAR(16777216)  — JSON array of trending skills
- `declining_skills` VARCHAR(16777216)  — JSON array of declining skills
- `salary_trends` VARCHAR(16777216)  — JSON object with salary trend data
- `job_type_distribution` VARCHAR(16777216)  — JSON object
- `work_model_distribution` VARCHAR(16777216)  — JSON object
- `created_at` TIMESTAMP 

### `data_source_metadata`

- `metadata_id` VARCHAR(255) PRIMARY KEY
- `source_name` VARCHAR(100) NOT NULL — 'usajobs', 'bls', 'state_board'
- `source_type` VARCHAR(50)  — 'api', 'scraper', 'manual', 'aggregated'
- `extraction_date` TIMESTAMP NOT NULL
- `extraction_method` VARCHAR(100) 
- `records_extracted` INTEGER 
- `records_new` INTEGER 
- `records_updated` INTEGER 
- `records_failed` INTEGER 
- `extraction_status` VARCHAR(50)  — 'success', 'partial', 'failed'
- `error_message` VARCHAR(16777216) 
- `api_endpoint` VARCHAR(1000) 
- `api_response_code` INTEGER 
- `extraction_duration_seconds` INTEGER 
- `created_at` TIMESTAMP 

### `user_job_search_history`

- `search_id` VARCHAR(255) PRIMARY KEY
- `user_id` VARCHAR(255) NOT NULL
- `search_query` VARCHAR(500) 
- `search_filters` VARCHAR(16777216)  — JSON object of filters applied
- `location_filter` VARCHAR(255) 
- `salary_filter_min` INTEGER 
- `salary_filter_max` INTEGER 
- `work_model_filter` VARCHAR(50) 
- `job_type_filter` VARCHAR(50) 
- `industry_filter` VARCHAR(100) 
- `results_count` INTEGER 
- `search_date` TIMESTAMP 

---

*Generated by documentation workflow. MDX-compatible markdown.*
