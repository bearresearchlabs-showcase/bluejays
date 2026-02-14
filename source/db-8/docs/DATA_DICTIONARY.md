# Data Dictionary - db-8

**Database:** Job Market Intelligence Database  
**Purpose:** Comprehensive column-level documentation for all tables

## Table of Contents

1. [User Management](#user-management)
2. [Job Postings](#job-postings)
3. [Skills](#skills)
4. [Applications](#applications)
5. [Market Intelligence](#market-intelligence)
6. [Data Management](#data-management)

---

## User Management

### user_profiles

Stores user profiles for job matching and application tracking.

| Column Name | Data Type | Constraints | Description | Business Context |
|------------|-----------|-------------|-------------|------------------|
| `user_id` | VARCHAR(255) | PRIMARY KEY | Unique user identifier | Used as foreign key in related tables |
| `email` | VARCHAR(255) | NOT NULL, UNIQUE | User email address | Primary contact method, used for authentication |
| `full_name` | VARCHAR(255) | NULL | User's full name | Display name for applications and recommendations |
| `location_city` | VARCHAR(100) | NULL | City where user is located | Used for location-based job matching |
| `location_state` | VARCHAR(2) | NULL | State code (2-letter) | Geographic filtering and matching |
| `location_country` | VARCHAR(2) | DEFAULT 'US' | Country code (ISO 3166-1 alpha-2) | Defaults to US, supports international users |
| `location_latitude` | NUMERIC(10, 7) | NULL | Geographic latitude | Enables distance-based job matching |
| `location_longitude` | NUMERIC(10, 7) | NULL | Geographic longitude | Enables distance-based job matching |
| `current_job_title` | VARCHAR(255) | NULL | User's current job title | Used for experience matching and career progression analysis |
| `current_company` | VARCHAR(255) | NULL | User's current employer | Company matching and transition analysis |
| `years_experience` | INTEGER | NULL | Years of professional experience | Experience level matching for job recommendations |
| `education_level` | VARCHAR(50) | NULL | Highest education level | Education requirement matching (e.g., 'Bachelor's Degree', 'Master's Degree', 'PhD') |
| `resume_text` | VARCHAR(16777216) | NULL | Full resume content | Text analysis for skill extraction and matching |
| `linkedin_url` | VARCHAR(500) | NULL | LinkedIn profile URL | External profile verification and networking |
| `github_url` | VARCHAR(500) | NULL | GitHub profile URL | Technical portfolio verification |
| `portfolio_url` | VARCHAR(500) | NULL | Portfolio website URL | Professional portfolio showcase |
| `preferred_work_model` | VARCHAR(50) | NULL | Work model preference | 'remote', 'hybrid', 'onsite' - used for job filtering |
| `salary_expectation_min` | INTEGER | NULL | Minimum salary expectation | Salary range matching for job recommendations |
| `salary_expectation_max` | INTEGER | NULL | Maximum salary expectation | Salary range matching for job recommendations |
| `preferred_locations` | VARCHAR(16777216) | NULL | JSON array of preferred locations | Multiple location preferences for job matching |
| `created_at` | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Profile creation timestamp | Account creation tracking |
| `updated_at` | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Profile last update timestamp | Profile modification tracking |
| `last_active_at` | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Last active timestamp | User engagement tracking |
| `profile_completeness_score` | NUMERIC(5, 2) | NULL | Profile completeness percentage (0-100) | Higher scores enable better job matching |
| `is_active` | BOOLEAN | DEFAULT TRUE | Active profile flag | Inactive profiles excluded from matching |

### user_skills

Links user profiles to their skills and proficiency levels.

| Column Name | Data Type | Constraints | Description | Business Context |
|------------|-----------|-------------|-------------|------------------|
| `user_skill_id` | VARCHAR(255) | PRIMARY KEY | Unique user skill identifier | Primary key for user-skill relationships |
| `user_id` | VARCHAR(255) | NOT NULL, FK → user_profiles | User reference | Links to user profile |
| `skill_id` | VARCHAR(255) | NOT NULL, FK → skills | Skill reference | Links to skills master table |
| `proficiency_level` | VARCHAR(50) | NULL | Proficiency level | 'beginner', 'intermediate', 'advanced', 'expert' |
| `proficiency_score` | NUMERIC(5, 2) | NULL | Proficiency score (1-10) | Quantitative proficiency measure for matching |
| `years_experience` | NUMERIC(4, 1) | NULL | Years of experience with skill | Experience duration matching |
| `last_used_date` | DATE | NULL | Last date skill was used | Recency factor for skill relevance |
| `verified` | BOOLEAN | DEFAULT FALSE | Skills verified through assessments/certifications | Verified skills carry more weight in matching |
| `created_at` | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Record creation timestamp | Skill addition tracking |
| `updated_at` | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Record update timestamp | Skill update tracking |
| **UNIQUE** | (user_id, skill_id) | UNIQUE | One skill per user | Prevents duplicate skill entries |

### user_job_search_history

Tracks user search behavior for recommendation improvement.

| Column Name | Data Type | Constraints | Description | Business Context |
|------------|-----------|-------------|-------------|------------------|
| `search_id` | VARCHAR(255) | PRIMARY KEY | Unique search identifier | Primary key for search history |
| `user_id` | VARCHAR(255) | NOT NULL, FK → user_profiles | User reference | Links to user profile |
| `search_query` | VARCHAR(500) | NULL | Search query text | User-entered search terms |
| `search_filters` | VARCHAR(16777216) | NULL | JSON object of filters applied | Structured filter data for analysis |
| `location_filter` | VARCHAR(255) | NULL | Location filter value | Geographic search preference |
| `salary_filter_min` | INTEGER | NULL | Minimum salary filter | Salary range search preference |
| `salary_filter_max` | INTEGER | NULL | Maximum salary filter | Salary range search preference |
| `work_model_filter` | VARCHAR(50) | NULL | Work model filter | 'remote', 'hybrid', 'onsite' preference |
| `job_type_filter` | VARCHAR(50) | NULL | Job type filter | 'full_time', 'part_time', 'contract', etc. |
| `industry_filter` | VARCHAR(100) | NULL | Industry filter | Industry sector preference |
| `results_count` | INTEGER | NULL | Number of results returned | Search result count for analytics |
| `search_date` | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Search timestamp | Search timing for pattern analysis |

---

## Job Postings

### companies

Stores employer/company information from job postings.

| Column Name | Data Type | Constraints | Description | Business Context |
|------------|-----------|-------------|-------------|------------------|
| `company_id` | VARCHAR(255) | PRIMARY KEY | Unique company identifier | Primary key for companies |
| `company_name` | VARCHAR(255) | NOT NULL, UNIQUE | Company name | Display name, must be unique |
| `company_name_normalized` | VARCHAR(255) | NULL | Normalized name for matching | Lowercase, trimmed name for cross-source matching |
| `industry` | VARCHAR(100) | NULL | Industry sector | Industry filtering and analytics |
| `company_size` | VARCHAR(50) | NULL | Company size category | 'startup', 'small', 'medium', 'large', 'enterprise' |
| `headquarters_city` | VARCHAR(100) | NULL | HQ city | Company location for geographic analysis |
| `headquarters_state` | VARCHAR(2) | NULL | HQ state code | State-level geographic analysis |
| `headquarters_country` | VARCHAR(2) | DEFAULT 'US' | HQ country code | Defaults to US, supports international companies |
| `website_url` | VARCHAR(500) | NULL | Company website URL | External company information |
| `linkedin_url` | VARCHAR(500) | NULL | LinkedIn company page URL | Social media presence |
| `description` | VARCHAR(16777216) | NULL | Company description | Company overview and culture |
| `founded_year` | INTEGER | NULL | Year company was founded | Company age analysis |
| `employee_count` | INTEGER | NULL | Number of employees | Company size metric |
| `revenue_range` | VARCHAR(50) | NULL | Revenue range | Financial size indicator (e.g., '$1B-$10B') |
| `is_federal_agency` | BOOLEAN | DEFAULT FALSE | Federal agency flag | TRUE for federal agencies from USAJobs.gov |
| `agency_code` | VARCHAR(50) | NULL | Agency code for federal agencies | Federal agency identifier (e.g., 'DOD', 'FBI', 'NSA') |
| `data_source` | VARCHAR(50) | NULL | Data source identifier | 'usajobs', 'bls', 'state_board', 'aggregated' |
| `created_at` | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Record creation timestamp | Company addition tracking |
| `updated_at` | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Record update timestamp | Company update tracking |
| `company_rating` | NUMERIC(3, 2) | NULL | Average company rating | User/employee rating (e.g., 1.00-5.00) |
| `total_reviews` | INTEGER | DEFAULT 0 | Total review count | Number of ratings/reviews |

### job_postings

Stores job listings from various .gov sources and aggregated sources.

| Column Name | Data Type | Constraints | Description | Business Context |
|------------|-----------|-------------|-------------|------------------|
| `job_id` | VARCHAR(255) | PRIMARY KEY | Unique job identifier | Primary key for job postings |
| `company_id` | VARCHAR(255) | NOT NULL, FK → companies | Company reference | Links to company posting the job |
| `job_title` | VARCHAR(255) | NOT NULL | Job title | Display title for job listings |
| `job_title_normalized` | VARCHAR(255) | NULL | Normalized title for matching | Lowercase, trimmed title for cross-source matching |
| `job_description` | VARCHAR(16777216) | NULL | Full job description | May contain HTML formatting from source |
| `job_type` | VARCHAR(50) | NULL | Job type | 'full_time', 'part_time', 'contract', 'temporary', 'internship' |
| `work_model` | VARCHAR(50) | NULL | Work model | 'remote', 'hybrid', 'onsite' - critical for user matching |
| `location_city` | VARCHAR(100) | NULL | Job location city | Geographic matching and filtering |
| `location_state` | VARCHAR(2) | NULL | Job location state | State-level geographic filtering |
| `location_country` | VARCHAR(2) | DEFAULT 'US' | Job location country | Defaults to US, supports international jobs |
| `location_latitude` | NUMERIC(10, 7) | NULL | Geographic latitude | Distance-based matching |
| `location_longitude` | NUMERIC(10, 7) | NULL | Geographic longitude | Distance-based matching |
| `salary_min` | INTEGER | NULL | Minimum salary | Salary range matching |
| `salary_max` | INTEGER | NULL | Maximum salary | Salary range matching |
| `salary_currency` | VARCHAR(3) | DEFAULT 'USD' | Currency code (ISO 4217) | Defaults to USD, supports international salaries |
| `salary_type` | VARCHAR(50) | NULL | Salary type | 'annual', 'hourly', 'monthly' - affects matching calculations |
| `posted_date` | TIMESTAMP_NTZ | NOT NULL | Job posting date | Used for "last 2 weeks" filtering |
| `expiration_date` | TIMESTAMP_NTZ | NULL | Job expiration date | Job closing date |
| `application_url` | VARCHAR(1000) | NULL | Application URL | Direct link to application |
| `application_method` | VARCHAR(50) | NULL | Application method | 'url', 'email', 'ats', 'usajobs' |
| `is_active` | BOOLEAN | DEFAULT TRUE | Active job flag | Inactive jobs excluded from matching |
| `is_federal_job` | BOOLEAN | DEFAULT FALSE | Federal job flag | TRUE for USAJobs.gov federal positions |
| `usajobs_id` | VARCHAR(255) | NULL | USAJobs.gov job ID | External ID for federal jobs |
| `agency_name` | VARCHAR(255) | NULL | Agency name (federal jobs) | Federal agency name |
| `pay_plan` | VARCHAR(50) | NULL | Pay plan (federal jobs) | Federal pay plan (e.g., 'GS', 'GG') |
| `grade_level` | VARCHAR(50) | NULL | Grade level (federal jobs) | Federal grade level (e.g., 'GS-13') |
| `data_source` | VARCHAR(50) | NOT NULL | Data source identifier | 'usajobs', 'bls', 'state_board', 'aggregated' |
| `source_url` | VARCHAR(1000) | NULL | Source URL | Original job posting URL |
| `created_at` | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Record creation timestamp | Job addition tracking |
| `updated_at` | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Record update timestamp | Job update tracking |
| `view_count` | INTEGER | DEFAULT 0 | Number of views | Job popularity metric |
| `application_count` | INTEGER | DEFAULT 0 | Number of applications | Job competition metric |
| `match_score_avg` | NUMERIC(5, 2) | NULL | Average match score | Average recommendation match score |

### job_skills_requirements

Links job postings to required/desired skills.

| Column Name | Data Type | Constraints | Description | Business Context |
|------------|-----------|-------------|-------------|------------------|
| `requirement_id` | VARCHAR(255) | PRIMARY KEY | Unique requirement identifier | Primary key for job-skill relationships |
| `job_id` | VARCHAR(255) | NOT NULL, FK → job_postings | Job reference | Links to job posting |
| `skill_id` | VARCHAR(255) | NOT NULL, FK → skills | Skill reference | Links to skills master table |
| `requirement_type` | VARCHAR(50) | NULL | Requirement type | 'required', 'preferred', 'nice_to_have' - affects matching weight |
| `importance_score` | NUMERIC(5, 2) | NULL | Importance score (1-10) | Quantitative importance for match calculations |
| `years_experience_required` | NUMERIC(4, 1) | NULL | Years of experience required | Experience requirement matching |
| `extracted_from_description` | BOOLEAN | DEFAULT TRUE | Whether skill was extracted from job description | TRUE if NLP-extracted, FALSE if manually added |
| `created_at` | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Record creation timestamp | Requirement addition tracking |
| **UNIQUE** | (job_id, skill_id, requirement_type) | UNIQUE | One requirement per job-skill-type | Prevents duplicate requirements |

---

## Skills

### skills

Master list of skills/technologies/competencies.

| Column Name | Data Type | Constraints | Description | Business Context |
|------------|-----------|-------------|-------------|------------------|
| `skill_id` | VARCHAR(255) | PRIMARY KEY | Unique skill identifier | Primary key for skills |
| `skill_name` | VARCHAR(255) | NOT NULL, UNIQUE | Skill name | Display name, must be unique (e.g., 'Python', 'React') |
| `skill_category` | VARCHAR(100) | NULL | Skill category | 'programming', 'framework', 'tool', 'soft_skill', 'certification' |
| `skill_type` | VARCHAR(50) | NULL | Skill type | 'technical', 'soft', 'certification', 'language' |
| `parent_skill_id` | VARCHAR(255) | NULL, FK → skills | Parent skill for hierarchies | Self-referential FK for skill hierarchies (e.g., React → JavaScript) |
| `description` | VARCHAR(16777216) | NULL | Skill description | Detailed skill description |
| `popularity_score` | NUMERIC(10, 2) | NULL | Popularity based on job posting frequency | Higher scores indicate more in-demand skills |
| `created_at` | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Record creation timestamp | Skill addition tracking |

---

## Applications

### job_applications

Tracks user applications to job postings.

| Column Name | Data Type | Constraints | Description | Business Context |
|------------|-----------|-------------|-------------|------------------|
| `application_id` | VARCHAR(255) | PRIMARY KEY | Unique application identifier | Primary key for applications |
| `user_id` | VARCHAR(255) | NOT NULL, FK → user_profiles | User reference | Links to user profile |
| `job_id` | VARCHAR(255) | NOT NULL, FK → job_postings | Job reference | Links to job posting |
| `application_status` | VARCHAR(50) | NULL | Application status | 'draft', 'submitted', 'under_review', 'interview', 'offer', 'rejected', 'withdrawn' |
| `application_date` | TIMESTAMP_NTZ | NULL | Application date | When user initiated application |
| `submitted_at` | TIMESTAMP_NTZ | NULL | Submission timestamp | When application was submitted |
| `status_updated_at` | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Last status update timestamp | Tracks status change timing |
| `cover_letter_text` | VARCHAR(16777216) | NULL | Cover letter content | User's cover letter text |
| `resume_version` | VARCHAR(255) | NULL | Resume version used | Resume file identifier |
| `match_score` | NUMERIC(5, 2) | NULL | Calculated match score at time of application | Match score snapshot for analytics |
| `application_method` | VARCHAR(50) | NULL | Application method | 'direct', 'ats', 'email', 'usajobs' |
| `application_reference_id` | VARCHAR(255) | NULL | External application ID | External system application ID |
| `notes` | VARCHAR(16777216) | NULL | Application notes | User or system notes |
| `created_at` | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Record creation timestamp | Application creation tracking |
| `updated_at` | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Record update timestamp | Application update tracking |

### job_recommendations

Stores AI-generated job recommendations for users (mirroring jobright.ai).

| Column Name | Data Type | Constraints | Description | Business Context |
|------------|-----------|-------------|-------------|------------------|
| `recommendation_id` | VARCHAR(255) | PRIMARY KEY | Unique recommendation identifier | Primary key for recommendations |
| `user_id` | VARCHAR(255) | NOT NULL, FK → user_profiles | User reference | Links to user profile |
| `job_id` | VARCHAR(255) | NOT NULL, FK → job_postings | Job reference | Links to job posting |
| `match_score` | NUMERIC(5, 2) | NOT NULL | Overall match score (0-100) | Primary ranking metric for recommendations |
| `skill_match_score` | NUMERIC(5, 2) | NULL | Skill alignment score | Component score for skill matching |
| `location_match_score` | NUMERIC(5, 2) | NULL | Location preference match | Component score for location matching |
| `salary_match_score` | NUMERIC(5, 2) | NULL | Salary expectation match | Component score for salary matching |
| `experience_match_score` | NUMERIC(5, 2) | NULL | Experience level match | Component score for experience matching |
| `work_model_match_score` | NUMERIC(5, 2) | NULL | Work model preference match | Component score for work model matching |
| `recommendation_reason` | VARCHAR(16777216) | NULL | Explanation for recommendation | Human-readable explanation (e.g., "Strong skill match") |
| `recommendation_rank` | INTEGER | NULL | Rank within user's recommendations | Ranking order (1 = best match) |
| `is_liked` | BOOLEAN | DEFAULT FALSE | User liked this recommendation | User feedback for algorithm improvement |
| `is_applied` | BOOLEAN | DEFAULT FALSE | User applied to this job | Conversion tracking |
| `is_dismissed` | BOOLEAN | DEFAULT FALSE | User dismissed this recommendation | Negative feedback for algorithm improvement |
| `recommendation_date` | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Recommendation date | When recommendation was generated |
| `expires_at` | TIMESTAMP_NTZ | NULL | Recommendation expiration | Recommendation validity period |
| `created_at` | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Record creation timestamp | Recommendation creation tracking |
| **UNIQUE** | (user_id, job_id, recommendation_date) | UNIQUE | One recommendation per user-job-date | Prevents duplicate recommendations |

---

## Market Intelligence

### market_trends

Aggregated job market trends and statistics.

| Column Name | Data Type | Constraints | Description | Business Context |
|------------|-----------|-------------|-------------|------------------|
| `trend_id` | VARCHAR(255) | PRIMARY KEY | Unique trend identifier | Primary key for market trends |
| `trend_date` | DATE | NOT NULL | Trend date | Date of trend measurement |
| `geographic_scope` | VARCHAR(50) | NULL | Geographic scope | 'national', 'state', 'city', 'metro' |
| `location_state` | VARCHAR(2) | NULL | State code | State-level geographic filtering |
| `location_city` | VARCHAR(100) | NULL | City name | City-level geographic filtering |
| `location_metro` | VARCHAR(100) | NULL | Metropolitan area | Metro area identification |
| `industry` | VARCHAR(100) | NULL | Industry sector | Industry filtering |
| `job_category` | VARCHAR(100) | NULL | Job category | Job category filtering |
| `total_job_postings` | INTEGER | NULL | Total job postings | Total active postings |
| `new_job_postings` | INTEGER | NULL | New postings in period | New postings in measurement period |
| `active_job_seekers` | INTEGER | NULL | Estimated active job seekers | Estimated from application data |
| `average_salary_min` | INTEGER | NULL | Average minimum salary | Average salary range minimum |
| `average_salary_max` | INTEGER | NULL | Average maximum salary | Average salary range maximum |
| `median_salary` | INTEGER | NULL | Median salary | Median salary for category |
| `top_skills` | VARCHAR(16777216) | NULL | JSON array of top skills | Most in-demand skills (JSON format) |
| `skill_demand_trend` | VARCHAR(16777216) | NULL | JSON object of skill demand changes | Skill demand change percentages (JSON format) |
| `competition_index` | NUMERIC(5, 2) | NULL | Applications per job ratio | Higher values indicate more competition |
| `growth_rate` | NUMERIC(10, 4) | NULL | Percentage growth in postings | Growth rate percentage |
| `data_source` | VARCHAR(50) | NULL | Data source identifier | 'bls', 'aggregated', 'usajobs' |
| `created_at` | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Record creation timestamp | Trend creation tracking |
| **UNIQUE** | (trend_date, geographic_scope, location_state, location_city, industry, job_category) | UNIQUE | One trend per date-scope-location-industry-category | Prevents duplicate trends |

### job_market_analytics

Detailed analytics for job market intelligence.

| Column Name | Data Type | Constraints | Description | Business Context |
|------------|-----------|-------------|-------------|------------------|
| `analytics_id` | VARCHAR(255) | PRIMARY KEY | Unique analytics identifier | Primary key for analytics |
| `analysis_date` | DATE | NOT NULL | Analysis date | Date of analysis |
| `analysis_type` | VARCHAR(50) | NULL | Analysis type | 'daily', 'weekly', 'monthly', 'quarterly' |
| `geographic_scope` | VARCHAR(50) | NULL | Geographic scope | Geographic scope of analysis |
| `location_state` | VARCHAR(2) | NULL | State code | State-level geographic filtering |
| `location_city` | VARCHAR(100) | NULL | City name | City-level geographic filtering |
| `industry` | VARCHAR(100) | NULL | Industry sector | Industry filtering |
| `total_companies` | INTEGER | NULL | Total companies | Number of companies in scope |
| `total_active_jobs` | INTEGER | NULL | Total active jobs | Number of active job postings |
| `remote_job_percentage` | NUMERIC(5, 2) | NULL | Percentage of remote jobs | Remote work trend metric |
| `hybrid_job_percentage` | NUMERIC(5, 2) | NULL | Percentage of hybrid jobs | Hybrid work trend metric |
| `average_time_to_fill_days` | INTEGER | NULL | Average time to fill positions | Hiring speed metric |
| `average_applications_per_job` | NUMERIC(10, 2) | NULL | Average applications per job | Competition metric |
| `top_employers` | VARCHAR(16777216) | NULL | JSON array of top employers | Most active employers (JSON format) |
| `emerging_skills` | VARCHAR(16777216) | NULL | JSON array of trending skills | Skills with increasing demand (JSON format) |
| `declining_skills` | VARCHAR(16777216) | NULL | JSON array of declining skills | Skills with decreasing demand (JSON format) |
| `salary_trends` | VARCHAR(16777216) | NULL | JSON object with salary trend data | Salary trend analysis (JSON format) |
| `job_type_distribution` | VARCHAR(16777216) | NULL | JSON object with job type distribution | Distribution of job types (JSON format) |
| `work_model_distribution` | VARCHAR(16777216) | NULL | JSON object with work model distribution | Distribution of work models (JSON format) |
| `created_at` | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Record creation timestamp | Analytics creation tracking |

---

## Data Management

### data_source_metadata

Tracks data sources and extraction metadata.

| Column Name | Data Type | Constraints | Description | Business Context |
|------------|-----------|-------------|-------------|------------------|
| `metadata_id` | VARCHAR(255) | PRIMARY KEY | Unique metadata identifier | Primary key for metadata records |
| `source_name` | VARCHAR(100) | NOT NULL | Source name | 'usajobs', 'bls', 'state_board' |
| `source_type` | VARCHAR(50) | NULL | Source type | 'api', 'scraper', 'manual', 'aggregated' |
| `extraction_date` | TIMESTAMP_NTZ | NOT NULL | Extraction date | When data was extracted |
| `extraction_method` | VARCHAR(100) | NULL | Extraction method description | Method used (e.g., 'REST API', 'Web Scraping') |
| `records_extracted` | INTEGER | NULL | Total records extracted | Total records processed |
| `records_new` | INTEGER | NULL | New records | New records added |
| `records_updated` | INTEGER | NULL | Updated records | Existing records updated |
| `records_failed` | INTEGER | NULL | Failed records | Records that failed processing |
| `extraction_status` | VARCHAR(50) | NULL | Extraction status | 'success', 'partial', 'failed' |
| `error_message` | VARCHAR(16777216) | NULL | Error message if failed | Error details for failed extractions |
| `api_endpoint` | VARCHAR(1000) | NULL | API endpoint used | API endpoint URL |
| `api_response_code` | INTEGER | NULL | API response code | HTTP response code |
| `extraction_duration_seconds` | INTEGER | NULL | Extraction duration | Processing time in seconds |
| `created_at` | TIMESTAMP_NTZ | DEFAULT CURRENT_TIMESTAMP() | Record creation timestamp | Metadata creation tracking |

---

## Data Types Reference

### VARCHAR
Variable-length character string. Maximum length specified in parentheses.

### INTEGER
Whole number (32-bit).

### NUMERIC(precision, scale)
Exact numeric with specified precision and scale. Example: NUMERIC(5, 2) stores values like 123.45.

### BOOLEAN
True/false value.

### TIMESTAMP_NTZ
Timestamp without timezone. Compatible across PostgreSQL.

### DATE
Date value (year, month, day).

### JSON Fields
Several fields store JSON data:
- `preferred_locations` (user_profiles): JSON array of location strings
- `top_skills` (market_trends): JSON array of skill objects
- `skill_demand_trend` (market_trends): JSON object with skill demand percentages
- `top_employers` (job_market_analytics): JSON array of employer objects
- `emerging_skills`, `declining_skills` (job_market_analytics): JSON arrays of skill objects
- `salary_trends`, `job_type_distribution`, `work_model_distribution` (job_market_analytics): JSON objects
- `search_filters` (user_job_search_history): JSON object of filter parameters

---

## Indexes

Indexes are created on:
- Foreign key columns for join performance
- Location columns (state, city) for geographic queries
- Date columns (posted_date, trend_date) for time-based queries
- Status columns (is_active, application_status) for filtering
- Match score columns for recommendation ranking
- Normalized name columns for text matching

See `schema.sql` for complete index definitions.

---

**Last Updated:** 2026-02-04
