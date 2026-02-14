-- Job Market Database Schema - Optimized for 30GB Scale
-- Compatible with PostgreSQL, Databricks, and Snowflake
-- Production schema for job market and targeted application system
-- Includes partitioning, additional indexes, and optimization for large-scale data

-- ============================================================================
-- BASE TABLES (Same as original schema.sql)
-- ============================================================================

-- User Profiles Table
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
    preferred_work_model VARCHAR(50),
    salary_expectation_min INTEGER,
    salary_expectation_max INTEGER,
    preferred_locations VARCHAR(16777216),
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    last_active_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    profile_completeness_score NUMERIC(5, 2),
    is_active BOOLEAN DEFAULT TRUE
);

-- Companies Table
CREATE TABLE companies (
    company_id VARCHAR(255) PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    company_name_normalized VARCHAR(255),
    industry VARCHAR(100),
    company_size VARCHAR(50),
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
    agency_code VARCHAR(50),
    data_source VARCHAR(50),
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    company_rating NUMERIC(3, 2),
    total_reviews INTEGER DEFAULT 0
);

-- Job Postings Table (Will be partitioned)
CREATE TABLE job_postings (
    job_id VARCHAR(255),
    company_id VARCHAR(255) NOT NULL,
    job_title VARCHAR(255) NOT NULL,
    job_title_normalized VARCHAR(255),
    job_description VARCHAR(16777216),
    job_type VARCHAR(50),
    work_model VARCHAR(50),
    location_city VARCHAR(100),
    location_state VARCHAR(2),
    location_country VARCHAR(2) DEFAULT 'US',
    location_latitude NUMERIC(10, 7),
    location_longitude NUMERIC(10, 7),
    salary_min INTEGER,
    salary_max INTEGER,
    salary_currency VARCHAR(3) DEFAULT 'USD',
    salary_type VARCHAR(50),
    posted_date TIMESTAMP_NTZ NOT NULL,
    expiration_date TIMESTAMP_NTZ,
    application_url VARCHAR(1000),
    application_method VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    is_federal_job BOOLEAN DEFAULT FALSE,
    usajobs_id VARCHAR(255),
    agency_name VARCHAR(255),
    pay_plan VARCHAR(50),
    grade_level VARCHAR(50),
    data_source VARCHAR(50) NOT NULL,
    source_url VARCHAR(1000),
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    view_count INTEGER DEFAULT 0,
    application_count INTEGER DEFAULT 0,
    match_score_avg NUMERIC(5, 2),
    FOREIGN KEY (company_id) REFERENCES companies(company_id),
    PRIMARY KEY (job_id, posted_date)
);

-- Skills Table
CREATE TABLE skills (
    skill_id VARCHAR(255) PRIMARY KEY,
    skill_name VARCHAR(255) NOT NULL UNIQUE,
    skill_category VARCHAR(100),
    skill_type VARCHAR(50),
    parent_skill_id VARCHAR(255),
    description VARCHAR(16777216),
    popularity_score NUMERIC(10, 2),
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (parent_skill_id) REFERENCES skills(skill_id)
);

-- Job Skills Requirements Table
CREATE TABLE job_skills_requirements (
    requirement_id VARCHAR(255) PRIMARY KEY,
    job_id VARCHAR(255) NOT NULL,
    skill_id VARCHAR(255) NOT NULL,
    requirement_type VARCHAR(50),
    importance_score NUMERIC(5, 2),
    years_experience_required NUMERIC(4, 1),
    extracted_from_description BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (skill_id) REFERENCES skills(skill_id),
    UNIQUE(job_id, skill_id, requirement_type)
);

-- User Skills Table
CREATE TABLE user_skills (
    user_skill_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    skill_id VARCHAR(255) NOT NULL,
    proficiency_level VARCHAR(50),
    proficiency_score NUMERIC(5, 2),
    years_experience NUMERIC(4, 1),
    last_used_date DATE,
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (user_id) REFERENCES user_profiles(user_id),
    FOREIGN KEY (skill_id) REFERENCES skills(skill_id),
    UNIQUE(user_id, skill_id)
);

-- Job Applications Table (Will be partitioned)
CREATE TABLE job_applications (
    application_id VARCHAR(255),
    user_id VARCHAR(255) NOT NULL,
    job_id VARCHAR(255) NOT NULL,
    application_status VARCHAR(50),
    application_date TIMESTAMP_NTZ,
    submitted_at TIMESTAMP_NTZ,
    status_updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    cover_letter_text VARCHAR(16777216),
    resume_version VARCHAR(255),
    match_score NUMERIC(5, 2),
    application_method VARCHAR(50),
    application_reference_id VARCHAR(255),
    notes VARCHAR(16777216),
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (user_id) REFERENCES user_profiles(user_id),
    PRIMARY KEY (application_id, submitted_at)
);

-- Job Recommendations Table (Will be partitioned)
CREATE TABLE job_recommendations (
    recommendation_id VARCHAR(255),
    user_id VARCHAR(255) NOT NULL,
    job_id VARCHAR(255) NOT NULL,
    match_score NUMERIC(5, 2) NOT NULL,
    skill_match_score NUMERIC(5, 2),
    location_match_score NUMERIC(5, 2),
    salary_match_score NUMERIC(5, 2),
    experience_match_score NUMERIC(5, 2),
    work_model_match_score NUMERIC(5, 2),
    recommendation_reason VARCHAR(16777216),
    recommendation_rank INTEGER,
    is_liked BOOLEAN DEFAULT FALSE,
    is_applied BOOLEAN DEFAULT FALSE,
    is_dismissed BOOLEAN DEFAULT FALSE,
    recommendation_date TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    expires_at TIMESTAMP_NTZ,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (user_id) REFERENCES user_profiles(user_id),
    PRIMARY KEY (recommendation_id, recommendation_date)
);

-- Market Trends Table (Will be partitioned)
CREATE TABLE market_trends (
    trend_id VARCHAR(255),
    trend_date DATE NOT NULL,
    geographic_scope VARCHAR(50),
    location_state VARCHAR(2),
    location_city VARCHAR(100),
    location_metro VARCHAR(100),
    industry VARCHAR(100),
    job_category VARCHAR(100),
    total_job_postings INTEGER,
    new_job_postings INTEGER,
    active_job_seekers INTEGER,
    average_salary_min INTEGER,
    average_salary_max INTEGER,
    median_salary INTEGER,
    top_skills VARCHAR(16777216),
    skill_demand_trend VARCHAR(16777216),
    competition_index NUMERIC(5, 2),
    growth_rate NUMERIC(10, 4),
    data_source VARCHAR(50),
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    PRIMARY KEY (trend_id, trend_date)
);

-- Job Market Analytics Table
CREATE TABLE job_market_analytics (
    analytics_id VARCHAR(255) PRIMARY KEY,
    analysis_date DATE NOT NULL,
    analysis_type VARCHAR(50),
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
    top_employers VARCHAR(16777216),
    emerging_skills VARCHAR(16777216),
    declining_skills VARCHAR(16777216),
    salary_trends VARCHAR(16777216),
    job_type_distribution VARCHAR(16777216),
    work_model_distribution VARCHAR(16777216),
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Data Source Metadata Table
CREATE TABLE data_source_metadata (
    metadata_id VARCHAR(255) PRIMARY KEY,
    source_name VARCHAR(100) NOT NULL,
    source_type VARCHAR(50),
    extraction_date TIMESTAMP_NTZ NOT NULL,
    extraction_method VARCHAR(100),
    records_extracted INTEGER,
    records_new INTEGER,
    records_updated INTEGER,
    records_failed INTEGER,
    extraction_status VARCHAR(50),
    error_message VARCHAR(16777216),
    api_endpoint VARCHAR(1000),
    api_response_code INTEGER,
    extraction_duration_seconds INTEGER,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- User Job Search History Table (Will be partitioned)
CREATE TABLE user_job_search_history (
    search_id VARCHAR(255),
    user_id VARCHAR(255) NOT NULL,
    search_query VARCHAR(500),
    search_filters VARCHAR(16777216),
    location_filter VARCHAR(255),
    salary_filter_min INTEGER,
    salary_filter_max INTEGER,
    work_model_filter VARCHAR(50),
    job_type_filter VARCHAR(50),
    industry_filter VARCHAR(100),
    results_count INTEGER,
    search_date TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (user_id) REFERENCES user_profiles(user_id),
    PRIMARY KEY (search_id, search_date)
);

-- ============================================================================
-- PARTITIONING (PostgreSQL)
-- ============================================================================

-- Note: For PostgreSQL, uncomment and execute these partitioning statements
-- For Databricks, use PARTITIONED BY clause in CREATE TABLE
-- For Snowflake, use clustering keys instead

/*
-- PostgreSQL Partitioning for job_postings (monthly partitions)
ALTER TABLE job_postings DROP CONSTRAINT job_postings_pkey;
CREATE TABLE job_postings_partitioned (
    LIKE job_postings INCLUDING ALL
) PARTITION BY RANGE (posted_date);

-- Create monthly partitions for last 2 years
DO $$
DECLARE
    start_date DATE := DATE_TRUNC('month', CURRENT_DATE - INTERVAL '24 months');
    end_date DATE := DATE_TRUNC('month', CURRENT_DATE + INTERVAL '1 month');
    partition_date DATE;
    partition_name TEXT;
BEGIN
    partition_date := start_date;
    WHILE partition_date < end_date LOOP
        partition_name := 'job_postings_' || TO_CHAR(partition_date, 'YYYY_MM');
        EXECUTE format('
            CREATE TABLE %I PARTITION OF job_postings_partitioned
            FOR VALUES FROM (%L) TO (%L)',
            partition_name,
            partition_date,
            partition_date + INTERVAL '1 month'
        );
        partition_date := partition_date + INTERVAL '1 month';
    END LOOP;
END $$;

-- Similar partitioning for other large tables...
*/

-- ============================================================================
-- ADDITIONAL INDEXES FOR 30GB SCALE
-- ============================================================================

-- Job Postings Indexes
CREATE INDEX idx_job_postings_company_id ON job_postings(company_id);
CREATE INDEX idx_job_postings_posted_date ON job_postings(posted_date DESC);
CREATE INDEX idx_job_postings_location_state ON job_postings(location_state);
CREATE INDEX idx_job_postings_location_city ON job_postings(location_city);
CREATE INDEX idx_job_postings_work_model ON job_postings(work_model);
CREATE INDEX idx_job_postings_job_type ON job_postings(job_type);
CREATE INDEX idx_job_postings_is_active ON job_postings(is_active);
CREATE INDEX idx_job_postings_data_source ON job_postings(data_source);
CREATE INDEX idx_job_postings_posted_date_active ON job_postings(posted_date DESC, is_active) WHERE is_active = TRUE;
CREATE INDEX idx_job_postings_date_location_active ON job_postings(posted_date DESC, location_state, is_active) WHERE is_active = TRUE AND posted_date >= CURRENT_DATE - INTERVAL '90 days';
CREATE INDEX idx_job_postings_industry_location ON job_postings(industry, location_state) WHERE industry IS NOT NULL;
CREATE INDEX idx_job_postings_salary_range ON job_postings(salary_min, salary_max) WHERE salary_min IS NOT NULL AND salary_max IS NOT NULL;
CREATE INDEX idx_job_postings_federal_job ON job_postings(is_federal_job, agency_name) WHERE is_federal_job = TRUE;

-- Job Skills Requirements Indexes
CREATE INDEX idx_job_skills_requirements_job_id ON job_skills_requirements(job_id);
CREATE INDEX idx_job_skills_requirements_skill_id ON job_skills_requirements(skill_id);
CREATE INDEX idx_job_skills_requirements_type ON job_skills_requirements(requirement_type);
CREATE INDEX idx_job_skills_requirements_job_skill ON job_skills_requirements(job_id, skill_id);
CREATE INDEX idx_job_skills_requirements_required ON job_skills_requirements(job_id, skill_id) WHERE requirement_type = 'required';

-- User Skills Indexes
CREATE INDEX idx_user_skills_user_id ON user_skills(user_id);
CREATE INDEX idx_user_skills_skill_id ON user_skills(skill_id);
CREATE INDEX idx_user_skills_user_proficiency ON user_skills(user_id, proficiency_score DESC);
CREATE INDEX idx_user_skills_verified ON user_skills(user_id, skill_id) WHERE verified = TRUE;

-- Job Applications Indexes
CREATE INDEX idx_job_applications_user_id ON job_applications(user_id);
CREATE INDEX idx_job_applications_job_id ON job_applications(job_id);
CREATE INDEX idx_job_applications_status ON job_applications(application_status);
CREATE INDEX idx_job_applications_submitted_at ON job_applications(submitted_at DESC);
CREATE INDEX idx_job_applications_user_status_date ON job_applications(user_id, application_status, submitted_at DESC);
CREATE INDEX idx_job_applications_user_submitted ON job_applications(user_id, submitted_at DESC) WHERE submitted_at IS NOT NULL;
CREATE INDEX idx_job_applications_match_score ON job_applications(match_score DESC) WHERE match_score IS NOT NULL;

-- Job Recommendations Indexes
CREATE INDEX idx_job_recommendations_user_id ON job_recommendations(user_id);
CREATE INDEX idx_job_recommendations_job_id ON job_recommendations(job_id);
CREATE INDEX idx_job_recommendations_match_score ON job_recommendations(match_score DESC);
CREATE INDEX idx_job_recommendations_date ON job_recommendations(recommendation_date DESC);
CREATE INDEX idx_job_recommendations_user_score_date ON job_recommendations(user_id, match_score DESC, recommendation_date DESC);
CREATE INDEX idx_job_recommendations_user_active ON job_recommendations(user_id, match_score DESC) WHERE is_dismissed = FALSE AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP);
CREATE INDEX idx_job_recommendations_applied ON job_recommendations(user_id, job_id) WHERE is_applied = TRUE;

-- Market Trends Indexes
CREATE INDEX idx_market_trends_date ON market_trends(trend_date DESC);
CREATE INDEX idx_market_trends_location ON market_trends(location_state, location_city);
CREATE INDEX idx_market_trends_industry ON market_trends(industry);
CREATE INDEX idx_market_trends_date_location ON market_trends(trend_date DESC, location_state, industry);
CREATE INDEX idx_market_trends_recent ON market_trends(trend_date DESC) WHERE trend_date >= CURRENT_DATE - INTERVAL '1 year';

-- User Profiles Indexes
CREATE INDEX idx_user_profiles_location ON user_profiles(location_state, location_city);
CREATE INDEX idx_user_profiles_email ON user_profiles(email);
CREATE INDEX idx_user_profiles_is_active ON user_profiles(is_active);
CREATE INDEX idx_user_profiles_last_active ON user_profiles(last_active_at DESC) WHERE is_active = TRUE;
CREATE INDEX idx_user_profiles_experience ON user_profiles(years_experience) WHERE years_experience IS NOT NULL;
CREATE INDEX idx_user_profiles_work_model ON user_profiles(preferred_work_model) WHERE preferred_work_model IS NOT NULL;

-- Companies Indexes
CREATE INDEX idx_companies_industry ON companies(industry);
CREATE INDEX idx_companies_name_normalized ON companies(company_name_normalized);
CREATE INDEX idx_companies_federal ON companies(is_federal_agency, agency_code) WHERE is_federal_agency = TRUE;
CREATE INDEX idx_companies_rating ON companies(company_rating DESC) WHERE company_rating IS NOT NULL;

-- User Job Search History Indexes
CREATE INDEX idx_user_job_search_history_user_id ON user_job_search_history(user_id);
CREATE INDEX idx_user_job_search_history_date ON user_job_search_history(search_date DESC);
CREATE INDEX idx_user_job_search_history_user_date ON user_job_search_history(user_id, search_date DESC);

-- Data Source Metadata Indexes
CREATE INDEX idx_data_source_metadata_source ON data_source_metadata(source_name, extraction_date DESC);
CREATE INDEX idx_data_source_metadata_status ON data_source_metadata(extraction_status, extraction_date DESC);
CREATE INDEX idx_data_source_metadata_recent ON data_source_metadata(extraction_date DESC) WHERE extraction_date >= CURRENT_TIMESTAMP - INTERVAL '30 days';

-- ============================================================================
-- MATERIALIZED VIEWS FOR ANALYTICS
-- ============================================================================

-- Daily Job Market Summary (PostgreSQL)
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_daily_job_market_summary AS
SELECT
    DATE(posted_date) AS summary_date,
    location_state,
    industry,
    COUNT(*) AS total_jobs,
    COUNT(DISTINCT company_id) AS unique_companies,
    AVG((salary_min + salary_max) / 2) AS avg_salary_midpoint,
    COUNT(DISTINCT CASE WHEN work_model = 'remote' THEN job_id END) AS remote_jobs_count,
    COUNT(DISTINCT CASE WHEN work_model = 'hybrid' THEN job_id END) AS hybrid_jobs_count,
    COUNT(DISTINCT CASE WHEN is_federal_job = TRUE THEN job_id END) AS federal_jobs_count
FROM job_postings
WHERE is_active = TRUE
GROUP BY DATE(posted_date), location_state, industry;

CREATE UNIQUE INDEX ON mv_daily_job_market_summary(summary_date, location_state, industry);

-- User Application Summary (PostgreSQL)
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_user_application_summary AS
SELECT
    user_id,
    COUNT(*) AS total_applications,
    COUNT(DISTINCT CASE WHEN application_status IN ('interview', 'offer') THEN application_id END) AS successful_applications,
    AVG(match_score) AS avg_match_score,
    MIN(submitted_at) AS first_application_date,
    MAX(submitted_at) AS last_application_date
FROM job_applications
WHERE submitted_at IS NOT NULL
GROUP BY user_id;

CREATE UNIQUE INDEX ON mv_user_application_summary(user_id);

-- ============================================================================
-- DATABRICKS OPTIMIZATION (Delta Lake)
-- ============================================================================

-- For Databricks, use these optimizations:
-- OPTIMIZE job_postings ZORDER BY (posted_date, location_state);
-- OPTIMIZE job_applications ZORDER BY (submitted_at, user_id);
-- OPTIMIZE job_recommendations ZORDER BY (recommendation_date, user_id);

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE job_postings IS 'Job postings table optimized for 30GB scale with partitioning support';
COMMENT ON TABLE job_applications IS 'Job applications table optimized for 30GB scale with partitioning support';
COMMENT ON TABLE job_recommendations IS 'Job recommendations table optimized for 30GB scale with partitioning support';
COMMENT ON MATERIALIZED VIEW mv_daily_job_market_summary IS 'Pre-computed daily job market aggregations for performance';
COMMENT ON MATERIALIZED VIEW mv_user_application_summary IS 'Pre-computed user application statistics for performance';
