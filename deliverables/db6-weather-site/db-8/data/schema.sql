-- Job Market Intelligence Database Schema
-- Compatible with PostgreSQL
-- Production schema for job market intelligence and targeted application system
-- Integrates data from USAJobs.gov, BLS, Department of Labor, and state employment boards

-- User Profiles Table
-- Stores user profiles for job matching and application tracking
CREATE TABLE user_profiles (
    user_id VARCHAR(255) PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    full_name VARCHAR(255),
    location_city VARCHAR(100),
    location_state VARCHAR(2),
    location_country VARCHAR(2) DEFAULT 'US',
    location_latitude NUMERIC(10, 7),
    location_longitude NUMERIC(10, 7),
    current_job_title VARCHAR(255),
    current_company VARCHAR(255),
    years_experience INTEGER,
    education_level VARCHAR(50),
    resume_text VARCHAR(16777216),
    linkedin_url VARCHAR(500),
    github_url VARCHAR(500),
    portfolio_url VARCHAR(500),
    preferred_work_model VARCHAR(50), -- 'remote', 'hybrid', 'onsite'
    salary_expectation_min INTEGER,
    salary_expectation_max INTEGER,
    preferred_locations VARCHAR(16777216), -- JSON array of preferred locations
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    last_active_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    profile_completeness_score NUMERIC(5, 2),
    is_active BOOLEAN DEFAULT TRUE
);

-- Companies Table
-- Stores employer/company information from job postings
CREATE TABLE companies (
    company_id VARCHAR(255) PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    company_name_normalized VARCHAR(255), -- Normalized name for matching
    industry VARCHAR(100),
    company_size VARCHAR(50), -- 'startup', 'small', 'medium', 'large', 'enterprise'
    headquarters_city VARCHAR(100),
    headquarters_state VARCHAR(2),
    headquarters_country VARCHAR(2) DEFAULT 'US',
    website_url VARCHAR(500),
    linkedin_url VARCHAR(500),
    description VARCHAR(16777216),
    founded_year INTEGER,
    employee_count INTEGER,
    revenue_range VARCHAR(50),
    is_federal_agency BOOLEAN DEFAULT FALSE,
    agency_code VARCHAR(50), -- For federal agencies
    data_source VARCHAR(50), -- 'usajobs', 'bls', 'state_board', 'aggregated'
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    company_rating NUMERIC(3, 2), -- Average rating from reviews
    total_reviews INTEGER DEFAULT 0
);

-- Job Postings Table
-- Stores job listings from various .gov sources and aggregated sources
CREATE TABLE job_postings (
    job_id VARCHAR(255) PRIMARY KEY,
    company_id VARCHAR(255) NOT NULL,
    job_title VARCHAR(255) NOT NULL,
    job_title_normalized VARCHAR(255), -- Normalized title for matching
    job_description VARCHAR(16777216),
    job_type VARCHAR(50), -- 'full_time', 'part_time', 'contract', 'temporary', 'internship'
    work_model VARCHAR(50), -- 'remote', 'hybrid', 'onsite'
    location_city VARCHAR(100),
    location_state VARCHAR(2),
    location_country VARCHAR(2) DEFAULT 'US',
    location_latitude NUMERIC(10, 7),
    location_longitude NUMERIC(10, 7),
    salary_min INTEGER,
    salary_max INTEGER,
    salary_currency VARCHAR(3) DEFAULT 'USD',
    salary_type VARCHAR(50), -- 'annual', 'hourly', 'monthly'
    posted_date TIMESTAMP_NTZ NOT NULL,
    expiration_date TIMESTAMP_NTZ,
    application_url VARCHAR(1000),
    application_method VARCHAR(50), -- 'url', 'email', 'ats', 'usajobs'
    is_active BOOLEAN DEFAULT TRUE,
    is_federal_job BOOLEAN DEFAULT FALSE,
    usajobs_id VARCHAR(255), -- USAJobs.gov job ID
    agency_name VARCHAR(255), -- For federal jobs
    pay_plan VARCHAR(50), -- For federal jobs
    grade_level VARCHAR(50), -- For federal jobs
    data_source VARCHAR(50) NOT NULL, -- 'usajobs', 'bls', 'state_board', 'aggregated'
    source_url VARCHAR(1000),
    industry VARCHAR(100), -- Denormalized from companies for query performance
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    view_count INTEGER DEFAULT 0,
    application_count INTEGER DEFAULT 0,
    match_score_avg NUMERIC(5, 2), -- Average match score from recommendations
    job_fingerprint VARCHAR(500), -- Hash for deduplication/matching
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

-- Skills Table
-- Master list of skills/technologies/competencies
CREATE TABLE skills (
    skill_id VARCHAR(255) PRIMARY KEY,
    skill_name VARCHAR(255) NOT NULL UNIQUE,
    skill_category VARCHAR(100), -- 'programming', 'framework', 'tool', 'soft_skill', 'certification'
    skill_type VARCHAR(50), -- 'technical', 'soft', 'certification', 'language'
    parent_skill_id VARCHAR(255), -- For skill hierarchies
    description VARCHAR(16777216),
    popularity_score NUMERIC(10, 2), -- Based on job posting frequency
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (parent_skill_id) REFERENCES skills(skill_id)
);

-- Job Skills Requirements Table
-- Links job postings to required/desired skills
CREATE TABLE job_skills_requirements (
    requirement_id VARCHAR(255) PRIMARY KEY,
    job_id VARCHAR(255) NOT NULL,
    skill_id VARCHAR(255) NOT NULL,
    requirement_type VARCHAR(50), -- 'required', 'preferred', 'nice_to_have'
    importance_score NUMERIC(5, 2), -- 1-10 importance score
    years_experience_required NUMERIC(4, 1),
    extracted_from_description BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (job_id) REFERENCES job_postings(job_id),
    FOREIGN KEY (skill_id) REFERENCES skills(skill_id),
    UNIQUE(job_id, skill_id, requirement_type)
);

-- User Skills Table
-- Links user profiles to their skills and proficiency levels
CREATE TABLE user_skills (
    user_skill_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    skill_id VARCHAR(255) NOT NULL,
    proficiency_level VARCHAR(50), -- 'beginner', 'intermediate', 'advanced', 'expert'
    proficiency_score NUMERIC(5, 2), -- 1-10 proficiency score
    years_experience NUMERIC(4, 1),
    last_used_date DATE,
    verified BOOLEAN DEFAULT FALSE, -- Skills verified through assessments/certifications
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (user_id) REFERENCES user_profiles(user_id),
    FOREIGN KEY (skill_id) REFERENCES skills(skill_id),
    UNIQUE(user_id, skill_id)
);

-- Job Applications Table
-- Tracks user applications to job postings
CREATE TABLE job_applications (
    application_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    job_id VARCHAR(255) NOT NULL,
    application_status VARCHAR(50), -- 'draft', 'submitted', 'under_review', 'interview', 'offer', 'rejected', 'withdrawn'
    application_date TIMESTAMP_NTZ,
    submitted_at TIMESTAMP_NTZ,
    status_updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    cover_letter_text VARCHAR(16777216),
    resume_version VARCHAR(255),
    match_score NUMERIC(5, 2), -- Calculated match score at time of application
    application_method VARCHAR(50), -- 'direct', 'ats', 'email', 'usajobs'
    application_reference_id VARCHAR(255), -- External application ID
    notes VARCHAR(16777216),
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (user_id) REFERENCES user_profiles(user_id),
    FOREIGN KEY (job_id) REFERENCES job_postings(job_id)
);

-- Job Recommendations Table
-- Stores AI-generated job recommendations for users (mirroring jobright.ai)
CREATE TABLE job_recommendations (
    recommendation_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    job_id VARCHAR(255) NOT NULL,
    match_score NUMERIC(5, 2) NOT NULL, -- Overall match score (0-100)
    skill_match_score NUMERIC(5, 2), -- Skill alignment score
    location_match_score NUMERIC(5, 2), -- Location preference match
    salary_match_score NUMERIC(5, 2), -- Salary expectation match
    experience_match_score NUMERIC(5, 2), -- Experience level match
    work_model_match_score NUMERIC(5, 2), -- Work model preference match
    recommendation_reason VARCHAR(16777216), -- Explanation for recommendation
    recommendation_rank INTEGER, -- Rank within user's recommendations
    is_liked BOOLEAN DEFAULT FALSE,
    is_applied BOOLEAN DEFAULT FALSE,
    is_dismissed BOOLEAN DEFAULT FALSE,
    recommendation_date TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    expires_at TIMESTAMP_NTZ, -- Recommendation expiration
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (user_id) REFERENCES user_profiles(user_id),
    FOREIGN KEY (job_id) REFERENCES job_postings(job_id),
    UNIQUE(user_id, job_id, recommendation_date)
);

-- Market Trends Table
-- Aggregated job market trends and statistics
CREATE TABLE market_trends (
    trend_id VARCHAR(255) PRIMARY KEY,
    trend_date DATE NOT NULL,
    geographic_scope VARCHAR(50), -- 'national', 'state', 'city', 'metro'
    location_state VARCHAR(2),
    location_city VARCHAR(100),
    location_metro VARCHAR(100),
    industry VARCHAR(100),
    job_category VARCHAR(100),
    total_job_postings INTEGER,
    new_job_postings INTEGER, -- New postings in period
    active_job_seekers INTEGER, -- Estimated from application data
    average_salary_min INTEGER,
    average_salary_max INTEGER,
    median_salary INTEGER,
    top_skills VARCHAR(16777216), -- JSON array of top skills
    skill_demand_trend VARCHAR(16777216), -- JSON object of skill demand changes
    competition_index NUMERIC(5, 2), -- Applications per job ratio
    growth_rate NUMERIC(10, 4), -- Percentage growth in postings
    data_source VARCHAR(50), -- 'bls', 'aggregated', 'usajobs'
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    UNIQUE(trend_date, geographic_scope, location_state, location_city, industry, job_category)
);

-- Job Market Analytics Table
-- Detailed analytics for job market intelligence
CREATE TABLE job_market_analytics (
    analytics_id VARCHAR(255) PRIMARY KEY,
    analysis_date DATE NOT NULL,
    analysis_type VARCHAR(50), -- 'daily', 'weekly', 'monthly', 'quarterly'
    geographic_scope VARCHAR(50),
    location_state VARCHAR(2),
    location_city VARCHAR(100),
    industry VARCHAR(100),
    total_companies INTEGER,
    total_active_jobs INTEGER,
    remote_job_percentage NUMERIC(5, 2),
    hybrid_job_percentage NUMERIC(5, 2),
    average_time_to_fill_days INTEGER,
    average_applications_per_job NUMERIC(10, 2),
    top_employers VARCHAR(16777216), -- JSON array
    emerging_skills VARCHAR(16777216), -- JSON array of trending skills
    declining_skills VARCHAR(16777216), -- JSON array of declining skills
    salary_trends VARCHAR(16777216), -- JSON object with salary trend data
    job_type_distribution VARCHAR(16777216), -- JSON object
    work_model_distribution VARCHAR(16777216), -- JSON object
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Data Source Metadata Table
-- Tracks data sources and extraction metadata
CREATE TABLE data_source_metadata (
    metadata_id VARCHAR(255) PRIMARY KEY,
    source_name VARCHAR(100) NOT NULL, -- 'usajobs', 'bls', 'state_board'
    source_type VARCHAR(50), -- 'api', 'scraper', 'manual', 'aggregated'
    extraction_date TIMESTAMP_NTZ NOT NULL,
    extraction_method VARCHAR(100),
    records_extracted INTEGER,
    records_new INTEGER,
    records_updated INTEGER,
    records_failed INTEGER,
    extraction_status VARCHAR(50), -- 'success', 'partial', 'failed'
    error_message VARCHAR(16777216),
    api_endpoint VARCHAR(1000),
    api_response_code INTEGER,
    extraction_duration_seconds INTEGER,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- User Job Search History Table
-- Tracks user search behavior for recommendation improvement
CREATE TABLE user_job_search_history (
    search_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    search_query VARCHAR(500),
    search_filters VARCHAR(16777216), -- JSON object of filters applied
    location_filter VARCHAR(255),
    salary_filter_min INTEGER,
    salary_filter_max INTEGER,
    work_model_filter VARCHAR(50),
    job_type_filter VARCHAR(50),
    industry_filter VARCHAR(100),
    results_count INTEGER,
    search_date TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (user_id) REFERENCES user_profiles(user_id)
);

-- Indexes for performance optimization
CREATE INDEX idx_job_postings_company_id ON job_postings(company_id);
CREATE INDEX idx_job_postings_posted_date ON job_postings(posted_date);
CREATE INDEX idx_job_postings_location_state ON job_postings(location_state);
CREATE INDEX idx_job_postings_location_city ON job_postings(location_city);
CREATE INDEX idx_job_postings_work_model ON job_postings(work_model);
CREATE INDEX idx_job_postings_job_type ON job_postings(job_type);
CREATE INDEX idx_job_postings_is_active ON job_postings(is_active);
CREATE INDEX idx_job_postings_data_source ON job_postings(data_source);
CREATE INDEX idx_job_postings_posted_date_active ON job_postings(posted_date, is_active);

CREATE INDEX idx_job_skills_requirements_job_id ON job_skills_requirements(job_id);
CREATE INDEX idx_job_skills_requirements_skill_id ON job_skills_requirements(skill_id);
CREATE INDEX idx_job_skills_requirements_type ON job_skills_requirements(requirement_type);

CREATE INDEX idx_user_skills_user_id ON user_skills(user_id);
CREATE INDEX idx_user_skills_skill_id ON user_skills(skill_id);

CREATE INDEX idx_job_applications_user_id ON job_applications(user_id);
CREATE INDEX idx_job_applications_job_id ON job_applications(job_id);
CREATE INDEX idx_job_applications_status ON job_applications(application_status);
CREATE INDEX idx_job_applications_submitted_at ON job_applications(submitted_at);

CREATE INDEX idx_job_recommendations_user_id ON job_recommendations(user_id);
CREATE INDEX idx_job_recommendations_job_id ON job_recommendations(job_id);
CREATE INDEX idx_job_recommendations_match_score ON job_recommendations(match_score DESC);
CREATE INDEX idx_job_recommendations_date ON job_recommendations(recommendation_date);

CREATE INDEX idx_market_trends_date ON market_trends(trend_date);
CREATE INDEX idx_market_trends_location ON market_trends(location_state, location_city);
CREATE INDEX idx_market_trends_industry ON market_trends(industry);

CREATE INDEX idx_user_profiles_location ON user_profiles(location_state, location_city);
CREATE INDEX idx_user_profiles_email ON user_profiles(email);
CREATE INDEX idx_user_profiles_is_active ON user_profiles(is_active);

CREATE INDEX idx_companies_industry ON companies(industry);
CREATE INDEX idx_companies_name_normalized ON companies(company_name_normalized);

-- Migration: Add industry to job_postings if missing (for existing databases)
ALTER TABLE job_postings ADD COLUMN IF NOT EXISTS industry VARCHAR(100);
